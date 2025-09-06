#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 컴포넌트 다이어그램 분석기
- 프로젝트 소스 구조를 동적으로 분석
- LLM을 활용하여 컴포넌트 역할과 관계 분석
- 마크다운 형식의 컴포넌트 다이어그램 생성
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
import requests
import subprocess
import time

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass
class Component:
    """컴포넌트 정보"""
    name: str
    type: str  # Controller, Service, Mapper, Entity, Config, etc.
    package: str
    file_path: str
    methods: List[str]
    dependencies: List[str]
    annotations: List[str]
    description: str = ""

@dataclass
class Layer:
    """계층 정보"""
    name: str
    components: List[Component]
    description: str = ""

@dataclass
class ProjectStructure:
    """프로젝트 구조 정보"""
    project_name: str
    layers: List[Layer]
    dependencies: List[Tuple[str, str]]  # (from, to)
    total_files: int
    total_lines: int

class ProjectStructureAnalyzer:
    """프로젝트 구조 분석기"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"
        self.components: List[Component] = []
        self.layers: Dict[str, Layer] = {}
        
        # Java 패키지 패턴
        self.java_patterns = {
            'controller': r'.*controller.*|.*web.*|.*api.*',
            'service': r'.*service.*|.*business.*',
            'mapper': r'.*mapper.*|.*dao.*|.*repository.*',
            'entity': r'.*entity.*|.*model.*|.*domain.*|.*vo.*|.*dto.*',
            'config': r'.*config.*|.*configuration.*',
            'util': r'.*util.*|.*helper.*|.*common.*'
        }
    
    def analyze_project(self) -> ProjectStructure:
        """프로젝트 전체 구조 분석"""
        logger.info(f"프로젝트 분석 시작: {self.project_path}")
        
        # 소스 파일 스캔
        java_files = self._scan_java_files()
        logger.info(f"Java 파일 {len(java_files)}개 발견")
        
        # 각 파일 분석
        for file_path in java_files:
            component = self._analyze_java_file(file_path)
            if component:
                self.components.append(component)
        
        # 계층별 분류
        self._classify_components()
        
        # 의존성 분석
        dependencies = self._analyze_dependencies()
        
        # 통계 정보
        total_files = len(java_files)
        total_lines = sum(self._count_lines(f) for f in java_files)
        
        return ProjectStructure(
            project_name=self.project_path.name,
            layers=list(self.layers.values()),
            dependencies=dependencies,
            total_files=total_files,
            total_lines=total_lines
        )
    
    def _scan_java_files(self) -> List[Path]:
        """Java 파일 스캔"""
        java_files = []
        
        if not self.src_path.exists():
            logger.warning(f"src 경로가 존재하지 않습니다: {self.src_path}")
            return java_files
        
        for file_path in self.src_path.rglob("*.java"):
            java_files.append(file_path)
        
        return java_files
    
    def _analyze_java_file(self, file_path: Path) -> Optional[Component]:
        """Java 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 패키지 정보 추출
            package_match = re.search(r'package\s+([^;]+);', content)
            package = package_match.group(1) if package_match else ""
            
            # 클래스명 추출
            class_match = re.search(r'(?:public\s+)?(?:class|interface|enum)\s+(\w+)', content)
            class_name = class_match.group(1) if class_match else file_path.stem
            
            # 메서드 추출
            methods = self._extract_methods(content)
            
            # 어노테이션 추출
            annotations = self._extract_annotations(content)
            
            # 의존성 추출
            dependencies = self._extract_dependencies(content)
            
            # 컴포넌트 타입 결정
            component_type = self._determine_component_type(package, class_name, annotations)
            
            return Component(
                name=class_name,
                type=component_type,
                package=package,
                file_path=str(file_path.relative_to(self.project_path)),
                methods=methods,
                dependencies=dependencies,
                annotations=annotations
            )
            
        except Exception as e:
            logger.error(f"파일 분석 오류 {file_path}: {e}")
            return None
    
    def _extract_methods(self, content: str) -> List[str]:
        """메서드 추출"""
        methods = []
        # 간단한 메서드 패턴 매칭
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>,\s]+\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        matches = re.findall(method_pattern, content)
        methods.extend(matches)
        return methods[:10]  # 최대 10개만
    
    def _extract_annotations(self, content: str) -> List[str]:
        """어노테이션 추출"""
        annotations = []
        annotation_pattern = r'@(\w+)'
        matches = re.findall(annotation_pattern, content)
        annotations.extend(matches)
        return list(set(annotations))  # 중복 제거
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """의존성 추출 (import 문)"""
        dependencies = []
        import_pattern = r'import\s+([^;]+);'
        matches = re.findall(import_pattern, content)
        for match in matches:
            # 패키지명에서 클래스명 추출
            if '.' in match:
                class_name = match.split('.')[-1]
                dependencies.append(class_name)
        return dependencies[:20]  # 최대 20개만
    
    def _determine_component_type(self, package: str, class_name: str, annotations: List[str]) -> str:
        """컴포넌트 타입 결정"""
        package_lower = package.lower()
        class_lower = class_name.lower()
        annotations_lower = [ann.lower() for ann in annotations]
        
        # 어노테이션 기반 판단
        if any(ann in ['Controller', 'RestController'] for ann in annotations):
            return 'Controller'
        elif any(ann in ['Service', 'Component'] for ann in annotations):
            return 'Service'
        elif any(ann in ['Repository', 'Mapper'] for ann in annotations):
            return 'Mapper'
        elif any(ann in ['Entity', 'Table'] for ann in annotations):
            return 'Entity'
        elif any(ann in ['Configuration', 'Config'] for ann in annotations):
            return 'Config'
        
        # 패키지명 기반 판단
        for layer_type, pattern in self.java_patterns.items():
            if re.match(pattern, package_lower) or re.match(pattern, class_lower):
                return layer_type.title()
        
        # 기본값
        return 'Component'
    
    def _classify_components(self):
        """컴포넌트를 계층별로 분류"""
        layer_groups = {
            'Controller': [],
            'Service': [],
            'Mapper': [],
            'Entity': [],
            'Config': [],
            'Util': []
        }
        
        for component in self.components:
            layer_type = component.type
            if layer_type in layer_groups:
                layer_groups[layer_type].append(component)
            else:
                layer_groups['Util'].append(component)
        
        # 계층 생성
        for layer_name, components in layer_groups.items():
            if components:  # 컴포넌트가 있는 계층만
                self.layers[layer_name] = Layer(
                    name=layer_name,
                    components=components,
                    description=self._get_layer_description(layer_name)
                )
    
    def _get_layer_description(self, layer_name: str) -> str:
        """계층별 설명"""
        descriptions = {
            'Controller': '사용자 요청을 받아 비즈니스 로직을 호출하는 웹 계층',
            'Service': '비즈니스 로직을 처리하는 서비스 계층',
            'Mapper': '데이터베이스 접근을 담당하는 데이터 접근 계층',
            'Entity': '데이터베이스 테이블과 매핑되는 엔티티 클래스',
            'Config': '애플리케이션 설정을 담당하는 설정 계층',
            'Util': '공통 유틸리티 및 헬퍼 클래스'
        }
        return descriptions.get(layer_name, '기타 컴포넌트')
    
    def _analyze_dependencies(self) -> List[Tuple[str, str]]:
        """컴포넌트 간 의존성 분석"""
        dependencies = []
        
        for component in self.components:
            for dep in component.dependencies:
                # 의존하는 컴포넌트 찾기
                for other_component in self.components:
                    if dep == other_component.name:
                        dependencies.append((component.name, other_component.name))
                        break
        
        return dependencies
    
    def _count_lines(self, file_path: Path) -> int:
        """파일 라인 수 계산"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0

class AIComponentAnalyzer:
    """AI 기반 컴포넌트 분석기"""
    
    def __init__(self, config_path: str = "config/ai_config.yaml"):
        from ai_model_client import AIModelManager
        self.ai_client = AIModelManager(config_path)
        
    
    def analyze_with_ai(self, project_structure: ProjectStructure) -> str:
        """AI를 활용한 컴포넌트 분석"""
        logger.info("🤖 AI 분석 시작")
        
        # 프로젝트 정보 수집
        logger.info("📊 프로젝트 정보 수집 중...")
        project_info = self._collect_project_info(project_structure)
        logger.info(f"📋 수집된 정보: {len(project_info['layers'])}개 계층, {project_info['total_files']}개 파일")
        
        # 프롬프트 생성
        logger.info("📝 AI 프롬프트 생성 중...")
        prompt = self._generate_analysis_prompt(project_info)
        logger.info(f"📄 생성된 프롬프트: {len(prompt)}자")
        logger.debug(f"📝 프롬프트 내용:\n{prompt}")
        
        # AI 모델 호출 (공통 클라이언트 사용)
        try:
            logger.info("🚀 AI 모델 호출 시작...")
            response = self.ai_client.generate(prompt)
            if response:
                logger.info("✅ AI 분석 완료")
                logger.info(f"📄 AI 응답 길이: {len(response)}자")
                return response
            else:
                logger.warning("⚠️ AI 응답이 비어있음")
        except Exception as e:
            logger.warning(f"⚠️ AI 모델 호출 실패: {e}")
        
        # AI 호출 실패 시 기본 분석
        logger.info("🔄 AI 호출 실패, 기본 분석 사용")
        return self._generate_default_analysis(project_structure)
    
    def _collect_project_info(self, project_structure: ProjectStructure) -> dict:
        """프로젝트 정보 수집"""
        info = {
            'project_name': project_structure.project_name,
            'total_files': project_structure.total_files,
            'total_lines': project_structure.total_lines,
            'layers': []
        }
        
        for layer in project_structure.layers:
            layer_info = {
                'name': layer.name,
                'component_count': len(layer.components),
                'components': []
            }
            
            for component in layer.components:
                component_info = {
                    'name': component.name,
                    'package': component.package,
                    'methods': component.methods[:5],  # 최대 5개
                    'annotations': component.annotations
                }
                layer_info['components'].append(component_info)
            
            info['layers'].append(layer_info)
        
        return info
    
    def _generate_analysis_prompt(self, project_info: dict) -> str:
        """AI 분석 프롬프트 생성"""
        logger.info("📝 프롬프트 구성 중...")
        
        prompt = f"""Java 프로젝트 분석: {project_info['project_name']}
