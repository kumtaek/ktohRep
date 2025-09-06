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

from parsers.base_parser import BaseParser

class JavaParserImproved(BaseParser):
    """개선된 Java 파서 - 과추출 문제 해결"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
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
        self._build_improved_patterns()
        
        # 신뢰도 설정
        self.confidence = 0.95

    def _build_improved_patterns(self):
        """개선된 패턴 구성 - 과추출 방지"""
        
        # 개선된 메소드 패턴 (과추출 방지)
        self.method_pattern = re.compile(
            r'(?:@\w+(?:\([^)]*\))?\s*)*\s*'  # 어노테이션 (선택적)
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
        self.class_pattern = re.compile(
            r'(?:public|private|protected|abstract|final|static\s+)*\s*'
            r'class\s+(\w+)\s*'
            r'(?:extends\s+(\w+))?\s*'
            r'(?:implements\s+([^{]+))?\s*'
            r'\{',
            re.MULTILINE
        )
        
        # 개선된 SQL 패턴
        self.sql_pattern = re.compile(
            r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']',
            re.IGNORECASE
        )

    def _get_parser_type(self) -> str:
        return 'java_improved'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Java 소스 코드를 파싱하여 메타데이터 추출 (개선된 버전)"""
        
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
            'confidence': self.confidence
        }
        
        return result

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """클래스 추출 (개선된 버전)"""
        classes = []
        
        matches = self.class_pattern.finditer(content)
        
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
        """메소드 추출 (개선된 버전 - 과추출 방지)"""
        methods = []
        
        matches = self.method_pattern.finditer(content)
        
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

    def _extract_sql_units(self, content: str) -> List[Dict[str, Any]]:
        """SQL Units 추출 (개선된 버전)"""
        sql_units = []
        
        matches = self.sql_pattern.finditer(content)
        
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
        """어노테이션 추출"""
        annotations = []
        
        annotation_pattern = re.compile(r'@(\w+)(?:\(([^)]*)\))?')
        matches = annotation_pattern.finditer(content)
        
        for match in matches:
            annotation_info = {
                'name': match.group(1),
                'attributes': match.group(2) if match.group(2) else '',
                'type': 'annotation'
            }
            annotations.append(annotation_info)
        
        return annotations

    def _extract_imports(self, content: str) -> List[str]:
        """Import 문 추출"""
        imports = []
        
        import_pattern = re.compile(r'import\s+([^;]+);', re.IGNORECASE)
        matches = import_pattern.finditer(content)
        
        for match in matches:
            imports.append(match.group(1).strip())
        
        return imports

    def _extract_dynamic_queries(self, content: str) -> List[Dict[str, Any]]:
        """다이나믹 쿼리 추출"""
        dynamic_queries = []
        
        # StringBuilder 패턴
        stringbuilder_pattern = re.compile(r'StringBuilder\s+(\w+)\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)')
        matches = stringbuilder_pattern.finditer(content)
        
        for match in matches:
            dynamic_queries.append({
                'type': 'stringbuilder_init',
                'variable': match.group(1),
                'initial_value': match.group(2),
                'unique_id': self._generate_unique_id(match.group(1), match.group(2))
            })
        
        return dynamic_queries

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """파일 메타데이터 추출"""
        if isinstance(context, str):
            file_path = context
        else:
            file_path = context.get('file_path', '')
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path) if file_path else '',
            'file_size': len(context.get('content', '')) if isinstance(context, dict) else 0,
            'parser_type': self._get_parser_type(),
            'confidence': self.confidence
        }

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

    def _is_keyword(self, word: str) -> bool:
        """키워드 여부 확인"""
        return word in self.java_keywords

    def _is_sql_keyword(self, word: str) -> bool:
        """SQL 키워드 여부 확인"""
        return word.upper() in self.sql_keywords

    def _get_database_type(self) -> str:
        """데이터베이스 타입 반환"""
        return 'oracle'

    def parse_sql(self, sql_content: str) -> Dict[str, Any]:
        """SQL 파싱"""
        return {
            'type': self._determine_sql_type(sql_content),
            'content': sql_content,
            'unique_id': self._generate_sql_unique_id(sql_content)
        }



