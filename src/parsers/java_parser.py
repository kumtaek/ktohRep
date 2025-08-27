"""
Java source code parser using JavaParser library.
Extracts classes, methods, annotations, and dependencies.
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
    # Fallback for environments without javalang
    javalang = None

from ..models.database import File, Class, Method, Edge
from ..utils.confidence_calculator import ConfidenceCalculator

class JavaParser:
    """Parser for Java source files using javalang library."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        
    def can_parse(self, file_path: str) -> bool:
        """Check if file can be parsed by this parser."""
        return file_path.endswith('.java') and javalang is not None
        
    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[Class], List[Method], List[Edge]]:
        """
        Parse a Java file and extract metadata.
        
        Args:
            file_path: Path to Java file
            project_id: Project ID from database
            
        Returns:
            Tuple of (File, Classes, Methods, Edges)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Calculate file metadata
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            file_stat = os.stat(file_path)
            loc = len([line for line in content.split('\n') if line.strip()])
            
            # Create File object
            file_obj = File(
                project_id=project_id,
                path=file_path,
                language='java',
                hash=file_hash,
                loc=loc,
                mtime=datetime.fromtimestamp(file_stat.st_mtime)
            )
            
            # Parse Java AST
            try:
                tree = javalang.parse.parse(content)
            except Exception as e:
                # If parsing fails, create file with low confidence
                print(f"Failed to parse {file_path}: {e}")
                return file_obj, [], [], []
                
            classes = []
            methods = []
            edges = []
            
            # Extract classes and methods
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_obj, class_methods, class_edges = self._extract_class(node, file_obj, path)
                classes.append(class_obj)
                methods.extend(class_methods)
                edges.extend(class_edges)
                
            # Extract interface declarations
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                interface_obj, interface_methods, interface_edges = self._extract_interface(node, file_obj, path)
                classes.append(interface_obj)
                methods.extend(interface_methods)
                edges.extend(interface_edges)
                
            # Extract enum declarations
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
        """Extract class information and its methods."""
        
        # Build fully qualified name
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        # Extract modifiers and annotations
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        # Estimate line numbers (javalang doesn't provide exact positions)
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
        """Extract interface information."""
        
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        start_line, end_line = self._estimate_line_numbers(node, file_obj)
        
        interface_obj = Class(  # Using Class table for interfaces too
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
        
        # Extract interface methods
        if hasattr(node, 'body') and node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, interface_obj)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                    
        return interface_obj, methods, edges
        
    def _extract_enum(self, node: javalang.tree.EnumDeclaration, file_obj: File, path: List) -> Tuple[Class, List[Method], List[Edge]]:
        """Extract enum information."""
        
        package_name = self._get_package_name(path)
        fqn = f"{package_name}.{node.name}" if package_name else node.name
        
        modifiers = [mod for mod in node.modifiers] if node.modifiers else []
        annotations = self._extract_annotations(node.annotations)
        
        start_line, end_line = self._estimate_line_numbers(node, file_obj)
        
        enum_obj = Class(  # Using Class table for enums too
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
        
        # Extract enum methods
        if hasattr(node, 'body') and node.body:
            for member in node.body.declarations if hasattr(node.body, 'declarations') else []:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_obj, method_edges = self._extract_method(member, enum_obj)
                    methods.append(method_obj)
                    edges.extend(method_edges)
                    
        return enum_obj, methods, edges
        
    def _extract_method(self, node: javalang.tree.MethodDeclaration, class_obj: Class) -> Tuple[Method, List[Edge]]:
        """Extract method information."""
        
        # Build method signature
        params = []
        if node.parameters:
            for param in node.parameters:
                param_type = self._get_type_string(param.type)
                params.append(f"{param_type} {param.name}")
        signature = f"{node.name}({', '.join(params)})"
        
        # Extract return type
        return_type = self._get_type_string(node.return_type) if node.return_type else 'void'
        
        # Extract annotations
        annotations = self._extract_annotations(node.annotations)
        
        # Estimate line numbers
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
        
        # Extract method calls from body
        if node.body:
            method_calls = self._extract_method_calls(node.body)
            for call in method_calls:
                call_edge = Edge(
                    src_type='method',
                    src_id=None,  # Will be set after method is saved
                    dst_type='method',
                    dst_id=None,  # Need to resolve later
                    edge_kind='call',
                    confidence=0.8  # Method calls are usually clear
                )
                edges.append(call_edge)
                
        return method_obj, edges
        
    def _extract_constructor(self, node: javalang.tree.ConstructorDeclaration, class_obj: Class) -> Tuple[Method, List[Edge]]:
        """Extract constructor information."""
        
        # Build constructor signature
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
            name=f"<init>",  # Constructor indicator
            signature=signature,
            return_type=class_obj.name,
            start_line=start_line,
            end_line=end_line,
            annotations=json.dumps(annotations)
        )
        
        edges = []
        
        # Extract method calls from constructor body
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
        """Extract package name from AST path."""
        for node in path:
            if isinstance(node, javalang.tree.CompilationUnit) and node.package:
                return node.package.name
        return None
        
    def _extract_annotations(self, annotations) -> List[Dict[str, Any]]:
        """Extract annotation information."""
        if not annotations:
            return []
            
        result = []
        for annotation in annotations:
            annotation_info = {
                'name': annotation.name,
                'element': None
            }
            
            if hasattr(annotation, 'element') and annotation.element:
                # Extract annotation parameters
                if isinstance(annotation.element, list):
                    annotation_info['element'] = [str(elem) for elem in annotation.element]
                else:
                    annotation_info['element'] = str(annotation.element)
                    
            result.append(annotation_info)
            
        return result
        
    def _get_type_string(self, type_node) -> str:
        """Convert type node to string representation."""
        if not type_node:
            return 'unknown'
            
        if hasattr(type_node, 'name'):
            return type_node.name
        elif hasattr(type_node, 'arguments') and type_node.arguments:
            # Generic type
            base_type = getattr(type_node, 'name', 'unknown')
            args = [self._get_type_string(arg) for arg in type_node.arguments]
            return f"{base_type}<{', '.join(args)}>"
        else:
            return str(type_node)
            
    def _estimate_line_numbers(self, node, file_obj: Optional[File]) -> Tuple[int, int]:
        """
        Estimate line numbers for AST nodes.
        Since javalang doesn't provide exact positions, this is a rough estimate.
        """
        # This is a placeholder - in real implementation you'd need
        # to track line numbers during parsing or use a different parser
        start_line = getattr(node, 'position', None)
        if start_line and hasattr(start_line, 'line'):
            start_line = start_line.line
        else:
            start_line = 1
            
        # Rough estimate for end line
        end_line = start_line + 10  # Default estimate
        
        return start_line, end_line
        
    def _extract_method_calls(self, body) -> List[str]:
        """Extract method calls from method body."""
        method_calls = []
        
        # This is a simplified implementation
        # In practice, you'd traverse the AST more thoroughly
        if hasattr(body, '__iter__'):
            for statement in body:
                if hasattr(statement, 'expression'):
                    calls = self._find_method_invocations(statement.expression)
                    method_calls.extend(calls)
                    
        return method_calls
        
    def _find_method_invocations(self, node) -> List[str]:
        """Find method invocation nodes in AST."""
        invocations = []
        
        if isinstance(node, javalang.tree.MethodInvocation):
            invocations.append(node.member)
            
        # Recursively search child nodes
        if hasattr(node, '__dict__'):
            for attr_value in node.__dict__.values():
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, '__dict__'):
                            invocations.extend(self._find_method_invocations(item))
                elif hasattr(attr_value, '__dict__'):
                    invocations.extend(self._find_method_invocations(attr_value))
                    
        return invocations