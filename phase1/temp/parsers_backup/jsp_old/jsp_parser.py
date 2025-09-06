"""
JSP(JavaServer Pages) 파서
JSP 파일에서 JSP 태그, Java 코드, SQL 쿼리 등을 추출합니다.
재현율을 높이기 위해 다양한 패턴을 처리합니다.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from ..base_parser import BaseParser
from phase1.utils.table_alias_resolver import get_table_alias_resolver

class JSPParser(BaseParser):
    """JSP 전용 파서 - 재현율 우선"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # JSP 태그 패턴
        self.jsp_tags = {
            'directives': [
                re.compile(r'<%@\s*(\w+)\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<%@\s*(\w+)\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            ],
            'scriptlets': [
                re.compile(r'<%\s*(.*?)\s*%>', re.DOTALL),
                re.compile(r'<%\s*(.*?)\s*%>', re.DOTALL),
            ],
            'expressions': [
                re.compile(r'<%=([^%>]*)%>', re.DOTALL),
                re.compile(r'<%=([^%>]*)%>', re.DOTALL),
            ],
            'declarations': [
                re.compile(r'<%!\s*(.*?)\s*%>', re.DOTALL),
                re.compile(r'<%!\s*(.*?)\s*%>', re.DOTALL),
            ],
            'actions': [
                re.compile(r'<jsp:(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<jsp:(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'custom_tags': [
                re.compile(r'<(\w+):(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<(\w+):(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'html_tags': [
                re.compile(r'<(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ]
        }
        
        # JSP 지시자 패턴
        self.jsp_directives = {
            'page': re.compile(r'<%@\s*page\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            'include': re.compile(r'<%@\s*include\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            'taglib': re.compile(r'<%@\s*taglib\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            'tag': re.compile(r'<%@\s*tag\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            'attribute': re.compile(r'<%@\s*attribute\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
            'variable': re.compile(r'<%@\s*variable\s+([^%>]*?)%>', re.IGNORECASE | re.DOTALL),
        }
        
        # JSP 액션 태그 패턴
        self.jsp_actions = {
            'useBean': re.compile(r'<jsp:useBean\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'setProperty': re.compile(r'<jsp:setProperty\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'getProperty': re.compile(r'<jsp:getProperty\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'include': re.compile(r'<jsp:include\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'forward': re.compile(r'<jsp:forward\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'param': re.compile(r'<jsp:param\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'plugin': re.compile(r'<jsp:plugin\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'fallback': re.compile(r'<jsp:fallback\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
        }
        
        # Java 코드 패턴
        self.java_patterns = {
            'imports': re.compile(r'import\s+([^;]+);', re.IGNORECASE),
            'classes': re.compile(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)', re.IGNORECASE),
            'methods': re.compile(r'(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)', re.IGNORECASE),
            'variables': re.compile(r'(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)', re.IGNORECASE),
            'sql_queries': [
                re.compile(r'"([^"]*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP)[^"]*)"', re.IGNORECASE),
                re.compile(r"'([^']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP)[^']*)'", re.IGNORECASE),
            ],
            'string_builder': [
                re.compile(r'StringBuilder\s+\w+\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'(\w+)\.append\s*\(([^)]*)\)', re.IGNORECASE),
            ]
        }
        
        # JSTL 태그 패턴
        self.jstl_patterns = {
            'core': [
                re.compile(r'<c:(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<c:(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'fmt': [
                re.compile(r'<fmt:(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<fmt:(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'sql': [
                re.compile(r'<sql:(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<sql:(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'xml': [
                re.compile(r'<x:(\w+)\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<x:(\w+)\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ]
        }
    
    def _get_parser_type(self) -> str:
        return 'jsp'
    
    def parse_file(self, file_path: str, project_id: int) -> Tuple['File', List[Any], List[Any], List[Any], List[Any], List[Any]]:
        """
        JSP 파일을 파싱하여 메타데이터를 추출합니다.
        
        Args:
            file_path: JSP 파일 경로
            project_id: 프로젝트 ID
            
        Returns:
            (File, List[SqlUnit], List[Join], List[Filter], List[Edge], List[Vulnerability]) 튜플
        """
        try:
            # 파일 내용 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # File 객체 생성
            file_obj = self._create_file_object(file_path, project_id, content)
            
            # JSP 파싱
            parsed_data = self.parse_content(content, {'file_path': file_path})
            
            # SqlUnit, Join, Filter, Edge, Vulnerability 객체 생성
            sql_units = self._create_sql_units(parsed_data, file_path, project_id)
            joins = self._create_joins(parsed_data, file_path, project_id)
            filters = self._create_filters(parsed_data, file_path, project_id)
            edges = self._create_edges(parsed_data, file_path, project_id)
            vulnerabilities = self._create_vulnerabilities(parsed_data, file_path, project_id)
            
            return file_obj, sql_units, joins, filters, edges, vulnerabilities
            
        except Exception as e:
            print(f"Error parsing JSP file {file_path}: {e}")
            # 빈 결과 반환
            file_obj = self._create_file_object(file_path, project_id, "")
            return file_obj, [], [], [], [], []
    
    def _create_file_object(self, file_path: str, project_id: int, content: str) -> 'File':
        """File 객체를 생성합니다."""
        from phase1.models.database import File
        import hashlib
        import datetime
        
        file_path_obj = Path(file_path)
        
        # 파일 해시 계산
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # 라인 수 계산
        line_count = len(content.splitlines()) if content else 0
        
        # 수정 시간
        mtime = datetime.datetime.fromtimestamp(file_path_obj.stat().st_mtime)
        
        return File(
            path=file_path,
            project_id=project_id,
            language='jsp',
            hash=file_hash,
            loc=line_count,
            mtime=mtime
        )
    
    def _create_sql_units(self, parsed_data: Dict[str, Any], file_path: str, project_id: int) -> List[Any]:
        """SQL Unit 객체들을 생성합니다."""
        from phase1.models.database import SqlUnit
        
        sql_units = []
        sql_queries = parsed_data.get('sql_queries', [])
        
        for i, query in enumerate(sql_queries):
            sql_unit = SqlUnit(
                file_id=None,  # 나중에 설정
                origin='jsp',
                mapper_ns=Path(file_path).stem,
                stmt_id=f'jsp_sql_{i}',
                start_line=1,  # TODO: 정확한 라인 수 계산
                end_line=1,
                stmt_kind=query.get('query_type', 'UNKNOWN'),
                normalized_fingerprint=self._create_sql_fingerprint(query.get('sql', ''))
            )
            sql_units.append(sql_unit)
        
        return sql_units
    
    def _create_joins(self, parsed_data: Dict[str, Any], file_path: str, project_id: int) -> List[Any]:
        """Join 객체들을 생성합니다."""
        # JSP에서는 직접적인 조인 정보가 없으므로 빈 리스트 반환
        return []
    
    def _create_filters(self, parsed_data: Dict[str, Any], file_path: str, project_id: int) -> List[Any]:
        """Filter 객체들을 생성합니다."""
        # JSP에서는 직접적인 필터 정보가 없으므로 빈 리스트 반환
        return []
    
    def _create_edges(self, parsed_data: Dict[str, Any], file_path: str, project_id: int) -> List[Any]:
        """Edge 객체들을 생성합니다."""
        from phase1.models.database import Edge
        
        edges = []
        
        # JSP 액션에서 페이지 간 관계 추출
        jsp_actions = parsed_data.get('jsp_actions', [])
        for action in jsp_actions:
            if action.get('type') == 'include':
                page = action.get('page')
                if page:
                    edge = Edge(
                        project_id=project_id,
                        src_type='jsp',
                        src_id=None,  # 나중에 설정
                        dst_type='jsp',
                        dst_id=None,  # 나중에 설정
                        edge_kind='include',
                        confidence=0.9,
                        meta=f'{{"included_page": "{page}"}}'
                    )
                    edges.append(edge)
            elif action.get('type') == 'forward':
                page = action.get('page')
                if page:
                    edge = Edge(
                        project_id=project_id,
                        src_type='jsp',
                        src_id=None,  # 나중에 설정
                        dst_type='jsp',
                        dst_id=None,  # 나중에 설정
                        edge_kind='forward',
                        confidence=0.9,
                        meta=f'{{"forwarded_page": "{page}"}}'
                    )
                    edges.append(edge)
        
        return edges
    
    def _create_vulnerabilities(self, parsed_data: Dict[str, Any], file_path: str, project_id: int) -> List[Any]:
        """Vulnerability 객체들을 생성합니다."""
        # JSP에서는 취약점 검사가 없으므로 빈 리스트 반환
        return []
    
    def _create_sql_fingerprint(self, sql_content: str) -> str:
        """SQL 지문을 생성합니다."""
        import hashlib
        import re
        
        # SQL 정규화
        normalized_sql = re.sub(r'\s+', ' ', sql_content.upper().strip())
        normalized_sql = re.sub(r'\d+', 'N', normalized_sql)  # 숫자를 N으로 치환
        normalized_sql = re.sub(r"'[^']*'", "'S'", normalized_sql)  # 문자열을 'S'로 치환
        normalized_sql = re.sub(r'"[^"]*"', '"S"', normalized_sql)  # 문자열을 "S"로 치환
        
        # 해시 생성
        return hashlib.md5(normalized_sql.encode('utf-8')).hexdigest()
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSP 파일을 파싱하여 메타데이터 추출 (재현율 우선)
        
        Args:
            content: JSP 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        normalized_content = self._remove_comments(content)
        
        result = {
            'jsp_directives': self._extract_jsp_directives_aggressive(normalized_content),
            'jsp_actions': self._extract_jsp_actions_aggressive(normalized_content),
            'jsp_scriptlets': self._extract_jsp_scriptlets_aggressive(normalized_content),
            'jsp_expressions': self._extract_jsp_expressions_aggressive(normalized_content),
            'jsp_declarations': self._extract_jsp_declarations_aggressive(normalized_content),
            'jstl_tags': self._extract_jstl_tags_aggressive(normalized_content),
            'custom_tags': self._extract_custom_tags_aggressive(normalized_content),
            'html_tags': self._extract_html_tags_aggressive(normalized_content),
            'java_code': self._extract_java_code_aggressive(normalized_content),
            'sql_units': self._extract_sql_queries_aggressive(normalized_content),
            'file_metadata': {'default_schema': context.get('default_schema', 'DEFAULT')},
            'confidence': 0.9
        }
        
        return result
    
    def _extract_jsp_directives_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSP 지시자를 공격적으로 추출 (재현율 우선)"""
        directives = []
        
        # 1. page 지시자
        page_matches = self.jsp_directives['page'].finditer(content)
        for match in page_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'page',
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'page'
            })
        
        # 2. include 지시자
        include_matches = self.jsp_directives['include'].finditer(content)
        for match in include_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'include',
                'file': self._extract_jsp_attribute(attributes, 'file'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'include'
            })
        
        # 3. taglib 지시자
        taglib_matches = self.jsp_directives['taglib'].finditer(content)
        for match in taglib_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'taglib',
                'uri': self._extract_jsp_attribute(attributes, 'uri'),
                'prefix': self._extract_jsp_attribute(attributes, 'prefix'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'taglib'
            })
        
        # 4. tag 지시자
        tag_matches = self.jsp_directives['tag'].finditer(content)
        for match in tag_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'tag',
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'tag'
            })
        
        # 5. attribute 지시자
        attribute_matches = self.jsp_directives['attribute'].finditer(content)
        for match in attribute_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'attribute',
                'name': self._extract_jsp_attribute(attributes, 'name'),
                'required': self._extract_jsp_attribute(attributes, 'required'),
                'rtexprvalue': self._extract_jsp_attribute(attributes, 'rtexprvalue'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'attribute'
            })
        
        # 6. variable 지시자
        variable_matches = self.jsp_directives['variable'].finditer(content)
        for match in variable_matches:
            attributes = match.group(1)
            directives.append({
                'type': 'variable',
                'name': self._extract_jsp_attribute(attributes, 'name'),
                'variable-class': self._extract_jsp_attribute(attributes, 'variable-class'),
                'scope': self._extract_jsp_attribute(attributes, 'scope'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'directive_type': 'variable'
            })
        
        return directives
    
    def _extract_jsp_actions_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSP 액션 태그를 공격적으로 추출 (재현율 우선)"""
        actions = []
        
        # 1. useBean 액션
        use_bean_matches = self.jsp_actions['useBean'].finditer(content)
        for match in use_bean_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'useBean',
                'id': self._extract_jsp_attribute(attributes, 'id'),
                'class': self._extract_jsp_attribute(attributes, 'class'),
                'scope': self._extract_jsp_attribute(attributes, 'scope'),
                'beanName': self._extract_jsp_attribute(attributes, 'beanName'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'bean_creation'
            })
        
        # 2. setProperty 액션
        set_property_matches = self.jsp_actions['setProperty'].finditer(content)
        for match in set_property_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'setProperty',
                'name': self._extract_jsp_attribute(attributes, 'name'),
                'property': self._extract_jsp_attribute(attributes, 'property'),
                'value': self._extract_jsp_attribute(attributes, 'value'),
                'param': self._extract_jsp_attribute(attributes, 'param'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'property_setting'
            })
        
        # 3. getProperty 액션
        get_property_matches = self.jsp_actions['getProperty'].finditer(content)
        for match in get_property_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'getProperty',
                'name': self._extract_jsp_attribute(attributes, 'name'),
                'property': self._extract_jsp_attribute(attributes, 'property'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'property_getting'
            })
        
        # 4. include 액션
        include_matches = self.jsp_actions['include'].finditer(content)
        for match in include_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'include',
                'page': self._extract_jsp_attribute(attributes, 'page'),
                'flush': self._extract_jsp_attribute(attributes, 'flush'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'page_inclusion'
            })
        
        # 5. forward 액션
        forward_matches = self.jsp_actions['forward'].finditer(content)
        for match in forward_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'forward',
                'page': self._extract_jsp_attribute(attributes, 'page'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'page_forwarding'
            })
        
        # 6. param 액션
        param_matches = self.jsp_actions['param'].finditer(content)
        for match in param_matches:
            attributes = match.group(1)
            actions.append({
                'type': 'param',
                'name': self._extract_jsp_attribute(attributes, 'name'),
                'value': self._extract_jsp_attribute(attributes, 'value'),
                'attributes': self._parse_jsp_attributes(attributes),
                'full_text': match.group(0),
                'action_type': 'parameter_passing'
            })
        
        return actions
    
    def _extract_jsp_scriptlets_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSP 스크립틀릿을 공격적으로 추출 (재현율 우선)"""
        scriptlets = []
        
        for pattern in self.jsp_tags['scriptlets']:
            matches = pattern.finditer(content)
            for match in matches:
                scriptlet_content = match.group(1)
                
                scriptlets.append({
                    'content': scriptlet_content.strip(),
                    'full_text': match.group(0),
                    'type': 'scriptlet',
                    'java_code': self._extract_java_code_from_scriptlet(scriptlet_content)
                })
        
        return scriptlets
    
    def _extract_jsp_expressions_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSP 표현식을 공격적으로 추출 (재현율 우선)"""
        expressions = []
        
        for pattern in self.jsp_tags['expressions']:
            matches = pattern.finditer(content)
            for match in matches:
                expression_content = match.group(1)
                
                expressions.append({
                    'content': expression_content.strip(),
                    'full_text': match.group(0),
                    'type': 'expression',
                    'java_code': self._extract_java_code_from_expression(expression_content)
                })
        
        return expressions
    
    def _extract_jsp_declarations_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSP 선언을 공격적으로 추출 (재현율 우선)"""
        declarations = []
        
        for pattern in self.jsp_tags['declarations']:
            matches = pattern.finditer(content)
            for match in matches:
                declaration_content = match.group(1)
                
                declarations.append({
                    'content': declaration_content.strip(),
                    'full_text': match.group(0),
                    'type': 'declaration',
                    'java_code': self._extract_java_code_from_declaration(declaration_content)
                })
        
        return declarations
    
    def _extract_jstl_tags_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """JSTL 태그를 공격적으로 추출 (재현율 우선)"""
        jstl_tags = []
        
        # Core 태그
        for pattern in self.jstl_patterns['core']:
            matches = pattern.finditer(content)
            for match in matches:
                tag_name = match.group(1)
                attributes = match.group(2)
                
                jstl_tags.append({
                    'library': 'core',
                    'tag': tag_name,
                    'attributes': self._parse_jsp_attributes(attributes),
                    'full_text': match.group(0),
                    'type': 'jstl_core'
                })
        
        # Formatting 태그
        for pattern in self.jstl_patterns['fmt']:
            matches = pattern.finditer(content)
            for match in matches:
                tag_name = match.group(1)
                attributes = match.group(2)
                
                jstl_tags.append({
                    'library': 'fmt',
                    'tag': tag_name,
                    'attributes': self._parse_jsp_attributes(attributes),
                    'full_text': match.group(0),
                    'type': 'jstl_formatting'
                })
        
        # SQL 태그
        for pattern in self.jstl_patterns['sql']:
            matches = pattern.finditer(content)
            for match in matches:
                tag_name = match.group(1)
                attributes = match.group(2)
                
                jstl_tags.append({
                    'library': 'sql',
                    'tag': tag_name,
                    'attributes': self._parse_jsp_attributes(attributes),
                    'full_text': match.group(0),
                    'type': 'jstl_sql'
                })
        
        # XML 태그
        for pattern in self.jstl_patterns['xml']:
            matches = pattern.finditer(content)
            for match in matches:
                tag_name = match.group(1)
                attributes = match.group(2)
                
                jstl_tags.append({
                    'library': 'xml',
                    'tag': tag_name,
                    'attributes': self._parse_jsp_attributes(attributes),
                    'full_text': match.group(0),
                    'type': 'jstl_xml'
                })
        
        return jstl_tags
    
    def _extract_custom_tags_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """커스텀 태그를 공격적으로 추출 (재현율 우선)"""
        custom_tags = []
        
        for pattern in self.jsp_tags['custom_tags']:
            matches = pattern.finditer(content)
            for match in matches:
                prefix = match.group(1)
                tag_name = match.group(2)
                attributes = match.group(3)
                
                custom_tags.append({
                    'prefix': prefix,
                    'tag': tag_name,
                    'attributes': self._parse_jsp_attributes(attributes),
                    'full_text': match.group(0),
                    'type': 'custom_tag'
                })
        
        return custom_tags
    
    def _extract_html_tags_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """HTML 태그를 공격적으로 추출 (재현율 우선)"""
        html_tags = []
        
        for pattern in self.jsp_tags['html_tags']:
            matches = pattern.finditer(content)
            for match in matches:
                tag_name = match.group(1)
                attributes = match.group(2)
                
                # JSP 관련 태그는 제외
                if not tag_name.lower().startswith(('jsp:', 'c:', 'fmt:', 'sql:', 'x:')):
                    html_tags.append({
                        'tag': tag_name,
                        'attributes': self._parse_jsp_attributes(attributes),
                        'full_text': match.group(0),
                        'type': 'html_tag'
                    })
        
        return html_tags
    
    def _extract_java_code_aggressive(self, content: str) -> Dict[str, List[str]]:
        """Java 코드를 공격적으로 추출 (재현율 우선)"""
        java_code = {
            'imports': [],
            'classes': [],
            'methods': [],
            'variables': []
        }
        
        # 1. import 문 추출
        import_matches = self.java_patterns['imports'].finditer(content)
        for match in import_matches:
            import_statement = match.group(1).strip()
            java_code['imports'].append(import_statement)
        
        # 2. 클래스 선언 추출
        class_matches = self.java_patterns['classes'].finditer(content)
        for match in class_matches:
            class_name = match.group(1)
            java_code['classes'].append(class_name)
        
        # 3. 메서드 선언 추출
        method_matches = self.java_patterns['methods'].finditer(content)
        for match in method_matches:
            return_type = match.group(1)
            method_name = match.group(2)
            parameters = match.group(3)
            java_code['methods'].append(f"{return_type} {method_name}({parameters})")
        
        # 4. 변수 선언 추출
        variable_matches = self.java_patterns['variables'].finditer(content)
        for match in variable_matches:
            variable_type = match.group(1)
            variable_name = match.group(2)
            java_code['variables'].append(f"{variable_type} {variable_name}")
        
        return java_code
    
    def _extract_sql_queries_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """SQL 쿼리를 공격적으로 추출 (재현율 우선)"""
        sql_queries = []
        
        # 1. 문자열 리터럴에서 SQL 추출
        for pattern in self.java_patterns['sql_queries']:
            matches = pattern.finditer(content)
            for match in matches:
                sql_content = match.group(1)
                sql_queries.append({
                    'sql': sql_content,
                    'type': 'string_literal',
                    'full_text': match.group(0),
                    'query_type': self._detect_sql_type(sql_content)
                })
        
        # 2. StringBuilder에서 SQL 추출
        for pattern in self.java_patterns['string_builder']:
            matches = pattern.finditer(content)
            for match in matches:
                if len(match.groups()) >= 2:
                    builder_var = match.group(1)
                    append_content = match.group(2)
                    sql_queries.append({
                        'sql': append_content,
                        'type': 'string_builder',
                        'builder_variable': builder_var,
                        'full_text': match.group(0),
                        'query_type': self._detect_sql_type(append_content)
                    })
        
        return sql_queries
    
    def _extract_java_code_from_scriptlet(self, scriptlet_content: str) -> Dict[str, Any]:
        """스크립틀릿에서 Java 코드 추출"""
        return {
            'imports': self._extract_imports_from_content(scriptlet_content),
            'classes': self._extract_classes_from_content(scriptlet_content),
            'methods': self._extract_methods_from_content(scriptlet_content),
            'variables': self._extract_variables_from_content(scriptlet_content)
        }
    
    def _extract_java_code_from_expression(self, expression_content: str) -> Dict[str, Any]:
        """표현식에서 Java 코드 추출"""
        return {
            'method_calls': self._extract_method_calls_from_content(expression_content),
            'variable_references': self._extract_variable_references_from_content(expression_content)
        }
    
    def _extract_java_code_from_declaration(self, declaration_content: str) -> Dict[str, Any]:
        """선언에서 Java 코드 추출"""
        return {
            'imports': self._extract_imports_from_content(declaration_content),
            'classes': self._extract_classes_from_content(declaration_content),
            'methods': self._extract_methods_from_content(declaration_content),
            'variables': self._extract_variables_from_content(declaration_content)
        }
    
    def _extract_imports_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 import 문 추출"""
        imports = []
        import_matches = self.java_patterns['imports'].finditer(content)
        for match in import_matches:
            imports.append(match.group(1).strip())
        return imports
    
    def _extract_classes_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 클래스 선언 추출"""
        classes = []
        class_matches = self.java_patterns['classes'].finditer(content)
        for match in class_matches:
            classes.append(match.group(1))
        return classes
    
    def _extract_methods_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 메서드 선언 추출"""
        methods = []
        method_matches = self.java_patterns['methods'].finditer(content)
        for match in method_matches:
            return_type = match.group(1)
            method_name = match.group(2)
            parameters = match.group(3)
            methods.append(f"{return_type} {method_name}({parameters})")
        return methods
    
    def _extract_variables_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 변수 선언 추출"""
        variables = []
        variable_matches = self.java_patterns['variables'].finditer(content)
        for match in variable_matches:
            variable_type = match.group(1)
            variable_name = match.group(2)
            variables.append(f"{variable_type} {variable_name}")
        return variables
    
    def _extract_method_calls_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 메서드 호출 추출"""
        method_calls = []
        # 메서드 호출 패턴: object.method() 또는 method()
        method_call_pattern = r'(\w+)\s*\.\s*(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(method_call_pattern, content)
        for match in matches:
            object_name = match.group(1)
            method_name = match.group(2)
            parameters = match.group(3)
            method_calls.append(f"{object_name}.{method_name}({parameters})")
        return method_calls
    
    def _extract_variable_references_from_content(self, content: str) -> List[str]:
        """컨텐츠에서 변수 참조 추출"""
        variable_refs = []
        # 변수 참조 패턴: 변수명
        variable_ref_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.finditer(variable_ref_pattern, content)
        for match in matches:
            variable_name = match.group(1)
            if not self._is_sql_keyword(variable_name):
                variable_refs.append(variable_name)
        return variable_refs
    
    def _extract_jsp_attribute(self, attributes: str, attr_name: str) -> str:
        """JSP 속성에서 특정 속성값 추출"""
        pattern = rf'{attr_name}\s*=\s*["\']([^"\']*)["\']'
        match = re.search(pattern, attributes, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_jsp_attributes(self, attr_string: str) -> Dict[str, str]:
        """JSP 속성 문자열을 파싱하여 딕셔너리로 변환"""
        attributes = {}
        
        if not attr_string.strip():
            return attributes
        
        # JSP 속성 패턴: name="value" 또는 name='value'
        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        attr_matches = re.finditer(attr_pattern, attr_string, re.IGNORECASE)
        
        for match in attr_matches:
            attr_name = match.group(1).lower()
            attr_value = match.group(2)
            attributes[attr_name] = attr_value
        
        return attributes
    
    def _detect_sql_type(self, sql_content: str) -> str:
        """SQL 타입 감지"""
        sql_upper = sql_content.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        else:
            return 'UNKNOWN'
    
    def _remove_comments(self, content: str) -> str:
        """JSP 관련 주석 제거"""
        # HTML 주석 제거
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # JSP 주석 제거
        content = re.sub(r'<%--.*?--%>', '', content, flags=re.DOTALL)
        return content
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'jsp'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)
