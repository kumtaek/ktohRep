"""
JPA(Java Persistence API) 파서
JPA 관련 파일에서 엔티티, 관계, 쿼리 등을 추출합니다.
재현율을 높이기 위해 다양한 패턴을 처리합니다.
"""

import re
from typing import Dict, List, Any, Set
from ..base_parser import BaseParser
from utils.table_alias_resolver import get_table_alias_resolver

class JPAParser(BaseParser):
    """JPA 전용 파서 - 재현율 우선"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # JPA 어노테이션 패턴
        self.jpa_annotations = {
            'entity_annotations': [
                '@Entity', '@Table', '@Id', '@GeneratedValue', '@Column', '@Transient',
                '@OneToOne', '@OneToMany', '@ManyToOne', '@ManyToMany', '@JoinColumn',
                '@JoinTable', '@Embedded', '@Embeddable', '@MappedSuperclass',
                '@Inheritance', '@DiscriminatorColumn', '@DiscriminatorValue'
            ],
            'patterns': [
                re.compile(r'@(\w+)(?:\(([^)]*)\))?', re.IGNORECASE),
                re.compile(r'@(\w+)\s*\{([^}]*)\}', re.IGNORECASE | re.DOTALL),
            ]
        }
        
        # JPA 쿼리 패턴
        self.jpa_query_patterns = {
            'jpql_queries': [
                re.compile(r'@Query\s*\([\'"]([^\'"]*)[\'"]\)', re.IGNORECASE),
                re.compile(r'createQuery\s*\([\'"]([^\'"]*)[\'"]\)', re.IGNORECASE),
                re.compile(r'createNativeQuery\s*\([\'"]([^\'"]*)[\'"]\)', re.IGNORECASE),
            ],
            'method_name_queries': [
                re.compile(r'(\w+)(?:By|And|Or|OrderBy|Distinct|First|Top)(\w+)', re.IGNORECASE),
            ],
            'criteria_queries': [
                re.compile(r'CriteriaBuilder\s+(\w+)\s*=\s*(\w+)\.getCriteriaBuilder\(\)', re.IGNORECASE),
                re.compile(r'CriteriaQuery<(\w+)>\s+(\w+)\s*=\s*(\w+)\.createQuery\((\w+)\.class\)', re.IGNORECASE),
            ]
        }
        
        # JPA 엔티티 패턴
        self.jpa_entity_patterns = {
            'class_declarations': [
                re.compile(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{', re.IGNORECASE | re.DOTALL),
                re.compile(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{', re.IGNORECASE | re.DOTALL),
                re.compile(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*\{', re.IGNORECASE | re.DOTALL),
            ],
            'field_declarations': [
                re.compile(r'(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)(?:\s*=\s*([^;]+))?\s*;', re.IGNORECASE),
                re.compile(r'(\w+(?:<[^>]+>)?)\s+(\w+)(?:\s*=\s*([^;]+))?\s*;', re.IGNORECASE),
            ],
            'method_declarations': [
                re.compile(r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{', re.IGNORECASE | re.DOTALL),
                re.compile(r'(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{', re.IGNORECASE | re.DOTALL),
            ]
        }
        
        # JPA 관계 패턴
        self.jpa_relationship_patterns = {
            'one_to_one': [
                re.compile(r'@OneToOne\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@OneToOne', re.IGNORECASE),
            ],
            'one_to_many': [
                re.compile(r'@OneToMany\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@OneToMany', re.IGNORECASE),
            ],
            'many_to_one': [
                re.compile(r'@ManyToOne\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@ManyToOne', re.IGNORECASE),
            ],
            'many_to_many': [
                re.compile(r'@ManyToMany\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@ManyToMany', re.IGNORECASE),
            ],
            'join_column': [
                re.compile(r'@JoinColumn\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@JoinColumn', re.IGNORECASE),
            ],
            'join_table': [
                re.compile(r'@JoinTable\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'@JoinTable', re.IGNORECASE),
            ]
        }
    
    def _get_parser_type(self) -> str:
        return 'jpa'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        JPA 관련 파일을 파싱하여 메타데이터 추출 (재현율 우선)
        
        Args:
            content: JPA 관련 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 1. 기본 SQL 처리
        processed_content = content
        
        # 2. 테이블 별칭 해석
        alias_resolver = get_table_alias_resolver(context.get('default_schema', 'DEFAULT'))
        alias_mapping = alias_resolver.extract_table_alias_mapping(processed_content)
        
        # 3. 정규화
        normalized_content = self._normalize_content(processed_content)
        
        result = {
            'entities': self._extract_entities_aggressive(normalized_content),
            'jpa_annotations': self._extract_jpa_annotations_aggressive(normalized_content),
            'relationships': self._extract_relationships_aggressive(normalized_content),
            'queries': self._extract_queries_aggressive(normalized_content),
            'fields': self._extract_fields_aggressive(normalized_content),
            'methods': self._extract_methods_aggressive(normalized_content),
            'table_mappings': self._extract_table_mappings_aggressive(normalized_content),
            'column_mappings': self._extract_column_mappings_aggressive(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence,
            # 동적 쿼리 및 별칭 정보 추가
            'dynamic_blocks': dynamic_result.dynamic_blocks,
            'alias_mapping': alias_mapping,
            'original_content': content,
            'processed_content': processed_content
        }
        
        # 4. 별칭을 실제 테이블명으로 해석하여 엔티티/테이블 목록 업데이트
        resolved_entities = set()
        for entity in result.get('entities', []):
            if isinstance(entity, dict) and 'name' in entity:
                resolved_entity = alias_resolver.resolve_table_alias(entity['name'], alias_mapping)
                resolved_entities.add(resolved_entity)
        result['resolved_entities'] = list(resolved_entities)
        
        return result
    
    def _extract_entities_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 엔티티를 공격적으로 추출 (재현율 우선)"""
        entities = []
        
        # 1. @Entity 어노테이션이 있는 클래스 찾기
        entity_pattern = r'@Entity\s+(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)'
        entity_matches = re.finditer(entity_pattern, content, re.IGNORECASE)
        
        for match in entity_matches:
            entity_name = match.group(1)
            
            # 클래스 정보 추출
            class_info = self._extract_class_info(content, entity_name)
            
            entities.append({
                'name': entity_name,
                'type': 'entity',
                'class_info': class_info,
                'annotations': self._extract_entity_annotations(content, entity_name),
                'table_name': self._extract_table_name(content, entity_name)
            })
        
        # 2. @Table 어노테이션이 있는 클래스 찾기
        table_pattern = r'@Table\s+(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)'
        table_matches = re.finditer(table_pattern, content, re.IGNORECASE)
        
        for match in table_matches:
            entity_name = match.group(1)
            
            # 이미 추가된 엔티티인지 확인
            if not any(e['name'] == entity_name for e in entities):
                class_info = self._extract_class_info(content, entity_name)
                
                entities.append({
                    'name': entity_name,
                    'type': 'table_mapped',
                    'class_info': class_info,
                    'annotations': self._extract_entity_annotations(content, entity_name),
                    'table_name': self._extract_table_name(content, entity_name)
                })
        
        return entities
    
    def _extract_jpa_annotations_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 어노테이션을 공격적으로 추출 (재현율 우선)"""
        annotations = []
        
        # 1. 모든 어노테이션 추출
        for pattern in self.jpa_annotations['patterns']:
            matches = pattern.finditer(content)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                # JPA 관련 어노테이션인지 확인
                is_jpa_annotation = any(
                    jpa_anno.lower() in annotation_name.lower() 
                    for jpa_anno in self.jpa_annotations['entity_annotations']
                )
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0),
                    'is_jpa': is_jpa_annotation,
                    'type': 'annotation'
                })
        
        return annotations
    
    def _extract_relationships_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 관계를 공격적으로 추출 (재현율 우선)"""
        relationships = []
        
        # 1. OneToOne 관계
        for pattern in self.jpa_relationship_patterns['one_to_one']:
            matches = pattern.finditer(content)
            for match in matches:
                relationship_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'OneToOne',
                    'value': relationship_value,
                    'full_text': match.group(0),
                    'relationship_type': 'one_to_one'
                })
        
        # 2. OneToMany 관계
        for pattern in self.jpa_relationship_patterns['one_to_many']:
            matches = pattern.finditer(content)
            for match in matches:
                relationship_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'OneToMany',
                    'value': relationship_value,
                    'full_text': match.group(0),
                    'relationship_type': 'one_to_many'
                })
        
        # 3. ManyToOne 관계
        for pattern in self.jpa_relationship_patterns['many_to_one']:
            matches = pattern.finditer(content)
            for match in matches:
                relationship_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'ManyToOne',
                    'value': relationship_value,
                    'full_text': match.group(0),
                    'relationship_type': 'many_to_one'
                })
        
        # 4. ManyToMany 관계
        for pattern in self.jpa_relationship_patterns['many_to_many']:
            matches = pattern.finditer(content)
            for match in matches:
                relationship_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'ManyToMany',
                    'value': relationship_value,
                    'full_text': match.group(0),
                    'relationship_type': 'many_to_many'
                })
        
        # 5. JoinColumn 관계
        for pattern in self.jpa_relationship_patterns['join_column']:
            matches = pattern.finditer(content)
            for match in matches:
                join_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'JoinColumn',
                    'value': join_value,
                    'full_text': match.group(0),
                    'relationship_type': 'join_column'
                })
        
        # 6. JoinTable 관계
        for pattern in self.jpa_relationship_patterns['join_table']:
            matches = pattern.finditer(content)
            for match in matches:
                join_value = match.group(1) if len(match.groups()) > 0 and match.group(1) else ''
                relationships.append({
                    'type': 'JoinTable',
                    'value': join_value,
                    'full_text': match.group(0),
                    'relationship_type': 'join_table'
                })
        
        return relationships
    
    def _extract_queries_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 쿼리를 공격적으로 추출 (재현율 우선)"""
        queries = []
        
        # 1. JPQL 쿼리 추출
        for pattern in self.jpa_query_patterns['jpql_queries']:
            matches = pattern.finditer(content)
            for match in matches:
                query_text = match.group(1)
                queries.append({
                    'type': 'jpql',
                    'query': query_text,
                    'full_text': match.group(0),
                    'query_type': self._detect_query_type(query_text)
                })
        
        # 2. 메서드명 쿼리 추출
        for pattern in self.jpa_query_patterns['method_name_queries']:
            matches = pattern.finditer(content)
            for match in matches:
                prefix = match.group(1)
                suffix = match.group(2)
                queries.append({
                    'type': 'method_name',
                    'prefix': prefix,
                    'suffix': suffix,
                    'full_text': match.group(0),
                    'query_type': 'find'
                })
        
        # 3. Criteria 쿼리 추출
        for pattern in self.jpa_query_patterns['criteria_queries']:
            matches = pattern.finditer(content)
            for match in matches:
                queries.append({
                    'type': 'criteria',
                    'builder': match.group(1),
                    'query': match.group(2),
                    'entity_type': match.group(4),
                    'full_text': match.group(0),
                    'query_type': 'criteria'
                })
        
        return queries
    
    def _extract_fields_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 필드를 공격적으로 추출 (재현율 우선)"""
        fields = []
        
        for pattern in self.jpa_entity_patterns['field_declarations']:
            matches = pattern.finditer(content)
            for match in matches:
                field_type = match.group(1)
                field_name = match.group(2)
                field_value = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                
                # 필드에 대한 어노테이션 추출
                field_annotations = self._extract_field_annotations(content, field_name)
                
                fields.append({
                    'type': field_type,
                    'name': field_name,
                    'value': field_value,
                    'annotations': field_annotations,
                    'is_id': any('@Id' in anno['full_text'] for anno in field_annotations),
                    'is_column': any('@Column' in anno['full_text'] for anno in field_annotations)
                })
        
        return fields
    
    def _extract_methods_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JPA 메서드를 공격적으로 추출 (재현율 우선)"""
        methods = []
        
        for pattern in self.jpa_entity_patterns['method_declarations']:
            matches = pattern.finditer(content)
            for match in matches:
                return_type = match.group(1)
                method_name = match.group(2)
                parameters = match.group(3)
                
                # 메서드에 대한 어노테이션 추출
                method_annotations = self._extract_method_annotations(content, method_name)
                
                methods.append({
                    'return_type': return_type,
                    'name': method_name,
                    'parameters': parameters,
                    'annotations': method_annotations,
                    'is_query_method': any('@Query' in anno['full_text'] for anno in method_annotations)
                })
        
        return methods
    
    def _extract_table_mappings_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """테이블 매핑을 공격적으로 추출 (재현율 우선)"""
        table_mappings = []
        
        # @Table 어노테이션에서 테이블명 추출
        table_pattern = r'@Table\s*\(([^)]*)\)'
        table_matches = re.finditer(table_pattern, content, re.IGNORECASE)
        
        for match in table_matches:
            table_attrs = match.group(1)
            table_name = self._extract_table_name_from_attrs(table_attrs)
            
            if table_name:
                table_mappings.append({
                    'table_name': table_name,
                    'attributes': table_attrs,
                    'full_text': match.group(0),
                    'type': 'table_mapping'
                })
        
        return table_mappings
    
    def _extract_column_mappings_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """컬럼 매핑을 공격적으로 추출 (재현율 우선)"""
        column_mappings = []
        
        # @Column 어노테이션에서 컬럼명 추출
        column_pattern = r'@Column\s*\(([^)]*)\)'
        column_matches = re.finditer(column_pattern, content, re.IGNORECASE)
        
        for match in column_matches:
            column_attrs = match.group(1)
            column_name = self._extract_column_name_from_attrs(column_attrs)
            
            if column_name:
                column_mappings.append({
                    'column_name': column_name,
                    'attributes': column_attrs,
                    'full_text': match.group(0),
                    'type': 'column_mapping'
                })
        
        return column_mappings
    
    def _extract_class_info(self, content: str, class_name: str) -> Dict[str, Any]:
        """클래스 정보 추출"""
        class_info = {
            'name': class_name,
            'extends': None,
            'implements': [],
            'is_abstract': False,
            'is_final': False
        }
        
        # 클래스 선언 라인 찾기
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+' + re.escape(class_name) + r'(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*'
        class_match = re.search(class_pattern, content, re.IGNORECASE)
        
        if class_match:
            class_info['extends'] = class_match.group(1) if class_match.group(1) else None
            if class_match.group(2):
                class_info['implements'] = [impl.strip() for impl in class_match.group(2).split(',')]
            
            # abstract, final 키워드 확인
            class_line = class_match.group(0)
            class_info['is_abstract'] = 'abstract' in class_line.lower()
            class_info['is_final'] = 'final' in class_line.lower()
        
        return class_info
    
    def _extract_entity_annotations(self, content: str, entity_name: str) -> List[Dict[str, Any]]:
        """엔티티에 대한 어노테이션 추출"""
        annotations = []
        
        # 엔티티 클래스 주변의 어노테이션 찾기
        entity_context = self._get_entity_context(content, entity_name)
        
        for pattern in self.jpa_annotations['patterns']:
            matches = pattern.finditer(entity_context)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0)
                })
        
        return annotations
    
    def _extract_table_name(self, content: str, entity_name: str) -> str:
        """테이블명 추출"""
        # @Table 어노테이션에서 name 속성 추출
        table_pattern = rf'@Table\s*\(([^)]*)\)\s*(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+{re.escape(entity_name)}'
        table_match = re.search(table_pattern, content, re.IGNORECASE)
        
        if table_match:
            table_attrs = table_match.group(1)
            return self._extract_table_name_from_attrs(table_attrs)
        
        # @Table 어노테이션이 없으면 클래스명을 테이블명으로 사용
        return entity_name.upper()
    
    def _extract_table_name_from_attrs(self, attrs: str) -> str:
        """테이블 어노테이션 속성에서 테이블명 추출"""
        # name="table_name" 형태에서 추출
        name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if name_match:
            return name_match.group(1)
        return ""
    
    def _extract_column_name_from_attrs(self, attrs: str) -> str:
        """컬럼 어노테이션 속성에서 컬럼명 추출"""
        # name="column_name" 형태에서 추출
        name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if name_match:
            return name_match.group(1)
        return ""
    
    def _extract_field_annotations(self, content: str, field_name: str) -> List[Dict[str, Any]]:
        """필드에 대한 어노테이션 추출"""
        annotations = []
        
        # 필드 주변의 어노테이션 찾기
        field_context = self._get_field_context(content, field_name)
        
        for pattern in self.jpa_annotations['patterns']:
            matches = pattern.finditer(field_context)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0)
                })
        
        return annotations
    
    def _extract_method_annotations(self, content: str, method_name: str) -> List[Dict[str, Any]]:
        """메서드에 대한 어노테이션 추출"""
        annotations = []
        
        # 메서드 주변의 어노테이션 찾기
        method_context = self._get_method_context(content, method_name)
        
        for pattern in self.jpa_annotations['patterns']:
            matches = pattern.finditer(method_context)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0)
                })
        
        return annotations
    
    def _get_entity_context(self, content: str, entity_name: str) -> str:
        """엔티티 클래스 주변 컨텍스트 추출"""
        # 클래스 시작부터 끝까지의 컨텍스트
        class_start = content.find(f"class {entity_name}")
        if class_start == -1:
            return ""
        
        # 클래스 시작 위치에서 앞쪽 어노테이션들 포함
        context_start = max(0, class_start - 500)
        context_end = min(len(content), class_start + 1000)
        
        return content[context_start:context_end]
    
    def _get_field_context(self, content: str, field_name: str) -> str:
        """필드 주변 컨텍스트 추출"""
        # 필드 선언 주변의 컨텍스트
        field_start = content.find(field_name)
        if field_start == -1:
            return ""
        
        # 필드 시작 위치에서 앞쪽 어노테이션들 포함
        context_start = max(0, field_start - 200)
        context_end = min(len(content), field_start + 100)
        
        return content[context_start:context_end]
    
    def _get_method_context(self, content: str, method_name: str) -> str:
        """메서드 주변 컨텍스트 추출"""
        # 메서드 선언 주변의 컨텍스트
        method_start = content.find(f"{method_name}(")
        if method_start == -1:
            return ""
        
        # 메서드 시작 위치에서 앞쪽 어노테이션들 포함
        context_start = max(0, method_start - 200)
        context_end = min(len(content), method_start + 100)
        
        return content[context_start:context_end]
    
    def _detect_query_type(self, query_text: str) -> str:
        """쿼리 타입 감지"""
        query_upper = query_text.upper()
        
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        else:
            return 'UNKNOWN'
    
    def _remove_comments(self, content: str) -> str:
        """JPA 관련 주석 제거"""
        # Java 주석 제거
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'jpa'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)