파일: {project_info['total_files']}개, 라인: {project_info['total_lines']}줄

계층별 컴포넌트:
"""
        
        for layer in project_info['layers']:
            prompt += f"\n{layer['name']} 계층 ({layer['component_count']}개):\n"
            for component in layer['components'][:3]:  # 최대 3개만
                prompt += f"- {component['name']}\n"
        
        prompt += """

아키텍처 패턴, 계층별 역할, 컴포넌트 관계, 설계 품질, 개선 제안을 마크다운으로 분석해주세요.
"""
        
        logger.info(f"📄 프롬프트 구성 완료: {len(prompt)}자")
        logger.info(f"📋 포함된 계층: {[layer['name'] for layer in project_info['layers']]}")
        
        return prompt
    
    
    def _generate_default_analysis(self, project_structure: ProjectStructure) -> str:
        """AI 호출 실패 시 기본 분석"""
        analysis = f"""# {project_structure.project_name} 컴포넌트 분석

## 프로젝트 개요
- **총 파일 수**: {project_structure.total_files}개
- **총 라인 수**: {project_structure.total_lines:,}줄
- **계층 수**: {len(project_structure.layers)}개

## 계층별 분석
"""
        
        for layer in project_structure.layers:
            analysis += f"""
### {layer.name} 계층
- **컴포넌트 수**: {len(layer.components)}개
- **역할**: {layer.description}

