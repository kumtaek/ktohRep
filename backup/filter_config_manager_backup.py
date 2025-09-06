"""
필터 설정 파일 관리 유틸리티
프로젝트별 필터링 설정을 관리하고 자동 생성합니다.
"""

import os
import yaml
import logging
import signal
import time
from pathlib import Path
from typing import Dict, Any, Optional


def input_timeout(prompt, timeout=30):
    """30초 제한으로 사용자 입력을 받습니다. 시간 초과시 'Y' 반환."""
    import platform
    import sys
    
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
        try:
            config_dir = f"./project/{project_name}/config"
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = f"{config_dir}/filter_config.yaml"
            
            # 상세한 주석이 포함된 기본 설정
            default_config = f"""# {project_name} 프로젝트 필터 설정 파일
# 이 파일은 프로젝트 분석 시 사용되는 필터링 규칙을 정의합니다.
#
# ============================================================================
# 📁 분석 대상 폴더 (include_patterns)
# ============================================================================
# **/src/main/java/**     : Java 소스코드가 위치한 폴더
# **/src/main/resources/**: 설정 파일, 리소스 파일이 위치한 폴더  
# **/src/main/webapp/**   : 웹 애플리케이션 리소스가 위치한 폴더
#
# 패턴 설명:
# - ** : 모든 하위 폴더를 재귀적으로 포함
# - *  : 와일드카드로 경로 매칭
#
include_patterns:
  - "**/*.java"
  - "**/*.xml" 
  - "**/*.jsp"
  - "**/*.jspf"
  - "**/*.properties"

# ============================================================================
# 🚫 분석 제외 폴더 (exclude_patterns)
# ============================================================================
# **/target/**        : Maven 빌드 결과물 (컴파일된 클래스, JAR 등)
# **/build/**         : Gradle/기타 빌드 결과물
# **/test/**          : 테스트 코드 (필요시 이 줄을 주석 처리하여 포함 가능)
# **/.git/**          : Git 버전 관리 메타데이터
# **/node_modules/**  : Node.js 의존성 패키지
# **/vendor/**        : PHP/기타 언어의 의존성 패키지
#
# 제외 이유:
# - 빌드 결과물은 분석 대상이 아님
# - 의존성 패키지는 외부 라이브러리로 분석 불필요
# - 메타데이터는 소스코드가 아님
#
exclude_patterns:
  - "**/target/**"
  - "**/build/**"
  - "**/test/**"
  - "**/.git/**"
  - "**/node_modules/**"
  - "**/vendor/**"

# ============================================================================
# 🏗️ 계층별 분류 패턴 (layer_patterns)
# ============================================================================
# 이 패턴들은 Java 클래스 파일명에 포함된 키워드를 기반으로
# 자동으로 계층을 분류하는 데 사용됩니다.
#
# 동작 원리:
# 1. 파일명에서 확장자(.java) 제거
# 2. 각 패턴과 매칭하여 해당 계층으로 분류
# 3. 매칭되지 않으면 "other" 계층으로 분류
#
# 패턴 예시:
# - "*Controller*" : OrderController.java, UserController.java 등
# - "*Service*"    : OrderService.java, UserService.java 등
# - "*Mapper*"     : OrderMapper.java, UserMapper.java 등
#
layer_patterns:
  # 웹 요청 처리 계층 (사용자 요청을 받아 처리)
  controller: 
    - "*Controller*"    # Spring MVC 컨트롤러
    - "*Servlet*"       # 서블릿 클래스
    - "*Action*"        # Struts 액션 클래스
  
  # 비즈니스 로직 계층 (핵심 업무 로직 처리)
  service: 
    - "*Service*"       # 서비스 클래스
    - "*Manager*"       # 매니저 클래스
    - "*Handler*"       # 이벤트 핸들러
  
  # 데이터 액세스 계층 (데이터베이스 접근)
  mapper: 
    - "*Mapper*"        # MyBatis 매퍼
    - "*DAO*"           # 데이터 액세스 객체
    - "*Repository*"    # JPA 리포지토리
  
  # 설정 및 구성 계층 (애플리케이션 설정)
  config: 
    - "*Config*"        # 설정 클래스
    - "*Configuration*" # Spring 설정
    - "*Setup*"         # 초기화 클래스
  
  # 유틸리티 계층 (공통 기능 제공)
  util: 
    - "*Util*"          # 유틸리티 클래스
    - "*Helper*"        # 헬퍼 클래스
    - "*Tool*"          # 도구 클래스
  
  # 데이터 모델 계층 (데이터 구조 정의)
  entity: 
    - "*Entity*"        # JPA 엔티티
    - "*Model*"         # 데이터 모델
    - "*DTO*"           # 데이터 전송 객체
    - "*VO*"            # 값 객체

# ============================================================================
# 💡 사용법 및 팁
# ============================================================================
# 1. 새로운 계층 추가:
#    layer_patterns:
#      custom: ["*Custom*", "*Special*"]
#
# 2. 패턴 수정:
#    - 기존 패턴을 수정하거나 새로운 패턴 추가 가능
#    - 와일드카드(*) 사용하여 유연한 매칭
#
# 3. 분석 대상 조정:
#    - include_patterns에 새로운 폴더 추가
#    - exclude_patterns에서 제외할 폴더 추가
#
# 4. 주의사항:
#    - 패턴이 겹치면 첫 번째로 매칭된 계층으로 분류
#    - 파일명에 계층 정보가 포함되어야 정확한 분류 가능
#
# ============================================================================
# 🔄 설정 변경 후 재분석
# ============================================================================
# 이 파일을 수정한 후에는 프로젝트를 다시 분석해야 합니다:
# python phase1/main.py --project-name {project_name} --verbose
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

📋 설정 파일 내용:
   - 분석할 폴더 패턴 (include_patterns)
   - 분석에서 제외할 폴더 패턴 (exclude_patterns)  
   - Java 클래스 계층별 분류 패턴 (layer_patterns)

💡 기본 설정으로 시작하시겠습니까?
   이 설정은 Maven/Spring Boot 표준 구조를 기반으로 합니다.

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
