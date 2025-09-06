"""
Oracle MERGE 쿼리 파서
MERGE 쿼리에서 테이블, 컬럼, 조건 등을 추출합니다.
"""

import re
from typing import Dict, List, Any
from phase1.parsers.base_parser import BaseParser

class OracleMergeParser(BaseParser):
    """Oracle MERGE 쿼리 전용 파서"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def _get_parser_type(self) -> str:
        return 'oracle_merge'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'tables': self._extract_tables(content),
            'columns': self._extract_columns(content),
            'where_conditions': self._extract_where_conditions(content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }
        return result

    def _extract_tables(self, content: str) -> List[str]:
        tables = []
        # MERGE INTO table 패턴
        pattern = r'\bMERGE\s+INTO\s+(\w+(?:\.\w+)?)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        tables.extend(matches)
        return tables

    def _extract_columns(self, content: str) -> List[str]:
        columns = []
        # UPDATE SET column = value 패턴
        pattern = r'\bSET\s+(\w+(?:\.\w+)?)\s*='
        matches = re.findall(pattern, content, re.IGNORECASE)
        columns.extend(matches)
        return columns

    def _extract_where_conditions(self, content: str) -> List[str]:
        conditions = []
        # WHERE 절 패턴
        pattern = r'\bWHERE\s+(.+?)(?=\bUPDATE\b|\bINSERT\b|$)'
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
