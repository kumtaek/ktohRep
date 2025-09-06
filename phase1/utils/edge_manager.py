#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
엣지 관리자 - 중복 방지 및 더미 청크 생성을 포함한 엣지 관리 시스템
"""

import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Set, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from models.database import (
    Edge, Class, Method, File, SqlUnit, DbTable, DbColumn, 
    Project, Chunk
)

logger = logging.getLogger(__name__)


class EdgeManager:
    """엣지 관리자 - 중복 방지, 더미 청크 생성, 엣지 검증"""
    
    def __init__(self, db_session: Session, project_id: int = 1, config_path: str = None):
        self.db_session = db_session
        self.project_id = project_id
        self.config = self._load_config(config_path)
        
        # 중복 방지를 위한 캐시
        self.existing_edges_cache: Set[Tuple] = set()
        self.dummy_chunks_cache: Dict[str, int] = {}  # "type:identifier" -> chunk_id
        
        # 통계
        self.stats = {
            'edges_created': 0,
            'edges_skipped_duplicate': 0,
            'dummy_chunks_created': 0,
            'errors': 0
        }
        
        self._init_existing_edges_cache()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """설정 파일 로드"""
        if not config_path:
            # 기본 설정 파일 경로들 시도
            possible_paths = [
                'config/phase1/config.yaml',
                'phase1/config/config.yaml',
                'config.yaml'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"설정 파일 로드 완료: {config_path}")
                return config
            except Exception as e:
                logger.error(f"설정 파일 로드 실패 {config_path}: {e}")
        
        # 기본 설정값
        default_config = {
            'database': {
                'default_schema_owner': 'SAMPLE',
                'default_table_owner': 'SAMPLE'
            },
            'edge_generation': {
                'enable_dummy_chunks': True,
                'min_confidence': 0.3,
                'max_edges_per_source': 100
            }
        }
        
        logger.warning("기본 설정값 사용")
        return default_config
    
    def _init_existing_edges_cache(self):
        """기존 엣지 캐시 초기화"""
        existing_edges = self.db_session.query(Edge).filter(
            Edge.project_id == self.project_id
        ).all()
        
        for edge in existing_edges:
            edge_key = (
                edge.src_type, edge.src_id,
                edge.dst_type, edge.dst_id, 
                edge.edge_kind
            )
            self.existing_edges_cache.add(edge_key)
        
        logger.info(f"기존 엣지 캐시 초기화: {len(self.existing_edges_cache)}개")
    
    def create_edge(self, src_type: str, src_id: int, dst_type: str, dst_id: int,
                   edge_kind: str, confidence: float = 0.5, meta: str = "",
                   auto_create_dummy: bool = True) -> Optional[Edge]:
        """엣지 생성 (중복 체크 및 더미 청크 생성 포함)"""
        
        # 1. 중복 체크
        edge_key = (src_type, src_id, dst_type, dst_id, edge_kind)
        if edge_key in self.existing_edges_cache:
            self.stats['edges_skipped_duplicate'] += 1
            logger.debug(f"중복 엣지 스킵: {src_type}:{src_id} → {dst_type}:{dst_id} ({edge_kind})")
            return None
        
        # 2. 소스 청크 존재 여부 확인
        if not self._chunk_exists(src_type, src_id):
            if auto_create_dummy:
                src_id = self._create_dummy_chunk(src_type, src_id, f"Source for edge: {edge_kind}")
                if not src_id:
                    self.stats['errors'] += 1
                    return None
            else:
                logger.warning(f"소스 청크 없음: {src_type}:{src_id}")
                self.stats['errors'] += 1
                return None
        
        # 3. 대상 청크 존재 여부 확인
        if dst_id and not self._chunk_exists(dst_type, dst_id):
            if auto_create_dummy:
                dst_id = self._create_dummy_chunk(dst_type, dst_id, f"Target for edge: {edge_kind}")
                if not dst_id:
                    self.stats['errors'] += 1
                    return None
            else:
                logger.warning(f"대상 청크 없음: {dst_type}:{dst_id}")
                self.stats['errors'] += 1
                return None
        
        # 4. 신뢰도 검증
        min_confidence = self.config.get('edge_generation', {}).get('min_confidence', 0.3)
        if confidence < min_confidence:
            logger.debug(f"신뢰도 부족으로 스킵: {confidence} < {min_confidence}")
            return None
        
        # 5. 엣지 생성
        try:
            edge = Edge(
                project_id=self.project_id,
                src_type=src_type,
                src_id=src_id,
                dst_type=dst_type,
                dst_id=dst_id,
                edge_kind=edge_kind,
                confidence=confidence,
                meta=meta[:500] if meta else ""  # 메타데이터 길이 제한
            )
            
            self.db_session.add(edge)
            self.db_session.flush()  # ID 할당을 위해 플러시
            
            # 캐시에 추가
            self.existing_edges_cache.add(edge_key)
            self.stats['edges_created'] += 1
            
            if self.stats['edges_created'] % 50 == 0:
                logger.info(f"엣지 생성 진행: {self.stats['edges_created']}개")
            
            return edge
            
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            self.stats['errors'] += 1
            return None
    
    def _chunk_exists(self, target_type: str, target_id: int) -> bool:
        """청크가 존재하는지 확인"""
        if target_type == 'class':
            return self.db_session.query(Class).filter(Class.class_id == target_id).first() is not None
        elif target_type == 'method':
            return self.db_session.query(Method).filter(Method.method_id == target_id).first() is not None
        elif target_type == 'file':
            return self.db_session.query(File).filter(File.file_id == target_id).first() is not None
        elif target_type == 'sql_unit':
            return self.db_session.query(SqlUnit).filter(SqlUnit.sql_id == target_id).first() is not None
        elif target_type == 'table':
            return self.db_session.query(DbTable).filter(DbTable.table_id == target_id).first() is not None
        elif target_type == 'column':
            return self.db_session.query(DbColumn).filter(DbColumn.column_id == target_id).first() is not None
        else:
            # 일반 청크 테이블에서 확인
            return self.db_session.query(Chunk).filter(
                Chunk.target_type == target_type,
                Chunk.target_id == target_id
            ).first() is not None
    
    def _create_dummy_chunk(self, target_type: str, original_id: int, description: str = "") -> Optional[int]:
        """더미 청크 생성"""
        
        # 캐시 확인
        cache_key = f"{target_type}:{original_id}"
        if cache_key in self.dummy_chunks_cache:
            return self.dummy_chunks_cache[cache_key]
        
        try:
            if target_type == 'table':
                # 테이블은 DbTable에 더미 레코드 생성
                return self._create_dummy_table(original_id, description)
            elif target_type == 'class':
                # 클래스는 Class에 더미 레코드 생성
                return self._create_dummy_class(original_id, description)
            else:
                # 기타는 Chunk 테이블에 더미 생성
                return self._create_dummy_in_chunks_table(target_type, original_id, description)
                
        except Exception as e:
            logger.error(f"더미 청크 생성 실패 {target_type}:{original_id}: {e}")
            return None
    
    def _create_dummy_table(self, table_id: int, description: str) -> Optional[int]:
        """더미 테이블 생성"""
        
        # 이미 존재하는지 확인
        existing_table = self.db_session.query(DbTable).filter(DbTable.table_id == table_id).first()
        if existing_table:
            return table_id
        
        # 기본 owner 가져오기
        default_owner = self.config.get('database', {}).get('default_table_owner', 'SAMPLE')
        
        # 테이블명 추론 (ID 기반 또는 description에서)
        table_name = f"DUMMY_TABLE_{table_id}"
        if "table:" in description:
            extracted_name = description.split("table:")[-1].strip()
            if extracted_name:
                table_name = extracted_name.upper()
        
        try:
            dummy_table = DbTable(
                table_id=table_id,
                owner=default_owner,
                table_name=table_name,
                table_type='TABLE',
                comments=f"DUMMY: {description}",
                num_rows=0,
                created_at=None,
                last_analyzed=None,
                is_dummy=True  # 더미 플래그 추가 (스키마에 컬럼이 있다면)
            )
            
            self.db_session.add(dummy_table)
            self.db_session.flush()
            
            # 캐시에 추가
            cache_key = f"table:{table_id}"
            self.dummy_chunks_cache[cache_key] = table_id
            self.stats['dummy_chunks_created'] += 1
            
            logger.debug(f"더미 테이블 생성: {default_owner}.{table_name} (ID: {table_id})")
            return table_id
            
        except Exception as e:
            logger.error(f"더미 테이블 생성 실패: {e}")
            return None
    
    def _create_dummy_class(self, class_id: int, description: str) -> Optional[int]:
        """더미 클래스 생성"""
        
        existing_class = self.db_session.query(Class).filter(Class.class_id == class_id).first()
        if existing_class:
            return class_id
        
        # 클래스명 추론
        class_name = f"DummyClass_{class_id}"
        fqn = f"com.example.dummy.{class_name}"
        
        if "class:" in description:
            extracted_fqn = description.split("class:")[-1].strip()
            if extracted_fqn and extracted_fqn.startswith('com.example'):
                fqn = extracted_fqn
                class_name = fqn.split('.')[-1]
        
        try:
            # 파일 정보도 필요한 경우 더미 파일 생성
            dummy_file_id = self._get_or_create_dummy_file(f"{class_name}.java")
            
            dummy_class = Class(
                class_id=class_id,
                file_id=dummy_file_id,
                fqn=fqn,
                name=class_name,
                package='.'.join(fqn.split('.')[:-1]),
                modifiers='public',
                extends=None,
                implements=None,
                annotations=None,
                comments=f"DUMMY: {description}",
                start_line=1,
                end_line=1
            )
            
            self.db_session.add(dummy_class)
            self.db_session.flush()
            
            cache_key = f"class:{class_id}"
            self.dummy_chunks_cache[cache_key] = class_id
            self.stats['dummy_chunks_created'] += 1
            
            logger.debug(f"더미 클래스 생성: {fqn} (ID: {class_id})")
            return class_id
            
        except Exception as e:
            logger.error(f"더미 클래스 생성 실패: {e}")
            return None
    
    def _create_dummy_in_chunks_table(self, target_type: str, target_id: int, description: str) -> Optional[int]:
        """Chunk 테이블에 더미 청크 생성"""
        
        try:
            dummy_chunk = Chunk(
                target_type=target_type,
                target_id=target_id,
                content=f"DUMMY CHUNK: {description}",
                token_count=0,
                hash=f"dummy_{target_type}_{target_id}"
            )
            
            self.db_session.add(dummy_chunk)
            self.db_session.flush()
            
            cache_key = f"{target_type}:{target_id}"
            self.dummy_chunks_cache[cache_key] = dummy_chunk.chunk_id
            self.stats['dummy_chunks_created'] += 1
            
            logger.debug(f"더미 청크 생성: {target_type}:{target_id}")
            return target_id
            
        except Exception as e:
            logger.error(f"더미 청크 생성 실패: {e}")
            return None
    
    def _get_or_create_dummy_file(self, filename: str) -> int:
        """더미 파일 가져오기 또는 생성"""
        
        # 기존 파일 확인 (경로 패턴으로)
        existing_file = self.db_session.query(File).filter(
            File.path.like(f'%{filename}')
        ).first()
        
        if existing_file:
            return existing_file.file_id
        
        try:
            # 새 더미 파일 생성
            dummy_file = File(
                path=f"/dummy/{filename}",
                language='java',
                encoding='utf-8',
                size=0,
                lines=1,
                created_at=None,
                modified_at=None
            )
            
            self.db_session.add(dummy_file)
            self.db_session.flush()
            
            logger.debug(f"더미 파일 생성: {filename} (ID: {dummy_file.file_id})")
            return dummy_file.file_id
            
        except Exception as e:
            logger.error(f"더미 파일 생성 실패: {e}")
            return 1  # 기본값
    
    def create_edge_by_names(self, src_type: str, src_name: str, dst_type: str, dst_name: str,
                           edge_kind: str, confidence: float = 0.5, meta: str = "") -> Optional[Edge]:
        """이름 기반 엣지 생성 (ID 조회 후 생성)"""
        
        # 소스 ID 찾기
        src_id = self._find_id_by_name(src_type, src_name)
        if not src_id:
            logger.warning(f"소스 ID 찾기 실패: {src_type}:{src_name}")
            return None
        
        # 대상 ID 찾기
        dst_id = self._find_id_by_name(dst_type, dst_name)
        if not dst_id:
            logger.warning(f"대상 ID 찾기 실패: {dst_type}:{dst_name}")
            return None
        
        return self.create_edge(src_type, src_id, dst_type, dst_id, edge_kind, confidence, meta)
    
    def _find_id_by_name(self, target_type: str, name: str) -> Optional[int]:
        """이름으로 ID 찾기"""
        try:
            if target_type == 'class':
                obj = self.db_session.query(Class).filter(
                    (Class.fqn == name) | (Class.name == name)
                ).first()
                return obj.class_id if obj else None
            
            elif target_type == 'table':
                obj = self.db_session.query(DbTable).filter(
                    DbTable.table_name.ilike(name)
                ).first()
                return obj.table_id if obj else None
            
            elif target_type == 'file':
                obj = self.db_session.query(File).filter(
                    File.path.like(f'%{name}%')
                ).first()
                return obj.file_id if obj else None
                
            # 다른 타입들도 필요시 추가
            return None
            
        except Exception as e:
            logger.error(f"ID 찾기 실패 {target_type}:{name}: {e}")
            return None
    
    def remove_duplicates(self) -> int:
        """중복 엣지 제거"""
        logger.info("중복 엣지 제거 시작")
        
        # 중복 엣지 찾기 (같은 src, dst, kind를 가진 엣지들)
        duplicate_query = """
        SELECT src_type, src_id, dst_type, dst_id, edge_kind, COUNT(*) as cnt
        FROM edges 
        WHERE project_id = ?
        GROUP BY src_type, src_id, dst_type, dst_id, edge_kind
        HAVING COUNT(*) > 1
        """
        
        duplicates = self.db_session.execute(duplicate_query, (self.project_id,)).fetchall()
        
        removed_count = 0
        for dup in duplicates:
            # 첫 번째를 제외하고 나머지 삭제
            edges_to_remove = self.db_session.query(Edge).filter(
                Edge.project_id == self.project_id,
                Edge.src_type == dup.src_type,
                Edge.src_id == dup.src_id,
                Edge.dst_type == dup.dst_type,
                Edge.dst_id == dup.dst_id,
                Edge.edge_kind == dup.edge_kind
            ).offset(1).all()  # 첫 번째 건너뛰기
            
            for edge in edges_to_remove:
                self.db_session.delete(edge)
                removed_count += 1
        
        if removed_count > 0:
            self.db_session.commit()
            logger.info(f"중복 엣지 제거 완료: {removed_count}개")
        
        return removed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """생성 통계 반환"""
        return {
            **self.stats,
            'total_edges_in_cache': len(self.existing_edges_cache),
            'dummy_chunks_cached': len(self.dummy_chunks_cache)
        }
    
    def commit_changes(self):
        """변경사항 커밋"""
        try:
            self.db_session.commit()
            logger.info(f"엣지 생성 커밋 완료: {self.stats}")
        except Exception as e:
            logger.error(f"커밋 실패: {e}")
            self.db_session.rollback()
            raise