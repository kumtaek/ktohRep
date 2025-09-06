"""
테이블 메타데이터 로더
CSV 파일에서 테이블 정보를 불러와서 메타DB에 저장하는 기능
"""
import csv
import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class TableMetadataLoader:
    """CSV에서 테이블 메타데이터를 불러오는 클래스"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.logger = logging.getLogger(__name__)
    
    def load_tables_from_csv(self, project_id: int, csv_file_path: str) -> Dict:
        """
        CSV 파일에서 테이블 정보를 읽어와 메타DB에 저장
        
        CSV 예상 형식:
        table_name, column_name, data_type, is_primary_key, is_foreign_key, 
        foreign_table, foreign_column, is_nullable, default_value, comment
        """
        try:
            loaded_tables = {}
            loaded_columns = []
            
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    table_name = row.get('table_name', '').strip()
                    column_name = row.get('column_name', '').strip()
                    data_type = row.get('data_type', '').strip()
                    
                    if not table_name or not column_name:
                        continue
                    
                    # 테이블 컴포넌트 추가
                    if table_name not in loaded_tables:
                        table_component_id = self.metadata_engine.add_component(
                            project_id=project_id,
                            file_id=None,  # CSV는 파일이 아님
                            component_name=table_name,
                            component_type='table',
                            line_start=None,
                            line_end=None
                        )
                        loaded_tables[table_name] = table_component_id
                        
                        # 비즈니스 태그 추가 (선택적)
                        try:
                            domain = self._classify_table_domain(table_name)
                            if domain:
                                self.metadata_engine.add_business_tag(
                                    project_id, table_component_id, domain, 'data'
                                )
                        except Exception as e:
                            self.logger.warning(f"비즈니스 태그 추가 실패: {e}")
                    
                    # 컬럼 정보 저장
                    column_info = {
                        'table_name': table_name,
                        'column_name': column_name,
                        'data_type': data_type,
                        'is_primary_key': row.get('is_primary_key', '').upper() == 'Y',
                        'is_foreign_key': row.get('is_foreign_key', '').upper() == 'Y',
                        'foreign_table': row.get('foreign_table', '').strip(),
                        'foreign_column': row.get('foreign_column', '').strip(),
                        'is_nullable': row.get('is_nullable', '').upper() != 'N',
                        'default_value': row.get('default_value', '').strip(),
                        'comment': row.get('comment', '').strip()
                    }
                    loaded_columns.append(column_info)
            
            self.logger.info(f"CSV에서 {len(loaded_tables)}개 테이블, {len(loaded_columns)}개 컬럼 로드 완료")
            
            return {
                'success': True,
                'loaded_tables': loaded_tables,
                'loaded_columns': loaded_columns,
                'table_count': len(loaded_tables),
                'column_count': len(loaded_columns)
            }
            
        except Exception as e:
            self.logger.error(f"CSV 테이블 로드 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_tables': {},
                'loaded_columns': []
            }
    
    def _classify_table_domain(self, table_name: str) -> Optional[str]:
        """테이블명으로 비즈니스 도메인 분류"""
        name_lower = table_name.lower()
        
        # 사용자 관련
        if any(keyword in name_lower for keyword in ['user', 'member', 'customer', 'account']):
            return 'user'
        # 주문 관련
        elif any(keyword in name_lower for keyword in ['order', 'cart', 'purchase', 'payment']):
            return 'order'
        # 상품 관련
        elif any(keyword in name_lower for keyword in ['product', 'item', 'goods', 'inventory']):
            return 'product'
        # 결제 관련
        elif any(keyword in name_lower for keyword in ['payment', 'billing', 'invoice']):
            return 'payment'
        # 시스템 관련
        elif any(keyword in name_lower for keyword in ['log', 'audit', 'config', 'setting']):
            return 'system'
        # 코드 테이블
        elif any(keyword in name_lower for keyword in ['code', 'type', 'category', 'status']):
            return 'reference'
        else:
            return None
    
    def create_foreign_key_relationships(self, project_id: int, loaded_tables: Dict, 
                                       loaded_columns: List[Dict]) -> Dict:
        """컬럼 정보를 바탕으로 외래키 관계를 생성"""
        try:
            relationships_created = []
            dummy_tables_created = {}
            
            for column_info in loaded_columns:
                if not column_info['is_foreign_key']:
                    continue
                
                source_table = column_info['table_name']
                target_table = column_info['foreign_table']
                target_column = column_info['foreign_column']
                
                if not target_table:
                    continue
                
                # 소스 테이블 ID 확인
                source_table_id = loaded_tables.get(source_table)
                if not source_table_id:
                    continue
                
                # 타겟 테이블 ID 확인 (없으면 더미 생성)
                target_table_id = loaded_tables.get(target_table)
                if not target_table_id:
                    # 더미 테이블 생성
                    target_table_id = self._create_dummy_table(
                        project_id, target_table
                    )
                    dummy_tables_created[target_table] = target_table_id
                    loaded_tables[target_table] = target_table_id
                
                # 외래키 관계 생성
                try:
                    self.metadata_engine.add_relationship(
                        project_id=project_id,
                        src_component_id=source_table_id,
                        dst_component_id=target_table_id,
                        relationship_type='foreign_key',
                        confidence=1.0
                    )
                    self.logger.info(f"외래키 관계 생성: {source_table} -> {target_table}")
                except Exception as e:
                    self.logger.error(f"외래키 관계 생성 실패: {source_table} -> {target_table}, 오류: {e}")
                    continue
                
                relationships_created.append({
                    'source_table': source_table,
                    'target_table': target_table,
                    'source_column': column_info['column_name'],
                    'target_column': target_column
                })
            
            self.logger.info(f"외래키 관계 {len(relationships_created)}개 생성 완료")
            self.logger.info(f"더미 테이블 {len(dummy_tables_created)}개 생성 완료")
            
            return {
                'success': True,
                'relationships_created': relationships_created,
                'dummy_tables_created': dummy_tables_created,
                'relationship_count': len(relationships_created),
                'dummy_table_count': len(dummy_tables_created)
            }
            
        except Exception as e:
            self.logger.error(f"외래키 관계 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'relationships_created': [],
                'dummy_tables_created': {}
            }
    
    def _create_dummy_table(self, project_id: int, table_name: str) -> int:
        """존재하지 않는 참조 테이블을 위한 더미 테이블 생성"""
        component_id = self.metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name=table_name,
            component_type='table_dummy',  # 더미 테이블 표시
            line_start=None,
            line_end=None
        )
        
        # 더미 테이블 비즈니스 태그 (선택적)
        try:
            domain = self._classify_table_domain(table_name)
            if domain:
                self.metadata_engine.add_business_tag(
                    project_id, component_id, domain, 'data_dummy'
                )
        except Exception as e:
            self.logger.warning(f"더미 테이블 비즈니스 태그 추가 실패: {e}")
        
        self.logger.info(f"더미 테이블 생성: {table_name} (ID: {component_id})")
        return component_id