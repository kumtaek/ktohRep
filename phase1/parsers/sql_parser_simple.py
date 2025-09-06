"""
SQL Parser (Simple Regex-based)
간단한 정규식 기반 SQL 파서
"""

import re
import hashlib
from typing import Dict, List, Any, Set, Tuple
from parsers.base_parser import BaseParser

class SimpleSQLParser(BaseParser):
    """간단한 정규식 기반 SQL 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # SQL 문법 패턴 (정규식 기반)
        self.sql_patterns = {
            'select': re.compile(r'\bSELECT\s+(.+?)\s+FROM\s+([^\s,()]+)', re.IGNORECASE | re.DOTALL),
            'insert': re.compile(r'\bINSERT\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
            'update': re.compile(r'\bUPDATE\s+([^\s,()]+)', re.IGNORECASE),
            'delete': re.compile(r'\bDELETE\s+FROM\s+([^\s,()]+)', re.IGNORECASE),
            'truncate': re.compile(r'\bTRUNCATE\s+TABLE\s+([^\s,()]+)', re.IGNORECASE),
            'merge': re.compile(r'\bMERGE\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
        }
        
        # 테이블 및 컬럼 추출 패턴
        self.extraction_patterns = {
            'tables': [
                re.compile(r'\bFROM\s+([^\s,()]+?)(?=\s+(?:JOIN|WHERE|GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bJOIN\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\b(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s+JOIN\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bUPDATE\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bINSERT\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bDELETE\s+FROM\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bTRUNCATE\s+TABLE\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bMERGE\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
            ],
            'columns': [
                re.compile(r'\bSELECT\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
                re.compile(r'\b(\w+)\.(\w+)\b', re.IGNORECASE),
                re.compile(r'\b(\w+)\s+AS\s+(\w+)', re.IGNORECASE),
                re.compile(r'\bSET\s+(.+?)(?=\bWHERE\b|$)', re.IGNORECASE | re.DOTALL),
            ],
            'where_conditions': [
                re.compile(r'\bWHERE\s+(.+?)(?=\b(?:GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
            ],
            'joins': [
                re.compile(r'\b(?:INNER|LEFT|RIGHT|FULL|OUTER|CROSS)\s+JOIN\s+([^\s,()]+)\s+ON\s+(.+?)(?=\b(?:JOIN|WHERE|GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
            ],
        }
        
        # SQL 키워드
        self.sql_keywords = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'MERGE', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP', 'BY',
            'ORDER', 'HAVING', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'AS', 'CREATE', 'ALTER', 'DROP',
            'TABLE', 'VIEW', 'INDEX', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'DATABASE', 'SCHEMA', 'GRANT', 'REVOKE',
            'COMMIT', 'ROLLBACK', 'BEGIN', 'END', 'DECLARE', 'SET', 'VALUES', 'INTO', 'UNION', 'ALL', 'EXISTS', 'NOT',
            'NULL', 'LIKE', 'BETWEEN', 'IS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CASE', 'WHEN', 'THEN',
            'ELSE', 'END', 'LIMIT', 'OFFSET', 'FETCH', 'NEXT'
        }
    
    def parse(self, content: str, file_path: str = None) -> Dict[str, Any]:
        """SQL 파일 파싱"""
        try:
            result = {
                'file_path': file_path,
                'sql_units': [],
                'tables': set(),
                'columns': set(),
                'joins': [],
                'metadata': {
                    'file_type': 'sql',
                    'file_size': len(content),
                    'line_count': len(content.split('\n')),
                    'hash': hashlib.md5(content.encode()).hexdigest()
                }
            }
            
            # SQL 단위별 분석
            sql_statements = self._extract_sql_statements(content)
            
            for i, sql_statement in enumerate(sql_statements):
                sql_unit = self._parse_sql_statement(sql_statement, i + 1)
                if sql_unit:
                    result['sql_units'].append(sql_unit)
                    result['tables'].update(sql_unit.get('tables', []))
                    result['columns'].update(sql_unit.get('columns', []))
                    result['joins'].extend(sql_unit.get('joins', []))
            
            # Set을 List로 변환
            result['tables'] = list(result['tables'])
            result['columns'] = list(result['columns'])
            
            return result
            
        except Exception as e:
            print(f"SQL 파싱 오류: {e}")
            return None
    
    def _extract_sql_statements(self, content: str) -> List[str]:
        """SQL 문장 추출"""
        # 세미콜론으로 분리
        statements = []
        current_statement = ""
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):  # 주석 제거
                continue
            
            current_statement += line + " "
            
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def _parse_sql_statement(self, sql: str, statement_id: int) -> Dict[str, Any]:
        """SQL 문장 파싱"""
        try:
            sql_unit = {
                'id': statement_id,
                'sql': sql,
                'type': self._get_sql_type(sql),
                'tables': [],
                'columns': [],
                'joins': [],
                'where_conditions': [],
                'subqueries': []
            }
            
            # 테이블 추출
            for pattern in self.extraction_patterns['tables']:
                matches = pattern.findall(sql)
                for match in matches:
                    table_name = match.strip()
                    if table_name and not self._is_sql_keyword(table_name):
                        sql_unit['tables'].append(table_name)
            
            # 컬럼 추출
            for pattern in self.extraction_patterns['columns']:
                matches = pattern.findall(sql)
                for match in matches:
                    if isinstance(match, tuple):
                        for column in match:
                            column_name = column.strip()
                            if column_name and not self._is_sql_keyword(column_name):
                                sql_unit['columns'].append(column_name)
                    else:
                        column_name = match.strip()
                        if column_name and not self._is_sql_keyword(column_name):
                            sql_unit['columns'].append(column_name)
            
            # JOIN 조건 추출
            for pattern in self.extraction_patterns['joins']:
                matches = pattern.findall(sql)
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        join_info = {
                            'table': match[0].strip(),
                            'condition': match[1].strip()
                        }
                        sql_unit['joins'].append(join_info)
            
            # WHERE 조건 추출
            for pattern in self.extraction_patterns['where_conditions']:
                matches = pattern.findall(sql)
                for match in matches:
                    sql_unit['where_conditions'].append(match.strip())
            
            return sql_unit
            
        except Exception as e:
            print(f"SQL 문장 파싱 오류: {e}")
            return None
    
    def _get_sql_type(self, sql: str) -> str:
        """SQL 타입 판별"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('TRUNCATE'):
            return 'TRUNCATE'
        elif sql_upper.startswith('MERGE'):
            return 'MERGE'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        else:
            return 'UNKNOWN'
    
    def _is_sql_keyword(self, word: str) -> bool:
        """SQL 키워드 판별"""
        return word.upper() in self.sql_keywords
    
    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 반환"""
        return ['.sql', '.ddl', '.dml']
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입 반환"""
        return 'sql'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문 파싱"""
        file_path = context.get('file_path', None)
        
        # Java 파일인 경우 SQL 문자열 추출
        if file_path and file_path.endswith('.java'):
            return self._extract_sql_from_java(sql_content, file_path)
        
        return self.parse(sql_content, file_path)
    
    def _extract_sql_from_java(self, java_content: str, file_path: str) -> Dict[str, Any]:
        """Java 파일에서 SQL 문자열 추출"""
        sql_units = []
        
        # Java 파일에서 SQL 문자열 패턴 찾기 (엄격한 패턴)
        sql_string_patterns = [
            # String sql = "SELECT ..."; (명시적 변수 할당만)
            r'String\s+\w+\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        ]
        
        for pattern in sql_string_patterns:
            matches = re.finditer(pattern, java_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                sql_text = match.group(1)
                if sql_text and len(sql_text.strip()) > 10:  # 최소 길이 체크
                    # SQL 타입 결정
                    sql_type = 'unknown'
                    for stmt_type, pattern_obj in self.sql_patterns.items():
                        if pattern_obj.search(sql_text):
                            sql_type = stmt_type
                            break
                    
                    sql_units.append({
                        'id': f'java_sql_{len(sql_units)}',
                        'type': sql_type,
                        'sql': sql_text.strip(),
                        'start_line': java_content[:match.start()].count('\n') + 1,
                        'end_line': java_content[:match.end()].count('\n') + 1,
                        'tables': self._extract_tables_from_sql(sql_text),
                        'columns': self._extract_columns_from_sql(sql_text),
                        'joins': self._extract_joins_from_sql(sql_text),
                        'filters': self._extract_filters_from_sql(sql_text)
                    })
        
        return {
            'sql_units': sql_units,
            'tables': list(set([table for unit in sql_units for table in unit.get('tables', [])])),
            'columns': list(set([col for unit in sql_units for col in unit.get('columns', [])])),
            'joins': list(set([join for unit in sql_units for join in unit.get('joins', [])])),
            'filters': list(set([filter_ for unit in sql_units for filter_ in unit.get('filters', [])]))
        }
    
    def _extract_joins_from_sql(self, sql: str) -> List[str]:
        """SQL에서 조인 정보 추출"""
        joins = []
        
        # JOIN 패턴들
        join_patterns = [
            r'JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'OUTER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        ]
        
        for pattern in join_patterns:
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                table = match.group(1)
                left_col = match.group(2)
                right_col = match.group(3)
                joins.append(f"{table}:{left_col}={right_col}")
        
        return joins
    
    def _extract_filters_from_sql(self, sql: str) -> List[str]:
        """SQL에서 필터 조건 추출"""
        filters = []
        
        # WHERE 절 패턴
        where_pattern = r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+HAVING|$)'
        where_match = re.search(where_pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if where_match:
            where_clause = where_match.group(1)
            # 개별 조건들 추출
            conditions = re.split(r'\s+AND\s+|\s+OR\s+', where_clause, flags=re.IGNORECASE)
            for condition in conditions:
                condition = condition.strip()
                if condition:
                    filters.append(condition)
        
        return filters
