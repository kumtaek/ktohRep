"""
향상된 관계 추출기
Java 소스코드에서 다양한 관계(calls, implements, extends, dependency 등)를 추출
"""
import re
import os
from typing import Dict, List, Set, Tuple
from pathlib import Path

class EnhancedRelationshipExtractor:
    """Java 코드에서 다양한 관계 추출"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        
    def extract_relationships_from_java(self, project_id: int, java_files: List[str]) -> Dict:
        """Java 파일들에서 관계 추출"""
        try:
            total_relationships = {
                'calls': [],
                'extends': [],
                'implements': [], 
                'dependency': [],
                'imports': []
            }
            
            for java_file in java_files:
                if not os.path.exists(java_file):
                    continue
                    
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 파일에서 관계 추출
                file_relationships = self._extract_from_content(content, java_file)
                
                # 결과 병합
                for rel_type, rels in file_relationships.items():
                    total_relationships[rel_type].extend(rels)
            
            # 메타DB에 저장
            self._save_relationships_to_db(project_id, total_relationships)
            
            return {
                'success': True,
                'relationships': total_relationships,
                'summary': {rel_type: len(rels) for rel_type, rels in total_relationships.items()}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_from_content(self, content: str, file_path: str) -> Dict:
        """Java 파일 내용에서 관계 추출"""
        relationships = {
            'calls': [],
            'extends': [],
            'implements': [],
            'dependency': [],
            'imports': []
        }
        
        # 라인별로 처리
        lines = content.split('\n')
        current_class = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 클래스 선언 찾기
            class_match = re.search(r'class\s+(\w+)', line)
            if class_match:
                current_class = class_match.group(1)
            
            # Import 관계
            import_match = re.search(r'import\s+([a-zA-Z0-9_.]+);', line)
            if import_match:
                import_target = import_match.group(1).split('.')[-1]  # 클래스명만 추출
                relationships['imports'].append({
                    'source': current_class or Path(file_path).stem,
                    'target': import_target,
                    'line': i + 1,
                    'file': file_path
                })
            
            # Extends 관계
            extends_match = re.search(r'class\s+(\w+)\s+extends\s+(\w+)', line)
            if extends_match:
                relationships['extends'].append({
                    'source': extends_match.group(1),
                    'target': extends_match.group(2),
                    'line': i + 1,
                    'file': file_path
                })
            
            # Implements 관계
            implements_match = re.search(r'class\s+(\w+).*implements\s+([^{]+)', line)
            if implements_match:
                source_class = implements_match.group(1)
                interfaces = [intf.strip() for intf in implements_match.group(2).split(',')]
                for interface in interfaces:
                    relationships['implements'].append({
                        'source': source_class,
                        'target': interface,
                        'line': i + 1,
                        'file': file_path
                    })
            
            # 메서드 호출 관계
            if current_class:
                method_calls = self._extract_method_calls(line)
                for call in method_calls:
                    relationships['calls'].append({
                        'source': current_class,
                        'target': call,
                        'line': i + 1,
                        'file': file_path
                    })
            
            # 의존성 관계 (변수 선언, 생성자 등)
            dependency_matches = self._extract_dependencies(line)
            for dep in dependency_matches:
                if current_class and dep != current_class:
                    relationships['dependency'].append({
                        'source': current_class,
                        'target': dep,
                        'line': i + 1,
                        'file': file_path
                    })
        
        return relationships
    
    def _extract_method_calls(self, line: str) -> List[str]:
        """라인에서 메서드 호출 추출"""
        calls = []
        
        # 기본적인 메서드 호출 패턴
        patterns = [
            r'(\w+)\.(\w+)\s*\(',  # object.method()
            r'new\s+(\w+)\s*\(',   # new ClassName()  
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                if pattern.startswith(r'(\w+)\.'):
                    # 객체.메서드 형태
                    obj_or_class = match.group(1)
                    method = match.group(2)
                    
                    # 대문자로 시작하면 클래스, 소문자면 객체로 판단
                    if obj_or_class[0].isupper():
                        calls.append(obj_or_class)  # 클래스 호출
                else:
                    # new 생성자 호출
                    calls.append(match.group(1))
        
        return calls
    
    def _extract_dependencies(self, line: str) -> List[str]:
        """라인에서 의존성 관계 추출"""
        dependencies = []
        
        # 변수 선언 패턴
        patterns = [
            r'private\s+(\w+)\s+\w+',     # private Type field
            r'public\s+(\w+)\s+\w+',      # public Type field  
            r'protected\s+(\w+)\s+\w+',   # protected Type field
            r'(\w+)\s+\w+\s*=\s*new',     # Type obj = new
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                type_name = match.group(1)
                
                # Java 기본 타입은 제외
                if type_name not in ['int', 'String', 'boolean', 'long', 'double', 'float', 'char', 'void']:
                    dependencies.append(type_name)
        
        return dependencies
    
    def _save_relationships_to_db(self, project_id: int, relationships: Dict):
        """관계 정보를 메타DB에 저장"""
        for rel_type, rels in relationships.items():
            for rel in rels:
                source = rel['source']
                target = rel['target']
                
                if not source or not target:
                    continue
                
                # 소스와 타겟 컴포넌트 생성 또는 조회
                source_id = self._get_or_create_component(project_id, source, 'class')
                target_id = self._get_or_create_component(project_id, target, 'class')
                
                if source_id and target_id:
                    try:
                        self.metadata_engine.add_relationship(
                            project_id=project_id,
                            src_component_id=source_id,
                            dst_component_id=target_id,
                            relationship_type=rel_type,
                            confidence=0.8
                        )
                    except Exception as e:
                        # 중복 관계는 무시
                        pass
    
    def _get_or_create_component(self, project_id: int, component_name: str, component_type: str) -> int:
        """컴포넌트를 조회하거나 생성"""
        try:
            return self.metadata_engine.add_component(
                project_id=project_id,
                file_id=None,  # 더미 파일 ID 0 사용
                component_name=component_name,
                component_type=component_type,
                line_start=None,
                line_end=None
            )
        except Exception:
            return None
    
    def add_business_tags_from_analysis(self, project_id: int):
        """컴포넌트 이름 분석을 통한 비즈니스 태그 자동 추가"""
        try:
            import sqlite3
            
            with sqlite3.connect(self.metadata_engine.db_path) as conn:
                cursor = conn.cursor()
                
                # 모든 컴포넌트 조회
                cursor.execute("""
                    SELECT component_id, component_name, component_type
                    FROM components
                    WHERE project_id = ?
                """, (project_id,))
                
                components = cursor.fetchall()
                
                for comp_id, comp_name, comp_type in components:
                    # 이름 패턴으로 계층 분류
                    layer = self._classify_layer(comp_name)
                    domain = self._classify_domain(comp_name)
                    
                    if layer or domain:
                        try:
                            self.metadata_engine.add_business_tag(
                                project_id=project_id,
                                component_id=comp_id,
                                domain=domain,
                                layer=layer,
                                priority=3
                            )
                        except Exception:
                            # 중복 태그는 무시
                            pass
                            
        except Exception as e:
            print(f"비즈니스 태그 추가 실패: {e}")
    
    def _classify_layer(self, component_name: str) -> str:
        """컴포넌트 이름으로 계층 분류"""
        name_lower = component_name.lower()
        
        if any(keyword in name_lower for keyword in ['controller', 'rest', 'web', 'api']):
            return 'controller'
        elif any(keyword in name_lower for keyword in ['service', 'business', 'logic']):
            return 'service'  
        elif any(keyword in name_lower for keyword in ['dao', 'repository', 'data']):
            return 'dao'
        elif any(keyword in name_lower for keyword in ['model', 'entity', 'dto', 'vo']):
            return 'model'
        elif any(keyword in name_lower for keyword in ['util', 'helper', 'common']):
            return 'util'
        elif any(keyword in name_lower for keyword in ['config', 'configuration']):
            return 'config'
        else:
            return None
            
    def _classify_domain(self, component_name: str) -> str:
        """컴포넌트 이름으로 도메인 분류"""
        name_lower = component_name.lower()
        
        if any(keyword in name_lower for keyword in ['user', 'member', 'account']):
            return 'user'
        elif any(keyword in name_lower for keyword in ['order', 'purchase', 'cart']):
            return 'order'
        elif any(keyword in name_lower for keyword in ['product', 'item', 'goods']):
            return 'product'
        elif any(keyword in name_lower for keyword in ['payment', 'billing']):
            return 'payment'
        else:
            return None