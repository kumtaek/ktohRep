"""
데이터베이스 ERD 분석 엔진
DB_SCHEMA 폴더의 CSV 파일들을 분석하여 ERD 정보를 추출합니다.
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import re

@dataclass
class ColumnInfo:
    """컬럼 정보"""
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    foreign_key: bool
    referenced_table: Optional[str]
    referenced_column: Optional[str]
    default_value: Optional[str]
    comment: Optional[str]

@dataclass
class TableInfo:
    """테이블 정보"""
    name: str
    comment: str
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: List[Tuple[str, str, str, str]]  # (column, referenced_table, referenced_column, constraint_name)
    indexes: List[str]
    row_count: Optional[int]

@dataclass
class ERDStructure:
    """ERD 구조 정보"""
    project_name: str
    tables: List[TableInfo]
    total_tables: int
    total_columns: int
    total_relationships: int
    analysis_time: datetime

class ERDAnalyzer:
    """ERD 분석기"""
    
    def __init__(self, project_path: str):
        """
        분석기 초기화
        
        Args:
            project_path: 분석할 프로젝트 경로
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        
        # CSV 파일 패턴
        self.csv_pattern = re.compile(r'\.csv$')
        
    def analyze_erd(self) -> ERDStructure:
        """
        ERD 분석
        
        Returns:
            ERD 구조 정보
        """
        self.logger.info(f"ERD 분석 시작: {self.project_path}")
        
        start_time = datetime.now()
        
        # DB_SCHEMA 디렉토리 찾기
        db_schema_dir = self._find_db_schema_directory()
        if not db_schema_dir:
            raise FileNotFoundError(f"DB_SCHEMA 디렉토리를 찾을 수 없습니다: {self.project_path}")
        
        # CSV 파일들 분석
        tables = []
        total_columns = 0
        total_relationships = 0
        
        for csv_file in db_schema_dir.glob("*.csv"):
            table_info = self._analyze_csv_file(csv_file)
            if table_info:
                tables.append(table_info)
                total_columns += len(table_info.columns)
                total_relationships += len(table_info.foreign_keys)
        
        # ERD 구조 정보 생성
        erd_structure = ERDStructure(
            project_name=self.project_path.name,
            tables=tables,
            total_tables=len(tables),
            total_columns=total_columns,
            total_relationships=total_relationships,
            analysis_time=start_time
        )
        
        self.logger.info(f"ERD 분석 완료: {len(tables)}개 테이블, {total_columns}개 컬럼")
        
        return erd_structure
    
    def _find_db_schema_directory(self) -> Optional[Path]:
        """DB_SCHEMA 디렉토리 찾기"""
        # 일반적인 DB_SCHEMA 위치들
        common_paths = [
            self.project_path / "DB_SCHEMA",
            self.project_path / "db_schema",
            self.project_path / "schema",
            self.project_path / "database" / "schema"
        ]
        
        for path in common_paths:
            if path.exists() and path.is_dir():
                self.logger.info(f"DB_SCHEMA 디렉토리 발견: {path}")
                return path
        
        return None
    
    def _analyze_csv_file(self, csv_file: Path) -> Optional[TableInfo]:
        """CSV 파일 분석"""
        try:
            table_name = csv_file.stem  # 파일명에서 확장자 제거
            
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                columns = []
                primary_keys = []
                foreign_keys = []
                
                for row in reader:
                    column_info = self._parse_column_row(row, table_name)
                    if column_info:
                        columns.append(column_info)
                        
                        if column_info.primary_key:
                            primary_keys.append(column_info.name)
                        
                        if column_info.foreign_key:
                            foreign_keys.append((
                                column_info.name,
                                column_info.referenced_table or '',
                                column_info.referenced_column or '',
                                f"FK_{table_name}_{column_info.name}"
                            ))
                
                if not columns:
                    return None
                
                return TableInfo(
                    name=table_name,
                    comment=f"{table_name} 테이블",
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    indexes=[],
                    row_count=None
                )
                
        except Exception as e:
            self.logger.error(f"CSV 파일 분석 실패 {csv_file}: {e}")
            return None
    
    def _parse_column_row(self, row: Dict[str, str], table_name: str) -> Optional[ColumnInfo]:
        """컬럼 행 파싱"""
        try:
            # CSV 컬럼명 매핑 (일반적인 형식들)
            column_name = row.get('COLUMN_NAME') or row.get('Column Name') or row.get('column_name') or row.get('name')
            data_type = row.get('DATA_TYPE') or row.get('Data Type') or row.get('data_type') or row.get('type')
            nullable = row.get('IS_NULLABLE') or row.get('Is Nullable') or row.get('is_nullable') or row.get('nullable')
            primary_key = row.get('IS_PRIMARY_KEY') or row.get('Is Primary Key') or row.get('is_primary_key') or row.get('pk')
            foreign_key = row.get('IS_FOREIGN_KEY') or row.get('Is Foreign Key') or row.get('is_foreign_key') or row.get('fk')
            referenced_table = row.get('REFERENCED_TABLE') or row.get('Referenced Table') or row.get('referenced_table')
            referenced_column = row.get('REFERENCED_COLUMN') or row.get('Referenced Column') or row.get('referenced_column')
            default_value = row.get('DEFAULT_VALUE') or row.get('Default Value') or row.get('default_value') or row.get('default')
            comment = row.get('COMMENT') or row.get('Comment') or row.get('comment') or row.get('description')
            
            if not column_name or not data_type:
                return None
            
            # 불린 값 변환
            is_nullable = self._parse_boolean(nullable)
            is_primary_key = self._parse_boolean(primary_key)
            is_foreign_key = self._parse_boolean(foreign_key)
            
            return ColumnInfo(
                name=column_name.strip(),
                data_type=data_type.strip(),
                nullable=is_nullable,
                primary_key=is_primary_key,
                foreign_key=is_foreign_key,
                referenced_table=referenced_table.strip() if referenced_table else None,
                referenced_column=referenced_column.strip() if referenced_column else None,
                default_value=default_value.strip() if default_value else None,
                comment=comment.strip() if comment else None
            )
            
        except Exception as e:
            self.logger.error(f"컬럼 행 파싱 실패: {e}")
            return None
    
    def _parse_boolean(self, value: str) -> bool:
        """불린 값 파싱"""
        if not value:
            return False
        
        value_lower = value.lower().strip()
        return value_lower in ['true', '1', 'yes', 'y', 'pk', 'fk', 'primary', 'foreign']
    
    def generate_summary(self, erd_structure: ERDStructure) -> Dict[str, Any]:
        """ERD 요약 정보 생성"""
        return {
            'project_name': erd_structure.project_name,
            'analysis_time': erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tables': erd_structure.total_tables,
            'total_columns': erd_structure.total_columns,
            'total_relationships': erd_structure.total_relationships,
            'average_columns_per_table': round(erd_structure.total_columns / erd_structure.total_tables, 2) if erd_structure.total_tables > 0 else 0
        }
