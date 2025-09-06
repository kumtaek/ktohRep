"""
SQL 파서

SQL 파일을 파싱하여 쿼리, 테이블, 컬럼 정보를 추출합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class SqlParser:
    """SQL 파서"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"SqlParser")
        
        # SQL 파싱 패턴들
        self.patterns = {
            'select': r'SELECT\s+.*?FROM\s+(\w+)',
            'insert': r'INSERT\s+INTO\s+(\w+)',
            'update': r'UPDATE\s+(\w+)',
            'delete': r'DELETE\s+FROM\s+(\w+)',
            'create_table': r'CREATE\s+TABLE\s+(\w+)',
            'alter_table': r'ALTER\s+TABLE\s+(\w+)',
            'drop_table': r'DROP\s+TABLE\s+(\w+)',
            'join': r'JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'left_join': r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'right_join': r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'inner_join': r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'foreign_key': r'FOREIGN\s+KEY\s+\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)',
            'primary_key': r'PRIMARY\s+KEY\s*\(([^)]+)\)',
            'column': r'(\w+)\s+([A-Z]+(?:\([^)]+\))?)',
            'function': r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)',
            'procedure': r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)'
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """SQL 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path)
            
        except Exception as e:
            self.logger.error(f"SQL 파일 파싱 실패 {file_path}: {e}")
            return {}
    
    def parse_content(self, content: str, file_path: str = '') -> Dict[str, Any]:
        """SQL 코드 내용 파싱"""
        result = {
            'file_path': file_path,
            'queries': self._extract_queries(content),
            'tables': self._extract_tables(content),
            'joins': self._extract_joins(content),
            'foreign_keys': self._extract_foreign_keys(content),
            'primary_keys': self._extract_primary_keys(content),
            'columns': self._extract_columns(content),
            'functions': self._extract_functions(content),
            'procedures': self._extract_procedures(content)
        }
        
        return result
    
    def _extract_queries(self, content: str) -> List[Dict]:
        """SQL 쿼리 추출"""
        queries = []
        
        # 쿼리 타입별로 추출
        query_types = ['select', 'insert', 'update', 'delete']
        
        for query_type in query_types:
            pattern = self.patterns[query_type]
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                query_info = {
                    'type': query_type.upper(),
                    'table': match.group(1) if match.groups() else '',
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'content': match.group(0)
                }
                queries.append(query_info)
        
        return queries
    
    def _extract_tables(self, content: str) -> List[str]:
        """테이블명 추출"""
        tables = set()
        
        # DDL에서 테이블 추출
        ddl_patterns = ['create_table', 'alter_table', 'drop_table']
        for pattern_name in ddl_patterns:
            pattern = self.patterns[pattern_name]
            matches = re.findall(pattern, content, re.IGNORECASE)
            tables.update(matches)
        
        # DML에서 테이블 추출
        dml_patterns = ['select', 'insert', 'update', 'delete']
        for pattern_name in dml_patterns:
            pattern = self.patterns[pattern_name]
            matches = re.findall(pattern, content, re.IGNORECASE)
            tables.update(matches)
        
        return list(tables)
    
    def _extract_joins(self, content: str) -> List[Dict]:
        """JOIN 관계 추출"""
        joins = []
        
        # JOIN 타입별로 추출
        join_types = ['join', 'left_join', 'right_join', 'inner_join']
        
        for join_type in join_types:
            pattern = self.patterns[join_type]
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                join_info = {
                    'type': join_type.replace('_', ' ').upper(),
                    'table': match.group(1),
                    'condition': match.group(2) if len(match.groups()) > 1 else '',
                    'start_pos': match.start(),
                    'end_pos': match.end()
                }
                joins.append(join_info)
        
        return joins
    
    def _extract_foreign_keys(self, content: str) -> List[Dict]:
        """외래키 관계 추출"""
        foreign_keys = []
        matches = re.finditer(self.patterns['foreign_key'], content, re.IGNORECASE)
        
        for match in matches:
            fk_info = {
                'fk_column': match.group(1),
                'ref_table': match.group(2),
                'ref_column': match.group(3),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            foreign_keys.append(fk_info)
        
        return foreign_keys
    
    def _extract_primary_keys(self, content: str) -> List[Dict]:
        """기본키 추출"""
        primary_keys = []
        matches = re.finditer(self.patterns['primary_key'], content, re.IGNORECASE)
        
        for match in matches:
            pk_info = {
                'columns': [col.strip() for col in match.group(1).split(',')],
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            primary_keys.append(pk_info)
        
        return primary_keys
    
    def _extract_columns(self, content: str) -> List[Dict]:
        """컬럼 정보 추출"""
        columns = []
        matches = re.finditer(self.patterns['column'], content, re.IGNORECASE)
        
        for match in matches:
            column_info = {
                'name': match.group(1),
                'type': match.group(2),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            columns.append(column_info)
        
        return columns
    
    def _extract_functions(self, content: str) -> List[Dict]:
        """함수 정보 추출"""
        functions = []
        matches = re.finditer(self.patterns['function'], content, re.IGNORECASE)
        
        for match in matches:
            function_info = {
                'name': match.group(1),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            functions.append(function_info)
        
        return functions
    
    def _extract_procedures(self, content: str) -> List[Dict]:
        """프로시저 정보 추출"""
        procedures = []
        matches = re.finditer(self.patterns['procedure'], content, re.IGNORECASE)
        
        for match in matches:
            procedure_info = {
                'name': match.group(1),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            procedures.append(procedure_info)
        
        return procedures
