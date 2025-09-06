#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 컴포넌트 다이어그램 생성기
- AI 분석 결과를 바탕으로 마크다운 형식의 컴포넌트 다이어그램 생성
- Mermaid 다이어그램 포함
- 상세한 컴포넌트 정보 및 관계 분석
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import asdict

from ai_component_analyzer import ProjectStructureAnalyzer, AIComponentAnalyzer, ProjectStructure

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIComponentDiagramGenerator:
    """AI 기반 컴포넌트 다이어그램 생성기"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.output_dir = self.project_path / "report"
        
        # 분석기 초기화
        self.structure_analyzer = ProjectStructureAnalyzer(str(self.project_path))
        self.ai_analyzer = AIComponentAnalyzer()
        
    def generate_diagram(self) -> str:
        """컴포넌트 다이어그램 생성"""
        logger.info(f"컴포넌트 다이어그램 생성 시작: {self.project_name}")
        
        # 1. 프로젝트 구조 분석
        project_structure = self.structure_analyzer.analyze_project()
        logger.info(f"프로젝트 구조 분석 완료: {len(project_structure.layers)}개 계층")
        
        # 2. AI 분석
        ai_analysis = self.ai_analyzer.analyze_with_ai(project_structure)
        logger.info("AI 분석 완료")
        
        # 3. 다이어그램 생성
        diagram_content = self._generate_diagram_content(project_structure, ai_analysis)
        
        # 4. 파일 저장
        output_file = self._save_diagram(diagram_content)
        
        logger.info(f"컴포넌트 다이어그램 생성 완료: {output_file}")
        return output_file
    
    def _generate_diagram_content(self, project_structure: ProjectStructure, ai_analysis: str) -> str:
        """다이어그램 내용 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        content = f"""# {self.project_name} AI 컴포넌트 다이어그램

> 생성일시: {datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")}  
> 분석 도구: AI 기반 컴포넌트 분석기 (Ollama + Qwen2.5)

---

## 📊 프로젝트 개요

| 항목 | 값 |
|------|-----|
| **프로젝트명** | {project_structure.project_name} |
| **총 파일 수** | {project_structure.total_files:,}개 |
| **총 라인 수** | {project_structure.total_lines:,}줄 |
| **계층 수** | {len(project_structure.layers)}개 |
| **컴포넌트 수** | {sum(len(layer.components) for layer in project_structure.layers)}개 |

---

## 🏗️ 아키텍처 다이어그램

```mermaid
graph TB
    subgraph "Presentation Layer"
        C[Controller Layer<br/>{len([c for layer in project_structure.layers if layer.name == 'Controller' for c in layer.components])} components]
    end
    
    subgraph "Business Layer"
        S[Service Layer<br/>{len([c for layer in project_structure.layers if layer.name == 'Service' for c in layer.components])} components]
    end
    
    subgraph "Data Access Layer"
        M[Mapper Layer<br/>{len([c for layer in project_structure.layers if layer.name == 'Mapper' for c in layer.components])} components]
    end
    
    subgraph "Domain Layer"
        E[Entity Layer<br/>{len([c for layer in project_structure.layers if layer.name == 'Entity' for c in layer.components])} components]
    end
    
    subgraph "Configuration Layer"
        CFG[Config Layer<br/>{len([c for layer in project_structure.layers if layer.name == 'Config' for c in layer.components])} components]
    end
    
    C --> S
    S --> M
    M --> E
    CFG -.-> C
    CFG -.-> S
    CFG -.-> M
```

---

## 🤖 AI 분석 결과

{ai_analysis}

---

## 📋 계층별 상세 분석

"""
        
        # 계층별 상세 정보
        for layer in project_structure.layers:
            content += self._generate_layer_section(layer)
        
        # 의존성 분석
        content += self._generate_dependency_section(project_structure)
        
        # 통계 정보
        content += self._generate_statistics_section(project_structure)
        
        # 개선 제안
        content += self._generate_improvement_section(project_structure)
        
        return content
    
    def _generate_layer_section(self, layer) -> str:
        """계층별 섹션 생성"""
        content = f"""
### 🔹 {layer.name} 계층

**역할**: {layer.description}  
**컴포넌트 수**: {len(layer.components)}개

| 컴포넌트명 | 패키지 | 메서드 수 | 주요 어노테이션 |
|------------|--------|-----------|-----------------|
"""
        
        for component in layer.components:
            methods_count = len(component.methods)
            annotations = ', '.join(component.annotations[:3]) if component.annotations else '-'
            content += f"| `{component.name}` | `{component.package}` | {methods_count}개 | {annotations} |\n"
        
        # 주요 컴포넌트 상세 정보
        if layer.components:
            content += f"""
#### 주요 컴포넌트 상세

"""
            for component in layer.components[:3]:  # 최대 3개
                content += f"""
**{component.name}**
- **파일 경로**: `{component.file_path}`
- **메서드**: {', '.join(component.methods[:5]) if component.methods else '없음'}
- **의존성**: {', '.join(component.dependencies[:5]) if component.dependencies else '없음'}
"""
        
        return content
    
    def _generate_dependency_section(self, project_structure: ProjectStructure) -> str:
        """의존성 분석 섹션 생성"""
        content = """
---

## 🔗 컴포넌트 의존성 분석

### 의존성 다이어그램

```mermaid
graph LR
"""
        
        # 계층별 의존성
        layer_deps = {
            'Controller': 'Service',
            'Service': 'Mapper', 
            'Mapper': 'Entity',
            'Config': ['Controller', 'Service', 'Mapper']
        }
        
        for from_layer, to_layer in layer_deps.items():
            if isinstance(to_layer, list):
                for to in to_layer:
                    content += f"    {from_layer[0]} --> {to[0]}\n"
            else:
                content += f"    {from_layer[0]} --> {to_layer[0]}\n"
        
        content += "```\n\n"
        
        # 실제 의존성 통계
        if project_structure.dependencies:
            content += f"""
### 의존성 통계
- **총 의존성 수**: {len(project_structure.dependencies)}개
- **주요 의존성**:
"""
            # 의존성 빈도 계산
            dep_count = {}
            for from_comp, to_comp in project_structure.dependencies:
                key = f"{from_comp} → {to_comp}"
                dep_count[key] = dep_count.get(key, 0) + 1
            
            # 상위 5개 의존성
            sorted_deps = sorted(dep_count.items(), key=lambda x: x[1], reverse=True)
            for dep, count in sorted_deps[:5]:
                content += f"- `{dep}` ({count}회)\n"
        else:
            content += "\n의존성 정보가 없습니다.\n"
        
        return content
    
    def _generate_statistics_section(self, project_structure: ProjectStructure) -> str:
        """통계 정보 섹션 생성"""
        content = """
---

## 📈 코드 품질 통계

### 계층별 통계

| 계층 | 컴포넌트 수 | 비율 |
|------|-------------|------|
"""
        
        total_components = sum(len(layer.components) for layer in project_structure.layers)
        
        for layer in project_structure.layers:
            count = len(layer.components)
            ratio = (count / total_components * 100) if total_components > 0 else 0
            content += f"| {layer.name} | {count}개 | {ratio:.1f}% |\n"
        
        content += f"""
### 전체 통계
- **평균 파일당 라인 수**: {project_structure.total_lines / project_structure.total_files:.1f}줄
- **계층당 평균 컴포넌트 수**: {total_components / len(project_structure.layers):.1f}개
- **아키텍처 복잡도**: {'높음' if total_components > 50 else '중간' if total_components > 20 else '낮음'}
"""
        
        return content
    
    def _generate_improvement_section(self, project_structure: ProjectStructure) -> str:
        """개선 제안 섹션 생성"""
        content = """
---

## 💡 아키텍처 개선 제안

### 1. 구조적 개선
"""
        
        # 계층별 개선 제안
        layer_suggestions = {
            'Controller': '비즈니스 로직을 Service 계층으로 위임하고, 요청/응답 처리에만 집중',
            'Service': '트랜잭션 경계를 명확히 하고, 도메인 로직과 인프라 로직 분리',
            'Mapper': '데이터 접근 로직을 캡슐화하고, 쿼리 최적화 고려',
            'Entity': '도메인 규칙을 엔티티에 포함하고, 불변성 보장',
            'Config': '환경별 설정 분리 및 보안 정보 외부화'
        }
        
        for layer in project_structure.layers:
            if layer.name in layer_suggestions:
                content += f"- **{layer.name} 계층**: {layer_suggestions[layer.name]}\n"
        
        content += """
### 2. 코드 품질 개선
- **메서드 길이**: 20줄 이하로 제한
- **클래스 크기**: 단일 책임 원칙 준수
- **의존성 관리**: 순환 의존성 제거
- **테스트 커버리지**: 단위 테스트 및 통합 테스트 추가

### 3. 성능 최적화
- **캐싱 전략**: 자주 조회되는 데이터 캐싱
- **지연 로딩**: 필요시점에 데이터 로딩
- **배치 처리**: 대량 데이터 처리 최적화
- **연결 풀링**: 데이터베이스 연결 관리

### 4. 보안 강화
- **입력 검증**: 모든 사용자 입력 검증
- **권한 관리**: 역할 기반 접근 제어
- **데이터 암호화**: 민감 정보 암호화
- **로깅 및 모니터링**: 보안 이벤트 추적
"""
        
        return content
    
    def _save_diagram(self, content: str) -> str:
        """다이어그램 파일 저장"""
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_컴포넌트다이어그램_{timestamp}.md"
        output_file = self.output_dir / filename
        
        # 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"다이어그램 저장 완료: {output_file}")
        return str(output_file)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 기반 컴포넌트 다이어그램 생성기')
    parser.add_argument('project_path', help='분석할 프로젝트 경로')
    parser.add_argument('--output', help='출력 디렉토리 (기본값: 프로젝트/report)')
    
    args = parser.parse_args()
    
    try:
        # 생성기 초기화
        generator = AIComponentDiagramGenerator(args.project_path)
        
        # 다이어그램 생성
        output_file = generator.generate_diagram()
        
        print(f"✅ AI 컴포넌트 다이어그램 생성 완료!")
        print(f"📁 출력 파일: {output_file}")
        
    except Exception as e:
        logger.error(f"다이어그램 생성 실패: {e}")
        raise

if __name__ == "__main__":
    main()