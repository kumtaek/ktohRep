"""
Oracle Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle SQL 파서
- CRUD 및 TRUNCATE 지원
- Oracle 특화 문법 지원
- 중복 방지 및 정확도 향상
- Oracle Database 19c 공식 문서 기반 패턴 매칭
"""

import re
import hashlib
from typing import Dict, List, Any, Set, Tuple
from phase1.parsers.base_parser import BaseParser

class OracleParserContext7(BaseParser):
    """
    Oracle Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle SQL 파서
    - CRUD 및 TRUNCATE 지원
    - Oracle 특화 문법 지원
    - 중복 방지 및 정확도 향상
    - Oracle Database 19c 공식 문서 기반 패턴 매칭
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Oracle SQL 문법 패턴 (Context7 기반)
        self.sql_patterns = {
            'select': re.compile(r'\bSELECT\s+(.+?)\s+FROM\s+([^\s,()]+)', re.IGNORECASE | re.DOTALL),
            'insert': re.compile(r'\bINSERT\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
            'update': re.compile(r'\bUPDATE\s+([^\s,()]+)', re.IGNORECASE),
            'delete': re.compile(r'\bDELETE\s+FROM\s+([^\s,()]+)', re.IGNORECASE),
            'truncate': re.compile(r'\bTRUNCATE\s+TABLE\s+([^\s,()]+)', re.IGNORECASE),
            'merge': re.compile(r'\bMERGE\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
        }
        
        # Oracle 특화 문법 패턴
        self.oracle_patterns = {
            'dual': re.compile(r'\bFROM\s+DUAL\b', re.IGNORECASE),
            'rownum': re.compile(r'\bROWNUM\b', re.IGNORECASE),
            'connect_by': re.compile(r'\bCONNECT\s+BY\b', re.IGNORECASE),
            'start_with': re.compile(r'\bSTART\s+WITH\b', re.IGNORECASE),
            'hierarchical': re.compile(r'\bPRIOR\b', re.IGNORECASE),
            'analytic_functions': re.compile(r'\b(?:ROW_NUMBER|RANK|DENSE_RANK|LAG|LEAD|FIRST_VALUE|LAST_VALUE)\s*\(', re.IGNORECASE),
            'pivot': re.compile(r'\bPIVOT\s*\(', re.IGNORECASE),
            'unpivot': re.compile(r'\bUNPIVOT\s*\(', re.IGNORECASE),
            'case_expressions': re.compile(r'\bCASE\s+WHEN\b', re.IGNORECASE),
            'decode': re.compile(r'\bDECODE\s*\(', re.IGNORECASE),
            'nvl': re.compile(r'\bNVL\s*\(', re.IGNORECASE),
            'to_char': re.compile(r'\bTO_CHAR\s*\(', re.IGNORECASE),
            'to_date': re.compile(r'\bTO_DATE\s*\(', re.IGNORECASE),
            'to_number': re.compile(r'\bTO_NUMBER\s*\(', re.IGNORECASE),
            'sysdate': re.compile(r'\bSYSDATE\b', re.IGNORECASE),
            'systimestamp': re.compile(r'\bSYSTIMESTAMP\b', re.IGNORECASE),
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
            'subqueries': [
                re.compile(r'\(\s*SELECT\s+.*?\s+FROM\s+.*?\s*\)', re.IGNORECASE | re.DOTALL),
            ],
        }
        
        # Oracle 키워드
        self.oracle_keywords = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'MERGE', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP', 'BY',
            'ORDER', 'HAVING', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'AS', 'CREATE', 'ALTER', 'DROP',
            'TABLE', 'VIEW', 'INDEX', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'DATABASE', 'SCHEMA', 'GRANT', 'REVOKE',
            'COMMIT', 'ROLLBACK', 'BEGIN', 'END', 'DECLARE', 'SET', 'VALUES', 'INTO', 'UNION', 'ALL', 'EXISTS', 'NOT',
            'NULL', 'LIKE', 'BETWEEN', 'IS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'CASE', 'WHEN', 'THEN',
            'ELSE', 'END', 'LIMIT', 'OFFSET', 'FETCH', 'NEXT', 'ROWNUM', 'DUAL', 'WITH', 'AS', 'CONNECT', 'START',
            'PRIOR', 'LEVEL', 'SYSDATE', 'SYSTIMESTAMP', 'TO_CHAR', 'TO_DATE', 'TO_NUMBER', 'NVL', 'DECODE', 'CAST',
            'CONVERT', 'TRUNC', 'ROUND', 'SUBSTR', 'INSTR', 'LENGTH', 'REPLACE', 'LPAD', 'RPAD', 'LTRIM', 'RTRIM',
            'UPPER', 'LOWER', 'INITCAP', 'ADD_MONTHS', 'LAST_DAY', 'NEXT_DAY', 'MONTHS_BETWEEN', 'EXTRACT',
            'XMLTABLE', 'XMLAGG', 'XMLQUERY', 'XMLSERIALIZE', 'JSON_TABLE', 'JSON_QUERY', 'JSON_VALUE', 'JSON_OBJECT',
            'JSON_ARRAY', 'JSON_EXISTS', 'JSON_TEXTCONTAINS', 'FOR', 'EACH', 'LOOP', 'WHILE', 'IF', 'THEN', 'ELSIF',
            'RETURN', 'PACKAGE', 'BODY', 'SPEC', 'TYPE', 'RECORD', 'CURSOR', 'OPEN', 'CLOSE', 'FETCH', 'EXCEPTION',
            'PRAGMA', 'AUTONOMOUS_TRANSACTION', 'NOCOPY', 'REF', 'SYS_REFCURSOR', 'PIVOT', 'UNPIVOT', 'ROW_NUMBER',
            'RANK', 'DENSE_RANK', 'LAG', 'LEAD', 'FIRST_VALUE', 'LAST_VALUE', 'PARTITION', 'OVER', 'WINDOW'
        }
        
        # 중복 방지를 위한 집합
        self._processed_sql_ids = set()
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'oracle'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Oracle SQL 파일을 파싱하여 메타데이터 추출 (Context7 기반)
        
        Args:
            content: Oracle SQL 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 1. 정규화 (주석 제거)
        normalized_content = self._remove_comments(content)
        
        # 2. 중복 방지를 위한 집합 초기화
        self._processed_sql_ids.clear()
        
        result = {
            'sql_units': self._extract_sql_statements_enhanced(normalized_content),
            'tables': self._extract_tables_enhanced(normalized_content),
            'columns': self._extract_columns_enhanced(normalized_content),
            'where_conditions': self._extract_where_conditions_enhanced(normalized_content),
            'joins': self._extract_joins_enhanced(normalized_content),
            'subqueries': self._extract_subqueries_enhanced(normalized_content),
            'oracle_features': self._extract_oracle_features_enhanced(normalized_content),
            'file_metadata': {'default_schema': context.get('default_schema', 'DEFAULT')},
            'confidence': 0.95,  # 향상된 신뢰도
            'original_content': content,
            'processed_content': normalized_content
        }
        
        return result
    
    def _extract_sql_statements_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced SQL 구문 추출 (중복 방지)"""
        sql_statements = []
        
        # 1. SELECT 구문 추출
        select_matches = self.sql_patterns['select'].finditer(content)
        for match in select_matches:
            sql_unit = self._process_sql_statement(match, 'select', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 2. INSERT 구문 추출
        insert_matches = self.sql_patterns['insert'].finditer(content)
        for match in insert_matches:
            sql_unit = self._process_sql_statement(match, 'insert', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 3. UPDATE 구문 추출
        update_matches = self.sql_patterns['update'].finditer(content)
        for match in update_matches:
            sql_unit = self._process_sql_statement(match, 'update', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 4. DELETE 구문 추출
        delete_matches = self.sql_patterns['delete'].finditer(content)
        for match in delete_matches:
            sql_unit = self._process_sql_statement(match, 'delete', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 5. TRUNCATE 구문 추출
        truncate_matches = self.sql_patterns['truncate'].finditer(content)
        for match in truncate_matches:
            sql_unit = self._process_sql_statement(match, 'truncate', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 6. MERGE 구문 추출
        merge_matches = self.sql_patterns['merge'].finditer(content)
        for match in merge_matches:
            sql_unit = self._process_sql_statement(match, 'merge', content)
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        return sql_statements
    
    def _process_sql_statement(self, match: re.Match, stmt_type: str, content: str) -> Dict[str, Any]:
        """SQL 구문 처리"""
        sql_content = match.group(0)
        
        # SQL 정규화
        normalized_sql = self._normalize_sql(sql_content)
        
        # 고유 ID 생성
        unique_id = self._generate_unique_id(stmt_type, normalized_sql)
        
        return {
            'type': stmt_type,
            'unique_id': unique_id,
            'sql_content': sql_content.strip(),
            'normalized_sql': normalized_sql,
            'full_text': sql_content,
            'tables': self._extract_tables_from_sql(sql_content),
            'columns': self._extract_columns_from_sql(sql_content),
            'where_conditions': self._extract_where_conditions_from_sql(sql_content),
            'joins': self._extract_joins_from_sql(sql_content),
            'subqueries': self._extract_subqueries_from_sql(sql_content),
            'oracle_features': self._extract_oracle_features_from_sql(sql_content),
            'line_number': self._get_line_number(content, match.start())
        }
    
    def _generate_unique_id(self, stmt_type: str, normalized_sql: str) -> str:
        """고유 ID 생성"""
        content_hash = hashlib.md5(normalized_sql.encode('utf-8')).hexdigest()[:8]
        return f"{stmt_type}_{content_hash}"
    
    def _is_unique_sql_unit(self, sql_unit: Dict[str, Any]) -> bool:
        """중복 SQL Unit 체크"""
        unique_id = sql_unit.get('unique_id', '')
        
        if unique_id in self._processed_sql_ids:
            return False
        
        self._processed_sql_ids.add(unique_id)
        return True
    
    def _get_line_number(self, content: str, position: int) -> int:
        """위치에 해당하는 라인 번호 반환"""
        return content[:position].count('\n') + 1
    
    def _extract_tables_enhanced(self, content: str) -> List[str]:
        """Enhanced 테이블명 추출"""
        tables = set()
        
        # 모든 SQL 구문에서 테이블 추출
        for sql_stmt in self._extract_sql_statements_enhanced(content):
            tables.update(sql_stmt.get('tables', []))
        
        return list(tables)
    
    def _extract_columns_enhanced(self, content: str) -> List[str]:
        """Enhanced 컬럼명 추출"""
        columns = set()
        
        # 모든 SQL 구문에서 컬럼 추출
        for sql_stmt in self._extract_sql_statements_enhanced(content):
            columns.update(sql_stmt.get('columns', []))
        
        return list(columns)
    
    def _extract_where_conditions_enhanced(self, content: str) -> List[str]:
        """Enhanced WHERE 조건 추출"""
        conditions = set()
        
        for pattern in self.extraction_patterns['where_conditions']:
            matches = pattern.finditer(content)
            for match in matches:
                condition = match.group(1).strip()
                if condition and not self._is_sql_keyword(condition):
                    conditions.add(condition)
        
        return list(conditions)
    
    def _extract_joins_enhanced(self, content: str) -> List[Dict[str, str]]:
        """Enhanced JOIN 정보 추출"""
        joins = []
        
        for pattern in self.extraction_patterns['joins']:
            matches = pattern.finditer(content)
            for match in matches:
                table = match.group(1).strip()
                condition = match.group(2).strip()
                if table and condition:
                    joins.append({
                        'table': table,
                        'condition': condition
                    })
        
        return joins
    
    def _extract_subqueries_enhanced(self, content: str) -> List[str]:
        """Enhanced 서브쿼리 추출"""
        subqueries = set()
        
        for pattern in self.extraction_patterns['subqueries']:
            matches = pattern.finditer(content)
            for match in matches:
                subquery = match.group(0).strip()
                if subquery:
                    subqueries.add(subquery)
        
        return list(subqueries)
    
    def _extract_oracle_features_enhanced(self, content: str) -> Dict[str, List[str]]:
        """Enhanced Oracle 특화 기능 추출"""
        features = {
            'dual_usage': [],
            'rownum_usage': [],
            'hierarchical_queries': [],
            'analytic_functions': [],
            'pivot_operations': [],
            'case_expressions': [],
            'oracle_functions': []
        }
        
        # DUAL 테이블 사용
        dual_matches = self.oracle_patterns['dual'].finditer(content)
        for match in dual_matches:
            features['dual_usage'].append(match.group(0))
        
        # ROWNUM 사용
        rownum_matches = self.oracle_patterns['rownum'].finditer(content)
        for match in rownum_matches:
            features['rownum_usage'].append(match.group(0))
        
        # 계층 쿼리
        connect_matches = self.oracle_patterns['connect_by'].finditer(content)
        for match in connect_matches:
            features['hierarchical_queries'].append(match.group(0))
        
        # 분석 함수
        analytic_matches = self.oracle_patterns['analytic_functions'].finditer(content)
        for match in analytic_matches:
            features['analytic_functions'].append(match.group(0))
        
        # PIVOT/UNPIVOT
        pivot_matches = self.oracle_patterns['pivot'].finditer(content)
        for match in pivot_matches:
            features['pivot_operations'].append(match.group(0))
        
        unpivot_matches = self.oracle_patterns['unpivot'].finditer(content)
        for match in unpivot_matches:
            features['pivot_operations'].append(match.group(0))
        
        # CASE 표현식
        case_matches = self.oracle_patterns['case_expressions'].finditer(content)
        for match in case_matches:
            features['case_expressions'].append(match.group(0))
        
        # Oracle 함수들
        oracle_functions = ['decode', 'nvl', 'to_char', 'to_date', 'to_number', 'sysdate', 'systimestamp']
        for func in oracle_functions:
            pattern = self.oracle_patterns.get(func)
            if pattern:
                matches = pattern.finditer(content)
                for match in matches:
                    features['oracle_functions'].append(match.group(0))
        
        return features
    
    def _extract_tables_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 테이블명 추출"""
        tables = set()
        
        for pattern in self.extraction_patterns['tables']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                table_ref = match.group(1).strip()
                # 스키마.테이블 형태에서 테이블명만 추출
                if '.' in table_ref:
                    table_ref = table_ref.split('.')[-1]
                # 특수문자 제거
                table_ref = re.sub(r'[^\w]', '', table_ref)
                if table_ref and not self._is_sql_keyword(table_ref):
                    tables.add(table_ref.upper())
        
        return list(tables)
    
    def _extract_columns_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 컬럼명 추출"""
        columns = set()
        
        for pattern in self.extraction_patterns['columns']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                if len(match.groups()) >= 2:
                    table_name = match.group(1)
                    column_name = match.group(2)
                    if not self._is_sql_keyword(table_name) and not self._is_sql_keyword(column_name):
                        columns.add(f"{table_name.upper()}.{column_name.upper()}")
        
        return list(columns)
    
    def _extract_where_conditions_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 WHERE 조건 추출"""
        conditions = set()
        
        for pattern in self.extraction_patterns['where_conditions']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                condition = match.group(1).strip()
                if condition and not self._is_sql_keyword(condition):
                    conditions.add(condition)
        
        return list(conditions)
    
    def _extract_joins_from_sql(self, sql_content: str) -> List[Dict[str, str]]:
        """SQL 내용에서 JOIN 정보 추출"""
        joins = []
        
        for pattern in self.extraction_patterns['joins']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                table = match.group(1).strip()
                condition = match.group(2).strip()
                if table and condition:
                    joins.append({
                        'table': table,
                        'condition': condition
                    })
        
        return joins
    
    def _extract_subqueries_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 서브쿼리 추출"""
        subqueries = set()
        
        for pattern in self.extraction_patterns['subqueries']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                subquery = match.group(0).strip()
                if subquery:
                    subqueries.add(subquery)
        
        return list(subqueries)
    
    def _extract_oracle_features_from_sql(self, sql_content: str) -> Dict[str, List[str]]:
        """SQL 내용에서 Oracle 특화 기능 추출"""
        features = {
            'dual_usage': [],
            'rownum_usage': [],
            'hierarchical_queries': [],
            'analytic_functions': [],
            'pivot_operations': [],
            'case_expressions': [],
            'oracle_functions': []
        }
        
        # DUAL 테이블 사용
        dual_matches = self.oracle_patterns['dual'].finditer(sql_content)
        for match in dual_matches:
            features['dual_usage'].append(match.group(0))
        
        # ROWNUM 사용
        rownum_matches = self.oracle_patterns['rownum'].finditer(sql_content)
        for match in rownum_matches:
            features['rownum_usage'].append(match.group(0))
        
        # 계층 쿼리
        connect_matches = self.oracle_patterns['connect_by'].finditer(sql_content)
        for match in connect_matches:
            features['hierarchical_queries'].append(match.group(0))
        
        # 분석 함수
        analytic_matches = self.oracle_patterns['analytic_functions'].finditer(sql_content)
        for match in analytic_matches:
            features['analytic_functions'].append(match.group(0))
        
        # PIVOT/UNPIVOT
        pivot_matches = self.oracle_patterns['pivot'].finditer(sql_content)
        for match in pivot_matches:
            features['pivot_operations'].append(match.group(0))
        
        unpivot_matches = self.oracle_patterns['unpivot'].finditer(sql_content)
        for match in unpivot_matches:
            features['pivot_operations'].append(match.group(0))
        
        # CASE 표현식
        case_matches = self.oracle_patterns['case_expressions'].finditer(sql_content)
        for match in case_matches:
            features['case_expressions'].append(match.group(0))
        
        # Oracle 함수들
        oracle_functions = ['decode', 'nvl', 'to_char', 'to_date', 'to_number', 'sysdate', 'systimestamp']
        for func in oracle_functions:
            pattern = self.oracle_patterns.get(func)
            if pattern:
                matches = pattern.finditer(sql_content)
                for match in matches:
                    features['oracle_functions'].append(match.group(0))
        
        return features
    
    def _remove_comments(self, content: str) -> str:
        """Oracle SQL 주석 제거"""
        # -- 스타일 주석 제거
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        # /* ... */ 스타일 주석 제거
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _is_sql_keyword(self, word: str) -> bool:
        """주어진 단어가 Oracle SQL 키워드인지 확인"""
        return word.upper() in self.oracle_keywords
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)





