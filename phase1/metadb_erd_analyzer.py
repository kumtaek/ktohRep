#!/usr/bin/env python3
"""
메타디비 기반 ERD 분석기
SQLite 메타디비를 직접 읽어서 ERD 구조를 분석합니다.
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ColumnInfo:
    """컬럼 정보"""
    name: str
    data_type: str
    nullable: bool
    comment: Optional[str]

@dataclass
class TableInfo:
    """테이블 정보"""
    owner: str
    name: str
    full_name: str
    status: str
    comment: str
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: List[Tuple[str, str, str]]  # (column, referenced_table, referenced_column)

@dataclass
class ERDStructure:
    """ERD 구조 정보"""
    project_name: str
    tables: List[TableInfo]
    total_tables: int
    total_columns: int
    total_relationships: int
    analysis_time: datetime

class MetaDBERDAnalyzer:
    """메타디비 기반 ERD 분석기"""
    
    def __init__(self, project_path: str):
        """
        분석기 초기화
        
        Args:
            project_path: 분석할 프로젝트 경로
        """
        self.project_path = Path(project_path)
        self.metadata_db_path = self.project_path / "metadata.db"
        self.logger = logging.getLogger(__name__)
        
    def analyze_erd(self) -> ERDStructure:
        """
        메타디비에서 ERD 분석
        
        Returns:
            ERD 구조 정보
        """
        self.logger.info(f"메타디비 ERD 분석 시작: {self.metadata_db_path}")
        
        if not self.metadata_db_path.exists():
            raise FileNotFoundError(f"메타디비를 찾을 수 없습니다: {self.metadata_db_path}")
        
        start_time = datetime.now()
        
        # SQLite 연결
        conn = sqlite3.connect(str(self.metadata_db_path))
        cursor = conn.cursor()
        
        try:
            # 테이블 정보 조회
            tables = self._analyze_tables(cursor)
            
            # 컬럼 정보 조회
            total_columns = 0
            total_relationships = 0
            
            for table in tables:
                columns = self._analyze_columns(cursor, table)
                table.columns = columns
                total_columns += len(columns)
                
                # PK 정보 조회
                primary_keys = self._analyze_primary_keys(cursor, table)
                table.primary_keys = primary_keys
                
                # FK 관계 추론
                foreign_keys = self._infer_foreign_keys(table, tables)
                table.foreign_keys = foreign_keys
                total_relationships += len(foreign_keys)
            
            # ERD 구조 정보 생성
            erd_structure = ERDStructure(
                project_name=self.project_path.name,
                tables=tables,
                total_tables=len(tables),
                total_columns=total_columns,
                total_relationships=total_relationships,
                analysis_time=start_time
            )
            
            return erd_structure
            
        finally:
            conn.close()
    
    def _analyze_tables(self, cursor: sqlite3.Cursor) -> List[TableInfo]:
        """테이블 정보 분석"""
        cursor.execute("""
            SELECT owner, table_name, status, table_comment 
            FROM db_tables 
            ORDER BY owner, table_name
        """)
        
        tables = []
        for row in cursor.fetchall():
            owner, table_name, status, comment = row
            full_name = f"{owner}.{table_name}" if owner else table_name
            
            table_info = TableInfo(
                owner=owner or '',
                name=table_name,
                full_name=full_name,
                status=status or 'VALID',
                comment=comment or f"{full_name} 테이블",
                columns=[],
                primary_keys=[],
                foreign_keys=[]
            )
            tables.append(table_info)
        
        return tables
    
    def _analyze_columns(self, cursor: sqlite3.Cursor, table: TableInfo) -> List[ColumnInfo]:
        """컬럼 정보 분석"""
        cursor.execute("""
            SELECT column_name, data_type, nullable, column_comment
            FROM db_columns 
            WHERE table_id = (SELECT table_id FROM db_tables WHERE owner = ? AND table_name = ?)
            ORDER BY column_name
        """, (table.owner, table.name))
        
        columns = []
        for row in cursor.fetchall():
            column_name, data_type, nullable, comment = row
            
            column_info = ColumnInfo(
                name=column_name,
                data_type=data_type or 'UNKNOWN',
                nullable=nullable == 'Y',
                comment=comment
            )
            columns.append(column_info)
        
        return columns
    
    def _analyze_primary_keys(self, cursor: sqlite3.Cursor, table: TableInfo) -> List[str]:
        """기본키 정보 분석"""
        cursor.execute("""
            SELECT column_name
            FROM db_pk 
            WHERE table_id = (SELECT table_id FROM db_tables WHERE owner = ? AND table_name = ?)
            ORDER BY pk_pos
        """, (table.owner, table.name))
        
        primary_keys = [row[0] for row in cursor.fetchall()]
        return primary_keys
    
    def _infer_foreign_keys(self, table: TableInfo, all_tables: List[TableInfo]) -> List[Tuple[str, str, str]]:
        """외래키 관계 추론"""
        foreign_keys = []
        
        for column in table.columns:
            # ID로 끝나는 컬럼이면서 PK가 아닌 경우 외래키 가능성 검토
            if (column.name.endswith('_ID') or column.name.endswith('ID')) and column.name not in table.primary_keys:
                # 참조할 수 있는 테이블 찾기
                referenced_table = self._find_referenced_table(column.name, all_tables)
                if referenced_table:
                    foreign_keys.append((column.name, referenced_table, column.name))
        
        return foreign_keys
    
    def _find_referenced_table(self, column_name: str, all_tables: List[TableInfo]) -> Optional[str]:
        """참조할 수 있는 테이블 찾기"""
        # 컬럼명에서 테이블명 추출 (예: CUSTOMER_ID -> CUSTOMERS)
        if column_name.endswith('_ID'):
            table_name = column_name[:-3] + 'S'  # CUSTOMER_ID -> CUSTOMERS
        elif column_name.endswith('ID'):
            table_name = column_name[:-2] + 'S'  # USER_ID -> USERS
        else:
            return None
        
        # 해당 테이블이 존재하는지 확인
        for table in all_tables:
            if table.name.upper() == table_name.upper():
                return table.full_name
        
        return None

if __name__ == "__main__":
    # 테스트
    analyzer = MetaDBERDAnalyzer("../project/sampleSrc")
    erd_structure = analyzer.analyze_erd()
    
    print(f"테이블 수: {erd_structure.total_tables}")
    print(f"컬럼 수: {erd_structure.total_columns}")
    print(f"관계 수: {erd_structure.total_relationships}")
    
    for table in erd_structure.tables:
        print(f"\n테이블: {table.full_name}")
        print(f"  컬럼 수: {len(table.columns)}")
        print(f"  PK: {table.primary_keys}")
        print(f"  FK: {len(table.foreign_keys)}")
