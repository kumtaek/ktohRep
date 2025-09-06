#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
컴포넌트 분석기 - 메타정보를 기반으로 프로젝트 컴포넌트 구조 분석
"""

import sqlite3
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Component:
    """컴포넌트 정보"""
    name: str
    type: str  # 'Controller', 'Service', 'Mapper', 'View', 'Config', 'Util'
    layer: str  # 'Presentation', 'Business', 'Data Access', 'Infrastructure'
    file_path: str
    description: str = ""
    methods: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class LayerInfo:
    """계층 정보"""
    name: str
    components: List[Component]
    description: str = ""
    
    def __post_init__(self):
        if self.components is None:
            self.components = []

@dataclass
class ProjectStructure:
    """프로젝트 구조 정보"""
    project_name: str
    layers: List[LayerInfo]
    total_components: int
    analysis_time: datetime
    
    def __post_init__(self):
        if self.layers is None:
            self.layers = []

class ComponentAnalyzer:
    """컴포넌트 분석기"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.metadata_db = self.project_path / "metadata.db"
        self.src_path = self.project_path / "src"
        
        # 계층별 컴포넌트 분류 규칙
        self.layer_rules = {
            'Presentation': {
                'keywords': ['controller', 'view', 'jsp', 'html', 'js', 'css'],
                'types': ['Controller', 'View']
            },
            'Business': {
                'keywords': ['service', 'util', 'helper', 'manager'],
                'types': ['Service', 'Util', 'Manager']
            },
            'Data Access': {
                'keywords': ['mapper', 'dao', 'repository', 'mybatis'],
                'types': ['Mapper', 'DAO', 'Repository']
            },
            'Infrastructure': {
                'keywords': ['config', 'configuration', 'database', 'db'],
                'types': ['Config', 'Database']
            }
        }
        
        # 컴포넌트 타입 분류 규칙
        self.type_rules = {
            'Controller': ['controller', 'ctrl'],
            'Service': ['service', 'svc'],
            'Mapper': ['mapper', 'dao'],
            'View': ['jsp', 'html', 'view'],
            'Config': ['config', 'configuration'],
            'Util': ['util', 'helper', 'manager']
        }
    
    def analyze_components(self) -> ProjectStructure:
        """컴포넌트 구조 분석"""
        logger.info(f"컴포넌트 분석 시작: {self.project_path}")
        
        # 메타정보에서 파일 정보 조회
        files_info = self._get_files_from_metadata()
        
        # 소스 파일에서 추가 정보 수집
        source_components = self._analyze_source_files()
        
        # 컴포넌트 통합 및 분류
        all_components = self._merge_components(files_info, source_components)
        
        # 계층별로 그룹화
        layers = self._group_by_layers(all_components)
        
        # 프로젝트 구조 생성
        project_structure = ProjectStructure(
            project_name=self.project_path.name,
            layers=layers,
            total_components=len(all_components),
            analysis_time=datetime.now()
        )
        
        logger.info(f"컴포넌트 분석 완료: {len(all_components)}개 컴포넌트, {len(layers)}개 계층")
        return project_structure
    
    def _get_files_from_metadata(self) -> List[Dict]:
        """메타정보에서 파일 정보 조회"""
        files_info = []
        
        if not self.metadata_db.exists():
            logger.warning(f"메타정보 DB가 존재하지 않습니다: {self.metadata_db}")
            return files_info
        
        try:
            conn = sqlite3.connect(self.metadata_db)
            cursor = conn.cursor()
            
            # 파일 정보 조회
            cursor.execute("""
                SELECT file_path, file_name, file_type, line_count, hash_value
                FROM files
                ORDER BY file_path
            """)
            
            for row in cursor.fetchall():
                file_path, file_name, file_type, line_count, hash_value = row
                files_info.append({
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_type': file_type,
                    'line_count': line_count,
                    'hash_value': hash_value
                })
            
            conn.close()
            logger.info(f"메타정보에서 {len(files_info)}개 파일 정보 조회")
            
        except Exception as e:
            logger.error(f"메타정보 조회 오류: {e}")
        
        return files_info
    
    def _analyze_source_files(self) -> List[Component]:
        """소스 파일 분석"""
        components = []
        
        if not self.src_path.exists():
            logger.warning(f"소스 경로가 존재하지 않습니다: {self.src_path}")
            return components
        
        # Java 파일 분석
        java_files = list(self.src_path.rglob("*.java"))
        for java_file in java_files:
            component = self._analyze_java_file(java_file)
            if component:
                components.append(component)
        
        # JSP 파일 분석
        jsp_files = list(self.src_path.rglob("*.jsp"))
        for jsp_file in jsp_files:
            component = self._analyze_jsp_file(jsp_file)
            if component:
                components.append(component)
        
        # HTML 파일 분석
        html_files = list(self.src_path.rglob("*.html"))
        for html_file in html_files:
            component = self._analyze_html_file(html_file)
            if component:
                components.append(component)
        
        logger.info(f"소스 파일 분석 완료: {len(components)}개 컴포넌트")
        return components
    
    def _analyze_java_file(self, file_path: Path) -> Component:
        """Java 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = file_path.name
            relative_path = str(file_path.relative_to(self.src_path))
            
            # 컴포넌트 타입 결정
            component_type = self._determine_component_type(file_name, content)
            
            # 계층 결정
            layer = self._determine_layer(file_name, content, component_type)
            
            # 메서드 추출
            methods = self._extract_methods(content)
            
            # 의존성 추출
            dependencies = self._extract_dependencies(content)
            
            # 설명 생성
            description = self._generate_description(component_type, file_name, methods)
            
            return Component(
                name=file_name,
                type=component_type,
                layer=layer,
                file_path=relative_path,
                description=description,
                methods=methods,
                dependencies=dependencies
            )
            
        except Exception as e:
            logger.error(f"Java 파일 분석 오류 {file_path}: {e}")
            return None
    
    def _analyze_jsp_file(self, file_path: Path) -> Component:
        """JSP 파일 분석"""
        try:
            file_name = file_path.name
            relative_path = str(file_path.relative_to(self.src_path))
            
            return Component(
                name=file_name,
                type='View',
                layer='Presentation',
                file_path=relative_path,
                description=f"JSP 뷰 화면 - {file_name.replace('.jsp', '')}"
            )
            
        except Exception as e:
            logger.error(f"JSP 파일 분석 오류 {file_path}: {e}")
            return None
    
    def _analyze_html_file(self, file_path: Path) -> Component:
        """HTML 파일 분석"""
        try:
            file_name = file_path.name
            relative_path = str(file_path.relative_to(self.src_path))
            
            return Component(
                name=file_name,
                type='View',
                layer='Presentation',
                file_path=relative_path,
                description=f"HTML 뷰 화면 - {file_name.replace('.html', '')}"
            )
            
        except Exception as e:
            logger.error(f"HTML 파일 분석 오류 {file_path}: {e}")
            return None
    
    def _determine_component_type(self, file_name: str, content: str) -> str:
        """컴포넌트 타입 결정"""
        file_name_lower = file_name.lower()
        
        for component_type, keywords in self.type_rules.items():
            for keyword in keywords:
                if keyword in file_name_lower:
                    return component_type
        
        # 클래스명으로 판단
        if '@Controller' in content or 'extends Controller' in content:
            return 'Controller'
        elif '@Service' in content or 'Service' in content:
            return 'Service'
        elif '@Mapper' in content or 'Mapper' in content:
            return 'Mapper'
        elif '@Configuration' in content or 'Configuration' in content:
            return 'Config'
        
        return 'Util'
    
    def _determine_layer(self, file_name: str, content: str, component_type: str) -> str:
        """계층 결정"""
        file_name_lower = file_name.lower()
        
        for layer_name, rules in self.layer_rules.items():
            # 키워드로 판단
            for keyword in rules['keywords']:
                if keyword in file_name_lower:
                    return layer_name
            
            # 타입으로 판단
            if component_type in rules['types']:
                return layer_name
        
        return 'Infrastructure'
    
    def _extract_methods(self, content: str) -> List[str]:
        """메서드 추출"""
        methods = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # public, private, protected 메서드 추출
            if (line.startswith('public ') or line.startswith('private ') or line.startswith('protected ')) and '(' in line and ')' in line:
                # 메서드명 추출
                if ' ' in line and '(' in line:
                    method_part = line.split('(')[0]
                    method_name = method_part.split()[-1]
                    if method_name and not method_name in ['class', 'interface', 'enum']:
                        methods.append(method_name)
        
        return methods[:10]  # 최대 10개만 반환
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """의존성 추출"""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # import 문 추출
            if line.startswith('import '):
                import_path = line.replace('import ', '').replace(';', '')
                if import_path:
                    dependencies.append(import_path)
        
        return dependencies[:10]  # 최대 10개만 반환
    
    def _generate_description(self, component_type: str, file_name: str, methods: List[str]) -> str:
        """설명 생성"""
        base_name = file_name.replace('.java', '').replace('.jsp', '').replace('.html', '')
        
        descriptions = {
            'Controller': f"{base_name} - 요청 처리 및 응답 제어",
            'Service': f"{base_name} - 비즈니스 로직 처리",
            'Mapper': f"{base_name} - 데이터 접근 및 SQL 매핑",
            'View': f"{base_name} - 사용자 인터페이스 화면",
            'Config': f"{base_name} - 설정 및 구성 관리",
            'Util': f"{base_name} - 유틸리티 및 헬퍼 기능"
        }
        
        description = descriptions.get(component_type, f"{base_name} - {component_type} 컴포넌트")
        
        if methods:
            description += f" (주요 메서드: {', '.join(methods[:3])})"
        
        return description
    
    def _merge_components(self, files_info: List[Dict], source_components: List[Component]) -> List[Component]:
        """컴포넌트 통합"""
        all_components = source_components.copy()
        
        # 메타정보의 파일 중 소스 분석에 포함되지 않은 것들 추가
        analyzed_files = {comp.file_path for comp in source_components}
        
        for file_info in files_info:
            file_path = file_info['file_path']
            if file_path not in analyzed_files:
                # 간단한 컴포넌트 생성
                component = Component(
                    name=file_info['file_name'],
                    type='File',
                    layer='Infrastructure',
                    file_path=file_path,
                    description=f"파일 - {file_info['file_name']}"
                )
                all_components.append(component)
        
        return all_components
    
    def _group_by_layers(self, components: List[Component]) -> List[LayerInfo]:
        """계층별로 그룹화"""
        layer_groups = {}
        
        for component in components:
            layer_name = component.layer
            if layer_name not in layer_groups:
                layer_groups[layer_name] = []
            layer_groups[layer_name].append(component)
        
        # 계층 정보 생성
        layers = []
        layer_descriptions = {
            'Presentation': '사용자 인터페이스 및 요청 처리 계층',
            'Business': '비즈니스 로직 및 서비스 계층',
            'Data Access': '데이터 접근 및 영속성 계층',
            'Infrastructure': '설정 및 인프라 계층'
        }
        
        for layer_name, layer_components in layer_groups.items():
            layer_info = LayerInfo(
                name=layer_name,
                components=layer_components,
                description=layer_descriptions.get(layer_name, f"{layer_name} 계층")
            )
            layers.append(layer_info)
        
        # 계층 순서 정렬
        layer_order = ['Presentation', 'Business', 'Data Access', 'Infrastructure']
        layers.sort(key=lambda x: layer_order.index(x.name) if x.name in layer_order else 999)
        
        return layers