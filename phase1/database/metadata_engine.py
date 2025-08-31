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
import json

from models.database import (
    DatabaseManager, Project, File, Class, Method, SqlUnit,
    Join, RequiredFilter, Edge, Summary, EnrichmentLog,
    DbTable, DbColumn, DbPk, DbView, ParseResultModel, VulnerabilityFix,
)
from utils.logger import LoggerFactory, PerformanceLogger, ExceptionHandler
from utils.confidence_calculator import ConfidenceCalculator, ParseResult as ConfidenceParseResult
from llm.assist import LlmAssist
from llm.enricher import generate_text

class MetadataEngine:
    """메타데이터 저장 및 관리 엔진"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.logger = LoggerFactory.get_engine_logger()
        self.confidence_calculator = ConfidenceCalculator(config)
        self.llm_assist = LlmAssist(config, db_manager=self.db_manager, logger=self.logger, confidence_calculator=self.confidence_calculator)
        
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

                # 보강 훅: 저장 후 File ID를 사용하여 EnrichmentLog 기록
                try:
                    if hasattr(file_obj, 'file_id') and file_obj.file_id and self.llm_assist.should_assist(confidence):
                        _ret = self.llm_assist.assist_java(file_id=file_obj.file_id, file_path=file_path, original_confidence=confidence)
                        if _ret and isinstance(_ret, dict) and _ret.get('json') and not self.llm_assist.cfg.dry_run:
                            _added = self._augment_java_from_json(file_id=file_obj.file_id, data=_ret['json'])
                            if isinstance(_added, dict):
                                self.logger.info(f"LLM augment(java): +classes={_added.get('classes',0)}, +methods={_added.get('methods',0)}")
                except Exception as _e:
                    self.logger.debug(f"LLM assist(java) skipped: {_e}")

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

                # 보강 훅: 저장 후 File ID로 EnrichmentLog 기록
                try:
                    if hasattr(file_obj, 'file_id') and file_obj.file_id and self.llm_assist.should_assist(confidence):
                        _ret = self.llm_assist.assist_jsp(file_id=file_obj.file_id, file_path=file_path, original_confidence=confidence)
                        if _ret and isinstance(_ret, dict) and _ret.get('json') and not self.llm_assist.cfg.dry_run:
                            _added = self._augment_sql_from_json(file_id=file_obj.file_id, file_path=file_path, data=_ret['json'])
                            if isinstance(_added, dict):
                                self.logger.info(f"LLM augment(jsp/xml): +sql_units={_added.get('sql_units',0)}, +joins={_added.get('joins',0)}, +filters={_added.get('filters',0)}")
                except Exception as _e:
                    self.logger.debug(f"LLM assist(jsp/xml) skipped: {_e}")

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

    def _augment_java_from_json(self, file_id: int, data: Dict[str, Any]) -> Dict[str, int]:
        added = {"classes": 0, "methods": 0}
        if not isinstance(data, dict):
            return added
        classes = data.get("classes")
        if not isinstance(classes, list):
            return added
        with self._get_sync_session() as session:
            existing_classes = session.query(Class).filter(Class.file_id == file_id).all()
            class_key_to_row = {}
            for c in existing_classes:
                key = (c.fqn or c.name or "").strip()
                class_key_to_row[key] = c
            for c in classes:
                if not isinstance(c, dict):
                    continue
                name = (c.get("name") or "").strip()
                fqn = (c.get("fqn") or "").strip() if c.get("fqn") else None
                key = (fqn or name)
                if not key:
                    continue
                row = class_key_to_row.get(key)
                if row is None:
                    row = Class(
                        file_id=file_id,
                        fqn=fqn or name,
                        name=name or (fqn or "Unknown"),
                        start_line=c.get("start_line"),
                        end_line=c.get("end_line"),
                        modifiers=json.dumps([]),
                        annotations=json.dumps([]),
                    )
                    session.add(row)
                    session.flush()
                    class_key_to_row[key] = row
                    added["classes"] += 1
                methods = c.get("methods") or []
                if not isinstance(methods, list):
                    continue
                existing_methods = session.query(Method).filter(Method.class_id == row.class_id).all()
                method_keys = set((m.name or "", m.signature or m.name or "") for m in existing_methods)
                for m in methods:
                    if not isinstance(m, dict):
                        continue
                    mname = (m.get("name") or "").strip()
                    if not mname:
                        continue
                    sig = (m.get("signature") or f"{mname}()")
                    keym = (mname, sig)
                    if keym in method_keys:
                        continue
                    mrow = Method(
                        class_id=row.class_id,
                        name=mname,
                        signature=sig,
                        return_type=m.get("return_type"),
                        start_line=m.get("start_line"),
                        end_line=m.get("end_line"),
                        annotations=json.dumps([]),
                    )
                    session.add(mrow)
                    method_keys.add(keym)
                    added["methods"] += 1
            session.commit()
        return added

    def _augment_sql_from_json(self, file_id: int, file_path: str, data: Dict[str, Any]) -> Dict[str, int]:
        added = {"sql_units": 0, "joins": 0, "filters": 0}
        if not isinstance(data, dict):
            return added
        units = data.get("sql_units")
        if not isinstance(units, list):
            return added
        origin = 'jsp' if file_path.endswith('.jsp') else ('mybatis' if file_path.endswith('.xml') else 'unknown')
        with self._get_sync_session() as session:
            existing_units = session.query(SqlUnit).filter(SqlUnit.file_id == file_id).all()
            existing_fp = set((u.normalized_fingerprint or "") for u in existing_units)
            for u in units:
                if not isinstance(u, dict):
                    continue
                stmt_kind = (u.get("stmt_kind") or "select").lower()
                tables = u.get("tables") or []
                joins = u.get("joins") or []
                filters = u.get("filters") or []
                fp_obj = {
                    "k": stmt_kind,
                    "t": sorted([str(t).upper() for t in tables if t]),
                    "j": sorted([
                        {"l": j.get("l_table"), "lc": j.get("l_col"), "o": j.get("op"), "r": j.get("r_table"), "rc": j.get("r_col")}
                        for j in joins if isinstance(j, dict)
                    ], key=lambda x: (str(x.get("l")), str(x.get("lc")), str(x.get("r")), str(x.get("rc"))))
                }
                try:
                    fp = json.dumps(fp_obj, sort_keys=True)
                except Exception:
                    fp = stmt_kind
                if fp in existing_fp:
                    continue
                su = SqlUnit(
                    file_id=file_id,
                    origin=origin,
                    mapper_ns=None,
                    stmt_id=None,
                    start_line=None,
                    end_line=None,
                    stmt_kind=stmt_kind,
                    normalized_fingerprint=fp,
                )
                session.add(su)
                session.flush()
                added["sql_units"] += 1
                for j in joins:
                    if not isinstance(j, dict):
                        continue
                    jr = Join(
                        sql_id=su.sql_id,
                        l_table=(j.get("l_table") or None),
                        l_col=(j.get("l_col") or None),
                        op=(j.get("op") or "="),
                        r_table=(j.get("r_table") or None),
                        r_col=(j.get("r_col") or None),
                        inferred_pkfk=0,
                        confidence=0.6,
                    )
                    session.add(jr)
                    added["joins"] += 1
                for f in filters:
                    if not isinstance(f, dict):
                        continue
                    fr = RequiredFilter(
                        sql_id=su.sql_id,
                        table_name=(f.get("table_name") or None),
                        column_name=(f.get("column_name") or None),
                        op=(f.get("op") or "="),
                        value_repr=(f.get("value_repr") or None),
                        always_applied=1 if f.get("always_applied") else 0,
                        confidence=0.6,
                    )
                    session.add(fr)
                    added["filters"] += 1
            session.commit()
        return added

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
                        vulnerability_type=vuln.vuln_type.value if hasattr(vuln.vuln_type, 'value') else str(vuln.vuln_type),
                        severity=vuln.severity.value if hasattr(vuln.severity, 'value') else str(vuln.severity),
                        owasp_category=getattr(vuln, 'owasp_category', ''),
                        cwe_id=getattr(vuln, 'cwe_id', ''),
                        description=vuln.message,
                        original_code=vuln.pattern,
                        start_line=vuln.line_number,
                        confidence=vuln.confidence
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
        from models.database import EdgeHint, Method, Class, File
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
                    default_owner = self.config.get('database', {}).get('project', {}).get('default_schema', 'SAMPLE')
                    
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
            
    # ---- LLM-driven enrichment tasks ----
    def llm_enrich_table_and_column_comments(self, *, max_tables: int = 50, max_columns: int = 100, lang: str = 'ko') -> Dict[str, int]:
        updated = {"tables": 0, "columns": 0}
        provider = self.config.get('llm_assist', {}).get('provider', 'auto') if isinstance(self.config, dict) else 'auto'
        dry_run = bool(self.config.get('llm_assist', {}).get('dry_run', False)) if isinstance(self.config, dict) else False
        temperature = float(self.config.get('llm_assist', {}).get('temperature', 0.0)) if isinstance(self.config, dict) else 0.0
        max_tokens = int(self.config.get('llm_assist', {}).get('max_tokens', 256)) if isinstance(self.config, dict) else 256
        with self._get_sync_session() as session:
            q_tables = session.query(DbTable).limit(max_tables * 5).all()
            picked = []
            for t in q_tables:
                tc = (t.table_comment or '').strip()
                if not tc or len(tc) < 4 or tc.lower() in ('tbd', 'todo', 'unknown'):
                    picked.append(t)
                if len(picked) >= max_tables:
                    break
            for t in picked:
                cols = [c.column_name for c in getattr(t, 'columns', [])]
                system = f"너는 데이터베이스 테이블 설명 작성기이다. 한국어({lang})로 간결하고 정확히 한두 문장으로 설명하라."
                user = (
                    f"테이블명: {t.owner + '.' if t.owner else ''}{t.table_name}\n"
                    f"컬럼들: {', '.join(cols[:30])}"
                )
                try:
                    text = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens, dry_run=dry_run)
                except Exception as e:
                    self.logger.debug(f"LLM table comment skipped: {t.table_name}: {e}")
                    continue
                t.table_comment = text
                updated["tables"] += 1
            q_cols = session.query(DbColumn).limit(max_columns * 5).all()
            pickedc = []
            for c in q_cols:
                cc = (c.column_comment or '').strip()
                if not cc or len(cc) < 3 or cc.lower() in ('tbd', 'todo', 'unknown'):
                    pickedc.append(c)
                if len(pickedc) >= max_columns:
                    break
            for c in pickedc:
                table = session.query(DbTable).filter(DbTable.table_id == c.table_id).first()
                tname = f"{getattr(table, 'owner', '') + '.' if getattr(table, 'owner', None) else ''}{getattr(table, 'table_name', '')}"
                system = f"너는 데이터베이스 컬럼 설명 작성기이다. 한국어({lang})로 한 문장으로 설명하라."
                user = f"테이블: {tname}\n컬럼: {c.column_name}\n데이터타입: {c.data_type or ''}\nNULL 허용: {c.nullable or ''}"
                try:
                    text = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens, dry_run=dry_run)
                except Exception as e:
                    self.logger.debug(f"LLM column comment skipped: {tname}.{c.column_name}: {e}")
                    continue
                c.column_comment = text
                updated["columns"] += 1
            session.commit()
        return updated

    def llm_summarize_sql_units(self, *, max_items: int = 50, lang: str = 'ko') -> int:
        created = 0
        provider = self.config.get('llm_assist', {}).get('provider', 'auto') if isinstance(self.config, dict) else 'auto'
        dry_run = bool(self.config.get('llm_assist', {}).get('dry_run', False)) if isinstance(self.config, dict) else False
        temperature = float(self.config.get('llm_assist', {}).get('temperature', 0.0)) if isinstance(self.config, dict) else 0.0
        max_tokens = int(self.config.get('llm_assist', {}).get('max_tokens', 256)) if isinstance(self.config, dict) else 256
        with self._get_sync_session() as session:
            existing_map = {(s.target_type, s.target_id) for s in session.query(Summary).filter(Summary.summary_type == 'logic').all()}
            units = session.query(SqlUnit).limit(max_items * 3).all()
            for u in units:
                key = ('sql_unit', u.sql_id)
                if key in existing_map:
                    continue
                joins = session.query(Join).filter(Join.sql_id == u.sql_id).all()
                filters = session.query(RequiredFilter).filter(RequiredFilter.sql_id == u.sql_id).all()
                system = f"너는 SQL 분석 보조 AI다. 한국어({lang})로 한두 문장 요약을 작성하라."
                jtxt = "; ".join([f"{j.l_table}.{j.l_col} {j.op} {j.r_table}.{j.r_col}" for j in joins if j.l_table and j.r_table])
                ftxt = "; ".join([f"{f.table_name}.{f.column_name} {f.op} {f.value_repr}" for f in filters if f.column_name])
                # Try to include raw snippet when possible
                snippet = ''
                try:
                    if getattr(u, 'start_line', None) and getattr(u, 'end_line', None) and getattr(u, 'file', None):
                        path = u.file.path
                        lines = open(path, 'r', encoding='utf-8', errors='ignore').read().splitlines()
                        s = max(0, (u.start_line or 1) - 1)
                        e = min(len(lines), (u.end_line or s + 1))
                        snippet = "\n".join(lines[s:e])
                except Exception:
                    snippet = ''
                # f-string 표현식 내의 백슬래시(\n) 사용은 문법 오류를 유발하므로 미리 구성
                snippet_block = f"원문:\n{snippet}" if snippet else ""
                user = (
                    f"SQL 종류: {u.stmt_kind}\n"
                    f"조인: {jtxt or '없음'}\n"
                    f"필터: {ftxt or '없음'}\n"
                    f"{snippet_block}"
                )
                try:
                    text = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens, dry_run=dry_run)
                except Exception as e:
                    self.logger.debug(f"LLM sql summary skipped: {u.sql_id}: {e}")
                    continue
                sm = Summary(target_type='sql_unit', target_id=u.sql_id, summary_type='logic', lang=lang, content=text, confidence=0.7)
                session.add(sm)
                created += 1
            session.commit()
        return created

    def llm_summarize_methods(self, *, max_items: int = 50, lang: str = 'ko') -> int:
        """호출 중심성과 공개 메소드 보너스를 가중해 우선순위 높은 메소드부터 요약한다.
        간단/전형적 메소드는 휴리스틱 요약으로 비용 없이 처리하여 커버리지 상승.
        """
        created = 0
        provider = self.config.get('llm_assist', {}).get('provider', 'auto') if isinstance(self.config, dict) else 'auto'
        dry_run = bool(self.config.get('llm_assist', {}).get('dry_run', False)) if isinstance(self.config, dict) else False
        temperature = float(self.config.get('llm_assist', {}).get('temperature', 0.0)) if isinstance(self.config, dict) else 0.0
        max_tokens = int(self.config.get('llm_assist', {}).get('max_tokens', 256)) if isinstance(self.config, dict) else 256
        from collections import defaultdict
        with self._get_sync_session() as session:
            existing_map = {(s.target_type, s.target_id) for s in session.query(Summary).filter(Summary.summary_type == 'logic').all()}
            # Build simple centrality from call edges
            in_deg = defaultdict(int); out_deg = defaultdict(int)
            for (mid,) in session.query(Edge.dst_id).filter(Edge.edge_kind == 'call', Edge.dst_type == 'method').all():
                if mid:
                    in_deg[mid] += 1
            for (mid,) in session.query(Edge.src_id).filter(Edge.edge_kind == 'call', Edge.src_type == 'method').all():
                if mid:
                    out_deg[mid] += 1
            methods = session.query(Method).all()
            scored = []
            for m in methods:
                if ('method', m.method_id) in existing_map:
                    continue
                score = in_deg.get(m.method_id, 0) * 2 + out_deg.get(m.method_id, 0)
                mods = getattr(m, 'modifiers', '') or ''
                if isinstance(mods, str) and 'public' in mods:
                    score += 2
                scored.append((score, m))
            scored.sort(key=lambda x: x[0], reverse=True)

            def _heuristic_method_summary(m: Method) -> Optional[str]:
                name = (m.name or '').lower()
                # Heuristic by name
                if name.startswith('get') and not name.startswith('get$'):
                    return '객체 속성 값을 반환하는 getter 메소드'
                if name.startswith('set') and not name.startswith('set$'):
                    return '객체 속성 값을 설정하는 setter 메소드'
                if name.startswith('is'):
                    return '불리언 상태를 반환하는 확인 메소드'
                if name in ('tostring', '__str__'):
                    return '객체 내용을 문자열로 변환하는 메소드'
                if name in ('equals', '__eq__'):
                    return '두 객체의 동등성을 비교하는 메소드'
                if name in ('hashcode', '__hash__'):
                    return '객체 해시코드를 계산하는 메소드'
                # Optional: short body heuristic (if line info available)
                try:
                    if getattr(m, 'start_line', None) and getattr(m, 'end_line', None):
                        # load file content via class -> file
                        cl = session.query(Class).filter(Class.class_id == m.class_id).first()
                        if cl:
                            f = session.query(File).filter(File.file_id == cl.file_id).first()
                            if f and f.path:
                                lines = open(f.path, 'r', encoding='utf-8', errors='ignore').read().splitlines()
                                s = max(0, (m.start_line or 1) - 1); e = min(len(lines), (m.end_line or s+1))
                                snippet = '\n'.join(lines[s:e])
                                # If very short and contains only return or single call
                                if (e - s) <= 6:
                                    if 'return' in snippet and snippet.count('return') == 1 and snippet.count('(') <= 2:
                                        return '간단한 반환/위임 로직을 수행하는 메소드'
                except Exception:
                    pass
                return None

            for _, m in scored[: max_items * 4]:
                if created >= max_items:
                    break
                # Heuristic first (free coverage)
                h = _heuristic_method_summary(m)
                if h:
                    sm = Summary(target_type='method', target_id=m.method_id, summary_type='logic', lang=lang, content=h, confidence=0.55)
                    session.add(sm)
                    created += 1
                    continue
                # Otherwise LLM
                cl = session.query(Class).filter(Class.class_id == m.class_id).first()
                system = f"너는 코드 요약 보조 AI다. 한국어({lang})로 한두 문장으로 메소드 역할을 추정 요약하라."
                user = f"클래스: {getattr(cl, 'fqn', '')}\n메소드: {m.name}\n시그니처: {m.signature or ''}"
                try:
                    text = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens, dry_run=dry_run)
                except Exception as e:
                    self.logger.debug(f"LLM method summary skipped: {m.method_id}: {e}")
                    continue
                sm = Summary(target_type='method', target_id=m.method_id, summary_type='logic', lang=lang, content=text, confidence=0.6)
                session.add(sm)
                created += 1
            session.commit()
        return created

    def llm_summarize_jsp_files(self, *, max_items: int = 50, lang: str = 'ko') -> int:
        """JSP 파일 내용을 샘플링하여 파일 단위 요약을 생성한다."""
        created = 0
        provider = self.config.get('llm_assist', {}).get('provider', 'auto') if isinstance(self.config, dict) else 'auto'
        dry_run = bool(self.config.get('llm_assist', {}).get('dry_run', False)) if isinstance(self.config, dict) else False
        temperature = float(self.config.get('llm_assist', {}).get('temperature', 0.0)) if isinstance(self.config, dict) else 0.0
        max_tokens = int(self.config.get('llm_assist', {}).get('max_tokens', 256)) if isinstance(self.config, dict) else 256
        file_max_lines = int(self.config.get('llm_assist', {}).get('file_max_lines', 1200)) if isinstance(self.config, dict) else 1200
        with self._get_sync_session() as session:
            existing_map = {(s.target_type, s.target_id) for s in session.query(Summary).filter(Summary.summary_type == 'logic').all()}
            files = session.query(File).filter(File.path.like('%.jsp')).limit(max_items * 5).all()
            for f in files:
                key = ('file', f.file_id)
                if key in existing_map:
                    continue
                # read snippet
                try:
                    text = open(f.path, 'r', encoding='utf-8', errors='ignore').read()
                except Exception:
                    text = ''
                lines = text.splitlines()
                if len(lines) > file_max_lines:
                    head = lines[: file_max_lines // 2]
                    tail = lines[-file_max_lines // 2 :]
                    snippet = "\n".join(head + ["\n<%-- ...snip... --%>\n"] + tail)
                else:
                    snippet = text
                system = f"너는 JSP 화면/서버 코드 요약 보조 AI다. 한국어({lang})로 이 파일의 역할을 한두 문장으로 요약하라."
                user = f"<JSP>\n{snippet}\n</JSP>"
                try:
                    summary = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens, dry_run=dry_run)
                except Exception as e:
                    self.logger.debug(f"LLM jsp summary skipped: {f.path}: {e}")
                    continue
                sm = Summary(target_type='file', target_id=f.file_id, summary_type='logic', lang=lang, content=summary, confidence=0.6)
                session.add(sm)
                created += 1
                if created >= max_items:
                    break
            session.commit()
        return created

    def llm_infer_join_keys(self, *, max_items: int = 50) -> int:
        """조인 키 추론(LLM/휴리스틱)으로 Join.inferred_pkfk/ confidence 보강."""
        updated = 0
        dry_run = bool(self.config.get('llm_assist', {}).get('dry_run', False)) if isinstance(self.config, dict) else False
        provider = self.config.get('llm_assist', {}).get('provider', 'auto') if isinstance(self.config, dict) else 'auto'
        temperature = float(self.config.get('llm_assist', {}).get('temperature', 0.0)) if isinstance(self.config, dict) else 0.0
        max_tokens = int(self.config.get('llm_assist', {}).get('max_tokens', 256)) if isinstance(self.config, dict) else 256
        default_owner = self.config.get('database', {}).get('default_schema') if isinstance(self.config, dict) else None

        def _coerce_json(text: str):
            import json as _json
            try:
                return _json.loads(text)
            except Exception:
                try:
                    s = text.find('{'); e = text.rfind('}')
                    if s != -1 and e != -1 and e > s:
                        return _json.loads(text[s:e+1])
                except Exception:
                    return {}
            return {}

        with self._get_sync_session() as session:
            joins = session.query(Join).filter(Join.inferred_pkfk == 0).limit(max_items * 3).all()
            for j in joins:
                if not (j.l_table and j.l_col and j.r_table and j.r_col):
                    continue
                ltab = j.l_table.upper(); rtab = j.r_table.upper()
                # Load table meta
                def _find_table(name: str):
                    q = session.query(DbTable).filter(DbTable.table_name == name)
                    return (q.filter(DbTable.owner == default_owner.upper()).first() if default_owner else q.first())
                lt = _find_table(ltab); rt = _find_table(rtab)
                lcols = [c.column_name for c in getattr(lt, 'columns', [])] if lt else []
                rcols = [c.column_name for c in getattr(rt, 'columns', [])] if rt else []
                lpk = [p.column_name for p in getattr(lt, 'pk_columns', [])] if lt else []
                rpk = [p.column_name for p in getattr(rt, 'pk_columns', [])] if rt else []

                if dry_run:
                    # Heuristic suitable for CI
                    l_name = (j.l_col or '').lower(); r_name = (j.r_col or '').lower()
                    likely = (l_name == 'id') or (r_name == 'id') or l_name.endswith('_id') or r_name.endswith('_id')
                    if likely:
                        j.inferred_pkfk = 1
                        j.confidence = min(1.0, (j.confidence or 0.6) + 0.2)
                        updated += 1
                    if updated >= max_items:
                        break
                    continue

                # LLM prompt
                system = (
                    "너는 데이터베이스 조인 분석기다. 주어진 두 테이블과 조인 조건을 보고 PK-FK 방향을 판단하고, "
                    "엄격한 JSON만 출력하라. 설명/문장은 금지."
                )
                user = (
                    f"LEFT: {ltab} (pk={lpk}) cols={lcols}\n"
                    f"RIGHT: {rtab} (pk={rpk}) cols={rcols}\n"
                    f"JOIN: {j.l_table}.{j.l_col} {j.op or '='} {j.r_table}.{j.r_col}\n"
                    "스키마: {\n  \"pk_table\": str, \"pk_column\": str, \n  \"fk_table\": str, \"fk_column\": str, \n  \"confidence\": 0.0..1.0\n}"
                )
                try:
                    text = generate_text(system, user, provider=provider, temperature=temperature, max_tokens=max_tokens)
                    data = _coerce_json(text if isinstance(text, str) else str(text))
                    pk_table = (data.get('pk_table') or '').upper()
                    pk_column = (data.get('pk_column') or '').upper()
                    fk_table = (data.get('fk_table') or '').upper()
                    fk_column = (data.get('fk_column') or '').upper()
                    conf = float(data.get('confidence', 0.6))
                    # Sanity check alignment with join
                    sides_ok = {
                        (j.l_table.upper(), j.l_col.upper(), j.r_table.upper(), j.r_col.upper()),
                        (j.r_table.upper(), j.r_col.upper(), j.l_table.upper(), j.l_col.upper()),
                    }
                    if (pk_table, pk_column, fk_table, fk_column) in sides_ok or (fk_table, fk_column, pk_table, pk_column) in sides_ok:
                        j.inferred_pkfk = 1
                        j.confidence = max(j.confidence or 0.6, min(1.0, conf))
                        updated += 1
                except Exception as e:
                    self.logger.debug(f"LLM join infer skipped: {j.l_table}.{j.l_col} ~ {j.r_table}.{j.r_col}: {e}")
                if updated >= max_items:
                    break
            session.commit()
        return updated

    def llm_suggest_edge_hints_for_unresolved_calls(self, *, max_items: int = 50) -> int:
        """해소되지 않은 메소드 호출 Edge에 대해 LLM/휴리스틱 힌트(EdgeHint) 생성."""
        created = 0
        with self._get_sync_session() as session:
            unresolved = session.query(Edge).filter(and_(Edge.edge_kind == 'call', Edge.dst_id.is_(None))).limit(max_items * 3).all()
            for e in unresolved:
                if created >= max_items:
                    break
                # Extract called name from meta if present
                called_name = None
                try:
                    if getattr(e, 'meta', None):
                        import json as _json
                        md = _json.loads(e.meta)
                        called_name = md.get('called_name')
                except Exception:
                    called_name = None
                if not called_name:
                    continue
                from models.database import EdgeHint
                hint = {"called_name": called_name}
                row = EdgeHint(
                    project_id=1,  # unknown here; left as 1 for hint bucket
                    src_type=e.src_type,
                    src_id=e.src_id or 0,
                    hint_type='method_call',
                    hint=json.dumps(hint, ensure_ascii=False),
                    confidence=0.4,
                )
                session.add(row)
                created += 1
            session.commit()
        return created

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
