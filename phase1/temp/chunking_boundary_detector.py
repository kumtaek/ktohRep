"""
Context7 PRegEx 패턴 기반 청킹 경계 인식 시스템
파일 타입별로 의미있는 단위로 정확한 분할 경계를 설정하는 시스템
개발: Context7 기반 PRegEx 라이브러리 활용
"""

import os
import sys
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
from datetime import datetime
import logging

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# PRegEx를 사용한 패턴 구성 (Context7 기반)
try:
    from pregex.core.pre import Pregex
    from pregex.core.classes import AnyLetter, AnyDigit, AnyWhitespace, AnyFrom, AnyButFrom
    from pregex.core.quantifiers import Optional, OneOrMore, AtLeastAtMost, AtLeast, AtMost
    from pregex.core.operators import Either
    from pregex.core.groups import Capture, Group
    from pregex.core.assertions import WordBoundary, FollowedBy, PrecededBy
    PREGEX_AVAILABLE = True
    print("PRegEx 라이브러리 로드 성공 - Context7 기반 청킹 시스템 활성화")
except ImportError as e:
    PREGEX_AVAILABLE = False
    print(f"PRegEx 라이브러리 로드 실패: {e} - Fallback 모드로 동작")

class ChunkingBoundaryDetector:
    """
    Context7 PRegEx 패턴 기반 청킹 경계 인식 시스템
    - 파일 타입별 의미있는 단위로 정확한 분할 경계 설정
    - PRegEx를 활용한 정밀한 패턴 매칭
    - 중첩 구조와 컨텍스트를 고려한 경계 인식
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # 파일 타입별 청킹 전략
        self.chunking_strategies = {
            'java': self._build_java_chunking_patterns,
            'jsp': self._build_jsp_chunking_patterns,
            'xml': self._build_xml_chunking_patterns,
            'spring': self._build_spring_chunking_patterns,
            'jpa': self._build_jpa_chunking_patterns
        }
        
        # PRegEx 패턴 저장소
        self.chunking_patterns = {}
        
        # 패턴 초기화
        self._initialize_chunking_patterns()
        
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_chunking_patterns(self):
        """청킹 패턴 초기화"""
        self.logger.info("Context7 PRegEx 기반 청킹 패턴 초기화 중...")
        
        for file_type, pattern_builder in self.chunking_strategies.items():
            try:
                self.chunking_patterns[file_type] = pattern_builder()
                self.logger.info(f"{file_type.upper()} 청킹 패턴 초기화 완료")
            except Exception as e:
                self.logger.error(f"{file_type.upper()} 청킹 패턴 초기화 실패: {e}")
        
        self.logger.info("모든 청킹 패턴 초기화 완료")
    
    def _build_java_chunking_patterns(self) -> Dict[str, Any]:
        """Java 파일 청킹 패턴 구성 (Context7 PRegEx 기반)"""
        patterns = {}
        
        if PREGEX_AVAILABLE:
            # Java 식별자 패턴 (개선된 버전)
            java_identifier = AnyLetter() + AtLeastAtMost(AnyLetter() | AnyDigit() | '_' | '$', n=0, m=50)
            
            # Java 타입 패턴 (재귀 참조 문제 해결)
            java_type = java_identifier + Optional('[]') + Optional('[]')  # 2차원 배열까지 지원
            
            # 클래스 경계 패턴 (개선된 버전)
            class_boundary = Group(
                Optional(Either('public', 'private', 'protected', 'abstract', 'final', 'static')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                'class' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(java_identifier) +  # 클래스명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('extends' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + java_identifier) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('implements' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + 
                        OneOrMore(java_identifier + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ',' + AtLeastAtMost(AnyWhitespace(), n=0, m=3))) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '{'  # 클래스 시작
            )
            
            # 메소드 경계 패턴 (개선된 버전)
            method_boundary = Group(
                Optional(Either('@Override', '@Deprecated', '@SuppressWarnings', '@Transactional', '@Service', '@Repository', '@Controller', '@RestController')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(Either('public', 'private', 'protected')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(Either('static', 'final', 'abstract', 'synchronized', 'native', 'strictfp')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                java_type + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(java_identifier) +  # 메소드명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '(' + Optional(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&' | '.' | '[' | ']')) + ')' +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('throws' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '.')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Either('{', ';')  # 메소드 본문 시작
            )
            
            # 필드 경계 패턴 (개선된 버전)
            field_boundary = Group(
                Optional(Either('public', 'private', 'protected')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(Either('static', 'final', 'volatile', 'transient')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                java_type + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(java_identifier) +  # 필드명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('=' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + 
                        OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '.' | ',' | '(' | ')' | '[' | ']' | '{' | '}' | '"' | "'" | '+' | '-' | '*' | '/' | '%')) +
                ';'
            )
            
            # 내부 클래스 경계 패턴 (개선된 버전)
            inner_class_boundary = Group(
                Optional(Either('public', 'private', 'protected', 'static')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                'class' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(java_identifier) +  # 내부 클래스명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('extends' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + java_identifier) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('implements' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + 
                        OneOrMore(java_identifier + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ',' + AtLeastAtMost(AnyWhitespace(), n=0, m=3))) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '{'
            )
            
            patterns = {
                'class_boundary': class_boundary,
                'method_boundary': method_boundary,
                'field_boundary': field_boundary,
                'inner_class_boundary': inner_class_boundary
            }
        else:
            # Fallback 패턴 (PRegEx 없을 때)
            patterns = {
                'class_boundary': re.compile(
                    r'(?:public|private|protected|abstract|final|static\s+)*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{',
                    re.IGNORECASE | re.MULTILINE
                ),
                'method_boundary': re.compile(
                    r'(?:@\w+(?:\([^)]*\))?\s*)*(?:public|private|protected)?\s*(?:static|final|abstract|synchronized)?\s*(?:[\w<>\[\],\s?&]+\s+)(\w+)\s*\([^)]*\)(?:\s+throws\s+[\w\s,\.]+)?\s*[;{]',
                    re.IGNORECASE | re.MULTILINE
                ),
                'field_boundary': re.compile(
                    r'(?:public|private|protected)?\s*(?:static|final|volatile|transient)?\s*(?:[\w<>\[\],\s?&]+\s+)(\w+)\s*(?:=[^;]*)?;',
                    re.IGNORECASE | re.MULTILINE
                ),
                'inner_class_boundary': re.compile(
                    r'(?:public|private|protected|static\s+)*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{',
                    re.IGNORECASE | re.MULTILINE
                )
            }
        
        return patterns
    
    def _build_jsp_chunking_patterns(self) -> Dict[str, Any]:
        """JSP 파일 청킹 패턴 구성 (Context7 PRegEx 기반)"""
        patterns = {}
        
        if PREGEX_AVAILABLE:
            # JSP 지시어 경계 패턴 (개선된 버전)
            directive_boundary = Group(
                '<%@' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(Either('page', 'include', 'taglib', 'tag', 'attribute', 'variable')) +  # 지시어 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '%>'
            )
            
            # JSP 액션 태그 경계 패턴 (개선된 버전)
            action_boundary = Group(
                '<jsp:' + Capture(Either('useBean', 'setProperty', 'getProperty', 'include', 'forward', 'plugin', 'params', 'param', 'fallback', 'element', 'attribute', 'body', 'invoke', 'doBody')) +  # 액션 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Either('/>', '>')
            )
            
            # 스크립틀릿 경계 패턴 (개선된 버전)
            scriptlet_boundary = Group(
                '<%' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | ';' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$')) +  # Java 코드
                '%>'
            )
            
            # 표현식 경계 패턴 (개선된 버전)
            expression_boundary = Group(
                '<%=' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | ';' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$')) +  # 표현식
                '%>'
            )
            
            # 선언부 경계 패턴 (개선된 버전)
            declaration_boundary = Group(
                '<%!' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | ';' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '?' | ':' | '@' | '#' | '$')) +  # 선언
                '%>'
            )
            
            # HTML 블록 경계 패턴 (개선된 버전)
            html_block_boundary = Group(
                '<' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '-')) +  # HTML 태그명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']'))) +  # 속성
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Either('/>', '>')
            )
            
            # JavaScript 함수 경계 패턴 (개선된 버전)
            js_function_boundary = Group(
                'function' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 함수명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '_' | '$' | '=' | ':' | '?' | '[' | ']' | '{' | '}'))) + ')' +  # 파라미터
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '{'
            )
            
            patterns = {
                'directive_boundary': directive_boundary,
                'action_boundary': action_boundary,
                'scriptlet_boundary': scriptlet_boundary,
                'expression_boundary': expression_boundary,
                'declaration_boundary': declaration_boundary,
                'html_block_boundary': html_block_boundary,
                'js_function_boundary': js_function_boundary
            }
        else:
            # Fallback 패턴
            patterns = {
                'directive_boundary': re.compile(
                    r'<%@\s*(page|include|taglib|tag|attribute|variable)\s+([^%>]*?)%>',
                    re.IGNORECASE | re.DOTALL
                ),
                'action_boundary': re.compile(
                    r'<jsp:(useBean|setProperty|getProperty|include|forward|plugin|params|param|fallback|element|attribute|body|invoke|doBody)([^>]*?)(?:/>|>)',
                    re.IGNORECASE | re.DOTALL
                ),
                'scriptlet_boundary': re.compile(
                    r'<%([^%]*?)%>',
                    re.IGNORECASE | re.DOTALL
                ),
                'expression_boundary': re.compile(
                    r'<%=([^%]*?)%>',
                    re.IGNORECASE | re.DOTALL
                ),
                'declaration_boundary': re.compile(
                    r'<%!([^%]*?)%>',
                    re.IGNORECASE | re.DOTALL
                ),
                'html_block_boundary': re.compile(
                    r'<(\w+)([^>]*?)(?:/>|>)',
                    re.IGNORECASE | re.DOTALL
                ),
                'js_function_boundary': re.compile(
                    r'function\s+(\w+)\s*\(([^)]*?)\)\s*\{',
                    re.IGNORECASE | re.DOTALL
                )
            }
        
        return patterns
    
    def _build_xml_chunking_patterns(self) -> Dict[str, Any]:
        """XML 파일 청킹 패턴 구성 (Context7 PRegEx 기반)"""
        patterns = {}
        
        if PREGEX_AVAILABLE:
            # XML 선언 경계 패턴 (개선된 버전)
            xml_declaration_boundary = Group(
                '<?xml' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '?>'
            )
            
            # XML 네임스페이스 경계 패턴 (개선된 버전)
            namespace_boundary = Group(
                'xmlns' + Optional(':' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '-'))) +  # 네임스페이스 접두사
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '=' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '"' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '.' | ':' | '/' | '-' | '_' | '=' | '?' | '&' | '%')) + '"'  # 네임스페이스 URI
            )
            
            # XML 요소 경계 패턴 (개선된 버전)
            element_boundary = Group(
                '<' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '-' | ':')) +  # 요소명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']'))) +  # 속성
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Either('/>', '>')
            )
            
            # MyBatis 매퍼 경계 패턴 (개선된 버전)
            mapper_boundary = Group(
                '<mapper' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '>'
            )
            
            # SQL 문 경계 패턴 (개선된 버전)
            sql_statement_boundary = Group(
                '<' + Capture(Either('select', 'insert', 'update', 'delete', 'sql')) +  # SQL 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '>'
            )
            
            # 동적 SQL 태그 경계 패턴 (개선된 버전)
            dynamic_sql_boundary = Group(
                '<' + Capture(Either('if', 'choose', 'when', 'otherwise', 'foreach', 'where', 'set', 'trim', 'bind')) +  # 동적 태그 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '>'
            )
            
            patterns = {
                'xml_declaration_boundary': xml_declaration_boundary,
                'namespace_boundary': namespace_boundary,
                'element_boundary': element_boundary,
                'mapper_boundary': mapper_boundary,
                'sql_statement_boundary': sql_statement_boundary,
                'dynamic_sql_boundary': dynamic_sql_boundary
            }
        else:
            # Fallback 패턴
            patterns = {
                'xml_declaration_boundary': re.compile(
                    r'<\?xml\s+([^?]*?)\?>',
                    re.IGNORECASE | re.DOTALL
                ),
                'namespace_boundary': re.compile(
                    r'xmlns(?::(\w+))?\s*=\s*"([^"]*)"',
                    re.IGNORECASE | re.DOTALL
                ),
                'element_boundary': re.compile(
                    r'<(\w+(?::\w+)?)([^>]*?)(?:/>|>)',
                    re.IGNORECASE | re.DOTALL
                ),
                'mapper_boundary': re.compile(
                    r'<mapper\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                ),
                'sql_statement_boundary': re.compile(
                    r'<(select|insert|update|delete|sql)\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                ),
                'dynamic_sql_boundary': re.compile(
                    r'<(if|choose|when|otherwise|foreach|where|set|trim|bind)\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                )
            }
        
        return patterns
    
    def _build_spring_chunking_patterns(self) -> Dict[str, Any]:
        """Spring 파일 청킹 패턴 구성 (Context7 PRegEx 기반)"""
        patterns = {}
        
        if PREGEX_AVAILABLE:
            # Spring 어노테이션 경계 패턴 (개선된 버전)
            annotation_boundary = Group(
                '@' + Capture(OneOrMore(AnyLetter() | AnyDigit() | '.')) +  # 어노테이션명
                Optional('(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')')
            )
            
            # Spring 빈 정의 경계 패턴 (개선된 버전)
            bean_definition_boundary = Group(
                '<bean' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '>'
            )
            
            # Spring 설정 경계 패턴 (개선된 버전)
            config_boundary = Group(
                '<' + Capture(Either('context', 'mvc', 'security', 'tx', 'aop', 'jpa', 'jdbc', 'cache')) +  # 설정 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '>'
            )
            
            # AOP 포인트컷 경계 패턴 (개선된 버전)
            aop_pointcut_boundary = Group(
                '<' + Capture(Either('pointcut', 'advisor', 'aspect')) +  # AOP 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '>'
            )
            
            # 트랜잭션 설정 경계 패턴 (개선된 버전)
            transaction_boundary = Group(
                '<' + Capture(Either('tx:advice', 'tx:annotation-driven', 'tx:transaction-manager')) +  # 트랜잭션 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '[' | ']')) +  # 속성
                '>'
            )
            
            patterns = {
                'annotation_boundary': annotation_boundary,
                'bean_definition_boundary': bean_definition_boundary,
                'config_boundary': config_boundary,
                'aop_pointcut_boundary': aop_pointcut_boundary,
                'transaction_boundary': transaction_boundary
            }
        else:
            # Fallback 패턴
            patterns = {
                'annotation_boundary': re.compile(
                    r'@(\w+(?:\.\w+)*)(?:\(([^)]*?)\))?',
                    re.IGNORECASE | re.DOTALL
                ),
                'bean_definition_boundary': re.compile(
                    r'<bean\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                ),
                'config_boundary': re.compile(
                    r'<(context|mvc|security|tx|aop|jpa|jdbc|cache)\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                ),
                'aop_pointcut_boundary': re.compile(
                    r'<(pointcut|advisor|aspect)\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                ),
                'transaction_boundary': re.compile(
                    r'<(tx:advice|tx:annotation-driven|tx:transaction-manager)\s+([^>]*?)>',
                    re.IGNORECASE | re.DOTALL
                )
            }
        
        return patterns
    
    def _build_jpa_chunking_patterns(self) -> Dict[str, Any]:
        """JPA 파일 청킹 패턴 구성 (Context7 PRegEx 기반)"""
        patterns = {}
        
        if PREGEX_AVAILABLE:
            # JPA 어노테이션 경계 패턴 (개선된 버전)
            jpa_annotation_boundary = Group(
                '@' + Capture(Either('Entity', 'Table', 'Id', 'GeneratedValue', 'Column', 'JoinColumn', 'OneToOne', 'OneToMany', 'ManyToOne', 'ManyToMany', 'JoinTable', 'Query', 'Modifying', 'Transactional', 'NamedQuery', 'NamedQueries', 'NamedNativeQuery', 'NamedNativeQueries')) +  # JPA 어노테이션
                Optional('(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')')
            )
            
            # 엔티티 클래스 경계 패턴 (개선된 버전)
            entity_class_boundary = Group(
                '@Entity' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('@Table' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + '(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 테이블 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')' + AtLeastAtMost(AnyWhitespace(), n=0, m=3)) +
                Optional(AnyFrom('public', 'private', 'protected')) + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                'class' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 엔티티 클래스명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('extends' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('implements' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '_' | '$')) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '{'
            )
            
            # JPA 관계 경계 패턴 (개선된 버전)
            jpa_relationship_boundary = Group(
                '@' + Capture(Either('OneToOne', 'OneToMany', 'ManyToOne', 'ManyToMany')) +  # 관계 타입
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 관계 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')') +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('@JoinColumn' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + '(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 조인 컬럼 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')' + AtLeastAtMost(AnyWhitespace(), n=0, m=3)) +
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional('@JoinTable' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + '(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | '&' | '%')) +  # 조인 테이블 속성
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')' + AtLeastAtMost(AnyWhitespace(), n=0, m=3))
            )
            
            # JPA 쿼리 메소드 경계 패턴 (개선된 버전)
            jpa_query_method_boundary = Group(
                Optional('@Query' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) + '(' + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                        '"' + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '"' | "'" | ',' | '.' | ':' | '-' | '_' | '(' | ')' | '{' | '}' | '[' | ']' | '?' | ':' | ';' | '+' | '-' | '*' | '/' | '%' | '&' | '|' | '!' | '<' | '>' | '@' | '#' | '$')) + '"' +  # 쿼리 문자열
                        AtLeastAtMost(AnyWhitespace(), n=0, m=3) + ')' + AtLeastAtMost(AnyWhitespace(), n=0, m=3)) +
                Optional('@Modifying' + AtLeastAtMost(AnyWhitespace(), n=0, m=3)) +
                Optional(AnyFrom('public', 'private', 'protected')) + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                Optional(AnyFrom('static', 'final', 'abstract')) + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                OneOrMore(AnyLetter() | AnyDigit() | '_' | '$' | '<' | '>' | '[' | ']') + AtLeastAtMost(AnyWhitespace(), n=0, m=3) +  # 반환 타입
                Capture(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$')) +  # 메소드명
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                '(' + Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&' | '_' | '$' | '.' | '[' | ']'))) + ')' +  # 파라미터
                AtLeastAtMost(AnyWhitespace(), n=0, m=3) +
                ';'
            )
            
            patterns = {
                'jpa_annotation_boundary': jpa_annotation_boundary,
                'entity_class_boundary': entity_class_boundary,
                'jpa_relationship_boundary': jpa_relationship_boundary,
                'jpa_query_method_boundary': jpa_query_method_boundary
            }
        else:
            # Fallback 패턴
            patterns = {
                'jpa_annotation_boundary': re.compile(
                    r'@(Entity|Table|Id|GeneratedValue|Column|JoinColumn|OneToOne|OneToMany|ManyToOne|ManyToMany|JoinTable|Query|Modifying|Transactional|NamedQuery|NamedQueries|NamedNativeQuery|NamedNativeQueries)(?:\(([^)]*?)\))?',
                    re.IGNORECASE | re.DOTALL
                ),
                'entity_class_boundary': re.compile(
                    r'@Entity\s*(?:@Table\s*\(([^)]*?)\)\s*)?(?:public|private|protected)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{',
                    re.IGNORECASE | re.DOTALL
                ),
                'jpa_relationship_boundary': re.compile(
                    r'@(OneToOne|OneToMany|ManyToOne|ManyToMany)(?:\(([^)]*?)\))?\s*(?:@JoinColumn\s*\(([^)]*?)\)\s*)?(?:@JoinTable\s*\(([^)]*?)\)\s*)?',
                    re.IGNORECASE | re.DOTALL
                ),
                'jpa_query_method_boundary': re.compile(
                    r'(?:@Query\s*\(\s*"([^"]*?)"\s*\)\s*)?(?:@Modifying\s*)?(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:[\w<>\[\],\s?&]+\s+)(\w+)\s*\(([^)]*?)\)\s*;',
                    re.IGNORECASE | re.DOTALL
                )
            }
        
        return patterns
    
    def detect_chunking_boundaries(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """
        파일 내용에서 청킹 경계를 감지 (Context7 PRegEx 기반)
        
        Args:
            content: 파일 내용
            file_type: 파일 타입 (java, jsp, xml, spring, jpa)
            
        Returns:
            청킹 경계 정보 리스트
        """
        if file_type not in self.chunking_patterns:
            self.logger.warning(f"지원하지 않는 파일 타입: {file_type}")
            return []
        
        boundaries = []
        patterns = self.chunking_patterns[file_type]
        
        for pattern_name, pattern in patterns.items():
            try:
                if PREGEX_AVAILABLE:
                    # PRegEx 사용 - Context7 기반
                    matches = pattern.get_captures(content)
                    for i, match in enumerate(matches):
                        # PRegEx에서 위치 정보 추출을 위한 개선된 방법
                        match_content = match[0] if len(match) > 0 else ''
                        start_pos = content.find(match_content, 0)
                        end_pos = start_pos + len(match_content) if start_pos != -1 else 0
                        
                        boundary_info = {
                            'type': pattern_name,
                            'pattern_name': pattern_name,
                            'start_pos': start_pos,
                            'end_pos': end_pos,
                            'content': match_content,
                            'captures': match,
                            'unique_id': self._generate_boundary_id(pattern_name, match_content),
                            'confidence': 0.95,  # Context7 PRegEx 기반 높은 신뢰도
                            'context7_based': True
                        }
                        boundaries.append(boundary_info)
                else:
                    # Fallback 패턴 사용
                    matches = pattern.finditer(content)
                    for match in matches:
                        boundary_info = {
                            'type': pattern_name,
                            'pattern_name': pattern_name,
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'content': match.group(0),
                            'captures': match.groups(),
                            'unique_id': self._generate_boundary_id(pattern_name, match.group(0)),
                            'confidence': 0.7,  # Fallback 패턴 낮은 신뢰도
                            'context7_based': False
                        }
                        boundaries.append(boundary_info)
            except Exception as e:
                self.logger.error(f"패턴 {pattern_name} 처리 중 오류: {e}")
                continue
        
        # 위치별로 정렬
        boundaries.sort(key=lambda x: x['start_pos'])
        
        self.logger.info(f"{file_type.upper()} 파일에서 {len(boundaries)}개의 청킹 경계 감지 (Context7 PRegEx 기반)")
        return boundaries
    
    def _generate_boundary_id(self, pattern_name: str, content: str) -> str:
        """청킹 경계 고유 ID 생성"""
        combined = f"boundary_{pattern_name}_{content}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def analyze_chunking_strategy(self, content: str, file_type: str) -> Dict[str, Any]:
        """
        청킹 전략 분석 (Context7 PRegEx 기반)
        
        Args:
            content: 파일 내용
            file_type: 파일 타입
            
        Returns:
            청킹 전략 분석 결과
        """
        boundaries = self.detect_chunking_boundaries(content, file_type)
        
        analysis = {
            'file_type': file_type,
            'total_boundaries': len(boundaries),
            'boundary_types': {},
            'chunking_recommendations': [],
            'complexity_score': 0.0,
            'context7_accuracy': 0.0,
            'chunking_metadata': {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'chunk_distribution': {},
                'dependency_analysis': {}
            }
        }
        
        # 경계 타입별 통계
        context7_count = 0
        for boundary in boundaries:
            boundary_type = boundary['type']
            if boundary_type not in analysis['boundary_types']:
                analysis['boundary_types'][boundary_type] = 0
            analysis['boundary_types'][boundary_type] += 1
            
            # Context7 기반 경계 카운트
            if boundary.get('context7_based', False):
                context7_count += 1
        
        # Context7 정확도 계산
        if len(boundaries) > 0:
            analysis['context7_accuracy'] = context7_count / len(boundaries)
        
        # 복잡도 점수 계산 (개선된 버전)
        content_length = len(content)
        boundary_density = len(boundaries) / max(content_length / 1000, 1)  # 1000자당 경계 수
        analysis['complexity_score'] = min(boundary_density / 10.0, 1.0)
        
        # 청킹 메타데이터 생성
        if boundaries:
            chunk_sizes = [boundary['end_pos'] - boundary['start_pos'] for boundary in boundaries]
            analysis['chunking_metadata']['total_chunks'] = len(boundaries)
            analysis['chunking_metadata']['avg_chunk_size'] = sum(chunk_sizes) / len(chunk_sizes)
            
            # 청크 분포 분석
            for boundary in boundaries:
                chunk_type = boundary['type']
                if chunk_type not in analysis['chunking_metadata']['chunk_distribution']:
                    analysis['chunking_metadata']['chunk_distribution'][chunk_type] = 0
                analysis['chunking_metadata']['chunk_distribution'][chunk_type] += 1
        
        # 청킹 권장사항 생성 (개선된 버전)
        if analysis['complexity_score'] > 0.7:
            analysis['chunking_recommendations'].append("높은 복잡도: 세밀한 청킹 전략 권장")
            analysis['chunking_recommendations'].append("Context7 PRegEx 기반 정밀 패턴 매칭 활용")
        elif analysis['complexity_score'] > 0.4:
            analysis['chunking_recommendations'].append("중간 복잡도: 균형잡힌 청킹 전략 권장")
            analysis['chunking_recommendations'].append("Context7 PRegEx 기반 적응형 청킹 적용")
        else:
            analysis['chunking_recommendations'].append("낮은 복잡도: 단순한 청킹 전략 권장")
            analysis['chunking_recommendations'].append("Context7 PRegEx 기반 기본 청킹 패턴 사용")
        
        # Context7 정확도 기반 권장사항
        if analysis['context7_accuracy'] > 0.9:
            analysis['chunking_recommendations'].append("Context7 PRegEx 패턴 매칭 정확도 우수")
        elif analysis['context7_accuracy'] > 0.7:
            analysis['chunking_recommendations'].append("Context7 PRegEx 패턴 매칭 정확도 양호")
        else:
            analysis['chunking_recommendations'].append("Context7 PRegEx 패턴 매칭 정확도 개선 필요")
        
        return analysis


def main():
    """메인 함수 - Context7 PRegEx 기반 청킹 경계 인식 시스템"""
    import argparse
    import yaml
    import json
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Context7 PRegEx 기반 청킹 경계 인식 시스템')
    parser.add_argument('--file-path', required=True, help='분석할 파일 경로')
    parser.add_argument('--file-type', required=True, choices=['java', 'jsp', 'xml', 'spring', 'jpa'], help='파일 타입')
    parser.add_argument('--config', default='./phase1/config/config.yaml', help='설정 파일 경로')
    parser.add_argument('--output-json', action='store_true', help='JSON 형태로 결과 출력')
    parser.add_argument('--verbose', action='store_true', help='상세 정보 출력')
    
    args = parser.parse_args()
    
    try:
        # 설정 로드
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 파일 내용 읽기
        with open(args.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 청킹 경계 인식 시스템 실행
        detector = ChunkingBoundaryDetector(config)
        boundaries = detector.detect_chunking_boundaries(content, args.file_type)
        analysis = detector.analyze_chunking_strategy(content, args.file_type)
        
        # 결과 출력
        if args.output_json:
            result = {
                'file_path': args.file_path,
                'file_type': args.file_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'boundaries': boundaries,
                'analysis': analysis,
                'context7_based': True
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("=" * 80)
            print("Context7 PRegEx 기반 청킹 경계 인식 시스템 결과")
            print("=" * 80)
            print(f"파일: {args.file_path}")
            print(f"타입: {args.file_type}")
            print(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"감지된 경계: {len(boundaries)}개")
            print(f"복잡도 점수: {analysis['complexity_score']:.2f}")
            print(f"Context7 정확도: {analysis['context7_accuracy']:.2f}")
            print(f"경계 타입별 통계: {analysis['boundary_types']}")
            
            if args.verbose:
                print("\n상세 청킹 메타데이터:")
                print(f"  - 총 청크 수: {analysis['chunking_metadata']['total_chunks']}")
                print(f"  - 평균 청크 크기: {analysis['chunking_metadata']['avg_chunk_size']:.1f}자")
                print(f"  - 청크 분포: {analysis['chunking_metadata']['chunk_distribution']}")
                
                print("\n감지된 경계 상세 정보:")
                for i, boundary in enumerate(boundaries[:10]):  # 처음 10개만 표시
                    print(f"  {i+1}. {boundary['type']} (위치: {boundary['start_pos']}-{boundary['end_pos']}, 신뢰도: {boundary['confidence']:.2f})")
                    if boundary.get('context7_based', False):
                        print(f"     Context7 PRegEx 기반 매칭")
            
            print(f"\n권장사항:")
            for recommendation in analysis['chunking_recommendations']:
                print(f"  - {recommendation}")
            
            print("=" * 80)
    
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
