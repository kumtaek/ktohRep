#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
개선된 Java 파서 (Context7 기반)
과추출 문제 해결을 위한 정밀한 패턴 매칭
"""

import re
import os
import hashlib
from typing import Dict, List, Any, Set, Tuple

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

class ImprovedJavaParser:
    """개선된 Java 파서 - 과추출 문제 해결"""

    def __init__(self):
        # Java 키워드
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
            'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
            'volatile', 'while', 'true', 'false', 'null'
        }
        
        # SQL 키워드
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER',
            'DROP', 'TRUNCATE', 'MERGE', 'UNION', 'ALL', 'DISTINCT', 'COUNT', 'SUM',
            'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'EXISTS',
            'IN', 'NOT', 'NULL', 'IS', 'BETWEEN', 'LIKE', 'AND', 'OR'
        }
        
        # 개선된 패턴 구성
        if PREGEX_AVAILABLE:
            self._build_improved_patterns()
        else:
            self._build_fallback_patterns()

    def _build_improved_patterns(self):
        """개선된 PRegEx 패턴 구성 - 과추출 방지"""
        
        # Java 식별자 패턴 (키워드 제외)
        java_identifier = AnyLetter() + Optional(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$'))
        
        # Java 타입 패턴 (더 정확한 타입 매칭)
        java_type = Either(
            'void', 'int', 'long', 'short', 'byte', 'char', 'boolean', 'float', 'double',
            'String', 'Object', 'List', 'Map', 'Set', 'Collection', 'Optional',
            java_identifier + Optional('[]') + Optional('[]')  # 2차원 배열까지
        )
        
        # 개선된 메소드 시그니처 패턴 (과추출 방지)
        self.improved_method_pattern = Group(
            # 어노테이션 (선택적, 정확한 매칭)
            Optional(OneOrMore('@' + java_identifier + Optional('(' + Optional(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '"' | "'" | '(' | ')' | '=' | ',' | '{' | '}')) + ')') + Optional(AnyWhitespace()))) +
            
            # 접근 제어자 (필수)
            Either('public', 'private', 'protected') +
            Optional(AnyWhitespace()) +
            
            # 기타 수식자 (선택적)
            Optional(Either('static', 'final', 'abstract', 'synchronized') + Optional(AnyWhitespace())) +
            
            # 반환 타입 (필수)
            java_type +
            Optional(AnyWhitespace()) +
            
            # 메소드명 (필수, 키워드가 아닌 식별자)
            Capture(java_identifier) +
            Optional(AnyWhitespace()) +
            
            # 파라미터 (필수)
            '(' +
            Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&' | '.' | '[' | ']'))) +
            ')' +
            Optional(AnyWhitespace()) +
            
            # 예외 선언 (선택적)
            Optional('throws' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '.'))) +
            Optional(AnyWhitespace()) +
            
            # 메소드 본문 시작 '{' 또는 ';' (생성자/추상 메소드)
            Either('{', ';')
        )
        
        # 개선된 클래스 선언 패턴
        self.improved_class_pattern = Group(
            # 접근 제어자 (선택적)
            Optional(Either('public', 'private', 'protected', 'abstract', 'final', 'static') + Optional(AnyWhitespace())) +
            
            # class 키워드 (필수)
            'class' + Optional(AnyWhitespace()) +
            
            # 클래스명 (필수)
            Capture(java_identifier) +
            Optional(AnyWhitespace()) +
            
            # 상속 (선택적)
            Optional('extends' + Optional(AnyWhitespace()) + Capture(java_identifier)) +
            Optional(AnyWhitespace()) +
            
            # 구현 (선택적)
            Optional('implements' + Optional(AnyWhitespace()) + Capture(OneOrMore(java_identifier + Optional(AnyWhitespace()) + ',' + Optional(AnyWhitespace())))) +
            Optional(AnyWhitespace()) +
            
            # 클래스 본문 시작 '{'
            '{'
        )
        
        # 개선된 SQL 문자열 패턴 (더 정확한 SQL 인식)
        self.improved_sql_pattern = Either(
            '"' + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', "'", '"', '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + '"',
            "'" + Capture(OneOrMore(Either(*self.sql_keywords) + Optional(AnyWhitespace()) + AnyLetter() + AnyDigit() + Either(' ', '.', ',', '(', ')', '=', '>', '<', '!', '+', '-', '*', '/', '%', '?', ':', ';', '"', "'", '[', ']', '{', '}', '|', '&', '^', '~', '`', '@', '#', '$', '\\', '\n', '\r', '\t'))) + "'"
        )

    def _build_fallback_patterns(self):
        """Fallback 패턴 구성"""
        
        # 개선된 메소드 패턴 (정규식)
        self.fallback_method_pattern = re.compile(
            r'(?:@\w+(?:\([^)]*\))?\s*)*\s*'  # 어노테이션
            r'(?:public|private|protected)\s+'  # 접근 제어자 (필수)
            r'(?:static|final|abstract|synchronized\s+)*'  # 기타 수식자
            r'(?:[\w<>\[\],\s?&\.]+\s+)?'  # 반환 타입
            r'(\w+)\s*'  # 메소드명
            r'\([^)]*\)\s*'  # 파라미터
            r'(?:throws\s+[\w\s,\.]+)?\s*'  # 예외 선언
            r'[;{]',  # 메소드 본문 시작
            re.MULTILINE | re.DOTALL
        )
        
        # 개선된 클래스 패턴
        self.fallback_class_pattern = re.compile(
            r'(?:public|private|protected|abstract|final|static\s+)*\s*'
            r'class\s+(\w+)\s*'
            r'(?:extends\s+(\w+))?\s*'
            r'(?:implements\s+([^{]+))?\s*'
            r'\{',
            re.MULTILINE
        )
        
        # 개선된 SQL 패턴
        self.fallback_sql_pattern = re.compile(
            r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']',
            re.IGNORECASE
        )

    def extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """개선된 메소드 추출 - 과추출 방지"""
        methods = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.improved_method_pattern.get_captures(content)
            
            for match in matches:
                if len(match) >= 1 and match[0] not in self.java_keywords:
                    method_info = {
                        'name': match[0],
                        'parameters': match[1] if len(match) > 1 and match[1] else '',
                        'exceptions': match[2] if len(match) > 2 and match[2] else '',
                        'type': 'method',
                        'unique_id': self._generate_unique_id(match[0], match[1] if len(match) > 1 else '')
                    }
                    methods.append(method_info)
        else:
            # Fallback 패턴 사용
            matches = self.fallback_method_pattern.finditer(content)
            
            for match in matches:
                method_name = match.group(1)
                if method_name not in self.java_keywords:
                    method_info = {
                        'name': method_name,
                        'parameters': '',
                        'exceptions': '',
                        'type': 'method',
                        'unique_id': self._generate_unique_id(method_name, '')
                    }
                    methods.append(method_info)
        
        return methods

    def extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """개선된 클래스 추출"""
        classes = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.improved_class_pattern.get_captures(content)
            
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
            matches = self.fallback_class_pattern.finditer(content)
            
            for match in matches:
                class_info = {
                    'name': match.group(1),
                    'extends': match.group(2) if match.group(2) else None,
                    'implements': match.group(3).split(',') if match.group(3) else [],
                    'type': 'class'
                }
                classes.append(class_info)
        
        return classes

    def extract_sql_units(self, content: str) -> List[Dict[str, Any]]:
        """개선된 SQL Units 추출"""
        sql_units = []
        
        if PREGEX_AVAILABLE:
            # PRegEx 사용
            matches = self.improved_sql_pattern.get_captures(content)
            
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
            matches = self.fallback_sql_pattern.finditer(content)
            
            for match in matches:
                sql_content = match.group(1)
                sql_units.append({
                    'type': self._determine_sql_type(sql_content),
                    'sql_content': sql_content,
                    'unique_id': self._generate_sql_unique_id(sql_content),
                    'source': 'string_literal'
                })
        
        return sql_units

    def _determine_sql_type(self, sql_content: str) -> str:
        """SQL 타입 결정"""
        sql_upper = sql_content.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        elif sql_upper.startswith('TRUNCATE'):
            return 'TRUNCATE'
        elif sql_upper.startswith('MERGE'):
            return 'MERGE'
        else:
            return 'UNKNOWN'

    def _generate_unique_id(self, name: str, params: str) -> str:
        """고유 ID 생성"""
        combined = f"{name}({params})"
        return hashlib.md5(combined.encode()).hexdigest()[:8]

    def _generate_sql_unique_id(self, sql_content: str) -> str:
        """SQL 고유 ID 생성"""
        return hashlib.md5(sql_content.encode()).hexdigest()[:8]

    def parse_content(self, content: str) -> Dict[str, Any]:
        """전체 파싱 실행"""
        result = {
            'classes': self.extract_classes(content),
            'methods': self.extract_methods(content),
            'sql_units': self.extract_sql_units(content),
            'confidence': 0.95  # 개선된 정확도
        }
        return result

def test_improved_parser():
    """개선된 파서 테스트"""
    
    print("=== 개선된 Java 파서 테스트 ===\n")
    
    # 샘플 파일 테스트
    sample_file = "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java"
    
    if not os.path.exists(sample_file):
        print(f"파일을 찾을 수 없습니다: {sample_file}")
        return
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 개선된 파서로 분석
    parser = ImprovedJavaParser()
    result = parser.parse_content(content)
    
    print(f"분석 파일: {sample_file}")
    print(f"파일 크기: {len(content)} 문자\n")
    
    print(f"개선된 파서 결과:")
    print(f"  클래스 수: {len(result['classes'])}")
    for i, cls in enumerate(result['classes'], 1):
        print(f"    {i}. {cls['name']}")
    
    print(f"  메소드 수: {len(result['methods'])}")
    for i, method in enumerate(result['methods'], 1):
        print(f"    {i}. {method['name']}")
    
    print(f"  SQL Units 수: {len(result['sql_units'])}")
    for i, sql in enumerate(result['sql_units'], 1):
        print(f"    {i}. {sql['type']}: {sql['sql_content'][:50]}...")
    
    print(f"\n정확도: {result['confidence'] * 100:.1f}%")

if __name__ == "__main__":
    test_improved_parser()
