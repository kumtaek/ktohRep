"""
설정 관리 모듈

config.yaml 파일을 로드하고 설정을 관리하는 모듈입니다.
"""

import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """설정 파일을 로드합니다."""
    if config_path is None:
        # create_metadb 루트 기준으로 config.yaml 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"설정 파일 파싱 오류: {e}")

def get_project_config(project_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """프로젝트별 설정을 반환합니다."""
    project_config = config.copy()
    
    # 프로젝트명으로 경로 치환
    for key, value in project_config.items():
        if isinstance(value, str) and "{project_name}" in value:
            project_config[key] = value.format(project_name=project_name)
        elif isinstance(value, dict):
            project_config[key] = get_project_config(project_name, value)
    
    return project_config
