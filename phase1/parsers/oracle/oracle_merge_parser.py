"""
Oracle MERGE Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle MERGE 파서
"""

from typing import Dict, List, Any
from parsers.oracle.oracle_parser_context7 import OracleParserContext7

class OracleMergeParser(OracleParserContext7):
    """
    Oracle MERGE Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle MERGE 파서
    """
    
    def _get_parser_type(self) -> str:
        return 'oracle_merge'