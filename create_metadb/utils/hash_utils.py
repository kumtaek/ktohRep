"""
해시 유틸리티

파일 해시 계산 및 비교 기능을 제공합니다.
"""

import hashlib
import logging
from typing import Optional

class HashUtils:
    """해시 유틸리티"""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """파일 해시값 계산"""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logging.error(f"파일 해시 계산 실패 {file_path}: {e}")
            return None
    
    @staticmethod
    def calculate_content_hash(content: str, algorithm: str = 'md5') -> str:
        """내용 해시값 계산"""
        try:
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(content.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            logging.error(f"내용 해시 계산 실패: {e}")
            return ""
    
    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> bool:
        """해시값 비교"""
        return hash1 == hash2