**주요 컴포넌트:**
"""
            for component in layer.components[:5]:  # 최대 5개
                analysis += f"- `{component.name}` ({component.package})\n"
                if component.methods:
                    analysis += f"  - 메서드: {', '.join(component.methods[:3])}\n"
                if component.annotations:
                    analysis += f"  - 어노테이션: {', '.join(component.annotations[:3])}\n"
        
        analysis += """
## 아키텍처 패턴
- **계층형 아키텍처**: Controller → Service → Mapper → Entity 구조
- **의존성 주입**: Spring Framework 기반 DI 패턴
- **MVC 패턴**: Model-View-Controller 분리

## 개선 제안
1. **패키지 구조 최적화**: 계층별 패키지 분리 강화
2. **의존성 관리**: 순환 의존성 제거
3. **코드 품질**: 메서드 길이 및 복잡도 개선
"""
        
        return analysis

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 컴포넌트 분석기 테스트')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    
    args = parser.parse_args()
    
    # 테스트 실행
    project_path = f"../project/{args.project_name}"
    analyzer = ProjectStructureAnalyzer(project_path)
    structure = analyzer.analyze_project()
    
    ai_analyzer = AIComponentAnalyzer()
    analysis = ai_analyzer.analyze_with_ai(structure)
    
    print("=== AI 컴포넌트 분석 결과 ===")
    print(analysis)
