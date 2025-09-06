"""
Oracle UPDATE Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle UPDATE 파서
"""

from typing import Dict, List, Any
from phase1.parsers.oracle.oracle_parser_context7 import OracleParserContext7

class OracleUpdateParser(OracleParserContext7):
    """
    Oracle UPDATE Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 Oracle UPDATE 파서
    """
    
    def _get_parser_type(self) -> str:
        return 'oracle_update'