"""
데이터베이스 연결 관리

SQLite 데이터베이스 연결 및 CRUD 작업을 관리합니다.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .schema import DatabaseSchema

class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('output_db', 'metadata_optimized.db')
        self.logger = logging.getLogger(f"DatabaseManager")
        self.conn = None
        
        # 데이터베이스 디렉토리 생성
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """데이터베이스 연결"""
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=self.config.get('database', {}).get('connection_timeout', 30))
            self.conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
            self.logger.info(f"데이터베이스 연결 성공: {self.db_path}")
            return self.conn
        except Exception as e:
            self.logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.logger.info("데이터베이스 연결 해제")
    
    def create_schema(self):
        """스키마 생성"""
        try:
            if not self.conn:
                self.connect()
            
            schema_sql = DatabaseSchema.get_schema_sql()
            self.conn.executescript(schema_sql)
            self.conn.commit()
            
            self.logger.info("데이터베이스 스키마 생성 완료")
            
        except Exception as e:
            self.logger.error(f"스키마 생성 실패: {e}")
            raise
    
    def clean_database(self):
        """데이터베이스 전체 초기화"""
        try:
            if not self.conn:
                self.connect()
            
            clean_sql = DatabaseSchema.get_clean_schema_sql()
            self.conn.executescript(clean_sql)
            self.conn.commit()
            
            # 스키마 재생성
            self.create_schema()
            
            self.logger.info("데이터베이스 전체 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def clear_deleted_data(self) -> int:
        """del_yn='Y'인 데이터만 물리적 삭제"""
        try:
            if not self.conn:
                self.connect()
            
            clear_sql = DatabaseSchema.get_clear_deleted_sql()
            cursor = self.conn.cursor()
            cursor.executescript(clear_sql)
            
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            self.logger.info(f"삭제된 데이터 정리 완료: {deleted_count}건")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"삭제된 데이터 정리 실패: {e}")
            raise
    
    def save_chunks(self, chunks: List[Dict]):
        """청크 저장"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            for chunk in chunks:
                cursor.execute("""
                    INSERT OR REPLACE INTO file_index 
                    (project_id, file_path, file_name, file_type, file_size, 
                     package_name, class_name, business_context, hash_value, del_yn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'N')
                """, (
                    1,  # project_id
                    chunk.get('file_path', ''),
                    chunk.get('file_name', ''),
                    chunk.get('file_type', ''),
                    chunk.get('file_size', 0),
                    chunk.get('package_name', ''),
                    chunk.get('class_name', ''),
                    chunk.get('business_context', ''),
                    chunk.get('hash_value', '')
                ))
            
            self.conn.commit()
            self.logger.info(f"청크 저장 완료: {len(chunks)}개")
            
        except Exception as e:
            self.logger.error(f"청크 저장 실패: {e}")
            raise
    
    def save_relationships(self, relationships: List[Dict]):
        """관계 저장"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            for rel in relationships:
                cursor.execute("""
                    INSERT OR REPLACE INTO core_relationships 
                    (project_id, src_type, src_id, src_name, dst_type, dst_id, dst_name,
                     relationship_type, confidence, metadata, hash_value, del_yn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N')
                """, (
                    1,  # project_id
                    rel.get('source_type', ''),
                    rel.get('source_id', 0),
                    rel.get('source_name', ''),
                    rel.get('target_type', ''),
                    rel.get('target_id', 0),
                    rel.get('target_name', ''),
                    rel.get('relationship_type', ''),
                    rel.get('confidence', 1.0),
                    json.dumps(rel.get('metadata', {})),
                    rel.get('hash_value', '')
                ))
            
            self.conn.commit()
            self.logger.info(f"관계 저장 완료: {len(relationships)}개")
            
        except Exception as e:
            self.logger.error(f"관계 저장 실패: {e}")
            raise
    
    def save_business_classifications(self, classifications: List[Dict]):
        """비즈니스 분류 저장"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            for classification in classifications:
                cursor.execute("""
                    INSERT OR REPLACE INTO business_classifications 
                    (project_id, component_type, component_id, component_name,
                     business_domain, architecture_layer, functional_category,
                     complexity_level, learning_priority, hash_value, del_yn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'N')
                """, (
                    1,  # project_id
                    classification.get('component_type', ''),
                    classification.get('component_id', 0),
                    classification.get('component_name', ''),
                    classification.get('business_domain', ''),
                    classification.get('architecture_layer', ''),
                    classification.get('functional_category', ''),
                    classification.get('complexity_level', ''),
                    classification.get('learning_priority', 0),
                    classification.get('hash_value', '')
                ))
            
            self.conn.commit()
            self.logger.info(f"비즈니스 분류 저장 완료: {len(classifications)}개")
            
        except Exception as e:
            self.logger.error(f"비즈니스 분류 저장 실패: {e}")
            raise
    
    def save_llm_summaries(self, summaries: List[Dict]):
        """LLM 요약 저장"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            for summary in summaries:
                cursor.execute("""
                    INSERT OR REPLACE INTO llm_summaries 
                    (project_id, target_type, target_id, target_name,
                     summary_text, summary_type, confidence_score, hash_value, del_yn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'N')
                """, (
                    1,  # project_id
                    summary.get('target_type', ''),
                    summary.get('target_id', 0),
                    summary.get('target_name', ''),
                    summary.get('summary_text', ''),
                    summary.get('summary_type', ''),
                    summary.get('confidence_score', 0.0),
                    summary.get('hash_value', '')
                ))
            
            self.conn.commit()
            self.logger.info(f"LLM 요약 저장 완료: {len(summaries)}개")
            
        except Exception as e:
            self.logger.error(f"LLM 요약 저장 실패: {e}")
            raise
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """파일 해시값 조회"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT hash_value FROM file_index 
                WHERE file_path = ? AND NVL(del_yn, 'N') <> 'Y'
            """, (file_path,))
            
            result = cursor.fetchone()
            return result['hash_value'] if result else None
            
        except Exception as e:
            self.logger.error(f"파일 해시 조회 실패 {file_path}: {e}")
            return None
    
    def update_file_hash(self, file_path: str, hash_value: str):
        """파일 해시값 업데이트"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE file_index 
                SET hash_value = ?, last_modified = CURRENT_TIMESTAMP
                WHERE file_path = ?
            """, (hash_value, file_path))
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"파일 해시 업데이트 실패 {file_path}: {e}")
    
    def get_all_file_paths(self) -> List[str]:
        """모든 파일 경로 조회"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT file_path FROM file_index 
                WHERE NVL(del_yn, 'N') <> 'Y'
            """)
            
            return [row['file_path'] for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.error(f"파일 경로 조회 실패: {e}")
            return []
    
    def mark_file_as_deleted(self, file_path: str):
        """파일을 논리적 삭제로 처리"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            # 파일 인덱스 삭제 처리
            cursor.execute("""
                UPDATE file_index 
                SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
                WHERE file_path = ?
            """, (file_path,))
            
            # 관련 관계들도 삭제 처리
            cursor.execute("""
                UPDATE core_relationships 
                SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
                WHERE src_name = ? OR dst_name = ?
            """, (Path(file_path).name, Path(file_path).name))
            
            # 관련 분류들도 삭제 처리
            cursor.execute("""
                UPDATE business_classifications 
                SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
                WHERE component_name = ?
            """, (Path(file_path).stem,))
            
            # 관련 요약들도 삭제 처리
            cursor.execute("""
                UPDATE llm_summaries 
                SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
                WHERE target_name = ?
            """, (Path(file_path).stem,))
            
            self.conn.commit()
            self.logger.info(f"파일 논리적 삭제 처리 완료: {file_path}")
            
        except Exception as e:
            self.logger.error(f"파일 논리적 삭제 처리 실패 {file_path}: {e}")
    
    def get_statistics(self) -> Dict[str, int]:
        """통계 정보 조회"""
        try:
            if not self.conn:
                self.connect()
            
            cursor = self.conn.cursor()
            
            stats = {}
            
            # 파일 수
            cursor.execute("SELECT COUNT(*) FROM file_index WHERE NVL(del_yn, 'N') <> 'Y'")
            stats['files'] = cursor.fetchone()[0]
            
            # 관계 수
            cursor.execute("SELECT COUNT(*) FROM core_relationships WHERE NVL(del_yn, 'N') <> 'Y'")
            stats['relationships'] = cursor.fetchone()[0]
            
            # 분류 수
            cursor.execute("SELECT COUNT(*) FROM business_classifications WHERE NVL(del_yn, 'N') <> 'Y'")
            stats['classifications'] = cursor.fetchone()[0]
            
            # 요약 수
            cursor.execute("SELECT COUNT(*) FROM llm_summaries WHERE NVL(del_yn, 'N') <> 'Y'")
            stats['summaries'] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"통계 조회 실패: {e}")
            return {}
