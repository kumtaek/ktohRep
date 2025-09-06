#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
청크 위치 추적기
각 청크(메서드, 쿼리, 함수 등)의 소스 파일 내 정확한 위치 정보를 관리합니다.
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from sqlalchemy.orm import Session
from models.database import Class, Method, File, SqlUnit, Chunk

logger = logging.getLogger(__name__)


@dataclass
class ChunkLocation:
    """청크 위치 정보"""
    file_path: str           # 소스 파일 경로
    start_line: int          # 시작 라인 번호
    end_line: int           # 끝 라인 번호
    start_column: int = 0    # 시작 컬럼 (선택적)
    end_column: int = 0     # 끝 컬럼 (선택적)
    content_preview: str = ""  # 내용 미리보기 (처음 100자)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'file_path': self.file_path,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'start_column': self.start_column,
            'end_column': self.end_column,
            'content_preview': self.content_preview,
            'line_count': self.end_line - self.start_line + 1
        }
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class ChunkLocationTracker:
    """청크 위치 추적기"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.file_content_cache: Dict[str, List[str]] = {}  # 파일별 라인 캐시
        
    def track_java_method_location(self, method_id: int, class_fqn: str, method_name: str) -> Optional[ChunkLocation]:
        """Java 메서드의 위치 정보 추적"""
        try:
            # Method 정보 조회
            method = self.db_session.query(Method).filter(Method.method_id == method_id).first()
            if not method:
                logger.warning(f"메서드 정보 없음: {method_id}")
                return None
            
            # 클래스 정보를 통해 파일 정보 조회
            class_obj = self.db_session.query(Class).filter(Class.fqn == class_fqn).first()
            if not class_obj:
                logger.warning(f"클래스 정보 없음: {class_fqn}")
                return None
            
            # 파일 정보 조회
            file_obj = self.db_session.query(File).filter(File.file_id == class_obj.file_id).first()
            if not file_obj:
                logger.warning(f"파일 정보 없음: {class_obj.file_id}")
                return None
            
            # 메서드가 이미 라인 정보를 가지고 있는 경우
            if hasattr(method, 'start_line') and method.start_line:
                content_preview = self._get_content_preview(file_obj.path, method.start_line, method.end_line or method.start_line)
                return ChunkLocation(
                    file_path=file_obj.path,
                    start_line=method.start_line,
                    end_line=method.end_line or method.start_line,
                    content_preview=content_preview
                )
            
            # 파일에서 메서드 위치 찾기
            location = self._find_method_in_file(file_obj.path, method_name, method.signature)
            if location:
                # 위치 정보를 DB에 업데이트
                self._update_method_location(method, location)
                
            return location
            
        except Exception as e:
            logger.error(f"Java 메서드 위치 추적 실패 {method_id}: {e}")
            return None
    
    def track_sql_unit_location(self, sql_unit_id: int) -> Optional[ChunkLocation]:
        """SQL Unit의 위치 정보 추적"""
        try:
            # SQL Unit 정보 조회
            sql_unit = self.db_session.query(SqlUnit).filter(SqlUnit.sql_id == sql_unit_id).first()
            if not sql_unit:
                logger.warning(f"SQL Unit 정보 없음: {sql_unit_id}")
                return None
            
            # 파일 정보 조회
            file_obj = self.db_session.query(File).filter(File.file_id == sql_unit.file_id).first()
            if not file_obj:
                logger.warning(f"파일 정보 없음: {sql_unit.file_id}")
                return None
            
            # SQL Unit이 이미 라인 정보를 가지고 있는 경우
            if hasattr(sql_unit, 'start_line') and sql_unit.start_line:
                content_preview = self._get_content_preview(file_obj.path, sql_unit.start_line, sql_unit.end_line or sql_unit.start_line)
                return ChunkLocation(
                    file_path=file_obj.path,
                    start_line=sql_unit.start_line,
                    end_line=sql_unit.end_line or sql_unit.start_line,
                    content_preview=content_preview
                )
            
            # XML 파일에서 SQL Unit 위치 찾기
            location = self._find_sql_unit_in_xml(file_obj.path, sql_unit.stmt_id, sql_unit.stmt_kind)
            if location:
                # 위치 정보를 DB에 업데이트
                self._update_sql_unit_location(sql_unit, location)
                
            return location
            
        except Exception as e:
            logger.error(f"SQL Unit 위치 추적 실패 {sql_unit_id}: {e}")
            return None
    
    def track_class_location(self, class_id: int) -> Optional[ChunkLocation]:
        """Java 클래스의 위치 정보 추적"""
        try:
            # 클래스 정보 조회
            class_obj = self.db_session.query(Class).filter(Class.class_id == class_id).first()
            if not class_obj:
                logger.warning(f"클래스 정보 없음: {class_id}")
                return None
            
            # 파일 정보 조회
            file_obj = self.db_session.query(File).filter(File.file_id == class_obj.file_id).first()
            if not file_obj:
                logger.warning(f"파일 정보 없음: {class_obj.file_id}")
                return None
            
            # 클래스가 이미 라인 정보를 가지고 있는 경우
            if hasattr(class_obj, 'start_line') and class_obj.start_line:
                content_preview = self._get_content_preview(file_obj.path, class_obj.start_line, class_obj.end_line or class_obj.start_line)
                return ChunkLocation(
                    file_path=file_obj.path,
                    start_line=class_obj.start_line,
                    end_line=class_obj.end_line or class_obj.start_line,
                    content_preview=content_preview
                )
            
            # 파일에서 클래스 위치 찾기
            location = self._find_class_in_file(file_obj.path, class_obj.name, class_obj.fqn)
            if location:
                # 위치 정보를 DB에 업데이트
                self._update_class_location(class_obj, location)
                
            return location
            
        except Exception as e:
            logger.error(f"클래스 위치 추적 실패 {class_id}: {e}")
            return None
    
    def create_location_metadata(self, chunk_type: str, chunk_id: int) -> Dict[str, Any]:
        """청크 타입에 따른 위치 메타데이터 생성"""
        
        location = None
        
        if chunk_type == 'method':
            # 메서드 정보 조회하여 위치 추적
            method = self.db_session.query(Method).filter(Method.method_id == chunk_id).first()
            if method:
                class_obj = self.db_session.query(Class).filter(Class.class_id == method.class_id).first()
                if class_obj:
                    location = self.track_java_method_location(chunk_id, class_obj.fqn, method.name)
        
        elif chunk_type == 'sql_unit':
            location = self.track_sql_unit_location(chunk_id)
        
        elif chunk_type == 'class':
            location = self.track_class_location(chunk_id)
        
        # 위치 정보를 메타데이터로 변환
        if location:
            metadata = location.to_dict()
            metadata['chunk_type'] = chunk_type
            metadata['chunk_id'] = chunk_id
            metadata['tracked_at'] = str(datetime.now())
            return metadata
        else:
            # 기본 메타데이터
            return {
                'chunk_type': chunk_type,
                'chunk_id': chunk_id,
                'location_status': 'not_found',
                'tracked_at': str(datetime.now())
            }
    
    def _find_method_in_file(self, file_path: str, method_name: str, method_signature: str = None) -> Optional[ChunkLocation]:
        """파일에서 메서드 위치 찾기"""
        try:
            lines = self._get_file_lines(file_path)
            if not lines:
                return None
            
            # 메서드 패턴들 (Java)
            patterns = [
                rf'^\s*(public|private|protected)?\s*(static)?\s*\w+\s+{re.escape(method_name)}\s*\(',  # 기본 메서드
                rf'^\s*@\w+.*\n\s*(public|private|protected)?\s*(static)?\s*\w+\s+{re.escape(method_name)}\s*\(',  # 어노테이션 포함
            ]
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line, re.MULTILINE):
                        # 메서드 시작점 찾음
                        start_line = i + 1
                        
                        # 메서드 끝점 찾기 (중괄호 매칭)
                        end_line = self._find_method_end_line(lines, i)
                        
                        content_preview = self._extract_content_preview(lines, i, min(i + 3, len(lines)))
                        
                        return ChunkLocation(
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line,
                            content_preview=content_preview
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"메서드 위치 찾기 실패 {file_path}: {e}")
            return None
    
    def _find_sql_unit_in_xml(self, file_path: str, stmt_id: str, stmt_kind: str) -> Optional[ChunkLocation]:
        """XML 파일에서 SQL Unit 위치 찾기"""
        try:
            lines = self._get_file_lines(file_path)
            if not lines:
                return None
            
            # SQL 문 태그 패턴 (select, insert, update, delete)
            tag_pattern = rf'<{re.escape(stmt_kind)}\s+.*id=["\']({re.escape(stmt_id)})["\']'
            
            for i, line in enumerate(lines):
                if re.search(tag_pattern, line, re.IGNORECASE):
                    # SQL 문 시작점 찾음
                    start_line = i + 1
                    
                    # 해당 태그의 끝점 찾기
                    end_line = self._find_xml_tag_end_line(lines, i, stmt_kind)
                    
                    content_preview = self._extract_content_preview(lines, i, min(i + 5, len(lines)))
                    
                    return ChunkLocation(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        content_preview=content_preview
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"SQL Unit 위치 찾기 실패 {file_path}: {e}")
            return None
    
    def _find_class_in_file(self, file_path: str, class_name: str, fqn: str) -> Optional[ChunkLocation]:
        """파일에서 클래스 위치 찾기"""
        try:
            lines = self._get_file_lines(file_path)
            if not lines:
                return None
            
            # 클래스 선언 패턴
            patterns = [
                rf'^\s*(public|private|protected)?\s*(final)?\s*(abstract)?\s*class\s+{re.escape(class_name)}\s*',
                rf'^\s*(public|private|protected)?\s*interface\s+{re.escape(class_name)}\s*',
                rf'^\s*(public|private|protected)?\s*enum\s+{re.escape(class_name)}\s*'
            ]
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line):
                        # 클래스 시작점 찾음
                        start_line = i + 1
                        
                        # 클래스 끝점 찾기 (파일 끝까지 또는 다음 클래스까지)
                        end_line = self._find_class_end_line(lines, i)
                        
                        content_preview = self._extract_content_preview(lines, i, min(i + 3, len(lines)))
                        
                        return ChunkLocation(
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line,
                            content_preview=content_preview
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"클래스 위치 찾기 실패 {file_path}: {e}")
            return None
    
    def _get_file_lines(self, file_path: str) -> Optional[List[str]]:
        """파일 라인별 내용 가져오기 (캐시 사용)"""
        if file_path in self.file_content_cache:
            return self.file_content_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.file_content_cache[file_path] = lines
                return lines
                
        except Exception as e:
            logger.warning(f"파일 읽기 실패 {file_path}: {e}")
            return None
    
    def _find_method_end_line(self, lines: List[str], start_idx: int) -> int:
        """메서드 끝 라인 찾기 (중괄호 매칭)"""
        brace_count = 0
        found_opening_brace = False
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            # 중괄호 개수 세기
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening_brace = True
                elif char == '}':
                    brace_count -= 1
                    
                    # 모든 중괄호가 닫히면 메서드 끝
                    if found_opening_brace and brace_count == 0:
                        return i + 1
        
        # 찾지 못한 경우 시작점 + 10라인을 기본값으로
        return start_idx + 10
    
    def _find_xml_tag_end_line(self, lines: List[str], start_idx: int, tag_name: str) -> int:
        """XML 태그 끝 라인 찾기"""
        end_tag = f"</{tag_name}>"
        
        for i in range(start_idx, len(lines)):
            if end_tag in lines[i]:
                return i + 1
        
        # 찾지 못한 경우 시작점 + 20라인을 기본값으로 (SQL은 길 수 있음)
        return start_idx + 20
    
    def _find_class_end_line(self, lines: List[str], start_idx: int) -> int:
        """클래스 끝 라인 찾기"""
        brace_count = 0
        found_opening_brace = False
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening_brace = True
                elif char == '}':
                    brace_count -= 1
                    
                    if found_opening_brace and brace_count == 0:
                        return i + 1
        
        # 찾지 못한 경우 파일 끝까지
        return len(lines)
    
    def _extract_content_preview(self, lines: List[str], start_idx: int, end_idx: int) -> str:
        """내용 미리보기 추출"""
        preview_lines = lines[start_idx:end_idx]
        preview = ''.join(preview_lines).strip()
        
        # 길이 제한 (처음 200자)
        if len(preview) > 200:
            preview = preview[:200] + "..."
        
        return preview
    
    def _get_content_preview(self, file_path: str, start_line: int, end_line: int) -> str:
        """파일에서 특정 라인 범위의 내용 미리보기"""
        lines = self._get_file_lines(file_path)
        if not lines:
            return ""
        
        # 라인 인덱스 조정 (1-based to 0-based)
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        return self._extract_content_preview(lines, start_idx, end_idx)
    
    def _update_method_location(self, method: Method, location: ChunkLocation):
        """메서드의 위치 정보를 DB에 업데이트"""
        try:
            if hasattr(method, 'start_line'):
                method.start_line = location.start_line
                method.end_line = location.end_line
            
            # 메타데이터로 위치 정보 저장
            method.meta = location.to_json()
            
            self.db_session.commit()
            logger.debug(f"메서드 위치 정보 업데이트: {method.name} ({location.start_line}-{location.end_line})")
            
        except Exception as e:
            logger.error(f"메서드 위치 정보 업데이트 실패: {e}")
    
    def _update_sql_unit_location(self, sql_unit: SqlUnit, location: ChunkLocation):
        """SQL Unit의 위치 정보를 DB에 업데이트"""
        try:
            if hasattr(sql_unit, 'start_line'):
                sql_unit.start_line = location.start_line
                sql_unit.end_line = location.end_line
            
            # 메타데이터로 위치 정보 저장
            sql_unit.meta = location.to_json()
            
            self.db_session.commit()
            logger.debug(f"SQL Unit 위치 정보 업데이트: {sql_unit.stmt_id} ({location.start_line}-{location.end_line})")
            
        except Exception as e:
            logger.error(f"SQL Unit 위치 정보 업데이트 실패: {e}")
    
    def _update_class_location(self, class_obj: Class, location: ChunkLocation):
        """클래스의 위치 정보를 DB에 업데이트"""
        try:
            if hasattr(class_obj, 'start_line'):
                class_obj.start_line = location.start_line
                class_obj.end_line = location.end_line
            
            # 메타데이터로 위치 정보 저장
            class_obj.meta = location.to_json()
            
            self.db_session.commit()
            logger.debug(f"클래스 위치 정보 업데이트: {class_obj.name} ({location.start_line}-{location.end_line})")
            
        except Exception as e:
            logger.error(f"클래스 위치 정보 업데이트 실패: {e}")


# 편의 함수들
from datetime import datetime

def extract_chunk_location_from_meta(meta_json: str) -> Optional[ChunkLocation]:
    """메타데이터 JSON에서 위치 정보 추출"""
    try:
        if not meta_json:
            return None
            
        meta = json.loads(meta_json)
        
        if 'file_path' in meta and 'start_line' in meta:
            return ChunkLocation(
                file_path=meta['file_path'],
                start_line=meta['start_line'],
                end_line=meta.get('end_line', meta['start_line']),
                start_column=meta.get('start_column', 0),
                end_column=meta.get('end_column', 0),
                content_preview=meta.get('content_preview', '')
            )
        
        return None
        
    except Exception:
        return None

def get_chunk_content_from_location(location: ChunkLocation) -> str:
    """위치 정보를 사용하여 실제 청크 내용 추출"""
    try:
        with open(location.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            start_idx = location.start_line - 1
            end_idx = location.end_line
            
            if start_idx >= 0 and end_idx <= len(lines):
                return ''.join(lines[start_idx:end_idx])
        
        return ""
        
    except Exception as e:
        logger.error(f"청크 내용 추출 실패 {location.file_path}: {e}")
        return ""