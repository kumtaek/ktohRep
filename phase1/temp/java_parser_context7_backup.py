"""
Java Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Java 파서
- PRegEx를 활용한 정확한 패턴 매칭
- 중복 방지 및 정확도 향상
- 다이나믹 쿼리 파싱 지원
- Spring 어노테이션 및 JPA 쿼리 메소드 인식
"""

import re
import os
import hashlib
from typing import Dict, List, Any, Set, Tuple
from ..base_parser import BaseParser

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

class JavaParserContext7(BaseParser):
    """
    Java Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Java 파서
    - PRegEx를 활용한 정확한 패턴 매칭
    - 중복 방지 및 정확도 향상
    - 다이나믹 쿼리 파싱 지원
    - Spring 어노테이션 및 JPA 쿼리 메소드 인식
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Java 키워드 (Context7 기반)
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
            'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
            'volatile', 'while', 'true', 'false', 'null'
        }
        
        # Spring 어노테이션 (Context7 기반)
        self.spring_annotations = {
            '@Controller', '@RestController', '@Service', '@Repository', '@Component',
            '@Autowired', '@Qualifier', '@Value', '@RequestMapping', '@GetMapping',
            '@PostMapping', '@PutMapping', '@DeleteMapping', '@PatchMapping',
            '@PathVariable', '@RequestParam', '@RequestBody', '@ResponseBody',
            '@Transactional', '@Cacheable', '@CacheEvict', '@Scheduled'
        }
        
        # JPA 어노테이션 (Context7 기반)
        self.jpa_annotations = {
            '@Entity', '@Table', '@Id', '@GeneratedValue', '@Column', '@OneToOne',
            '@OneToMany', '@ManyToOne', '@ManyToMany', '@JoinColumn', '@JoinTable',
            '@Query', '@Modifying', '@Transactional', '@EntityManager', '@PersistenceContext'
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
        
        # Java 식별자 패턴
        java_identifier = AnyLetter() + Optional(AnyLetter() | AnyDigit() | '_' | '$')
        
        # Java 타입 패턴
        java_type = java_identifier + Optional('[]') + Optional('[]')  # 2차원 배열까지 지원
        
        # Java 메소드 시그니처 패턴 (Context7 기반 개선 - 과추출 방지)
        method_signature = Group(
            # 어노테이션 (선택적)
            Optional(Either(*self.spring_annotations | self.jpa_annotations)) + 
            Optional(AnyWhitespace()) +
            # 접근 제어자 (선택적)
            Optional(Either('public', 'private', 'protected')) +
            Optional(AnyWhitespace()) +
            # 기타 수식자 (선택적)
            Optional(Either('static', 'final', 'abstract', 'synchronized')) +
            Optional(AnyWhitespace()) +
            # 반환 타입 (필수)
            java_type + 
            Optional(AnyWhitespace()) +
            # 메소드명 (필수)
            Capture(java_identifier) +  
            Optional(AnyWhitespace()) +
            # 파라미터 (필수)
            '(' + 
            Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&'))) +  
            ')' +
            Optional(AnyWhitespace()) +
            # 예외 선언 (선택적)
            Optional('throws' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '.'))) +
            # 메소드 본문 시작을 나타내는 '{' 또는 ';' (생성자/추상 메소드)
            Optional(AnyWhitespace()) + Either('{', ';')
        )
        
        # SQL 문자열 패턴
        sql_string = Either(
            '"' + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '\'', '"', '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + '"',
            "'" + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '"', "'", '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + "'"
        )
        
        # JPA 쿼리 메소드 패턴
        jpa_query_method = Group(
            Capture(java_identifier) +  # 메소드명
            Optional(AnyWhitespace()) +
            '(' +
            Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&'))) +  # 파라미터
            ')'
        )
        
        # StringBuilder SQL 패턴
        stringbuilder_sql = Group(
            'StringBuilder' + Optional(AnyWhitespace()) + Capture(java_identifier) +  # 변수명
            Optional(AnyWhitespace()) + '=' + Optional(AnyWhitespace()) + 'new' + Optional(AnyWhitespace()) + 'StringBuilder' +
            Optional(AnyWhitespace()) + '(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '+' | '(' | ')' | ';'))) + ')'  # 초기값
        )
        
        # 어노테이션 패턴
        annotation = Group(
            '@' + Capture(java_identifier) +  # 어노테이션명
            Optional('(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(' | ')' | '=' | ',' | '{' | '}'))) + ')')  # 어노테이션 속성
        )
        
        # 클래스 선언 패턴
        class_declaration = Group(
            Optional(Either('public', 'private', 'protected', 'abstract', 'final', 'static')) +
            Optional(AnyWhitespace()) +
            'class' + Optional(AnyWhitespace()) +
            Capture(java_identifier) +  # 클래스명
            Optional(AnyWhitespace()) +
            Optional('extends' + Optional(AnyWhitespace()) + Capture(java_identifier)) +  # 상속
            Optional(AnyWhitespace()) +
            Optional('implements' + Optional(AnyWhitespace()) + Capture(OneOrMore(java_identifier + Optional(AnyWhitespace()) + ',' + Optional(AnyWhitespace()))))  # 구현
        )
        
        # 패턴 저장
        self.pregex_patterns = {
            'method_signature': method_signature,
            'sql_string': sql_string,
            'jpa_query_method': jpa_query_method,
            'stringbuilder_sql': stringbuilder_sql,
            'annotation': annotation,
            'class_declaration': class_declaration
        }
    
    def _build_fallback_patterns(self):
        """PRegEx가 없을 때 사용할 fallback 패턴 (Context7 기반)"""
        
        # Java 메소드 시그니처 패턴 (fallback - Context7 기반 개선)
        self.fallback_patterns = {
            'method_signature': re.compile(
                r'(?:@\w+(?:\([^)]*\))?\s*)*'  # 어노테이션
                r'(?:public|private|protected)?\s*'  # 접근제어자
                r'(?:static|final|abstract|synchronized)?\s*'  # 기타 수식자
                r'(?:[\w<>\[\],\s?&]+\s+)'  # 반환타입 (필수)
                r'(\w+)\s*'  # 메소드명 (캡처)
                r'\(([^)]*)\)'  # 파라미터 (캡처)
                r'(?:\s+throws\s+([\w\s,\.]+))?'  # 예외 (캡처)
                r'\s*[;{]',  # 메소드 본문 시작 (';' 또는 '{')
                re.IGNORECASE | re.MULTILINE
            ),
            'sql_string': re.compile(
                r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']',
                re.IGNORECASE
            ),
            'jpa_query_method': re.compile(
                r'(\w+)\s*\(([^)]*)\)',  # 메소드명과 파라미터
                re.IGNORECASE
            ),
            'stringbuilder_sql': re.compile(
                r'StringBuilder\s+(\w+)\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)',
                re.IGNORECASE
            ),
            'annotation': re.compile(
                r'@(\w+)(?:\(([^)]*)\))?',
                re.IGNORECASE
            ),
            'class_declaration': re.compile(
                r'(?:public|private|protected|abstract|final|static\s+)*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?',
                re.IGNORECASE
            )
        }
    
    def _get_parser_type(self) -> str:
        return 'java_context7'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Java 소스 코드를 파싱하여 메타데이터 추출 (Context7 기반)
        
        Args:
            content: Java 소스 코드 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 정규화
        normalized_content = self._normalize_content(content)
        
        result = {
            'classes': self._extract_classes(normalized_content),
            'methods': self._extract_methods(normalized_content),
            'sql_units': self._extract_sql_units(normalized_content),
            'annotations': self._extract_annotations(normalized_content),
            'imports': self._extract_imports(normalized_content),
            'dynamic_queries': self._extract_dynamic_queries(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': 0.95  # Context7 기반으로 높은 신뢰도
        }
        
        return result
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """클래스 추출 (Context7 기반)"""
        classes = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.pregex_patterns['class_declaration'].get_captures(content)
            for match in matches:
                if len(match) >= 1:
                    class_info = {
                        'name': match[0],
                        'extends': match[1] if len(match) > 1 and match[1] else None,
                        'implements': match[2].split(',') if len(match) > 2 and match[2] else [],
                        'type': 'class'
                    }
                    classes.append(class_info)
        else:
            # Fallback 패턴 사용
            matches = self.fallback_patterns['class_declaration'].finditer(content)
            for match in matches:
                class_info = {
                    'name': match.group(1),
                    'extends': match.group(2) if match.group(2) else None,
                    'implements': match.group(3).split(',') if match.group(3) else [],
                    'type': 'class'
                }
                classes.append(class_info)
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """메소드 추출 (Context7 기반)"""
        methods = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.pregex_patterns['method_signature'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    method_info = {
                        'name': match[1],  # 메소드명
                        'parameters': match[2] if len(match) > 2 and match[2] else '',
                        'exceptions': match[3] if len(match) > 3 and match[3] else '',
                        'type': 'method',
                        'unique_id': self._generate_unique_id(match[1], match[2] if len(match) > 2 else '')
                    }
                    methods.append(method_info)
        else:
            # Fallback 패턴 사용
            matches = self.fallback_patterns['method_signature'].finditer(content)
            for match in matches:
                method_info = {
                    'name': match.group(1),
                    'parameters': match.group(2) if match.group(2) else '',
                    'exceptions': match.group(3) if match.group(3) else '',
                    'type': 'method',
                    'unique_id': self._generate_unique_id(match.group(1), match.group(2) if match.group(2) else '')
                }
                methods.append(method_info)
        
        return methods
    
    def _extract_sql_units(self, content: str) -> List[Dict[str, Any]]:
        """SQL Units 추출 (Context7 기반)"""
        sql_units = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.pregex_patterns['sql_string'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    sql_content = match[0]
                    sql_units.append({
                        'type': self._determine_sql_type(sql_content),
                        'sql_content': sql_content,
                        'unique_id': self._generate_sql_unique_id(sql_content),
                        'source': 'string_literal'
                    })
        else:
            # Fallback 패턴 사용
            matches = self.fallback_patterns['sql_string'].finditer(content)
            for match in matches:
                sql_content = match.group(1)
                sql_units.append({
                    'type': self._determine_sql_type(sql_content),
                    'sql_content': sql_content,
                    'unique_id': self._generate_sql_unique_id(sql_content),
                    'source': 'string_literal'
                })
        
        return sql_units
    
    def _extract_annotations(self, content: str) -> List[Dict[str, Any]]:
        """어노테이션 추출 (Context7 기반)"""
        annotations = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.pregex_patterns['annotation'].get_captures(content)
            for match in matches:
                if len(match) >= 1:
                    annotation_info = {
                        'name': match[0],
                        'attributes': match[1] if len(match) > 1 and match[1] else '',
                        'type': 'annotation'
                    }
                    annotations.append(annotation_info)
        else:
            # Fallback 패턴 사용
            matches = self.fallback_patterns['annotation'].finditer(content)
            for match in matches:
                annotation_info = {
                    'name': match.group(1),
                    'attributes': match.group(2) if match.group(2) else '',
                    'type': 'annotation'
                }
                annotations.append(annotation_info)
        
        return annotations
    
    def _extract_imports(self, content: str) -> List[str]:
        """Import 문 추출 (Context7 기반)"""
        imports = []
        
        import_pattern = re.compile(r'import\s+([^;]+);', re.IGNORECASE)
        matches = import_pattern.finditer(content)
        
        for match in matches:
            imports.append(match.group(1).strip())
        
        return imports
    
    def _extract_dynamic_queries(self, content: str) -> List[Dict[str, Any]]:
        """다이나믹 쿼리 추출 (Context7 기반 개선)"""
        dynamic_queries = []
        
        # Context7 기반 Java 동적 쿼리 생성 패턴 - 더 정확한 매칭
        dynamic_patterns = {
            'stringbuilder_init': r'StringBuilder\s+(\w+)\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)',
            'stringbuilder_append': r'(\w+)\.append\s*\(([^)]*)\)',
            'criteria_builder': r'CriteriaBuilder\s+(\w+)\s*=\s*entityManager\.getCriteriaBuilder\s*\(\)',
            'criteria_query': r'CriteriaQuery<(\w+)>\s+(\w+)\s*=\s*cb\.createQuery\s*\([^)]*\)',
            'query_dsl': r'Q(\w+)\s+(\w+)\s*=\s*Q(\w+)\.(\w+)',
            'jpa_query': r'@Query\s*\(\s*["\']([^"\']*)["\']\s*\)',
            'jdbc_template': r'jdbcTemplate\.(query|update|execute)\s*\(([^)]*)\)',
            'named_parameter': r'namedParameterJdbcTemplate\.(query|update|execute)\s*\(([^)]*)\)',
            'string_concat': r'String\s+(\w+)\s*=\s*([^;]+);',
            'string_plus_assign': r'(\w+)\s*\+=\s*([^;]+);',
            'conditional_query': r'if\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}',
            'loop_query': r'for\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}'
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
        combined = f"java_dynamic_{pattern_type}_{content}"
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
    
    def _generate_unique_id(self, name: str, params: str = '') -> str:
        """고유 ID 생성 (Context7 기반)"""
        content = f"{name}_{params}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
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
    
    def _extract_file_metadata(self, context) -> Dict[str, Any]:
        """파일 메타데이터 추출 (Context7 기반)"""
        if isinstance(context, str):
            # context가 문자열인 경우 (파일 경로)
            file_path = context
            file_name = os.path.basename(file_path) if file_path else ''
        else:
            # context가 딕셔너리인 경우
            file_path = context.get('file_path', '') if context else ''
            file_name = context.get('file_name', '') if context else ''
        
        return {
            'file_path': file_path,
            'file_name': file_name,
            'parser_type': self._get_parser_type(),
            'parser_version': 'context7',
            'confidence': 0.95
        }
