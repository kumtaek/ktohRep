"""
최적화된 Java 파서 - 필수 메타정보만 추출하여 DB 저장 최소화
"""
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from core.optimized_metadata_engine import OptimizedMetadataEngine
from utils.dynamic_file_reader import DynamicFileReader


class OptimizedJavaParser:
    """
    최적화된 Java 파서
    - 필수적인 메타정보만 추출하여 DB 저장
    - 상세 정보는 파일에서 동적 조회
    """
    
    def __init__(self, metadata_engine: OptimizedMetadataEngine):
        self.metadata_engine = metadata_engine
        self.file_reader = DynamicFileReader()
    
    def parse_java_file(self, project_id: int, file_path: str) -> Dict:
        """Java 파일 파싱 - 필수 정보만 추출"""
        try:
            content = self.file_reader.get_file_content(file_path)
            if not content:
                return {'success': False, 'error': 'Could not read file'}
            
            # 1. 파일 인덱스 추가
            file_id = self.metadata_engine.add_file_index(
                project_id, file_path, 'java'
            )
            
            # 2. 기본 구조 정보만 추출 (패키지, 클래스명, 메서드명)
            structure_info = self._extract_basic_structure(content)
            
            # 3. 컴포넌트 추가 (클래스, 인터페이스)
            component_ids = {}
            for class_info in structure_info['classes']:
                component_id = self.metadata_engine.add_component(
                    project_id=project_id,
                    file_id=file_id,
                    component_name=class_info['name'],
                    component_type=class_info['type'],  # 'class' 또는 'interface'
                    line_start=class_info.get('line_start'),
                    line_end=class_info.get('line_end')
                )
                component_ids[class_info['name']] = component_id
                
                # 비즈니스 태그 추가 (간단한 도메인 분류)
                domain = self._classify_domain(class_info['name'])
                layer = self._classify_layer(class_info['name'])
                
                if domain or layer:
                    self.metadata_engine.add_business_tag(
                        project_id, component_id, domain, layer
                    )
            
            # 4. 메서드 컴포넌트 추가
            for method_info in structure_info['methods']:
                parent_class = method_info.get('parent_class')
                parent_component_id = component_ids.get(parent_class)
                
                method_id = self.metadata_engine.add_component(
                    project_id=project_id,
                    file_id=file_id,
                    component_name=method_info['name'],
                    component_type='method',
                    line_start=method_info.get('line_start'),
                    line_end=method_info.get('line_end'),
                    parent_component_id=parent_component_id
                )
                component_ids[f"{parent_class}.{method_info['name']}"] = method_id
            
            # 5. 기본 관계 정보 추가 (extends, implements만)
            self._add_basic_relationships(
                project_id, structure_info, component_ids
            )
            
            return {
                'success': True,
                'file_id': file_id,
                'components_created': len(component_ids),
                'structure_info': structure_info
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_basic_structure(self, content: str) -> Dict:
        """기본 구조 정보만 추출 (상세 내용 제외)"""
        structure = {
            'package': None,
            'classes': [],
            'methods': [],
            'basic_relationships': []
        }
        
        lines = content.split('\n')
        
        # 패키지명 추출
        for line in lines:
            if line.strip().startswith('package '):
                structure['package'] = line.strip().replace('package ', '').replace(';', '')
                break
        
        # 클래스/인터페이스 추출
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        
        for i, line in enumerate(lines, 1):
            class_match = re.search(class_pattern, line)
            if class_match:
                class_type = class_match.group(1)  # 'class' or 'interface'
                class_name = class_match.group(2)
                extends = class_match.group(3)
                implements = class_match.group(4)
                
                class_info = {
                    'name': class_name,
                    'type': class_type,
                    'line_start': i,
                    'line_end': None,  # 필요시 동적 계산
                    'extends': extends,
                    'implements': implements.split(',') if implements else []
                }
                structure['classes'].append(class_info)
        
        # 메서드 기본 정보만 추출 (시그니처는 동적 조회시)
        method_pattern = r'(?:public|private|protected|static|final|abstract)?\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        current_class = None
        
        for i, line in enumerate(lines, 1):
            # 현재 클래스 추적
            for class_info in structure['classes']:
                if class_info['line_start'] == i:
                    current_class = class_info['name']
                    break
            
            method_match = re.search(method_pattern, line)
            if method_match and current_class:
                return_type = method_match.group(1)
                method_name = method_match.group(2)
                
                # 생성자, getter/setter 등은 우선순위 낮게 설정
                priority = self._calculate_method_priority(method_name, return_type)
                
                method_info = {
                    'name': method_name,
                    'return_type': return_type,
                    'parent_class': current_class,
                    'line_start': i,
                    'priority': priority
                }
                structure['methods'].append(method_info)
        
        return structure
    
    def _classify_domain(self, class_name: str) -> Optional[str]:
        """클래스명으로 비즈니스 도메인 분류"""
        name_lower = class_name.lower()
        
        if any(keyword in name_lower for keyword in ['user', 'member', 'account']):
            return 'user'
        elif any(keyword in name_lower for keyword in ['order', 'cart', 'purchase']):
            return 'order'
        elif any(keyword in name_lower for keyword in ['product', 'item', 'goods']):
            return 'product'
        elif any(keyword in name_lower for keyword in ['payment', 'billing']):
            return 'payment'
        elif any(keyword in name_lower for keyword in ['auth', 'login', 'security']):
            return 'auth'
        else:
            return None
    
    def _classify_layer(self, class_name: str) -> Optional[str]:
        """클래스명으로 아키텍처 레이어 분류"""
        name_lower = class_name.lower()
        
        if name_lower.endswith('controller'):
            return 'controller'
        elif name_lower.endswith('service'):
            return 'service'
        elif any(suffix in name_lower for suffix in ['dao', 'repository']):
            return 'dao'
        elif any(suffix in name_lower for suffix in ['entity', 'model', 'vo', 'dto']):
            return 'entity'
        elif name_lower.endswith('util') or name_lower.endswith('utils'):
            return 'util'
        else:
            return None
    
    def _calculate_method_priority(self, method_name: str, return_type: str) -> int:
        """메서드 우선순위 계산 (1: 높음, 5: 낮음)"""
        name_lower = method_name.lower()
        
        # 생성자는 중간 우선순위
        if method_name.startswith(method_name[0].upper()):
            return 3
        
        # getter/setter는 낮은 우선순위
        if name_lower.startswith(('get', 'set', 'is')):
            return 4
        
        # 비즈니스 로직 메서드는 높은 우선순위
        if any(keyword in name_lower for keyword in ['process', 'execute', 'handle', 'create', 'update', 'delete']):
            return 1
        
        # main 메서드는 높은 우선순위
        if method_name == 'main':
            return 1
        
        # 기본 우선순위
        return 3
    
    def _add_basic_relationships(self, project_id: int, structure_info: Dict, component_ids: Dict):
        """기본 관계 정보만 추가 (extends, implements)"""
        for class_info in structure_info['classes']:
            src_component_id = component_ids.get(class_info['name'])
            if not src_component_id:
                continue
            
            # extends 관계
            if class_info.get('extends'):
                # 같은 파일 내의 클래스인지 확인
                dst_component_id = component_ids.get(class_info['extends'])
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id, 
                        'extends', confidence=0.9
                    )
            
            # implements 관계
            for interface in class_info.get('implements', []):
                interface = interface.strip()
                dst_component_id = component_ids.get(interface)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'implements', confidence=0.9
                    )


