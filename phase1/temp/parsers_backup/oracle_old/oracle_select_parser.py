"""
Oracle SELECT 쿼리 파서
SELECT 쿼리에서 테이블, 컬럼, 조건, 서브쿼리 등을 추출합니다.
재현율을 높이기 위해 다양한 패턴을 처리합니다.
"""

import re
from typing import Dict, List, Any, Set
from phase1.parsers.base_parser import BaseParser
from phase1.utils.table_alias_resolver import get_table_alias_resolver

class OracleSelectParser(BaseParser):
    """Oracle SELECT 쿼리 전용 파서 - 재현율 우선"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Oracle 전용 키워드 및 함수
        self.oracle_keywords = {
            'DUAL', 'ROWNUM', 'ROWID', 'LEVEL', 'CONNECT_BY_ROOT',
            'NVL', 'NVL2', 'DECODE', 'CASE', 'TO_CHAR', 'TO_DATE', 'TO_NUMBER',
            'SUBSTR', 'INSTR', 'LENGTH', 'LOWER', 'UPPER', 'TRIM', 'LTRIM', 'RTRIM',
            'ROUND', 'TRUNC', 'MOD', 'POWER', 'SQRT', 'ABS', 'CEIL', 'FLOOR',
            'SYSDATE', 'ADD_MONTHS', 'MONTHS_BETWEEN', 'LAST_DAY', 'NEXT_DAY',
            'EXTRACT', 'GREATEST', 'LEAST', 'NULLIF', 'COALESCE'
        }

        # SELECT 쿼리 패턴들 (재현율 우선)
        self.select_patterns = {
            'tables': [
                re.compile(r'\bFROM\s+([^JOIN]+?)(?=\b(?:JOIN|WHERE|GROUP|ORDER|HAVING|CONNECT\s+BY|START\s+WITH|$))', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bJOIN\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\b(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s+JOIN\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\bWITH\s+(\w+)\s+AS\s*\(', re.IGNORECASE),  # CTE
            ],
            'columns': [
                re.compile(r'\bSELECT\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
                re.compile(r'\b(\w+)\.(\w+)\b', re.IGNORECASE),
                re.compile(r'\b(\w+)\s+AS\s+(\w+)', re.IGNORECASE),  # 별칭
            ],
            'where_conditions': [
                re.compile(r'\bWHERE\s+(.+?)(?=\b(?:GROUP|ORDER|HAVING|CONNECT\s+BY|START\s+WITH|$))', re.IGNORECASE | re.DOTALL),
            ],
            'subqueries': [
                re.compile(r'\(\s*SELECT\s+(.+?)\s*\)', re.IGNORECASE | re.DOTALL),
                re.compile(r'\(\s*SELECT\s+(.+?)\s+FROM\s+(.+?)\s*\)', re.IGNORECASE | re.DOTALL),
            ],
            'inline_views': [
                re.compile(r'\bFROM\s*\(\s*SELECT\s+(.+?)\s*\)\s+(\w+)', re.IGNORECASE | re.DOTALL),
            ],
            'oracle_specific': [
                re.compile(r'\bCONNECT\s+BY\s+(?:NOCYCLE\s+)?(.+?)(?=\bWHERE\b|\bORDER\s+BY\b|\bGROUP\s+BY\b|$)', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bSTART\s+WITH\s+(.+?)(?=\bCONNECT\s+BY\b|\bWHERE\b|\bORDER\s+BY\b|\bGROUP\s+BY\b|$)', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bMODEL\s+(.+?)(?=\bWHERE\b|\bORDER\s+BY\b|\bGROUP\s+BY\b|$)', re.IGNORECASE | re.DOTALL),
            ]
        }

    def _get_parser_type(self) -> str:
        return 'oracle_select'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        SELECT 쿼리를 파싱하여 메타데이터 추출 (재현율 우선)

        Args:
            content: SELECT 쿼리
            context: 컨텍스트 정보

        Returns:
            파싱된 메타데이터
        """
        # 1. 기본 SQL 처리
        processed_content = content
        
        # 2. 테이블 별칭 해석
        alias_resolver = get_table_alias_resolver(context.get('default_schema', 'DEFAULT'))
        alias_mapping = alias_resolver.extract_table_alias_mapping(processed_content)
        
        # 3. 정규화
        normalized_content = self._normalize_content(processed_content)

        result = {
            'tables': self._extract_tables_aggressive(normalized_content),
            'columns': self._extract_columns_aggressive(normalized_content),
            'where_conditions': self._extract_where_conditions_aggressive(normalized_content),
            'subqueries': self._extract_subqueries_aggressive(normalized_content),
            'inline_views': self._extract_inline_views_aggressive(normalized_content),
            'joins': self._extract_joins_aggressive(normalized_content),
            'oracle_specific': self._extract_oracle_specific_constructs(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence,
            # 동적 쿼리 및 별칭 정보 추가
            'dynamic_blocks': dynamic_result.dynamic_blocks,
            'alias_mapping': alias_mapping,
            'original_sql': content,
            'processed_sql': processed_content
        }

        return result

    def _extract_tables_aggressive(self, content: str) -> List[str]:
        """테이블 추출 (재현율 우선)"""
        tables = set()
        for pattern in self.select_patterns['tables']:
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    tables.update(match)
                else:
                    tables.add(match)
        return list(tables)

    def _extract_columns_aggressive(self, content: str) -> List[str]:
        """컬럼 추출 (재현율 우선)"""
        columns = set()
        for pattern in self.select_patterns['columns']:
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    columns.update(match)
                else:
                    columns.add(match)
        return list(columns)

    def _extract_where_conditions_aggressive(self, content: str) -> List[str]:
        """WHERE 조건 추출 (재현율 우선)"""
        conditions = []
        for pattern in self.select_patterns['where_conditions']:
            matches = pattern.findall(content)
            conditions.extend(matches)
        return conditions

    def _extract_subqueries_aggressive(self, content: str) -> List[str]:
        """서브쿼리 추출 (재현율 우선)"""
        subqueries = []
        for pattern in self.select_patterns['subqueries']:
            matches = pattern.findall(content)
            subqueries.extend(matches)
        return subqueries

    def _extract_inline_views_aggressive(self, content: str) -> List[str]:
        """인라인 뷰 추출 (재현율 우선)"""
        views = []
        for pattern in self.select_patterns['inline_views']:
            matches = pattern.findall(content)
            views.extend(matches)
        return views

    def _extract_joins_aggressive(self, content: str) -> List[str]:
        """JOIN 추출 (재현율 우선)"""
        joins = []
        # JOIN 패턴들
        join_patterns = [
            r'\b(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s+JOIN\s+(\w+(?:\.\w+)?)',
            r'\bJOIN\s+(\w+(?:\.\w+)?)',
            r'\b(\w+(?:\.\w+)?)\s+JOIN\s+(\w+(?:\.\w+)?)'
        ]
        
        for pattern in join_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            joins.extend(matches)
        
        return joins

    def _extract_oracle_specific_constructs(self, content: str) -> List[str]:
        """Oracle 전용 구문 추출 (재현율 우선)"""
        constructs = []
        for pattern in self.select_patterns['oracle_specific']:
            matches = pattern.findall(content)
            constructs.extend(matches)
        return constructs

    def _normalize_content(self, content: str) -> str:
        """쿼리 내용 정규화"""
        # 주석 제거
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 공백 정규화
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """파일 메타데이터 추출"""
        return {
            'file_path': context.get('file_path', ''),
            'file_name': context.get('file_name', ''),
            'parser_type': self._get_parser_type(),
            'confidence': self.confidence
        }
