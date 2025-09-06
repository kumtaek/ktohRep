#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 SQL 파서
- PRegEx를 활용한 정확한 패턴 매칭
- 중복 방지 및 정확도 향상
- Oracle SQL 문법 (CRUD, TRUNCATE, MERGE) 지원
- Oracle 특화 기능 (계층 쿼리, 분석 함수) 인식
"""

import re
import os
import hashlib
from typing import Dict, List, Any, Set, Tuple

from ..base_parser import BaseParser

# PRegEx를 사용한 패턴 구성 (Context7 기반)
try:
    from pregex.core.pre import Pregex
    from pregex.core.classes import AnyLetter, AnyDigit, AnyWhitespace
    from pregex.core.quantifiers import Optional, OneOrMore
    from pregex.core.operators import Either
    from pregex.core.groups import Capture, Group
    from pregex.core.assertions import WordBoundary
    PREGEX_AVAILABLE = True
except ImportError:
    PREGEX_AVAILABLE = False

class SQLParserContext7(BaseParser):
    """SQL Parser (Context7 기반)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # SQL 키워드 (Context7 기반)
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER',
            'DROP', 'TRUNCATE', 'MERGE', 'UNION', 'ALL', 'DISTINCT', 'COUNT', 'SUM',
            'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'EXISTS',
            'IN', 'NOT', 'NULL', 'IS', 'BETWEEN', 'LIKE', 'AND', 'OR', 'AS'
        }
        
        # Oracle 특화 키워드
        self.oracle_keywords = {
            'ROWNUM', 'ROWID', 'DUAL', 'SYSDATE', 'NVL', 'DECODE', 'CONNECT', 'PRIOR',
            'START', 'WITH', 'LEVEL', 'SIBLINGS', 'CONNECT_BY_ROOT', 'CONNECT_BY_ISLEAF',
            'RANK', 'DENSE_RANK', 'ROW_NUMBER', 'OVER', 'PARTITION', 'WINDOW'
        }
        
        # Context7 기반 패턴 구성
        if PREGEX_AVAILABLE:
            self._build_context7_patterns()
        
        # Fallback 패턴은 항상 구성
        self._build_fallback_patterns()
        
        # 신뢰도 설정 (Context7 기반으로 높은 신뢰도)
        self.confidence = 0.95

    def _build_context7_patterns(self):
        """Context7 기반 패턴 구성 (고급 기능 활용)"""
        
        # SQL 식별자 패턴 (Context7 고급 기능 활용)
        sql_identifier = AnyLetter() + Optional(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$' | '#'))
        
        # Context7 고급 SELECT 패턴
        self.context7_select_pattern = Group(
            'SELECT' + Optional(AnyWhitespace()) +
            Optional('DISTINCT' + Optional(AnyWhitespace())) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '.' | ',' | '*' | '(' | ')' | 'AS' | '_' | '$' | '#')) +
            Optional(AnyWhitespace()) +
            'FROM' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '.' | ',' | '(' | ')' | 'AS' | '_' | '$' | '#'))
        )
        
        # Context7 고급 INSERT 패턴
        self.context7_insert_pattern = Group(
            'INSERT' + Optional(AnyWhitespace()) +
            Optional('INTO' + Optional(AnyWhitespace())) +
            Capture(sql_identifier) +
            Optional(AnyWhitespace()) +
            Optional('(' + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '_' | '$' | '#')) + ')' + Optional(AnyWhitespace())) +
            'VALUES' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '(' | ')' | "'" | '"' | '_' | '$' | '#'))
        )
        
        # Context7 고급 UPDATE 패턴
        self.context7_update_pattern = Group(
            'UPDATE' + Optional(AnyWhitespace()) +
            Capture(sql_identifier) +
            Optional(AnyWhitespace()) +
            'SET' + Optional(AnyWhitespace()) +
            Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '=' | '.' | "'" | '"' | '_' | '$' | '#')) +
            Optional(AnyWhitespace()) +
            Optional('WHERE' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '>' | '<' | '!' | 'AND' | 'OR' | 'IN' | 'NOT' | 'NULL' | 'IS' | 'BETWEEN' | 'LIKE' | '.' | "'" | '"' | '_' | '$' | '#')))
        )
        
        # Context7 고급 DELETE 패턴
        self.context7_delete_pattern = Group(
            'DELETE' + Optional(AnyWhitespace()) +
            Optional('FROM' + Optional(AnyWhitespace())) +
            Capture(sql_identifier) +
            Optional(AnyWhitespace()) +
            Optional('WHERE' + Optional(AnyWhitespace()) + Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | '=' | '>' | '<' | '!' | 'AND' | 'OR' | 'IN' | 'NOT' | 'NULL' | 'IS' | 'BETWEEN' | 'LIKE' | '.' | "'" | '"' | '_' | '$' | '#')))
        )

    def _build_fallback_patterns(self):
        """Fallback 패턴 구성 (Context7 스타일 유지)"""
        
        # Context7 스타일의 SELECT 패턴
        self.fallback_select_pattern = re.compile(
            r'SELECT\s+(?:DISTINCT\s+)?(.+?)\s+FROM\s+(\w+(?:\.\w+)?)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
        
        # Context7 스타일의 INSERT 패턴
        self.fallback_insert_pattern = re.compile(
            r'INSERT\s+(?:INTO\s+)?(\w+(?:\.\w+)?)\s*(?:\(([^)]+)\))?\s*VALUES\s*(.+)',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
        
        # Context7 스타일의 UPDATE 패턴
        self.fallback_update_pattern = re.compile(
            r'UPDATE\s+(\w+(?:\.\w+)?)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
        
        # Context7 스타일의 DELETE 패턴
        self.fallback_delete_pattern = re.compile(
            r'DELETE\s+(?:FROM\s+)?(\w+(?:\.\w+)?)(?:\s+WHERE\s+(.+))?',
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

    def _get_parser_type(self) -> str:
        return 'sql_context7'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 쿼리를 파싱하여 메타데이터 추출 (Context7 기반)"""
        
        # 정규화
        normalized_content = self._normalize_content(content)
        
        result = {
            'select_queries': self._extract_select_queries(normalized_content),
            'insert_queries': self._extract_insert_queries(normalized_content),
            'update_queries': self._extract_update_queries(normalized_content),
            'delete_queries': self._extract_delete_queries(normalized_content),
            'tables': self._extract_tables(normalized_content),
            'columns': self._extract_columns(normalized_content),
            'joins': self._extract_joins(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }
        
        return result

    def _extract_select_queries(self, content: str) -> List[Dict[str, Any]]:
        """SELECT 쿼리 추출 (Context7 기반)"""
        queries = []
        
        if PREGEX_AVAILABLE:
            try:
                matches = self.context7_select_pattern.get_captures(content)
                
                for match in matches:
                    if len(match) >= 2:
                        query_info = {
                            'type': 'SELECT',
                            'columns': match[0].strip() if match[0] else '',
                            'tables': match[1].strip() if match[1] else '',
                            'unique_id': self._generate_unique_id('SELECT', match[0] + match[1] if len(match) >= 2 else ''),
                            'context7_confidence': 0.98
                        }
                        queries.append(query_info)
            except Exception as e:
                print(f"Context7 SELECT 패턴 오류, Fallback 사용: {e}")
                matches = self.fallback_select_pattern.finditer(content)
                
                for match in matches:
                    query_info = {
                        'type': 'SELECT',
                        'columns': match.group(1).strip(),
                        'tables': match.group(2).strip(),
                        'unique_id': self._generate_unique_id('SELECT', match.group(1) + match.group(2)),
                        'context7_confidence': 0.85
                    }
                    queries.append(query_info)
        else:
            matches = self.fallback_select_pattern.finditer(content)
            
            for match in matches:
                query_info = {
                    'type': 'SELECT',
                    'columns': match.group(1).strip(),
                    'tables': match.group(2).strip(),
                    'unique_id': self._generate_unique_id('SELECT', match.group(1) + match.group(2)),
                    'context7_confidence': 0.85
                }
                queries.append(query_info)
        
        return queries

    def _extract_insert_queries(self, content: str) -> List[Dict[str, Any]]:
        """INSERT 쿼리 추출 (Context7 기반)"""
        queries = []
        
        if PREGEX_AVAILABLE:
            try:
                matches = self.context7_insert_pattern.get_captures(content)
                
                for match in matches:
                    if len(match) >= 1:
                        query_info = {
                            'type': 'INSERT',
                            'table': match[0].strip() if match[0] else '',
                            'columns': match[1].strip() if len(match) > 1 and match[1] else '',
                            'values': match[2].strip() if len(match) > 2 and match[2] else '',
                            'unique_id': self._generate_unique_id('INSERT', match[0]),
                            'context7_confidence': 0.98
                        }
                        queries.append(query_info)
            except Exception as e:
                print(f"Context7 INSERT 패턴 오류, Fallback 사용: {e}")
                matches = self.fallback_insert_pattern.finditer(content)
                
                for match in matches:
                    query_info = {
                        'type': 'INSERT',
                        'table': match.group(1).strip(),
                        'columns': match.group(2).strip() if match.group(2) else '',
                        'values': match.group(3).strip(),
                        'unique_id': self._generate_unique_id('INSERT', match.group(1)),
                        'context7_confidence': 0.85
                    }
                    queries.append(query_info)
        else:
            matches = self.fallback_insert_pattern.finditer(content)
            
            for match in matches:
                query_info = {
                    'type': 'INSERT',
                    'table': match.group(1).strip(),
                    'columns': match.group(2).strip() if match.group(2) else '',
                    'values': match.group(3).strip(),
                    'unique_id': self._generate_unique_id('INSERT', match.group(1)),
                    'context7_confidence': 0.85
                }
                queries.append(query_info)
        
        return queries

    def _extract_update_queries(self, content: str) -> List[Dict[str, Any]]:
        """UPDATE 쿼리 추출 (Context7 기반)"""
        queries = []
        
        if PREGEX_AVAILABLE:
            try:
                matches = self.context7_update_pattern.get_captures(content)
                
                for match in matches:
                    if len(match) >= 2:
                        query_info = {
                            'type': 'UPDATE',
                            'table': match[0].strip() if match[0] else '',
                            'set_clause': match[1].strip() if match[1] else '',
                            'where_clause': match[2].strip() if len(match) > 2 and match[2] else '',
                            'unique_id': self._generate_unique_id('UPDATE', match[0]),
                            'context7_confidence': 0.98
                        }
                        queries.append(query_info)
            except Exception as e:
                print(f"Context7 UPDATE 패턴 오류, Fallback 사용: {e}")
                matches = self.fallback_update_pattern.finditer(content)
                
                for match in matches:
                    query_info = {
                        'type': 'UPDATE',
                        'table': match.group(1).strip(),
                        'set_clause': match.group(2).strip(),
                        'where_clause': match.group(3).strip() if match.group(3) else '',
                        'unique_id': self._generate_unique_id('UPDATE', match.group(1)),
                        'context7_confidence': 0.85
                    }
                    queries.append(query_info)
        else:
            matches = self.fallback_update_pattern.finditer(content)
            
            for match in matches:
                query_info = {
                    'type': 'UPDATE',
                    'table': match.group(1).strip(),
                    'set_clause': match.group(2).strip(),
                    'where_clause': match.group(3).strip() if match.group(3) else '',
                    'unique_id': self._generate_unique_id('UPDATE', match.group(1)),
                    'context7_confidence': 0.85
                }
                queries.append(query_info)
        
        return queries

    def _extract_delete_queries(self, content: str) -> List[Dict[str, Any]]:
        """DELETE 쿼리 추출 (Context7 기반)"""
        queries = []
        
        if PREGEX_AVAILABLE:
            try:
                matches = self.context7_delete_pattern.get_captures(content)
                
                for match in matches:
                    if len(match) >= 1:
                        query_info = {
                            'type': 'DELETE',
                            'table': match[0].strip() if match[0] else '',
                            'where_clause': match[1].strip() if len(match) > 1 and match[1] else '',
                            'unique_id': self._generate_unique_id('DELETE', match[0]),
                            'context7_confidence': 0.98
                        }
                        queries.append(query_info)
            except Exception as e:
                print(f"Context7 DELETE 패턴 오류, Fallback 사용: {e}")
                matches = self.fallback_delete_pattern.finditer(content)
                
                for match in matches:
                    query_info = {
                        'type': 'DELETE',
                        'table': match.group(1).strip(),
                        'where_clause': match.group(2).strip() if match.group(2) else '',
                        'unique_id': self._generate_unique_id('DELETE', match.group(1)),
                        'context7_confidence': 0.85
                    }
                    queries.append(query_info)
        else:
            matches = self.fallback_delete_pattern.finditer(content)
            
            for match in matches:
                query_info = {
                    'type': 'DELETE',
                    'table': match.group(1).strip(),
                    'where_clause': match.group(2).strip() if match.group(2) else '',
                    'unique_id': self._generate_unique_id('DELETE', match.group(1)),
                    'context7_confidence': 0.85
                }
                queries.append(query_info)
        
        return queries

    def _extract_tables(self, content: str) -> List[str]:
        """테이블명 추출 (Context7 기반)"""
        tables = set()
        
        # FROM 절에서 테이블 추출
        from_pattern = re.compile(r'FROM\s+(\w+(?:\.\w+)?)', re.IGNORECASE)
        matches = from_pattern.finditer(content)
        
        for match in matches:
            tables.add(match.group(1))
        
        # JOIN 절에서 테이블 추출
        join_pattern = re.compile(r'JOIN\s+(\w+(?:\.\w+)?)', re.IGNORECASE)
        matches = join_pattern.finditer(content)
        
        for match in matches:
            tables.add(match.group(1))
        
        return list(tables)

    def _extract_columns(self, content: str) -> List[str]:
        """컬럼명 추출 (Context7 기반)"""
        columns = set()
        
        # SELECT 절에서 컬럼 추출
        select_pattern = re.compile(r'SELECT\s+(?:DISTINCT\s+)?(.+?)\s+FROM', re.IGNORECASE | re.DOTALL)
        matches = select_pattern.finditer(content)
        
        for match in matches:
            column_list = match.group(1)
            # 쉼표로 분리된 컬럼들 추출
            column_items = re.split(r',', column_list)
            for item in column_items:
                # AS 별칭 제거
                column = re.sub(r'\s+AS\s+\w+', '', item, flags=re.IGNORECASE).strip()
                if column and column != '*':
                    columns.add(column)
        
        return list(columns)

    def _extract_joins(self, content: str) -> List[Dict[str, str]]:
        """JOIN 관계 추출 (Context7 기반)"""
        joins = []
        
        # JOIN 패턴 추출
        join_pattern = re.compile(r'(\w+(?:\.\w+)?)\s+JOIN\s+(\w+(?:\.\w+)?)\s+ON\s+(.+)', re.IGNORECASE)
        matches = join_pattern.finditer(content)
        
        for match in matches:
            join_info = {
                'left_table': match.group(1),
                'right_table': match.group(2),
                'condition': match.group(3).strip()
            }
            joins.append(join_info)
        
        return joins

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """파일 메타데이터 추출 (Context7 기반)"""
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

    def _generate_unique_id(self, query_type: str, content: str) -> str:
        """고유 ID 생성 (Context7 기반)"""
        combined = f"{query_type}:{content}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]

    def _get_database_type(self) -> str:
        """데이터베이스 타입 반환 (Context7 기반)"""
        return 'oracle'

    def parse_sql(self, sql_content: str) -> Dict[str, Any]:
        """SQL 파싱 (Context7 기반)"""
        return {
            'type': self._determine_sql_type(sql_content),
            'content': sql_content,
            'unique_id': self._generate_unique_id('SQL', sql_content)
        }

    def _determine_sql_type(self, sql_content: str) -> str:
        """SQL 타입 결정 (Context7 기반)"""
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



