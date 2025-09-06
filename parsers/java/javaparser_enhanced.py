#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
향상된 Java 파서 (Context7 기반)
Java 코드 분석을 위한 고급 파싱 기능 제공
"""

import re
import os
import hashlib
from typing import Dict, List, Any, Set, Tuple, Optional
from pathlib import Path

from parsers.base_parser import BaseParser

class JavaParserEnhanced(BaseParser):
    """향상된 Java 파서 - Context7 기반"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        
        # Java 키워드
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
            'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
            'volatile', 'while', 'true', 'false', 'null'
        }
        
        # 신뢰도 설정
        self.confidence = 0.95

    def parse(self, content: str, file_path: str) -> Dict[str, Any]:
        """Java 파일 파싱"""
        try:
            result = {
                'file_path': file_path,
                'file_type': 'java',
                'classes': [],
                'methods': [],
                'imports': [],
                'annotations': [],
                'confidence': self.confidence
            }
            
            # 클래스 추출
            result['classes'] = self._extract_classes(content)
            
            # 메서드 추출
            result['methods'] = self._extract_methods(content)
            
            # Import 추출
            result['imports'] = self._extract_imports(content)
            
            # 어노테이션 추출
            result['annotations'] = self._extract_annotations(content)
            
            return result
            
        except Exception as e:
            return {
                'file_path': file_path,
                'file_type': 'java',
                'error': str(e),
                'confidence': 0.0
            }

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """클래스 추출"""
        classes = []
        
        # 클래스 정의 패턴
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            extends = match.group(2) if match.group(2) else None
            implements = match.group(3).strip() if match.group(3) else None
            
            # 클래스 위치 찾기
            start_pos = match.start()
            line_num = content[:start_pos].count('\n') + 1
            
            classes.append({
                'name': class_name,
                'extends': extends,
                'implements': implements,
                'start_line': line_num,
                'modifiers': self._extract_modifiers(match.group(0))
            })
        
        return classes

    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """메서드 추출 - 향상된 패턴 매칭"""
        methods = []
        
        # 다양한 메서드 패턴들
        method_patterns = [
            # 일반 메서드
            r'(?:public\s+|private\s+|protected\s+)?(?:static\s+|final\s+|abstract\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{',
            # 생성자
            r'(?:public\s+|private\s+|protected\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{',
            # void 메서드
            r'(?:public\s+|private\s+|protected\s+)?(?:static\s+|final\s+)?void\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{',
            # 인터페이스 메서드 (abstract)
            r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\([^)]*\)\s*;',
        ]
        
        for pattern in method_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                # 메서드 위치 찾기
                start_pos = match.start()
                line_num = content[:start_pos].count('\n') + 1
                
                # 패턴에 따라 메서드 정보 추출
                if 'void' in pattern:
                    # void 메서드
                    method_name = match.group(1)
                    return_type = 'void'
                elif 'abstract' in pattern and ';' in match.group(0):
                    # 인터페이스 메서드
                    return_type = match.group(1)
                    method_name = match.group(2)
                elif len(match.groups()) == 1:
                    # 생성자
                    method_name = match.group(1)
                    return_type = None
                else:
                    # 일반 메서드
                    return_type = match.group(1)
                    method_name = match.group(2)
                
                methods.append({
                    'name': method_name,
                    'return_type': return_type,
                    'start_line': line_num,
                    'modifiers': self._extract_modifiers(match.group(0)),
                    'is_constructor': return_type is None
                })
        
        return methods

    def _extract_imports(self, content: str) -> List[str]:
        """Import 문 추출"""
        imports = []
        
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1).strip())
        
        return imports

    def _extract_annotations(self, content: str) -> List[str]:
        """어노테이션 추출"""
        annotations = []
        
        annotation_pattern = r'@(\w+)(?:\([^)]*\))?'
        
        for match in re.finditer(annotation_pattern, content):
            annotations.append(match.group(1))
        
        return list(set(annotations))  # 중복 제거

    def _extract_modifiers(self, declaration: str) -> List[str]:
        """접근 제어자 및 수식어 추출"""
        modifiers = []
        
        modifier_keywords = ['public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized']
        
        for keyword in modifier_keywords:
            if keyword in declaration:
                modifiers.append(keyword)
        
        return modifiers

    def get_file_type(self) -> str:
        """파일 타입 반환"""
        return 'java'

    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 반환"""
        return ['.java']
