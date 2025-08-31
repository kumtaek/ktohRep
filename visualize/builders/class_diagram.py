"""
Source Analyzer Class Diagram Builder

클래스 다이어그램 생성을 위한 빌더 모듈
- Python 파일에서 클래스 정의를 추출
- 클래스 간 관계(상속, 연관) 분석  
- 메서드, 속성 정보 수집
"""

import logging
import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from ..data_access import VizDB

# Import database models
import sys
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
from phase1.models.database import File

logger = logging.getLogger(__name__)


class ClassAnalyzer(ast.NodeVisitor):
    """Python AST를 순회하며 클래스 정보를 추출하는 분석기"""
    
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.classes: Dict[str, Dict] = {}
        self.imports: Dict[str, str] = {}  # alias -> full_name
        self.current_class = None
        
    def visit_Import(self, node):
        """import 문 처리"""
        for alias in node.names:
            name = alias.name
            asname = alias.asname or alias.name
            self.imports[asname] = name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """from ... import 문 처리"""
        module = node.module or ''
        for alias in node.names:
            name = alias.name
            asname = alias.asname or alias.name
            full_name = f"{module}.{name}" if module else name
            self.imports[asname] = full_name
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """클래스 정의 처리"""
        class_name = node.name
        self.current_class = class_name
        
        # 기본 클래스 정보
        class_info = {
            'name': class_name,
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node),
            'bases': [],  # 상속받는 클래스들
            'methods': [],
            'attributes': [],
            'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
            'is_abstract': any(
                isinstance(d, ast.Name) and d.id == 'abstractmethod' 
                for d in node.decorator_list
            )
        }
        
        # 상속 관계 분석
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name:
                class_info['bases'].append(base_name)
        
        self.classes[class_name] = class_info
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        """메서드 정의 처리"""
        if self.current_class:
            method_info = {
                'name': node.name,
                'lineno': node.lineno,
                'docstring': ast.get_docstring(node),
                'args': [arg.arg for arg in node.args.args],
                'decorators': [self._get_name_from_node(d) for d in node.decorator_list],
                'is_property': any(
                    self._get_name_from_node(d) == 'property' 
                    for d in node.decorator_list
                ),
                'is_static': any(
                    self._get_name_from_node(d) == 'staticmethod' 
                    for d in node.decorator_list
                ),
                'is_class': any(
                    self._get_name_from_node(d) == 'classmethod' 
                    for d in node.decorator_list
                ),
                'is_private': node.name.startswith('_'),
                'is_special': node.name.startswith('__') and node.name.endswith('__')
            }
            self.classes[self.current_class]['methods'].append(method_info)
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """속성 할당 처리 (클래스 변수와 인스턴스 변수)"""
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attr_info = {
                        'name': target.id,
                        'lineno': node.lineno,
                        'type': 'class_variable',
                        'is_private': target.id.startswith('_')
                    }
                    self.classes[self.current_class]['attributes'].append(attr_info)
                elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                    attr_info = {
                        'name': target.attr,
                        'lineno': node.lineno,
                        'type': 'instance_variable',
                        'is_private': target.attr.startswith('_')
                    }
                    self.classes[self.current_class]['attributes'].append(attr_info)
        
        self.generic_visit(node)
    
    def _get_name_from_node(self, node) -> Optional[str]:
        """AST 노드에서 이름을 추출"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name_from_node(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return None


def analyze_python_file(file_path: str) -> Dict[str, Any]:
    """Python 파일을 분석하여 클래스 정보 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = ClassAnalyzer(file_path)
        analyzer.visit(tree)
        
        return {
            'file_path': file_path,
            'classes': analyzer.classes,
            'imports': analyzer.imports
        }
    except Exception as e:
        logger.warning(f"Failed to analyze {file_path}: {e}")
        return {'file_path': file_path, 'classes': {}, 'imports': {}}


def find_python_files(config: Dict[str, Any], project_id: int, project_name: Optional[str] = None, modules_filter: Optional[str] = None) -> List[str]:
    """프로젝트에서 Python 파일들을 찾아 반환"""
    try:
        db = VizDB(config, project_name)
        session = db.session()
        
        # Get project source files
        query = session.query(File.path).filter(File.project_id == project_id, File.path.like('%.py')).order_by(File.path)
        files = [row.path for row in query.all()]
        
        # Filter by modules if specified
        if modules_filter:
            module_patterns = [m.strip() for m in modules_filter.split(',')]
            filtered_files = []
            for file_path in files:
                for pattern in module_patterns:
                    if pattern in file_path or file_path.endswith(f"/{pattern}.py"):
                        filtered_files.append(file_path)
                        break
            files = filtered_files
        
        return files
        
    except Exception as e:
        logger.error(f"Error finding Python files: {e}")
        return []


