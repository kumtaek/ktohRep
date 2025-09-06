"""
검증 유틸리티

입력값 검증 및 유효성 확인 기능을 제공합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class ValidationUtils:
    """검증 유틸리티"""
    
    @staticmethod
    def validate_project_name(project_name: str) -> bool:
        """프로젝트명 검증"""
        if not project_name or not isinstance(project_name, str):
            return False
        
        # 프로젝트명은 영문자, 숫자, 언더스코어, 하이픈만 허용
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, project_name))
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """파일 경로 검증"""
        if not file_path or not isinstance(file_path, str):
            return False
        
        # 기본적인 경로 검증
        return len(file_path) > 0 and not file_path.startswith('..')
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """설정 검증"""
        errors = []
        
        # 필수 설정 확인
        required_keys = ['project', 'database']
        for key in required_keys:
            if key not in config:
                errors.append(f"필수 설정 누락: {key}")
        
        # 프로젝트 설정 검증
        if 'project' in config:
            project_config = config['project']
            if 'name' not in project_config:
                errors.append("프로젝트명이 설정되지 않았습니다.")
            if 'source_path' not in project_config:
                errors.append("소스 경로가 설정되지 않았습니다.")
        
        # 데이터베이스 설정 검증
        if 'database' in config:
            db_config = config['database']
            if 'output_db' not in db_config:
                errors.append("출력 데이터베이스 경로가 설정되지 않았습니다.")
        
        return errors
    
    @staticmethod
    def validate_llm_config(llm_config: Dict[str, Any]) -> List[str]:
        """LLM 설정 검증"""
        errors = []
        
        if llm_config.get('enabled', False):
            if not llm_config.get('api_key'):
                errors.append("LLM API 키가 설정되지 않았습니다.")
            if not llm_config.get('model'):
                errors.append("LLM 모델이 설정되지 않았습니다.")
            if llm_config.get('max_tokens', 0) <= 0:
                errors.append("최대 토큰 수가 올바르지 않습니다.")
        
        return errors
