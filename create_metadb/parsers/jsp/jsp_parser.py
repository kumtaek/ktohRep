"""
JSP 파서

JSP 파일을 파싱하여 페이지 지시어, 액션 태그, 스크립트릿 정보를 추출합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class JspParser:
    """JSP 파서"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"JspParser")
        
        # JSP 파싱 패턴들
        self.patterns = {
            'page_directive': r'<%@\s+page[^%]*%>',
            'include_directive': r'<%@\s+include[^%]*%>',
            'taglib_directive': r'<%@\s+taglib[^%]*%>',
            'jsp_action': r'<jsp:[^>]*>',
            'custom_tag': r'<[a-zA-Z][^>]*>',
            'scriptlet': r'<%[^%]*%>',
            'expression': r'<%=.*?%>',
            'declaration': r'<%![^%]*%>',
            'comment': r'<%--.*?--%>',
            'html_comment': r'<!--.*?-->',
            'form': r'<form[^>]*>',
            'input': r'<input[^>]*>',
            'select': r'<select[^>]*>',
            'textarea': r'<textarea[^>]*>'
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """JSP 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path)
            
        except Exception as e:
            self.logger.error(f"JSP 파일 파싱 실패 {file_path}: {e}")
            return {}
    
    def parse_content(self, content: str, file_path: str = '') -> Dict[str, Any]:
        """JSP 코드 내용 파싱"""
        result = {
            'file_path': file_path,
            'page_directives': self._extract_page_directives(content),
            'include_directives': self._extract_include_directives(content),
            'taglib_directives': self._extract_taglib_directives(content),
            'jsp_actions': self._extract_jsp_actions(content),
            'custom_tags': self._extract_custom_tags(content),
            'scriptlets': self._extract_scriptlets(content),
            'expressions': self._extract_expressions(content),
            'declarations': self._extract_declarations(content),
            'forms': self._extract_forms(content),
            'inputs': self._extract_inputs(content),
            'java_imports': self._extract_java_imports(content),
            'java_classes': self._extract_java_classes(content)
        }
        
        return result
    
    def _extract_page_directives(self, content: str) -> List[Dict]:
        """페이지 지시어 추출"""
        directives = []
        matches = re.finditer(self.patterns['page_directive'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            directive_text = match.group(0)
            directive_info = {
                'content': directive_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'attributes': self._extract_directive_attributes(directive_text)
            }
            directives.append(directive_info)
        
        return directives
    
    def _extract_include_directives(self, content: str) -> List[Dict]:
        """Include 지시어 추출"""
        includes = []
        matches = re.finditer(self.patterns['include_directive'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            include_text = match.group(0)
            include_info = {
                'content': include_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'file_path': self._extract_include_file_path(include_text)
            }
            includes.append(include_info)
        
        return includes
    
    def _extract_taglib_directives(self, content: str) -> List[Dict]:
        """Taglib 지시어 추출"""
        taglibs = []
        matches = re.finditer(self.patterns['taglib_directive'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            taglib_text = match.group(0)
            taglib_info = {
                'content': taglib_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'attributes': self._extract_directive_attributes(taglib_text)
            }
            taglibs.append(taglib_info)
        
        return taglibs
    
    def _extract_jsp_actions(self, content: str) -> List[Dict]:
        """JSP 액션 태그 추출"""
        actions = []
        matches = re.finditer(self.patterns['jsp_action'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            action_text = match.group(0)
            action_info = {
                'content': action_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'action_type': self._extract_action_type(action_text),
                'attributes': self._extract_tag_attributes(action_text)
            }
            actions.append(action_info)
        
        return actions
    
    def _extract_custom_tags(self, content: str) -> List[Dict]:
        """커스텀 태그 추출"""
        custom_tags = []
        matches = re.finditer(self.patterns['custom_tag'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            tag_text = match.group(0)
            tag_info = {
                'content': tag_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'tag_name': self._extract_tag_name(tag_text),
                'attributes': self._extract_tag_attributes(tag_text)
            }
            custom_tags.append(tag_info)
        
        return custom_tags
    
    def _extract_scriptlets(self, content: str) -> List[Dict]:
        """스크립트릿 추출"""
        scriptlets = []
        matches = re.finditer(self.patterns['scriptlet'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            scriptlet_text = match.group(0)
            scriptlet_info = {
                'content': scriptlet_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'java_code': scriptlet_text[2:-2].strip()  # <% %> 제거
            }
            scriptlets.append(scriptlet_info)
        
        return scriptlets
    
    def _extract_expressions(self, content: str) -> List[Dict]:
        """표현식 추출"""
        expressions = []
        matches = re.finditer(self.patterns['expression'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            expression_text = match.group(0)
            expression_info = {
                'content': expression_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'expression': expression_text[3:-2].strip()  # <%= %> 제거
            }
            expressions.append(expression_info)
        
        return expressions
    
    def _extract_declarations(self, content: str) -> List[Dict]:
        """선언부 추출"""
        declarations = []
        matches = re.finditer(self.patterns['declaration'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            declaration_text = match.group(0)
            declaration_info = {
                'content': declaration_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'java_code': declaration_text[3:-2].strip()  # <%! %> 제거
            }
            declarations.append(declaration_info)
        
        return declarations
    
    def _extract_forms(self, content: str) -> List[Dict]:
        """폼 태그 추출"""
        forms = []
        matches = re.finditer(self.patterns['form'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            form_text = match.group(0)
            form_info = {
                'content': form_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'attributes': self._extract_tag_attributes(form_text)
            }
            forms.append(form_info)
        
        return forms
    
    def _extract_inputs(self, content: str) -> List[Dict]:
        """입력 필드 추출"""
        inputs = []
        matches = re.finditer(self.patterns['input'], content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            input_text = match.group(0)
            input_info = {
                'content': input_text,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'input_type': self._extract_input_type(input_text),
                'attributes': self._extract_tag_attributes(input_text)
            }
            inputs.append(input_info)
        
        return inputs
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Java import 문 추출"""
        imports = []
        
        # 스크립트릿과 선언부에서 import 문 찾기
        java_code_pattern = r'<%[!]?[^%]*%>'
        java_matches = re.finditer(java_code_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in java_matches:
            java_code = match.group(0)[2:-2].strip()  # <% %> 제거
            import_matches = re.findall(r'import\s+([^;]+);', java_code)
            imports.extend(import_matches)
        
        return list(set(imports))  # 중복 제거
    
    def _extract_java_classes(self, content: str) -> List[str]:
        """Java 클래스명 추출"""
        classes = []
        
        # 스크립트릿과 선언부에서 클래스명 찾기
        java_code_pattern = r'<%[!]?[^%]*%>'
        java_matches = re.finditer(java_code_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in java_matches:
            java_code = match.group(0)[2:-2].strip()  # <% %> 제거
            class_matches = re.findall(r'(\w+)\s+\w+\s*=', java_code)  # 변수 선언
            classes.extend(class_matches)
        
        return list(set(classes))  # 중복 제거
    
    def _extract_directive_attributes(self, directive_text: str) -> Dict[str, str]:
        """지시어 속성 추출"""
        attributes = {}
        
        # 속성 패턴: key="value" 또는 key='value'
        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        matches = re.finditer(attr_pattern, directive_text, re.IGNORECASE)
        
        for match in matches:
            key = match.group(1)
            value = match.group(2)
            attributes[key] = value
        
        return attributes
    
    def _extract_include_file_path(self, include_text: str) -> str:
        """Include 파일 경로 추출"""
        file_match = re.search(r'file\s*=\s*["\']([^"\']*)["\']', include_text, re.IGNORECASE)
        return file_match.group(1) if file_match else ''
    
    def _extract_action_type(self, action_text: str) -> str:
        """액션 타입 추출"""
        type_match = re.search(r'<jsp:(\w+)', action_text, re.IGNORECASE)
        return type_match.group(1) if type_match else 'unknown'
    
    def _extract_tag_name(self, tag_text: str) -> str:
        """태그명 추출"""
        name_match = re.search(r'<(\w+)', tag_text, re.IGNORECASE)
        return name_match.group(1) if name_match else 'unknown'
    
    def _extract_tag_attributes(self, tag_text: str) -> Dict[str, str]:
        """태그 속성 추출"""
        attributes = {}
        
        # 속성 패턴: key="value" 또는 key='value'
        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        matches = re.finditer(attr_pattern, tag_text, re.IGNORECASE)
        
        for match in matches:
            key = match.group(1)
            value = match.group(2)
            attributes[key] = value
        
        return attributes
    
    def _extract_input_type(self, input_text: str) -> str:
        """입력 필드 타입 추출"""
        type_match = re.search(r'type\s*=\s*["\']([^"\']*)["\']', input_text, re.IGNORECASE)
        return type_match.group(1) if type_match else 'text'
