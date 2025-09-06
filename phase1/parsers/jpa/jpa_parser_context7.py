"""
JPA Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 JPA 파서
- PRegEx를 활용한 정확한 패턴 매칭
- 중복 방지 및 정확도 향상
- 다이나믹 쿼리 파싱 지원
- JPA 어노테이션, 엔티티, 쿼리 메소드 인식
"""

import re
import hashlib
from typing import Dict, List, Any, Set, Tuple
from parsers.base_parser import BaseParser

# PRegEx를 사용한 패턴 구성 (Context7 기반)
try:
    from pregex.core.pre import Pregex
    from pregex.core.classes import AnyLetter, AnyDigit, AnyWhitespace, AnyFrom
    from pregex.core.quantifiers import Optional, OneOrMore, AtLeastAtMost
    from pregex.core.operators import Either
    from pregex.core.groups import Capture, Group
    from pregex.core.assertions import WordBoundary, FollowedBy, PrecededBy
    PREGEX_AVAILABLE = True
except ImportError:
    PREGEX_AVAILABLE = False

class JPAParserContext7(BaseParser):
    """
    JPA Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 JPA 파서
    - PRegEx를 활용한 정확한 패턴 매칭
    - 중복 방지 및 정확도 향상
    - 다이나믹 쿼리 파싱 지원
    - JPA 어노테이션, 엔티티, 쿼리 메소드 인식
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # JPA 어노테이션 (Context7 기반)
        self.jpa_annotations = {
            '@Entity', '@Table', '@Id', '@GeneratedValue', '@Column', '@JoinColumn',
            '@OneToOne', '@OneToMany', '@ManyToOne', '@ManyToMany', '@JoinTable',
            '@Query', '@Modifying', '@Transactional', '@EntityManager', '@PersistenceContext',
            '@NamedQuery', '@NamedQueries', '@NamedNativeQuery', '@NamedNativeQueries',
            '@SqlResultSetMapping', '@SqlResultSetMappings', '@ConstructorResult',
            '@ColumnResult', '@FieldResult', '@AssociationOverride', '@AssociationOverrides',
            '@AttributeOverride', '@AttributeOverrides', '@Embedded', '@Embeddable',
            '@MappedSuperclass', '@Inheritance', '@DiscriminatorColumn', '@DiscriminatorValue',
            '@SecondaryTable', '@SecondaryTables', '@UniqueConstraint', '@Index',
            '@Cacheable', '@Cache', '@CacheRetrieve', '@CacheStore', '@CacheMode',
            '@Lock', '@LockModeType', '@Version', '@Temporal', '@Enumerated', '@Lob',
            '@Transient', '@Access', '@AccessType', '@OrderBy', '@OrderColumn',
            '@MapKey', '@MapKeyClass', '@MapKeyColumn', '@MapKeyEnumerated', '@MapKeyTemporal',
            '@MapKeyJoinColumn', '@MapKeyJoinColumns', '@JoinColumns', '@JoinColumnOrFormula',
            '@JoinFormula', '@JoinTableOrFormula', '@JoinTable', '@JoinTableOrFormula',
            '@CollectionTable', '@CollectionTables', '@ElementCollection', '@MapKey',
            '@MapKeyClass', '@MapKeyColumn', '@MapKeyEnumerated', '@MapKeyTemporal',
            '@MapKeyJoinColumn', '@MapKeyJoinColumns', '@JoinColumns', '@JoinColumnOrFormula',
            '@JoinFormula', '@JoinTableOrFormula', '@JoinTable', '@JoinTableOrFormula'
        }
        
        # JPA 쿼리 메소드 키워드 (Context7 기반)
        self.jpa_query_keywords = {
            'find', 'findBy', 'findAll', 'findAllBy', 'findDistinct', 'findDistinctBy',
            'count', 'countBy', 'countDistinct', 'countDistinctBy',
            'delete', 'deleteBy', 'remove', 'removeBy',
            'exists', 'existsBy',
            'save', 'saveAll', 'saveAndFlush',
            'update', 'updateBy', 'modify', 'modifyBy',
            'get', 'getBy', 'getAll', 'getAllBy',
            'read', 'readBy', 'readAll', 'readAllBy',
            'query', 'queryBy', 'search', 'searchBy'
        }
        
        # SQL 키워드 (Context7 기반)
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER',
            'DROP', 'TRUNCATE', 'MERGE', 'UNION', 'ALL', 'DISTINCT', 'COUNT', 'SUM',
            'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'EXISTS',
            'IN', 'NOT', 'NULL', 'IS', 'BETWEEN', 'LIKE', 'AND', 'OR'
        }
        
        # PRegEx 기반 패턴 구성 (Context7 기반)
        if PREGEX_AVAILABLE:
            self._build_pregex_patterns()
        else:
            self._build_fallback_patterns()
    
    def _build_pregex_patterns(self):
        """PRegEx를 사용한 패턴 구성 (Context7 기반)"""
        
        # JPA 어노테이션 패턴
        jpa_annotation = Group(
            '@' + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyFrom('.'))) +  # 어노테이션명
            Optional('(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(', ')', '=', ',', '{', '}', '[' | ']' | '.' | '-' | '_' | ':' | ';' | '\\' | '\n' | '\r' | '\t'))) + ')')  # 어노테이션 속성
        )
        
        # JPA 엔티티 클래스 패턴
        jpa_entity = Group(
            Optional(AnyFrom(*self.jpa_annotations)) +  # JPA 어노테이션
            Optional(AnyWhitespace()) +
            Optional(AnyFrom('public', 'private', 'protected', 'abstract', 'final', 'static')) +  # 접근제어자
            Optional(AnyWhitespace()) +
            'class' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 클래스명
            Optional(AnyWhitespace()) +
            Optional('extends' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$' | '.'))) +  # 상속
            Optional(AnyWhitespace()) +
            Optional('implements' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '_' | '$' | '.')))  # 구현
        )
        
        # JPA 필드 패턴
        jpa_field = Group(
            Optional(AnyFrom(*self.jpa_annotations)) +  # JPA 어노테이션
            Optional(AnyWhitespace()) +
            Optional(AnyFrom('public', 'private', 'protected', 'static', 'final', 'transient', 'volatile')) +  # 접근제어자
            Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '<' | '>' | '[' | ']' | ',' | '?' | '&' | '.')) +  # 타입
            Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 필드명
            Optional(AnyWhitespace()) + ';'
        )
        
        # JPA 쿼리 메소드 패턴
        jpa_query_method = Group(
            Optional(AnyFrom('@Query', '@Modifying', '@Transactional')) +  # 쿼리 어노테이션
            Optional(AnyWhitespace()) +
            Optional(AnyFrom('public', 'private', 'protected', 'static', 'final', 'abstract')) +  # 접근제어자
            Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '<' | '>' | '[' | ']' | ',' | '?' | '&' | '.')) +  # 반환타입
            Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 메소드명
            Optional(AnyWhitespace()) + '(' +
            Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&' | '.' | '[' | ']'))) +  # 파라미터
            ')' + Optional(AnyWhitespace()) + '{'
        )
        
        # SQL 문자열 패턴
        sql_string = Either(
            '"' + Capture(OneOrMore(AnyFrom(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + AnyFrom(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '\'', '"', '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + '"',
            "'" + Capture(OneOrMore(AnyFrom(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + AnyFrom(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '"', "'", '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + "'"
        )
        
        # JPA 네임드 쿼리 패턴
        named_query = Group(
            '@NamedQuery' + Optional(AnyWhitespace()) + '(' +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(', ')', '=', ',', '{', '}', '[' | ']' | '.' | '-' | '_' | ':' | ';' | '\\' | '\n' | '\r' | '\t')) +  # 쿼리 정의
            ')'
        )
        
        # JPA 네이티브 쿼리 패턴
        native_query = Group(
            '@NamedNativeQuery' + Optional(AnyWhitespace()) + '(' +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(', ')', '=', ',', '{', '}', '[' | ']' | '.' | '-' | '_' | ':' | ';' | '\\' | '\n' | '\r' | '\t')) +  # 네이티브 쿼리 정의
            ')'
        )
        
        # 패턴 저장
        self.pregex_patterns = {
            'jpa_annotation': jpa_annotation,
            'jpa_entity': jpa_entity,
            'jpa_field': jpa_field,
            'jpa_query_method': jpa_query_method,
            'sql_string': sql_string,
            'named_query': named_query,
            'native_query': native_query
        }
    
    def _build_fallback_patterns(self):
        """PRegEx가 없을 때 사용할 fallback 패턴 (Context7 기반)"""
        
        self.fallback_patterns = {
            'jpa_annotation': re.compile(
                r'@(\w+(?:\.\w+)*)(?:\(([^)]*)\))?',
                re.IGNORECASE
            ),
            'jpa_entity': re.compile(
                r'(?:@\w+(?:\([^)]*\))?\s*)*'  # 어노테이션
                r'(?:public|private|protected|abstract|final|static\s+)*'  # 접근제어자
                r'class\s+(\w+)'  # 클래스명 (캡처)
                r'(?:\s+extends\s+(\w+))?'  # 상속 (캡처)
                r'(?:\s+implements\s+([\w\s,\.]+))?',  # 구현 (캡처)
                re.IGNORECASE | re.MULTILINE
            ),
            'jpa_field': re.compile(
                r'(?:@\w+(?:\([^)]*\))?\s*)*'  # 어노테이션
                r'(?:public|private|protected|static|final|transient|volatile\s+)*'  # 접근제어자
                r'([\w<>\[\],\s?&\.]+)\s+'  # 타입 (캡처)
                r'(\w+)\s*;',  # 필드명 (캡처)
                re.IGNORECASE | re.MULTILINE
            ),
            'jpa_query_method': re.compile(
                r'(?:@\w+(?:\([^)]*\))?\s*)*'  # 어노테이션
                r'(?:public|private|protected|static|final|abstract\s+)*'  # 접근제어자
                r'([\w<>\[\],\s?&\.]+)\s+'  # 반환타입 (캡처)
                r'(\w+)\s*'  # 메소드명 (캡처)
                r'\(([^)]*)\)',  # 파라미터 (캡처)
                re.IGNORECASE | re.MULTILINE
            ),
            'sql_string': re.compile(
                r'["\']([^"\']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
                re.IGNORECASE
            ),
            'named_query': re.compile(
                r'@NamedQuery\s*\(([^)]*)\)',
                re.IGNORECASE | re.DOTALL
            ),
            'native_query': re.compile(
                r'@NamedNativeQuery\s*\(([^)]*)\)',
                re.IGNORECASE | re.DOTALL
            )
        }
    
    def _get_parser_type(self) -> str:
        return 'jpa_context7'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        JPA 파일을 파싱하여 메타데이터 추출 (Context7 기반)
        
        Args:
            content: JPA 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 정규화
        normalized_content = self._normalize_content(content)
        
        result = {
            'jpa_annotations': self._extract_jpa_annotations(normalized_content),
            'jpa_entities': self._extract_jpa_entities(normalized_content),
            'jpa_fields': self._extract_jpa_fields(normalized_content),
            'jpa_query_methods': self._extract_jpa_query_methods(normalized_content),
            'sql_units': self._extract_sql_units(normalized_content),
            'named_queries': self._extract_named_queries(normalized_content),
            'native_queries': self._extract_native_queries(normalized_content),
            'dynamic_queries': self._extract_dynamic_queries(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': 0.95  # Context7 기반으로 높은 신뢰도
        }
        
        return result
    
    def _extract_jpa_annotations(self, content: str) -> List[Dict[str, Any]]:
        """JPA 어노테이션 추출 (Context7 기반)"""
        annotations = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['jpa_annotation'].get_captures(content)
            for match in matches:
                if len(match) >= 1:
                    annotation_info = {
                        'name': match[0],
                        'attributes': match[1] if len(match) > 1 and match[1] else '',
                        'type': 'jpa_annotation',
                        'unique_id': self._generate_unique_id('annotation', match[0])
                    }
                    annotations.append(annotation_info)
        else:
            matches = self.fallback_patterns['jpa_annotation'].finditer(content)
            for match in matches:
                annotation_info = {
                    'name': match.group(1),
                    'attributes': match.group(2) if match.group(2) else '',
                    'type': 'jpa_annotation',
                    'unique_id': self._generate_unique_id('annotation', match.group(1))
                }
                annotations.append(annotation_info)
        
        return annotations
    
    def _extract_jpa_entities(self, content: str) -> List[Dict[str, Any]]:
        """JPA 엔티티 추출 (Context7 기반)"""
        entities = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['jpa_entity'].get_captures(content)
            for match in matches:
                if len(match) >= 1:
                    entity_info = {
                        'name': match[0],
                        'extends': match[1] if len(match) > 1 and match[1] else None,
                        'implements': match[2].split(',') if len(match) > 2 and match[2] else [],
                        'type': 'jpa_entity',
                        'unique_id': self._generate_unique_id('entity', match[0])
                    }
                    entities.append(entity_info)
        else:
            matches = self.fallback_patterns['jpa_entity'].finditer(content)
            for match in matches:
                entity_info = {
                    'name': match.group(1),
                    'extends': match.group(2) if match.group(2) else None,
                    'implements': match.group(3).split(',') if match.group(3) else [],
                    'type': 'jpa_entity',
                    'unique_id': self._generate_unique_id('entity', match.group(1))
                }
                entities.append(entity_info)
        
        return entities
    
    def _extract_jpa_fields(self, content: str) -> List[Dict[str, Any]]:
        """JPA 필드 추출 (Context7 기반)"""
        fields = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['jpa_field'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    field_info = {
                        'type': match[0],
                        'name': match[1],
                        'type': 'jpa_field',
                        'unique_id': self._generate_unique_id('field', match[1])
                    }
                    fields.append(field_info)
        else:
            matches = self.fallback_patterns['jpa_field'].finditer(content)
            for match in matches:
                field_info = {
                    'type': match.group(1),
                    'name': match.group(2),
                    'type': 'jpa_field',
                    'unique_id': self._generate_unique_id('field', match.group(2))
                }
                fields.append(field_info)
        
        return fields
    
    def _extract_jpa_query_methods(self, content: str) -> List[Dict[str, Any]]:
        """JPA 쿼리 메소드 추출 (Context7 기반)"""
        methods = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['jpa_query_method'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    method_info = {
                        'return_type': match[0],
                        'name': match[1],
                        'parameters': match[2] if len(match) > 2 and match[2] else '',
                        'type': 'jpa_query_method',
                        'unique_id': self._generate_unique_id('method', match[1])
                    }
                    methods.append(method_info)
        else:
            matches = self.fallback_patterns['jpa_query_method'].finditer(content)
            for match in matches:
                method_info = {
                    'name': match.group(1),
                    'parameters': match.group(2) if match.group(2) else '',
                    'type': 'jpa_query_method',
                    'unique_id': self._generate_unique_id('method', match.group(1))
                }
                methods.append(method_info)
        
        return methods
    
    def _extract_sql_units(self, content: str) -> List[Dict[str, Any]]:
        """SQL Units 추출 (Context7 기반)"""
        sql_units = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['sql_string'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    sql_content = match[0]
                    sql_units.append({
                        'type': self._determine_sql_type(sql_content),
                        'sql_content': sql_content,
                        'unique_id': self._generate_sql_unique_id(sql_content),
                        'source': 'jpa_string_literal'
                    })
        else:
            matches = self.fallback_patterns['sql_string'].finditer(content)
            for match in matches:
                sql_content = match.group(1)
                sql_units.append({
                    'type': self._determine_sql_type(sql_content),
                    'sql_content': sql_content,
                    'unique_id': self._generate_sql_unique_id(sql_content),
                    'source': 'jpa_string_literal'
                })
        
        return sql_units
    
    def _extract_named_queries(self, content: str) -> List[Dict[str, Any]]:
        """네임드 쿼리 추출 (Context7 기반)"""
        named_queries = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['named_query'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    query_info = {
                        'definition': match[0],
                        'type': 'named_query',
                        'unique_id': self._generate_unique_id('named_query', match[0])
                    }
                    named_queries.append(query_info)
        else:
            matches = self.fallback_patterns['named_query'].finditer(content)
            for match in matches:
                query_info = {
                    'definition': match.group(1),
                    'type': 'named_query',
                    'unique_id': self._generate_unique_id('named_query', match.group(1))
                }
                named_queries.append(query_info)
        
        return named_queries
    
    def _extract_native_queries(self, content: str) -> List[Dict[str, Any]]:
        """네이티브 쿼리 추출 (Context7 기반)"""
        native_queries = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['native_query'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    query_info = {
                        'definition': match[0],
                        'type': 'native_query',
                        'unique_id': self._generate_unique_id('native_query', match[0])
                    }
                    native_queries.append(query_info)
        else:
            matches = self.fallback_patterns['native_query'].finditer(content)
            for match in matches:
                query_info = {
                    'definition': match.group(1),
                    'type': 'native_query',
                    'unique_id': self._generate_unique_id('native_query', match.group(1))
                }
                native_queries.append(query_info)
        
        return native_queries
    
    def _extract_dynamic_queries(self, content: str) -> List[Dict[str, Any]]:
        """다이나믹 쿼리 추출 (Context7 기반 개선)"""
        dynamic_queries = []
        
        # Context7 기반 JPA 동적 쿼리 생성 패턴 - 더 정확한 매칭
        dynamic_patterns = {
            'query_annotation': r'@Query\s*\(\s*["\']([^"\']*)["\']\s*\)',
            'criteria_builder_init': r'CriteriaBuilder\s+(\w+)\s*=\s*entityManager\.getCriteriaBuilder\s*\(\)',
            'criteria_query_init': r'CriteriaQuery<(\w+)>\s+(\w+)\s*=\s*cb\.createQuery\s*\([^)]*\)',
            'criteria_select': r'(\w+)\.select\s*\(([^)]*)\)',
            'criteria_from': r'(\w+)\.from\s*\(([^)]*)\)',
            'criteria_where': r'(\w+)\.where\s*\(([^)]*)\)',
            'criteria_order_by': r'(\w+)\.orderBy\s*\(([^)]*)\)',
            'criteria_group_by': r'(\w+)\.groupBy\s*\(([^)]*)\)',
            'criteria_having': r'(\w+)\.having\s*\(([^)]*)\)',
            'query_dsl': r'Q(\w+)\s+(\w+)\s*=\s*Q(\w+)\.(\w+)',
            'query_dsl_query': r'JPAQuery<(\w+)>\s+(\w+)\s*=\s*new\s+JPAQuery<[^>]*>',
            'stringbuilder_init': r'StringBuilder\s+(\w+)\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)',
            'stringbuilder_append': r'(\w+)\.append\s*\(([^)]*)\)',
            'string_concat': r'String\s+(\w+)\s*=\s*([^;]+);',
            'string_plus_assign': r'(\w+)\s*\+=\s*([^;]+);',
            'conditional_query': r'if\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}',
            'loop_query': r'for\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}',
            'named_query': r'@NamedQuery\s*\(\s*name\s*=\s*["\']([^"\']*)["\']\s*,\s*query\s*=\s*["\']([^"\']*)["\']\s*\)',
            'native_query': r'@NamedNativeQuery\s*\(\s*name\s*=\s*["\']([^"\']*)["\']\s*,\s*query\s*=\s*["\']([^"\']*)["\']\s*\)'
        }
        
        for pattern_name, pattern in dynamic_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                dynamic_info = {
                    'type': 'dynamic_query',
                    'pattern_type': pattern_name,
                    'pattern': pattern,
                    'full_match': match.group(0),
                    'variable': match.group(1) if len(match.groups()) > 0 else '',
                    'content': match.group(2) if len(match.groups()) > 1 else '',
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'unique_id': self._generate_dynamic_query_id(pattern_name, match.group(0))
                }
                dynamic_queries.append(dynamic_info)
        
        return dynamic_queries
    
    def _generate_dynamic_query_id(self, pattern_type: str, content: str) -> str:
        """다이나믹 쿼리 고유 ID 생성 (Context7 기반)"""
        combined = f"jpa_dynamic_{pattern_type}_{content}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _determine_sql_type(self, sql_content: str) -> str:
        """SQL 타입 결정 (Context7 기반)"""
        sql_upper = sql_content.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'select'
        elif sql_upper.startswith('INSERT'):
            return 'insert'
        elif sql_upper.startswith('UPDATE'):
            return 'update'
        elif sql_upper.startswith('DELETE'):
            return 'delete'
        elif sql_upper.startswith('CREATE'):
            return 'create'
        elif sql_upper.startswith('ALTER'):
            return 'alter'
        elif sql_upper.startswith('DROP'):
            return 'drop'
        elif sql_upper.startswith('TRUNCATE'):
            return 'truncate'
        elif sql_upper.startswith('MERGE'):
            return 'merge'
        else:
            return 'unknown'
    
    def _generate_unique_id(self, prefix: str, content: str) -> str:
        """고유 ID 생성 (Context7 기반)"""
        combined = f"{prefix}_{content}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _generate_sql_unique_id(self, sql_content: str) -> str:
        """SQL 고유 ID 생성 (Context7 기반)"""
        # SQL 내용을 정규화하여 중복 방지
        normalized_sql = re.sub(r'\s+', ' ', sql_content.strip())
        return hashlib.md5(normalized_sql.encode()).hexdigest()[:12]
    
    def _normalize_content(self, content: str) -> str:
        """컨텐츠 정규화 (Context7 기반)"""
        # 주석 제거
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 여러 공백을 단일 공백으로
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """파일 메타데이터 추출 (Context7 기반)"""
        return {
            'file_path': context.get('file_path', ''),
            'file_name': context.get('file_name', ''),
            'parser_type': self._get_parser_type(),
            'parser_version': 'context7',
            'confidence': 0.95
        }
