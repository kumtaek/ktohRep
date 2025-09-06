# AI 컴포넌트 분석기
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any

class AIComponentAnalyzer:
    """LLM을 이용한 컴포넌트 다이어그램 분석기"""
    
    def __init__(self, config_path: str = "config/ai_config.yaml"):
        """AI 분석기 초기화"""
        self.config = self._load_config(config_path)
        self.ollama_url = self.config.get('local_ollama', {}).get('url', 'http://localhost:11434')
        self.model = self.config.get('local_ollama', {}).get('model', 'gemma3:1b')
        
    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            return {
                'local_ollama': {
                    'url': 'http://localhost:11434',
                    'model': 'gemma3:1b'
                }
            }
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """프로젝트 구조 분석"""
        src_path = os.path.join(project_path, 'src')
        
        # 파일 구조 수집
        file_structure = {
            'java_files': [],
            'jsp_files': [],
            'xml_files': [],
            'other_files': []
        }
        
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), src_path)
                    if file.endswith('.java'):
                        file_structure['java_files'].append(file_path)
                    elif file.endswith('.jsp'):
                        file_structure['jsp_files'].append(file_path)
                    elif file.endswith('.xml'):
                        file_structure['xml_files'].append(file_path)
                    else:
                        file_structure['other_files'].append(file_path)
        
        return file_structure
    
    def _call_ollama(self, prompt: str) -> str:
        """Ollama API 호출"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Ollama API 오류: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Ollama API 호출 실패: {e}")
            return ""
    
    def analyze_component_architecture(self, file_structure: Dict[str, Any]) -> str:
        """LLM을 이용한 컴포넌트 아키텍처 분석"""
        
        # 파일 구조를 텍스트로 변환
        structure_text = f"""
프로젝트 파일 구조:
Java 파일들: {file_structure['java_files']}
JSP 파일들: {file_structure['jsp_files']}
XML 파일들: {file_structure['xml_files']}
기타 파일들: {file_structure['other_files']}
"""
        
        prompt = f"""
다음은 Java 웹 애플리케이션 프로젝트의 파일 구조입니다. 
이 구조를 분석하여 계층형 컴포넌트 다이어그램을 생성해주세요.

{structure_text}

요구사항:
1. 계층별로 컴포넌트를 분류하세요 (Presentation Layer, Business Layer, Data Access Layer, Infrastructure Layer)
2. 각 계층 내에서 세부 컴포넌트들을 그룹화하세요 (Controllers, Views, Services, Mappers 등)
3. 각 파일의 역할과 기능을 간단히 설명하세요
4. 마크다운 형식으로 출력하세요

출력 형식:
# [프로젝트명] 컴포넌트 다이어그램

## 전체 아키텍처 구조
[계층별 구조 설명]

## 상세 컴포넌트 구조

### 1. Presentation Layer (표현 계층)
#### Controllers
- [파일명]: [역할 설명]

#### Views  
- [파일명]: [역할 설명]

### 2. Business Layer (비즈니스 계층)
#### Services
- [파일명]: [역할 설명]

### 3. Data Access Layer (데이터 접근 계층)
#### Mappers
- [파일명]: [역할 설명]

### 4. Infrastructure Layer (인프라 계층)
#### Config
- [파일명]: [역할 설명]

각 파일의 역할을 한국어로 간단명료하게 설명해주세요.
"""
        
        return self._call_ollama(prompt)
    
    def generate_component_diagram(self, project_path: str) -> str:
        """컴포넌트 다이어그램 생성"""
        print(f"프로젝트 분석 시작: {project_path}")
        
        # 1. 프로젝트 구조 분석
        file_structure = self.analyze_project_structure(project_path)
        print(f"분석된 파일: Java({len(file_structure['java_files'])}), JSP({len(file_structure['jsp_files'])}), XML({len(file_structure['xml_files'])})")
        
        # 2. LLM을 이용한 아키텍처 분석
        print("LLM을 이용한 컴포넌트 아키텍처 분석 중...")
        component_diagram = self.analyze_component_architecture(file_structure)
        
        if not component_diagram:
            print("LLM 분석 실패, 기본 구조로 대체")
            component_diagram = self._generate_fallback_diagram(file_structure)
        
        return component_diagram
    
    def _generate_fallback_diagram(self, file_structure: Dict[str, Any]) -> str:
        """LLM 실패 시 기본 다이어그램 생성"""
        project_name = "sampleSrc"
        
        content = f"""# {project_name} 프로젝트 컴포넌트 다이어그램

## 전체 아키텍처 구조
이 프로젝트는 전형적인 Java 웹 애플리케이션의 계층형 아키텍처를 따르고 있습니다.

## 상세 컴포넌트 구조

### 1. Presentation Layer (표현 계층)
#### Controllers
"""
        
        # Java 파일들에서 Controller 분류
        for file_path in file_structure['java_files']:
            if 'controller' in file_path.lower():
                file_name = os.path.basename(file_path)
                content += f"- `{file_name}`: 컨트롤러 클래스\n"
        
        content += """
#### Views
"""
        
        # JSP 파일들 분류
        for file_path in file_structure['jsp_files']:
            file_name = os.path.basename(file_path)
            content += f"- `{file_name}`: JSP 뷰 페이지\n"
        
        content += """
### 2. Business Layer (비즈니스 계층)
#### Services
"""
        
        # Java 파일들에서 Service 분류
        for file_path in file_structure['java_files']:
            if 'service' in file_path.lower():
                file_name = os.path.basename(file_path)
                content += f"- `{file_name}`: 서비스 클래스\n"
        
        content += """
### 3. Data Access Layer (데이터 접근 계층)
#### Mappers
"""
        
        # Java 파일들에서 Mapper 분류
        for file_path in file_structure['java_files']:
            if 'mapper' in file_path.lower():
                file_name = os.path.basename(file_path)
                content += f"- `{file_name}`: 매퍼 인터페이스\n"
        
        content += """
### 4. Infrastructure Layer (인프라 계층)
#### Config
"""
        
        # Java 파일들에서 Config 분류
        for file_path in file_structure['java_files']:
            if 'config' in file_path.lower():
                file_name = os.path.basename(file_path)
                content += f"- `{file_name}`: 설정 클래스\n"
        
        return content

if __name__ == "__main__":
    analyzer = AIComponentAnalyzer()
    project_path = "../project/sampleSrc"
    result = analyzer.generate_component_diagram(project_path)
    print(result)

