"""
Database schema CSV loader
Loads Oracle database metadata from CSV files
"""

import os
import pandas as pd
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.database import DBTable, DBColumn, DBPrimaryKey, DBView


class CSVSchemaLoader:
    """데이터베이스 스키마 CSV 로더"""
    
    def __init__(self, session: Session, config: Dict = None):
        self.session = session
        self.config = config or {}
        self.db_schema_config = self.config.get('db_schema', {})
    
    def get_schema_directory(self, project_name: str) -> str:
        """프로젝트의 스키마 디렉토리 경로 생성"""
        base_path = self.db_schema_config.get('base_path', './PROJECT/{project_name}/DB_SCHEMA')
        return base_path.format(project_name=project_name)
    
    def load_tables_csv(self, schema_dir: str) -> List[Dict]:
        """ALL_TABLES.csv 로드"""
        tables_file = self.db_schema_config.get('files', {}).get('tables', 'ALL_TABLES.csv')
        csv_path = os.path.join(schema_dir, tables_file)
        
        if not os.path.exists(csv_path):
            print(f"Tables CSV not found: {csv_path}")
            return []
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # 필수 컬럼 확인
            required_columns = ['OWNER', 'TABLE_NAME']
            if not all(col in df.columns for col in required_columns):
                print(f"Missing required columns in {tables_file}")
                return []
            
            tables = []
            for _, row in df.iterrows():
                table_info = {
                    'owner': str(row.get('OWNER', '')).strip(),
                    'table_name': str(row.get('TABLE_NAME', '')).strip(),
                    'status': str(row.get('STATUS', 'VALID')).strip()
                }
                
                if table_info['table_name']:  # 테이블명이 있는 경우만
                    tables.append(table_info)
            
            print(f"Loaded {len(tables)} tables from {tables_file}")
            return tables
            
        except Exception as e:
            print(f"Error loading tables CSV: {e}")
            return []
    
    def load_columns_csv(self, schema_dir: str) -> List[Dict]:
        """ALL_TAB_COLUMNS.csv 로드"""
        columns_file = self.db_schema_config.get('files', {}).get('columns', 'ALL_TAB_COLUMNS.csv')
        csv_path = os.path.join(schema_dir, columns_file)
        
        if not os.path.exists(csv_path):
            print(f"Columns CSV not found: {csv_path}")
            return []
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # 필수 컬럼 확인
            required_columns = ['OWNER', 'TABLE_NAME', 'COLUMN_NAME']
            if not all(col in df.columns for col in required_columns):
                print(f"Missing required columns in {columns_file}")
                return []
            
            columns = []
            for _, row in df.iterrows():
                column_info = {
                    'owner': str(row.get('OWNER', '')).strip(),
                    'table_name': str(row.get('TABLE_NAME', '')).strip(),
                    'column_name': str(row.get('COLUMN_NAME', '')).strip(),
                    'data_type': str(row.get('DATA_TYPE', '')).strip(),
                    'nullable': str(row.get('NULLABLE', 'Y')).strip()
                }
                
                if column_info['table_name'] and column_info['column_name']:
                    columns.append(column_info)
            
            print(f"Loaded {len(columns)} columns from {columns_file}")
            return columns
            
        except Exception as e:
            print(f"Error loading columns CSV: {e}")
            return []
    
    def load_primary_keys_csv(self, schema_dir: str) -> List[Dict]:
        """PK_INFO.csv 로드"""
        pk_file = self.db_schema_config.get('files', {}).get('primary_keys', 'PK_INFO.csv')
        csv_path = os.path.join(schema_dir, pk_file)
        
        if not os.path.exists(csv_path):
            print(f"Primary keys CSV not found: {csv_path}")
            return []
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # 필수 컬럼 확인
            required_columns = ['OWNER', 'TABLE_NAME', 'COLUMN_NAME']
            if not all(col in df.columns for col in required_columns):
                print(f"Missing required columns in {pk_file}")
                return []
            
            primary_keys = []
            for _, row in df.iterrows():
                pk_info = {
                    'owner': str(row.get('OWNER', '')).strip(),
                    'table_name': str(row.get('TABLE_NAME', '')).strip(),
                    'column_name': str(row.get('COLUMN_NAME', '')).strip(),
                    'position': int(row.get('POSITION', 1)) if pd.notna(row.get('POSITION')) else 1
                }
                
                if pk_info['table_name'] and pk_info['column_name']:
                    primary_keys.append(pk_info)
            
            print(f"Loaded {len(primary_keys)} primary key constraints from {pk_file}")
            return primary_keys
            
        except Exception as e:
            print(f"Error loading primary keys CSV: {e}")
            return []
    
    def load_views_csv(self, schema_dir: str) -> List[Dict]:
        """ALL_VIEWS.csv 로드"""
        views_file = self.db_schema_config.get('files', {}).get('views', 'ALL_VIEWS.csv')
        csv_path = os.path.join(schema_dir, views_file)
        
        if not os.path.exists(csv_path):
            print(f"Views CSV not found: {csv_path}")
            return []
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # 필수 컬럼 확인
            required_columns = ['OWNER', 'VIEW_NAME']
            if not all(col in df.columns for col in required_columns):
                print(f"Missing required columns in {views_file}")
                return []
            
            views = []
            for _, row in df.iterrows():
                view_info = {
                    'owner': str(row.get('OWNER', '')).strip(),
                    'view_name': str(row.get('VIEW_NAME', '')).strip(),
                    'text': str(row.get('TEXT', '')).strip() if pd.notna(row.get('TEXT')) else ''
                }
                
                if view_info['view_name']:
                    views.append(view_info)
            
            print(f"Loaded {len(views)} views from {views_file}")
            return views
            
        except Exception as e:
            print(f"Error loading views CSV: {e}")
            return []
    
    def store_tables(self, tables_data: List[Dict]) -> Dict[str, int]:
        """테이블 정보를 데이터베이스에 저장"""
        table_id_map = {}  # (owner, table_name) -> table_id 매핑
        
        # 기존 테이블 정보 삭제 (재로드)
        self.session.query(DBPrimaryKey).delete()
        self.session.query(DBColumn).delete()
        self.session.query(DBTable).delete()
        
        # 테이블 정보 저장
        for table_data in tables_data:
            try:
                table_obj = DBTable(
                    owner=table_data['owner'],
                    table_name=table_data['table_name'],
                    status=table_data['status']
                )
                self.session.add(table_obj)
                self.session.flush()  # table_id 생성
                
                key = (table_data['owner'], table_data['table_name'])
                table_id_map[key] = table_obj.table_id
                
            except Exception as e:
                print(f"Error storing table {table_data['table_name']}: {e}")
        
        print(f"Stored {len(table_id_map)} tables")
        return table_id_map
    
    def store_columns(self, columns_data: List[Dict], table_id_map: Dict[str, int]) -> int:
        """컬럼 정보를 데이터베이스에 저장"""
        stored_count = 0
        
        for column_data in columns_data:
            try:
                key = (column_data['owner'], column_data['table_name'])
                table_id = table_id_map.get(key)
                
                if table_id:
                    column_obj = DBColumn(
                        table_id=table_id,
                        column_name=column_data['column_name'],
                        data_type=column_data['data_type'],
                        nullable=column_data['nullable']
                    )
                    self.session.add(column_obj)
                    stored_count += 1
                else:
                    print(f"Table not found for column: {column_data['owner']}.{column_data['table_name']}.{column_data['column_name']}")
            
            except Exception as e:
                print(f"Error storing column {column_data['column_name']}: {e}")
        
        print(f"Stored {stored_count} columns")
        return stored_count
    
    def store_primary_keys(self, pk_data: List[Dict], table_id_map: Dict[str, int]) -> int:
        """기본키 정보를 데이터베이스에 저장"""
        stored_count = 0
        
        for pk_info in pk_data:
            try:
                key = (pk_info['owner'], pk_info['table_name'])
                table_id = table_id_map.get(key)
                
                if table_id:
                    pk_obj = DBPrimaryKey(
                        table_id=table_id,
                        column_name=pk_info['column_name'],
                        pk_pos=pk_info['position']
                    )
                    self.session.add(pk_obj)
                    stored_count += 1
                else:
                    print(f"Table not found for PK: {pk_info['owner']}.{pk_info['table_name']}.{pk_info['column_name']}")
            
            except Exception as e:
                print(f"Error storing primary key {pk_info['column_name']}: {e}")
        
        print(f"Stored {stored_count} primary key constraints")
        return stored_count
    
    def store_views(self, views_data: List[Dict]) -> int:
        """뷰 정보를 데이터베이스에 저장"""
        stored_count = 0
        
        # 기존 뷰 정보 삭제
        self.session.query(DBView).delete()
        
        for view_data in views_data:
            try:
                view_obj = DBView(
                    owner=view_data['owner'],
                    view_name=view_data['view_name'],
                    text=view_data['text']
                )
                self.session.add(view_obj)
                stored_count += 1
            
            except Exception as e:
                print(f"Error storing view {view_data['view_name']}: {e}")
        
        print(f"Stored {stored_count} views")
        return stored_count
    
    def load_project_schema(self, project_name: str) -> Dict[str, int]:
        """프로젝트의 데이터베이스 스키마 전체 로드"""
        schema_dir = self.get_schema_directory(project_name)
        
        if not os.path.exists(schema_dir):
            print(f"Schema directory not found: {schema_dir}")
            return {}
        
        print(f"Loading database schema from: {schema_dir}")
        
        try:
            # CSV 파일들 로드
            tables_data = self.load_tables_csv(schema_dir)
            columns_data = self.load_columns_csv(schema_dir)
            pk_data = self.load_primary_keys_csv(schema_dir)
            views_data = self.load_views_csv(schema_dir)
            
            # 데이터베이스에 저장
            table_id_map = self.store_tables(tables_data)
            columns_count = self.store_columns(columns_data, table_id_map)
            pk_count = self.store_primary_keys(pk_data, table_id_map)
            views_count = self.store_views(views_data)
            
            # 변경사항 커밋
            self.session.commit()
            
            summary = {
                'tables_loaded': len(table_id_map),
                'columns_loaded': columns_count,
                'primary_keys_loaded': pk_count,
                'views_loaded': views_count
            }
            
            print(f"Schema loading completed: {summary}")
            return summary
            
        except Exception as e:
            self.session.rollback()
            print(f"Error loading project schema: {e}")
            return {}
    
    def get_schema_statistics(self) -> Dict[str, int]:
        """데이터베이스 스키마 통계 조회"""
        stats = {
            'total_tables': self.session.query(DBTable).count(),
            'total_columns': self.session.query(DBColumn).count(),
            'total_primary_keys': self.session.query(DBPrimaryKey).count(),
            'total_views': self.session.query(DBView).count()
        }
        
        return stats
    
    def validate_schema_files(self, project_name: str) -> Dict[str, bool]:
        """스키마 파일 존재 여부 검증"""
        schema_dir = self.get_schema_directory(project_name)
        file_config = self.db_schema_config.get('files', {})
        
        validation = {}
        for file_type, filename in file_config.items():
            file_path = os.path.join(schema_dir, filename)
            validation[file_type] = os.path.exists(file_path)
        
        return validation
    
    def create_sample_schema_files(self, project_name: str):
        """샘플 스키마 CSV 파일 생성"""
        schema_dir = self.get_schema_directory(project_name)
        os.makedirs(schema_dir, exist_ok=True)
        
        # 샘플 테이블 데이터
        sample_tables = pd.DataFrame({
            'OWNER': ['SAMPLE', 'SAMPLE', 'SAMPLE'],
            'TABLE_NAME': ['CUSTOMERS', 'ORDERS', 'ORDER_ITEMS'],
            'STATUS': ['VALID', 'VALID', 'VALID']
        })
        
        # 샘플 컬럼 데이터
        sample_columns = pd.DataFrame({
            'OWNER': ['SAMPLE'] * 10,
            'TABLE_NAME': ['CUSTOMERS', 'CUSTOMERS', 'CUSTOMERS', 'CUSTOMERS',
                          'ORDERS', 'ORDERS', 'ORDERS', 
                          'ORDER_ITEMS', 'ORDER_ITEMS', 'ORDER_ITEMS'],
            'COLUMN_NAME': ['CUSTOMER_ID', 'NAME', 'EMAIL', 'CREATED_DATE',
                           'ORDER_ID', 'CUSTOMER_ID', 'ORDER_DATE',
                           'ORDER_ID', 'PRODUCT_ID', 'QUANTITY'],
            'DATA_TYPE': ['NUMBER', 'VARCHAR2', 'VARCHAR2', 'DATE',
                         'NUMBER', 'NUMBER', 'DATE',
                         'NUMBER', 'NUMBER', 'NUMBER'],
            'NULLABLE': ['N', 'N', 'Y', 'N', 'N', 'N', 'N', 'N', 'N', 'N']
        })
        
        # 샘플 기본키 데이터
        sample_pk = pd.DataFrame({
            'OWNER': ['SAMPLE', 'SAMPLE', 'SAMPLE'],
            'TABLE_NAME': ['CUSTOMERS', 'ORDERS', 'ORDER_ITEMS'],
            'COLUMN_NAME': ['CUSTOMER_ID', 'ORDER_ID', 'ORDER_ID'],
            'POSITION': [1, 1, 1]
        })
        
        # CSV 파일 저장
        file_config = self.db_schema_config.get('files', {})
        
        tables_file = file_config.get('tables', 'ALL_TABLES.csv')
        sample_tables.to_csv(os.path.join(schema_dir, tables_file), index=False, encoding='utf-8')
        
        columns_file = file_config.get('columns', 'ALL_TAB_COLUMNS.csv')
        sample_columns.to_csv(os.path.join(schema_dir, columns_file), index=False, encoding='utf-8')
        
        pk_file = file_config.get('primary_keys', 'PK_INFO.csv')
        sample_pk.to_csv(os.path.join(schema_dir, pk_file), index=False, encoding='utf-8')
        
        print(f"Sample schema files created in: {schema_dir}")


if __name__ == "__main__":
    # 테스트 코드
    from ..models.database import create_database_engine
    
    engine, SessionLocal = create_database_engine("sqlite:///./data/test_metadata.db")
    
    with SessionLocal() as session:
        config = {
            'db_schema': {
                'base_path': './PROJECT/{project_name}/DB_SCHEMA',
                'files': {
                    'tables': 'ALL_TABLES.csv',
                    'columns': 'ALL_TAB_COLUMNS.csv',
                    'primary_keys': 'PK_INFO.csv',
                    'views': 'ALL_VIEWS.csv'
                }
            }
        }
        
        loader = CSVSchemaLoader(session, config)
        
        # 샘플 스키마 파일 생성
        loader.create_sample_schema_files('sample-app')
        
        # 스키마 로드
        summary = loader.load_project_schema('sample-app')
        print(f"Load summary: {summary}")
        
        # 통계 조회
        stats = loader.get_schema_statistics()
        print(f"Schema statistics: {stats}")