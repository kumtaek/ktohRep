"""
Metadata extraction and storage engine
Orchestrates parsing and stores results in database
"""

import os
import hashlib
import concurrent.futures
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.database import (
    create_database_engine, init_database,
    Project, File, JavaClass, JavaMethod, SQLUnit,
    Edge, Join, RequiredFilter, Summary
)
from ..parsers.java_parser import JavaSourceParser, JavaParsingResult
from ..parsers.jsp_mybatis_parser import JSPMyBatisAnalyzer, JSPParsingResult, MyBatisParsingResult
from ..parsers.sql_parser import SQLParser, SQLParsingResult


class MetadataEngine:
    """메타데이터 추출 및 저장 엔진"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_config = config.get('database', {})
        self.parsing_config = config.get('parsing', {})
        
        # 데이터베이스 초기화
        db_path = self.db_config.get('path', './data/metadata.db')
        self.engine, self.SessionLocal = create_database_engine(f"sqlite:///{db_path}")
        init_database(self.engine)
        
        # 파서 초기화
        self.java_parser = JavaSourceParser(self.parsing_config.get('java', {}))
        self.jsp_mybatis_analyzer = JSPMyBatisAnalyzer(self.parsing_config.get('mybatis', {}))
        self.sql_parser = SQLParser(self.parsing_config.get('sql', {}))
        
        # 멀티스레드 설정
        self.thread_count = self.parsing_config.get('java', {}).get('thread_count', 4)
    
    def create_or_get_project(self, root_path: str, project_name: str = None) -> int:
        """프로젝트 생성 또는 기존 프로젝트 조회"""
        with self.SessionLocal() as session:
            # 기존 프로젝트 조회
            existing_project = session.query(Project).filter(
                Project.root_path == root_path
            ).first()
            
            if existing_project:
                return existing_project.project_id
            
            # 새 프로젝트 생성
            new_project = Project(
                root_path=root_path,
                name=project_name or os.path.basename(root_path)
            )
            session.add(new_project)
            session.commit()
            return new_project.project_id
    
    def should_reparse_file(self, file_path: str, project_id: int) -> bool:
        """파일 재파싱 필요 여부 확인 (증분 분석)"""
        try:
            current_stat = os.stat(file_path)
            current_mtime = datetime.fromtimestamp(current_stat.st_mtime)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_content = f.read()
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            
            with self.SessionLocal() as session:
                existing_file = session.query(File).filter(
                    and_(
                        File.project_id == project_id,
                        File.path == os.path.relpath(file_path)
                    )
                ).first()
                
                if not existing_file:
                    return True  # 새 파일
                
                # 해시나 수정시간이 다르면 재파싱
                if existing_file.hash != current_hash or existing_file.mtime != current_mtime:
                    return True
                
                return False
        except:
            return True  # 에러 시 재파싱
    
    def store_java_results(self, results: List[JavaParsingResult], session: Session) -> List[int]:
        """Java 파싱 결과를 데이터베이스에 저장"""
        file_ids = []
        
        for result in results:
            try:
                # 파일 정보 저장
                file_obj = File(**result.file_info)
                
                # 기존 파일 확인 및 업데이트
                existing_file = session.query(File).filter(
                    and_(
                        File.project_id == result.file_info['project_id'],
                        File.path == result.file_info['path']
                    )
                ).first()
                
                if existing_file:
                    # 기존 관련 데이터 삭제
                    session.query(JavaMethod).filter(
                        JavaMethod.class_id.in_(
                            session.query(JavaClass.class_id).filter(JavaClass.file_id == existing_file.file_id)
                        )
                    ).delete(synchronize_session=False)
                    session.query(JavaClass).filter(JavaClass.file_id == existing_file.file_id).delete()
                    
                    # 파일 정보 업데이트
                    for key, value in result.file_info.items():
                        setattr(existing_file, key, value)
                    file_obj = existing_file
                else:
                    session.add(file_obj)
                
                session.flush()  # file_id 생성
                file_ids.append(file_obj.file_id)
                
                # 클래스 정보 저장
                class_map = {}
                for class_info in result.classes:
                    class_obj = JavaClass(
                        file_id=file_obj.file_id,
                        **class_info
                    )
                    session.add(class_obj)
                    session.flush()
                    class_map[class_info['name']] = class_obj
                
                # 메소드 정보 저장
                for method_info in result.methods:
                    class_name = method_info.pop('class_name')
                    if class_name in class_map:
                        method_obj = JavaMethod(
                            class_id=class_map[class_name].class_id,
                            **method_info
                        )
                        session.add(method_obj)
                
                # 의존성 정보는 별도 처리 (향후 구현)
                
            except Exception as e:
                print(f"Error storing Java result: {e}")
                continue
        
        return file_ids
    
    def store_jsp_results(self, results: List[JSPParsingResult], session: Session) -> List[int]:
        """JSP 파싱 결과를 데이터베이스에 저장"""
        file_ids = []
        
        for result in results:
            try:
                # 파일 정보 저장
                file_obj = File(**result.file_info)
                
                existing_file = session.query(File).filter(
                    and_(
                        File.project_id == result.file_info['project_id'],
                        File.path == result.file_info['path']
                    )
                ).first()
                
                if existing_file:
                    for key, value in result.file_info.items():
                        setattr(existing_file, key, value)
                    file_obj = existing_file
                else:
                    session.add(file_obj)
                
                session.flush()
                file_ids.append(file_obj.file_id)
                
                # JSP 특성 정보를 Summary 테이블에 저장
                if result.includes or result.scriptlets or result.el_expressions:
                    summary_content = {
                        'includes': len(result.includes),
                        'scriptlets': len(result.scriptlets),
                        'el_expressions': len(result.el_expressions),
                        'jstl_tags': len(result.jstl_tags)
                    }
                    
                    summary_obj = Summary(
                        target_type='file',
                        target_id=file_obj.file_id,
                        summary_type='jsp_structure',
                        content=str(summary_content),
                        confidence=result.confidence
                    )
                    session.add(summary_obj)
                
            except Exception as e:
                print(f"Error storing JSP result: {e}")
                continue
        
        return file_ids
    
    def store_mybatis_results(self, results: List[MyBatisParsingResult], session: Session) -> List[int]:
        """MyBatis 파싱 결과를 데이터베이스에 저장"""
        file_ids = []
        
        for result in results:
            try:
                # 파일 정보 저장
                file_obj = File(**result.file_info)
                
                existing_file = session.query(File).filter(
                    and_(
                        File.project_id == result.file_info['project_id'],
                        File.path == result.file_info['path']
                    )
                ).first()
                
                if existing_file:
                    # 기존 SQL 유닛 삭제
                    session.query(Join).filter(
                        Join.sql_id.in_(
                            session.query(SQLUnit.sql_id).filter(SQLUnit.file_id == existing_file.file_id)
                        )
                    ).delete(synchronize_session=False)
                    session.query(RequiredFilter).filter(
                        RequiredFilter.sql_id.in_(
                            session.query(SQLUnit.sql_id).filter(SQLUnit.file_id == existing_file.file_id)
                        )
                    ).delete(synchronize_session=False)
                    session.query(SQLUnit).filter(SQLUnit.file_id == existing_file.file_id).delete()
                    
                    for key, value in result.file_info.items():
                        setattr(existing_file, key, value)
                    file_obj = existing_file
                else:
                    session.add(file_obj)
                
                session.flush()
                file_ids.append(file_obj.file_id)
                
                # SQL 유닛 저장
                for stmt_info in result.statements:
                    sql_unit = SQLUnit(
                        file_id=file_obj.file_id,
                        origin='mybatis',
                        mapper_ns=result.namespace,
                        stmt_id=stmt_info['id'],
                        stmt_kind=stmt_info['type'],
                        normalized_fingerprint=hashlib.md5(
                            stmt_info.get('sql_content', '').encode()
                        ).hexdigest()[:16]
                    )
                    session.add(sql_unit)
                    session.flush()
                    
                    # TODO: 조인과 필터 정보 저장 (SQL 파싱 연동 후 구현)
                
            except Exception as e:
                print(f"Error storing MyBatis result: {e}")
                continue
        
        return file_ids
    
    def store_sql_results(self, results: List[SQLParsingResult], session: Session) -> List[int]:
        """SQL 파싱 결과를 데이터베이스에 저장"""
        file_ids = []
        
        for result in results:
            try:
                # 파일 정보 저장
                file_obj = File(**result.file_info)
                
                existing_file = session.query(File).filter(
                    and_(
                        File.project_id == result.file_info['project_id'],
                        File.path == result.file_info['path']
                    )
                ).first()
                
                if existing_file:
                    # 기존 데이터 삭제
                    session.query(Join).filter(
                        Join.sql_id.in_(
                            session.query(SQLUnit.sql_id).filter(SQLUnit.file_id == existing_file.file_id)
                        )
                    ).delete(synchronize_session=False)
                    session.query(RequiredFilter).filter(
                        RequiredFilter.sql_id.in_(
                            session.query(SQLUnit.sql_id).filter(SQLUnit.file_id == existing_file.file_id)
                        )
                    ).delete(synchronize_session=False)
                    session.query(SQLUnit).filter(SQLUnit.file_id == existing_file.file_id).delete()
                    
                    for key, value in result.file_info.items():
                        setattr(existing_file, key, value)
                    file_obj = existing_file
                else:
                    session.add(file_obj)
                
                session.flush()
                file_ids.append(file_obj.file_id)
                
                # SQL 문 저장
                for stmt_info in result.statements:
                    sql_unit = SQLUnit(
                        file_id=file_obj.file_id,
                        origin='direct',
                        stmt_kind=stmt_info['type'],
                        normalized_fingerprint=stmt_info['fingerprint']
                    )
                    session.add(sql_unit)
                    session.flush()
                    
                    # 조인 정보 저장
                    for join_info in stmt_info['joins']:
                        join_obj = Join(
                            sql_id=sql_unit.sql_id,
                            l_table=join_info.get('left_table'),
                            l_col=join_info.get('left_column'),
                            op=join_info.get('operator'),
                            r_table=join_info.get('right_table'),
                            r_col=join_info.get('right_column'),
                            confidence=join_info.get('confidence', 0.5)
                        )
                        session.add(join_obj)
                    
                    # 필터 정보 저장
                    for filter_info in stmt_info['filters']:
                        filter_obj = RequiredFilter(
                            sql_id=sql_unit.sql_id,
                            table_name=filter_info.get('table_name'),
                            column_name=filter_info.get('column_name'),
                            op=filter_info.get('operator'),
                            value_repr=filter_info.get('value'),
                            always_applied=1 if filter_info.get('always_applied', False) else 0,
                            confidence=filter_info.get('confidence', 0.5)
                        )
                        session.add(filter_obj)
                
            except Exception as e:
                print(f"Error storing SQL result: {e}")
                continue
        
        return file_ids
    
    def process_files_batch(self, file_paths: List[str], project_id: int) -> Tuple[List, List, List, List]:
        """파일 배치 처리"""
        java_results = []
        jsp_results = []
        mybatis_results = []
        sql_results = []
        
        for file_path in file_paths:
            try:
                if not self.should_reparse_file(file_path, project_id):
                    continue
                
                if self.java_parser.can_parse(file_path):
                    result = self.java_parser.parse_file(file_path, project_id)
                    java_results.append(result)
                
                elif file_path.endswith(('.jsp', '.jspx')):
                    result = self.jsp_mybatis_analyzer.jsp_parser.parse_file(file_path, project_id)
                    jsp_results.append(result)
                
                elif self.jsp_mybatis_analyzer.mybatis_parser.can_parse(file_path):
                    result = self.jsp_mybatis_analyzer.mybatis_parser.parse_file(file_path, project_id)
                    mybatis_results.append(result)
                
                elif self.sql_parser.can_parse(file_path):
                    result = self.sql_parser.parse_file(file_path, project_id)
                    sql_results.append(result)
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        return java_results, jsp_results, mybatis_results, sql_results
    
    def analyze_project(self, project_root: str, project_name: str = None) -> Dict[str, Any]:
        """프로젝트 전체 분석"""
        print(f"Starting analysis of project: {project_root}")
        
        # 프로젝트 생성/조회
        project_id = self.create_or_get_project(project_root, project_name)
        
        # 분석 대상 파일 수집
        target_files = []
        supported_extensions = []
        for lang_config in self.config['project']['supported_extensions'].values():
            supported_extensions.extend(lang_config)
        
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    target_files.append(os.path.join(root, file))
        
        print(f"Found {len(target_files)} files to analyze")
        
        # 파일을 배치로 나누기
        batch_size = max(1, len(target_files) // self.thread_count)
        file_batches = [target_files[i:i + batch_size] for i in range(0, len(target_files), batch_size)]
        
        # 멀티스레드 파싱
        all_java_results = []
        all_jsp_results = []
        all_mybatis_results = []
        all_sql_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            future_to_batch = {
                executor.submit(self.process_files_batch, batch, project_id): batch 
                for batch in file_batches
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    java_results, jsp_results, mybatis_results, sql_results = future.result()
                    all_java_results.extend(java_results)
                    all_jsp_results.extend(jsp_results)
                    all_mybatis_results.extend(mybatis_results)
                    all_sql_results.extend(sql_results)
                except Exception as e:
                    print(f"Error in batch processing: {e}")
        
        # 데이터베이스 저장
        print("Storing results in database...")
        with self.SessionLocal() as session:
            try:
                java_file_ids = self.store_java_results(all_java_results, session)
                jsp_file_ids = self.store_jsp_results(all_jsp_results, session)
                mybatis_file_ids = self.store_mybatis_results(all_mybatis_results, session)
                sql_file_ids = self.store_sql_results(all_sql_results, session)
                
                session.commit()
                
                # 결과 요약
                summary = {
                    'project_id': project_id,
                    'files_processed': len(target_files),
                    'java_files': len(all_java_results),
                    'jsp_files': len(all_jsp_results),
                    'mybatis_files': len(all_mybatis_results),
                    'sql_files': len(all_sql_results),
                    'total_classes': sum(len(r.classes) for r in all_java_results),
                    'total_methods': sum(len(r.methods) for r in all_java_results),
                    'total_sql_statements': sum(len(r.statements) for r in all_sql_results),
                    'analysis_time': datetime.now().isoformat()
                }
                
                print("Analysis completed successfully!")
                return summary
                
            except Exception as e:
                session.rollback()
                print(f"Error storing results: {e}")
                raise
    
    def get_project_statistics(self, project_id: int) -> Dict[str, Any]:
        """프로젝트 통계 조회"""
        with self.SessionLocal() as session:
            stats = {}
            
            # 파일 통계
            stats['total_files'] = session.query(File).filter(File.project_id == project_id).count()
            stats['java_files'] = session.query(File).filter(
                and_(File.project_id == project_id, File.language == 'java')
            ).count()
            stats['jsp_files'] = session.query(File).filter(
                and_(File.project_id == project_id, File.language == 'jsp')
            ).count()
            stats['mybatis_files'] = session.query(File).filter(
                and_(File.project_id == project_id, File.language == 'mybatis')
            ).count()
            stats['sql_files'] = session.query(File).filter(
                and_(File.project_id == project_id, File.language == 'sql')
            ).count()
            
            # 구조 통계
            stats['total_classes'] = session.query(JavaClass).join(File).filter(
                File.project_id == project_id
            ).count()
            stats['total_methods'] = session.query(JavaMethod).join(JavaClass).join(File).filter(
                File.project_id == project_id
            ).count()
            stats['total_sql_units'] = session.query(SQLUnit).join(File).filter(
                File.project_id == project_id
            ).count()
            
            return stats


if __name__ == "__main__":
    # 테스트 코드
    import yaml
    
    # 설정 로드
    config_path = "./config/config.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        config = {
            'project': {'supported_extensions': {'java': ['.java'], 'jsp': ['.jsp'], 'mybatis': ['.xml'], 'sql': ['.sql']}},
            'database': {'path': './data/metadata.db'},
            'parsing': {'java': {'thread_count': 2}}
        }
    
    engine = MetadataEngine(config)
    
    # 샘플 프로젝트 분석
    sample_project = "./PROJECT/sample-app"
    if os.path.exists(sample_project):
        summary = engine.analyze_project(sample_project, "sample-app")
        print(f"\nAnalysis Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # 통계 조회
        stats = engine.get_project_statistics(summary['project_id'])
        print(f"\nProject Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print("Sample project not found")