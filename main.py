"""
소스 분석기 메인 모듈
1단계 메타정보 생성 시스템의 진입점
"""

import os
import sys
import argparse
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List
import asyncio

# 프로젝트 루트를 Python 패스에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.database import DatabaseManager
from src.parsers.java_parser import JavaParser
from src.parsers.jsp_mybatis_parser import JspMybatisParser
from src.parsers.sql_parser import SqlParser
from src.database.metadata_engine import MetadataEngine
from src.utils.csv_loader import CsvLoader

class SourceAnalyzer:
    """소스 분석기 메인 클래스"""
    
    def __init__(self, config_path: str):
        """
        소스 분석기 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # 데이터베이스 매니저 초기화
        self.db_manager = DatabaseManager(self.config)
        self.db_manager.initialize()
        
        # 파서들 초기화
        self.java_parser = JavaParser(self.config)
        self.jsp_mybatis_parser = JspMybatisParser(self.config)
        self.sql_parser = SqlParser(self.config)
        
        # 메타데이터 엔진 초기화
        self.metadata_engine = MetadataEngine(self.config, self.db_manager)
        
        # CSV 로더 초기화
        self.csv_loader = CsvLoader(self.config)
        
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"설정 파일 파싱 오류: {e}")
            
    def setup_logging(self):
        """로깅 설정"""
        log_config = self.config.get('logging', {})
        
        # 로그 디렉토리 생성
        log_file = log_config.get('file', './logs/analyzer.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 로깅 설정
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    async def analyze_project(self, project_root: str, project_name: str = None) -> Dict[str, Any]:
        """
        프로젝트 전체 분석
        
        Args:
            project_root: 프로젝트 루트 경로
            project_name: 프로젝트 이름 (없으면 폴더명 사용)
            
        Returns:
            분석 결과 딕셔너리
        """
        
        if not project_name:
            project_name = os.path.basename(project_root.rstrip('/\\'))
            
        self.logger.info(f"프로젝트 분석 시작: {project_name} ({project_root})")
        
        try:
            # 1. 프로젝트 등록
            project_id = await self.metadata_engine.create_project(project_root, project_name)
            
            # 2. DB 스키마 정보 로드
            await self._load_db_schema(project_root, project_name, project_id)
            
            # 3. 소스 파일들 수집
            source_files = self._collect_source_files(project_root)
            self.logger.info(f"발견된 소스 파일: {len(source_files)}개")
            
            # 4. 파일들 분석 (병렬 처리)
            analysis_results = await self._analyze_files(source_files, project_id)
            
            # 5. 의존성 그래프 구축
            await self.metadata_engine.build_dependency_graph(project_id)
            
            # 6. 분석 결과 요약
            summary = await self._generate_analysis_summary(project_id)
            
            self.logger.info(f"프로젝트 분석 완료: {project_name}")
            
            return {
                'project_id': project_id,
                'project_name': project_name,
                'files_analyzed': len(source_files),
                'analysis_results': analysis_results,
                'summary': summary
            }
            
        except Exception as e:
            self.logger.error(f"프로젝트 분석 오류: {e}")
            raise
            
    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        """DB 스키마 정보 로드"""
        
        db_schema_path = os.path.join(project_root, f"DB_SCHEMA")
        if not os.path.exists(db_schema_path):
            self.logger.warning(f"DB 스키마 경로가 없습니다: {db_schema_path}")
            return
            
        self.logger.info("DB 스키마 정보 로딩 중...")
        
        # 필수 CSV 파일들 로드
        required_files = self.config['db_schema']['required_files']
        
        for csv_file in required_files:
            csv_path = os.path.join(db_schema_path, csv_file)
            if os.path.exists(csv_path):
                await self.csv_loader.load_csv(csv_path, project_id)
                self.logger.info(f"로드 완료: {csv_file}")
            else:
                self.logger.warning(f"CSV 파일 없음: {csv_path}")
                
    def _collect_source_files(self, project_root: str) -> List[str]:
        """소스 파일들 수집"""
        
        source_files = []
        file_patterns = self.config['file_patterns']
        include_patterns = file_patterns.get('include', [])
        exclude_patterns = file_patterns.get('exclude', [])
        
        for root, dirs, files in os.walk(project_root):
            # 제외 패턴에 해당하는 디렉토리 건너뛰기
            dirs[:] = [d for d in dirs if not any(
                self._match_pattern(os.path.join(root, d), pattern) 
                for pattern in exclude_patterns
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 포함 패턴 확인
                if any(self._match_pattern(file_path, pattern) for pattern in include_patterns):
                    # 제외 패턴 확인
                    if not any(self._match_pattern(file_path, pattern) for pattern in exclude_patterns):
                        source_files.append(file_path)
                        
        return source_files
        
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """파일 패턴 매칭"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern)
        
    async def _analyze_files(self, source_files: List[str], project_id: int) -> Dict[str, Any]:
        """소스 파일들 분석"""
        
        analysis_results = {
            'java_files': 0,
            'jsp_files': 0,
            'xml_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_sql_units': 0,
            'errors': []
        }
        
        # 병렬 처리를 위한 세마포어
        max_workers = self.config['processing'].get('max_workers', 4)
        semaphore = asyncio.Semaphore(max_workers)
        
        # 파일별 분석 태스크 생성
        tasks = [
            self._analyze_single_file(file_path, project_id, semaphore) 
            for file_path in source_files
        ]
        
        # 병렬 실행
        file_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        for i, result in enumerate(file_results):
            if isinstance(result, Exception):
                analysis_results['errors'].append({
                    'file': source_files[i],
                    'error': str(result)
                })
            else:
                # 파일 타입별 카운팅
                file_path = source_files[i]
                if file_path.endswith('.java'):
                    analysis_results['java_files'] += 1
                elif file_path.endswith('.jsp'):
                    analysis_results['jsp_files'] += 1
                elif file_path.endswith('.xml'):
                    analysis_results['xml_files'] += 1
                    
                # 요소별 카운팅
                if result:
                    analysis_results['total_classes'] += result.get('classes', 0)
                    analysis_results['total_methods'] += result.get('methods', 0)
                    analysis_results['total_sql_units'] += result.get('sql_units', 0)
                    
        return analysis_results
        
    async def _analyze_single_file(self, file_path: str, project_id: int, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """단일 파일 분석"""
        
        async with semaphore:
            try:
                self.logger.debug(f"파일 분석 시작: {file_path}")
                
                result = {'classes': 0, 'methods': 0, 'sql_units': 0}
                
                # 파일 타입에 따른 파서 선택
                if self.java_parser.can_parse(file_path):
                    file_obj, classes, methods, edges = self.java_parser.parse_file(file_path, project_id)
                    
                    # 데이터베이스에 저장
                    await self.metadata_engine.save_java_analysis(file_obj, classes, methods, edges)
                    
                    result['classes'] = len(classes)
                    result['methods'] = len(methods)
                    
                elif self.jsp_mybatis_parser.can_parse(file_path):
                    file_obj, sql_units, joins, filters, edges = self.jsp_mybatis_parser.parse_file(file_path, project_id)
                    
                    # 데이터베이스에 저장
                    await self.metadata_engine.save_jsp_mybatis_analysis(file_obj, sql_units, joins, filters, edges)
                    
                    result['sql_units'] = len(sql_units)
                    
                return result
                
            except Exception as e:
                self.logger.error(f"파일 분석 오류 {file_path}: {e}")
                raise
                
    async def _generate_analysis_summary(self, project_id: int) -> Dict[str, Any]:
        """분석 결과 요약 생성"""
        
        return await self.metadata_engine.generate_project_summary(project_id)
        
def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(description='소스 코드 분석 도구 - 1단계 메타정보 생성')
    
    parser.add_argument('project_path', help='분석할 프로젝트 경로')
    parser.add_argument('--config', default='./config/config.yaml', help='설정 파일 경로')
    parser.add_argument('--project-name', help='프로젝트 이름 (기본값: 폴더명)')
    parser.add_argument('--incremental', action='store_true', help='증분 분석 모드')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_path):
        print(f"오류: 프로젝트 경로가 존재하지 않습니다: {args.project_path}")
        sys.exit(1)
        
    if not os.path.exists(args.config):
        print(f"오류: 설정 파일이 존재하지 않습니다: {args.config}")
        sys.exit(1)
        
    try:
        # 소스 분석기 초기화
        analyzer = SourceAnalyzer(args.config)
        
        # 프로젝트 분석 실행
        result = asyncio.run(analyzer.analyze_project(
            args.project_path, 
            args.project_name
        ))
        
        # 결과 출력
        print("=" * 50)
        print("분석 완료!")
        print(f"프로젝트: {result['project_name']}")
        print(f"분석된 파일 수: {result['files_analyzed']}")
        print(f"Java 파일: {result['analysis_results']['java_files']}")
        print(f"JSP 파일: {result['analysis_results']['jsp_files']}")  
        print(f"XML 파일: {result['analysis_results']['xml_files']}")
        print(f"클래스 수: {result['analysis_results']['total_classes']}")
        print(f"메서드 수: {result['analysis_results']['total_methods']}")
        print(f"SQL 구문 수: {result['analysis_results']['total_sql_units']}")
        
        if result['analysis_results']['errors']:
            print(f"오류 파일 수: {len(result['analysis_results']['errors'])}")
            
        print("=" * 50)
        
    except Exception as e:
        print(f"분석 중 오류가 발생했습니다: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()