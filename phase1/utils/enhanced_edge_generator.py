#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
향상된 엣지 생성기 모듈
소스 코드를 동적으로 분석하여 실제 관계를 파악하고 메타DB에 엣지 정보를 생성합니다.
AST 파싱, 정규식 분석, LLM 분석을 결합한 다층적 접근법을 사용합니다.
"""

import logging
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
from sqlalchemy.orm import Session
from phase1.models.database import Edge, Class, Method, File, SqlUnit, DbTable, DbColumn, Project
from phase1.parsers.java.javaparser_enhanced import JavaParserEnhanced
from phase1.parsers.jsp.jsp_parser import JSPParser
from phase1.parsers.mybatis.mybatis_parser import MyBatisParser
from phase1.llm.enricher import LLMMetadataEnricher
from phase1.utils.chunk_location_tracker import ChunkLocationTracker

logger = logging.getLogger(__name__)


class EnhancedEdgeGenerator:
    """향상된 엣지 생성기 - 동적 분석 기반"""
    
    def __init__(self, db_session: Session, project_path: str, project_id: int = 1):
        self.db_session = db_session
        self.project_path = Path(project_path)
        self.project_id = project_id
        self.edge_count = 0
        
        # 파서 초기화
        self.java_parser = JavaParserEnhanced()
        self.jsp_parser = JSPParser()
        self.mybatis_parser = MyBatisParser()
        self.llm_enricher = LLMMetadataEnricher()
        
        # 위치 추적기 초기화
        self.location_tracker = ChunkLocationTracker(db_session)
        
        # 캐시 초기화
        self.class_cache: Dict[str, Any] = {}
        self.file_cache: Dict[str, Any] = {}
        self.import_cache: Dict[str, Set[str]] = {}
        self.annotation_cache: Dict[str, List[str]] = {}
        
    def generate_all_edges(self) -> int:
        """모든 엣지를 동적으로 생성합니다."""
        logger.info(f"향상된 엣지 생성 시작: {self.project_path}")
        
        try:
            # 기존 엣지 삭제
            self._clear_existing_edges()
            
            # 프로젝트 소스 파일 스캔
            self._scan_project_files()
            
            # 1단계: 파서 기반 엣지 생성
            self._generate_java_dependency_edges()
            self._generate_mybatis_mapping_edges()
            self._generate_jsp_controller_edges()
            self._generate_db_relationship_edges()
            
            # 2단계: SQL 조인 기반 엣지 생성
            self._generate_sql_join_edges()
            
            # 3단계: LLM 기반 엣지 생성
            self._generate_llm_inferred_edges()
            
            # 4단계: 엣지 검증 및 정제
            self._validate_and_refine_edges()
            
            logger.info(f"엣지 생성 완료: {self.edge_count}개")
            return self.edge_count
            
        except Exception as e:
            logger.error(f"엣지 생성 중 오류 발생: {e}", exc_info=True)
            raise
    
    def _clear_existing_edges(self):
        """기존 엣지를 삭제합니다."""
        deleted_count = self.db_session.query(Edge).filter(
            Edge.project_id == self.project_id
        ).delete()
        logger.info(f"기존 엣지 삭제 완료: {deleted_count}개")
    
    def _scan_project_files(self):
        """프로젝트 파일들을 스캔하여 캐시를 구축합니다."""
        logger.info("프로젝트 파일 스캔 시작")
        
        # Java 파일 스캔
        java_files = list(self.project_path.rglob("*.java"))
        for java_file in java_files:
            self._cache_java_file(java_file)
        
        # XML 파일 스캔
        xml_files = list(self.project_path.rglob("*.xml"))
        for xml_file in xml_files:
            if 'mybatis' in str(xml_file) or 'mapper' in str(xml_file):
                self._cache_xml_file(xml_file)
        
        # JSP 파일 스캔
        jsp_files = list(self.project_path.rglob("*.jsp"))
        for jsp_file in jsp_files:
            self._cache_jsp_file(jsp_file)
        
        logger.info(f"파일 스캔 완료: Java {len(java_files)}, XML {len(xml_files)}, JSP {len(jsp_files)}")
    
    def _cache_java_file(self, java_file: Path):
        """Java 파일을 분석하여 캐시에 저장합니다."""
        try:
            analysis_result = self.java_parser.analyze_file(str(java_file))
            
            if analysis_result:
                file_key = str(java_file.relative_to(self.project_path))
                self.file_cache[file_key] = analysis_result
                
                # 클래스 캐시 구축
                for class_info in analysis_result.get('classes', []):
                    class_fqn = class_info.get('fqn')
                    if class_fqn:
                        self.class_cache[class_fqn] = {
                            'file_path': file_key,
                            'class_info': class_info
                        }
                
                # Import 캐시 구축
                imports = analysis_result.get('imports', [])
                self.import_cache[file_key] = set(imports)
                
                # 어노테이션 캐시 구축
                annotations = []
                for class_info in analysis_result.get('classes', []):
                    annotations.extend(class_info.get('annotations', []))
                    for method in class_info.get('methods', []):
                        annotations.extend(method.get('annotations', []))
                self.annotation_cache[file_key] = annotations
                
        except Exception as e:
            logger.warning(f"Java 파일 분석 실패 {java_file}: {e}")
    
    def _cache_xml_file(self, xml_file: Path):
        """XML 파일을 분석하여 캐시에 저장합니다."""
        try:
            analysis_result = self.mybatis_parser.parse_file(str(xml_file))
            
            if analysis_result:
                file_key = str(xml_file.relative_to(self.project_path))
                self.file_cache[file_key] = analysis_result
                
        except Exception as e:
            logger.warning(f"XML 파일 분석 실패 {xml_file}: {e}")
    
    def _cache_jsp_file(self, jsp_file: Path):
        """JSP 파일을 분석하여 캐시에 저장합니다."""
        try:
            analysis_result = self.jsp_parser.parse_file(str(jsp_file))
            
            if analysis_result:
                file_key = str(jsp_file.relative_to(self.project_path))
                self.file_cache[file_key] = analysis_result
                
        except Exception as e:
            logger.warning(f"JSP 파일 분석 실패 {jsp_file}: {e}")
    
    def _generate_java_dependency_edges(self):
        """Java 클래스 간 의존성 엣지를 동적으로 생성합니다."""
        logger.info("Java 의존성 엣지 생성 시작")
        
        for file_path, file_analysis in self.file_cache.items():
            if not file_path.endswith('.java'):
                continue
            
            for class_info in file_analysis.get('classes', []):
                class_fqn = class_info.get('fqn')
                if not class_fqn:
                    continue
                
                # 1. Import 기반 의존성
                self._create_import_dependencies(class_fqn, file_path)
                
                # 2. Field 타입 기반 의존성
                self._create_field_dependencies(class_fqn, class_info)
                
                # 3. Method 파라미터/반환타입 기반 의존성
                self._create_method_dependencies(class_fqn, class_info)
                
                # 4. 어노테이션 기반 의존성 (@Autowired 등)
                self._create_annotation_dependencies(class_fqn, class_info)
    
    def _create_import_dependencies(self, class_fqn: str, file_path: str):
        """Import 문 기반 의존성 엣지 생성"""
        imports = self.import_cache.get(file_path, set())
        
        for import_name in imports:
            # 프로젝트 내부 클래스만 처리 (com.example로 시작하는 것)
            if import_name.startswith('com.example'):
                if import_name in self.class_cache:
                    src_class = self._get_class_from_db(class_fqn)
                    dst_class = self._get_class_from_db(import_name)
                    
                    if src_class and dst_class:
                        self._create_edge_safe(
                            src_type='class',
                            src_id=src_class.class_id,
                            dst_type='class',
                            dst_id=dst_class.class_id,
                            edge_kind='import',
                            confidence=0.9,
                            meta=f"Import dependency: {class_fqn} → {import_name}"
                        )
    
    def _create_field_dependencies(self, class_fqn: str, class_info: Dict):
        """필드 타입 기반 의존성 엣지 생성"""
        fields = class_info.get('fields', [])
        
        for field in fields:
            field_type = field.get('type', '')
            
            # 프로젝트 내부 타입 체크
            if self._is_project_class(field_type):
                src_class = self._get_class_from_db(class_fqn)
                dst_class = self._get_class_from_db(field_type)
                
                if src_class and dst_class:
                    # @Autowired 필드는 dependency로, 일반 필드는 reference로
                    edge_kind = 'dependency' if self._has_autowired_annotation(field) else 'reference'
                    confidence = 0.8 if edge_kind == 'dependency' else 0.6
                    
                    self._create_edge_safe(
                        src_type='class',
                        src_id=src_class.class_id,
                        dst_type='class',
                        dst_id=dst_class.class_id,
                        edge_kind=edge_kind,
                        confidence=confidence,
                        meta=f"Field dependency: {class_fqn}.{field.get('name')} → {field_type}"
                    )
    
    def _create_method_dependencies(self, class_fqn: str, class_info: Dict):
        """메서드 파라미터/반환타입 기반 의존성 엣지 생성"""
        methods = class_info.get('methods', [])
        
        for method in methods:
            # 반환 타입
            return_type = method.get('return_type', '')
            if self._is_project_class(return_type):
                self._create_class_reference_edge(class_fqn, return_type, 'return_type')
            
            # 파라미터 타입들
            parameters = method.get('parameters', [])
            for param in parameters:
                param_type = param.get('type', '')
                if self._is_project_class(param_type):
                    self._create_class_reference_edge(class_fqn, param_type, 'parameter')
    
    def _create_annotation_dependencies(self, class_fqn: str, class_info: Dict):
        """어노테이션 기반 의존성 엣지 생성"""
        # Spring 어노테이션 기반 관계 추론
        if self._has_controller_annotation(class_info):
            # Controller는 Service에 의존
            service_classes = self._find_related_service_classes(class_fqn)
            for service_class in service_classes:
                self._create_spring_dependency_edge(class_fqn, service_class, 'controller_service')
        
        elif self._has_service_annotation(class_info):
            # Service는 Mapper에 의존
            mapper_classes = self._find_related_mapper_classes(class_fqn)
            for mapper_class in mapper_classes:
                self._create_spring_dependency_edge(class_fqn, mapper_class, 'service_mapper')
    
    def _generate_mybatis_mapping_edges(self):
        """MyBatis XML 매퍼와 Java 인터페이스 간 엣지 생성"""
        logger.info("MyBatis 매핑 엣지 생성 시작")
        
        for file_path, file_analysis in self.file_cache.items():
            if not file_path.endswith('.xml'):
                continue
            
            namespace = file_analysis.get('namespace')
            if not namespace:
                continue
            
            # XML 파일과 Java 인터페이스 연결
            xml_file_db = self._get_file_from_db(file_path)
            java_interface = self._get_class_from_db(namespace)
            
            if xml_file_db and java_interface:
                self._create_edge_safe(
                    src_type='file',
                    src_id=xml_file_db.file_id,
                    dst_type='class',
                    dst_id=java_interface.class_id,
                    edge_kind='implements',
                    confidence=0.95,
                    meta=f"MyBatis mapping: {file_path} implements {namespace}"
                )
            
            # SQL Unit과 테이블 관계
            sql_units = file_analysis.get('sql_units', [])
            for sql_unit in sql_units:
                self._create_sql_table_edges(sql_unit, file_path)
    
    def _generate_jsp_controller_edges(self):
        """JSP 파일과 Controller 간 엣지 생성"""
        logger.info("JSP Controller 엣지 생성 시작")
        
        for file_path, file_analysis in self.file_cache.items():
            if not file_path.endswith('.jsp'):
                continue
            
            # JSP에서 참조하는 Controller 찾기
            form_actions = file_analysis.get('form_actions', [])
            url_patterns = file_analysis.get('url_patterns', [])
            
            all_urls = form_actions + url_patterns
            
            for url in all_urls:
                controller_method = self._find_controller_method_by_url(url)
                if controller_method:
                    jsp_file_db = self._get_file_from_db(file_path)
                    method_db = self._get_method_from_db(controller_method)
                    
                    if jsp_file_db and method_db:
                        self._create_edge_safe(
                            src_type='file',
                            src_id=jsp_file_db.file_id,
                            dst_type='method',
                            dst_id=method_db.method_id,
                            edge_kind='calls',
                            confidence=0.8,
                            meta=f"JSP calls controller: {file_path} → {controller_method}"
                        )
    
    def _generate_db_relationship_edges(self):
        """데이터베이스 테이블 간 관계 엣지 생성"""
        logger.info("DB 관계 엣지 생성 시작")
        
        # 1. 스키마 정보 기반 FK 관계
        self._create_schema_based_relationships()
        
        # 2. MyBatis JOIN 쿼리 기반 관계
        self._create_join_based_relationships()
    
    def _generate_sql_join_edges(self):
        """SQL 조인 조건으로부터 엣지 생성"""
        logger.info("SQL 조인 엣지 생성 시작")
        
        # SQL Unit에서 JOIN 구문 분석
        sql_units = self.db_session.query(SqlUnit).filter(
            SqlUnit.normalized_fingerprint.like('%JOIN%')
        ).all()
        
        for sql_unit in sql_units:
            join_relationships = self._extract_join_relationships(sql_unit.normalized_fingerprint)
            
            for rel in join_relationships:
                self._create_table_join_edge(
                    rel['left_table'], 
                    rel['right_table'], 
                    rel['join_condition'],
                    sql_unit.sql_id
                )
    
    def _generate_llm_inferred_edges(self):
        """LLM을 사용하여 코드 분석으로 엣지 추론"""
        logger.info("LLM 기반 엣지 추론 시작")
        
        # 복잡한 관계는 LLM에게 분석 요청
        complex_files = self._identify_complex_files()
        
        for file_info in complex_files:
            try:
                file_content = self._get_file_content(file_info['path'])
                
                # LLM에게 관계 분석 요청
                prompt = self._build_relationship_analysis_prompt(file_content, file_info)
                llm_result = self.llm_enricher.analyze_relationships(prompt)
                
                if llm_result and 'relationships' in llm_result:
                    self._process_llm_relationships(llm_result['relationships'], file_info)
                    
            except Exception as e:
                logger.warning(f"LLM 분석 실패 {file_info['path']}: {e}")
    
    def _validate_and_refine_edges(self):
        """엣지 검증 및 정제"""
        logger.info("엣지 검증 시작")
        
        # 1. 중복 엣지 제거
        self._remove_duplicate_edges()
        
        # 2. 신뢰도 기반 필터링
        self._filter_low_confidence_edges()
        
        # 3. 순환 참조 검증
        self._validate_circular_dependencies()
    
    # 헬퍼 메서드들
    
    def _get_class_from_db(self, fqn: str) -> Optional[Class]:
        """FQN으로 클래스를 DB에서 조회"""
        return self.db_session.query(Class).filter(Class.fqn == fqn).first()
    
    def _get_file_from_db(self, file_path: str) -> Optional[File]:
        """파일 경로로 파일을 DB에서 조회"""
        # 상대경로를 절대경로로 변환
        full_path = str(self.project_path / file_path)
        return self.db_session.query(File).filter(File.path == full_path).first()
    
    def _get_method_from_db(self, method_signature: str) -> Optional[Method]:
        """메서드 시그니처로 메서드를 DB에서 조회"""
        return self.db_session.query(Method).filter(
            Method.signature.like(f'%{method_signature}%')
        ).first()
    
    def _is_project_class(self, class_name: str) -> bool:
        """프로젝트 내부 클래스인지 판단"""
        return class_name.startswith('com.example') and class_name in self.class_cache
    
    def _has_autowired_annotation(self, field: Dict) -> bool:
        """필드에 @Autowired 어노테이션이 있는지 확인"""
        annotations = field.get('annotations', [])
        return any('Autowired' in ann for ann in annotations)
    
    def _has_controller_annotation(self, class_info: Dict) -> bool:
        """클래스에 @Controller 어노테이션이 있는지 확인"""
        annotations = class_info.get('annotations', [])
        return any('Controller' in ann for ann in annotations)
    
    def _has_service_annotation(self, class_info: Dict) -> bool:
        """클래스에 @Service 어노테이션이 있는지 확인"""
        annotations = class_info.get('annotations', [])
        return any('Service' in ann for ann in annotations)
    
    def _find_related_service_classes(self, controller_fqn: str) -> List[str]:
        """Controller와 관련된 Service 클래스들 찾기"""
        # 이름 패턴 기반 매칭 (UserController → UserService)
        base_name = controller_fqn.split('.')[-1].replace('Controller', '')
        
        related_services = []
        for class_fqn in self.class_cache.keys():
            if 'service' in class_fqn.lower() and base_name in class_fqn:
                related_services.append(class_fqn)
        
        return related_services
    
    def _find_related_mapper_classes(self, service_fqn: str) -> List[str]:
        """Service와 관련된 Mapper 클래스들 찾기"""
        base_name = service_fqn.split('.')[-1].replace('Service', '').replace('Impl', '')
        
        related_mappers = []
        for class_fqn in self.class_cache.keys():
            if 'mapper' in class_fqn.lower() and base_name in class_fqn:
                related_mappers.append(class_fqn)
        
        return related_mappers
    
    def _create_edge_safe(self, src_type: str, src_id: int, dst_type: str, 
                         dst_id: int, edge_kind: str, confidence: float = 0.5, meta: str = ""):
        """안전한 엣지 생성 (중복 체크 및 위치 정보 포함)"""
        try:
            # 중복 체크
            existing_edge = self.db_session.query(Edge).filter(
                Edge.project_id == self.project_id,
                Edge.src_type == src_type,
                Edge.src_id == src_id,
                Edge.dst_type == dst_type,
                Edge.dst_id == dst_id,
                Edge.edge_kind == edge_kind
            ).first()
            
            if existing_edge:
                return  # 이미 존재하는 엣지
            
            # 소스 청크의 위치 정보 수집
            src_location_meta = self.location_tracker.create_location_metadata(src_type, src_id)
            
            # 대상 청크의 위치 정보 수집 (존재하는 경우)
            dst_location_meta = None
            if dst_id:
                dst_location_meta = self.location_tracker.create_location_metadata(dst_type, dst_id)
            
            # 메타데이터 구성
            enhanced_meta = {
                'description': meta,
                'source_location': src_location_meta,
                'target_location': dst_location_meta,
                'created_by': 'enhanced_edge_generator',
                'analysis_method': 'parser_based'
            }
            
            # JSON 문자열로 변환 (길이 제한)
            import json
            meta_json = json.dumps(enhanced_meta, ensure_ascii=False)
            if len(meta_json) > 1000:  # 메타데이터 길이 제한
                # 위치 정보만 남기고 축약
                enhanced_meta = {
                    'description': meta[:200],
                    'source_location': {
                        'file_path': src_location_meta.get('file_path', ''),
                        'start_line': src_location_meta.get('start_line', 0),
                        'end_line': src_location_meta.get('end_line', 0)
                    } if src_location_meta else None,
                    'created_by': 'enhanced_edge_generator'
                }
                meta_json = json.dumps(enhanced_meta, ensure_ascii=False)
            
            edge = Edge(
                project_id=self.project_id,
                src_type=src_type,
                src_id=src_id,
                dst_type=dst_type,
                dst_id=dst_id,
                edge_kind=edge_kind,
                confidence=confidence,
                meta=meta_json
            )
            
            self.db_session.add(edge)
            self.edge_count += 1
            
            if self.edge_count % 20 == 0:
                logger.debug(f"엣지 생성 진행: {self.edge_count}개")
                
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
    
    # 추가 구현 메서드들 (필요시)
    def _create_class_reference_edge(self, src_fqn: str, dst_fqn: str, relation_type: str):
        """클래스 간 참조 엣지 생성"""
        src_class = self._get_class_from_db(src_fqn)
        dst_class = self._get_class_from_db(dst_fqn)
        
        if src_class and dst_class:
            self._create_edge_safe(
                src_type='class',
                src_id=src_class.class_id,
                dst_type='class', 
                dst_id=dst_class.class_id,
                edge_kind='reference',
                confidence=0.6,
                meta=f"{relation_type}: {src_fqn} → {dst_fqn}"
            )
    
    def _create_spring_dependency_edge(self, src_fqn: str, dst_fqn: str, dependency_type: str):
        """Spring 의존성 엣지 생성"""
        src_class = self._get_class_from_db(src_fqn)
        dst_class = self._get_class_from_db(dst_fqn)
        
        if src_class and dst_class:
            self._create_edge_safe(
                src_type='class',
                src_id=src_class.class_id,
                dst_type='class',
                dst_id=dst_class.class_id,
                edge_kind='dependency',
                confidence=0.8,
                meta=f"Spring {dependency_type}: {src_fqn} → {dst_fqn}"
            )
    
    def _create_sql_table_edges(self, sql_unit: Dict, file_path: str):
        """SQL Unit과 테이블 간 엣지 생성"""
        # SQL에서 참조하는 테이블들 추출
        sql_content = sql_unit.get('content', '')
        referenced_tables = self._extract_table_references(sql_content)
        
        for table_name in referenced_tables:
            table_db = self.db_session.query(DbTable).filter(
                DbTable.table_name.ilike(table_name)
            ).first()
            
            sql_unit_db = self.db_session.query(SqlUnit).filter(
                SqlUnit.stmt_id == sql_unit.get('id')
            ).first()
            
            if table_db and sql_unit_db:
                self._create_edge_safe(
                    src_type='sql_unit',
                    src_id=sql_unit_db.sql_id,
                    dst_type='table',
                    dst_id=table_db.table_id,
                    edge_kind='references',
                    confidence=0.9,
                    meta=f"SQL references table: {sql_unit.get('id')} → {table_name}"
                )
    
    def _extract_table_references(self, sql_content: str) -> List[str]:
        """SQL에서 테이블 참조를 추출"""
        tables = []
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'DELETE\s+FROM\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql_content, re.IGNORECASE)
            tables.extend(matches)
        
        return list(set(tables))
    
    def _extract_join_relationships(self, sql_content: str) -> List[Dict]:
        """SQL JOIN 구문에서 관계 추출"""
        relationships = []
        
        # JOIN ... ON 패턴 매칭
        join_pattern = r'(\w+)\s+.*?JOIN\s+(\w+)\s+.*?ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)'
        matches = re.findall(join_pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            left_table = match[0]
            right_table = match[1]
            left_column = match[2]
            right_column = match[3]
            
            relationships.append({
                'left_table': left_table,
                'right_table': right_table,
                'join_condition': f"{left_column} = {right_column}"
            })
        
        return relationships
    
    def _create_table_join_edge(self, left_table: str, right_table: str, condition: str, sql_id: int):
        """테이블 JOIN 엣지 생성"""
        left_table_db = self.db_session.query(DbTable).filter(
            DbTable.table_name.ilike(left_table)
        ).first()
        
        right_table_db = self.db_session.query(DbTable).filter(
            DbTable.table_name.ilike(right_table)
        ).first()
        
        if left_table_db and right_table_db:
            self._create_edge_safe(
                src_type='table',
                src_id=left_table_db.table_id,
                dst_type='table',
                dst_id=right_table_db.table_id,
                edge_kind='join',
                confidence=0.95,
                meta=f"SQL JOIN: {left_table} → {right_table} ON {condition} (SQL ID: {sql_id})"
            )
    
    # 나머지 헬퍼 메서드들
    def _create_schema_based_relationships(self):
        """스키마 정보 기반 관계 생성"""
        pass  # 구현 필요
    
    def _create_join_based_relationships(self):
        """JOIN 기반 관계 생성"""
        pass  # 구현 필요
    
    def _identify_complex_files(self) -> List[Dict]:
        """복잡한 분석이 필요한 파일들 식별"""
        return []  # 구현 필요
    
    def _get_file_content(self, file_path: str) -> str:
        """파일 내용 읽기"""
        try:
            full_path = self.project_path / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def _build_relationship_analysis_prompt(self, content: str, file_info: Dict) -> str:
        """관계 분석용 LLM 프롬프트 생성"""
        return f"""
        다음 소스 코드를 분석하여 다른 컴포넌트와의 관계를 찾아주세요:
        
        파일: {file_info['path']}
        
        코드:
        {content[:2000]}  # 제한된 길이
        
        찾을 관계 유형:
        1. 클래스 간 의존성
        2. 메서드 호출 관계
        3. 데이터 플로우
        4. 설정 기반 관계
        """
    
    def _process_llm_relationships(self, relationships: List[Dict], file_info: Dict):
        """LLM이 찾은 관계를 처리하여 엣지 생성"""
        pass  # 구현 필요
    
    def _remove_duplicate_edges(self):
        """중복 엣지 제거"""
        pass  # 구현 필요
    
    def _filter_low_confidence_edges(self):
        """낮은 신뢰도 엣지 필터링"""
        pass  # 구현 필요
    
    def _validate_circular_dependencies(self):
        """순환 참조 검증"""
        pass  # 구현 필요
    
    def _find_controller_method_by_url(self, url: str) -> Optional[str]:
        """URL로 Controller 메서드 찾기"""
        # URL 패턴 분석하여 Controller 메서드 추론
        url_parts = url.strip('/').split('/')
        
        if len(url_parts) >= 2:
            controller_name = url_parts[0]
            method_name = url_parts[1] if len(url_parts) > 1 else 'index'
            
            # Controller 클래스 찾기
            for class_fqn in self.class_cache.keys():
                if 'controller' in class_fqn.lower() and controller_name.lower() in class_fqn.lower():
                    return f"{class_fqn}.{method_name}"
        
        return None