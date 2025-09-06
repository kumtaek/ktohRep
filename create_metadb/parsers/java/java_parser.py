"""
Java 파서

Java 소스 코드를 파싱하여 클래스, 메서드, 필드 정보를 추출합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class JavaParser:
    """Java 파서"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"JavaParser")
        
        # Java 파싱 패턴들
        self.patterns = {
            'package': r'package\s+([^;]+);',
            'import': r'import\s+([^;]+);',
            'class': r'(?:public|private|protected)?\s*(?:abstract|final|static)?\s*class\s+(\w+)',
            'interface': r'(?:public|private|protected)?\s*interface\s+(\w+)',
            'method': r'(?:public|private|protected|static|final|abstract|synchronized)\s+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{',
            'field': r'(?:public|private|protected|static|final)\s+[\w<>\[\]]+\s+(\w+)\s*[=;]',
            'annotation': r'@(\w+)(?:\([^)]*\))?'
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Java 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path)
            
        except Exception as e:
            self.logger.error(f"Java 파일 파싱 실패 {file_path}: {e}")
            return {}
    
    def parse_content(self, content: str, file_path: str = '') -> Dict[str, Any]:
        """Java 코드 내용 파싱"""
        result = {
            'file_path': file_path,
            'package': self._extract_package(content),
            'imports': self._extract_imports(content),
            'classes': self._extract_classes(content),
            'interfaces': self._extract_interfaces(content),
            'methods': self._extract_methods(content),
            'fields': self._extract_fields(content),
            'annotations': self._extract_annotations(content)
        }
        
        return result
    
    def _extract_package(self, content: str) -> str:
        """패키지명 추출"""
        match = re.search(self.patterns['package'], content)
        return match.group(1) if match else ''
    
    def _extract_imports(self, content: str) -> List[str]:
        """Import 문 추출"""
        matches = re.findall(self.patterns['import'], content)
        return matches
    
    def _extract_classes(self, content: str) -> List[Dict]:
        """클래스 정보 추출"""
        classes = []
        matches = re.finditer(self.patterns['class'], content)
        
        for match in matches:
            class_name = match.group(1)
            class_info = {
                'name': class_name,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'modifiers': self._extract_modifiers(match.group(0))
            }
            classes.append(class_info)
        
        return classes
    
    def _extract_interfaces(self, content: str) -> List[Dict]:
        """인터페이스 정보 추출"""
        interfaces = []
        matches = re.finditer(self.patterns['interface'], content)
        
        for match in matches:
            interface_name = match.group(1)
            interface_info = {
                'name': interface_name,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'modifiers': self._extract_modifiers(match.group(0))
            }
            interfaces.append(interface_info)
        
        return interfaces
    
    def _extract_methods(self, content: str) -> List[Dict]:
        """메서드 정보 추출"""
        methods = []
        matches = re.finditer(self.patterns['method'], content, re.DOTALL)
        
        for match in matches:
            method_name = match.group(1)
            method_info = {
                'name': method_name,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'modifiers': self._extract_modifiers(match.group(0)),
                'parameters': self._extract_parameters(match.group(0)),
                'return_type': self._extract_return_type(match.group(0))
            }
            methods.append(method_info)
        
        return methods
    
    def _extract_fields(self, content: str) -> List[Dict]:
        """필드 정보 추출"""
        fields = []
        matches = re.finditer(self.patterns['field'], content)
        
        for match in matches:
            field_name = match.group(1)
            field_info = {
                'name': field_name,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'modifiers': self._extract_modifiers(match.group(0)),
                'type': self._extract_field_type(match.group(0))
            }
            fields.append(field_info)
        
        return fields
    
    def _extract_annotations(self, content: str) -> List[Dict]:
        """어노테이션 정보 추출"""
        annotations = []
        matches = re.finditer(self.patterns['annotation'], content)
        
        for match in matches:
            annotation_name = match.group(1)
            annotation_info = {
                'name': annotation_name,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'full_text': match.group(0)
            }
            annotations.append(annotation_info)
        
        return annotations
    
    def _extract_modifiers(self, declaration: str) -> List[str]:
        """접근 제어자 및 수식어 추출"""
        modifiers = []
        modifier_keywords = [
            'public', 'private', 'protected', 'static', 'final', 
            'abstract', 'synchronized', 'volatile', 'transient'
        ]
        
        for keyword in modifier_keywords:
            if keyword in declaration:
                modifiers.append(keyword)
        
        return modifiers
    
    def _extract_parameters(self, method_declaration: str) -> List[Dict]:
        """메서드 매개변수 추출"""
        parameters = []
        
        # 매개변수 부분 추출
        param_match = re.search(r'\(([^)]*)\)', method_declaration)
        if param_match:
            param_text = param_match.group(1).strip()
            if param_text:
                # 매개변수들을 쉼표로 분리
                param_list = [p.strip() for p in param_text.split(',')]
                
                for param in param_list:
                    if param:
                        # 타입과 변수명 분리
                        parts = param.split()
                        if len(parts) >= 2:
                            param_type = ' '.join(parts[:-1])
                            param_name = parts[-1]
                            
                            parameters.append({
                                'type': param_type,
                                'name': param_name
                            })
        
        return parameters
    
    def _extract_return_type(self, method_declaration: str) -> str:
        """메서드 반환 타입 추출"""
        # 메서드명 앞의 부분에서 반환 타입 추출
        parts = method_declaration.split()
        
        # 접근 제어자와 수식어 제거
        keywords_to_remove = [
            'public', 'private', 'protected', 'static', 'final', 
            'abstract', 'synchronized', 'volatile', 'transient'
        ]
        
        filtered_parts = [part for part in parts if part not in keywords_to_remove]
        
        # 메서드명과 괄호 제거
        if len(filtered_parts) >= 2:
            return ' '.join(filtered_parts[:-1])
        
        return 'void'
    
    def _extract_field_type(self, field_declaration: str) -> str:
        """필드 타입 추출"""
        # 필드명 앞의 부분에서 타입 추출
        parts = field_declaration.split()
        
        # 접근 제어자와 수식어 제거
        keywords_to_remove = [
            'public', 'private', 'protected', 'static', 'final', 
            'volatile', 'transient'
        ]
        
        filtered_parts = [part for part in parts if part not in keywords_to_remove]
        
        # 필드명과 할당 연산자 제거
        if len(filtered_parts) >= 2:
            return ' '.join(filtered_parts[:-1])
        
        return 'unknown'
