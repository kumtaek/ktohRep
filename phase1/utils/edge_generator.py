#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
엣지 생성기 모듈
소스 코드 분석 결과를 바탕으로 컴포넌트 간 관계(엣지)를 생성합니다.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from phase1.models.database import Edge, Class, Method, File, SqlUnit, DbTable, DbColumn, DbPk

logger = logging.getLogger(__name__)


class EdgeGenerator:
    """엣지 생성기 클래스"""
    
    def __init__(self, db_session: Session, config: dict = None):
        self.db_session = db_session
        self.edge_count = 0
        self.config = config or {}
        
    def generate_all_edges(self) -> int:
        """모든 엣지를 생성합니다."""
        logger.info("엣지 생성 시작")
        
        try:
            # 기존 엣지 삭제
            self._clear_existing_edges()
            
            # 각 유형별 엣지 생성
            self._generate_java_dependency_edges()
            self._generate_method_call_edges()           # 메서드 호출 관계 추가
            self._generate_data_flow_edges()             # 데이터 흐름 관계 추가
            self._generate_service_layer_edges()         # 계층 간 관계 추가  
            self._generate_xml_mapper_edges()
            self._generate_jsp_controller_edges()
            self._generate_db_table_edges()
            self._generate_sql_unit_edges()
            
            # AutoCommitSession은 자동으로 커밋되므로 별도 커밋 불필요
            logger.info(f"엣지 생성 완료: {self.edge_count}개")
            return self.edge_count
            
        except Exception as e:
            logger.error(f"엣지 생성 중 오류 발생: {e}")
            # AutoCommitSession은 롤백 메서드가 없으므로 예외만 로깅
            raise
    
    def _clear_existing_edges(self):
        """기존 엣지를 삭제합니다."""
        self.db_session.query(Edge).delete()
        logger.info("기존 엣지 삭제 완료")
    
    def _generate_java_dependency_edges(self):
        """Java 클래스 간 의존성 엣지를 동적으로 생성합니다."""
        logger.info("Java 의존성 엣지 동적 생성 시작")
        
        # 모든 클래스를 가져와서 동적 분석
        all_classes = self.db_session.query(Class).all()
        
        for source_class in all_classes:
            # 각 클래스의 소스 코드를 분석하여 의존성 찾기
            dependencies = self._analyze_class_dependencies(source_class)
            
            for dep in dependencies:
                target_class = self._find_class_by_name_or_fqn(dep['target_name'])
                if target_class:
                    self._create_edge(
                        source_type='class',
                        source_id=source_class.class_id,
                        target_type='class', 
                        target_id=target_class.class_id,
                        edge_type=dep['relation_type'],
                        description=f"{source_class.name} {dep['relation_type']} {target_class.name}"
                    )
    
    def _generate_xml_mapper_edges(self):
        """XML 매퍼 관계 엣지를 동적으로 생성합니다."""
        logger.info("XML 매퍼 엣지 동적 생성 시작")
        
        # XML 파일들을 동적 분석
        xml_files = self.db_session.query(File).filter(
            File.language == 'xml'
        ).all()
        
        for xml_file in xml_files:
            # 동적으로 XML 매퍼 관계 분석
            mapper_relations = self._analyze_xml_mapper_relations(xml_file)
            
            for relation in mapper_relations:
                if relation['target_type'] == 'class':
                    target_class = self._find_class_by_name_or_fqn(relation['target_name'])
                    if target_class:
                        self._create_edge(
                            source_type='file',
                            source_id=xml_file.file_id,
                            target_type='class',
                            target_id=target_class.class_id,
                            edge_type=relation['relation_type'],
                            description=f"{xml_file.path.split('/')[-1]} {relation['relation_type']} {target_class.name}"
                        )
                
                elif relation['target_type'] == 'table':
                    table = self._find_or_create_table(relation['target_name'])
                    if table:
                        self._create_edge(
                            source_type=relation['source_type'],
                            source_id=relation['source_id'],
                            target_type='table',
                            target_id=table.table_id,
                            edge_type='references',
                            description=f"{relation['source_name']} → {table.table_name}"
                        )
    
    def _generate_jsp_controller_edges(self):
        """JSP → Controller 관계 엣지를 생성합니다."""
        logger.info("JSP Controller 엣지 생성 시작")
        
        jsp_files = self.db_session.query(File).filter(
            File.language == 'jsp'
        ).all()
        
        for jsp_file in jsp_files:
            # JSP 파일의 Controller 관계를 동적 분석
            controller_relations = self._analyze_jsp_controller_relations(jsp_file)
            
            for relation in controller_relations:
                target_class = self._find_class_by_name_or_fqn(relation['target_name'])
                if target_class:
                    self._create_edge(
                        source_type='file',
                        source_id=jsp_file.file_id,
                        target_type='class',
                        target_id=target_class.class_id,
                        edge_type=relation['relation_type'],
                        description=f"{jsp_file.path.split('/')[-1]} {relation['relation_type']} {target_class.name}"
                    )
    
    def _generate_db_table_edges(self):
        """DB 테이블 간 관계 엣지를 동적으로 분석하여 생성합니다."""
        logger.info("DB 테이블 엣지 동적 생성 시작")
        
        # 실제 DB 스키마 데이터를 분석하여 관계 도출
        relationships = self._analyze_db_relationships()
        
        for rel in relationships:
            try:
                # 소스 테이블 확인
                source_table = self.db_session.query(DbTable).filter(
                    DbTable.table_name == rel['source_table']
                ).first()
                
                if not source_table:
                    # 더미 테이블 생성
                    source_table = self._create_dummy_table(rel['source_table'])
                
                # 타겟 테이블 확인
                target_table = self.db_session.query(DbTable).filter(
                    DbTable.table_name == rel['target_table']
                ).first()
                
                if not target_table:
                    # 더미 테이블 생성
                    target_table = self._create_dummy_table(rel['target_table'])
                
                if source_table and target_table:
                    self._create_edge(
                        source_type='table',
                        source_id=source_table.table_id,
                        target_type='table', 
                        target_id=target_table.table_id,
                        edge_type=rel['relation_type'],
                        description=rel['description']
                    )
                    
            except Exception as e:
                logger.warning(f"DB 테이블 관계 엣지 생성 실패 {rel}: {e}")
                
        logger.info(f"DB 테이블 엣지 {len(relationships)}개 생성 완료")
    
    def _generate_sql_unit_edges(self):
        """SQL Unit 간 관계 엣지를 생성합니다."""
        logger.info("SQL Unit 엣지 생성 시작")
        
        # 같은 파일 내 SQL Units 간 관계
        sql_units = self.db_session.query(SqlUnit).all()
        
        for sql_unit in sql_units:
            # INSERT → SELECT 관계 (같은 테이블)
            if sql_unit.stmt_kind == 'insert':
                table_name = self._extract_table_from_sql(sql_unit.normalized_fingerprint)
                if table_name:
                    select_units = self.db_session.query(SqlUnit).filter(
                        SqlUnit.stmt_kind == 'select',
                        SqlUnit.file_id == sql_unit.file_id,
                        SqlUnit.normalized_fingerprint.like(f'%{table_name}%')
                    ).all()
                    
                    for select_unit in select_units:
                        self._create_edge(
                            source_type='sql_unit',
                            source_id=sql_unit.sql_id,
                            target_type='sql_unit',
                            target_id=select_unit.sql_id,
                            edge_type='data_flow',
                            description=f'{sql_unit.stmt_id} → {select_unit.stmt_id}'
                        )
    
    def _find_service_dependencies(self, controller: Class) -> List[int]:
        """Controller에서 Service 의존성을 찾습니다."""
        service_deps = []
        
        try:
            # 파일을 읽어서 @Autowired 필드 분석
            if hasattr(controller, 'file_id'):
                file_obj = self.db_session.query(File).filter_by(file_id=controller.file_id).first()
                if file_obj and file_obj.path:
                    with open(file_obj.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # @Autowired 또는 @Resource가 있는 Service 필드 찾기
                    import re
                    patterns = [
                        r'@(?:Autowired|Resource)\s+(?:private\s+)?(\w+Service)\s+(\w+);',
                        r'private\s+(\w+Service)\s+(\w+);\s*//.*@Autowired'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        for service_type, field_name in matches:
                            # Service 클래스 찾기
                            service = self.db_session.query(Class).filter(
                                Class.name == service_type
                            ).first()
                            if service:
                                service_deps.append(service.class_id)
                                logger.debug(f"발견된 의존성: {controller.name} → {service_type}")
        except Exception as e:
            logger.warning(f"Service 의존성 분석 실패 {controller.name}: {e}")
            
        return service_deps
    
    def _find_mapper_dependencies(self, service: Class) -> List[int]:
        """Service에서 Mapper 의존성을 찾습니다."""
        mapper_deps = []
        
        try:
            # 파일을 읽어서 @Autowired Mapper 필드 분석
            if hasattr(service, 'file_id'):
                file_obj = self.db_session.query(File).filter_by(file_id=service.file_id).first()
                if file_obj and file_obj.path:
                    with open(file_obj.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # @Autowired 또는 @Resource가 있는 Mapper 필드 찾기
                    import re
                    patterns = [
                        r'@(?:Autowired|Resource)\s+(?:private\s+)?(\w+Mapper)\s+(\w+);',
                        r'private\s+(\w+Mapper)\s+(\w+);\s*//.*@Autowired'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        for mapper_type, field_name in matches:
                            # Mapper 클래스 찾기
                            mapper = self.db_session.query(Class).filter(
                                Class.name == mapper_type
                            ).first()
                            if mapper:
                                mapper_deps.append(mapper.class_id)
                                logger.debug(f"발견된 의존성: {service.name} → {mapper_type}")
        except Exception as e:
            logger.warning(f"Mapper 의존성 분석 실패 {service.name}: {e}")
            
        return mapper_deps
    
    def _find_model_dependencies(self, cls: Class) -> List[int]:
        """클래스에서 Model 의존성을 찾습니다."""
        model_deps = []
        
        try:
            # 파일을 읽어서 import 및 사용 분석
            if hasattr(cls, 'file_id'):
                file_obj = self.db_session.query(File).filter_by(file_id=cls.file_id).first()
                if file_obj and file_obj.path:
                    with open(file_obj.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # import문에서 model 클래스 찾기
                    import re
                    import_pattern = r'import\s+[^;]*\.model\.(\w+);'
                    import_matches = re.findall(import_pattern, content)
                    
                    for model_name in import_matches:
                        # Model 클래스 찾기
                        model = self.db_session.query(Class).filter(
                            Class.name == model_name,
                            Class.fqn.like('%.model.%')
                        ).first()
                        if model:
                            model_deps.append(model.class_id)
                            logger.debug(f"발견된 Model 의존성: {cls.name} → {model_name}")
        except Exception as e:
            logger.warning(f"Model 의존성 분석 실패 {cls.name}: {e}")
            
        return model_deps
    
    def _extract_namespace_from_xml(self, file_path: str) -> Optional[str]:
        """XML 파일에서 네임스페이스를 추출합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # MyBatis XML에서 namespace 추출
            import re
            patterns = [
                r'<mapper\s+namespace="([^"]+)"',  # <mapper namespace="...">
                r'namespace\s*=\s*"([^"]+)"'       # namespace="..."
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    namespace = match.group(1)
                    logger.debug(f"XML 네임스페이스 발견: {file_path} → {namespace}")
                    return namespace
                    
        except Exception as e:
            logger.warning(f"XML 파일 읽기 실패 {file_path}: {e}")
        return None
    
    def _extract_table_references(self, sql_content: str) -> List[str]:
        """SQL에서 테이블 참조를 추출합니다."""
        import re
        # 간단한 테이블명 추출 (FROM, JOIN 절)
        tables = []
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql_content, re.IGNORECASE)
            tables.extend(matches)
        
        return list(set(tables))  # 중복 제거
    
    def _extract_controller_references(self, jsp_path: str) -> List[str]:
        """JSP 파일에서 Controller 참조를 추출합니다."""
        try:
            with open(jsp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Controller 참조 패턴들
            import re
            patterns = [
                # form action 패턴
                r'action\s*=\s*["\']([^"\']*?)(?:\.do|\.action|/(\w+))["\']',
                # Spring MVC URL 패턴
                r'<c:url\s+value\s*=\s*["\']([^"\']*?)/(\w+)["\']',
                # JavaScript 또는 AJAX 호출
                r'url\s*:\s*["\']([^"\']*?)/(\w+)["\']',
                # a href 링크
                r'href\s*=\s*["\']([^"\']*?)/(\w+)(?:\.do|\.action)?["\']'
            ]
            
            controllers = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # 두 번째 그룹이 컨트롤러명
                        for group in match:
                            if group and group.isalpha():
                                controllers.append(group)
                    else:
                        controllers.append(match)
            
            # JSP 파일명에서 관련 컨트롤러 추론
            from pathlib import Path
            jsp_name = Path(jsp_path).stem.lower()  # user.jsp → user
            if jsp_name:
                potential_controller = jsp_name.capitalize() + 'Controller'  # UserController
                controllers.append(potential_controller)
                
            logger.debug(f"JSP Controller 참조 발견: {jsp_path} → {controllers}")
            return list(set(controllers))
            
        except Exception as e:
            logger.warning(f"JSP 파일 읽기 실패 {jsp_path}: {e}")
        return []
    
    def _is_foreign_key_column(self, column_name: str) -> bool:
        """컬럼명이 FK인지 판단합니다."""
        fk_patterns = ['_id', 'id_', 'fk_', '_fk']
        return any(pattern in column_name.lower() for pattern in fk_patterns)
    
    def _infer_referenced_table(self, column_name: str) -> Optional[str]:
        """컬럼명에서 참조 테이블을 추론합니다."""
        # user_id → users, product_id → products 등
        if column_name.endswith('_id'):
            table_name = column_name[:-3]  # _id 제거
            # 복수형 변환 (간단한 규칙)
            if not table_name.endswith('s'):
                table_name += 's'
            return table_name
        return None
    
    def _extract_table_from_sql(self, sql_content: str) -> Optional[str]:
        """SQL에서 테이블명을 추출합니다."""
        import re
        # INSERT INTO table_name 패턴
        match = re.search(r'INSERT\s+INTO\s+(\w+)', sql_content, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _create_edge(self, source_type: str, source_id: int, target_type: str, 
                    target_id: int, edge_type: str, description: str, project_id: int = 1):
        """엣지를 생성합니다."""
        try:
            edge = Edge(
                project_id=project_id,
                src_type=source_type,
                src_id=source_id,
                dst_type=target_type,
                dst_id=target_id,
                edge_kind=edge_type,
                meta=description
            )
            self.db_session.add(edge)
            self.edge_count += 1
            
            if self.edge_count % 10 == 0:
                logger.debug(f"엣지 생성 진행: {self.edge_count}개")
                
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
    
    def _create_dummy_table(self, table_name: str):
        """더미 테이블을 생성합니다."""
        try:
            # 이미 존재하는지 확인
            existing = self.db_session.query(DbTable).filter(
                DbTable.table_name == table_name.upper()
            ).first()
            if existing:
                return existing
                
            # 설정에서 default owner 가져오기
            default_owner = self.config.get('database', {}).get('default_table_owner', 'SAMPLE')
            
            dummy_table = DbTable(
                owner=default_owner,
                table_name=table_name.upper(),
                status='INFERRED',
                table_comment=f'더미 테이블 (SQL 분석에서 추론됨)'
            )
            
            self.db_session.add(dummy_table)
            self.db_session.flush()
            logger.debug(f"더미 테이블 생성: {default_owner}.{table_name}")
            return dummy_table
            
        except Exception as e:
            logger.warning(f"더미 테이블 생성 실패 {table_name}: {e}")
            return None
    
    def _analyze_class_dependencies(self, source_class: Class) -> List[dict]:
        """클래스의 소스 코드를 동적으로 분석하여 의존성을 찾습니다."""
        dependencies = []
        
        try:
            # 파일 경로에서 소스 코드 읽기
            file_obj = self.db_session.query(File).filter_by(file_id=source_class.file_id).first()
            if not file_obj or not file_obj.path:
                return dependencies
                
            with open(file_obj.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Import 문 분석
            import_deps = self._analyze_imports(content)
            dependencies.extend(import_deps)
            
            # 2. 필드 의존성 분석 (@Autowired, @Inject 등)
            field_deps = self._analyze_field_dependencies(content)
            dependencies.extend(field_deps)
            
            # 3. 상속/구현 관계 분석
            inheritance_deps = self._analyze_inheritance(content)
            dependencies.extend(inheritance_deps)
            
            # 4. 메서드 호출 분석 (생성자 주입 등)
            method_deps = self._analyze_method_dependencies(content)
            dependencies.extend(method_deps)
            
            logger.debug(f"클래스 {source_class.name} 의존성 {len(dependencies)}개 발견")
            
        except Exception as e:
            logger.warning(f"클래스 의존성 분석 실패 {source_class.name}: {e}")
            
        return dependencies
    
    def _analyze_imports(self, content: str) -> List[dict]:
        """Import 문을 분석하여 의존성을 찾습니다."""
        dependencies = []
        import re
        
        # Java import 패턴
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        matches = re.findall(import_pattern, content)
        
        for import_stmt in matches:
            # 패키지명.클래스명에서 클래스명 추출
            if '.' in import_stmt:
                class_name = import_stmt.split('.')[-1]
                # 내부 클래스나 메서드 제외
                if not class_name.isupper() and class_name[0].isupper():
                    dependencies.append({
                        'target_name': class_name,
                        'relation_type': 'import',
                        'source': 'import_statement'
                    })
        
        return dependencies
    
    def _analyze_field_dependencies(self, content: str) -> List[dict]:
        """필드 의존성을 분석합니다 (@Autowired, @Inject 등)."""
        dependencies = []
        import re
        
        # 의존성 주입 어노테이션 패턴
        injection_patterns = [
            r'@(?:Autowired|Inject|Resource)\s+(?:private\s+)?(\w+)\s+\w+\s*;',
            r'@(?:Autowired|Inject|Resource)\s*\n\s*(?:private\s+)?(\w+)\s+\w+\s*;'
        ]
        
        for pattern in injection_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                dependencies.append({
                    'target_name': match,
                    'relation_type': 'dependency',
                    'source': 'field_injection'
                })
        
        return dependencies
    
    def _analyze_inheritance(self, content: str) -> List[dict]:
        """상속 및 구현 관계를 분석합니다."""
        dependencies = []
        import re
        
        # 상속 패턴 (extends)
        extends_pattern = r'class\s+\w+\s+extends\s+(\w+)'
        extends_matches = re.findall(extends_pattern, content)
        for match in extends_matches:
            dependencies.append({
                'target_name': match,
                'relation_type': 'extends',
                'source': 'class_declaration'
            })
        
        # 구현 패턴 (implements)
        implements_pattern = r'(?:class|interface)\s+\w+\s+implements\s+([^{]+)'
        implements_matches = re.findall(implements_pattern, content)
        for match in implements_matches:
            # 여러 인터페이스 구현 시 콤마로 분리
            interfaces = [i.strip() for i in match.split(',')]
            for interface in interfaces:
                if interface and interface[0].isupper():
                    dependencies.append({
                        'target_name': interface,
                        'relation_type': 'implements',
                        'source': 'class_declaration'
                    })
        
        return dependencies
    
    def _analyze_method_dependencies(self, content: str) -> List[dict]:
        """메서드 내 의존성을 분석합니다."""
        dependencies = []
        import re
        
        # 생성자 호출 패턴
        constructor_pattern = r'new\s+(\w+)\s*\('
        matches = re.findall(constructor_pattern, content)
        
        for match in matches:
            if match[0].isupper():  # 클래스명은 대문자로 시작
                dependencies.append({
                    'target_name': match,
                    'relation_type': 'uses',
                    'source': 'constructor_call'
                })
        
        return dependencies
    
    def _find_class_by_name_or_fqn(self, class_name: str) -> Class:
        """클래스명 또는 FQN으로 클래스를 찾습니다."""
        # 먼저 정확한 클래스명으로 찾기
        target_class = self.db_session.query(Class).filter(
            Class.name == class_name
        ).first()
        
        if not target_class:
            # FQN 끝부분이 일치하는 것 찾기
            target_class = self.db_session.query(Class).filter(
                Class.fqn.like(f'%.{class_name}')
            ).first()
        
        return target_class
    
    def _analyze_xml_mapper_relations(self, xml_file: File) -> List[dict]:
        """XML 매퍼 파일의 관계를 동적으로 분석합니다."""
        relations = []
        
        try:
            with open(xml_file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 네임스페이스 분석 (Java 인터페이스와의 매핑)
            namespace_match = re.search(r'<mapper\s+namespace="([^"]+)"', content)
            if namespace_match:
                namespace = namespace_match.group(1)
                class_name = namespace.split('.')[-1]  # 마지막 부분이 클래스명
                relations.append({
                    'target_name': class_name,
                    'target_type': 'class',
                    'relation_type': 'implements',
                    'source': 'namespace'
                })
            
            # 2. SQL Units와 테이블 관계 분석
            sql_units = self.db_session.query(SqlUnit).filter(
                SqlUnit.file_id == xml_file.file_id
            ).all()
            
            for sql_unit in sql_units:
                # SQL 내용에서 테이블 참조 동적 추출
                table_refs = self._extract_table_references_dynamic(sql_unit.normalized_fingerprint)
                for table_name in table_refs:
                    relations.append({
                        'target_name': table_name,
                        'target_type': 'table',
                        'relation_type': 'references',
                        'source_type': 'sql_unit',
                        'source_id': sql_unit.sql_id,
                        'source_name': sql_unit.stmt_id
                    })
            
            # 3. resultType 분석 (Java 클래스와의 매핑)
            resulttype_pattern = r'resultType="([^"]+)"'
            resulttype_matches = re.findall(resulttype_pattern, content)
            for resulttype in resulttype_matches:
                if '.' in resulttype:  # 패키지명.클래스명
                    class_name = resulttype.split('.')[-1]
                    relations.append({
                        'target_name': class_name,
                        'target_type': 'class',
                        'relation_type': 'maps_to',
                        'source': 'resultType'
                    })
                    
            logger.debug(f"XML {xml_file.path} 관계 {len(relations)}개 발견")
            
        except Exception as e:
            logger.warning(f"XML 매퍼 관계 분석 실패 {xml_file.path}: {e}")
            
        return relations
    
    def _extract_table_references_dynamic(self, sql_content: str) -> List[str]:
        """SQL에서 테이블 참조를 동적으로 추출합니다."""
        if not sql_content:
            return []
            
        tables = []
        import re
        
        # 다양한 SQL 패턴에서 테이블명 추출
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'DELETE\s+FROM\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql_content, re.IGNORECASE)
            for match in matches:
                # 테이블명 검증 (대소문자, 숫자, 언더스코어만 허용)
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', match):
                    tables.append(match.upper())
        
        return list(set(tables))  # 중복 제거
    
    def _find_or_create_table(self, table_name: str):
        """테이블을 찾거나 더미 테이블을 생성합니다."""
        # 먼저 기존 테이블 찾기
        table = self.db_session.query(DbTable).filter(
            DbTable.table_name == table_name.upper()
        ).first()
        
        if not table:
            # 더미 테이블 생성
            table = self._create_dummy_table(table_name)
            
        return table
    
    def _analyze_jsp_controller_relations(self, jsp_file: File) -> List[dict]:
        """JSP 파일의 Controller 관계를 동적으로 분석합니다."""
        relations = []
        
        try:
            with open(jsp_file.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # 1. form action 패턴
            action_patterns = [
                r'action\s*=\s*["\']([^"\']*?)(?:\.do|\.action)?["\']',
                r'<c:url\s+value\s*=\s*["\']([^"\']*?)["\']'
            ]
            
            for pattern in action_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # URL에서 Controller 추정
                    controller_name = self._infer_controller_from_url(match)
                    if controller_name:
                        relations.append({
                            'target_name': controller_name,
                            'relation_type': 'calls',
                            'source': 'form_action'
                        })
            
            # 2. JavaScript AJAX 호출
            ajax_pattern = r'url\s*:\s*["\']([^"\']*?)["\']'
            ajax_matches = re.findall(ajax_pattern, content, re.IGNORECASE)
            for match in ajax_matches:
                controller_name = self._infer_controller_from_url(match)
                if controller_name:
                    relations.append({
                        'target_name': controller_name,
                        'relation_type': 'ajax_call',
                        'source': 'javascript'
                    })
            
            # 3. JSP 파일명에서 Controller 추정
            from pathlib import Path
            jsp_name = Path(jsp_file.path).stem.lower()
            if jsp_name:
                # user.jsp → UserController
                potential_controller = jsp_name.capitalize() + 'Controller'
                relations.append({
                    'target_name': potential_controller,
                    'relation_type': 'renders',
                    'source': 'jsp_naming_convention'
                })
                
            logger.debug(f"JSP {jsp_file.path} Controller 관계 {len(relations)}개 발견")
            
        except Exception as e:
            logger.warning(f"JSP Controller 관계 분석 실패 {jsp_file.path}: {e}")
            
        return relations
    
    def _infer_controller_from_url(self, url: str) -> str:
        """URL에서 Controller명을 추정합니다."""
        if not url or url.startswith('#'):
            return None
            
        # URL 파싱: /user/list → UserController
        url_parts = [part for part in url.split('/') if part and not part.startswith('?')]
        
        if url_parts:
            # 첫 번째 경로 부분을 Controller로 추정
            controller_path = url_parts[0]
            return controller_path.capitalize() + 'Controller'
        
        return None
    
    def _analyze_db_relationships(self) -> List[dict]:
        """DB 스키마 데이터를 동적으로 분석하여 테이블 간 관계를 도출합니다."""
        relationships = []
        
        try:
            # 1. PK 정보에서 관계 분석
            pk_relationships = self._analyze_pk_relationships()
            relationships.extend(pk_relationships)
            
            # 2. 컬럼 명명 규칙에서 관계 분석
            naming_relationships = self._analyze_column_naming_relationships()
            relationships.extend(naming_relationships)
            
            # 3. 실제 데이터베이스 제약조건 분석 (있는 경우)
            constraint_relationships = self._analyze_constraint_relationships()
            relationships.extend(constraint_relationships)
            
            logger.debug(f"DB 관계 {len(relationships)}개 분석 완료")
            
        except Exception as e:
            logger.warning(f"DB 관계 분석 실패: {e}")
            
        return relationships
    
    def _analyze_pk_relationships(self) -> List[dict]:
        """PK 정보를 분석하여 테이블 간 관계를 도출합니다."""
        relationships = []
        
        try:
            # PK 정보 조회
            pks = self.db_session.query(DbPk).all()
            
            for pk in pks:
                # PK가 다른 테이블에서 FK로 사용되는지 확인
                potential_fks = self.db_session.query(DbColumn).filter(
                    DbColumn.column_name == pk.column_name,
                    DbColumn.table_name != pk.table_name
                ).all()
                
                for fk_column in potential_fks:
                    relationships.append({
                        'source_table': fk_column.table_name,
                        'target_table': pk.table_name,
                        'relation_type': 'foreign_key',
                        'description': f'{fk_column.table_name}.{fk_column.column_name} → {pk.table_name}.{pk.column_name}',
                        'source': 'pk_analysis'
                    })
                    
        except Exception as e:
            logger.warning(f"PK 관계 분석 실패: {e}")
            
        return relationships
    
    def _analyze_column_naming_relationships(self) -> List[dict]:
        """컬럼 명명 규칙을 분석하여 테이블 간 관계를 도출합니다."""
        relationships = []
        
        try:
            # 모든 컬럼 조회
            columns = self.db_session.query(DbColumn).all()
            
            for column in columns:
                # ID로 끝나는 컬럼 (FK 후보)
                if column.column_name.upper().endswith('_ID') or column.column_name.upper().endswith('ID'):
                    # 테이블명 추출 (USER_ID → USER)
                    table_candidate = self._extract_table_name_from_fk_column(column.column_name)
                    
                    # DbColumn은 table_id를 가지고 있으므로 table 관계를 통해 table_name에 접근
                    if table_candidate and table_candidate != column.table.table_name:
                        # 해당 테이블이 실제로 존재하는지 확인
                        target_table_exists = self.db_session.query(DbTable).filter(
                            DbTable.table_name == table_candidate
                        ).first()
                        
                        if target_table_exists:
                            relationships.append({
                                'source_table': column.table.table_name,
                                'target_table': table_candidate,
                                'relation_type': 'foreign_key',
                                'description': f'{column.table.table_name}.{column.column_name} → {table_candidate}',
                                'source': 'naming_convention'
                            })
                        else:
                            # 테이블이 없으면 더미 생성을 위해 관계 추가
                            relationships.append({
                                'source_table': column.table.table_name,
                                'target_table': table_candidate,
                                'relation_type': 'foreign_key',
                                'description': f'{column.table.table_name}.{column.column_name} → {table_candidate} (dummy)',
                                'source': 'naming_convention_dummy'
                            })
                            
        except Exception as e:
            logger.warning(f"컬럼 명명 관계 분석 실패: {e}")
            
        return relationships
    
    def _analyze_constraint_relationships(self) -> List[dict]:
        """데이터베이스 제약조건을 분석하여 관계를 도출합니다."""
        relationships = []
        
        # 현재 스키마에 제약조건 정보가 없으므로 빈 리스트 반환
        # 향후 CONSTRAINT 정보가 추가되면 여기서 분석
        
        return relationships
    
    def _extract_table_name_from_fk_column(self, column_name: str) -> str:
        """FK 컬럼명에서 테이블명을 추출합니다."""
        if not column_name:
            return None
            
        column_upper = column_name.upper()
        
        # USER_ID → USER
        if column_upper.endswith('_ID'):
            return column_upper[:-3]
        
        # USERID → USER (가정: ID로 끝나는 경우)
        elif column_upper.endswith('ID') and len(column_upper) > 2:
            return column_upper[:-2]
            
        return None

    def _generate_method_call_edges(self):
        """메서드 간 호출 관계 엣지를 생성합니다."""
        logger.info("메서드 호출 관계 엣지 생성 시작")
        
        # 모든 클래스를 가져와서 메서드 호출 관계 분석
        all_classes = self.db_session.query(Class).all()
        
        for source_class in all_classes:
            try:
                # 클래스 파일을 읽어서 메서드 호출 분석
                file_obj = self.db_session.query(File).filter_by(file_id=source_class.file_id).first()
                if not file_obj or not file_obj.path:
                    continue
                    
                with open(file_obj.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 메서드 호출 패턴 찾기
                method_calls = self._extract_method_calls(content)
                
                for call in method_calls:
                    # 호출되는 메서드가 같은 클래스 내부인지 확인
                    if call['is_internal']:
                        # 같은 클래스 내부 메서드 호출
                        self._create_edge(
                            source_type='class',
                            source_id=source_class.class_id,
                            target_type='class',
                            target_id=source_class.class_id,
                            edge_type='calls',
                            description=f"{source_class.name} 내부 메서드 호출: {call['method_name']}"
                        )
                    else:
                        # 다른 클래스 메서드 호출
                        target_class = self._find_class_by_name_or_fqn(call['target_class'])
                        if target_class:
                            self._create_edge(
                                source_type='class',
                                source_id=source_class.class_id,
                                target_type='class',
                                target_id=target_class.class_id,
                                edge_type='calls',
                                description=f"{source_class.name} → {target_class.name}.{call['method_name']}()"
                            )
                            
            except Exception as e:
                logger.warning(f"메서드 호출 관계 분석 실패 {source_class.name}: {e}")
    
    def _extract_method_calls(self, content: str) -> List[dict]:
        """소스 코드에서 메서드 호출을 추출합니다."""
        method_calls = []
        import re
        
        # 메서드 호출 패턴들
        patterns = [
            # 일반적인 메서드 호출: object.method()
            r'(\w+)\.(\w+)\s*\(',
            # this.method() 호출
            r'this\.(\w+)\s*\(',
            # super.method() 호출  
            r'super\.(\w+)\s*\(',
            # 정적 메서드 호출: ClassName.method()
            r'([A-Z]\w+)\.(\w+)\s*\('
        ]
        
        # 일반 메서드 호출
        for pattern in patterns[:1]:  # object.method()
            matches = re.findall(pattern, content)
            for obj_name, method_name in matches:
                # 필드명에서 클래스 추정 (userService → UserService)
                if obj_name.endswith('Service') or obj_name.endswith('Mapper') or obj_name.endswith('Repository'):
                    target_class = obj_name.capitalize() if obj_name.islower() else obj_name
                    if not target_class.endswith('Service') and not target_class.endswith('Mapper'):
                        target_class += 'Service'  # 기본으로 Service 추가
                    
                    method_calls.append({
                        'method_name': method_name,
                        'target_class': target_class,
                        'is_internal': False,
                        'call_type': 'external'
                    })
        
        # 내부 메서드 호출 (this.method())
        this_pattern = r'this\.(\w+)\s*\('
        this_matches = re.findall(this_pattern, content)
        for method_name in this_matches:
            method_calls.append({
                'method_name': method_name,
                'target_class': None,
                'is_internal': True,
                'call_type': 'internal'
            })
        
        # 정적 메서드 호출 (ClassName.method())
        static_pattern = r'([A-Z]\w+)\.(\w+)\s*\('
        static_matches = re.findall(static_pattern, content)
        for class_name, method_name in static_matches:
            method_calls.append({
                'method_name': method_name,
                'target_class': class_name,
                'is_internal': False,
                'call_type': 'static'
            })
        
        return method_calls
    
    def _generate_data_flow_edges(self):
        """데이터 흐름 관계 엣지를 생성합니다."""
        logger.info("데이터 흐름 관계 엣지 생성 시작")
        
        # 모든 클래스에 대해 데이터 흐름 분석
        all_classes = self.db_session.query(Class).all()
        
        for source_class in all_classes:
            try:
                file_obj = self.db_session.query(File).filter_by(file_id=source_class.file_id).first()
                if not file_obj or not file_obj.path:
                    continue
                    
                with open(file_obj.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 데이터 변환 패턴 찾기
                data_flows = self._extract_data_flows(content)
                
                for flow in data_flows:
                    if flow['target_class']:
                        target_class = self._find_class_by_name_or_fqn(flow['target_class'])
                        if target_class:
                            self._create_edge(
                                source_type='class',
                                source_id=source_class.class_id,
                                target_type='class',
                                target_id=target_class.class_id,
                                edge_type='data_flow',
                                description=f"데이터 흐름: {source_class.name} → {target_class.name} ({flow['flow_type']})"
                            )
                            
            except Exception as e:
                logger.warning(f"데이터 흐름 분석 실패 {source_class.name}: {e}")
    
    def _extract_data_flows(self, content: str) -> List[dict]:
        """소스 코드에서 데이터 흐름을 추출합니다."""
        data_flows = []
        import re
        
        # 데이터 변환 패턴들
        patterns = {
            'dto_conversion': [
                r'(\w+)\.toDto\(',
                r'(\w+)\.fromDto\(',
                r'(\w+)\.convert\('
            ],
            'model_mapping': [
                r'new\s+(\w+)\s*\(',  # 객체 생성
                r'(\w+)\.builder\(\)'  # 빌더 패턴
            ],
            'return_statement': [
                r'return\s+(\w+)\.',  # 반환문
                r'return\s+new\s+(\w+)\('
            ]
        }
        
        for flow_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # 클래스명 추정 (dto, model 등)
                    if isinstance(match, str) and match[0].isupper():
                        data_flows.append({
                            'target_class': match,
                            'flow_type': flow_type,
                            'pattern': pattern
                        })
        
        return data_flows
    
    def _generate_service_layer_edges(self):
        """Spring MVC 계층 간 관계 엣지를 생성합니다."""
        logger.info("서비스 계층 관계 엣지 생성 시작")
        
        # Controller → Service 관계
        controllers = self.db_session.query(Class).filter(
            Class.name.like('%Controller%')
        ).all()
        
        for controller in controllers:
            service_deps = self._find_service_dependencies(controller)
            for service_id in service_deps:
                self._create_edge(
                    source_type='class',
                    source_id=controller.class_id,
                    target_type='class',
                    target_id=service_id,
                    edge_type='uses_service',
                    description=f"{controller.name} uses service"
                )
        
        # Service → Repository/Mapper 관계
        services = self.db_session.query(Class).filter(
            Class.name.like('%Service%')
        ).all()
        
        for service in services:
            mapper_deps = self._find_mapper_dependencies(service)
            for mapper_id in mapper_deps:
                self._create_edge(
                    source_type='class',
                    source_id=service.class_id,
                    target_type='class',
                    target_id=mapper_id,
                    edge_type='uses_repository',
                    description=f"{service.name} uses mapper/repository"
                )
