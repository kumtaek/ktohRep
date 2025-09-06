"""
Oracle DELETE 쿼리 파서
DELETE 쿼리에서 테이블, 조건 등을 추출합니다.
"""

import re
from typing import Dict, List, Any
from phase1.parsers.base_parser import BaseParser

class OracleDeleteParser(BaseParser):
    """Oracle DELETE 쿼리 전용 파서"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def _get_parser_type(self) -> str:
        return 'oracle_delete'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'tables': self._extract_tables(content),
            'where_conditions': self._extract_where_conditions(content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }
        return result

    def _extract_tables(self, content: str) -> List[str]:
        tables = []
        pattern = r'\bDELETE\s+FROM\s+(\w+(?:\.\w+)?)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        tables.extend(matches)
        return tables

    def _extract_where_conditions(self, content: str) -> List[str]:
        conditions = []
        pattern = r'\bWHERE\s+(.+?)(?=\bORDER\s+BY\b|$)'
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        conditions.extend(matches)
        return conditions

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'file_path': context.get('file_path', ''),
            'file_name': context.get('file_name', ''),
            'parser_type': self._get_parser_type(),
            'confidence': self.confidence
        }
