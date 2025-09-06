"""
메타정보 생성 엔진

전체 메타정보 생성 프로세스를 조율하는 핵심 엔진입니다.
"""

import os
import hashlib
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from create_metadb.config import load_config, get_project_config
from create_metadb.database import DatabaseManager
from create_metadb.core.relationship_extractor import RelationshipExtractor
from create_metadb.core.business_classifier import BusinessClassifier
from create_metadb.core.lightweight_chunker import LightweightChunker
from create_metadb.llm import LLMClient
from create_metadb.analyzers.sql_join_analyzer import SqlJoinAnalyzer

class MetadataEngine:
    """메타정보 생성 엔진"""
    
    def __init__(self, project_name: str, config_path: str = None):
        self.project_name = project_name
        self.config = load_config(config_path)
        self.project_config = get_project_config(project_name, self.config)
        
        # 로깅 설정
        self.logger = self._setup_logging()
        
        # 컴포넌트 초기화
        self.db_manager = DatabaseManager(self.project_config)
        self.relationship_extractor = RelationshipExtractor(self.project_config)
        self.business_classifier = BusinessClassifier(self.project_config)
        self.lightweight_chunker = LightweightChunker(self.project_config)
        
        # LLM 클라이언트 (옵션)
        self.llm_client = None
        if self.project_config.get('llm', {}).get('enabled', False):
            self.llm_client = LLMClient(self.project_config['llm'])
        
        # SQL 조인 분석기
        self.sql_join_analyzer = SqlJoinAnalyzer(self.llm_client)
        
        self.logger.info(f"MetadataEngine 초기화 완료: {project_name}")
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(f"MetadataEngine_{self.project_name}")
        logger.setLevel(getattr(logging, self.project_config.get('logging', {}).get('level', 'INFO')))
        
        # 파일 핸들러
        log_file = self.project_config.get('logging', {}).get('file', 'logs/create_metadb.log')
        log_file = log_file.format(timestamp=datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            self.project_config.get('logging', {}).get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def generate_metadata(self, clean_mode: bool = False, del_clear_mode: bool = False) -> Dict[str, Any]:
        """메타정보 생성 메인 프로세스"""
        try:
            self.logger.info(f"메타정보 생성 시작: {self.project_name}")
            
            # 1. 데이터베이스 초기화
            if clean_mode:
                self.db_manager.clean_database()
                self.logger.info("데이터베이스 전체 초기화 완료")
                return {"status": "cleaned", "message": "데이터베이스가 초기화되었습니다."}
            
            if del_clear_mode:
                deleted_count = self.db_manager.clear_deleted_data()
                self.logger.info(f"삭제된 데이터 정리 완료: {deleted_count}건")
                return {"status": "cleared", "message": f"{deleted_count}건의 삭제된 데이터가 정리되었습니다."}
            
            # 2. 데이터베이스 스키마 생성
            self.db_manager.create_schema()
            
            # 3. 소스 파일 스캔 및 변동분 감지
            source_files = self._scan_source_files()
            changed_files = self._detect_changes(source_files)
            
            if not changed_files:
                self.logger.info("변경된 파일이 없습니다.")
                return {"status": "no_changes", "message": "변경된 파일이 없습니다."}
            
            self.logger.info(f"변경된 파일 {len(changed_files)}개 감지")
            
            # 4. 메타정보 생성
            stats = self._process_files(changed_files)
            
            # 5. 삭제된 파일 처리
            deleted_files = self._detect_deleted_files(source_files)
            if deleted_files:
                self._mark_files_as_deleted(deleted_files)
                stats['deleted_files'] = len(deleted_files)
            
            self.logger.info(f"메타정보 생성 완료: {stats}")
            return {"status": "success", "stats": stats}
            
        except Exception as e:
            self.logger.error(f"메타정보 생성 중 오류 발생: {e}")
            raise
    
    def _scan_source_files(self) -> List[str]:
        """소스 파일 스캔"""
        source_path = self.project_config.get('source_path', f'../project/{self.project_name}/src')
        source_files = []
        
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith(('.java', '.jsp', '.xml', '.sql')):
                    file_path = os.path.join(root, file)
                    source_files.append(file_path)
        
        return source_files
    
    def _detect_changes(self, source_files: List[str]) -> List[str]:
        """변동분 감지 (해시값 비교)"""
        changed_files = []
        
        for file_path in source_files:
            current_hash = self._calculate_file_hash(file_path)
            stored_hash = self.db_manager.get_file_hash(file_path)
            
            if current_hash != stored_hash:
                changed_files.append(file_path)
        
        return changed_files
    
    def _detect_deleted_files(self, current_files: List[str]) -> List[str]:
        """삭제된 파일 감지"""
        stored_files = self.db_manager.get_all_file_paths()
        current_file_set = set(current_files)
        
        deleted_files = []
        for stored_file in stored_files:
            if stored_file not in current_file_set:
                deleted_files.append(stored_file)
        
        return deleted_files
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """파일 해시값 계산"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception as e:
            self.logger.warning(f"파일 해시 계산 실패 {file_path}: {e}")
            return ""
    
    def _process_files(self, file_paths: List[str]) -> Dict[str, int]:
        """파일 처리 및 메타정보 생성"""
        stats = {
            'processed_files': 0,
            'chunks_created': 0,
            'relationships_created': 0,
            'business_classifications': 0,
            'llm_summaries': 0
        }
        
        for file_path in file_paths:
            try:
                self.logger.info(f"파일 처리 중: {file_path}")
                
                # 1. 청킹
                chunks = self.lightweight_chunker.chunk_file(file_path)
                stats['chunks_created'] += len(chunks)
                
                # 2. 관계 추출
                relationships = self.relationship_extractor.extract_relationships(file_path, chunks)
                stats['relationships_created'] += len(relationships)
                
                # 3. 비즈니스 분류
                classifications = self.business_classifier.classify_components(chunks)
                stats['business_classifications'] += len(classifications)
                
                # 4. LLM 요약 생성 (옵션)
                if self.llm_client:
                    summaries = self._generate_llm_summaries(chunks)
                    stats['llm_summaries'] += len(summaries)
                
                # 5. 데이터베이스 저장
                self.db_manager.save_chunks(chunks)
                self.db_manager.save_relationships(relationships)
                self.db_manager.save_business_classifications(classifications)
                
                if self.llm_client:
                    self.db_manager.save_llm_summaries(summaries)
                
                # 6. 파일 해시값 업데이트
                file_hash = self._calculate_file_hash(file_path)
                self.db_manager.update_file_hash(file_path, file_hash)
                
                stats['processed_files'] += 1
                
            except Exception as e:
                self.logger.error(f"파일 처리 실패 {file_path}: {e}")
                continue
        
        return stats
    
    def _generate_llm_summaries(self, chunks: List[Dict]) -> List[Dict]:
        """LLM 요약 생성"""
        summaries = []
        
        for chunk in chunks:
            try:
                summary = self.llm_client.generate_summary(
                    chunk['content'], 
                    chunk['type']
                )
                summaries.append({
                    'chunk_id': chunk['id'],
                    'summary_text': summary,
                    'summary_type': 'business_purpose',
                    'confidence_score': 0.8
                })
            except Exception as e:
                self.logger.warning(f"LLM 요약 생성 실패 {chunk['id']}: {e}")
                continue
        
        return summaries
    
    def _mark_files_as_deleted(self, file_paths: List[str]):
        """파일을 논리적 삭제로 처리"""
        for file_path in file_paths:
            self.db_manager.mark_file_as_deleted(file_path)
            self.logger.info(f"파일 논리적 삭제 처리: {file_path}")
