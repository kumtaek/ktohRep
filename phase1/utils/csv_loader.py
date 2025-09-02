"""
CSV 파일 로더
DB 스키마 정보 CSV 파일들을 로드하여 데이터베이스에 저장
"""

import csv
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from models.database import DbTable, DbColumn, DbPk, DbView

class CsvLoader:
    """CSV 파일을 로드하여 DB 스키마 정보를 저장하는 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        CSV 로더 초기화
        
        Args:
            config: 데이터베이스 설정 딕셔너리
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # CSV 파일별 처리 매핑
        self.csv_handlers = {
            'ALL_TABLES.csv': self._load_tables,
            'ALL_TAB_COLUMNS.csv': self._load_columns,
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
        """
        Oracle ALL_TABLES.csv 파일을 로드하여 테이블 정보를 데이터베이스에 저장
        
        Args:
            rows: CSV에서 읽은 데이터 행들
            project_id: 프로젝트 ID
            
        Returns:
            로드된 레코드 수 정보
        """
        
        from models.database import DatabaseManager
        
        # 임시로 세션 생성 (실제로는 의존성 주입 필요)
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
        db_manager.initialize()  # 데이터베이스 초기화 추가
        session = db_manager.get_session()
        
        try:
            loaded_count = 0
            
            for row in rows:
                owner = row.get('OWNER', '').strip()
                table_name = row.get('TABLE_NAME', '').strip()
                comments = (row.get('COMMENTS') or '').strip()
                status = (row.get('STATUS') or 'VALID').strip()

                # 기존 레코드 확인
                existing = session.query(DbTable).filter(
                    DbTable.owner == owner,
                    DbTable.table_name == table_name
                ).first()

                if existing:
                    # CSV에서 정확한 정보가 제공되므로 모든 필드 업데이트
                    # 조인에서 추론된 정보든 기존 정보든 CSV 정보로 덮어쓰기
                    was_inferred = existing.table_type == 'INFERRED'
                    
                    if comments:
                        existing.table_comment = comments
                        existing.comments = comments  # comments 필드도 업데이트
                    if status:
                        existing.status = status
                    
                    # 추론된 테이블에서 실제 테이블로 업그레이드
                    existing.table_type = 'TABLE'  # 실제 CSV 정보이므로 TABLE로 변경
                    existing.updated_at = datetime.utcnow()
                    
                    if was_inferred:
                        self.logger.info(f"CSV에서 테이블 정보 덮어쓰기: {table_name} (조인 추론 → 실제 정보)")
                    else:
                        self.logger.debug(f"CSV에서 테이블 정보 업데이트: {table_name}")
                else:
                    table = DbTable(
                        owner=owner,
                        table_name=table_name,
                        status=status,
                        table_comment=comments
                    )
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
        
        from models.database import DatabaseManager
        
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
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
                col_comments = (row.get('COLUMN_COMMENTS') or '').strip()
                
                # 테이블 ID 찾기
                table_key = (owner, table_name)
                if table_key not in table_map:
                    self.logger.warning(f"테이블을 찾을 수 없음: {owner}.{table_name}")
                    continue
                    
                column = DbColumn(
                    table_id=table_map[table_key],
                    column_name=column_name,
                    data_type=row.get('DATA_TYPE', '').strip(),
                    nullable=row.get('NULLABLE', 'Y').strip(),
                    column_comment=col_comments
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
        
        from models.database import DatabaseManager
        from models.database import Summary
        
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
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
        
        from models.database import DatabaseManager
        from models.database import Summary
        
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
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
        
        from models.database import DatabaseManager
        
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
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
                # Allow legacy header 'PK_POS' too
                pk_position = int((row.get('POSITION') or row.get('PK_POS') or '1'))
                
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
        
        from models.database import DatabaseManager
        
        db_config = self.config.get('database', {}).get('project', {})
        db_manager = DatabaseManager(db_config)
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
            'ALL_TABLES.csv': ['OWNER', 'TABLE_NAME', 'COMMENTS'],
            'ALL_TAB_COLUMNS.csv': ['OWNER', 'TABLE_NAME', 'COLUMN_NAME', 'DATA_TYPE', 'NULLABLE', 'COLUMN_COMMENTS'],
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
    
    async def load_project_db_schema(self, project_name: str, project_id: int) -> Dict[str, Any]:
        """
        프로젝트별 DB 스키마 CSV 파일 자동 검색 및 로드
        
        Args:
            project_name: 프로젝트 이름
            project_id: 프로젝트 ID
            
        Returns:
            로드 결과 정보
        """
        import os
        
        # 프로젝트별 db_schema 디렉토리 경로
        db_schema_dir = f"./project/{project_name}/db_schema"
        
        result = {
            'loaded_files': {},
            'errors': [],
            'total_records': 0,
            'schema_dir': db_schema_dir
        }
        
        # db_schema 디렉토리가 존재하지 않으면 생성
        if not os.path.exists(db_schema_dir):
            os.makedirs(db_schema_dir, exist_ok=True)
            self.logger.info(f"DB 스키마 디렉토리 생성: {db_schema_dir}")
            result['errors'].append(f"DB 스키마 디렉토리가 비어있습니다: {db_schema_dir}")
            return result
        
        # 지원되는 CSV 파일 목록
        supported_files = list(self.csv_handlers.keys())
        
        # 디렉토리에서 CSV 파일 검색
        found_files = []
        for filename in os.listdir(db_schema_dir):
            if filename.endswith('.csv') and filename in supported_files:
                found_files.append(filename)
        
        if not found_files:
            self.logger.warning(f"DB 스키마 CSV 파일을 찾을 수 없습니다: {db_schema_dir}")
            result['errors'].append(f"지원되는 CSV 파일이 없습니다. 필요한 파일: {supported_files}")
            return result
        
        # 찾은 CSV 파일들을 순서대로 로드
        load_order = ['ALL_TABLES.csv', 'ALL_TAB_COLUMNS.csv', 'PK_INFO.csv', 'ALL_VIEWS.csv']
        
        for filename in load_order:
            if filename in found_files:
                csv_path = os.path.join(db_schema_dir, filename)
                try:
                    self.logger.info(f"DB 스키마 CSV 로드 중: {filename}")
                    load_result = await self.load_csv(csv_path, project_id)
                    
                    result['loaded_files'][filename] = load_result
                    result['total_records'] += sum(load_result.values())
                    self.logger.info(f"DB 스키마 CSV 로드 완료: {filename} ({sum(load_result.values())} records)")
                    
                except Exception as e:
                    error_msg = f"{filename} 로드 실패: {e}"
                    self.logger.error(error_msg)
                    result['errors'].append(error_msg)
        
        return result
