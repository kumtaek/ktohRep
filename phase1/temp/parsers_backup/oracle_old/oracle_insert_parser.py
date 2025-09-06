"""
Oracle INSERT 쿼리 파서
INSERT 쿼리에서 테이블, 컬럼 등을 추출합니다.
"""

import re
from typing import Dict, List, Any
from phase1.parsers.base_parser import BaseParser

class OracleInsertParser(BaseParser):
    """Oracle INSERT 쿼리 전용 파서"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def _get_parser_type(self) -> str:
        return 'oracle_insert'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'tables': self._extract_tables(content),
            'columns': self._extract_columns(content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }
        return result

    def _extract_tables(self, content: str) -> List[str]:
        tables = []
        pattern = r'\bINSERT\s+INTO\s+(\w+(?:\.\w+)?)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        tables.extend(matches)
        return tables

    def _extract_columns(self, content: str) -> List[str]:
        columns = []
        pattern = r'\(\s*([^)]+)\s*\)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            cols = [col.strip() for col in match.split(',')]
            columns.extend(cols)
        return columns

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'file_path': context.get('file_path', ''),
            'file_name': context.get('file_name', ''),
            'parser_type': self._get_parser_type(),
            'confidence': self.confidence
        }
