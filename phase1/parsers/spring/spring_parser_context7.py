"""
Spring Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Spring 파서
- PRegEx를 활용한 정확한 패턴 매칭
- 중복 방지 및 정확도 향상
- 다이나믹 쿼리 파싱 지원
- Spring 어노테이션, 빈 정의, AOP 설정 인식
"""

import re
import hashlib
from typing import Dict, List, Any, Set, Tuple
from phase1.parsers.base_parser import BaseParser

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

class SpringParserContext7(BaseParser):
    """
    Spring Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Spring 파서
    - PRegEx를 활용한 정확한 패턴 매칭
    - 중복 방지 및 정확도 향상
    - 다이나믹 쿼리 파싱 지원
    - Spring 어노테이션, 빈 정의, AOP 설정 인식
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Spring 어노테이션 (Context7 기반)
        self.spring_annotations = {
            '@Component', '@Controller', '@RestController', '@Service', '@Repository',
            '@Autowired', '@Qualifier', '@Value', '@Primary', '@Lazy',
            '@RequestMapping', '@GetMapping', '@PostMapping', '@PutMapping', 
            '@DeleteMapping', '@PatchMapping', '@PathVariable', '@RequestParam',
            '@RequestBody', '@ResponseBody', '@ResponseStatus', '@ExceptionHandler',
            '@Transactional', '@Cacheable', '@CacheEvict', '@CachePut', '@Scheduled',
            '@Async', '@EventListener', '@Order', '@Profile', '@Conditional',
            '@Configuration', '@Bean', '@Import', '@ComponentScan', '@EnableAutoConfiguration',
            '@EnableWebMvc', '@EnableJpaRepositories', '@EnableTransactionManagement',
            '@EnableCaching', '@EnableAsync', '@EnableScheduling', '@EnableAspectJAutoProxy'
        }
        
        # Spring XML 태그 (Context7 기반)
        self.spring_xml_tags = {
            'bean', 'component-scan', 'context:component-scan', 'aop:config',
            'aop:aspect', 'aop:pointcut', 'aop:before', 'aop:after', 'aop:around',
            'tx:advice', 'tx:annotation-driven', 'mvc:annotation-driven',
            'context:property-placeholder', 'context:annotation-config',
            'jdbc:embedded-database', 'jpa:repositories', 'cache:annotation-driven'
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
        
        # Spring 어노테이션 패턴
        spring_annotation = Group(
            '@' + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyFrom('.'))) +  # 어노테이션명
            Optional('(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(' | ')' | '=' | ',' | '{' | '}' | '[' | ']' | '.' | '-' | '_' | ':' | ';' | '\\'))) + ')')  # 어노테이션 속성
        )
        
        # Spring 빈 정의 패턴 (XML)
        spring_bean_xml = Group(
            '<bean' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ';' | ',' | '.' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$' | '\\')) +  # 빈 속성
            Optional(AnyWhitespace()) + '>'
        )
        
        # Spring 컴포넌트 스캔 패턴 (XML)
        component_scan_xml = Group(
            '<' + Optional('context:') + 'component-scan' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ';' | ',' | '.' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$' | '\\')) +  # 스캔 속성
            Optional(AnyWhitespace()) + '>'
        )
        
        # Spring AOP 패턴 (XML)
        spring_aop_xml = Group(
            '<aop:' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '-')) +  # AOP 타입
            Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ';' | ',' | '.' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$' | '\\')) +  # AOP 속성
            Optional(AnyWhitespace()) + '>'
        )
        
        # Spring 메소드 패턴
        spring_method = Group(
            Optional(Either(*self.spring_annotations)) +  # 어노테이션
            Optional(AnyWhitespace()) +
            Optional(Either('public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized')) +  # 접근제어자
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
            '"' + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '\'', '"', '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + '"',
            "'" + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '"', "'", '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + "'"
        )
        
        # Spring 설정 프로퍼티 패턴
        spring_property = Group(
            Capture(OneOrMore(AnyLetter() | AnyDigit() | '.' | '-' | '_')) +  # 프로퍼티 키
            Optional(AnyWhitespace()) + '=' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '.' | '-' | '_' | ':' | '/' | '@' | '#' | '$' | '%' | '&' | '*' | '+' | '=' | '?' | '^' | '`' | '|' | '~' | '[' | ']' | '{' | '}' | '(' | ')' | '<' | '>' | ';' | ',' | '!' | '"' | "'"))  # 프로퍼티 값
        )
        
        # 패턴 저장
        self.pregex_patterns = {
            'spring_annotation': spring_annotation,
            'spring_bean_xml': spring_bean_xml,
            'component_scan_xml': component_scan_xml,
            'spring_aop_xml': spring_aop_xml,
            'spring_method': spring_method,
            'sql_string': sql_string,
            'spring_property': spring_property
        }
    
    def _build_fallback_patterns(self):
        """PRegEx가 없을 때 사용할 fallback 패턴 (Context7 기반)"""
        
        self.fallback_patterns = {
            'spring_annotation': re.compile(
                r'@(\w+(?:\.\w+)*)(?:\(([^)]*)\))?',
                re.IGNORECASE
            ),
            'spring_bean_xml': re.compile(
                r'<bean\s+([^>]*?)>',
                re.IGNORECASE | re.DOTALL
            ),
            'component_scan_xml': re.compile(
                r'<(?:context:)?component-scan\s+([^>]*?)>',
                re.IGNORECASE | re.DOTALL
            ),
            'spring_aop_xml': re.compile(
                r'<aop:(\w+)\s+([^>]*?)>',
                re.IGNORECASE | re.DOTALL
            ),
            'spring_method': re.compile(
                r'(?:@\w+(?:\([^)]*\))?\s*)*'  # 어노테이션
                r'(?:public|private|protected|static|final|abstract|synchronized\s+)*'  # 접근제어자
                r'(?:[\w<>\[\],\s?&\.]+\s+)?'  # 반환타입
                r'(\w+)\s*'  # 메소드명 (캡처)
                r'\(([^)]*)\)'  # 파라미터 (캡처)
                r'(?:\s+throws\s+([\w\s,\.]+))?',  # 예외 (캡처)
                re.IGNORECASE | re.MULTILINE
            ),
            'sql_string': re.compile(
                r'["\']([^"\']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
                re.IGNORECASE
            ),
            'spring_property': re.compile(
                r'(\w+(?:\.\w+)*)\s*=\s*(.+)',
                re.IGNORECASE
            )
        }
    
    def _get_parser_type(self) -> str:
        return 'spring_context7'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spring 파일을 파싱하여 메타데이터 추출 (Context7 기반)
        
        Args:
            content: Spring 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 정규화
        normalized_content = self._normalize_content(content)
        
        result = {
            'spring_annotations': self._extract_spring_annotations(normalized_content),
            'spring_beans': self._extract_spring_beans(normalized_content),
            'component_scans': self._extract_component_scans(normalized_content),
            'aop_configurations': self._extract_aop_configurations(normalized_content),
            'spring_methods': self._extract_spring_methods(normalized_content),
            'sql_units': self._extract_sql_units(normalized_content),
            'spring_properties': self._extract_spring_properties(normalized_content),
            'dynamic_queries': self._extract_dynamic_queries(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': 0.95  # Context7 기반으로 높은 신뢰도
        }
        
        return result
    
    def _extract_spring_annotations(self, content: str) -> List[Dict[str, Any]]:
        """Spring 어노테이션 추출 (Context7 기반)"""
        annotations = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['spring_annotation'].get_captures(content)
            for match in matches:
                if len(match) >= 1:
                    annotation_info = {
                        'name': match[0],
                        'attributes': match[1] if len(match) > 1 and match[1] else '',
                        'type': 'spring_annotation',
                        'unique_id': self._generate_unique_id('annotation', match[0])
                    }
                    annotations.append(annotation_info)
        else:
            matches = self.fallback_patterns['spring_annotation'].finditer(content)
            for match in matches:
                annotation_info = {
                    'name': match.group(1),
                    'attributes': match.group(2) if match.group(2) else '',
                    'type': 'spring_annotation',
                    'unique_id': self._generate_unique_id('annotation', match.group(1))
                }
                annotations.append(annotation_info)
        
        return annotations
    
    def _extract_spring_beans(self, content: str) -> List[Dict[str, Any]]:
        """Spring 빈 정의 추출 (Context7 기반)"""
        beans = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['spring_bean_xml'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    bean_info = {
                        'attributes': match[0],
                        'type': 'spring_bean',
                        'unique_id': self._generate_unique_id('bean', match[0])
                    }
                    beans.append(bean_info)
        else:
            matches = self.fallback_patterns['spring_bean_xml'].finditer(content)
            for match in matches:
                bean_info = {
                    'attributes': match.group(1),
                    'type': 'spring_bean',
                    'unique_id': self._generate_unique_id('bean', match.group(1))
                }
                beans.append(bean_info)
        
        return beans
    
    def _extract_component_scans(self, content: str) -> List[Dict[str, Any]]:
        """컴포넌트 스캔 설정 추출 (Context7 기반)"""
        scans = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['component_scan_xml'].get_captures(content)
            for match in matches:
                if len(match) >= 1 and match[0]:
                    scan_info = {
                        'attributes': match[0],
                        'type': 'component_scan',
                        'unique_id': self._generate_unique_id('scan', match[0])
                    }
                    scans.append(scan_info)
        else:
            matches = self.fallback_patterns['component_scan_xml'].finditer(content)
            for match in matches:
                scan_info = {
                    'attributes': match.group(1),
                    'type': 'component_scan',
                    'unique_id': self._generate_unique_id('scan', match.group(1))
                }
                scans.append(scan_info)
        
        return scans
    
    def _extract_aop_configurations(self, content: str) -> List[Dict[str, Any]]:
        """AOP 설정 추출 (Context7 기반)"""
        aop_configs = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['spring_aop_xml'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    aop_info = {
                        'aop_type': match[0],
                        'attributes': match[1],
                        'type': 'aop_configuration',
                        'unique_id': self._generate_unique_id('aop', match[0])
                    }
                    aop_configs.append(aop_info)
        else:
            matches = self.fallback_patterns['spring_aop_xml'].finditer(content)
            for match in matches:
                aop_info = {
                    'aop_type': match.group(1),
                    'attributes': match.group(2),
                    'type': 'aop_configuration',
                    'unique_id': self._generate_unique_id('aop', match.group(1))
                }
                aop_configs.append(aop_info)
        
        return aop_configs
    
    def _extract_spring_methods(self, content: str) -> List[Dict[str, Any]]:
        """Spring 메소드 추출 (Context7 기반)"""
        methods = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['spring_method'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    method_info = {
                        'return_type': match[0],
                        'name': match[1],
                        'parameters': match[2] if len(match) > 2 and match[2] else '',
                        'exceptions': match[3] if len(match) > 3 and match[3] else '',
                        'type': 'spring_method',
                        'unique_id': self._generate_unique_id('method', match[1])
                    }
                    methods.append(method_info)
        else:
            matches = self.fallback_patterns['spring_method'].finditer(content)
            for match in matches:
                method_info = {
                    'name': match.group(1),
                    'parameters': match.group(2) if match.group(2) else '',
                    'exceptions': match.group(3) if match.group(3) else '',
                    'type': 'spring_method',
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
                        'source': 'spring_string_literal'
                    })
        else:
            matches = self.fallback_patterns['sql_string'].finditer(content)
            for match in matches:
                sql_content = match.group(1)
                sql_units.append({
                    'type': self._determine_sql_type(sql_content),
                    'sql_content': sql_content,
                    'unique_id': self._generate_sql_unique_id(sql_content),
                    'source': 'spring_string_literal'
                })
        
        return sql_units
    
    def _extract_spring_properties(self, content: str) -> List[Dict[str, Any]]:
        """Spring 프로퍼티 추출 (Context7 기반)"""
        properties = []
        
        if PREGEX_AVAILABLE:
            matches = self.pregex_patterns['spring_property'].get_captures(content)
            for match in matches:
                if len(match) >= 2:
                    property_info = {
                        'key': match[0],
                        'value': match[1],
                        'type': 'spring_property',
                        'unique_id': self._generate_unique_id('property', match[0])
                    }
                    properties.append(property_info)
        else:
            matches = self.fallback_patterns['spring_property'].finditer(content)
            for match in matches:
                property_info = {
                    'key': match.group(1),
                    'value': match.group(2),
                    'type': 'spring_property',
                    'unique_id': self._generate_unique_id('property', match.group(1))
                }
                properties.append(property_info)
        
        return properties
    
    def _extract_dynamic_queries(self, content: str) -> List[Dict[str, Any]]:
        """다이나믹 쿼리 추출 (Context7 기반 개선)"""
        dynamic_queries = []
        
        # Context7 기반 Spring 동적 쿼리 생성 패턴 - 더 정확한 매칭
        dynamic_patterns = {
            'query_annotation': r'@Query\s*\(\s*["\']([^"\']*)["\']\s*\)',
            'jdbc_template_query': r'jdbcTemplate\.(query|queryForObject|queryForList|update|execute)\s*\(([^)]*)\)',
            'named_parameter_query': r'namedParameterJdbcTemplate\.(query|queryForObject|queryForList|update|execute)\s*\(([^)]*)\)',
            'simple_jdbc_query': r'simpleJdbcTemplate\.(query|queryForObject|queryForList|update|execute)\s*\(([^)]*)\)',
            'stringbuilder_init': r'StringBuilder\s+(\w+)\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)',
            'stringbuilder_append': r'(\w+)\.append\s*\(([^)]*)\)',
            'string_concat': r'String\s+(\w+)\s*=\s*([^;]+);',
            'string_plus_assign': r'(\w+)\s*\+=\s*([^;]+);',
            'conditional_query': r'if\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}',
            'loop_query': r'for\s*\([^)]+\)\s*\{\s*([^}]*String[^}]*)\}',
            'spring_data_query': r'@Query\s*\(\s*value\s*=\s*["\']([^"\']*)["\']\s*,\s*nativeQuery\s*=\s*(true|false)\s*\)',
            'spel_query': r'@Query\s*\(\s*["\']([^"\']*#\{[^}]*\}[^"\']*)["\']\s*\)'
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
        combined = f"spring_dynamic_{pattern_type}_{content}"
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
        # XML 주석 제거
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
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