class OptimizedProjectAnalyzer:
    """최적화된 프로젝트 분석기"""
    
    def __init__(self, project_path: str = "./project"):
        self.metadata_engine = OptimizedMetadataEngine(project_path=project_path)
        self.java_parser = OptimizedJavaParser(self.metadata_engine)
        self.project_path = Path(project_path)
    
    def analyze_project(self, project_name: str) -> Dict:
        """프로젝트 전체 분석"""
        # 프로젝트 생성
        project_id = self.metadata_engine.create_project(
            project_name, str(self.project_path)
        )
        
        results = {
            'project_id': project_id,
            'files_processed': 0,
            'components_created': 0,
            'errors': []
        }
        
        # Java 파일들 처리
        java_files = list(self.project_path.rglob('*.java'))
        
        for java_file in java_files:
            relative_path = str(java_file.relative_to(self.project_path))
            
            result = self.java_parser.parse_java_file(project_id, relative_path)
            
            if result['success']:
                results['files_processed'] += 1
                results['components_created'] += result['components_created']
            else:
                results['errors'].append({
                    'file': relative_path,
                    'error': result['error']
                })
        
        # 통계 업데이트
        stats = self.metadata_engine.get_project_statistics(project_id)
        results['statistics'] = stats
        
        return results
    
    def quick_search(self, query: str) -> List[Dict]:
        """빠른 검색 (메타DB만 사용)"""
        return self.metadata_engine.search_components(query)
    
    def detailed_analysis(self, component_name: str) -> Dict:
        """상세 분석 (하이브리드 방식)"""
        return self.metadata_engine.get_component_full_details(component_name)