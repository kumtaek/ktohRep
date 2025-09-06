"""
파일 유틸리티

파일 관련 공통 기능을 제공합니다.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

class FileUtils:
    """파일 유틸리티"""
    
    @staticmethod
    def get_supported_file_extensions() -> List[str]:
        """지원하는 파일 확장자 목록"""
        return ['.java', '.jsp', '.xml', '.sql', '.properties', '.yml', '.yaml']
    
    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """지원하는 파일인지 확인"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in FileUtils.get_supported_file_extensions()
    
    @staticmethod
    def scan_source_files(source_path: str) -> List[str]:
        """소스 파일 스캔"""
        source_files = []
        
        try:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if FileUtils.is_supported_file(file_path):
                        source_files.append(file_path)
        except Exception as e:
            logging.error(f"소스 파일 스캔 실패 {source_path}: {e}")
        
        return source_files
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """파일 정보 추출"""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': Path(file_path).name,
                'extension': Path(file_path).suffix.lower(),
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime
            }
        except Exception as e:
            logging.error(f"파일 정보 추출 실패 {file_path}: {e}")
            return {}
    
    @staticmethod
    def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
        """파일 내용 읽기"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logging.error(f"파일 읽기 실패 {file_path}: {e}")
            return ""
    
    @staticmethod
    def write_file_content(file_path: str, content: str, encoding: str = 'utf-8'):
        """파일 내용 쓰기"""
        try:
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            logging.error(f"파일 쓰기 실패 {file_path}: {e}")
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """상대 경로 계산"""
        try:
            return os.path.relpath(file_path, base_path)
        except Exception as e:
            logging.error(f"상대 경로 계산 실패 {file_path}, {base_path}: {e}")
            return file_path