def build_relationships(file_analyses: List[Dict]) -> List[Dict]:
    """클래스 간 관계를 분석하여 엣지 생성"""
    relationships = []
    all_classes = {}
    
    # 모든 클래스 수집
    for analysis in file_analyses:
        file_path = analysis['file_path']
        for class_name, class_info in analysis['classes'].items():
            full_name = f"{file_path}::{class_name}"
            all_classes[full_name] = class_info
            all_classes[class_name] = class_info  # 단순 이름도 등록
    
    relationship_id = 1
    
    # 상속 관계 분석
    for analysis in file_analyses:
        file_path = analysis['file_path']
        for class_name, class_info in analysis['classes'].items():
            source_id = f"{file_path}::{class_name}"
            
            for base_class in class_info['bases']:
                # 베이스 클래스 찾기
                target_id = None
                if base_class in all_classes:
                    # 같은 파일이나 import된 클래스
                    for analysis2 in file_analyses:
                        for cls_name, cls_info in analysis2['classes'].items():
                            if cls_name == base_class:
                                target_id = f"{analysis2['file_path']}::{cls_name}"
                                break
                        if target_id:
                            break
                
                if target_id and target_id != source_id:
                    relationships.append({
                        'id': f'rel_{relationship_id}',
                        'source': source_id,
                        'target': target_id,
                        'kind': 'inherits',
                        'confidence': 1.0,
                        'meta': {
                            'relationship_type': 'inheritance',
                            'base_class': base_class
                        }
                    })
                    relationship_id += 1
    
    return relationships


def build_class_diagram_json(
    config: Dict[str, Any],
    project_id: int, 
    project_name: Optional[str] = None,
    modules_filter: Optional[str] = None,
    include_private: bool = False,
    max_methods: int = 10,
    max_nodes: int = 1000
) -> Dict[str, Any]:
    """클래스 다이어그램을 위한 JSON 데이터 구조 생성"""
    
    logger.info(f"클래스 다이어그램 데이터 수집 시작: 프로젝트 {project_id}")
    
    # Python 파일 찾기
    python_files = find_python_files(config, project_id, project_name, modules_filter)
    logger.info(f"Python 파일 {len(python_files)}개 발견")
    
    if not python_files:
        logger.warning("분석할 Python 파일을 찾을 수 없습니다")
        return {'nodes': [], 'edges': [], 'stats': {'total_files': 0, 'total_classes': 0}}
    
    # 각 파일 분석
    file_analyses = []
    for file_path in python_files[:50]:  # 너무 많은 파일은 제한
        analysis = analyze_python_file(file_path)
        if analysis['classes']:  # 클래스가 있는 파일만 포함
            file_analyses.append(analysis)
    
    logger.info(f"클래스가 포함된 파일 {len(file_analyses)}개 분석 완료")
    
    # 노드 생성 (클래스들)
    nodes = []
    node_count = 0
    
    for analysis in file_analyses:
        if node_count >= max_nodes:
            break
            
        file_path = analysis['file_path']
        module_name = Path(file_path).stem
        
        for class_name, class_info in analysis['classes'].items():
            if node_count >= max_nodes:
                break
            
            # private 멤버 필터링
            methods = class_info['methods']
            if not include_private:
                methods = [m for m in methods if not m['is_private'] or m['is_special']]
            
            # 메서드 수 제한
            methods = methods[:max_methods]
            
            attributes = class_info['attributes']
            if not include_private:
                attributes = [a for a in attributes if not a['is_private']]
            
            node = {
                'id': f"{file_path}::{class_name}",
                'label': class_name,
                'type': 'class',
                'group': 'Class',
                'meta': {
                    'file_path': file_path,
                    'module_name': module_name,
                    'docstring': class_info['docstring'],
                    'line_number': class_info['lineno'],
                    'methods': methods,
                    'attributes': attributes,
                    'base_classes': class_info['bases'],
                    'decorators': class_info['decorators'],
                    'is_abstract': class_info['is_abstract'],
                    'total_methods': len(class_info['methods']),
                    'total_attributes': len(class_info['attributes'])
                }
            }
            nodes.append(node)
            node_count += 1
    
    # 관계 생성
    edges = build_relationships(file_analyses)
    
    # 통계
    total_classes = sum(len(analysis['classes']) for analysis in file_analyses)
    stats = {
        'total_files': len(file_analyses),
        'total_classes': total_classes,
        'displayed_nodes': len(nodes),
        'relationships': len(edges)
    }
    
    logger.info(f"클래스 다이어그램 생성 완료: {len(nodes)}개 노드, {len(edges)}개 관계")
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': stats,
        'metadata': {
            'diagram_type': 'class',
            'project_id': project_id,
            'modules_filter': modules_filter,
            'include_private': include_private,
            'max_methods': max_methods
        }
    }