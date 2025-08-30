"""
SQL 파서 - Oracle PL/SQL을 포함한 SQL 구문 분석
JSQLParser와 정규식을 조합하여 SQL 구문을 분석하고 메타데이터를 추출합니다.
"""

import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
import json

try:
    # JSQLParser Python 바인딩이 있다면 사용
    import jsqlparser
    HAS_JSQLPARSER = True
except ImportError:
    # 없다면 정규식 기반으로 폴백
    HAS_JSQLPARSER = False

from models.database import SqlUnit, Join, RequiredFilter, Edge
from utils.confidence_calculator import ConfidenceCalculator

class SqlParser:
    """SQL 구문을 분석하는 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        SQL 파서 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        
        # Oracle PL/SQL 키워드
        self.plsql_keywords = [
            'PROCEDURE', 'FUNCTION', 'PACKAGE', 'TRIGGER', 'CURSOR',
            'EXCEPTION', 'LOOP', 'IF', 'ELSIF', 'ELSE', 'CASE', 'WHEN'
        ]
        
        # SQL 패턴들
        self.table_pattern = re.compile(
            r'\b(?:FROM|JOIN|UPDATE|INSERT\s+INTO)\s+(\w+(?:\.\w+)?)',
            re.IGNORECASE
        )
        
        self.column_pattern = re.compile(
            r'\b(\w+)\.(\w+)\b',
            re.IGNORECASE
        )
        
        # 조인 패턴
        self.join_patterns = [
            re.compile(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', re.IGNORECASE),
            re.compile(r'JOIN\s+(\w+)\s+\w*\s*ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', re.IGNORECASE),
            re.compile(r'INNER\s+JOIN\s+(\w+)\s+\w*\s*ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', re.IGNORECASE),
            re.compile(r'LEFT\s+JOIN\s+(\w+)\s+\w*\s*ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', re.IGNORECASE),
        ]
        
        # WHERE 절 필터 패턴
        self.filter_patterns = [
            re.compile(r'(\w+)\.(\w+)\s*(=|!=|<>|LIKE|IN|NOT\s+IN)\s*([^,\s]+)', re.IGNORECASE),
            re.compile(r'(\w+)\s*(=|!=|<>|LIKE|IN|NOT\s+IN)\s*([^,\s]+)', re.IGNORECASE),
        ]
        
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Tuple[List[Join], List[RequiredFilter], List[str], List[str]]:
        """
        SQL 구문을 분석하여 조인, 필터, 테이블, 컬럼 정보 추출
        
        Args:
            sql_content: 분석할 SQL 구문
            context: 컨텍스트 정보 (파일 경로, 라인 번호 등)
            
        Returns:
            Tuple of (Joins, Filters, Tables, Columns)
        """
        
        joins = []
        filters = []
        tables = []
        columns = []
        
        try:
            # SQL 전처리
            normalized_sql = self._normalize_sql(sql_content)
            
            # JSQLParser 사용 가능하면 우선 시도
            if HAS_JSQLPARSER:
                try:
                    parsed_info = self._parse_with_jsqlparser(normalized_sql)
                    if parsed_info:
                        return parsed_info
                except Exception as e:
                    print(f"JSQLParser 파싱 실패, 정규식으로 폴백: {e}")
            
            # 정규식 기반 분석
            joins = self._extract_joins_regex(normalized_sql)
            filters = self._extract_filters_regex(normalized_sql)
            tables = self._extract_tables_regex(normalized_sql)
            columns = self._extract_columns_regex(normalized_sql)
            
        except Exception as e:
            print(f"SQL 파싱 오류: {e}")
            
        return joins, filters, tables, columns
        
    def _normalize_sql(self, sql_content: str) -> str:
        """
        SQL 구문을 분석하기 쉽게 정규화
        
        Args:
            sql_content: 원본 SQL 구문
            
        Returns:
            정규화된 SQL 구문
        """
        
        # 여러 공백을 하나로 통일
        normalized = re.sub(r'\s+', ' ', sql_content.strip())
        
        # 주석 제거
        normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        # Oracle 특수 구문 처리
        normalized = self._handle_oracle_syntax(normalized)
        
        return normalized
        
    def _handle_oracle_syntax(self, sql: str) -> str:
        """
        Oracle 데이터베이스 특수 구문을 처리
        
        Args:
            sql: SQL 구문
            
        Returns:
            Oracle 구문이 처리된 SQL
        """
        
        # DUAL 테이블 처리
        sql = re.sub(r'\bFROM\s+DUAL\b', 'FROM DUAL', sql, flags=re.IGNORECASE)
        
        # Oracle 힌트 제거
        sql = re.sub(r'/\*\+.*?\*/', '', sql, flags=re.DOTALL)
        
        # ROWNUM 처리
        sql = re.sub(r'\bROWNUM\s*<=?\s*\d+', 'ROWNUM <= N', sql, flags=re.IGNORECASE)
        
        return sql
        
    def _parse_with_jsqlparser(self, sql: str) -> Optional[Tuple[List[Join], List[RequiredFilter], List[str], List[str]]]:
        """
        JSQLParser 라이브러리를 사용한 정확한 SQL 분석
        
        Args:
            sql: 분석할 SQL 구문
            
        Returns:
            파싱된 조인, 필터, 테이블, 컬럼 정보 또는 None
        
        Note:
            현재는 구현 예정 상태로 None을 반환
        """
        
        # JSQLParser Python 바인딩 사용한 구현
        # 현재는 스켈레톤만 제공
        
        return None
        
    def _extract_joins_regex(self, sql: str) -> List[Join]:
        """
        정규식 패턴을 사용하여 SQL에서 조인 조건을 추출
        
        Args:
            sql: SQL 구문
            
        Returns:
            추출된 조인 정보 리스트
        """
        
        joins = []
        
        for pattern in self.join_patterns:
            matches = pattern.finditer(sql)
            
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 4:
                    # 명시적 JOIN 구문인 경우
                    if 'JOIN' in match.group().upper():
                        if len(groups) >= 5:
                            join = Join(
                                sql_id=None,
                                l_table=groups[1],  # JOIN 후 테이블
                                l_col=groups[2],
                                op='=',
                                r_table=groups[3],
                                r_col=groups[4],
                                inferred_pkfk=0,
                                confidence=0.9  # 명시적 조인은 신뢰도 높음
                            )
                        else:
                            continue
                    else:
                        # WHERE 절의 조인 조건
                        join = Join(
                            sql_id=None,
                            l_table=groups[0],
                            l_col=groups[1],
                            op='=',
                            r_table=groups[2],
                            r_col=groups[3],
                            inferred_pkfk=0,
                            confidence=0.8
                        )
                    
                    joins.append(join)
                    
        return joins
        
    def _extract_filters_regex(self, sql: str) -> List[RequiredFilter]:
        """
        정규식 패턴을 사용하여 WHERE 절의 필터 조건을 추출
        
        Args:
            sql: SQL 구문
            
        Returns:
            추출된 필터 조건 리스트
        """
        
        filters = []
        
        # WHERE 절 추출
        where_match = re.search(r'\bWHERE\b(.*?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|$)', sql, re.IGNORECASE | re.DOTALL)
        
        if where_match:
            where_clause = where_match.group(1)
            
            for pattern in self.filter_patterns:
                matches = pattern.finditer(where_clause)
                
                for match in matches:
                    groups = match.groups()
                    
                    if len(groups) >= 3:
                        table_name = None
                        column_name = groups[0]
                        op = groups[1] if len(groups) > 1 else '='
                        value_repr = groups[2] if len(groups) > 2 else 'unknown'
                        
                        # 테이블.컬럼 형태인지 확인
                        if len(groups) >= 4:  # 테이블명이 별도로 있는 경우
                            table_name = groups[0]
                            column_name = groups[1]
                            op = groups[2]
                            value_repr = groups[3]
                        elif '.' in column_name:
                            # 테이블.컬럼 형태
                            parts = column_name.split('.')
                            if len(parts) == 2:
                                table_name = parts[0]
                                column_name = parts[1]
                        
                        # 값 정규화
                        value_repr = self._normalize_filter_value(value_repr)
                        
                        # 항상 적용되는 필터인지 판단 (동적 조건이 없으면 1)
                        always_applied = 1 if not self._has_dynamic_condition(match.group()) else 0
                        
                        filter_obj = RequiredFilter(
                            sql_id=None,
                            table_name=table_name,
                            column_name=column_name,
                            op=op.upper(),
                            value_repr=value_repr,
                            always_applied=always_applied,
                            confidence=0.7
                        )
                        
                        filters.append(filter_obj)
                        
        return filters
        
    def _extract_tables_regex(self, sql: str) -> List[str]:
        """
        정규식 패턴을 사용하여 SQL에서 테이블명을 추출
        
        Args:
            sql: SQL 구문
            
        Returns:
            추출된 테이블명 리스트
        """
        
        tables = set()
        
        # FROM, JOIN, UPDATE, INSERT INTO 절에서 테이블 추출
        matches = self.table_pattern.finditer(sql)
        
        for match in matches:
            table_name = match.group(1)
            
            # 스키마.테이블 형태에서 테이블명만 추출
            if '.' in table_name:
                table_name = table_name.split('.')[-1]
                
            # 별칭 제거 (AS 키워드가 있는 경우)
            table_name = re.sub(r'\s+AS\s+\w+', '', table_name, flags=re.IGNORECASE)
            table_name = table_name.strip()
            
            if table_name.upper() != 'DUAL':  # Oracle DUAL 테이블 제외
                tables.add(table_name.upper())
                
        return list(tables)
        
    def _extract_columns_regex(self, sql: str) -> List[str]:
        """
        정규식 패턴을 사용하여 SQL에서 컬럼 참조를 추출
        
        Args:
            sql: SQL 구문
            
        Returns:
            테이블명.컬럼명 형태의 컬럼 참조 리스트
        """
        
        columns = set()
        
        # 테이블.컬럼 형태의 참조 추출
        matches = self.column_pattern.finditer(sql)
        
        for match in matches:
            table_name = match.group(1).upper()
            column_name = match.group(2).upper()
            
            # Oracle 시스템 컬럼 제외
            if column_name not in ['ROWNUM', 'ROWID']:
                columns.add(f"{table_name}.{column_name}")
                
        return list(columns)
        
    def _normalize_filter_value(self, value: str) -> str:
        """
        필터 조건의 값을 표준화된 형태로 정규화
        
        Args:
            value: 원본 필터 값
            
        Returns:
            정규화된 필터 값 표현
        """
        
        value = value.strip()
        
        # 문자열 리터럴
        if value.startswith("'") and value.endswith("'"):
            return value
        elif value.startswith('"') and value.endswith('"'):
            return value
        # 숫자
        elif value.isdigit() or re.match(r'^\d+\.\d+$', value):
            return 'NUMBER'
        # 파라미터
        elif value.startswith(':') or value.startswith('?'):
            return ':param'
        # 함수 호출
        elif '(' in value and ')' in value:
            return 'FUNCTION()'
        else:
            return value
            
    def _has_dynamic_condition(self, condition: str) -> bool:
        """
        필터 조건이 동적(런타임에 변하는)인지 판단
        
        Args:
            condition: 필터 조건 문자열
            
        Returns:
            동적 조건이면 True, 정적 조건이면 False
        """
        
        # MyBatis 동적 파라미터
        if '${' in condition or '#{' in condition:
            return True
        
        # CASE 문
        if re.search(r'\bCASE\b.*\bWHEN\b', condition, re.IGNORECASE):
            return True
            
        # 함수 호출이 있는 경우
        if re.search(r'\w+\([^)]*\)', condition):
            return True
            
        return False
        
    def detect_plsql_elements(self, sql_content: str) -> Dict[str, List[str]]:
        """
        Oracle PL/SQL 특수 요소들을 감지하여 분류
        
        Args:
            sql_content: PL/SQL을 포함한 SQL 구문
            
        Returns:
            PL/SQL 요소별 감지된 이름들의 딕셔너리
        """
        
        elements = {
            'procedures': [],
            'functions': [], 
            'packages': [],
            'triggers': [],
            'cursors': [],
            'exceptions': []
        }
        
        # 프로시저 감지
        proc_pattern = r'(?:CREATE\s+OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)'
        matches = re.finditer(proc_pattern, sql_content, re.IGNORECASE)
        elements['procedures'] = [match.group(1) for match in matches]
        
        # 함수 감지  
        func_pattern = r'(?:CREATE\s+OR\s+REPLACE\s+)?FUNCTION\s+(\w+)'
        matches = re.finditer(func_pattern, sql_content, re.IGNORECASE)
        elements['functions'] = [match.group(1) for match in matches]
        
        # 패키지 감지
        pkg_pattern = r'(?:CREATE\s+OR\s+REPLACE\s+)?PACKAGE\s+(?:BODY\s+)?(\w+)'
        matches = re.finditer(pkg_pattern, sql_content, re.IGNORECASE)
        elements['packages'] = [match.group(1) for match in matches]
        
        # 트리거 감지
        trigger_pattern = r'(?:CREATE\s+OR\s+REPLACE\s+)?TRIGGER\s+(\w+)'
        matches = re.finditer(trigger_pattern, sql_content, re.IGNORECASE)
        elements['triggers'] = [match.group(1) for match in matches]
        
        # 커서 감지
        cursor_pattern = r'CURSOR\s+(\w+)'
        matches = re.finditer(cursor_pattern, sql_content, re.IGNORECASE)
        elements['cursors'] = [match.group(1) for match in matches]
        
        return elements