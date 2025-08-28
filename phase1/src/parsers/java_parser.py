"""
JavaParser 라이브러리를 사용한 Java 소스 코드 파서
클래스, 메서드, 어노테이션, 의존성 정보를 추출합니다.
"""

import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
import re

try:
    import javalang
except ImportError:
    # javalang이 설치되지 않은 환경을 위한 대체 처리
    javalang = None

from ..models.database import File, Class, Method, Edge
from ..utils.confidence_calculator import ConfidenceCalculator

class JavaParser:
    """javalang 라이브러리를 사용한 Java 소스 파일 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Java 파서 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        
    def can_parse(self, file_path: str) -> bool:
        """
        이 파서로 파일을 처리할 수 있는지 확인
        
        Args:
            file_path: 파일 경로
            
        Returns:
            처리 가능 여부
        """
        return file_path.endswith('.java') and javalang is not None
        
    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[Class], List[Method], List[Edge]]:
        """
        Java 파일을 파싱하여 메타데이터 추출
        
        Args:
            file_path: Java 파일 경로
            project_id: 데이터베이스 프로젝트 ID
            
        Returns:
            (File, Classes, Methods, Edges) 튜플
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 파일 메타데이터 계산
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            file_stat = os.stat(file_path)
            loc = len([line for line in content.split('\n') if line.strip()])
            
            # File 객체 생성
            file_obj = File(
                project_id=project_id,
                path=file_path,
                language='java',
                hash=file_hash,
                loc=loc,
                mtime=datetime.fromtimestamp(file_stat.st_mtime)
            )
            
            # Java AST 파싱
            try:
                tree = javalang.parse.parse(content)
            except Exception as e:
                # 파싱 실패 시 낮은 신뢰도로 파일 생성
                print(f"파일 파싱 실패 {file_path}: {e}")
                return file_obj, [], [], []
                
            classes = []
            methods = []
            edges = []
            
            # 클래스와 메서드 추출
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_obj, class_methods, class_edges = self._extract_class(node, file_obj, path)
                classes.append(class_obj)
                methods.extend(class_methods)
                edges.extend(class_edges)
                
            # 인터페이스 선언 추출
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                interface_obj, interface_methods, interface_edges = self._extract_interface(node, file_obj, path)
                classes.append(interface_obj)
                methods.extend(interface_methods)
                edges.extend(interface_edges)
                
            # 열거형 선언 추출
            for path, node in tree.filter(javalang.tree.EnumDeclaration):
                enum_obj, enum_methods, enum_edges = self._extract_enum(node, file_obj, path)
                classes.append(enum_obj)
                methods.extend(enum_methods)
                edges.extend(enum_edges)
                
            return file_obj, classes, methods, edges
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return file_obj, [], [], []
            
    def _extract_class(self, node: javalang.tree.ClassDeclaration, file_obj: File, path: List) -> Tuple[Class, List[Method], List[Edge]]:
        """
        클래스 정보와 메서드들을 추출
        
        Args:
            node: 클래스 선언 AST 노드
            file_obj: 파일 객체
            path: AST 경로
            
        Returns:
            (Class, Methods, Edges) 튜플
        """
        
        # 완전한 클래스명 구성
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        # 수식어와 어노테이션 추출
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        # 라인 번호 추정 (javalang은 정확한 위치 정보를 제공하지 않음)
        start_line, end_line = self._estimate_line_numbers(node, file_obj)
        
        class_obj = Class(
            file_id=None,  # Will be set after file is saved
            fqn=fqn,
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            modifiers=json.dumps(modifiers),
            annotations=json.dumps(annotations)
        )
        
        methods = []
        edges = []
        
        # Extract methods
        if hasattr(node, 'body') and node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, class_obj)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                elif isinstance(member, javalang.tree.ConstructorDeclaration):
                    constructor_obj, constructor_edges = self._extract_constructor(member, class_obj)
                    methods.append(constructor_obj)
                    edges.extend(constructor_edges)
                    
        # Extract inheritance relationships
        if node.extends:
            inheritance_edge = Edge(
                src_type='class',
                src_id=None,  # Will be set after class is saved
                dst_type='class',
                dst_id=None,  # Need to resolve later
                edge_kind='extends',
                confidence=0.9
            )
            edges.append(inheritance_edge)
            
        # Extract interface implementations  
        if node.implements:
            for interface in node.implements:
                implementation_edge = Edge(
                    src_type='class',
                    src_id=None,
                    dst_type='interface',
                    dst_id=None,  # Need to resolve later
                    edge_kind='implements',
                    confidence=0.9
                )
                edges.append(implementation_edge)
                
        return class_obj, methods, edges
        
    def _extract_interface(self, node: javalang.tree.InterfaceDeclaration, file_obj: File, path: List) -> Tuple[Class, List[Method], List[Edge]]:
        """
        인터페이스 정보와 메서드들을 추출
        
        Args:
            node: 인터페이스 선언 AST 노드
            file_obj: 파일 객체
            path: AST 경로
            
        Returns:
            (Interface, Methods, Edges) 튜플
        """
        
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        start_line, end_line = self._estimate_line_numbers(node, file_obj)
        
        interface_obj = Class(  # 인터페이스도 Class 테이블 사용
            file_id=None,
            fqn=fqn,
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            modifiers=json.dumps(['interface'] + modifiers),
            annotations=json.dumps(annotations)
        )
        
        methods = []
        edges = []
        
        # 인터페이스 메서드 추출
        if hasattr(node, 'body') and node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, interface_obj)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                    
        return interface_obj, methods, edges
        
    def _extract_enum(self, node: javalang.tree.EnumDeclaration, file_obj: File, path: List) -> Tuple[Class, List[Method], List[Edge]]:
        """
        열거형(enum) 정보와 메서드들을 추출
        
        Args:
            node: 열거형 선언 AST 노드
            file_obj: 파일 객체
            path: AST 경로
            
        Returns:
            (Enum, Methods, Edges) 튜플
        """
        
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        start_line, end_line = self._estimate_line_numbers(node, file_obj)
        
        enum_obj = Class(  # 열거형도 Class 테이블 사용
            file_id=None,
            fqn=fqn,
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            modifiers=json.dumps(['enum'] + modifiers),
            annotations=json.dumps(annotations)
        )
        
        methods = []
        edges = []
        
        # 열거형 메서드 추출
        if hasattr(node, 'body') and node.body:
            for member in node.body.declarations if hasattr(node.body, 'declarations') else []:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, enum_obj)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                    
        return enum_obj, methods, edges
        
    def _extract_method(self, node: javalang.tree.MethodDeclaration, class_obj: Class) -> Tuple[Method, List[Edge]]:
        """
        메서드 정보와 호출 관계를 추출
        
        Args:
            node: 메서드 선언 AST 노드
            class_obj: 소속 클래스 객체
            
        Returns:
            (Method, Edges) 튜플
        """
        
        # 메서드 시그니처 구성
        params = []
        if node.parameters:
            for param in node.parameters:
                param_type = self._get_type_string(param.type)
                params.append(f"{param_type} {param.name}")
        signature = f"{node.name}({', '.join(params)})"
        
        # 반환 타입 추출
        return_type = self._get_type_string(node.return_type) if node.return_type else 'void'
        
        # 어노테이션 추출
        annotations = self._extract_annotations(node.annotations)
        
        # 라인 번호 추정
        start_line, end_line = self._estimate_line_numbers(node, None)
        
        method_obj = Method(
            class_id=None,  # Will be set after class is saved
            name=node.name,
            signature=signature,
            return_type=return_type,
            start_line=start_line,
            end_line=end_line,
            annotations=json.dumps(annotations)
        )
        
        edges = []
        
        # 메서드 본문에서 호출 관계 추출
        if node.body:
            method_calls = self._extract_method_calls(node.body)
            for call in method_calls:
                call_edge = Edge(
                    src_type='method',
                    src_id=None,  # Will be set after method is saved
                    dst_type='method',
                    dst_id=None,  # Need to resolve later
                    edge_kind='call',
                    confidence=0.8  # 메서드 호출은 대체로 명확함
                )
                edges.append(call_edge)
                
        return method_obj, edges
        
    def _extract_constructor(self, node: javalang.tree.ConstructorDeclaration, class_obj: Class) -> Tuple[Method, List[Edge]]:
        """
        생성자 정보와 호출 관계를 추출
        
        Args:
            node: 생성자 선언 AST 노드
            class_obj: 소속 클래스 객체
            
        Returns:
            (Constructor, Edges) 튜플
        """
        
        # 생성자 시그니처 구성
        params = []
        if node.parameters:
            for param in node.parameters:
                param_type = self._get_type_string(param.type)
                params.append(f"{param_type} {param.name}")
        signature = f"{node.name}({', '.join(params)})"
        
        annotations = self._extract_annotations(node.annotations)
        start_line, end_line = self._estimate_line_numbers(node, None)
        
        constructor_obj = Method(
            class_id=None,
            name=f"<init>",  # 생성자 식별자
            signature=signature,
            return_type=class_obj.name,
            start_line=start_line,
            end_line=end_line,
            annotations=json.dumps(annotations)
        )
        
        edges = []
        
        # 생성자 본문에서 메서드 호출 관계 추출
        if node.body:
            method_calls = self._extract_method_calls(node.body)
            for call in method_calls:
                call_edge = Edge(
                    src_type='method',
                    src_id=None,
                    dst_type='method',
                    dst_id=None,
                    edge_kind='call',
                    confidence=0.8
                )
                edges.append(call_edge)
                
        return constructor_obj, edges
        
    def _get_package_name(self, path: List) -> Optional[str]:
        """
        AST 경로에서 패키지 이름을 추출
        
        Args:
            path: AST 경로 리스트
            
        Returns:
            패키지 이름 (없으면 None)
        """
        for node in path:
            if isinstance(node, javalang.tree.CompilationUnit) and node.package:
                return node.package.name
        return None
        
    def _extract_annotations(self, annotations) -> List[Dict[str, Any]]:
        """
        어노테이션 정보를 추출
        
        Args:
            annotations: 어노테이션 노드 리스트
            
        Returns:
            어노테이션 정보 딕셔너리 리스트
        """
        if not annotations:
            return []
            
        result = []
        for annotation in annotations:
            annotation_info = {
                'name': annotation.name,
                'element': None
            }
            
            if hasattr(annotation, 'element') and annotation.element:
                # 어노테이션 매개변수 추출
                if isinstance(annotation.element, list):
                    annotation_info['element'] = [str(elem) for elem in annotation.element]
                else:
                    annotation_info['element'] = str(annotation.element)
                    
            result.append(annotation_info)
            
        return result
        
    def _get_type_string(self, type_node) -> str:
        """
        타입 노드를 문자열 표현으로 변환
        
        Args:
            type_node: 타입 AST 노드
            
        Returns:
            타입 문자열 표현
        """
        if not type_node:
            return 'unknown'
            
        if hasattr(type_node, 'name'):
            return type_node.name
        elif hasattr(type_node, 'arguments') and type_node.arguments:
            # 제네릭 타입
            base_type = getattr(type_node, 'name', 'unknown')
            args = [self._get_type_string(arg) for arg in type_node.arguments]
            return f"{base_type}<{', '.join(args)}>"
        else:
            return str(type_node)
            
    def _estimate_line_numbers(self, node, file_obj: Optional[File]) -> Tuple[int, int]:
        """
        AST 노드의 라인 번호를 추정
        javalang이 정확한 위치 정보를 제공하지 않으므로 대략적인 추정값
        
        Args:
            node: AST 노드
            file_obj: 파일 객체 (옵션)
            
        Returns:
            (시작_라인, 종료_라인) 튜플
        """
        # 실제 구현에서는 파싱 중 라인 번호 추적이나 다른 파서 사용 필요
        start_line = getattr(node, 'position', None)
        if start_line and hasattr(start_line, 'line'):
            start_line = start_line.line
        else:
            start_line = 1
            
        # 종료 라인 대략 추정
        end_line = start_line + 10  # 기본 추정값
        
        return start_line, end_line
        
    def _extract_method_calls(self, body) -> List[str]:
        """
        메서드 본문에서 메서드 호출을 추출
        
        Args:
            body: 메서드 본문 AST 노드
            
        Returns:
            호출된 메서드 이름 리스트
        """
        method_calls = []
        
        # 단순화된 구현
        # 실제로는 AST를 더 철저하게 순회해야 함
        if hasattr(body, '__iter__'):
            for statement in body:
                if hasattr(statement, 'expression'):
                    calls = self._find_method_invocations(statement.expression)
                    method_calls.extend(calls)
                    
        return method_calls
        
    def _find_method_invocations(self, node) -> List[str]:
        """
        AST에서 메서드 호출 노드를 찾음
        
        Args:
            node: 검색할 AST 노드
            
        Returns:
            발견된 메서드 호출 이름 리스트
        """
        invocations = []
        
        if isinstance(node, javalang.tree.MethodInvocation):
            invocations.append(node.member)
            
        # 자식 노드들을 재귀적으로 검색
        if hasattr(node, '__dict__'):
            for attr_value in node.__dict__.values():
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, '__dict__'):
                            invocations.extend(self._find_method_invocations(item))
                elif hasattr(attr_value, '__dict__'):
                    invocations.extend(self._find_method_invocations(attr_value))
                    
        return invocations