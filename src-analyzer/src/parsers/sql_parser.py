"""
SQL parser for Oracle dialect
Handles SQL statements, joins, filters, and Oracle-specific syntax
"""

import os
import re
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import sqlparse
from sqlparse import sql, tokens as T


@dataclass
class SQLParsingResult:
    """SQL 파싱 결과"""
    file_info: Dict
    statements: List[Dict]
    joins: List[Dict]
    filters: List[Dict]
    tables_used: List[str]
    columns_used: List[str]
    confidence: float


@dataclass
class JoinInfo:
    """조인 정보"""
    left_table: str
    left_column: str
    operator: str
    right_table: str
    right_column: str
    join_type: str  # INNER, LEFT, RIGHT, FULL
    confidence: float


@dataclass
class FilterInfo:
    """필터 정보"""
    table_name: str
    column_name: str
    operator: str
    value: str
    always_applied: bool
    confidence: float


class SQLParser:
    """SQL 파서 (Oracle 방언 지원)"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.oracle_dialect = self.config.get('oracle_dialect', True)
        self.extract_joins = self.config.get('extract_joins', True)
        self.extract_filters = self.config.get('extract_filters', True)
    
    def can_parse(self, file_path: str) -> bool:
        """파일 파싱 가능 여부 확인"""
        return file_path.endswith('.sql')
    
    def calculate_file_hash(self, content: str) -> str:
        """파일 내용의 SHA-256 해시 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def count_lines(self, content: str) -> int:
        """코드 라인 수 계산"""
        return len([line for line in content.splitlines() if line.strip()])
    
    def normalize_sql(self, sql_text: str) -> str:
        """SQL 정규화 (파라미터 제거, 공백 정리)"""
        # 파라미터 정규화 (:param -> :PARAM, ? -> :PARAM)
        normalized = re.sub(r':\w+', ':PARAM', sql_text)
        normalized = re.sub(r'\?', ':PARAM', normalized)
        
        # 문자열 리터럴 정규화
        normalized = re.sub(r"'[^']*'", "'STRING'", normalized)
        normalized = re.sub(r'"[^"]*"', "'STRING'", normalized)
        
        # 숫자 정규화
        normalized = re.sub(r'\b\d+\b', 'NUMBER', normalized)
        
        # 공백 정리
        normalized = ' '.join(normalized.split())
        
        return normalized.upper()
    
    def create_fingerprint(self, sql_text: str) -> str:
        """SQL 구조 기반 지문 생성"""
        try:
            parsed = sqlparse.parse(sql_text)[0]
            
            # 주요 구조 요소만 추출
            structure_tokens = []
            for token in parsed.flatten():
                if token.ttype in (T.Keyword, T.Keyword.DML, T.Keyword.DDL):
                    structure_tokens.append(str(token).upper())
                elif token.ttype is T.Name:
                    structure_tokens.append('NAME')
                elif token.ttype is T.Operator:
                    structure_tokens.append(str(token))
            
            fingerprint = ' '.join(structure_tokens)
            return hashlib.md5(fingerprint.encode()).hexdigest()[:16]
        except:
            # 파싱 실패 시 정규화된 SQL로 지문 생성
            normalized = self.normalize_sql(sql_text)
            return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def extract_tables_from_sql(self, sql_text: str) -> List[str]:
        """SQL에서 사용된 테이블 추출"""
        tables = set()
        
        try:
            parsed = sqlparse.parse(sql_text)[0]
            
            # FROM, JOIN 절에서 테이블 추출
            from_seen = False
            join_seen = False
            
            for token in parsed.flatten():
                if token.ttype is T.Keyword and str(token).upper() in ('FROM', 'UPDATE', 'INTO'):
                    from_seen = True
                elif token.ttype is T.Keyword and str(token).upper() in ('JOIN', 'LEFT', 'RIGHT', 'INNER', 'FULL'):
                    join_seen = True
                elif token.ttype is T.Name and (from_seen or join_seen):
                    table_name = str(token).strip()
                    if table_name and not table_name.upper() in ('SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING'):
                        tables.add(table_name.upper())
                elif token.ttype is T.Keyword:
                    from_seen = False
                    join_seen = False
        except:
            # 파싱 실패 시 정규식으로 테이블 추출
            from_pattern = r'FROM\s+([A-Za-z_][A-Za-z0-9_]*)'
            join_pattern = r'JOIN\s+([A-Za-z_][A-Za-z0-9_]*)'
            update_pattern = r'UPDATE\s+([A-Za-z_][A-Za-z0-9_]*)'
            into_pattern = r'INTO\s+([A-Za-z_][A-Za-z0-9_]*)'
            
            for pattern in [from_pattern, join_pattern, update_pattern, into_pattern]:
                matches = re.findall(pattern, sql_text, re.IGNORECASE)
                tables.update([match.upper() for match in matches])
        
        return list(tables)
    
    def extract_columns_from_sql(self, sql_text: str) -> List[str]:
        """SQL에서 사용된 컬럼 추출"""
        columns = set()
        
        # SELECT 절 컬럼 추출
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        match = re.search(select_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if match:
            select_clause = match.group(1)
            # 간단한 컬럼 추출 (별표 제외)
            if '*' not in select_clause:
                col_pattern = r'([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)'
                matches = re.findall(col_pattern, select_clause)
                columns.update([match.upper() for match in matches])
        
        # WHERE 절 컬럼 추출
        where_pattern = r'WHERE\s+.*?(?=GROUP|ORDER|HAVING|$)'
        match = re.search(where_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if match:
            where_clause = match.group(0)
            col_pattern = r'([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\s*[=<>!]'
            matches = re.findall(col_pattern, where_clause)
            columns.update([match.upper() for match in matches])
        
        return list(columns)
    
    def extract_joins(self, sql_text: str) -> List[JoinInfo]:
        """조인 조건 추출"""
        joins = []
        
        try:
            # JOIN ... ON ... 패턴 추출
            join_pattern = r'((?:INNER|LEFT|RIGHT|FULL)\s+)?JOIN\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:[A-Za-z_][A-Za-z0-9_]*\s+)?ON\s+([A-Za-z_][A-Za-z0-9_.]*)\s*([=<>!]+)\s*([A-Za-z_][A-Za-z0-9_.]*)'
            
            matches = re.finditer(join_pattern, sql_text, re.IGNORECASE)
            for match in matches:
                join_type = (match.group(1) or 'INNER').strip().upper()
                table = match.group(2).upper()
                left_col = match.group(3).upper()
                operator = match.group(4)
                right_col = match.group(5).upper()
                
                # 테이블명 분리
                left_table = left_col.split('.')[0] if '.' in left_col else ''
                left_column = left_col.split('.')[-1]
                right_table = right_col.split('.')[0] if '.' in right_col else ''
                right_column = right_col.split('.')[-1]
                
                join_info = JoinInfo(
                    left_table=left_table,
                    left_column=left_column,
                    operator=operator,
                    right_table=right_table,
                    right_column=right_column,
                    join_type=join_type,
                    confidence=0.8 if operator == '=' else 0.6
                )
                joins.append(join_info)
            
            # WHERE 절 조인 조건도 추출
            where_join_pattern = r'WHERE\s+.*?([A-Za-z_][A-Za-z0-9_.]*)\s*([=<>!]+)\s*([A-Za-z_][A-Za-z0-9_.]*)'
            matches = re.finditer(where_join_pattern, sql_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                left_col = match.group(1).upper()
                operator = match.group(2)
                right_col = match.group(3).upper()
                
                # 컬럼끼리 조인인지 확인 (둘 다 테이블.컬럼 형태)
                if '.' in left_col and '.' in right_col:
                    left_table = left_col.split('.')[0]
                    left_column = left_col.split('.')[-1]
                    right_table = right_col.split('.')[0]
                    right_column = right_col.split('.')[-1]
                    
                    join_info = JoinInfo(
                        left_table=left_table,
                        left_column=left_column,
                        operator=operator,
                        right_table=right_table,
                        right_column=right_column,
                        join_type='WHERE',
                        confidence=0.7 if operator == '=' else 0.5
                    )
                    joins.append(join_info)
        
        except Exception as e:
            pass  # 조인 추출 실패 시 빈 리스트 반환
        
        return joins
    
    def extract_filters(self, sql_text: str) -> List[FilterInfo]:
        """필터 조건 추출"""
        filters = []
        
        try:
            # WHERE 절 추출
            where_pattern = r'WHERE\s+(.*?)(?=GROUP|ORDER|HAVING|;|$)'
            match = re.search(where_pattern, sql_text, re.IGNORECASE | re.DOTALL)
            if not match:
                return filters
            
            where_clause = match.group(1).strip()
            
            # 개별 조건 추출
            # 간단한 조건: column operator value
            condition_pattern = r'([A-Za-z_][A-Za-z0-9_.]*)\s*(=|<>|!=|<|>|<=|>=|LIKE|IN|NOT IN)\s*([^AND^OR^)]+)'
            
            matches = re.finditer(condition_pattern, where_clause, re.IGNORECASE)
            for match in matches:
                column_ref = match.group(1).strip().upper()
                operator = match.group(2).strip().upper()
                value = match.group(3).strip()
                
                # 테이블명과 컬럼명 분리
                if '.' in column_ref:
                    table_name = column_ref.split('.')[0]
                    column_name = column_ref.split('.')[-1]
                else:
                    table_name = ''  # 테이블명 없음
                    column_name = column_ref
                
                # 값 정규화
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]  # 따옴표 제거
                
                # 항상 적용되는 필터인지 판단 (동적 태그 없는 경우)
                always_applied = True  # 기본적으로 SQL에서는 항상 적용
                confidence = 0.8
                
                # MyBatis 동적 태그가 있다면 신뢰도 낮춤
                if re.search(r'<if\s+test|<choose|<when', sql_text, re.IGNORECASE):
                    confidence = 0.6
                    always_applied = False
                
                filter_info = FilterInfo(
                    table_name=table_name,
                    column_name=column_name,
                    operator=operator,
                    value=value,
                    always_applied=always_applied,
                    confidence=confidence
                )
                filters.append(filter_info)
        
        except Exception as e:
            pass  # 필터 추출 실패 시 빈 리스트 반환
        
        return filters
    
    def detect_statement_type(self, sql_text: str) -> str:
        """SQL 문 타입 감지"""
        sql_upper = sql_text.strip().upper()
        
        if sql_upper.startswith('SELECT'):
            return 'select'
        elif sql_upper.startswith('INSERT'):
            return 'insert'
        elif sql_upper.startswith('UPDATE'):
            return 'update'
        elif sql_upper.startswith('DELETE'):
            return 'delete'
        elif sql_upper.startswith('CREATE OR REPLACE PROCEDURE') or sql_upper.startswith('PROCEDURE'):
            return 'procedure'
        elif sql_upper.startswith('CREATE OR REPLACE FUNCTION') or sql_upper.startswith('FUNCTION'):
            return 'function'
        elif sql_upper.startswith('CREATE'):
            return 'ddl'
        elif sql_upper.startswith('ALTER'):
            return 'ddl'
        elif sql_upper.startswith('DROP'):
            return 'ddl'
        else:
            return 'unknown'
    
    def parse_sql_content(self, content: str, file_path: str = '') -> List[Dict]:
        """SQL 내용 파싱하여 개별 문 분리"""
        statements = []
        
        try:
            # sqlparse로 문 분리
            parsed_statements = sqlparse.split(content)
            
            for i, stmt_text in enumerate(parsed_statements):
                if not stmt_text.strip():
                    continue
                
                stmt_type = self.detect_statement_type(stmt_text)
                fingerprint = self.create_fingerprint(stmt_text)
                
                # 테이블/컬럼 추출
                tables = self.extract_tables_from_sql(stmt_text) if self.extract_joins else []
                columns = self.extract_columns_from_sql(stmt_text) if self.extract_filters else []
                
                # 조인/필터 추출
                joins = self.extract_joins(stmt_text) if self.extract_joins else []
                filters = self.extract_filters(stmt_text) if self.extract_filters else []
                
                statement_info = {
                    'index': i,
                    'type': stmt_type,
                    'fingerprint': fingerprint,
                    'tables': tables,
                    'columns': columns,
                    'joins': [join.__dict__ for join in joins],
                    'filters': [filter_info.__dict__ for filter_info in filters],
                    'length': len(stmt_text),
                    'normalized': self.normalize_sql(stmt_text)[:500]  # 첫 500자만 저장
                }
                statements.append(statement_info)
        
        except Exception as e:
            # 파싱 실패 시 전체를 하나의 문으로 처리
            stmt_type = self.detect_statement_type(content)
            statements.append({
                'index': 0,
                'type': stmt_type,
                'fingerprint': 'error',
                'tables': [],
                'columns': [],
                'joins': [],
                'filters': [],
                'length': len(content),
                'normalized': content[:500]
            })
        
        return statements
    
    def parse_file(self, file_path: str, project_id: int) -> SQLParsingResult:
        """SQL 파일 파싱"""
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 기본 파일 정보
            file_stat = os.stat(file_path)
            file_info = {
                'project_id': project_id,
                'path': os.path.relpath(file_path),
                'language': 'sql',
                'hash': self.calculate_file_hash(content),
                'loc': self.count_lines(content),
                'mtime': datetime.fromtimestamp(file_stat.st_mtime)
            }
            
            # SQL 문 파싱
            statements = self.parse_sql_content(content, file_path)
            
            # 전체 파일에서 사용된 테이블/컬럼 수집
            all_tables = set()
            all_columns = set()
            all_joins = []
            all_filters = []
            
            for stmt in statements:
                all_tables.update(stmt['tables'])
                all_columns.update(stmt['columns'])
                all_joins.extend(stmt['joins'])
                all_filters.extend(stmt['filters'])
            
            # 신뢰도 계산
            confidence = 0.8
            if any(stmt['type'] == 'unknown' for stmt in statements):
                confidence = 0.6
            if any(stmt['fingerprint'] == 'error' for stmt in statements):
                confidence = 0.3
            
            return SQLParsingResult(
                file_info=file_info,
                statements=statements,
                joins=all_joins,
                filters=all_filters,
                tables_used=list(all_tables),
                columns_used=list(all_columns),
                confidence=confidence
            )
            
        except Exception as e:
            file_info['hash'] = 'error'
            file_info['loc'] = 0
            
            return SQLParsingResult(
                file_info=file_info,
                statements=[],
                joins=[],
                filters=[],
                tables_used=[],
                columns_used=[],
                confidence=0.0
            )
    
    def parse_directory(self, directory_path: str, project_id: int) -> List[SQLParsingResult]:
        """디렉토리 내 모든 SQL 파일 파싱"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if self.can_parse(file):
                    file_path = os.path.join(root, file)
                    try:
                        result = self.parse_file(file_path, project_id)
                        results.append(result)
                    except Exception as e:
                        print(f"Error parsing SQL {file_path}: {e}")
        
        return results


# Oracle PL/SQL 전용 파서 (향후 확장)
class PLSQLParser:
    """Oracle PL/SQL Stored Procedure/Function 파서 (향후 구현)"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def parse_procedure(self, plsql_content: str) -> Dict:
        """저장 프로시저 파싱 (향후 구현)"""
        # TODO: antlr-plsql 라이브러리 사용하여 PL/SQL AST 파싱
        return {}
    
    def parse_function(self, plsql_content: str) -> Dict:
        """저장 함수 파싱 (향후 구현)"""
        # TODO: PL/SQL 함수 구조 분석
        return {}
    
    def extract_table_operations(self, plsql_content: str) -> List[Dict]:
        """PL/SQL에서 테이블 작업 추출 (향후 구현)"""
        # TODO: CRUD 작업 및 의존성 분석
        return []


if __name__ == "__main__":
    # 테스트 코드
    parser = SQLParser()
    
    # 샘플 SQL 테스트
    sample_sql = """
    SELECT c.customer_id, c.name, o.order_id, o.amount
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.status = 'ACTIVE'
    AND o.order_date >= :startDate
    AND c.del_yn <> 'Y'
    ORDER BY o.order_date DESC
    """
    
    statements = parser.parse_sql_content(sample_sql)
    print(f"Parsed {len(statements)} statements")
    
    for stmt in statements:
        print(f"\nStatement Type: {stmt['type']}")
        print(f"Tables: {stmt['tables']}")
        print(f"Columns: {stmt['columns']}")
        print(f"Joins: {len(stmt['joins'])}")
        print(f"Filters: {len(stmt['filters'])}")
        print(f"Fingerprint: {stmt['fingerprint']}")
    
    # 디렉토리 파싱 테스트
    sample_project_path = "./PROJECT/sample-app"
    if os.path.exists(sample_project_path):
        results = parser.parse_directory(sample_project_path, project_id=1)
        print(f"\nParsed {len(results)} SQL files from directory")
    else:
        print("\nSample project not found")