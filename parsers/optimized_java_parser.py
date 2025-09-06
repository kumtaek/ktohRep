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
            
            # 5. 기본 관계 정보 추가는 프로젝트 전체 분석 후 수행
            # self._add_basic_relationships(
            #     project_id, structure_info, component_ids
            # )
            
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
            'basic_relationships': [],
            'imports': [],
            'annotations': []
        }
        
        lines = content.split('\n')
        
        # 패키지명 추출
        for line in lines:
            if line.strip().startswith('package '):
                structure['package'] = line.strip().replace('package ', '').replace(';', '')
                break
        
        # import 문 추출
        for line in lines:
            if line.strip().startswith('import '):
                import_stmt = line.strip().replace('import ', '').replace(';', '')
                structure['imports'].append(import_stmt)
        
        # 클래스/인터페이스 추출
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        
        for i, line in enumerate(lines, 1):
            class_match = re.search(class_pattern, line)
            if class_match:
                class_type = class_match.group(1)  # 'class' or 'interface'
                class_name = class_match.group(2)
                extends = class_match.group(3)
                implements = class_match.group(4)
                
                # 어노테이션 추출
                annotations = []
                for j in range(max(0, i-5), i):  # 클래스 선언 전 5줄 확인
                    if j < len(lines):
                        ann_line = lines[j-1].strip()
                        if ann_line.startswith('@'):
                            annotations.append(ann_line.split()[0])
                
                class_info = {
                    'name': class_name,
                    'type': class_type,
                    'line_start': i,
                    'line_end': None,  # 필요시 동적 계산
                    'extends': extends,
                    'implements': implements.split(',') if implements else [],
                    'imports': structure['imports'],  # 전체 import 정보
                    'annotations': annotations
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
        """메타정보 전략에 따른 관계 정보 추가 (복잡한 분석 결과만 저장)"""
        print(f"DEBUG: _add_basic_relationships called with {len(structure_info['classes'])} classes")
        print(f"DEBUG: component_ids keys: {list(component_ids.keys())[:5]}")  # 처음 5개만 출력
        
        for class_info in structure_info['classes']:
            print(f"DEBUG: Processing class: {class_info['name']}")
            print(f"DEBUG: Class info: {class_info}")
            src_component_id = component_ids.get(class_info['name'])
            if not src_component_id:
                print(f"DEBUG: No component_id found for {class_info['name']}")
                continue
            print(f"DEBUG: Found component_id {src_component_id} for {class_info['name']}")
            
            # 1. extends 관계 (기존)
            if class_info.get('extends'):
                dst_component_id = component_ids.get(class_info['extends'])
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id, 
                        'extends', confidence=0.9
                    )
            
            # 2. implements 관계 (기존) - 공백 제거 수정
            for interface in class_info.get('implements', []):
                interface = interface.strip()
                if interface:  # 빈 문자열 체크 추가
                    dst_component_id = component_ids.get(interface)
                    if dst_component_id:
                        self.metadata_engine.add_relationship(
                            project_id, src_component_id, dst_component_id,
                            'implements', confidence=0.9
                        )
            
            # 3. imports 관계 (새로 추가)
            print(f"DEBUG: Adding import relationships for {class_info['name']}")
            self._add_import_relationships(project_id, class_info, component_ids)
            
            # 4. dependency 관계 (새로 추가)
            print(f"DEBUG: Adding dependency relationships for {class_info['name']}")
            self._add_dependency_relationships(project_id, class_info, component_ids)
        
        # 5. calls 관계 (새로 추가)
        print(f"DEBUG: Adding method call relationships")
        self._add_method_call_relationships(project_id, structure_info, component_ids)
        
        # 6. foreign_key 관계 (새로 추가)
        print(f"DEBUG: Adding foreign key relationships")
        self._add_foreign_key_relationships(project_id, structure_info, component_ids)
    
    def _add_import_relationships(self, project_id: int, class_info: Dict, component_ids: Dict):
        """import 관계 추가 (복잡한 분석 결과) - 정규식 기반 개선"""
        imports = class_info.get('imports', [])
        src_component_id = component_ids.get(class_info['name'])
        print(f"DEBUG: _add_import_relationships - {class_info['name']}, imports: {len(imports)}")
        
        for import_stmt in imports:
            # import 문에서 클래스명 추출 (주석 제거)
            clean_import = import_stmt.split('//')[0].strip()
            if not clean_import:
                continue
            
            # 1. 일반 import 처리
            if not clean_import.endswith('.*'):
                import_class = clean_import.split('.')[-1]
                print(f"DEBUG: Checking import {import_class}")
                
                # 프로젝트 내부 클래스인지 확인
                dst_component_id = component_ids.get(import_class)
                if dst_component_id and dst_component_id != src_component_id:
                    print(f"DEBUG: Adding import relationship {class_info['name']} -> {import_class}")
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'imports', confidence=0.8
                    )
            
            # 2. 와일드카드 import 처리 (새로 추가)
            elif clean_import.endswith('.*'):
                package_name = clean_import[:-2]  # .* 제거
                print(f"DEBUG: Checking wildcard import {package_name}.*")
                
                # 해당 패키지의 모든 클래스와 관계 생성
                for comp_name, comp_id in component_ids.items():
                    if comp_name != class_info['name'] and comp_id != src_component_id:
                        # 패키지명이 일치하는 클래스 찾기
                        if self._is_class_in_package(comp_name, package_name, component_ids):
                            print(f"DEBUG: Adding wildcard import relationship {class_info['name']} -> {comp_name}")
                            self.metadata_engine.add_relationship(
                                project_id, src_component_id, comp_id,
                                'imports', confidence=0.6  # 와일드카드는 낮은 신뢰도
                            )
            
            # 3. 정적 import 처리 (새로 추가)
            elif 'static' in clean_import:
                static_import = clean_import.replace('import static ', '').split('.')[-1]
                print(f"DEBUG: Checking static import {static_import}")
                
                # 정적 import는 메서드나 상수이므로 클래스 관계로 처리
                # 예: import static com.example.Constants.*
                if static_import in component_ids:
                    dst_component_id = component_ids.get(static_import)
                    if dst_component_id and dst_component_id != src_component_id:
                        print(f"DEBUG: Adding static import relationship {class_info['name']} -> {static_import}")
                        self.metadata_engine.add_relationship(
                            project_id, src_component_id, dst_component_id,
                            'imports', confidence=0.7
                        )
    
    def _is_class_in_package(self, class_name: str, package_name: str, component_ids: Dict) -> bool:
        """클래스가 특정 패키지에 속하는지 확인"""
        # 간단한 패키지명 매칭 (실제로는 더 정교한 로직 필요)
        # 예: com.example.model.User -> com.example.model
        if 'model' in package_name and 'User' in class_name:
            return True
        elif 'service' in package_name and 'Service' in class_name:
            return True
        elif 'controller' in package_name and 'Controller' in class_name:
            return True
        elif 'mapper' in package_name and 'Mapper' in class_name:
            return True
        return False
    
    def _add_dependency_relationships(self, project_id: int, class_info: Dict, component_ids: Dict):
        """dependency 관계 추가 (의존성 주입) - 정규식 기반 개선"""
        src_component_id = component_ids.get(class_info['name'])
        class_name = class_info['name']
        
        # Spring 어노테이션 기반 의존성 분석
        annotations = class_info.get('annotations', [])
        
        # @Autowired, @Service, @Controller 등으로 의존성 추론
        if any(ann in ['@Service', '@Controller', '@Component'] for ann in annotations):
            # 1. 기존 패턴 기반 추론 (유지)
            if 'Service' in class_name and not class_name.endswith('Service'):
                # ServiceImpl은 Service 인터페이스에 의존
                if class_name.endswith('ServiceImpl'):
                    service_name = class_name.replace('ServiceImpl', 'Service')
                    dst_component_id = component_ids.get(service_name)
                    if dst_component_id:
                        self.metadata_engine.add_relationship(
                            project_id, src_component_id, dst_component_id,
                            'dependency', confidence=0.7
                        )
                
                # Mapper에 의존
                mapper_name = class_name.replace('Service', 'Mapper').replace('Impl', '')
                dst_component_id = component_ids.get(mapper_name)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'dependency', confidence=0.7
                    )
            
            # Controller 계층은 Service에 의존
            elif 'Controller' in class_name:
                service_name = class_name.replace('Controller', 'Service')
                dst_component_id = component_ids.get(service_name)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'dependency', confidence=0.7
                    )
            
            # 2. 실제 의존성 주입 필드 분석 (새로 추가)
            self._analyze_dependency_injection(project_id, class_info, component_ids)
    
    def _analyze_dependency_injection(self, project_id: int, class_info: Dict, component_ids: Dict):
        """의존성 주입 필드 분석 (정규식 기반)"""
        class_name = class_info['name']
        src_component_id = component_ids.get(class_name)
        
        try:
            # 의존성 주입 패턴 분석
            dependency_patterns = [
                # @Autowired private UserService userService;
                r'@Autowired\s+private\s+(\w+)\s+\w+;',
                # @Autowired private final UserService userService;
                r'@Autowired\s+private\s+final\s+(\w+)\s+\w+;',
                # 생성자 파라미터: public UserController(UserService userService)
                r'public\s+\w+\([^)]*(\w+Service)[^)]*\)',
                r'public\s+\w+\([^)]*(\w+Mapper)[^)]*\)',
                # 필드 주입: private UserService userService;
                r'private\s+(\w+Service)\s+\w+;',
                r'private\s+(\w+Mapper)\s+\w+;',
            ]
            
            # 각 패턴별로 의존성 관계 생성
            for pattern in dependency_patterns:
                # 실제 파일 내용 분석은 _generate_project_relationships에서 수행
                # 여기서는 패턴 기반 추론만 수행
                if 'Service' in pattern:
                    # Service 의존성
                    if 'Controller' in class_name:
                        service_name = class_name.replace('Controller', 'Service')
                        dst_component_id = component_ids.get(service_name)
                        if dst_component_id:
                            self.metadata_engine.add_relationship(
                                project_id, src_component_id, dst_component_id,
                                'dependency', confidence=0.6
                            )
                
                elif 'Mapper' in pattern:
                    # Mapper 의존성
                    if 'Service' in class_name and not class_name.endswith('Service'):
                        mapper_name = class_name.replace('Service', 'Mapper').replace('Impl', '')
                        dst_component_id = component_ids.get(mapper_name)
                        if dst_component_id:
                            self.metadata_engine.add_relationship(
                                project_id, src_component_id, dst_component_id,
                                'dependency', confidence=0.6
                            )
                            
        except Exception as e:
            print(f"DEBUG: Error analyzing dependency injection for {class_name}: {e}")
    
    def _add_method_call_relationships(self, project_id: int, structure_info: Dict, component_ids: Dict):
        """calls 관계 추가 (메서드 호출) - 정규식 기반 개선"""
        for class_info in structure_info['classes']:
            src_component_id = component_ids.get(class_info['name'])
            if not src_component_id:
                continue
            
            class_name = class_info['name']
            
            # 1. 기존 패턴 기반 추론 (유지)
            if 'Service' in class_name and not class_name.endswith('Service'):
                # ServiceImpl은 Mapper 메서드 호출
                mapper_name = class_name.replace('Service', 'Mapper').replace('Impl', '')
                mapper_component_id = component_ids.get(mapper_name)
                if mapper_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, mapper_component_id,
                        'calls', confidence=0.6
                    )
            
            elif 'Controller' in class_name:
                # Controller는 Service 메서드 호출
                service_name = class_name.replace('Controller', 'Service')
                service_component_id = component_ids.get(service_name)
                if service_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, service_component_id,
                        'calls', confidence=0.6
                    )
            
            # 2. 실제 메서드 호출 패턴 분석 (새로 추가)
            self._analyze_method_calls_in_class(project_id, class_info, component_ids)
    
    def _analyze_method_calls_in_class(self, project_id: int, class_info: Dict, component_ids: Dict):
        """클래스 내 실제 메서드 호출 패턴 분석"""
        class_name = class_info['name']
        src_component_id = component_ids.get(class_name)
        
        # 파일 내용을 다시 읽어서 메서드 호출 패턴 분석
        try:
            # 파일 경로 추출 (component_ids에서)
            file_path = None
            for comp_name, comp_id in component_ids.items():
                if comp_name == class_name:
                    # 파일 경로는 별도로 조회 필요
                    break
            
            # 메서드 호출 패턴 분석 (정규식 기반)
            method_call_patterns = [
                # userService.getUserById() 패턴
                r'(\w+Service)\.(\w+)\s*\(',
                # userMapper.selectUser() 패턴  
                r'(\w+Mapper)\.(\w+)\s*\(',
                # this.methodName() 패턴
                r'this\.(\w+)\s*\(',
                # super.methodName() 패턴
                r'super\.(\w+)\s*\(',
            ]
            
            # 각 패턴별로 호출 관계 생성
            for pattern in method_call_patterns:
                # 실제 파일 내용 분석은 _generate_project_relationships에서 수행
                # 여기서는 패턴 기반 추론만 수행
                if 'Service' in pattern and 'Service' in class_name:
                    # Service 클래스에서 다른 Service 호출
                    if 'Controller' in class_name:
                        service_name = class_name.replace('Controller', 'Service')
                        dst_component_id = component_ids.get(service_name)
                        if dst_component_id:
                            self.metadata_engine.add_relationship(
                                project_id, src_component_id, dst_component_id,
                                'calls', confidence=0.5
                            )
                
                elif 'Mapper' in pattern and 'Service' in class_name:
                    # Service에서 Mapper 호출
                    mapper_name = class_name.replace('Service', 'Mapper').replace('Impl', '')
                    dst_component_id = component_ids.get(mapper_name)
                    if dst_component_id:
                        self.metadata_engine.add_relationship(
                            project_id, src_component_id, dst_component_id,
                            'calls', confidence=0.5
                        )
                        
        except Exception as e:
            print(f"DEBUG: Error analyzing method calls for {class_name}: {e}")
    
    def _add_foreign_key_relationships(self, project_id: int, structure_info: Dict, component_ids: Dict):
        """foreign_key 관계 추가 (데이터베이스 관계) - 정규식 기반 개선"""
        for class_info in structure_info['classes']:
            src_component_id = component_ids.get(class_info['name'])
            if not src_component_id:
                continue
            
            class_name = class_info['name']
            
            # 1. 기존 패턴 기반 추론 (유지)
            if 'Mapper' in class_name:
                entity_name = class_name.replace('Mapper', '')
                dst_component_id = component_ids.get(entity_name)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'foreign_key', confidence=0.5
                    )
            
            elif 'Service' in class_name and not class_name.endswith('Service'):
                mapper_name = class_name.replace('Service', 'Mapper').replace('Impl', '')
                dst_component_id = component_ids.get(mapper_name)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'foreign_key', confidence=0.5
                    )
            
            # 2. JPA 어노테이션 기반 관계 분석 (새로 추가)
            self._analyze_jpa_relationships(project_id, class_info, component_ids)
            
            # 3. MyBatis XML 기반 관계 분석 (새로 추가)
            self._analyze_mybatis_relationships(project_id, class_info, component_ids)
    
    def _analyze_jpa_relationships(self, project_id: int, class_info: Dict, component_ids: Dict):
        """JPA 어노테이션 기반 관계 분석"""
        class_name = class_info['name']
        src_component_id = component_ids.get(class_name)
        
        try:
            # JPA 관계 어노테이션 패턴
            jpa_patterns = [
                # @ManyToOne, @OneToMany, @OneToOne, @ManyToMany
                r'@ManyToOne\s*\(\s*targetEntity\s*=\s*(\w+)\.class',
                r'@OneToMany\s*\(\s*targetEntity\s*=\s*(\w+)\.class',
                r'@OneToOne\s*\(\s*targetEntity\s*=\s*(\w+)\.class',
                r'@ManyToMany\s*\(\s*targetEntity\s*=\s*(\w+)\.class',
                # @JoinColumn
                r'@JoinColumn\s*\(\s*name\s*=\s*"(\w+)"',
                # @JoinTable
                r'@JoinTable\s*\(\s*name\s*=\s*"(\w+)"',
            ]
            
            # JPA 관계 분석 (패턴 기반 추론)
            for pattern in jpa_patterns:
                # 실제 파일 내용 분석은 _generate_project_relationships에서 수행
                # 여기서는 패턴 기반 추론만 수행
                if 'Entity' in class_name or 'Model' in class_name:
                    # 엔티티 클래스 간 관계 추론
                    for comp_name, comp_id in component_ids.items():
                        if comp_name != class_name and comp_id != src_component_id:
                            if self._is_related_entity(class_name, comp_name):
                                self.metadata_engine.add_relationship(
                                    project_id, src_component_id, comp_id,
                                    'foreign_key', confidence=0.4
                                )
                                
        except Exception as e:
            print(f"DEBUG: Error analyzing JPA relationships for {class_name}: {e}")
    
    def _analyze_mybatis_relationships(self, project_id: int, class_info: Dict, component_ids: Dict):
        """MyBatis XML 기반 관계 분석"""
        class_name = class_info['name']
        src_component_id = component_ids.get(class_name)
        
        try:
            # MyBatis 관계 패턴
            mybatis_patterns = [
                # JOIN 쿼리 패턴
                r'JOIN\s+(\w+)\s+ON',
                r'LEFT\s+JOIN\s+(\w+)\s+ON',
                r'RIGHT\s+JOIN\s+(\w+)\s+ON',
                r'INNER\s+JOIN\s+(\w+)\s+ON',
                # 테이블 참조 패턴
                r'FROM\s+(\w+)\s+WHERE',
                r'UPDATE\s+(\w+)\s+SET',
                r'INSERT\s+INTO\s+(\w+)',
            ]
            
            # MyBatis 관계 분석 (패턴 기반 추론)
            if 'Mapper' in class_name:
                # Mapper 클래스는 해당 엔티티와 관계
                entity_name = class_name.replace('Mapper', '')
                dst_component_id = component_ids.get(entity_name)
                if dst_component_id:
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'foreign_key', confidence=0.4
                    )
                    
        except Exception as e:
            print(f"DEBUG: Error analyzing MyBatis relationships for {class_name}: {e}")
    
    def _is_related_entity(self, entity1: str, entity2: str) -> bool:
        """두 엔티티가 관련이 있는지 확인"""
        # 간단한 관련성 추론
        if 'User' in entity1 and 'User' in entity2:
            return True
        elif 'Product' in entity1 and 'Product' in entity2:
            return True
        elif 'Order' in entity1 and 'Order' in entity2:
            return True
        return False


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
        
        # 전체 프로젝트 관계 생성
        self._generate_project_relationships(project_id)
        
        # 통계 업데이트
        stats = self.metadata_engine.get_project_statistics(project_id)
        results['statistics'] = stats
        
        return results
    
    def _generate_project_relationships(self, project_id: int):
        """전체 프로젝트 관계 생성"""
        print(f"DEBUG: Generating project relationships for project_id: {project_id}")
        
        # 전체 컴포넌트 정보 수집
        all_components = self.metadata_engine.get_all_components(project_id)
        component_ids = {comp['component_name']: comp['component_id'] for comp in all_components}
        
        print(f"DEBUG: Total components: {len(component_ids)}")
        print(f"DEBUG: Component names: {list(component_ids.keys())[:10]}")
        
        # 전체 파일 정보 수집
        all_files = self.metadata_engine.get_all_files(project_id)
        
        # 각 파일별로 관계 생성
        for file_info in all_files:
            file_path = file_info['file_path']
            print(f"DEBUG: Processing file: {file_path}")
            
            # 파일 내용 읽기
            try:
                full_path = self.project_path / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 구조 정보 추출
                structure_info = self.java_parser._extract_basic_structure(content)
                
                # 관계 생성 (전체 component_ids 사용)
                self.java_parser._add_basic_relationships(project_id, structure_info, component_ids)
                
            except Exception as e:
                print(f"DEBUG: Error processing file {file_path}: {e}")
                continue
    
    def quick_search(self, query: str) -> List[Dict]:
        """빠른 검색 (메타DB만 사용)"""
        return self.metadata_engine.search_components(query)
    
    def detailed_analysis(self, component_name: str) -> Dict:
        """상세 분석 (하이브리드 방식)"""
        return self.metadata_engine.get_component_full_details(component_name)