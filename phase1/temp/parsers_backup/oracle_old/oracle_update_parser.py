"""
Oracle UPDATE 쿼리 파서
UPDATE 쿼리에서 테이블, 컬럼, 조건 등을 추출합니다.
"""

import re
from typing import Dict, List, Any
from parsers.base_parser import BaseParser

class OracleUpdateParser(BaseParser):
    """Oracle UPDATE 쿼리 전용 파서"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def _get_parser_type(self) -> str:
        return 'oracle_update'

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        UPDATE 쿼리를 파싱하여 메타데이터 추출

        Args:
            content: UPDATE 쿼리
            context: 컨텍스트 정보

        Returns:
            파싱된 메타데이터
        """
        result = {
            'tables': self._extract_tables(content),
            'columns': self._extract_columns(content),
            'where_conditions': self._extract_where_conditions(content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }

        return result

    def _extract_tables(self, content: str) -> List[str]:
        """테이블 추출"""
        tables = []
        # UPDATE table_name 패턴
        pattern = r'\bUPDATE\s+(\w+(?:\.\w+)?)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        tables.extend(matches)
        return tables

    def _extract_columns(self, content: str) -> List[str]:
        """컬럼 추출"""
        columns = []
        # SET column = value 패턴
        pattern = r'\bSET\s+(\w+(?:\.\w+)?)\s*='
        matches = re.findall(pattern, content, re.IGNORECASE)
        columns.extend(matches)
        return columns

    def _extract_where_conditions(self, content: str) -> List[str]:
        """WHERE 조건 추출"""
        conditions = []
        # WHERE 절 패턴
        pattern = r'\bWHERE\s+(.+?)(?=\bORDER\s+BY\b|\bGROUP\s+BY\b|$)'
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        conditions.extend(matches)
        return conditions

    def _extract_file_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """파일 메타데이터 추출"""
        return {
            'file_path': context.get('file_path', ''),
            'file_name': context.get('file_name', ''),
            'parser_type': self._get_parser_type(),
            'confidence': self.confidence
        }
