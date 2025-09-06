"""
JavaParser 라이브러리를 사용한 향상된 Java 파서
JavaParser 라이브러리를 사용하여 더 정확한 AST 파싱을 수행합니다.
"""

import re
import os
import sys
import json
from typing import Dict, List, Any, Set, Tuple, Optional
from pathlib import Path

# JavaParser 라이브러리 임포트 (설치 필요)
try:
    from javalang import parse, tree
    from javalang.parser import JavaSyntaxError
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False
    print("Warning: javalang library not available. Install with: pip install javalang")

from phase1.parsers.base_parser import BaseParser
from phase1.models.database import Class, Method, Edge, File

class JavaParserEnhanced(BaseParser):
    """JavaParser 라이브러리를 사용한 향상된 Java 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.javalang_available = JAVALANG_AVAILABLE
        
        if not self.javalang_available:
            print("Warning: javalang not available, falling back to regex parsing")
    
    def _get_parser_type(self) -> str:
        return 'java_enhanced'
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'java'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출 (Java 파서는 SQL을 처리하지 않음)"""
        return {'sql_units': [], 'tables': [], 'columns': []}
    
    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[Class], List[Method], List[Edge]]:
        """
        Java 파일을 파싱하여 메타데이터를 추출합니다.
        
        Args:
            file_path: Java 파일 경로
            project_id: 프로젝트 ID
            
        Returns:
            (File, List[Class], List[Method], List[Edge]) 튜플
        """
        try:
            # 파일 내용 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # File 객체 생성
            file_obj = self._create_file_object(file_path, project_id, content)
            
            if self.javalang_available:
                # JavaParser 라이브러리 사용
                classes, methods, edges = self._parse_with_javalang(content, file_path, project_id)
            else:
                # 정규식 기반 파싱 (fallback)
                classes, methods, edges = self._parse_with_regex(content, file_path, project_id)
            
            return file_obj, classes, methods, edges
            
        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")
            # 빈 결과 반환
            file_obj = self._create_file_object(file_path, project_id, "")
            return file_obj, [], [], []
    
    def _create_file_object(self, file_path: str, project_id: int, content: str) -> File:
        """File 객체를 생성합니다."""
        file_path_obj = Path(file_path)
        
        # 파일 해시 계산
        import hashlib
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 라인 수 계산
        line_count = len(content.splitlines()) if content else 0
        
        # 수정 시간
        import datetime
        mtime = datetime.datetime.fromtimestamp(file_path_obj.stat().st_mtime)
        
        return File(
            path=file_path,
            project_id=project_id,
            language='java',
            hash=file_hash,
            loc=line_count,
            mtime=mtime
        )
    
    def _parse_with_javalang(self, content: str, file_path: str, project_id: int) -> Tuple[List[Class], List[Method], List[Edge]]:
        """JavaParser 라이브러리를 사용하여 파싱합니다."""
        classes = []
        methods = []
        edges = []
        try:
            tree = parse.parse(content)
            package_name = tree.package.name if tree.package else ""

            for type_decl in tree.types:
                if type(type_decl).__name__ == 'ClassDeclaration':
                    class_obj = self._extract_class_from_javalang(type_decl, file_path, project_id, package_name)
                    if class_obj:
                        classes.append(class_obj)
                        class_methods = self._extract_methods_from_class(type_decl, file_path, project_id, class_obj.fqn)
                        methods.extend(class_methods)

                elif type(type_decl).__name__ == 'InterfaceDeclaration':
                    interface_obj = self._extract_interface_from_javalang(type_decl, file_path, project_id, package_name)
                    if interface_obj:
                        classes.append(interface_obj) # Treat interfaces as classes for simplicity
                        interface_methods = self._extract_methods_from_interface(type_decl, file_path, project_id, interface_obj.fqn)
                        methods.extend(interface_methods)
            
            edges = self._extract_dependencies_from_javalang(tree, file_path, project_id, methods)

        except JavaSyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return self._parse_with_regex(content, file_path, project_id)
        except Exception as e:
            print(f"Error parsing with javalang {file_path}: {e}")
            return self._parse_with_regex(content, file_path, project_id)

        return classes, methods, edges
    
    def _extract_class_from_javalang(self, class_decl: tree.ClassDeclaration, file_path: str, project_id: int, package_name: str) -> Optional[Class]:
        """JavaParser AST에서 클래스 정보를 추출합니다."""
        try:
            # 클래스 이름
            class_name = class_decl.name
            
            # FQN 생성
            fqn = f"{package_name}.{class_name}" if package_name else class_name
            
            # 수퍼클래스
            extends = class_decl.extends.name if class_decl.extends else None
            
            # 구현 인터페이스
            implements = []
            if class_decl.implements:
                for impl in class_decl.implements:
                    implements.append(impl.name)
            
            # 어노테이션
            annotations = []
            if class_decl.annotations:
                for ann in class_decl.annotations:
                    annotations.append(ann.name)
            
            # 수정자
            modifiers = class_decl.modifiers or []
            
            # 클래스 타입 결정
            class_type = []
            if 'public' in modifiers:
                class_type.append('public')
            if 'abstract' in modifiers:
                class_type.append('abstract')
            if 'final' in modifiers:
                class_type.append('final')
            if 'static' in modifiers:
                class_type.append('static')
            
            return Class(
                file_id=None,  # 나중에 설정됨
                name=class_name,
                fqn=fqn,
                start_line=0,  # TODO: 정확한 라인 번호 계산
                end_line=0,    # TODO: 정확한 라인 번호 계산
                modifiers=json.dumps(list(modifiers)) if modifiers else None,
                annotations=json.dumps(annotations) if annotations else None
            )
            
        except Exception as e:
            print(f"Error extracting class from javalang: {e}")
            return None
    
    def _extract_interface_from_javalang(self, interface_decl: tree.InterfaceDeclaration, file_path: str, project_id: int, package_name: str) -> Optional[Class]:
        """JavaParser AST에서 인터페이스 정보를 추출합니다."""
        try:
            # 인터페이스 이름
            interface_name = interface_decl.name
            
            # FQN 생성
            fqn = f"{package_name}.{interface_name}" if package_name else interface_name
            
            # 확장 인터페이스
            extends = []
            if interface_decl.extends:
                for ext in interface_decl.extends:
                    extends.append(ext.name)
            
            # 어노테이션
            annotations = []
            if interface_decl.annotations:
                for ann in interface_decl.annotations:
                    annotations.append(ann.name)
            
            # 수정자
            modifiers = interface_decl.modifiers or []
            
            # 인터페이스 타입 결정
            interface_type = ['interface']
            if 'public' in modifiers:
                interface_type.append('public')
            
            return Class(
                file_id=None,  # 나중에 설정됨
                name=interface_name,
                fqn=fqn,
                start_line=0,  # TODO: 정확한 라인 번호 계산
                end_line=0,    # TODO: 정확한 라인 번호 계산
                modifiers=json.dumps(list(modifiers)) if modifiers else None,
                annotations=json.dumps(annotations) if annotations else None
            )
            
        except Exception as e:
            print(f"Error extracting interface from javalang: {e}")
            return None
    
    def _extract_methods_from_class(self, class_decl: tree.ClassDeclaration, file_path: str, project_id: int, class_fqn: str) -> List[Method]:
        """클래스에서 메서드들을 추출합니다."""
        methods = []
        
        # javalang에서는 메서드가 body 안에 있습니다
        if not class_decl.body:
            return methods
        
        for member in class_decl.body:
            try:
                # 멤버가 메서드인지 확인
                if isinstance(member, tree.MethodDeclaration):
                    method_obj = self._extract_method_from_javalang(member, file_path, project_id, class_fqn)
                    if method_obj:
                        methods.append(method_obj)
                # 생성자도 메서드로 처리
                elif isinstance(member, tree.ConstructorDeclaration):
                    method_obj = self._extract_constructor_from_javalang(member, file_path, project_id, class_fqn)
                    if method_obj:
                        methods.append(method_obj)
            except Exception as e:
                print(f"Error extracting method from class body: {e}")
                continue
        
        return methods
    
    def _extract_methods_from_interface(self, interface_decl: tree.InterfaceDeclaration, file_path: str, project_id: int, interface_fqn: str) -> List[Method]:
        """인터페이스에서 메서드들을 추출합니다."""
        methods = []
        
        # javalang에서는 인터페이스 메서드도 body 안에 있습니다
        if not interface_decl.body:
            return methods
        
        for member in interface_decl.body:
            try:
                # 맴버가 메서드인지 확인
                if isinstance(member, tree.MethodDeclaration):
                    method_obj = self._extract_method_from_javalang(member, file_path, project_id, interface_fqn)
                    if method_obj:
                        methods.append(method_obj)
            except Exception as e:
                print(f"Error extracting method from interface body: {e}")
                continue
        
        return methods
    
    def _extract_method_from_javalang(self, method_decl, file_path: str, project_id: int, owner_fqn: str) -> Optional[Method]:
        """JavaParser AST에서 메서드 정보를 추출합니다."""
        try:
            # 메서드 이름
            method_name = method_decl.name
            
            # 반환 타입
            return_type = method_decl.return_type.name if method_decl.return_type else 'void'
            
            # 매개변수
            parameters = []
            if method_decl.parameters:
                for param in method_decl.parameters:
                    param_type = param.type.name if param.type else 'Object'
                    param_name = param.name
                    parameters.append(f"{param_type} {param_name}")
            
            # 어노테이션
            annotations = []
            if method_decl.annotations:
                for ann in method_decl.annotations:
                    annotations.append(ann.name)
            
            # 수정자
            modifiers = method_decl.modifiers or []
            
            # 메서드 타입 결정
            method_type = []
            if 'public' in modifiers:
                method_type.append('public')
            elif 'private' in modifiers:
                method_type.append('private')
            elif 'protected' in modifiers:
                method_type.append('protected')
            
            if 'static' in modifiers:
                method_type.append('static')
            if 'final' in modifiers:
                method_type.append('final')
            if 'abstract' in modifiers:
                method_type.append('abstract')
            if 'synchronized' in modifiers:
                method_type.append('synchronized')
            
            # 시그너처 생성
            signature = f"{method_name}({','.join(parameters) if parameters else ''})"
            
            method_obj = Method(
                class_id=None,  # 나중에 설정됨
                name=method_name,
                signature=signature,
                return_type=return_type,
                start_line=0,  # TODO: 정확한 라인 번호 계산
                end_line=0,    # TODO: 정확한 라인 번호 계산
                annotations=json.dumps(annotations) if annotations else None,
                parameters=json.dumps(parameters) if parameters else None,
                modifiers=json.dumps(list(modifiers)) if modifiers else None
            )
            
            # MetadataEngine에서 필요한 속성 추가
            method_obj.owner_fqn = owner_fqn
            
            return method_obj
            
        except Exception as e:
            print(f"Error extracting method from javalang: {e}")
            return None
    
    def _extract_constructor_from_javalang(self, constructor_decl, file_path: str, project_id: int, owner_fqn: str) -> Optional[Method]:
        """JavaParser AST에서 생성자 정보를 추출합니다."""
        try:
            # 생성자 이름은 클래스 이름과 동일
            constructor_name = constructor_decl.name
            
            # 매개변수
            parameters = []
            if constructor_decl.parameters:
                for param in constructor_decl.parameters:
                    param_type = param.type.name if param.type else 'Object'
                    param_name = param.name
                    parameters.append(f"{param_type} {param_name}")
            
            # 어노테이션
            annotations = []
            if constructor_decl.annotations:
                for ann in constructor_decl.annotations:
                    annotations.append(ann.name)
            
            # 수정자
            modifiers = constructor_decl.modifiers or []
            
            # 시그너처 생성
            signature = f"{constructor_name}({','.join(parameters) if parameters else ''})"
            
            constructor_obj = Method(
                class_id=None,  # 나중에 설정됨
                name=constructor_name,
                signature=signature,
                return_type='void',  # 생성자는 반환 타입이 없음
                start_line=0,  # TODO: 정확한 라인 번호 계산
                end_line=0,    # TODO: 정확한 라인 번호 계산
                annotations=json.dumps(annotations) if annotations else None,
                parameters=json.dumps(parameters) if parameters else None,
                modifiers=json.dumps(list(modifiers)) if modifiers else None
            )
            
            # MetadataEngine에서 필요한 속성 추가
            constructor_obj.owner_fqn = owner_fqn
            
            return constructor_obj
            
        except Exception as e:
            print(f"Error extracting constructor from javalang: {e}")
            return None
    
    def _extract_dependencies_from_javalang(self, tree, file_path: str, project_id: int, methods: List[Method]) -> List[Edge]:
        """의존성 관계를 추출합니다."""
        edges = []
        
        try:
            # import 문에서 의존성 추출
            if tree.imports:
                for import_decl in tree.imports:
                    if import_decl.path:
                        # import된 클래스와의 의존성 관계 생성
                        imported_class = import_decl.path.split('.')[-1]
                        
                        # 각 메서드에서 이 클래스를 사용하는지 확인
                        for method in methods:
                            edge = Edge(
                                project_id=project_id,
                                src_type='method',
                                src_id=None,  # 나중에 설정
                                dst_type='class',
                                dst_id=None,  # 외부 클래스이므로 None
                                edge_kind='uses',
                                confidence=0.7,
                                meta=f'{{"imported_class": "{imported_class}", "import_path": "{import_decl.path}"}}'
                            )
                            edges.append(edge)
            
        except Exception as e:
            print(f"Error extracting dependencies from javalang: {e}")
        
        return edges
    
    def _count_lines_in_node(self, node) -> int:
        """AST 노드의 라인 수를 계산합니다."""
        try:
            if hasattr(node, 'position') and node.position:
                return node.position.line
            return 1
        except:
            return 1
    
    def _parse_with_regex(self, content: str, file_path: str, project_id: int) -> Tuple[List[Class], List[Method], List[Edge]]:
        """정규식 기반 파싱 (fallback)"""
        classes = []
        methods = []
        edges = []
        
        try:
            # 패키지 추출
            package_match = re.search(r'package\s+([^;]+);', content)
            package_name = package_match.group(1) if package_match else ""
            
            # 클래스 추출 (더 정확한 패턴)
            class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
            for match in re.finditer(class_pattern, content, re.IGNORECASE):
                class_name = match.group(1)
                extends = match.group(2) if match.group(2) else None
                implements = match.group(3) if match.group(3) else None
                
                fqn = f"{package_name}.{class_name}" if package_name else class_name
                
                # 클래스 내부의 메서드 수 계산
                class_start = match.start()
                class_end = self._find_matching_brace(content, class_start)
                class_content = content[class_start:class_end] if class_end > class_start else ""
                
                # 메서드 수 계산
                method_count = len(re.findall(r'(?:public|private|protected|static|final|abstract|synchronized)?\s*\w+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{', class_content))
                
                class_obj = Class(
                    file_id=None,  # 나중에 설정
                    fqn=fqn,
                    name=class_name,
                    start_line=1,  # TODO: 정확한 라인 계산
                    end_line=self._count_lines_in_content(class_content),
                    modifiers=json.dumps(['public'] if 'public' in match.group(0) else []),
                    annotations=json.dumps([])
                )
                classes.append(class_obj)
            
            # 인터페이스 추출
            interface_pattern = r'(?:public\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{'
            for match in re.finditer(interface_pattern, content, re.IGNORECASE):
                interface_name = match.group(1)
                extends = match.group(2) if match.group(2) else None
                
                fqn = f"{package_name}.{interface_name}" if package_name else interface_name
                
                # 인터페이스 내부의 메서드 수 계산
                interface_start = match.start()
                interface_end = self._find_matching_brace(content, interface_start)
                interface_content = content[interface_start:interface_end] if interface_end > interface_start else ""
                
                # 메서드 수 계산 (인터페이스는 추상 메서드만)
                method_count = len(re.findall(r'(?:public\s+)?(?:abstract\s+)?\w+\s+\w+\s*\([^)]*\)\s*;', interface_content))
                
                interface_obj = Class(
                    file_id=None,  # 나중에 설정
                    fqn=fqn,
                    name=interface_name,
                    start_line=1,  # TODO: 정확한 라인 계산
                    end_line=self._count_lines_in_content(interface_content),
                    modifiers=json.dumps(['public', 'interface'] if 'public' in match.group(0) else ['interface']),
                    annotations=json.dumps([])
                )
                classes.append(interface_obj)
            
            # 메서드 추출 (더 정확한 패턴)
            method_pattern = r'(?:public|private|protected|static|final|abstract|synchronized)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            for match in re.finditer(method_pattern, content, re.IGNORECASE):
                return_type = match.group(1)
                method_name = match.group(2)
                parameters = match.group(3) if match.group(3) else ""
                
                # 메서드가 속한 클래스 찾기
                owner_fqn = ""
                for class_obj in classes:
                    class_start = content.find(f"class {class_obj.name}")
                    if class_start != -1 and match.start() > class_start:
                        # 클래스 내부에 있는지 확인
                        class_end = self._find_matching_brace(content, class_start)
                        if match.start() < class_end:
                            owner_fqn = class_obj.fqn
                            break
                
                if not owner_fqn and classes:
                    owner_fqn = classes[0].fqn  # fallback
                
                method_obj = Method(
                    class_id=None,  # 나중에 설정
                    name=method_name,
                    signature=f"{return_type} {method_name}({parameters})",
                    return_type=return_type,
                    start_line=1,  # TODO: 정확한 라인 계산
                    end_line=1,  # TODO: 정확한 라인 계산
                    annotations=json.dumps([]),
                    parameters=json.dumps(parameters.split(',') if parameters else []),
                    modifiers=json.dumps([])
                )
                # owner_fqn 정보를 메서드 객체에 추가 (임시 속성)
                method_obj.owner_fqn = owner_fqn
                methods.append(method_obj)
            
            # Edge 생성 로직 추가
            edges = self._generate_edges_from_regex(content, classes, methods, package_name, project_id)
            
            # Edge의 src_id, dst_id 설정 (클래스 ID로)
            for edge in edges:
                if hasattr(edge, 'src_fqn') and hasattr(edge, 'dst_fqn'):
                    # 클래스 FQN으로 클래스 ID 찾기
                    for cls in classes:
                        if cls.fqn == edge.src_fqn:
                            edge.src_id = cls.class_id
                        if cls.fqn == edge.dst_fqn:
                            edge.dst_id = cls.class_id
            
        except Exception as e:
            print(f"Error in regex parsing: {e}")
        
        return classes, methods, edges
    
    def _generate_edges_from_regex(self, content: str, classes: List[Class], methods: List[Method], package_name: str, project_id: int) -> List[Edge]:
        """정규식 기반으로 Edge 관계를 생성합니다."""
        edges = []
        
        try:
            # import 문에서 의존성 추출
            import_pattern = r'import\s+([^;]+);'
            imports = re.findall(import_pattern, content)
            
            # 클래스 간 상속/구현 관계 생성
            for class_obj in classes:
                class_content = self._extract_class_content(content, class_obj.name)
                if not class_content:
                    continue
                
                # extends 관계
                extends_match = re.search(r'extends\s+(\w+)', class_content)
                if extends_match:
                    parent_class = extends_match.group(1)
                    # import 문에서 정확한 FQN 찾기
                    dst_fqn = self._resolve_class_fqn(parent_class, imports, package_name)
                    if dst_fqn:
                        edge = Edge(
                            project_id=project_id,
                            src_id=None,  # 나중에 설정
                            dst_id=None,  # 나중에 설정
                            src_type='class',
                            dst_type='class',
                            edge_kind='extends',
                            confidence=0.9,
                            meta=json.dumps({'parent_class': parent_class})
                        )
                        edge.src_fqn = class_obj.fqn
                        edge.dst_fqn = dst_fqn
                        edges.append(edge)
                
                # implements 관계
                implements_match = re.search(r'implements\s+([^{]+)', class_content)
                if implements_match:
                    interfaces = [i.strip() for i in implements_match.group(1).split(',')]
                    for interface in interfaces:
                        # import 문에서 정확한 FQN 찾기
                        dst_fqn = self._resolve_class_fqn(interface, imports, package_name)
                        if dst_fqn:
                            edge = Edge(
                                project_id=project_id,
                                src_id=None,  # 나중에 설정
                                dst_id=None,  # 나중에 설정
                                src_type='class',
                                dst_type='interface',
                                edge_kind='implements',
                                confidence=0.9,
                                meta=json.dumps({'interface': interface})
                            )
                            edge.src_fqn = class_obj.fqn
                            edge.dst_fqn = dst_fqn
                            edges.append(edge)
                
                # 메서드 호출 관계 (간단한 패턴)
                method_calls = re.findall(r'(\w+)\s*\([^)]*\)', class_content)
                for method_call in method_calls:
                    # 다른 클래스의 메서드 호출인지 확인
                    for other_class in classes:
                        if other_class.name != class_obj.name and method_call in other_class.name.lower():
                            edge = Edge(
                                project_id=project_id,
                                src_id=None,  # 나중에 설정
                                dst_id=None,  # 나중에 설정
                                src_type='class',
                                dst_type='class',
                                edge_kind='calls',
                                confidence=0.7,
                                meta=json.dumps({'method_call': method_call})
                            )
                            edge.src_fqn = class_obj.fqn
                            edge.dst_fqn = other_class.fqn
                            edges.append(edge)
                            break
            
            print(f"Generated {len(edges)} edges from regex parsing")
            
        except Exception as e:
            print(f"Error generating edges from regex: {e}")
        
        return edges
    
    def _resolve_class_fqn(self, class_name: str, imports: List[str], package_name: str) -> str:
        """클래스명을 FQN으로 해결합니다."""
        # 1. import 문에서 정확한 FQN 찾기
        for import_stmt in imports:
            if import_stmt.endswith(f".{class_name}"):
                return import_stmt
        
        # 2. java.lang 패키지 클래스들
        java_lang_classes = ['String', 'Object', 'Integer', 'Long', 'Double', 'Float', 'Boolean', 'Character', 'Byte', 'Short']
        if class_name in java_lang_classes:
            return f"java.lang.{class_name}"
        
        # 3. 현재 패키지의 클래스
        if package_name:
            return f"{package_name}.{class_name}"
        
        # 4. 기본 패키지
        return class_name
    
    def _extract_class_content(self, content: str, class_name: str) -> str:
        """클래스 내용을 추출합니다."""
        try:
            # 클래스 시작 찾기
            class_pattern = rf'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+{class_name}\s*[^{{]*\{{'
            match = re.search(class_pattern, content, re.IGNORECASE)
            if not match:
                return ""
            
            start_pos = match.start()
            end_pos = self._find_matching_brace(content, start_pos)
            
            if end_pos > start_pos:
                return content[start_pos:end_pos]
            return ""
            
        except Exception as e:
            print(f"Error extracting class content: {e}")
            return ""
    
    def _find_matching_brace(self, content: str, start_pos: int) -> int:
        """시작 위치부터 매칭되는 중괄호를 찾습니다."""
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i + 1
        
        return len(content)
    
    def _count_lines_in_content(self, content: str) -> int:
        """내용의 라인 수를 계산합니다."""
        return len(content.splitlines()) if content else 0
    
    def parse(self, content: str, file_path: str, project_id: int = 1) -> Tuple[File, List[Class], List[Method], List[Edge]]:
        """
        Java 소스 코드 내용을 파싱하여 메타데이터를 추출합니다.
        
        Args:
            content: Java 소스 코드 내용
            file_path: 파일 경로
            project_id: 프로젝트 ID
            
        Returns:
            (File, List[Class], List[Method], List[Edge]) 튜플
        """
        try:
            # File 객체 생성
            file_obj = self._create_file_object(file_path, project_id, content)
            
            # javalang을 사용한 파싱
            if self.javalang_available:
                classes, methods, edges = self._parse_with_javalang(content, file_path, project_id)
            else:
                # 정규식 기반 파싱 (fallback)
                classes, methods, edges = self._parse_with_regex(content, file_path, project_id)
            
            return file_obj, classes, methods, edges
                
        except Exception as e:
            print(f"Java 파싱 실패 {file_path}: {e}")
            # 에러 시에도 File 객체는 반환
            file_obj = self._create_file_object(file_path, project_id, content)
            return file_obj, [], [], []

    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """BaseParser 인터페이스 구현"""
        if self.javalang_available:
            try:
                tree = parse.parse(content)
                return {
                    'classes': self._extract_classes_from_tree(tree),
                    'methods': self._extract_methods_from_tree(tree),
                    'imports': self._extract_imports_from_tree(tree),
                    'confidence': 0.9
                }
            except:
                return {'classes': [], 'methods': [], 'imports': [], 'confidence': 0.3}
        else:
            return {'classes': [], 'methods': [], 'imports': [], 'confidence': 0.1}
    
    def _extract_classes_from_tree(self, tree) -> List[Dict[str, Any]]:
        """AST에서 클래스 정보를 추출합니다."""
        classes = []
        package_name = tree.package.name if tree.package else ""
        
        for type_decl in tree.types:
            if isinstance(type_decl, tree.ClassDeclaration):
                classes.append({
                    'name': type_decl.name,
                    'package': package_name,
                    'type': 'class',
                    'modifiers': type_decl.modifiers or []
                })
            elif isinstance(type_decl, tree.InterfaceDeclaration):
                classes.append({
                    'name': type_decl.name,
                    'package': package_name,
                    'type': 'interface',
                    'modifiers': type_decl.modifiers or []
                })
        
        return classes
    
    def _extract_methods_from_tree(self, tree) -> List[Dict[str, Any]]:
        """AST에서 메서드 정보를 추출합니다."""
        methods = []
        
        for type_decl in tree.types:
            if hasattr(type_decl, 'methods') and type_decl.methods:
                for method_decl in type_decl.methods:
                    methods.append({
                        'name': method_decl.name,
                        'return_type': method_decl.return_type.name if method_decl.return_type else 'void',
                        'modifiers': method_decl.modifiers or []
                    })
        
        return methods
    
    def _extract_imports_from_tree(self, tree) -> List[str]:
        """AST에서 import 정보를 추출합니다."""
        imports = []
        
        if tree.imports:
            for import_decl in tree.imports:
                if import_decl.path:
                    imports.append(import_decl.path)
        
        return imports
