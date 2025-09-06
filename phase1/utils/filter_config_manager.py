"""
필터 설정 파일 관리 유틸리티
프로젝트별 필터링 설정을 관리하고 자동 생성합니다.
"""

import os
import yaml
import logging
import time
from typing import Dict, Any, Optional


def input_timeout(prompt, timeout=30):
    """30초 제한으로 사용자 입력을 받습니다. 시간 초과시 'Y' 반환."""
    import platform
    
    if platform.system() == 'Windows':
        # Windows용 msvcrt 사용
        import msvcrt
        print(f"{prompt} (30초 후 자동 'Y' 응답)")
        
        start_time = time.time()
        response = ""
        
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8', errors='ignore')
                if char == '\r':  # Enter 키
                    break
                elif char == '\b':  # Backspace 키
                    if response:
                        response = response[:-1]
                        print('\b \b', end='', flush=True)
                else:
                    response += char
                    print(char, end='', flush=True)
            time.sleep(0.1)
        
        if time.time() - start_time >= timeout:
            print(f"\n⏰ 30초 시간 초과! 자동으로 'Y'로 응답합니다.")
            return 'Y'
        
        print()  # 줄바꿈
        return response.strip().upper() if response.strip() else 'Y'
    else:
        # Unix/Linux용 signal 사용
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("입력 시간 초과")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            print(f"{prompt} (30초 후 자동 'Y' 응답)")
            response = input().strip().upper()
            signal.alarm(0)
            return response
        except TimeoutError:
            print(f"\n⏰ 30초 시간 초과! 자동으로 'Y'로 응답합니다.")
            return 'Y'
        except KeyboardInterrupt:
            print(f"\n⏰ 사용자 중단! 자동으로 'Y'로 응답합니다.")
            return 'Y'
        finally:
            signal.signal(signal.SIGALRM, old_handler)


class FilterConfigManager:
    """프로젝트별 필터 설정 파일을 관리합니다."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_filter_config_path(self, project_name: str) -> str:
        """프로젝트별 필터 설정 파일 경로를 반환합니다."""
        return f"./project/{project_name}/config/filter_config.yaml"
    
    def config_exists(self, project_name: str) -> bool:
        """필터 설정 파일이 존재하는지 확인합니다."""
        config_path = self.get_filter_config_path(project_name)
        return os.path.exists(config_path)
    
    def load_filter_config(self, project_name: str) -> Dict[str, Any]:
        """필터 설정 파일을 로드합니다."""
        config_path = self.get_filter_config_path(project_name)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"필터 설정 파일이 존재하지 않습니다: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise ValueError(f"설정 파일 형식이 잘못되었습니다: {e}")
    
    def create_config_auto(self, project_name: str) -> str:
        """기본 필터 설정 파일을 자동으로 생성합니다 (사용자 입력 없이)."""
        config_dir = f"./project/{project_name}/config"
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = f"{config_dir}/filter_config.yaml"
        
        # 기본 설정
        default_config = f"""# {project_name} 프로젝트 필터 설정 파일
include_patterns:
  - "**/*.java"
  - "**/*.xml" 
  - "**/*.jsp"
  - "**/*.jspf"
  - "**/*.properties"

exclude_patterns:
  - "**/target/**"
  - "**/build/**"
  - "**/test/**"
  - "**/.git/**"
  - "**/node_modules/**"
  - "**/vendor/**"

layer_patterns:
  controller: 
    - "*Controller*"
    - "*Servlet*"
    - "*Action*"
  
  service: 
    - "*Service*"
    - "*Manager*"
    - "*Handler*"
  
  mapper: 
    - "*Mapper*"
    - "*DAO*"
    - "*Repository*"
  
  config: 
    - "*Config*"
    - "*Configuration*"
    - "*Setup*"
  
  util: 
    - "*Util*"
    - "*Helper*"
    - "*Tool*"
  
  entity: 
    - "*Entity*"
    - "*Model*"
    - "*DTO*"
    - "*VO*"
"""
        
        # 파일 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
        
        self.logger.info(f"기본 필터 설정 파일이 생성되었습니다: {config_path}")
        return config_path
    
    def show_config_help(self, project_name: str):
        """설정 파일이 없을 때 도움말을 표시합니다."""
        help_message = f"""
{'='*80}
❌ 필터 설정 파일이 필요합니다!
{'='*80}

프로젝트 분석을 위해 필터링 설정을 먼저 구성해야 합니다.

📁 필요한 파일 위치:
   ./project/{project_name}/config/filter_config.yaml

🔧 설정 파일 생성 방법:
   1. 수동 생성: 위 경로에 filter_config.yaml 파일 생성
   2. 자동 생성: 아래 질문에 'Y'로 답변

💡 기본 설정으로 시작하시겠습니까?

{'='*80}
"""
        print(help_message)
    
    def prompt_for_config_creation(self, project_name: str) -> bool:
        """사용자에게 설정 파일 생성 여부를 묻습니다 (30초 제한)."""
        while True:
            response = input_timeout("기본 설정 파일을 생성하시겠습니까? (Y/N): ")
            if response in ['Y', 'YES']:
                return True
            elif response in ['N', 'NO']:
                return False
            else:
                print("Y 또는 N으로 답변해주세요.")
    
    def create_config_interactive(self, project_name: str) -> Optional[str]:
        """대화형으로 설정 파일을 생성합니다."""
        try:
            # 도움말 표시
            self.show_config_help(project_name)
            
            # 사용자 확인
            if self.prompt_for_config_creation(project_name):
                # 기본 설정 파일 생성
                config_path = self.create_config_auto(project_name)
                
                print(f"\n✅ 설정 파일이 성공적으로 생성되었습니다!")
                print(f"📁 생성 위치: {config_path}")
                print(f"\n🔍 이제 프로젝트를 다시 분석할 수 있습니다.")
                print(f"💡 명령어: python phase1/main.py --project-name {project_name} --verbose")
                
                return config_path
            else:
                print(f"\n❌ 설정 파일 생성이 취소되었습니다.")
                print(f"📝 수동으로 설정 파일을 생성한 후 다시 시도해주세요.")
                return None
                
        except Exception as e:
            self.logger.error(f"설정 파일 생성 실패: {e}")
            print(f"\n❌ 설정 파일 생성 중 오류가 발생했습니다: {e}")
            return None
