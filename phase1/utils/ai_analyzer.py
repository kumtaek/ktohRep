"""
AI 기반 소스코드 분석 리포트 생성기
로컬 Ollama (gemma3:1b) 및 원격 Qwen2.5 7B 모델을 활용하여 소스코드 분석
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import requests
import subprocess
import asyncio

@dataclass
class AnalysisRequest:
    """분석 요청 정보"""
    project_path: str
    analysis_type: str  # 'erd', 'architecture', 'code_quality', 'security', 'comprehensive'
    model_type: str     # 'local_gemma', 'remote_qwen'
    output_format: str  # 'markdown', 'html', 'json'
    custom_prompt: Optional[str] = None

@dataclass
class AnalysisResult:
    """분석 결과"""
    success: bool
    content: str
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float = 0.0

class AIAnalyzer:
    """AI 기반 소스코드 분석기"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        분석기 초기화
        
        Args:
            config: 설정 정보
                - local_ollama_url: 로컬 Ollama URL (기본값: http://localhost:11434)
                - remote_api_url: 원격 API URL
                - remote_api_key: 원격 API 키
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 기본 설정
        self.local_ollama_url = config.get('local_ollama_url', 'http://localhost:11434')
        self.remote_api_url = config.get('remote_api_url')
        self.remote_api_key = config.get('remote_api_key')
        
        # 모델 설정
        self.local_model = "gemma3:1b"  # 실제 설치된 모델명으로 복원
        self.remote_model = "qwen2.5-7b"
        
    def analyze_project(self, request: AnalysisRequest) -> AnalysisResult:
        """
        프로젝트 분석 실행
        
        Args:
            request: 분석 요청 정보
            
        Returns:
            분석 결과
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"AI 분석 시작: {request.analysis_type} - {request.model_type}")
            
            # 1단계: 프로젝트 정보 수집
            project_info = self._collect_project_info(request.project_path)
            
            # 2단계: 분석 프롬프트 생성
            prompt = self._generate_analysis_prompt(request, project_info)
            
            # 3단계: AI 모델로 분석 실행
            if request.model_type == 'local_gemma':
                ai_response = self._analyze_with_local_gemma(prompt)
            elif request.model_type == 'remote_qwen':
                ai_response = self._analyze_with_remote_qwen(prompt)
            else:
                raise ValueError(f"지원하지 않는 모델 타입: {request.model_type}")
            
            # 4단계: 응답 후처리
            processed_content = self._post_process_response(ai_response, request.output_format)
            
            # 5단계: 메타데이터 생성
            metadata = {
                'analysis_type': request.analysis_type,
                'model_type': request.model_type,
                'model_name': self.local_model if request.model_type == 'local_gemma' else self.remote_model,
                'project_path': request.project_path,
                'project_info': project_info,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            return AnalysisResult(
                success=True,
                content=processed_content,
                metadata=metadata,
                processing_time=metadata['processing_time']
            )
            
        except Exception as e:
            self.logger.error(f"AI 분석 실패: {e}")
            return AnalysisResult(
                success=False,
                content="",
                metadata={},
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _collect_project_info(self, project_path: str) -> Dict[str, Any]:
        """프로젝트 정보 수집"""
        project_path = Path(project_path)
        
        info = {
            'project_name': project_path.name,
            'structure': {},
            'file_count': 0,
            'total_size': 0,
            'languages': {},
            'last_modified': None
        }
        
        # 디렉토리 구조 스캔
        for root, dirs, files in os.walk(project_path):
            rel_path = Path(root).relative_to(project_path)
            
            # 파일 정보 수집
            for file in files:
                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()
                
                if file_ext:
                    if file_ext not in info['languages']:
                        info['languages'][file_ext] = 0
                    info['languages'][file_ext] += 1
                
                info['file_count'] += 1
                info['total_size'] += file_path.stat().st_size
                
                # 마지막 수정 시간
                mtime = file_path.stat().st_mtime
                if info['last_modified'] is None or mtime > info['last_modified']:
                    info['last_modified'] = mtime
        
        return info
    
    def _generate_analysis_prompt(self, request: AnalysisRequest, project_info: Dict[str, Any]) -> str:
        """분석 프롬프트 생성"""
        
        base_prompt = f"""당신은 전문 소스코드 분석가입니다. 
다음 프로젝트를 분석하여 {request.analysis_type} 분석 리포트를 생성해주세요.

프로젝트 정보:
- 프로젝트명: {project_info['project_name']}
- 총 파일 수: {project_info['file_count']}개
- 총 크기: {project_info['total_size']:,} bytes
- 사용 언어: {', '.join(project_info['languages'].keys())}

분석 요청: {request.analysis_type}

"""
        
        if request.analysis_type == 'erd':
            base_prompt += """ERD 분석을 위해 다음을 수행해주세요:
1. 데이터베이스 스키마 파일들 (CSV, SQL 등) 분석
2. 테이블 구조 및 관계 파악
3. 정규화 상태 평가
4. 개선 제안사항 도출

결과는 마크다운 형식으로 작성해주세요.
"""
        
        elif request.analysis_type == 'architecture':
            base_prompt += """아키텍처 분석을 위해 다음을 수행해주세요:
1. 프로젝트 구조 및 패턴 분석
2. 사용된 기술 스택 파악
3. 아키텍처 패턴 식별 (MVC, Layered, Microservices 등)
4. 의존성 및 결합도 분석
5. 확장성 및 유지보수성 평가

결과는 마크다운 형식으로 작성해주세요.
"""
        
        elif request.analysis_type == 'code_quality':
            base_prompt += """코드 품질 분석을 위해 다음을 수행해주세요:
1. 코드 복잡도 및 가독성 평가
2. 코딩 컨벤션 준수도 확인
3. 테스트 커버리지 및 품질 평가
4. 보안 취약점 검토
5. 성능 최적화 기회 식별

결과는 마크다운 형식으로 작성해주세요.
"""
        
        elif request.analysis_type == 'comprehensive':
            base_prompt += """종합 분석을 위해 다음을 수행해주세요:
1. 전체적인 프로젝트 구조 분석
2. 기술적 특징 및 장단점 평가
3. 비즈니스 로직 및 도메인 분석
4. 보안 및 성능 관점에서의 평가
5. 유지보수 및 확장성 제언
6. 개선 우선순위 제시

결과는 마크다운 형식으로 작성해주세요.
"""
        
        if request.custom_prompt:
            base_prompt += f"\n추가 요청사항:\n{request.custom_prompt}\n"
        
        base_prompt += "\n분석 결과는 한국어로 작성하고, 이모지와 마크다운 포맷을 활용하여 가독성을 높여주세요."
        
        return base_prompt
    
    def _analyze_with_local_gemma(self, prompt: str) -> str:
        """로컬 Gemma 모델로 분석"""
        try:
            # Ollama API 호출
            response = requests.post(
                f"{self.local_ollama_url}/api/generate",
                json={
                    "model": self.local_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4000
                    }
                },
                timeout=300  # 5분 타임아웃
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Ollama API 오류: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"로컬 Gemma 모델 연결 실패: {e}")
    
    def _analyze_with_remote_qwen(self, prompt: str) -> str:
        """원격 Qwen 모델로 분석"""
        if not self.remote_api_url or not self.remote_api_key:
            raise Exception("원격 API 설정이 필요합니다")
        
        try:
            # 원격 API 호출 (실제 구현은 API 제공자의 스펙에 따라 달라짐)
            headers = {
                'Authorization': f'Bearer {self.remote_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.remote_model,
                'messages': [
                    {'role': 'system', 'content': '당신은 전문 소스코드 분석가입니다.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            
            response = requests.post(
                self.remote_api_url,
                headers=headers,
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                # API 응답 구조에 따라 수정 필요
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                raise Exception(f"원격 API 오류: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"원격 Qwen 모델 연결 실패: {e}")
    
    def _post_process_response(self, ai_response: str, output_format: str) -> str:
        """AI 응답 후처리"""
        if output_format == 'json':
            # JSON 형식으로 변환
            try:
                # 마크다운을 구조화된 데이터로 파싱 시도
                return json.dumps({'content': ai_response}, ensure_ascii=False, indent=2)
            except:
                return json.dumps({'raw_content': ai_response}, ensure_ascii=False, indent=2)
        
        elif output_format == 'html':
            # HTML 형식으로 변환 (간단한 변환)
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI 분석 리포트</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
        code {{ background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
{ai_response}
</body>
</html>
"""
            return html_content
        
        else:  # markdown
            return ai_response
    
    def test_connection(self, model_type: str) -> bool:
        """모델 연결 테스트"""
        try:
            if model_type == 'local_gemma':
                response = requests.get(f"{self.local_ollama_url}/api/tags", timeout=10)
                return response.status_code == 200
            elif model_type == 'remote_qwen':
                # 원격 API 연결 테스트
                return bool(self.remote_api_url and self.remote_api_key)
            else:
                return False
        except:
            return False
