"""
Java source code parser using javalang library
Extracts classes, methods, annotations, and basic structural information
"""

import os
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import javalang
from dataclasses import dataclass
from datetime import datetime

from ..models.database import File, JavaClass, JavaMethod


@dataclass
class JavaParsingResult:
    """Java 파싱 결과"""
    file_info: Dict
    classes: List[Dict]
    methods: List[Dict]
    dependencies: List[Dict]
    confidence: float


class JavaSourceParser:
    """Java 소스코드 파서"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_file_size_mb = self.config.get('max_file_size_mb', 10)
    
    def can_parse(self, file_path: str) -> bool:
        """파일 파싱 가능 여부 확인"""
        if not file_path.endswith('.java'):
            return False
        
        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size_mb * 1024 * 1024:
                return False
            return True
        except:
            return False
    
    def calculate_file_hash(self, content: str) -> str:
        """파일 내용의 SHA-256 해시 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def count_lines(self, content: str) -> int:
        """코드 라인 수 계산"""
        return len([line for line in content.splitlines() if line.strip()])
    
    def extract_annotations(self, node) -> List[str]:
        """어노테이션 추출"""
        annotations = []
        if hasattr(node, 'annotations') and node.annotations:
            for annotation in node.annotations:
                if hasattr(annotation, 'name'):
                    annotations.append(annotation.name)
        return annotations
    
    def extract_modifiers(self, node) -> List[str]:
        """접근제어자 및 기타 modifier 추출"""
        modifiers = []
        if hasattr(node, 'modifiers') and node.modifiers:
            modifiers.extend(node.modifiers)
        return modifiers
    
    def get_method_signature(self, method_node) -> str:
        """메소드 시그니처 생성"""
        try:
            name = method_node.name
            params = []
            if hasattr(method_node, 'parameters') and method_node.parameters:
                for param in method_node.parameters:
                    if hasattr(param, 'type') and hasattr(param.type, 'name'):
                        params.append(param.type.name)
            
            return f"{name}({', '.join(params)})"
        except:
            return method_node.name if hasattr(method_node, 'name') else "unknown"
    
    def get_return_type(self, method_node) -> Optional[str]:
        """리턴 타입 추출"""
        try:
            if hasattr(method_node, 'return_type') and method_node.return_type:
                if hasattr(method_node.return_type, 'name'):
                    return method_node.return_type.name
            return None
        except:
            return None
    
    def parse_file(self, file_path: str, project_id: int) -> JavaParsingResult:
        """Java 파일 파싱"""
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 기본 파일 정보
            file_stat = os.stat(file_path)
            file_info = {
                'project_id': project_id,
                'path': os.path.relpath(file_path),
                'language': 'java',
                'hash': self.calculate_file_hash(content),
                'loc': self.count_lines(content),
                'mtime': datetime.fromtimestamp(file_stat.st_mtime)
            }
            
            # Java 파싱
            try:
                tree = javalang.parse.parse(content)
                confidence = 0.9  # 파싱 성공 시 높은 신뢰도
            except javalang.parser.JavaSyntaxError as e:
                # 파싱 실패 시 부분 정보만 추출
                return JavaParsingResult(
                    file_info=file_info,
                    classes=[],
                    methods=[],
                    dependencies=[],
                    confidence=0.1
                )
            
            classes = []
            methods = []
            dependencies = []
            
            # 클래스 정보 추출
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = {
                    'name': node.name,
                    'fqn': self._get_fully_qualified_name(tree, node),
                    'start_line': getattr(node, 'position', {}).get('line', 0) or 0,
                    'end_line': 0,  # javalang doesn't provide end position
                    'modifiers': ','.join(self.extract_modifiers(node)),
                    'annotations': ','.join(self.extract_annotations(node))
                }
                classes.append(class_info)
                
                # 클래스 내 메소드 추출
                for method_path, method_node in node.filter(javalang.tree.MethodDeclaration):
                    method_info = {
                        'class_name': node.name,
                        'name': method_node.name,
                        'signature': self.get_method_signature(method_node),
                        'return_type': self.get_return_type(method_node),
                        'start_line': getattr(method_node, 'position', {}).get('line', 0) or 0,
                        'end_line': 0,  # javalang doesn't provide end position
                        'annotations': ','.join(self.extract_annotations(method_node))
                    }
                    methods.append(method_info)
            
            # Import 정보를 의존성으로 추가
            for path, node in tree.filter(javalang.tree.Import):
                dep_info = {
                    'type': 'import',
                    'target': node.path,
                    'static': getattr(node, 'static', False),
                    'wildcard': getattr(node, 'wildcard', False)
                }
                dependencies.append(dep_info)
            
            return JavaParsingResult(
                file_info=file_info,
                classes=classes,
                methods=methods,
                dependencies=dependencies,
                confidence=confidence
            )
            
        except Exception as e:
            # 파싱 실패
            file_info['hash'] = 'error'
            file_info['loc'] = 0
            
            return JavaParsingResult(
                file_info=file_info,
                classes=[],
                methods=[],
                dependencies=[],
                confidence=0.0
            )
    
    def _get_fully_qualified_name(self, tree, class_node) -> str:
        """클래스의 Fully Qualified Name 생성"""
        try:
            package_name = ""
            for path, node in tree.filter(javalang.tree.PackageDeclaration):
                package_name = node.name
                break
            
            if package_name:
                return f"{package_name}.{class_node.name}"
            return class_node.name
        except:
            return class_node.name
    
    def parse_directory(self, directory_path: str, project_id: int) -> List[JavaParsingResult]:
        """디렉토리 내 모든 Java 파일 파싱"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    if self.can_parse(file_path):
                        try:
                            result = self.parse_file(file_path, project_id)
                            results.append(result)
                        except Exception as e:
                            print(f"Error parsing {file_path}: {e}")
        
        return results
    
    def extract_spring_annotations(self, annotations: List[str]) -> Dict[str, any]:
        """Spring 관련 어노테이션 추출 및 분석"""
        spring_info = {
            'is_controller': False,
            'is_service': False,
            'is_repository': False,
            'is_component': False,
            'endpoints': [],
            'mappings': []
        }
        
        spring_annotations = [
            'RestController', 'Controller', 'Service', 'Repository', 
            'Component', 'GetMapping', 'PostMapping', 'PutMapping', 
            'DeleteMapping', 'RequestMapping'
        ]
        
        for annotation in annotations:
            if annotation in ['RestController', 'Controller']:
                spring_info['is_controller'] = True
            elif annotation == 'Service':
                spring_info['is_service'] = True
            elif annotation == 'Repository':
                spring_info['is_repository'] = True
            elif annotation == 'Component':
                spring_info['is_component'] = True
            elif annotation.endswith('Mapping'):
                spring_info['mappings'].append(annotation)
        
        return spring_info


# Placeholder for future Java AST analysis extensions
class AdvancedJavaAnalyzer:
    """향후 확장을 위한 고급 Java 분석기 placeholder"""
    
    def __init__(self):
        pass
    
    def analyze_method_calls(self, tree) -> List[Dict]:
        """메소드 호출 분석 (향후 구현)"""
        # TODO: Implement method call extraction
        return []
    
    def analyze_data_flow(self, tree) -> List[Dict]:
        """데이터 플로우 분석 (향후 구현)"""
        # TODO: Implement data flow analysis
        return []
    
    def analyze_spring_dependencies(self, tree) -> List[Dict]:
        """Spring DI 의존성 분석 (향후 구현)"""
        # TODO: Implement Spring dependency injection analysis
        return []


if __name__ == "__main__":
    # 테스트 코드
    parser = JavaSourceParser()
    
    # 샘플 프로젝트 파싱 테스트
    sample_project_path = "./PROJECT/sample-app/src"
    if os.path.exists(sample_project_path):
        results = parser.parse_directory(sample_project_path, project_id=1)
        print(f"Parsed {len(results)} Java files")
        
        for result in results[:3]:  # 처음 3개 파일만 출력
            print(f"\nFile: {result.file_info['path']}")
            print(f"Classes: {len(result.classes)}")
            print(f"Methods: {len(result.methods)}")
            print(f"Confidence: {result.confidence}")
    else:
        print("Sample project not found")