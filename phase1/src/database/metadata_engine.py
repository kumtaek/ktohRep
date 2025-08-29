"""
메타데이터 엔진 (개선된 병렬 처리 버전)
분석된 메타데이터를 데이터베이스에 저장하고 관리하는 엔진
병렬 처리 및 개선된 예외 처리 포함
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import hashlib
import concurrent.futures
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, func
from contextlib import asynccontextmanager, contextmanager
import time
import os

from ..models.database import (
    DatabaseManager, Project, File, Class, Method, SqlUnit, 
    Join, RequiredFilter, Edge, Summary, EnrichmentLog,
    DbTable, DbColumn, DbPk, DbView, ParseResultModel, VulnerabilityFix
)
from ..utils.logger import LoggerFactory, PerformanceLogger, ExceptionHandler
from ..utils.confidence_calculator import ConfidenceCalculator, ParseResult as ConfidenceParseResult

class MetadataEngine:
    """메타데이터 저장 및 관리 엔진"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.logger = LoggerFactory.get_engine_logger()
        self.confidence_calculator = ConfidenceCalculator(config)
        
        # 병렬 처리 설정
        self.max_workers = config.get('processing', {}).get('max_workers', 4)
        self.batch_size = config.get('processing', {}).get('batch_size', 10)
        
        # 삭제된 파일 정리 확장 로드
        try:
            from . import metadata_engine_cleanup
        except ImportError:
            self.logger.debug("삭제된 파일 정리 확장 모듈을 로드할 수 없습니다")
    
    @asynccontextmanager
    async def _get_async_session(self):
        """안전한 비동기 데이터베이스 세션 컨텍스트 매니저"""
        session = self.db_manager.get_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @contextmanager
    def _get_sync_session(self):
        """안전한 동기 데이터베이스 세션 컨텍스트 매니저"""
        session = self.db_manager.get_session()
        try:
            with session.begin():
                yield session
        except Exception:
            # session.begin() 컨텍스트가 자동 롤백
            raise
        finally:
            session.close()
        
    async def create_project(self, project_path: str, project_name: str) -> int:
        """
        새 프로젝트 생성 또는 기존 프로젝트 업데이트
        
        Args:
            project_path: 프로젝트 경로
            project_name: 프로젝트 이름
            
        Returns:
            프로젝트 ID
        """
        
        async with self._get_async_session() as session:
            # 기존 프로젝트 확인
            existing_project = session.query(Project).filter(
                Project.root_path == project_path
            ).first()
            
            if existing_project:
                # 기존 프로젝트 업데이트
                existing_project.updated_at = datetime.utcnow()
                existing_project.name = project_name
                session.commit()
                return existing_project.project_id
            else:
                # 새 프로젝트 생성
                new_project = Project(
                    root_path=project_path,
                    name=project_name
                )
                session.add(new_project)
                session.commit()
                return new_project.project_id
            
    async def analyze_files_parallel(self, file_paths: List[str], project_id: int,
                                   parsers: Dict[str, Any]) -> Dict[str, Any]:
        """
        파일들을 병렬로 분석
        
        Args:
            file_paths: 분석할 파일 경로 리스트
            project_id: 프로젝트 ID
            parsers: 파서 객체들 딕셔너리
            
        Returns:
            분석 결과 요약
        """
        
        with PerformanceLogger(self.logger, "병렬 파일 분석", len(file_paths)):
            self.logger.info(f"병렬 파일 분석 시작: {len(file_paths)}개 파일, {self.max_workers}개 워커")
            
            results = {
                'total_files': len(file_paths),
                'success_count': 0,
                'error_count': 0,
                'java_files': 0,
                'jsp_files': 0,
                'xml_files': 0,
                'total_classes': 0,
                'total_methods': 0,
                'total_sql_units': 0,
                'errors': []
            }
            
            # 파일들을 배치로 나누기
            batches = [file_paths[i:i + self.batch_size] 
                      for i in range(0, len(file_paths), self.batch_size)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 각 배치를 병렬로 처리
                future_to_batch = {
                    executor.submit(self._analyze_batch_sync, batch, project_id, parsers): batch_idx
                    for batch_idx, batch in enumerate(batches)
                }
                
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_idx = future_to_batch[future]
                    try:
                        batch_result = future.result()
                        
                        # 결과 집계
                        results['success_count'] += batch_result['success_count']
                        results['error_count'] += batch_result['error_count']
                        results['java_files'] += batch_result['java_files']
                        results['jsp_files'] += batch_result['jsp_files']
                        results['xml_files'] += batch_result['xml_files']
                        results['total_classes'] += batch_result['total_classes']
                        results['total_methods'] += batch_result['total_methods']
                        results['total_sql_units'] += batch_result['total_sql_units']
                        results['errors'].extend(batch_result['errors'])
                        
                        self.logger.info(f"배치 {batch_idx + 1}/{len(batches)} 완료")
                        
                    except Exception as e:
                        batch = batches[batch_idx]
                        self.logger.error(f"배치 {batch_idx + 1} 처리 실패", exception=e)
                        results['error_count'] += len(batch)
                        results['errors'].append({
                            'batch': batch_idx,
                            'files': batch,
                            'error': str(e)
                        })
            
            self.logger.info(f"병렬 분석 완료: 성공 {results['success_count']}, 실패 {results['error_count']}")
            return results
            
    def _analyze_batch_sync(self, file_paths: List[str], project_id: int, 
                           parsers: Dict[str, Any]) -> Dict[str, Any]:
        """
        파일 배치를 동기적으로 분석 (스레드에서 실행)
        """
        batch_result = {
            'success_count': 0,
            'error_count': 0,
            'java_files': 0,
            'jsp_files': 0,
            'xml_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_sql_units': 0,
            'errors': []
        }
        
        for file_path in file_paths:
            try:
                result = self._analyze_single_file_sync(file_path, project_id, parsers)
                if result:
                    batch_result['success_count'] += 1
                    
                    # 파일 타입별 카운팅
                    if file_path.endswith('.java'):
                        batch_result['java_files'] += 1
                    elif file_path.endswith('.jsp'):
                        batch_result['jsp_files'] += 1
                    elif file_path.endswith('.xml'):
                        batch_result['xml_files'] += 1
                    
                    # 요소 카운팅
                    batch_result['total_classes'] += result.get('classes', 0)
                    batch_result['total_methods'] += result.get('methods', 0)
                    batch_result['total_sql_units'] += result.get('sql_units', 0)
                else:
                    batch_result['error_count'] += 1
                    
            except Exception as e:
                batch_result['error_count'] += 1
                batch_result['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
                
        return batch_result
        
    def _analyze_single_file_sync(self, file_path: str, project_id: int, 
                                 parsers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        단일 파일 동기 분석
        """
        start_time = time.time()
        
        try:
            # 파일 타입에 따른 파서 선택
            if file_path.endswith('.java') and 'java' in parsers:
                file_obj, classes, methods, edges = parsers['java'].parse_file(file_path, project_id)
                parse_time = time.time() - start_time
                
                # 파싱 결과를 ParseResult 객체로 저장
                parse_result_data = ConfidenceParseResult(
                    file_path=file_path,
                    parser_type='javalang',
                    success=True,
                    parse_time=parse_time,
                    ast_complete=True,
                    classes=len(classes),
                    methods=len(methods)
                )
                
                # 신뢰도 계산
                confidence, factors = self.confidence_calculator.calculate_parsing_confidence(parse_result_data)
                
                # 동기 저장 메서드 호출 (asyncio.run 제거)
                saved_counts = self._save_java_analysis_sync(file_obj, classes, methods, edges)
                
                return saved_counts
                
            elif (file_path.endswith('.jsp') or file_path.endswith('.xml')) and 'jsp_mybatis' in parsers:
                file_obj, sql_units, joins, filters, edges, vulnerabilities = parsers['jsp_mybatis'].parse_file(file_path, project_id)
                parse_time = time.time() - start_time
                
                # 파싱 결과 저장
                parse_result_data = ConfidenceParseResult(
                    file_path=file_path,
                    parser_type='mybatis_xml' if file_path.endswith('.xml') else 'jsp',
                    success=True,
                    parse_time=parse_time,
                    ast_complete=True,
                    sql_units=len(sql_units)
                )
                
                # 신뢰도 계산
                confidence, factors = self.confidence_calculator.calculate_parsing_confidence(parse_result_data)
                
                # 동기 저장 메서드 호출 (asyncio.run 제거)
                saved_counts = self._save_jsp_mybatis_analysis_sync(file_obj, sql_units, joins, filters, edges, vulnerabilities)
                
                return saved_counts
                
            return None
            
        except Exception as e:
            parse_time = time.time() - start_time
            
            # 실패한 파싱 결과도 기록
            parse_result_data = ConfidenceParseResult(
                file_path=file_path,
                parser_type='unknown',
                success=False,
                parse_time=parse_time,
                error_message=str(e)
            )
            
            # 낮은 신뢰도로 기록
            confidence = 0.1
            
            self.logger.log_parsing_failure(file_path, 'unknown', e)
            raise e
            
    def _save_java_analysis_sync(self, 
                                file_obj: File, 
                                classes: List[Class], 
                                methods: List[Method], 
                                edges: List[Edge]) -> Dict[str, int]:
        """
        Java 분석 결과 저장 (동기 버전)
        
        Args:
            file_obj: 파일 객체
            classes: 클래스 리스트
            methods: 메서드 리스트  
            edges: 의존성 엣지 리스트
            
        Returns:
            저장된 엔티티 수
        """
        
        with self._get_sync_session() as session:
            # 파일 저장
            session.add(file_obj)
            session.flush()  # ID 생성을 위해 flush
            
            saved_counts = {'files': 1, 'classes': 0, 'methods': 0, 'edges': 0}
            
            # 클래스 저장 및 FQN 매핑
            fqn_to_class_id = {}
            for class_obj in classes:
                class_obj.file_id = file_obj.file_id
                session.add(class_obj)
                session.flush()
                try:
                    if class_obj.fqn:
                        fqn_to_class_id[class_obj.fqn] = class_obj.class_id
                except Exception:
                    pass
                
                # 해당 클래스의 메서드들 저장
                class_methods = [m for m in methods if getattr(m, 'owner_fqn', None) == class_obj.fqn]
                for method_obj in class_methods:
                    method_obj.class_id = class_obj.class_id
                    session.add(method_obj)
                    session.flush()
                    # 메서드 기원 엣지의 src_id 채우기(호출관계 저장용)
                    for e in [e for e in edges if e.src_type == 'method' and e.src_id is None]:
                        e.src_id = method_obj.method_id
                    
                saved_counts['classes'] += 1
                
            saved_counts['methods'] = len(methods)
            
            # 의존성 엣지 저장: call 엣지는 dst 미해결 상태도 저장
            confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
            count_edges = 0
            for edge in edges:
                if edge.edge_kind == 'call':
                    session.add(edge)
                    count_edges += 1
                else:
                    if (edge.src_id is not None and edge.dst_id is not None 
                        and edge.src_id != 0 and edge.dst_id != 0
                        and edge.confidence >= confidence_threshold):
                        session.add(edge)
                        count_edges += 1
            saved_counts['edges'] += count_edges
            self.logger.debug(f"Java 분석 - 전체 엣지: {len(edges)}, 저장 엣지: {count_edges}")
                
            session.commit()
            return saved_counts

    async def save_java_analysis(self, 
                                file_obj: File, 
                                classes: List[Class], 
                                methods: List[Method], 
                                edges: List[Edge]) -> Dict[str, int]:
        """
        Java 분석 결과 저장 (비동기 버전)
        """
        return self._save_java_analysis_sync(file_obj, classes, methods, edges)
            
    def _save_jsp_mybatis_analysis_sync(self, 
                                       file_obj: File, 
                                       sql_units: List[SqlUnit], 
                                       joins: List[Join], 
                                       filters: List[RequiredFilter],
                                       edges: List[Edge],
                                       vulnerabilities: List[Dict] = None) -> Dict[str, int]:
        """
        JSP/MyBatis 분석 결과 저장 (동기 버전)
        
        Args:
            file_obj: 파일 객체
            sql_units: SQL 구문 리스트
            joins: 조인 조건 리스트
            filters: 필터 조건 리스트
            edges: 의존성 엣지 리스트
            
        Returns:
            저장된 엔티티 수
        """
        
        with self._get_sync_session() as session:
            # 파일 저장
            session.add(file_obj)
            session.flush()
            
            saved_counts = {'files': 1, 'sql_units': 0, 'joins': 0, 'filters': 0, 'edges': 0}
            
            # SQL 구문 저장
            for sql_unit in sql_units:
                sql_unit.file_id = file_obj.file_id
                session.add(sql_unit)
                session.flush()
                
                # 해당 SQL 구문의 조인과 필터 저장
                sql_joins = [j for j in joins if j.sql_id is None]  # 임시로 None인 것들
                sql_filters = [f for f in filters if f.sql_id is None]
                
                for join_obj in sql_joins:
                    join_obj.sql_id = sql_unit.sql_id
                    session.add(join_obj)
                    
                for filter_obj in sql_filters:
                    filter_obj.sql_id = sql_unit.sql_id
                    session.add(filter_obj)
                    
                saved_counts['sql_units'] += 1
                
            saved_counts['joins'] = len(joins)
            saved_counts['filters'] = len(filters)
            
            # 의존성 엣지 저장 (유효한 엣지만)
            confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
            valid_edges = [edge for edge in edges 
                          if edge.src_id is not None and edge.dst_id is not None 
                          and edge.src_id != 0 and edge.dst_id != 0
                          and edge.confidence >= confidence_threshold]
            
            self.logger.debug(f"JSP/MyBatis 분석 - 전체 엣지: {len(edges)}, 유효한 엣지: {len(valid_edges)}")
            
            for edge in valid_edges:
                session.add(edge)
                saved_counts['edges'] += 1
            
            # 취약점 저장 (새로운 기능)
            saved_counts['vulnerabilities'] = 0
            if vulnerabilities:
                for vuln in vulnerabilities:
                    vuln_fix = VulnerabilityFix(
                        target_type='file',
                        target_id=file_obj.file_id,
                        vulnerability_type=vuln.get('type', 'UNKNOWN'),
                        severity=vuln.get('severity', 'MEDIUM'),
                        owasp_category=vuln.get('owasp_category', ''),
                        cwe_id=vuln.get('cwe_id', ''),
                        description=vuln.get('message', ''),
                        original_code=vuln.get('pattern', ''),
                        start_line=vuln.get('line_number', 0),
                        confidence=vuln.get('confidence', 0.8)
                    )
                    session.add(vuln_fix)
                    saved_counts['vulnerabilities'] += 1
                    
                self.logger.info(f"취약점 저장 완료: {saved_counts['vulnerabilities']}개")
                
            session.commit()
            return saved_counts

    async def save_jsp_mybatis_analysis(self, 
                                       file_obj: File, 
                                       sql_units: List[SqlUnit], 
                                       joins: List[Join], 
                                       filters: List[RequiredFilter],
                                       edges: List[Edge],
                                       vulnerabilities: List[Dict] = None) -> Dict[str, int]:
        """
        JSP/MyBatis 분석 결과 저장 (비동기 버전)
        """
        return self._save_jsp_mybatis_analysis_sync(file_obj, sql_units, joins, filters, edges, vulnerabilities)
            
    async def build_dependency_graph(self, project_id: int):
        """
        프로젝트의 의존성 그래프 구축
        
        Args:
            project_id: 프로젝트 ID
        """
        
        async with self._get_async_session() as session:
            # 메서드 호출 관계 해결
            await self._resolve_method_calls(session, project_id)
            
            # 테이블 사용 관계 해결  
            await self._resolve_table_usage(session, project_id)
            
            # PK-FK 관계 추론
            await self._infer_pk_fk_relationships(session, project_id)
            
            session.commit()
            
    async def _resolve_method_calls(self, session, project_id: int):
        """메서드 호출 관계 해결"""
        from ..models.database import EdgeHint, Method, Class, File
        import json as _json
        # 미해결된 메서드 호출 엣지들 조회
        unresolved_calls = session.query(Edge).filter(
            and_(
                Edge.edge_kind == 'call',
                Edge.dst_id.is_(None)
            )
        ).all()
        
        for edge in unresolved_calls:
            # 소스 메서드 정보 조회
            if edge.src_type == 'method':
                src_method = session.query(Method).filter(
                    Method.method_id == edge.src_id
                ).first()
                
                if src_method:
                    # 같은 프로젝트 내에서 호출 대상 메서드 찾기
                    called_method_name = ''
                    # 1) Edge.metadata(JSON) 우선 사용
                    try:
                        if getattr(edge, 'meta', None):
                            md = _json.loads(edge.meta)
                            called_method_name = md.get('called_name', '')
                    except Exception:
                        called_method_name = ''
                    # 2) EdgeHint 보조 사용
                    if not called_method_name:
                        hint_row = session.query(EdgeHint).filter(
                            and_(
                                EdgeHint.project_id == project_id,
                                EdgeHint.src_type == 'method',
                                EdgeHint.src_id == src_method.method_id,
                                EdgeHint.hint_type == 'method_call'
                            )
                        ).order_by(EdgeHint.created_at.desc()).first()
                        if hint_row:
                            try:
                                called_method_name = _json.loads(hint_row.hint).get('called_name', '')
                            except Exception:
                                called_method_name = ''
                    
                    if called_method_name:
                        # 1) 동일 클래스 내 메서드 우선 검색
                        target_method = session.query(Method).filter(
                            and_(
                                Method.class_id == src_method.class_id,
                                Method.name == called_method_name
                            )
                        ).first()
                        
                        # 2) 전역 검색 (패키지/임포트 정보 고려 필요)
                        if not target_method:
                            target_method = session.query(Method).join(Class).join(File).filter(
                                and_(
                                    Method.name == called_method_name,
                                    File.project_id == project_id
                                )
                            ).first()
                        
                        # 3) 호출 관계 엣지 업데이트
                        if target_method:
                            edge.dst_type = 'method'
                            edge.dst_id = target_method.method_id
                            edge.confidence = min(1.0, edge.confidence + 0.2)  # 해결된 호출에 신뢰도 보너스
                            
                            self.logger.debug(f"메서드 호출 해결: {src_method.name} -> {target_method.name}")
                        else:
                            # 해결되지 않은 호출은 신뢰도 감소
                            edge.confidence = max(0.1, edge.confidence - 0.3)
                            self.logger.debug(f"미해결 메서드 호출: {src_method.name} -> {called_method_name}")
                    
        session.commit()
        self.logger.info(f"메서드 호출 관계 해결 완료: {len(unresolved_calls)}개 처리")
                    
    async def _resolve_table_usage(self, session, project_id: int):
        """테이블 사용 관계 해결"""
        
        # SQL 구문에서 테이블 사용 관계 추출
        sql_units = session.query(SqlUnit).join(File).filter(
            File.project_id == project_id
        ).all()
        
        for sql_unit in sql_units:
            # 조인 테이블들에서 사용 관계 생성
            joins = session.query(Join).filter(
                Join.sql_id == sql_unit.sql_id
            ).all()
            
            for join in joins:
                # SQL -> 테이블 사용 엣지 생성 (유효한 테이블 ID가 있을 때만)
                if join.l_table:
                    # DB 스키마에서 테이블 찾기 (개선된 스키마 매칭)
                    default_owner = self.config.get('database', {}).get('default_schema', 'SAMPLE')
                    
                    # 1차: 기본 스키마에서 검색
                    query = session.query(DbTable).filter(DbTable.table_name == join.l_table.upper())
                    if default_owner:
                        db_table = query.filter(DbTable.owner == default_owner.upper()).first()
                        
                        # 2차: 기본 스키마에서 못 찾으면 전역 검색
                        if not db_table:
                            self.logger.debug(f"기본 스키마 '{default_owner}'에서 테이블 '{join.l_table}' 못 찾음, 전역 검색 시도")
                            db_table = session.query(DbTable).filter(DbTable.table_name == join.l_table.upper()).first()
                    else:
                        db_table = query.first()
                    
                    if db_table:
                        table_edge = Edge(
                            src_type='sql_unit',
                            src_id=sql_unit.sql_id,
                            dst_type='table',
                            dst_id=db_table.table_id,
                            edge_kind='use_table',
                            confidence=0.8
                        )
                        session.add(table_edge)
                    else:
                        self.logger.warning(f"테이블을 찾을 수 없음: {join.l_table} (스키마: {default_owner})")
                    
    async def _infer_pk_fk_relationships(self, session, project_id: int):
        """PK-FK 관계 추론"""
        
        # 조인 조건들을 분석하여 PK-FK 관계 추론
        joins = session.query(Join).join(SqlUnit).join(File).filter(
            File.project_id == project_id
        ).all()
        
        # 조인 패턴 분석
        join_patterns = {}
        
        for join in joins:
            pattern_key = f"{join.l_table}.{join.l_col}={join.r_table}.{join.r_col}"
            if pattern_key not in join_patterns:
                join_patterns[pattern_key] = []
            join_patterns[pattern_key].append(join)
            
        # 빈도가 높은 조인 패턴을 PK-FK로 추론
        for pattern, pattern_joins in join_patterns.items():
            if len(pattern_joins) >= 2:  # 2번 이상 나타나는 패턴
                for join in pattern_joins:
                    join.inferred_pkfk = 1
                    join.confidence = min(1.0, join.confidence + 0.2)
                    
    async def generate_project_summary(self, project_id: int) -> Dict[str, Any]:
        """
        프로젝트 분석 결과 요약 생성
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            요약 딕셔너리
        """
        
        async with self._get_async_session() as session:
            # 기본 통계
            file_count = session.query(File).filter(File.project_id == project_id).count()
            class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
            method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            sql_count = session.query(SqlUnit).join(File).filter(File.project_id == project_id).count()
            
            # 언어별 파일 수
            language_stats = session.query(File.language, func.count(File.file_id)).filter(
                File.project_id == project_id
            ).group_by(File.language).all()
            
            # 조인과 필터 통계
            join_count = session.query(Join).join(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).count()
            
            filter_count = session.query(RequiredFilter).join(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).count()
            
            # 의존성 엣지 통계
            edge_stats = session.query(Edge.edge_kind, func.count(Edge.edge_id)).group_by(
                Edge.edge_kind
            ).all()
            
            summary = {
                'basic_stats': {
                    'files': file_count,
                    'classes': class_count,
                    'methods': method_count,
                    'sql_units': sql_count,
                    'joins': join_count,
                    'filters': filter_count
                },
                'language_distribution': {lang: count for lang, count in language_stats},
                'dependency_stats': {kind: count for kind, count in edge_stats},
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
    async def save_enrichment_log(self, 
                                 target_type: str, 
                                 target_id: int, 
                                 pre_confidence: float,
                                 post_confidence: float,
                                 model: str,
                                 prompt_id: str,
                                 params: Dict[str, Any]):
        """
        LLM 보강 로그 저장
        
        Args:
            target_type: 대상 타입
            target_id: 대상 ID
            pre_confidence: 보강 전 신뢰도
            post_confidence: 보강 후 신뢰도
            model: 사용된 모델
            prompt_id: 프롬프트 ID
            params: 파라미터
        """
        
        async with self._get_async_session() as session:
            log_entry = EnrichmentLog(
                target_type=target_type,
                target_id=target_id,
                pre_conf=pre_confidence,
                post_conf=post_confidence,
                model=model,
                prompt_id=prompt_id,
                params=str(params)  # JSON 문자열로 저장
            )
            
            session.add(log_entry)
            session.commit()
            
    async def get_project_files(self, project_id: int, 
                               language: Optional[str] = None,
                               modified_since: Optional[datetime] = None) -> List[File]:
        """
        프로젝트의 파일 목록 조회
        
        Args:
            project_id: 프로젝트 ID
            language: 언어 필터 (선택적)
            modified_since: 수정 시간 필터 (선택적)
            
        Returns:
            파일 리스트
        """
        
        session = self.db_manager.get_session()
        
        try:
            query = session.query(File).filter(File.project_id == project_id)
            
            if language:
                query = query.filter(File.language == language)
                
            if modified_since:
                query = query.filter(File.mtime > modified_since)
                
            return query.all()
            
        finally:
            session.close()
            
    async def check_file_changes(self, project_id: int) -> List[Tuple[str, str]]:
        """
        파일 변경 사항 확인 (증분 분석용)
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            (파일경로, 변경타입) 튜플 리스트
        """
        
        session = self.db_manager.get_session()
        
        try:
            changes = []
            
            # DB에 있는 파일들
            db_files = {f.path: f.hash for f in session.query(File).filter(
                File.project_id == project_id
            ).all()}
            
            # 실제 파일 시스템의 파일들과 비교
            project = session.query(Project).filter(
                Project.project_id == project_id
            ).first()
            
            if project:
                # 실제 구현에서는 파일 시스템 스캔 로직 필요
                pass
                
            return changes
            
        finally:
            session.close()
