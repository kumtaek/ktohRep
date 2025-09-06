#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공통 테이블 별칭 해석 유틸리티
모든 SQL 파서에서 일관된 별칭 처리를 위한 공통 모듈
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

# 전역 인스턴스 캐시
_resolver_cache = {}

def get_table_alias_resolver(default_schema: str = 'DEFAULT') -> 'TableAliasResolver':
    """
    테이블 별칭 해석기 인스턴스 반환
    
    Args:
        default_schema: 기본 스키마명
        
    Returns:
        TableAliasResolver 인스턴스
    """
    # 현재는 단순한 구현으로 매번 새 인스턴스 반환
    # 추후 데이터베이스 연동 시 실제 db_tables 정보를 주입하도록 개선
    config = {'database': {'default_schema': default_schema}}
    db_tables = []  # 실제 구현에서는 메타데이터베이스에서 조회
    return TableAliasResolver(config, db_tables)


@dataclass
class TableReference:
    """테이블 참조 정보"""
    full_name: str      # schema.table_name 또는 table_name
    alias: str          # 별칭
    schema: Optional[str] = None
    table_name: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 스키마와 테이블명 분리"""
        if self.full_name and '.' in self.full_name:
            parts = self.full_name.split('.')
            if len(parts) == 2:
                self.schema = parts[0]
                self.table_name = parts[1]
        else:
            self.table_name = self.full_name


class TableAliasResolver:
    """테이블 별칭 해석기 - 모든 SQL 파서에서 공통 사용"""
    
    def __init__(self, default_schema: str = "DEFAULT"):
        """
        별칭 해석기 초기화
        
        Args:
            default_schema: 스키마가 없는 테이블의 기본 스키마
        """
        self.default_schema = default_schema
        
        # FROM 절 패턴 (Oracle, MySQL, PostgreSQL 호환)
        self.from_patterns = [
            # FROM table_name alias, table2 alias2
            re.compile(r'\bFROM\s+(.+?)(?=\b(?:JOIN|WHERE|GROUP|ORDER|HAVING|CONNECT\s+BY|START\s+WITH|UNION|MINUS|INTERSECT|$))', 
                      re.IGNORECASE | re.DOTALL),
        ]
        
        # JOIN 절 패턴
        self.join_patterns = [
            # JOIN table_name alias ON condition
            re.compile(r'\b(?:INNER\s+)?(?:LEFT\s+)?(?:RIGHT\s+)?(?:FULL\s+)?(?:OUTER\s+)?(?:CROSS\s+)?JOIN\s+(\w+(?:\.\w+)?)\s+(?:AS\s+)?(\w+)?', 
                      re.IGNORECASE),
        ]
        
        # UPDATE/INSERT/DELETE 패턴
        self.dml_patterns = [
            re.compile(r'\bUPDATE\s+(\w+(?:\.\w+)?)\s+(?:AS\s+)?(\w+)?', re.IGNORECASE),
            re.compile(r'\bINSERT\s+(?:INTO\s+)?(\w+(?:\.\w+)?)', re.IGNORECASE),
            re.compile(r'\bDELETE\s+(?:FROM\s+)?(\w+(?:\.\w+)?)\s+(?:AS\s+)?(\w+)?', re.IGNORECASE),
            re.compile(r'\bMERGE\s+(?:INTO\s+)?(\w+(?:\.\w+)?)\s+(?:AS\s+)?(\w+)?', re.IGNORECASE),
        ]
    
    def extract_table_alias_mapping(self, sql_content: str) -> Dict[str, TableReference]:
        """
        SQL에서 테이블명과 별칭의 매핑을 추출
        
        Args:
            sql_content: SQL 구문
            
        Returns:
            {별칭: TableReference} 형태의 딕셔너리
        """
        alias_mapping = {}
        
        # FROM 절에서 테이블과 별칭 추출
        self._extract_from_aliases(sql_content, alias_mapping)
        
        # JOIN 절에서 테이블과 별칭 추출
        self._extract_join_aliases(sql_content, alias_mapping)
        
        # DML 문에서 테이블과 별칭 추출
        self._extract_dml_aliases(sql_content, alias_mapping)
        
        return alias_mapping
    
    def _extract_from_aliases(self, sql_content: str, alias_mapping: Dict[str, TableReference]):
        """FROM 절에서 테이블명과 별칭 추출"""
        for pattern in self.from_patterns:
            match = pattern.search(sql_content)
            if match:
                from_clause = match.group(1).strip()
                
                # 콤마로 구분된 테이블들 파싱
                tables = self._split_table_list(from_clause)
                
                for table_ref in tables:
                    table_info = self._parse_table_reference(table_ref)
                    if table_info and table_info.alias:
                        alias_mapping[table_info.alias.upper()] = table_info
    
    def _extract_join_aliases(self, sql_content: str, alias_mapping: Dict[str, TableReference]):
        """JOIN 절에서 테이블명과 별칭 추출"""
        for pattern in self.join_patterns:
            for match in pattern.finditer(sql_content):
                table_name = match.group(1)
                alias = match.group(2) if len(match.groups()) >= 2 else None
                
                if alias:
                    table_info = TableReference(
                        full_name=table_name,
                        alias=alias
                    )
                    alias_mapping[alias.upper()] = table_info
    
    def _extract_dml_aliases(self, sql_content: str, alias_mapping: Dict[str, TableReference]):
        """DML 문에서 테이블명과 별칭 추출"""
        for pattern in self.dml_patterns:
            for match in pattern.finditer(sql_content):
                table_name = match.group(1)
                alias = match.group(2) if len(match.groups()) >= 2 else None
                
                if alias:
                    table_info = TableReference(
                        full_name=table_name,
                        alias=alias
                    )
                    alias_mapping[alias.upper()] = table_info
    
    def _split_table_list(self, table_list: str) -> List[str]:
        """
        콤마로 구분된 테이블 목록을 분리
        서브쿼리의 콤마는 무시하고 최상위 레벨의 콤마만 처리
        """
        tables = []
        current_table = ""
        paren_count = 0
        
        for char in table_list:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                if current_table.strip():
                    tables.append(current_table.strip())
                current_table = ""
                continue
            
            current_table += char
        
        # 마지막 테이블 추가
        if current_table.strip():
            tables.append(current_table.strip())
        
        return tables
    
    def _parse_table_reference(self, table_ref: str) -> Optional[TableReference]:
        """
        테이블 참조 문자열을 파싱하여 TableReference 객체 생성
        
        Supports:
        - table_name alias
        - table_name AS alias
        - schema.table_name alias
        - (subquery) alias
        """
        table_ref = table_ref.strip()
        
        # 서브쿼리인 경우 처리하지 않음
        if table_ref.startswith('('):
            return None
        
        # AS 키워드 제거
        table_ref = re.sub(r'\s+AS\s+', ' ', table_ref, flags=re.IGNORECASE)
        
        # 공백으로 분리
        parts = table_ref.split()
        
        if len(parts) == 1:
            # 별칭 없음
            return TableReference(full_name=parts[0], alias=parts[0])
        elif len(parts) == 2:
            # 테이블명 별칭
            return TableReference(full_name=parts[0], alias=parts[1])
        else:
            # 복잡한 경우는 첫 번째와 마지막 부분 사용
            return TableReference(full_name=parts[0], alias=parts[-1])
    
    def resolve_table_alias(self, table_ref: str, alias_mapping: Dict[str, TableReference]) -> str:
        """
        테이블 참조를 실제 테이블명으로 해석
        
        Args:
            table_ref: 테이블 참조 (별칭 또는 실제 테이블명)
            alias_mapping: 별칭 매핑 딕셔너리
            
        Returns:
            실제 테이블명 (스키마 포함)
        """
        if not table_ref:
            return table_ref
        
        table_ref_upper = table_ref.upper()
        
        # 별칭 매핑에서 찾기
        if table_ref_upper in alias_mapping:
            table_info = alias_mapping[table_ref_upper]
            if table_info.schema:
                return f"{table_info.schema}.{table_info.table_name}"
            else:
                return f"{self.default_schema}.{table_info.table_name}"
        
        # 별칭이 아닌 경우 그대로 반환 (스키마가 없으면 기본 스키마 추가)
        if '.' not in table_ref:
            return f"{self.default_schema}.{table_ref.upper()}"
        
        return table_ref.upper()
    
    def resolve_join_tables(self, l_table: str, r_table: str, alias_mapping: Dict[str, TableReference]) -> Tuple[str, str]:
        """
        조인의 양쪽 테이블을 모두 해석
        
        Args:
            l_table: 왼쪽 테이블 참조
            r_table: 오른쪽 테이블 참조
            alias_mapping: 별칭 매핑 딕셔너리
            
        Returns:
            (해석된_왼쪽_테이블, 해석된_오른쪽_테이블)
        """
        resolved_l = self.resolve_table_alias(l_table, alias_mapping)
        resolved_r = self.resolve_table_alias(r_table, alias_mapping)
        return resolved_l, resolved_r
    
    def clean_dynamic_sql(self, sql_content: str) -> str:
        """
        동적 SQL 태그 제거 (MyBatis, JPA 등)
        
        Args:
            sql_content: 동적 태그가 포함된 SQL
            
        Returns:
            정리된 SQL
        """
        # MyBatis 동적 태그 제거
        sql_content = re.sub(r'<if[^>]*>(.*?)</if>', r'\1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<choose[^>]*>(.*?)</choose>', r'\1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<when[^>]*>(.*?)</when>', r'\1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<otherwise[^>]*>(.*?)</otherwise>', r'\1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<where[^>]*>(.*?)</where>', r'WHERE \1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<set[^>]*>(.*?)</set>', r'SET \1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<foreach[^>]*>(.*?)</foreach>', r'\1', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'<trim[^>]*>(.*?)</trim>', r'\1', sql_content, flags=re.DOTALL)
        
        # 기타 XML 태그 제거
        sql_content = re.sub(r'<[^>]+>', ' ', sql_content)
        
        # 공백 정리
        sql_content = re.sub(r'\s+', ' ', sql_content).strip()
        
        return sql_content


# 전역 인스턴스 (싱글톤 패턴)
_global_resolver = None


def get_table_alias_resolver(default_schema: str = "DEFAULT") -> TableAliasResolver:
    """전역 테이블 별칭 해석기 인스턴스 반환"""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = TableAliasResolver(default_schema)
    return _global_resolver


def resolve_table_aliases_in_sql(sql_content: str, default_schema: str = "DEFAULT") -> Tuple[str, Dict[str, TableReference]]:
    """
    SQL에서 별칭을 실제 테이블명으로 변환
    
    Args:
        sql_content: 원본 SQL
        default_schema: 기본 스키마명
        
    Returns:
        (변환된_SQL, 별칭_매핑)
    """
    resolver = get_table_alias_resolver(default_schema)
    
    # 동적 SQL 태그 정리
    cleaned_sql = resolver.clean_dynamic_sql(sql_content)
    
    # 별칭 매핑 추출
    alias_mapping = resolver.extract_table_alias_mapping(cleaned_sql)
    
    # SQL에서 별칭을 실제 테이블명으로 치환
    resolved_sql = cleaned_sql
    for alias, table_info in alias_mapping.items():
        # 별칭을 실제 테이블명으로 치환
        pattern = r'\b' + re.escape(alias) + r'\b'
        replacement = f"{table_info.schema or default_schema}.{table_info.table_name}"
        resolved_sql = re.sub(pattern, replacement, resolved_sql, flags=re.IGNORECASE)
    
    return resolved_sql, alias_mapping
