#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 모델 클라이언트 공통 인터페이스
- 개발환경: Ollama (gemma3:1b)
- 운영환경: vLLM (Qwen2.5 7B)
- 모듈 교체 가능한 구조
"""

import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass
class ModelConfig:
    """모델 설정"""
    name: str
    url: str
    timeout: int = 30
    max_tokens: int = 2000
    temperature: float = 0.7

class AIModelClient(ABC):
    """AI 모델 클라이언트 추상 클래스"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """텍스트 생성"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """모델 사용 가능 여부 확인"""
        pass

class OllamaClient(AIModelClient):
    """Ollama 클라이언트 (개발환경)"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_name = config.name
        self.url = config.url
        self.timeout = config.timeout
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Ollama API로 텍스트 생성"""
        try:
            url = f"{self.url}/api/generate"
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 2000)
                }
            }
            
            logger.info(f"🚀 Ollama 호출 시작: {self.model_name}")
            logger.info(f"📝 프롬프트 길이: {len(prompt)}자")
            logger.info(f"⏱️ 타임아웃: {self.timeout}초")
            logger.debug(f"📝 전송할 프롬프트:\n{prompt}")
            logger.debug(f"📤 요청 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                logger.info(f"✅ Ollama 응답 완료: {len(response_text)}자")
                logger.info(f"📄 응답 미리보기: {response_text[:100]}...")
                logger.debug(f"📥 전체 응답 내용:\n{response_text}")
                logger.debug(f"📥 응답 메타데이터: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return response_text
            else:
                logger.error(f"❌ Ollama API 오류: {response.status_code}")
                logger.error(f"📄 오류 내용: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ollama 호출 실패: {e}")
            logger.error(f"🔍 오류 타입: {type(e).__name__}")
            return None
    
    def is_available(self) -> bool:
        """Ollama 서비스 사용 가능 여부 확인"""
        try:
            url = f"{self.url}/api/tags"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                is_available = self.model_name in model_names
                logger.info(f"Ollama 모델 {self.model_name} 사용 가능: {is_available}")
                return is_available
            return False
        except Exception as e:
            logger.warning(f"Ollama 연결 확인 실패: {e}")
            return False

class VLLMClient(AIModelClient):
    """vLLM 클라이언트 (운영환경)"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_name = config.name
        self.url = config.url
        self.timeout = config.timeout
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """vLLM API로 텍스트 생성"""
        try:
            url = f"{self.url}/v1/chat/completions"
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": False
            }
            
            logger.info(f"🚀 vLLM 호출 시작: {self.model_name}")
            logger.info(f"📝 프롬프트 길이: {len(prompt)}자")
            logger.info(f"⏱️ 타임아웃: {self.timeout}초")
            logger.debug(f"📝 전송할 프롬프트:\n{prompt}")
            logger.debug(f"📤 요청 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                logger.info(f"✅ vLLM 응답 완료: {len(response_text)}자")
                logger.info(f"📄 응답 미리보기: {response_text[:100]}...")
                logger.debug(f"📥 전체 응답 내용:\n{response_text}")
                logger.debug(f"📥 응답 메타데이터: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return response_text
            else:
                logger.error(f"vLLM API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"vLLM 호출 실패: {e}")
            return None
    
    def is_available(self) -> bool:
        """vLLM 서비스 사용 가능 여부 확인"""
        try:
            url = f"{self.url}/v1/models"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('data', [])
                model_names = [model.get('id', '') for model in models]
                is_available = self.model_name in model_names
                logger.info(f"vLLM 모델 {self.model_name} 사용 가능: {is_available}")
                return is_available
            return False
        except Exception as e:
            logger.warning(f"vLLM 연결 확인 실패: {e}")
            return False

class AIModelManager:
    """AI 모델 관리자"""
    
    def __init__(self, config_path: str = "config/ai_config.yaml"):
        self.config = self._load_config(config_path)
        self.clients = {}
        self._initialize_clients()
    
    def _load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except:
            # 기본 설정
            return {
                'environment': 'development',  # development, production
                'models': {
                    'ollama': {
                        'name': 'gemma3:1b',
                        'url': 'http://localhost:11434',
                        'timeout': 30
                    },
                    'vllm': {
                        'name': 'qwen2.5-7b',
                        'url': 'http://localhost:8000',
                        'timeout': 60
                    }
                }
            }
    
    def _initialize_clients(self):
        """클라이언트 초기화"""
        # Ollama 클라이언트
        ollama_config = self.config.get('models', {}).get('ollama', {})
        ollama_model_config = ModelConfig(
            name=ollama_config.get('name', 'gemma3:1b'),
            url=ollama_config.get('url', 'http://localhost:11434'),
            timeout=ollama_config.get('timeout', 30)
        )
        self.clients['ollama'] = OllamaClient(ollama_model_config)
        
        # vLLM 클라이언트
        vllm_config = self.config.get('models', {}).get('vllm', {})
        vllm_model_config = ModelConfig(
            name=vllm_config.get('name', 'qwen2.5-7b'),
            url=vllm_config.get('url', 'http://localhost:8000'),
            timeout=vllm_config.get('timeout', 60)
        )
        self.clients['vllm'] = VLLMClient(vllm_model_config)
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """텍스트 생성 (환경에 따라 자동 선택)"""
        environment = self.config.get('environment', 'development')
        
        if environment == 'development':
            # 개발환경: Ollama 우선 시도
            if self.clients['ollama'].is_available():
                logger.info("개발환경: Ollama 사용")
                return self.clients['ollama'].generate(prompt, **kwargs)
            elif self.clients['vllm'].is_available():
                logger.info("개발환경: vLLM 백업 사용")
                return self.clients['vllm'].generate(prompt, **kwargs)
        else:
            # 운영환경: vLLM 우선 시도
            if self.clients['vllm'].is_available():
                logger.info("운영환경: vLLM 사용")
                return self.clients['vllm'].generate(prompt, **kwargs)
            elif self.clients['ollama'].is_available():
                logger.info("운영환경: Ollama 백업 사용")
                return self.clients['ollama'].generate(prompt, **kwargs)
        
        logger.error("사용 가능한 AI 모델이 없습니다")
        return None
    
    def get_available_models(self) -> Dict[str, bool]:
        """사용 가능한 모델 목록 반환"""
        return {
            'ollama': self.clients['ollama'].is_available(),
            'vllm': self.clients['vllm'].is_available()
        }
    
    def switch_environment(self, environment: str):
        """환경 전환"""
        if environment in ['development', 'production']:
            self.config['environment'] = environment
            logger.info(f"환경 전환: {environment}")
        else:
            logger.error(f"지원하지 않는 환경: {environment}")

# 편의 함수
def create_ai_client(environment: str = 'development') -> AIModelManager:
    """AI 클라이언트 생성"""
    manager = AIModelManager()
    manager.switch_environment(environment)
    return manager

if __name__ == "__main__":
    # 테스트
    client = create_ai_client('development')
    
    print("=== AI 모델 사용 가능 여부 ===")
    available = client.get_available_models()
    for model, is_available in available.items():
        print(f"{model}: {'✅' if is_available else '❌'}")
    
    if any(available.values()):
        print("\n=== AI 모델 테스트 ===")
        response = client.generate("Hello, how are you?")
        if response:
            print(f"응답: {response[:100]}...")
        else:
            print("응답 실패")
    else:
        print("사용 가능한 AI 모델이 없습니다")
