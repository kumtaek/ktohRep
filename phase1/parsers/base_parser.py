"""
데이터베이스 파서 기본 클래스
모든 데이터베이스별 파서가 상속받아야 하는 기본 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import re

class BaseDatabaseParser(ABC):
    """데이터베이스 파서의 기본 인터페이스"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        기본 파서 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.db_type = self._get_database_type()
        
    @abstractmethod
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환 (예: 'oracle', 'postgresql', 'mssql')"""
        pass
    
    @abstractmethod
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        SQL 구문을 파싱하여 메타데이터를 추출
        
        Args:
            sql_content: 분석할 SQL 구문
            context: 컨텍스트 정보 (파일 경로, 라인 번호 등)
            
        Returns:
            파싱된 메타데이터 딕셔너리
        """
        pass
    
    def _normalize_sql(self, sql_content: str) -> str:
        """
        SQL 구문을 정규화 (공통 처리)
        
        Args:
            sql_content: 원본 SQL 구문
            
        Returns:
            정규화된 SQL 구문
        """
        # 여러 공백을 하나로 통일
        normalized = re.sub(r'\s+', ' ', sql_content.strip())
        
        # 주석 제거
        normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        return normalized
    
    def _extract_basic_tables(self, sql: str) -> List[str]:
        """
        기본적인 테이블 추출 (공통 로직)
        
        Args:
            sql: SQL 구문
            
        Returns:
            추출된 테이블명 리스트
        """
        tables = set()
        
        # FROM 절에서 테이블 추출
        from_pattern = r'\bFROM\s+([^JOIN]+?)(?=\b(?:JOIN|WHERE|GROUP|ORDER|HAVING|$))'
        from_matches = re.finditer(from_pattern, sql, re.IGNORECASE | re.DOTALL)
        
        for match in from_matches:
            from_clause = match.group(1).strip()
            table_refs = [t.strip() for t in from_clause.split(',')]
            
            for table_ref in table_refs:
                parts = table_ref.strip().split()
                if parts:
                    table_name = parts[0]
                    if '.' in table_name:
                        table_name = table_name.split('.')[-1]
                    tables.add(table_name.upper())
        
        return list(tables)
    
    def _extract_basic_columns(self, sql: str) -> List[str]:
        """
        기본적인 컬럼 추출 (공통 로직)
        
        Args:
            sql: SQL 구문
            
        Returns:
            추출된 컬럼명 리스트
        """
        columns = set()
        
        # 테이블.컬럼 형태 추출
        column_pattern = r'\b(\w+)\.(\w+)\b'
        column_matches = re.finditer(column_pattern, sql, re.IGNORECASE)
        
        for match in column_matches:
            table_name = match.group(1)
            column_name = match.group(2)
            
            # 테이블명이 SQL 키워드가 아닌 경우만 컬럼으로 인식
            if not self._is_sql_keyword(table_name):
                columns.add(f"{table_name.upper()}.{column_name.upper()}")
        
        return list(columns)
    
    def _is_sql_keyword(self, word: str) -> bool:
        """
        주어진 단어가 SQL 키워드인지 확인
        
        Args:
            word: 확인할 단어
            
        Returns:
            SQL 키워드 여부
        """
        sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'GROUP', 'ORDER', 'HAVING',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE',
            'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL'
        }
        return word.upper() in sql_keywords

# BaseParser 별칭 추가 (기존 코드와의 호환성을 위해)
BaseParser = BaseDatabaseParser
