"""
Oracle SELECT Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle SELECT 파서
"""

import re
from typing import Dict, List, Any
from parsers.oracle.oracle_parser_context7 import OracleParserContext7

class OracleSelectParser(OracleParserContext7):
    """
    Oracle SELECT Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle SELECT 파서
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # SELECT 전용 패턴 추가
        self.select_specific_patterns = {
            'select_with_hints': re.compile(r'SELECT\s+/\*\+.*?\*/\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
            'select_distinct': re.compile(r'SELECT\s+DISTINCT\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
            'select_all': re.compile(r'SELECT\s+\*\s+FROM', re.IGNORECASE),
        }
    
    def _get_parser_type(self) -> str:
        return 'oracle_select'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Oracle SELECT 쿼리 전용 파싱
        """
        # 기본 Oracle 파서 결과 가져오기
        result = super().parse_content(content, context)
        
        # SELECT 전용 기능 추가
        result['select_features'] = self._extract_select_features(content)
        
        return result
    
    def _extract_select_features(self, content: str) -> Dict[str, List[str]]:
        """SELECT 전용 기능 추출"""
        features = {
            'hints': [],
            'distinct_usage': [],
            'select_all': [],
            'group_by': [],
            'order_by': [],
            'having_clause': []
        }
        
        # 힌트 추출
        hint_matches = self.select_specific_patterns['select_with_hints'].finditer(content)
        for match in hint_matches:
            features['hints'].append(match.group(0))
        
        # DISTINCT 사용
        distinct_matches = self.select_specific_patterns['select_distinct'].finditer(content)
        for match in distinct_matches:
            features['distinct_usage'].append(match.group(0))
        
        # SELECT * 사용
        all_matches = self.select_specific_patterns['select_all'].finditer(content)
        for match in all_matches:
            features['select_all'].append(match.group(0))
        
        # GROUP BY 절
        group_by_pattern = re.compile(r'\bGROUP\s+BY\s+(.+?)(?=\b(?:ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL)
        group_matches = group_by_pattern.finditer(content)
        for match in group_matches:
            features['group_by'].append(match.group(1).strip())
        
        # ORDER BY 절
        order_by_pattern = re.compile(r'\bORDER\s+BY\s+(.+?)(?=\b(?:HAVING|$))', re.IGNORECASE | re.DOTALL)
        order_matches = order_by_pattern.finditer(content)
        for match in order_matches:
            features['order_by'].append(match.group(1).strip())
        
        # HAVING 절
        having_pattern = re.compile(r'\bHAVING\s+(.+?)(?=\b(?:ORDER|$))', re.IGNORECASE | re.DOTALL)
        having_matches = having_pattern.finditer(content)
        for match in having_matches:
            features['having_clause'].append(match.group(1).strip())
        
        return features