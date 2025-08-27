"""
CSV 파일 로더
DB 스키마 정보 CSV 파일들을 로드하여 데이터베이스에 저장
"""

import csv
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..models.database import DbTable, DbColumn, DbPk, DbView

class CsvLoader:
    """CSV 파일을 로드하여 DB 스키마 정보를 저장하는 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # CSV 파일별 처리 매핑
        self.csv_handlers = {
            'ALL_TABLES.csv': self._load_tables,
            'ALL_TAB_COLUMNS.csv': self._load_columns,
            'ALL_TAB_COMMENTS.csv': self._load_table_comments,
            'ALL_COL_COMMENTS.csv': self._load_column_comments,
            'PK_INFO.csv': self._load_pk_info,
            'ALL_VIEWS.csv': self._load_views
        }
        
    async def load_csv(self, csv_path: str, project_id: int) -> Dict[str, int]:
        """
        CSV 파일 로드
        
        Args:
            csv_path: CSV 파일 경로
            project_id: 프로젝트 ID
            
        Returns:
            로드된 레코드 수
        """
        
        filename = os.path.basename(csv_path)
        
        if filename not in self.csv_handlers:
            self.logger.warning(f"지원되지 않는 CSV 파일: {filename}")
            return {'records': 0}
            
        self.logger.info(f"CSV 파일 로딩 중: {filename}")
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                # CSV 파일의 인코딩 감지 및 처리
                reader = csv.DictReader(f)
                rows = list(reader)
                
            handler = self.csv_handlers[filename]
            result = await handler(rows, project_id)
            
            self.logger.info(f"CSV 로드 완료: {filename}, 레코드 수: {result['records']}")
            return result
            
        except Exception as e:
            self.logger.error(f"CSV 로드 실패 {filename}: {e}")
            raise
            
    async def _load_tables(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """ALL_TABLES.csv 로드"""
        
        from ..models.database import DatabaseManager
        
        # 임시로 세션 생성 (실제로는 의존성 주입 필요)
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            for row in rows:
                # 필드명은 Oracle ALL_TABLES 뷰 구조에 따라 조정
                table = DbTable(
                    owner=row.get('OWNER', '').strip(),
                    table_name=row.get('TABLE_NAME', '').strip(),
                    status=row.get('STATUS', 'VALID').strip()
                )
                
                # 중복 확인
                existing = session.query(DbTable).filter(
                    DbTable.owner == table.owner,
                    DbTable.table_name == table.table_name
                ).first()
                
                if not existing:
                    session.add(table)
                    loaded_count += 1
                    
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _load_columns(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """ALL_TAB_COLUMNS.csv 로드"""
        
        from ..models.database import DatabaseManager
        
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            # 테이블 ID 매핑 생성
            tables = session.query(DbTable).all()
            table_map = {(t.owner, t.table_name): t.table_id for t in tables}
            
            for row in rows:
                owner = row.get('OWNER', '').strip()
                table_name = row.get('TABLE_NAME', '').strip()
                column_name = row.get('COLUMN_NAME', '').strip()
                
                # 테이블 ID 찾기
                table_key = (owner, table_name)
                if table_key not in table_map:
                    self.logger.warning(f"테이블을 찾을 수 없음: {owner}.{table_name}")
                    continue
                    
                column = DbColumn(
                    table_id=table_map[table_key],
                    column_name=column_name,
                    data_type=row.get('DATA_TYPE', '').strip(),
                    nullable=row.get('NULLABLE', 'Y').strip()
                )
                
                # 중복 확인
                existing = session.query(DbColumn).filter(
                    DbColumn.table_id == column.table_id,
                    DbColumn.column_name == column.column_name
                ).first()
                
                if not existing:
                    session.add(column)
                    loaded_count += 1
                    
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _load_table_comments(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """ALL_TAB_COMMENTS.csv 로드"""
        
        from ..models.database import DatabaseManager
        from ..models.database import Summary
        
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            # 테이블 ID 매핑 생성
            tables = session.query(DbTable).all()
            table_map = {(t.owner, t.table_name): t.table_id for t in tables}
            
            for row in rows:
                owner = row.get('OWNER', '').strip()
                table_name = row.get('TABLE_NAME', '').strip()
                comments = row.get('COMMENTS', '').strip()
                
                if not comments:  # 빈 코멘트는 건너뛰기
                    continue
                    
                table_key = (owner, table_name)
                if table_key not in table_map:
                    continue
                    
                # 테이블 코멘트를 Summary 테이블에 저장
                summary = Summary(
                    target_type='table',
                    target_id=table_map[table_key],
                    summary_type='db_comment',
                    lang='ko',
                    content=comments,
                    confidence=1.0  # 원본 코멘트는 신뢰도 최고
                )
                
                session.add(summary)
                loaded_count += 1
                
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _load_column_comments(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """ALL_COL_COMMENTS.csv 로드"""
        
        from ..models.database import DatabaseManager
        from ..models.database import Summary
        
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            # 컬럼 ID 매핑 생성 (조인 쿼리 필요)
            columns_query = session.query(DbColumn, DbTable.owner, DbTable.table_name).join(DbTable).all()
            column_map = {
                (owner, table_name, col.column_name): col.column_id 
                for col, owner, table_name in columns_query
            }
            
            for row in rows:
                owner = row.get('OWNER', '').strip()
                table_name = row.get('TABLE_NAME', '').strip()
                column_name = row.get('COLUMN_NAME', '').strip()
                comments = row.get('COMMENTS', '').strip()
                
                if not comments:  # 빈 코멘트는 건너뛰기
                    continue
                    
                column_key = (owner, table_name, column_name)
                if column_key not in column_map:
                    continue
                    
                # 컬럼 코멘트를 Summary 테이블에 저장
                summary = Summary(
                    target_type='column',
                    target_id=column_map[column_key],
                    summary_type='db_comment',
                    lang='ko',
                    content=comments,
                    confidence=1.0
                )
                
                session.add(summary)
                loaded_count += 1
                
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _load_pk_info(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """PK_INFO.csv 로드 (PK 컬럼 정보)"""
        
        from ..models.database import DatabaseManager
        
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            # 테이블 ID 매핑 생성
            tables = session.query(DbTable).all()
            table_map = {(t.owner, t.table_name): t.table_id for t in tables}
            
            for row in rows:
                owner = row.get('OWNER', '').strip()
                table_name = row.get('TABLE_NAME', '').strip()
                column_name = row.get('COLUMN_NAME', '').strip()
                pk_position = int(row.get('POSITION', '1'))
                
                table_key = (owner, table_name)
                if table_key not in table_map:
                    continue
                    
                pk_info = DbPk(
                    table_id=table_map[table_key],
                    column_name=column_name,
                    pk_pos=pk_position
                )
                
                # 중복 확인
                existing = session.query(DbPk).filter(
                    DbPk.table_id == pk_info.table_id,
                    DbPk.column_name == pk_info.column_name
                ).first()
                
                if not existing:
                    session.add(pk_info)
                    loaded_count += 1
                    
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _load_views(self, rows: List[Dict[str, str]], project_id: int) -> Dict[str, int]:
        """ALL_VIEWS.csv 로드"""
        
        from ..models.database import DatabaseManager
        
        db_manager = DatabaseManager(self.config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            for row in rows:
                view = DbView(
                    owner=row.get('OWNER', '').strip(),
                    view_name=row.get('VIEW_NAME', '').strip(),
                    text=row.get('TEXT', '').strip()  # 뷰 정의 SQL
                )
                
                # 중복 확인
                existing = session.query(DbView).filter(
                    DbView.owner == view.owner,
                    DbView.view_name == view.view_name
                ).first()
                
                if not existing:
                    session.add(view)
                    loaded_count += 1
                    
            session.commit()
            return {'records': loaded_count}
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def validate_csv_structure(self, csv_path: str) -> Dict[str, Any]:
        """
        CSV 파일 구조 검증
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            검증 결과
        """
        
        filename = os.path.basename(csv_path)
        
        # 예상 컬럼 구조 정의
        expected_columns = {
            'ALL_TABLES.csv': ['OWNER', 'TABLE_NAME', 'STATUS'],
            'ALL_TAB_COLUMNS.csv': ['OWNER', 'TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE', 'NULLABLE'],
            'ALL_TAB_COMMENTS.csv': ['OWNER', 'TABLE_NAME', 'COMMENTS'],
            'ALL_COL_COMMENTS.csv': ['OWNER', 'TABLE_NAME', 'COLUMN_NAME', 'COMMENTS'],
            'PK_INFO.csv': ['OWNER', 'TABLE_NAME', 'COLUMN_NAME', 'POSITION'],
            'ALL_VIEWS.csv': ['OWNER', 'VIEW_NAME', 'TEXT']
        }
        
        if filename not in expected_columns:
            return {'valid': False, 'reason': f'지원되지 않는 파일: {filename}'}
            
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                actual_columns = reader.fieldnames
                
                expected = set(expected_columns[filename])
                actual = set(actual_columns) if actual_columns else set()
                
                missing_columns = expected - actual
                extra_columns = actual - expected
                
                result = {
                    'valid': len(missing_columns) == 0,
                    'expected_columns': list(expected),
                    'actual_columns': list(actual),
                    'missing_columns': list(missing_columns),
                    'extra_columns': list(extra_columns)
                }
                
                if not result['valid']:
                    result['reason'] = f'필수 컬럼 누락: {missing_columns}'
                    
                return result
                
        except Exception as e:
            return {'valid': False, 'reason': f'파일 읽기 오류: {e}'}