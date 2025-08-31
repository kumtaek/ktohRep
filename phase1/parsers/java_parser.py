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

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    # tree_sitter_java 등이 설치되어야 함
    try:
        import tree_sitter_java
        TREE_SITTER_AVAILABLE = True
    except ImportError:
        TREE_SITTER_AVAILABLE = False
except ImportError:
    tree_sitter = None
    Language = None
    Parser = None
    TREE_SITTER_AVAILABLE = False

from models.database import File, Class, Method, Edge
from utils.confidence_calculator import ConfidenceCalculator

class JavaParser:
    """javalang 또는 Tree-sitter를 사용한 Java 소스 파일 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Java 파서 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        # logger
        try:
            from utils.logger import LoggerFactory
            self.logger = LoggerFactory.get_parser_logger("java")
        except Exception:
            self.logger = None
        
        # Tree-sitter 파서 초기화
        self.tree_sitter_parser = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.java_language = Language(tree_sitter_java.language(), "java")
                self.tree_sitter_parser = Parser()
                self.tree_sitter_parser.set_language(self.java_language)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Tree-sitter 초기화 실패: {e}")
                else:
                    print(f"Tree-sitter 초기화 실패: {e}")
                self.tree_sitter_parser = None
        
    def can_parse(self, file_path: str) -> bool:
        """
        이 파서로 파일을 처리할 수 있는지 확인
        
        Args:
            file_path: 파일 경로
            
        Returns:
            처리 가능 여부
        """
        return file_path.endswith('.java') and (javalang is not None or self.tree_sitter_parser is not None)
        
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
            
            # Parser configuration and selection
            parser_cfg = (self.config.get('java', {}) or {}).get('parser_type', 'javalang').lower()
            
            def _select_parser() -> str:
                if parser_cfg == 'tree-sitter' and self.tree_sitter_parser:
                    return 'tree_sitter'
                if parser_cfg == 'javalang' and javalang is not None:
                    return 'javalang'
                # 폴백: 사용 가능 항목 우선
                if self.tree_sitter_parser:
                    return 'tree_sitter'
                if javalang is not None:
                    return 'javalang'
                return 'none'

            parser_used = _select_parser()
            if parser_used == 'none':
                # 로깅 후 빈 결과 반환
                if self.logger:
                    self.logger.warning('No available Java parser (javalang/tree-sitter)')
                else:
                    print('No available Java parser (javalang/tree-sitter)')
                return file_obj, [], [], []

            # Java AST 파싱
            try:
                if parser_used == 'javalang':
                    tree = javalang.parse.parse(content)
                elif parser_used == 'tree_sitter':
                    tree = self._parse_with_tree_sitter(content)
                else:
                    tree = None
            except Exception as e:
                # 파싱 실패 시 낮은 신뢰도로 파일 생성
                if self.logger:
                    self.logger.error(f"파일 파싱 실패: {file_path}", exception=e)
                else:
                    print(f"파일 파싱 실패 {file_path}: {e}")
                return file_obj, [], [], []
                
            classes = []
            methods = []
            edges = []
            
            # 파서에 따른 추출 방식 선택
            if parser_used == 'javalang':
                # Javalang를 사용한 추출
                for path, node in tree.filter(javalang.tree.ClassDeclaration):
                    class_obj, class_methods, class_edges = self._extract_class(node, file_obj, path)
                    classes.append(class_obj)
                    methods.extend(class_methods)
                    edges.extend(class_edges)
                    
                for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                    interface_obj, interface_methods, interface_edges = self._extract_interface(node, file_obj, path)
                    classes.append(interface_obj)
                    methods.extend(interface_methods)
                    edges.extend(interface_edges)
                    
                for path, node in tree.filter(javalang.tree.EnumDeclaration):
                    enum_obj, enum_methods, enum_edges = self._extract_enum(node, file_obj, path)
                    classes.append(enum_obj)
                    methods.extend(enum_methods)
                    edges.extend(enum_edges)
                    
            elif parser_used == 'tree_sitter':
                # Tree-sitter를 사용한 추출
                classes, methods, edges = self._extract_with_tree_sitter(tree, file_obj, content)
                
            return file_obj, classes, methods, edges
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Java 파싱 중 오류: {file_path}", exception=e)
            else:
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
        
        # Extract fields to resolve method calls later
        fields = {}
        if hasattr(node, 'body') and node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.FieldDeclaration):
                    field_type = self._get_type_string(member.type)
                    for declarator in member.declarators:
                        fields[declarator.name] = field_type

        # Extract methods
        if hasattr(node, 'body') and node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, class_obj, fields)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                elif isinstance(member, javalang.tree.ConstructorDeclaration):
                    constructor_obj, constructor_edges = self._extract_constructor(member, class_obj)
                    methods.append(constructor_obj)
                    edges.extend(constructor_edges)
                    
        # Extract inheritance relationships
        if node.extends:
            target = self._get_type_string(node.extends)
            inheritance_edge = Edge(
                src_type='class',
                src_id=None,  # Will be set after class is saved
                dst_type='class',
                dst_id=None,  # Need to resolve later
                edge_kind='extends',
                confidence=0.9
            )
            setattr(inheritance_edge, 'src_class_fqn', fqn)
            try:
                setattr(inheritance_edge, 'meta', json.dumps({'target': target}))
            except Exception:
                pass
            edges.append(inheritance_edge)

        # Extract interface implementations
        if node.implements:
            for interface in node.implements:
                target = self._get_type_string(interface)
                implementation_edge = Edge(
                    src_type='class',
                    src_id=None,
                    dst_type='interface',
                    dst_id=None,  # Need to resolve later
                    edge_kind='implements',
                    confidence=0.9
                )
                setattr(implementation_edge, 'src_class_fqn', fqn)
                try:
                    setattr(implementation_edge, 'meta', json.dumps({'target': target}))
                except Exception:
                    pass
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
                    method_obj, method_edges = self._extract_method(member, interface_obj, {})  # Pass empty dict for fields
                    methods.append(method_obj)
                    edges.extend(method_edges)

        # 인터페이스 상속 관계 추출
        if node.extends:
            for parent in node.extends:
                target = self._get_type_string(parent)
                extends_edge = Edge(
                    src_type='interface',
                    src_id=None,
                    dst_type='interface',
                    dst_id=None,
                    edge_kind='extends',
                    confidence=0.9,
                )
                setattr(extends_edge, 'src_class_fqn', fqn)
                try:
                    setattr(extends_edge, 'meta', json.dumps({'target': target}))
                except Exception:
                    pass
                edges.append(extends_edge)

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
                    method_obj, method_edges = self._extract_method(member, enum_obj, {})  # Pass empty dict for fields
                    methods.append(method_obj)
                    edges.extend(method_edges)

        # 열거형은 암묵적으로 java.lang.Enum을 상속받지만, 명시적인 extends는 없음.
        # 필요하다면 여기에 Enum 상속 엣지를 추가할 수 있음.

        return enum_obj, methods, edges
        
    def _extract_method(self, node: javalang.tree.MethodDeclaration, class_obj: Class, fields: Dict[str, str]) -> Tuple[Method, List[Edge]]:
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
        # 저장 단계 매핑용 임시 속성
        try:
            setattr(method_obj, 'owner_fqn', class_obj.fqn)
        except Exception:
            pass
        
        edges = []

        # 심볼 테이블 초기화: 클래스 필드, this, 메서드 매개변수
        symbol_table = dict(fields)
        symbol_table['this'] = class_obj.fqn
        if node.parameters:
            for param in node.parameters:
                param_type = self._get_type_string(param.type)
                symbol_table[param.name] = param_type

        # 메서드 본문에서 호출 관계 추출
        if node.body:
            method_calls = self._extract_method_calls(node.body, symbol_table)
            for call_info in method_calls:
                call_edge = Edge(
                    src_type='method',
                    src_id=None,  # Will be set after method is saved
                    dst_type='method',
                    dst_id=None,  # Need to resolve later
                    edge_kind='call',
                    confidence=0.8  # 메서드 호출은 대체로 명확함
                )
                # 메타데이터(JSON) 또는 보조 힌트로 저장
                try:
                    setattr(call_edge, 'meta', json.dumps({
                        'called_name': call_info['member'],
                        'callee_qualifier_type': call_info.get('qualifier_type'),
                        'src_method_fqn': f"{class_obj.fqn}.{method_obj.name}"  # 호출하는 메서드의 FQN 추가
                    }))
                except Exception:
                    setattr(call_edge, 'called_method_name', call_info['member'])
                    setattr(call_edge, 'callee_qualifier_type', call_info.get('qualifier_type'))
                    setattr(call_edge, 'src_method_fqn', f"{class_obj.fqn}.{method_obj.name}")  # 대체 속성에도 추가
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
        # 저장 단계 매핑용 임시 속성
        try:
            setattr(constructor_obj, 'owner_fqn', class_obj.fqn)
        except Exception:
            pass
        
        edges = []

        # 심볼 테이블 초기화: this 및 매개변수
        symbol_table: Dict[str, str] = {'this': class_obj.fqn}
        if node.parameters:
            for param in node.parameters:
                param_type = self._get_type_string(param.type)
                symbol_table[param.name] = param_type

        # 생성자 본문에서 메서드 호출 관계 추출
        if node.body:
            method_calls = self._extract_method_calls(node.body, symbol_table)
            for call in method_calls:
                call_edge = Edge(
                    src_type='method',
                    src_id=None,
                    dst_type='method',
                    dst_id=None,
                    edge_kind='call',
                    confidence=0.8
                )
                try:
                    setattr(call_edge, 'meta', json.dumps({
                        'called_name': call['member'],
                        'callee_qualifier_type': call.get('qualifier_type'),
                        'src_method_fqn': f"{class_obj.fqn}.<init>"
                    }))
                except Exception:
                    setattr(call_edge, 'called_method_name', call['member'])
                    setattr(call_edge, 'callee_qualifier_type', call.get('qualifier_type'))
                    setattr(call_edge, 'src_method_fqn', f"{class_obj.fqn}.<init>")
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
        
    def _extract_method_calls(self, body, symbol_table: Dict[str, str]) -> List[Dict[str, str]]:
        """
        메서드 본문에서 메서드 호출을 추출 (재귀적 AST 순회)

        Args:
            body: 메서드 본문 AST 노드 (list 또는 javalang.tree.Node)
            symbol_table: 변수 -> 타입 매핑을 보유한 심볼 테이블

        Returns:
            호출된 메서드 정보 딕셔너리 리스트
        """
        method_calls = []
        if self.logger:
            self.logger.debug(f"[_extract_method_calls] body type: {type(body)}")
        if body:
            # body가 리스트인 경우 각 요소를 순회
            if isinstance(body, list):
                for item in body:
                    method_calls.extend(self._find_method_invocations_recursive(item, symbol_table))
            # body가 단일 AST 노드인 경우
            else:
                method_calls.extend(self._find_method_invocations_recursive(body, symbol_table))
        if self.logger:
            self.logger.debug(f"[_extract_method_calls] found {len(method_calls)} method calls.")
        return method_calls

    def _find_method_invocations_recursive(self, node, symbol_table: Dict[str, str]) -> List[Dict[str, str]]:
        """
        AST 노드를 재귀적으로 순회하며 메서드 호출 노드를 찾음

        Args:
            node: 검색할 AST 노드
            symbol_table: 현재 스코프의 변수 -> 타입 매핑

        Returns:
            발견된 메서드 호출 정보 딕셔너리 리스트
        """
        invocations = []
        if self.logger:
            self.logger.debug(f"[_find_method_invocations_recursive] node type: {type(node)}, node: {node}")

        if isinstance(node, javalang.tree.MethodInvocation):
            qualifier = getattr(node, 'qualifier', None)
            if qualifier is None:
                qualifier_type = symbol_table.get('this')
            else:
                qualifier_type = symbol_table.get(qualifier, qualifier)

            call_info = {
                'member': node.member,
                'qualifier': qualifier,
                'qualifier_type': qualifier_type
            }
            invocations.append(call_info)
            if self.logger:
                self.logger.debug(f"[_find_method_invocations_recursive] Found MethodInvocation: {call_info}")

        elif isinstance(node, javalang.tree.MethodInvocation):
            invocations.append({
                'member': node.member,
                'qualifier': 'this',
                'qualifier_type': symbol_table.get('this')
            })

        elif isinstance(node, javalang.tree.SuperMethodInvocation):
            invocations.append({
                'member': node.member,
                'qualifier': 'super',
                'qualifier_type': symbol_table.get('this')
            })

        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            var_type = self._get_type_string(node.type)
            for declarator in node.declarators:
                symbol_table[declarator.name] = var_type
                if getattr(declarator, 'initializer', None):
                    invocations.extend(self._find_method_invocations_recursive(declarator.initializer, symbol_table))
            # 변수 선언 자체는 호출이 아니므로 바로 반환
            return invocations

        elif isinstance(node, javalang.tree.Assignment):
            # 오른쪽 값을 먼저 분석하여 호출을 수집
            if hasattr(node, 'value'):
                invocations.extend(self._find_method_invocations_recursive(node.value, symbol_table))
            # 단순한 타입 추론 (new 연산자)
            if isinstance(node.expressionl, javalang.tree.MemberReference) and isinstance(getattr(node, 'value', None), javalang.tree.ClassCreator):
                var_name = node.expressionl.member
                var_type = self._get_type_string(node.value.type)
                symbol_table[var_name] = var_type
            return invocations

        # 노드의 자식들을 재귀적으로 검색
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                invocations.extend(self._find_method_invocations_recursive(child, symbol_table))
        elif isinstance(node, list):  # 리스트인 경우 각 요소를 순회
            for item in node:
                invocations.extend(self._find_method_invocations_recursive(item, symbol_table))
        elif hasattr(node, '__dict__'):  # 다른 속성들도 확인 (javalang AST 구조에 따라)
            for attr_value in node.__dict__.values():
                if isinstance(attr_value, (javalang.tree.Node, list)):
                    invocations.extend(self._find_method_invocations_recursive(attr_value, symbol_table))

        return invocations
    
    def _parse_with_tree_sitter(self, content: str):
        """
        Tree-sitter를 사용한 Java 코드 파싱
        
        Args:
            content: Java 소스 코드
            
        Returns:
            Tree-sitter AST
        """
        try:
            tree = self.tree_sitter_parser.parse(bytes(content, 'utf8'))
            return tree
        except Exception as e:
            if self.logger:
                self.logger.error("Tree-sitter 파싱 오류", exception=e)
            else:
                print(f"Tree-sitter 파싱 오류: {e}")
            return None
            
    def _extract_with_tree_sitter(self, tree, file_obj: File, content: str) -> Tuple[List[Class], List[Method], List[Edge]]:
        """
        Tree-sitter AST에서 클래스, 메서드, 엣지 정보 추출
        
        Args:
            tree: Tree-sitter AST
            file_obj: 파일 객체
            content: 원본 소스 코드
            
        Returns:
            (Classes, Methods, Edges) 튜플
        """
        classes = []
        methods = []
        edges = []
        
        if not tree or not tree.root_node:
            return classes, methods, edges
            
        # 코드를 라인별로 분할
        lines = content.split('\n')

        # 패키지명 추출
        pkg_nodes = self._find_nodes_by_type(tree.root_node, 'package_declaration')
        package_name = None
        if pkg_nodes:
            ids = self._find_nodes_by_type(pkg_nodes[0], 'scoped_identifier') or self._find_nodes_by_type(pkg_nodes[0], 'identifier')
            if ids:
                package_name = self._get_node_text(ids[0], lines)

        # 클래스 선언 찾기
        class_nodes = self._find_nodes_by_type(tree.root_node, 'class_declaration')
        for class_node in class_nodes:
            class_obj, class_methods, class_edges = self._extract_class_from_tree_sitter(
                class_node, file_obj, lines, package_name
            )
            if class_obj:
                classes.append(class_obj)
                methods.extend(class_methods)
                edges.extend(class_edges)
        
        # 인터페이스 선언 찾기
        interface_nodes = self._find_nodes_by_type(tree.root_node, 'interface_declaration')
        for interface_node in interface_nodes:
            interface_obj, interface_methods, interface_edges = self._extract_interface_from_tree_sitter(
                interface_node, file_obj, lines
            )
            if interface_obj:
                classes.append(interface_obj)
                methods.extend(interface_methods)
                edges.extend(interface_edges)
                
        # 열거형 선언 찾기
        enum_nodes = self._find_nodes_by_type(tree.root_node, 'enum_declaration')
        for enum_node in enum_nodes:
            enum_obj, enum_methods, enum_edges = self._extract_enum_from_tree_sitter(
                enum_node, file_obj, lines
            )
            if enum_obj:
                classes.append(enum_obj)
                methods.extend(enum_methods)
                edges.extend(enum_edges)
                
        return classes, methods, edges
        
    def _find_nodes_by_type(self, node, node_type: str):
        """
        주어진 타입의 노드들을 찾음
        
        Args:
            node: 검색할 루트 노드
            node_type: 찾을 노드 타입
            
        Returns:
            해당 타입의 노드 리스트
        """
        results = []
        
        if node.type == node_type:
            results.append(node)
            
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, node_type))
            
        return results
    
    def _extract_class_from_tree_sitter(self, class_node, file_obj: File, lines: List[str], package_name: Optional[str] = None) -> Tuple[Optional[Class], List[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 클래스 정보 추출
        """
        try:
            # 클래스 이름 추출
            name_node = None
            for child in class_node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
                    
            if not name_node:
                return None, [], []
                
            class_name = self._get_node_text(name_node, lines)
            
            # 위치 정보
            start_line = class_node.start_point[0] + 1  # 0-based to 1-based
            end_line = class_node.end_point[0] + 1
            
            # 클래스 객체 생성
            class_obj = Class(
                file_id=None,
                fqn=f"{package_name}.{class_name}" if package_name else class_name,
                name=class_name,
                start_line=start_line,
                end_line=end_line,
                modifiers=json.dumps(self._extract_modifiers(class_node, lines)),
                annotations=json.dumps(self._extract_annotations_ts(class_node, lines))
            )
            
            methods = []
            edges = []
            
            # 메서드 추출
            method_nodes = self._find_nodes_by_type(class_node, 'method_declaration')
            for method_node in method_nodes:
                method_obj, method_edges = self._extract_method_from_tree_sitter(
                    method_node, class_obj, lines
                )
                if method_obj:
                    methods.append(method_obj)
                    edges.extend(method_edges)
                    
            # 생성자 추출
            constructor_nodes = self._find_nodes_by_type(class_node, 'constructor_declaration')
            for constructor_node in constructor_nodes:
                constructor_obj, constructor_edges = self._extract_constructor_from_tree_sitter(
                    constructor_node, class_obj, lines
                )
                if constructor_obj:
                    methods.append(constructor_obj)
                    edges.extend(constructor_edges)
            
            return class_obj, methods, edges
            
        except Exception as e:
            logger.error(f"Failed to extract class from tree-sitter node: {e}")
            return None, [], []

    def _extract_class_from_tree_sitter_backup(self, class_node, file_obj: File, lines: List[str], package_name: Optional[str] = None) -> Tuple[Optional[Class], List[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 클래스 정보 추출
        """
        try:
            # 클래스 이름 추출
            name_node = None
            for child in class_node.children:
                if child.type == 'identifier':
                    name_node = child
                    break

            if not name_node:
                return None, [], []

            class_name = self._get_node_text(name_node, lines)

            # 위치 정보
            start_line = class_node.start_point[0] + 1  # 0-based to 1-based
            end_line = class_node.end_point[0] + 1

            # 클래스 객체 생성
            class_obj = Class(
                file_id=None,
                fqn=f"{package_name}.{class_name}" if package_name else class_name,
                name=class_name,
                start_line=start_line,
                end_line=end_line,
                modifiers=json.dumps(self._extract_modifiers(class_node, lines)),
                annotations=json.dumps(self._extract_annotations_ts(class_node, lines))
            )

            methods = []
            edges = []

            # 메서드 추출
            method_nodes = self._find_nodes_by_type(class_node, 'method_declaration')
            for method_node in method_nodes:
                method_obj, method_edges = self._extract_method_from_tree_sitter(
                    method_node, class_obj, lines
                )
                if method_obj:
                    methods.append(method_obj)
                    edges.extend(method_edges)

            # 생성자 추출
            constructor_nodes = self._find_nodes_by_type(class_node, 'constructor_declaration')
            for constructor_node in constructor_nodes:
                constructor_obj, constructor_edges = self._extract_constructor_from_tree_sitter(
                    constructor_node, class_obj, lines
                )
                if constructor_obj:
                    methods.append(constructor_obj)
                    edges.extend(constructor_edges)

            # 상속/구현 관계 추출
            kind = class_node.type
            if kind == 'class_declaration':
                superclass_nodes = [c for c in class_node.children if c.type == 'superclass']
                if superclass_nodes:
                    ids = self._find_nodes_by_type(superclass_nodes[0], 'type_identifier') or \
                          self._find_nodes_by_type(superclass_nodes[0], 'identifier')
                    if ids:
                        target = self._get_node_text(ids[0], lines)
                        edge = Edge(
                            src_type='class',
                            src_id=None,
                            dst_type='class',
                            dst_id=None,
                            edge_kind='extends',
                            confidence=0.9,
                            meta=json.dumps({'target': target})
                        )
                        setattr(edge, 'src_class_fqn', class_obj.fqn)
                        edges.append(edge)
                super_interfaces = [c for c in class_node.children if c.type == 'super_interfaces']
                for sinode in super_interfaces:
                    ids = self._find_nodes_by_type(sinode, 'type_identifier') or \
                          self._find_nodes_by_type(sinode, 'identifier')
                    for id_node in ids:
                        target = self._get_node_text(id_node, lines)
                        edge = Edge(
                            src_type='class',
                            src_id=None,
                            dst_type='interface',
                            dst_id=None,
                            edge_kind='implements',
                            confidence=0.9,
                            meta=json.dumps({'target': target})
                        )
                        setattr(edge, 'src_class_fqn', class_obj.fqn)
                        edges.append(edge)
            elif kind == 'interface_declaration':
                extends_nodes = [c for c in class_node.children if c.type == 'extends_interfaces']
                for enode in extends_nodes:
                    ids = self._find_nodes_by_type(enode, 'type_identifier') or \
                          self._find_nodes_by_type(enode, 'identifier')
                    for id_node in ids:
                        target = self._get_node_text(id_node, lines)
                        edge = Edge(
                            src_type='interface',
                            src_id=None,
                            dst_type='interface',
                            dst_id=None,
                            edge_kind='extends',
                            confidence=0.9,
                            meta=json.dumps({'target': target})
                        )
                        setattr(edge, 'src_class_fqn', class_obj.fqn)
                        edges.append(edge)

            return class_obj, methods, edges

        except Exception as e:
            if self.logger:
                self.logger.error("Tree-sitter 클래스 추출 오류", exception=e)
            else:
                print(f"Tree-sitter 클래스 추출 오류: {e}")
            return None, [], []

    def _extract_interface_from_tree_sitter(self, interface_node, file_obj: File, lines: List[str], package_name: Optional[str] = None) -> Tuple[Optional[Class], List[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 인터페이스 정보 추출
        """
        # 인터페이스도 클래스와 비슷한 방식으로 처리
        return self._extract_class_from_tree_sitter(interface_node, file_obj, lines, package_name)

    def _extract_enum_from_tree_sitter(self, enum_node, file_obj: File, lines: List[str], package_name: Optional[str] = None) -> Tuple[Optional[Class], List[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 열거형 정보 추출
        """
        # 열거형도 클래스와 비슷한 방식으로 처리
        return self._extract_class_from_tree_sitter(enum_node, file_obj, lines, package_name)
        
    def _extract_method_from_tree_sitter(self, method_node, class_obj: Class, lines: List[str]) -> Tuple[Optional[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 메서드 정보 추출
        """
        try:
            # 메서드 이름 추출
            name_node = None
            for child in method_node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
                    
            if not name_node:
                return None, []
                
            method_name = self._get_node_text(name_node, lines)
            
            # 위치 정보
            start_line = method_node.start_point[0] + 1
            end_line = method_node.end_point[0] + 1
            
            # 반환 타입 및 파라미터 시그니처 추출
            ret_nodes = [c for c in method_node.children if c.type == 'type']
            return_type = self._get_node_text(ret_nodes[0], lines) if ret_nodes else 'void'
            params = []
            for plist in [c for c in method_node.children if c.type == 'formal_parameters']:
                for p in self._find_nodes_by_type(plist, 'formal_parameter'):
                    tnode = self._find_nodes_by_type(p, 'type')
                    pname = self._find_nodes_by_type(p, 'identifier')
                    if tnode and pname:
                        params.append(f"{self._get_node_text(tnode[0], lines)} {self._get_node_text(pname[0], lines)}")
            signature = f"{method_name}({', '.join(params)})"

            # 메서드 객체 생성
            method_obj = Method(
                class_id=None,  # 나중에 설정
                name=method_name,
                signature=signature,
                start_line=start_line,
                end_line=end_line,
                return_type=return_type,
                parameters='',
                modifiers=json.dumps([])
            )
            try:
                setattr(method_obj, 'owner_fqn', class_obj.fqn)
            except Exception:
                pass
            
            edges = []
            # 메서드 호출 관계 추출도 가능하지만 복잡하므로 생략
            
            return method_obj, edges
            
        except Exception as e:
            if self.logger:
                self.logger.error("Tree-sitter 메서드 추출 오류", exception=e)
            else:
                print(f"Tree-sitter 메서드 추출 오류: {e}")
            return None, []

    def _extract_modifiers(self, node, lines: List[str]) -> List[str]:
        mods: List[str] = []
        # Tree-sitter 자바 grammar에 맞춰 modifiers 노드 탐색
        for child in getattr(node, 'children', []):
            if child.type == 'modifiers':
                for m in getattr(child, 'children', []):
                    try:
                        mods.append(self._get_node_text(m, lines))
                    except Exception:
                        continue
        return mods

    def _extract_annotations_ts(self, node, lines: List[str]) -> List[str]:
        anns: List[str] = []
        for a in self._find_nodes_by_type(node, 'annotation'):
            try:
                anns.append(self._get_node_text(a, lines))
            except Exception:
                continue
        return anns
            
    def _extract_constructor_from_tree_sitter(self, constructor_node, class_obj: Class, lines: List[str]) -> Tuple[Optional[Method], List[Edge]]:
        """
        Tree-sitter 노드에서 생성자 정보 추출
        """
        # 생성자도 메서드와 비슷한 방식으로 처리
        return self._extract_method_from_tree_sitter(constructor_node, class_obj, lines)
        
    def _get_node_text(self, node, lines: List[str]) -> str:
        """
        Tree-sitter 노드의 텍스트 추출
        
        Args:
            node: Tree-sitter 노드
            lines: 소스 코드 라인 리스트
            
        Returns:
            노드의 텍스트
        """
        try:
            start_row, start_col = node.start_point
            end_row, end_col = node.end_point
            
            if start_row == end_row:
                return lines[start_row][start_col:end_col]
            else:
                # 여러 라인에 걸쳐있는 경우
                text_parts = []
                text_parts.append(lines[start_row][start_col:])
                for i in range(start_row + 1, end_row):
                    text_parts.append(lines[i])
                text_parts.append(lines[end_row][:end_col])
                return ''.join(text_parts)
        except (IndexError, TypeError):
            return 'unknown'
