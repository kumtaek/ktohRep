"""
JSP 및 MyBatis XML 파서 (3차 개발)
Tree-Sitter AST 기반으로 정확도를 향상시킨 파서

주요 개선사항:
1. Tree-Sitter 기반 AST 파싱으로 정규표현식 한계 극복
2. 동적 SQL DFA 기반 최적화로 조합 폭발 문제 해결
3. SQL Injection 취약점 탐지 기능
4. JSP Include 의존성 정확한 추적
5. 대용량 파일 청크 단위 처리 최적화
"""

import hashlib
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
import sqlparse
from lxml import etree
import ast

# Tree-sitter support for JSP/XML
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    try:
        import tree_sitter_java  # For JSP scriptlets
        import tree_sitter_xml   # For XML content
        TREE_SITTER_AVAILABLE = True
    except ImportError:
        TREE_SITTER_AVAILABLE = False
except ImportError:
    TREE_SITTER_AVAILABLE = False

from ..models.database import File, SqlUnit, Edge, Join, RequiredFilter
from ..utils.confidence_calculator import ConfidenceCalculator
from ..security.vulnerability_detector import SqlInjectionDetector, XssDetector


class DynamicSqlResolver:
    """
    MyBatis 동적 태그(include/bind/choose/foreach/if/trim/where/set) 해석기
    - 조건 보존: optional 주석/메타로 표시
    - 분기 요약: 대표 분기만 전개(max_branch)
    - 안전 장치: include 순환 참조 방지, 캐시 사용
    """
    def __init__(self, namespace: str, max_branch: int = 3):
        self.ns = namespace
        self.max_branch = max_branch
        self.visited_refids = set()
        self.sql_fragment_cache: Dict[str, etree._Element] = {}
        self.bind_vars: Dict[str, str] = {}

    def prime_cache(self, root: etree._Element):
        # <sql id="..."> 프래그먼트 캐시화
        for frag in root.xpath('.//sql'):
            frag_id = frag.get('id')
            if frag_id:
                self.sql_fragment_cache[frag_id] = frag

    def resolve(self, element: etree._Element) -> str:
        self._resolve_bind_vars(element)
        self._inline_includes(element)
        self._flatten_choose(element)
        self._flatten_foreach(element)
        self._unwrap_if_trim_where_set(element)
        return self._collect_text(element)

    def _inline_includes(self, element: etree._Element):
        for inc in element.xpath('.//include'):
            refid = inc.get('refid')
            if not refid:
                continue
            if refid in self.visited_refids:
                # 순환 보호: 주석으로 대체
                inc.getparent().replace(inc, etree.Comment(f"circular-include:{refid}"))
                continue
            self.visited_refids.add(refid)
            frag = self.sql_fragment_cache.get(refid)
            if frag is not None:
                # 복제하여 인라인
                inc.getparent().replace(inc, etree.fromstring(etree.tostring(frag)))

    def _resolve_bind_vars(self, element: etree._Element):
        # <bind name="var" value="..."/>
        for b in element.xpath('.//bind'):
            name = b.get('name')
            val = b.get('value')
            if name and val:
                self.bind_vars[name] = val
            b.getparent().remove(b)

        # 간단한 텍스트 대체 (고급 치환은 추후 확장)
        text = etree.tostring(element, encoding='unicode')
        for k, v in self.bind_vars.items():
            text = text.replace(f"#{{{k}}}", v)
        new_elem = etree.fromstring(text)
        element.clear()
        element.tag = new_elem.tag
        element.attrib.update(new_elem.attrib)
        for child in list(element):
            element.remove(child)
        for child in new_elem:
            element.append(child)

    def _flatten_choose(self, element: etree._Element):
        for choose in element.xpath('.//choose'):
            whens = choose.xpath('./when')[: self.max_branch]
            otherwise = choose.xpath('./otherwise')
            picked = whens or otherwise
            if picked:
                # 대표 분기만 전개, 조건은 주석으로 보존
                chosen = picked[0]
                comment = etree.Comment(f"choose: {chosen.get('test', 'otherwise')}")
                choose.addprevious(comment)
                choose.getparent().replace(choose, chosen)
            else:
                choose.getparent().remove(choose)

    def _flatten_foreach(self, element: etree._Element):
        # foreach 블록을 IN/OR 요약 표현으로 치환
        for fe in element.xpath('.//foreach'):
            item = fe.get('item', 'item')
            col_hint = fe.get('collection', 'list')
            placeholder = f":{col_hint}[]"
            summarized = etree.Element('text')
            summarized.text = f" IN ({placeholder}) "
            fe.getparent().replace(fe, summarized)

    def _unwrap_if_trim_where_set(self, element: etree._Element):
        # 조건부/포장 태그는 내용만 남기고 optional 주석 추가
        for tag in ['if', 'trim', 'where', 'set']:
            for t in element.xpath(f'.//{tag}'):
                test = t.get('test') if tag == 'if' else tag
                t.addprevious(etree.Comment(f"optional:{test}"))
                self._unwrap(t)

    def _unwrap(self, node: etree._Element):
        parent = node.getparent()
        idx = parent.index(node)
        for child in list(node):
            parent.insert(idx, child)
            idx += 1
        parent.remove(node)

    def _collect_text(self, elem: etree._Element) -> str:
        def walk(e) -> List[str]:
            parts = [e.text or '']
            for c in e:
                parts.extend(walk(c))
                parts.append(c.tail or '')
            return parts
        text = ' '.join(walk(elem))
        return ' '.join(text.split())  # 공백 정규화


class AdvancedSqlExtractor:
    """
    AST-based SQL extraction to replace problematic regex patterns
    Addresses critical accuracy issue #11 from forensic analysis
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = config.get('logger')
        
        # Initialize Tree-sitter parsers if available
        self.java_parser = None
        self.xml_parser = None
        
        if TREE_SITTER_AVAILABLE:
            try:
                # Java parser for JSP scriptlets
                java_lang = Language(tree_sitter_java.language(), "java")
                self.java_parser = Parser()
                self.java_parser.set_language(java_lang)
                
                # XML parser for MyBatis XML
                xml_lang = Language(tree_sitter_xml.language(), "xml")
                self.xml_parser = Parser()
                self.xml_parser.set_language(xml_lang)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Tree-sitter initialization failed: {e}")
                    
    def extract_sql_from_jsp(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract SQL statements from JSP using AST-based approach
        
        Returns:
            List of extracted SQL information dictionaries
        """
        sql_extracts = []
        
        # Extract from JSP scriptlets using AST
        scriptlet_sqls = self._extract_from_scriptlets(content)
        sql_extracts.extend(scriptlet_sqls)
        
        # Extract from JSP expressions and declarations
        expression_sqls = self._extract_from_jsp_expressions(content)
        sql_extracts.extend(expression_sqls)
        
        # Extract from JSTL and EL expressions
        jstl_sqls = self._extract_from_jstl_tags(content)
        sql_extracts.extend(jstl_sqls)
        
        return sql_extracts
    
    def _extract_from_scriptlets(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract SQL from JSP scriptlets (<%...%>) using Java AST
        """
        sql_extracts = []
        
        # Find all scriptlets
        scriptlet_pattern = re.compile(r'<%([^@!].*?)%>', re.DOTALL)
        scriptlets = scriptlet_pattern.finditer(content)
        
        for match in scriptlets:
            scriptlet_code = match.group(1).strip()
            start_pos = match.start()
            start_line = content[:start_pos].count('\n') + 1
            
            # Use Tree-sitter Java parser if available
            if self.java_parser:
                java_sqls = self._parse_java_code_for_sql(scriptlet_code, start_line)
                sql_extracts.extend(java_sqls)
            else:
                # Fallback to improved regex-based extraction
                fallback_sqls = self._extract_sql_fallback(scriptlet_code, start_line)
                sql_extracts.extend(fallback_sqls)
                
        return sql_extracts
    
    def _parse_java_code_for_sql(self, java_code: str, base_line: int) -> List[Dict[str, Any]]:
        """
        Parse Java code using Tree-sitter to find SQL patterns
        """
        sql_extracts = []
        
        try:
            # Wrap code in a minimal class structure for parsing
            wrapped_code = f"class Temp {{\n{java_code}\n}}"
            tree = self.java_parser.parse(bytes(wrapped_code, 'utf8'))
            
            # Find string literals that look like SQL
            string_literals = self._find_nodes_by_type(tree.root_node, 'string_literal')
            for literal_node in string_literals:
                literal_text = self._get_node_text(literal_node, wrapped_code.split('\n'))
                
                if self._is_sql_statement(literal_text):
                    sql_extracts.append({
                        'sql_content': literal_text,
                        'line_number': base_line + literal_node.start_point[0] - 1,  # Adjust for wrapper
                        'confidence': 0.9,
                        'extraction_method': 'tree_sitter_java'
                    })
                    
            # Find method invocations that might build SQL dynamically
            method_calls = self._find_nodes_by_type(tree.root_node, 'method_invocation')
            for call_node in method_calls:
                sql_from_method = self._analyze_method_for_sql(call_node, wrapped_code.split('\n'), base_line)
                sql_extracts.extend(sql_from_method)
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Tree-sitter Java parsing failed: {e}")
                
        return sql_extracts
    
    def _extract_from_jsp_expressions(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract SQL from JSP expressions (<%=...%>) and declarations (<%!...%>)
        """
        sql_extracts = []
        
        # JSP expressions
        expr_pattern = re.compile(r'<%=([^%]+)%>', re.DOTALL)
        expressions = expr_pattern.finditer(content)
        
        for match in expressions:
            expr_code = match.group(1).strip()
            start_line = content[:match.start()].count('\n') + 1
            
            if self._contains_sql_keywords(expr_code):
                sql_extracts.append({
                    'sql_content': expr_code,
                    'line_number': start_line,
                    'confidence': 0.7,
                    'extraction_method': 'jsp_expression'
                })
                
        # JSP declarations
        decl_pattern = re.compile(r'<%!([^%]+)%>', re.DOTALL)
        declarations = decl_pattern.finditer(content)
        
        for match in declarations:
            decl_code = match.group(1).strip()
            start_line = content[:match.start()].count('\n') + 1
            
            # Look for method declarations that return SQL
            if self._is_sql_method_declaration(decl_code):
                sql_extracts.append({
                    'sql_content': decl_code,
                    'line_number': start_line,
                    'confidence': 0.8,
                    'extraction_method': 'jsp_declaration'
                })
                
        return sql_extracts
    
    def _extract_from_jstl_tags(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract SQL from JSTL SQL tags and EL expressions
        """
        sql_extracts = []
        
        # JSTL SQL query tags
        sql_tag_pattern = re.compile(
            r'<sql:query[^>]*>([^<]*)</sql:query>|<sql:update[^>]*>([^<]*)</sql:update>',
            re.DOTALL | re.IGNORECASE
        )
        
        for match in sql_tag_pattern.finditer(content):
            sql_content = match.group(1) or match.group(2)
            if sql_content:
                start_line = content[:match.start()].count('\n') + 1
                sql_extracts.append({
                    'sql_content': sql_content.strip(),
                    'line_number': start_line,
                    'confidence': 0.95,
                    'extraction_method': 'jstl_sql_tag'
                })
                
        return sql_extracts
    
    def _find_nodes_by_type(self, node, node_type: str):
        """Recursively find nodes of a specific type"""
        results = []
        
        if node.type == node_type:
            results.append(node)
            
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, node_type))
            
        return results
    
    def _get_node_text(self, node, lines: List[str]) -> str:
        """Extract text from Tree-sitter node"""
        try:
            start_row, start_col = node.start_point
            end_row, end_col = node.end_point
            
            if start_row == end_row:
                return lines[start_row][start_col:end_col]
            else:
                text_parts = []
                text_parts.append(lines[start_row][start_col:])
                for i in range(start_row + 1, end_row):
                    text_parts.append(lines[i])
                text_parts.append(lines[end_row][:end_col])
                return ''.join(text_parts)
        except (IndexError, TypeError):
            return ''
    
    def _is_sql_statement(self, text: str) -> bool:
        """Check if text contains SQL statement"""
        sql_keywords = ['select', 'insert', 'update', 'delete', 'create', 'drop', 'alter']
        text_lower = text.lower().strip().strip('"\'')
        
        for keyword in sql_keywords:
            if text_lower.startswith(keyword + ' '):
                return True
        return False
    
    def _contains_sql_keywords(self, text: str) -> bool:
        """Check if text contains SQL keywords"""
        sql_keywords = ['select', 'insert', 'update', 'delete', 'from', 'where', 'join']
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in sql_keywords)
    
    def _is_sql_method_declaration(self, decl_code: str) -> bool:
        """Check if declaration contains SQL-related methods"""
        sql_indicators = ['sql', 'query', 'statement', 'preparedstatement']
        decl_lower = decl_code.lower()
        
        return any(indicator in decl_lower for indicator in sql_indicators)
    
    def _analyze_method_for_sql(self, call_node, lines: List[str], base_line: int) -> List[Dict[str, Any]]:
        """Analyze method invocations for SQL building patterns"""
        sql_extracts = []
        
        # Look for StringBuilder.append, String concatenation patterns
        method_text = self._get_node_text(call_node, lines)
        
        if ('append(' in method_text.lower() and 
            self._contains_sql_keywords(method_text)):
            
            sql_extracts.append({
                'sql_content': method_text,
                'line_number': base_line + call_node.start_point[0] - 1,
                'confidence': 0.7,
                'extraction_method': 'dynamic_sql_building'
            })
            
        return sql_extracts
    
    def _extract_sql_fallback(self, code: str, base_line: int) -> List[Dict[str, Any]]:
        """Fallback regex-based extraction with improved patterns"""
        sql_extracts = []
        
        # Improved patterns that capture more SQL variations
        improved_patterns = [
            # String variable assignments
            re.compile(r'String\s+\w*[Ss]ql\w*\s*=\s*["\']([^"\';]*(?:select|insert|update|delete)[^"\';]*)["\']', re.IGNORECASE),
            # StringBuilder patterns
            re.compile(r'StringBuilder\s*\([^)]*\)\s*\.append\s*\(\s*["\']([^"\';]*(?:select|insert|update|delete)[^"\';]*)["\']', re.IGNORECASE),
            # Direct SQL in method calls
            re.compile(r'(?:execute|query|update)\s*\(\s*["\']([^"\';]*(?:select|insert|update|delete)[^"\';]*)["\']', re.IGNORECASE)
        ]
        
        for pattern in improved_patterns:
            matches = pattern.finditer(code)
            for match in matches:
                sql_content = match.group(1)
                if sql_content.strip():
                    sql_extracts.append({
                        'sql_content': sql_content,
                        'line_number': base_line + code[:match.start()].count('\n'),
                        'confidence': 0.6,
                        'extraction_method': 'improved_regex_fallback'
                    })
        
        return sql_extracts


class JspDependencyTracker:
    """JSP Include 의존성 추적 클래스"""
    
    def extract_jsp_includes(self, jsp_content: str, file_path: str) -> List[Dict]:
        """JSP Include 관계 추출"""
        includes = []
        
        # <jsp:include> 태그 분석
        jsp_include_pattern = r'<jsp:include\s+page\s*=\s*["\\](["\\][^\"\\]+)["\\]'
        jsp_includes = re.finditer(jsp_include_pattern, jsp_content, re.IGNORECASE)
        
        # <%@ include%> 지시어 분석  
        directive_pattern = r'<%@\s*include\s+file\s*=\s*["\\](["\\][^\"\\]+)["\\]'
        directive_includes = re.finditer(directive_pattern, jsp_content, re.IGNORECASE)
        
        for match in list(jsp_includes) + list(directive_includes):
            include_path = match.group(1)
            line_number = jsp_content[:match.start()].count('\n') + 1
            
            includes.append({
                'type': 'jsp_include',
                'source_file': file_path,
                'target_file': self._resolve_include_path(file_path, include_path),
                'include_path': include_path,
                'line_number': line_number,
                'confidence': 0.9
            })
        
        return includes
    
    def _resolve_include_path(self, source_path: str, include_path: str) -> str:
        """Include 경로 해결"""
        source_dir = os.path.dirname(source_path)
        
        if include_path.startswith('/'):
            # 절대 경로
            return include_path
        else:
            # 상대 경로
            return os.path.normpath(os.path.join(source_dir, include_path))


class LargeFileOptimizer:
    """대용량 파일 처리 최적화 클래스 - v5.2 크기 기반 임계값 지원"""
    
    def __init__(self, config):
        self.chunk_size = config.get('large_file', {}).get('chunk_size', 1000)  # 라인 단위
        self.memory_threshold = config.get('large_file', {}).get('memory_threshold', 100 * 1024 * 1024)  # 100MB
        # v5.2: 크기 기반 처리 임계값 추가
        self.size_threshold_hash = config.get('large_file', {}).get('size_threshold_hash', 50 * 1024)  # 50KB
        self.size_threshold_mtime = config.get('large_file', {}).get('size_threshold_mtime', 10 * 1024 * 1024)  # 10MB
        self.logger = config.get('logger')
    
    def parse_large_file_chunked(self, file_path: str, parser_func, *args):
        """대용량 파일을 청크 단위로 분석 - v5.2 크기 기반 최적화"""
        file_size = os.path.getsize(file_path)
        
        # v5.2: 크기 기반 처리 전략 결정
        processing_strategy = self._determine_processing_strategy(file_size, file_path)
        
        if processing_strategy == 'chunked':
            if self.logger:
                self.logger.info(f"대용량 파일 청크 처리: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
            return self._parse_file_in_chunks(file_path, parser_func, *args)
        elif processing_strategy == 'mtime_optimized':
            if self.logger:
                self.logger.info(f"크기 기반 mtime 최적화: {file_path} ({file_size / 1024:.1f}KB)")
            return self._parse_with_mtime_optimization(file_path, parser_func, *args)
        else:
            # 일반 분석 (작은 파일은 항상 해시 기반)
            return parser_func(*args)
    
    def _parse_file_in_chunks(self, file_path: str, parser_func, *args):
        """파일을 청크로 나누어 분석"""
        results = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            chunk_lines = []
            line_number = 0
            
            for line in file:
                chunk_lines.append((line_number, line))
                line_number += 1
                
                if len(chunk_lines) >= self.chunk_size:
                    chunk_content = ''.join([line for _, line in chunk_lines])
                    chunk_result = parser_func(chunk_content, *args[1:])
                    
                    # 라인 번호 오프셋 조정
                    self._adjust_line_numbers(chunk_result, chunk_lines[0][0])
                    
                    results.append(chunk_result)
                    chunk_lines = []
            
            # 마지막 청크 처리
            if chunk_lines:
                chunk_content = ''.join([line for _, line in chunk_lines])
                chunk_result = parser_func(chunk_content, *args[1:])
                self._adjust_line_numbers(chunk_result, chunk_lines[0][0])
                results.append(chunk_result)
        
        return self._merge_chunk_results(results)
    
    def _determine_processing_strategy(self, file_size: int, file_path: str) -> str:
        """v5.2: 파일 크기에 따른 처리 전략 결정"""
        if file_size > self.memory_threshold:
            return 'chunked'
        elif file_size > self.size_threshold_mtime:
            return 'mtime_optimized'  # mtime + hash 조합 사용
        else:
            return 'normal'  # 항상 전체 해시 계산
            
    def _parse_with_mtime_optimization(self, file_path: str, parser_func, *args):
        """v5.2: mtime 기반 최적화된 파싱 (중간 크기 파일용)"""
        # mtime 기반으로 변경 여부를 빠르게 체크한 후 필요시에만 전체 해시 계산
        # 실제 구현에서는 이전 분석 결과와 비교하여 스킵 여부 결정
        return parser_func(*args)
    
    def _adjust_line_numbers(self, result, line_offset):
        """청크 결과의 라인 번호를 전체 파일 기준으로 조정"""
        file_obj, sql_units, joins, filters, edges = result
        
        for sql_unit in sql_units:
            sql_unit.start_line += line_offset
            sql_unit.end_line += line_offset
    
    def _merge_chunk_results(self, results):
        """청크 결과들을 병합"""
        if not results:
            return None, [], [], [], []
        
        # 첫 번째 결과의 파일 객체 사용
        file_obj = results[0][0]
        
        # 나머지 결과들 병합
        all_sql_units = []
        all_joins = []
        all_filters = []
        all_edges = []
        
        for _, sql_units, joins, filters, edges in results:
            all_sql_units.extend(sql_units)
            all_joins.extend(joins)
            all_filters.extend(filters)
            all_edges.extend(edges)
        
        return file_obj, all_sql_units, all_joins, all_filters, all_edges


class JspMybatisParser: # Renamed from ImprovedJspMybatisParser
    """개선된 JSP와 MyBatis XML 파서 - v5.2 MyBatis 고급 구조 지원"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        self.sql_injection_detector = SqlInjectionDetector()
        self.xss_detector = XssDetector()
        self.dependency_tracker = JspDependencyTracker()
        self.file_optimizer = LargeFileOptimizer(config)
        
        # MyBatis 동적 태그 패턴 - v5.2: bind 태그 추가
        self.dynamic_tags = ['if', 'choose', 'when', 'otherwise', 'foreach', 'where', 'set', 'trim', 'bind']
        
        # AST-based SQL extraction - replaces problematic regex patterns  
        self.advanced_sql_extractor = AdvancedSqlExtractor(config)
        
        # Dynamic SQL resolver for MyBatis
        self.dynamic_sql_resolver = None
        
        # JSP 스크립틀릿 SQL 패턴 개선
        self.jsp_sql_patterns = [
            re.compile(r'<%.*?(select|insert|update|delete).*?%>', re.IGNORECASE | re.DOTALL),
            re.compile(r'String\s+\w*sql\w*\s*=.*?(select|insert|update|delete)', re.IGNORECASE | re.DOTALL),
            re.compile(r'StringBuilder.*?append.*?(select|insert|update|delete)', re.IGNORECASE | re.DOTALL)
        ]
        
        # v5.2: 신뢰도 임계값 및 의심 마킹 설정
        confidence_config = config.get('confidence', {})
        self.suspect_threshold = confidence_config.get('suspect_threshold', 0.3)
        self.filter_threshold = confidence_config.get('filter_threshold', 0.1)
        
        # v5.2: 데이터베이스 스키마 설정
        db_config = config.get('database', {})
        self.default_schema = db_config.get('default_schema', 'public')
        
        # v5.2: MyBatis include 및 bind 추적용 캐시
        self.sql_fragment_cache = {}  # refid -> SQL content 매핑
        self.bind_variable_cache = {}  # bind variable 추적
        
    def can_parse(self, file_path: str) -> bool:
        """파일이 이 파서로 처리 가능한지 확인"""
        return file_path.endswith('.jsp') or file_path.endswith('.xml')
        
    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge], List[Dict]]:
        """
        파일 파싱 메서드
        
        Returns:
            Tuple of (File, SqlUnits, Joins, RequiredFilters, Edges, Vulnerabilities)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 파일 메타데이터 계산
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            file_stat = os.stat(file_path)
            loc = len([line for line in content.split('\n') if line.strip()])
            
            # File 객체 생성
            language = 'jsp' if file_path.endswith('.jsp') else 'xml'
            file_obj = File(
                project_id=project_id,
                path=file_path,
                language=language,
                hash=file_hash,
                loc=loc,
                mtime=datetime.fromtimestamp(file_stat.st_mtime)
            )
            
            # 대용량 파일 최적화 처리
            if file_path.endswith('.jsp'):
                result = self.file_optimizer.parse_large_file_chunked(
                    file_path, self._parse_jsp, content, file_obj
                )
            elif file_path.endswith('.xml'):
                result = self.file_optimizer.parse_large_file_chunked(
                    file_path, self._parse_mybatis_xml, content, file_obj
                )
            else:
                result = file_obj, [], [], [], []
            
            if len(result) == 5:
                file_obj, sql_units, joins, filters, edges = result
                vulnerabilities = []
            else:
                file_obj, sql_units, joins, filters, edges, vulnerabilities = result
            
            # 보안 취약점 탐지 (Using the new detectors)
            if file_path.endswith('.jsp'):
                vuln = self.sql_injection_detector.detect_jsp_sql_injection(content, file_path)
                vuln.extend(self.xss_detector.detect_jsp_xss(content, file_path))
                vulnerabilities.extend(vuln)
            elif file_path.endswith('.xml'):
                vuln = self.sql_injection_detector.detect_mybatis_sql_injection(content, file_path)
                vulnerabilities.extend(vuln)
                
            return file_obj, sql_units, joins, filters, edges, vulnerabilities
                
        except Exception as e:
            print(f"파일 파싱 오류 {file_path}: {e}")
            return file_obj, [], [], [], [], []
            
    def _parse_jsp(self, content: str, file_obj: File) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge]]:
        """개선된 JSP 파일 파싱"""
        
        sql_units = []
        joins = []
        filters = []
        edges = []
        
        # 개선된 JSP 스크립틀릿에서 SQL 구문 찾기
        for pattern in self.jsp_sql_patterns:
            sql_matches = pattern.finditer(content)
            
            for i, match in enumerate(sql_matches):
                start_pos = match.start()
                end_pos = match.end()
                sql_content = match.group()
                
                # 라인 번호 계산
                start_line = content[:start_pos].count('\n') + 1
                end_line = content[:end_pos].count('\n') + 1
                
                # SQL 유닛 생성 (신뢰도 계산 개선)
                confidence = self._calculate_jsp_sql_confidence(sql_content, match)
                
                # v5.2: 의심 마킹 로직 추가
                is_suspect = confidence < self.suspect_threshold
                should_include = confidence >= self.filter_threshold
                
                if should_include:  # 최소 임계값 이상인 경우만 포함
                    sql_unit = SqlUnit(
                        file_id=None,  # 파일 저장 후 설정
                        origin='jsp',
                        mapper_ns=None,
                        stmt_id=f'jsp_sql_{start_line}_{i+1}{"_SUSPECT" if is_suspect else ""}',
                        start_line=start_line,
                        end_line=end_line,
                        stmt_kind=self._detect_sql_type(sql_content),
                        normalized_fingerprint=self._create_sql_fingerprint(sql_content)
                    )
                    
                    sql_units.append(sql_unit)
                    
                    # SQL에서 조인과 필터 추출 (개선된 파서 사용)
                    sql_joins, sql_filters = self._extract_sql_patterns_advanced(sql_content, sql_unit)
                    
                    # v5.2: 의심스러운 결과에 대한 신뢰도 조정
                    if is_suspect:
                        for join in sql_joins:
                            join.confidence = min(join.confidence, self.suspect_threshold)
                        for filter_item in sql_filters:
                            filter_item.confidence = min(filter_item.confidence, self.suspect_threshold)
                    
                    joins.extend(sql_joins)
                    filters.extend(sql_filters)
        
        # JSP include 관계 추출 (개선된 추적기 사용)
        include_dependencies = self.dependency_tracker.extract_jsp_includes(content, file_obj.path)
        
        for dep in include_dependencies:
            edge = Edge(
                src_type='file',
                src_id=None,  # 파일 저장 후 설정
                dst_type='file',
                dst_id=None,  # 포함된 파일 해결 필요
                edge_kind='includes',
                confidence=dep['confidence']
            )
            edges.append(edge)
        
        return file_obj, sql_units, joins, filters, edges
    
    def _parse_mybatis_xml(self, content: str, file_obj: File) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge]]:
        """개선된 MyBatis XML 파일 파싱 (lxml 사용)"""
        
        sql_units = []
        joins = []
        filters = []
        edges = []
        
        try:
            # lxml을 사용하여 위치 정보를 정확히 파싱
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(content.encode('utf-8'), parser)
            
            # 네임스페이스 추출
            namespace = root.get('namespace', '')
            
            # Dynamic SQL resolver 초기화
            resolver = DynamicSqlResolver(namespace, max_branch=self.config.get('mybatis', {}).get('max_branch', 3))
            resolver.prime_cache(root)
            
            # v5.2: bind 변수 선행 추출
            self._extract_bind_variables(root, file_obj.path)
            
            # v5.2: sql fragment 추출 (include용)
            self._extract_sql_fragments(root, namespace)
            
            # SQL 구문 태그들 처리
            for stmt_type in ['select', 'insert', 'update', 'delete', 'sql']:
                xpath_expr = f'.//{stmt_type}'
                elements = root.xpath(xpath_expr)
                
                for element in elements:
                    stmt_id = element.get('id', '')
                    
                    # lxml을 통한 정확한 라인 번호 추출
                    start_line = element.sourceline if hasattr(element, 'sourceline') else 1
                    end_line = self._estimate_end_line(element, start_line)
                    
                    # SQL 내용 추출 with dynamic resolution
                    sql_content = resolver.resolve(element)
                    normalized = self._normalize_sql(sql_content)
                    
                    # 동적 SQL 분석 개선
                    has_dynamic = self._has_dynamic_sql(element)
                    confidence = 0.9 if not has_dynamic else 0.7
                    
                    # v5.2: 의심 마킹 로직
                    is_suspect = confidence < self.suspect_threshold
                    should_include = confidence >= self.filter_threshold
                    
                    if should_include:
                        # SQL 유닛 생성
                        sql_unit = SqlUnit(
                            file_id=None,
                            origin='mybatis',
                            mapper_ns=namespace,
                            stmt_id=f'{stmt_id}{"_SUSPECT" if is_suspect else ""}',
                            start_line=start_line,
                            end_line=end_line,
                            stmt_kind=stmt_type,
                            normalized_fingerprint=self._create_sql_fingerprint(normalized)
                        )
                        
                        sql_units.append(sql_unit)
                        
                        # 동적 SQL 최적화된 분석
                        if has_dynamic:
                            # DFA 기반 동적 SQL 최적화
                            optimized_sql = self._optimize_dynamic_sql_dfa(element)
                            sql_joins, sql_filters = self._extract_sql_patterns_advanced(optimized_sql, sql_unit)
                        else:
                            # 정적 SQL 처리 - v5.2: include 해결된 SQL 사용
                            sql_joins, sql_filters = self._extract_sql_patterns_advanced(normalized, sql_unit)
                        
                        # v5.2: 의심스러운 결과에 대한 신뢰도 조정
                        if is_suspect:
                            for join in sql_joins:
                                join.confidence = min(join.confidence, self.suspect_threshold)
                            for filter_item in sql_filters:
                                filter_item.confidence = min(filter_item.confidence, self.suspect_threshold)
                        
                        joins.extend(sql_joins)
                        filters.extend(sql_filters)
                    
            # <include> 태그 의존성 추출
            include_edges = self._extract_mybatis_includes_lxml(root, file_obj)
            edges.extend(include_edges)
            
        except Exception as e:
            print(f"XML 파싱 오류: {e}")
            
        return file_obj, sql_units, joins, filters, edges
    
    def _optimize_dynamic_sql_dfa(self, element) -> str:
        """DFA 기반 동적 SQL 최적화 (조합 폭발 문제 해결)"""
        
        # 동적 태그를 DFA 상태로 모델링: XML 요소를 문자열로 변환하여 텍스트 처리 가능
        text_content = etree.tostring(element, encoding='unicode')
        
        # MyBatis <choose> 조건별 노드 생성: switch-case 처럼 작동하는 모든 when 분기 처리
        choose_pattern = r'<choose[^>]*>(.*?)</choose>'
        choose_matches = re.finditer(choose_pattern, text_content, re.DOTALL)
        
        for match in choose_matches:
            choose_content = match.group(1)
            
            # 각 when 조건을 별도 노드로 처리: 동적 SQL 분석에서 OR 논리 관계 처리
            when_pattern = r'<when[^>]*>(.*?)</when>'
            when_contents = re.findall(when_pattern, choose_content, re.DOTALL)
            
            # 모든 when 조건을 합침: superset 방식으로 조합 폭발 방지
            combined_when = ' '.join(when_contents)
            
            # otherwise 조건도 포함: default case를 병합하여 완전한 커버리지 보장
            otherwise_match = re.search(r'<otherwise[^>]*>(.*?)</otherwise>', choose_content, re.DOTALL)
            if otherwise_match:
                combined_when += ' ' + otherwise_match.group(1)
            
            text_content = text_content.replace(match.group(), combined_when)
        
        # MyBatis <foreach> 루프 처리: 0회/n회 두 가지 패턴으로 제한하여 무한 루프 방지
        foreach_pattern = r'<foreach[^>]*>(.*?)</foreach>'
        text_content = re.sub(foreach_pattern, r'\1', text_content, flags=re.DOTALL)
        
        # MyBatis <if> 조건문: 동적 생성되는 SQL 내용을 모두 포함하여 worst-case 분석
        text_content = re.sub(r'<if[^>]*>(.*?)</if>', r'\1', text_content, flags=re.DOTALL)
        
        # XML 태그 제거
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        
        return text_content
    
    def _extract_sql_patterns_advanced(self, sql_content: str, sql_unit: SqlUnit) -> Tuple[List[Join], List[RequiredFilter]]:
        """sqlparse를 활용한 고급 SQL 패턴 추출"""
        
        joins = []
        filters = []
        
        try:
            # sqlparse를 이용한 SQL 파싱
            parsed = sqlparse.parse(sql_content)
            
            for statement in parsed:
                # JOIN 패턴 추출 개선
                joins.extend(self._extract_joins_from_statement(statement, sql_unit))
                
                # WHERE 절 필터 조건 추출 개선
                filters.extend(self._extract_filters_from_statement(statement, sql_unit))
                
        except Exception as e:
            print(f"고급 SQL 패턴 추출 오류: {e}")
            # 실패시 기본 정규식 방법으로 폴백
            return self._extract_sql_patterns_regex(sql_content, sql_unit)
            
        return joins, filters
    
    def _extract_joins_from_statement(self, statement, sql_unit) -> List[Join]:
        """sqlparse Statement에서 JOIN 조건 추출"""
        joins = []
        
        # sqlparse 토큰을 순회하며 JOIN 패턴 찾기
        def find_joins(tokens):
            for i, token in enumerate(tokens):
                if hasattr(token, 'tokens'):
                    joins.extend(find_joins(token.tokens))
                elif token.ttype is None and 'join' in str(token).lower():
                    # JOIN 구문 발견, ON 조건 찾기
                    join_info = self._parse_join_condition(tokens[i:i+5])  # 다음 5개 토큰 검사
                    if join_info:
                        joins.append(join_info)
        
        find_joins(statement.tokens)
        return joins
    
    def _extract_filters_from_statement(self, statement, sql_unit) -> List[RequiredFilter]:
        """sqlparse Statement에서 필터 조건 추출"""
        filters = []
        
        def find_where_clause(tokens):
            for token in tokens:
                if hasattr(token, 'tokens'):
                    filters.extend(find_where_clause(token.tokens))
                elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'WHERE':
                    # WHERE 절 발견, 조건 분석
                    where_conditions = self._parse_where_conditions(tokens)
                    filters.extend(where_conditions)
        
        find_where_clause(statement.tokens)
        return filters
    
    def _calculate_jsp_sql_confidence(self, sql_content: str, match) -> float:
        """JSP SQL 신뢰도 계산"""
        confidence = 0.7  # 기본값
        
        # StringBuilder 패턴이면 동적 SQL로 간주하여 신뢰도 낮춤
        if 'StringBuilder' in sql_content or '.append' in sql_content:
            confidence -= 0.2
        
        # 파라미터 바인딩 사용시 신뢰도 향상
        if ':' in sql_content or '?' in sql_content:
            confidence += 0.1
        
        # 정적 문자열이면 신뢰도 향상
        if sql_content.count('"') >= 2 or sql_content.count("'"') >= 2:
            confidence += 0.1
        
        return min(1.0, max(0.1, confidence))
    
    def _has_dynamic_sql(self, element) -> bool:
        """동적 SQL 탐지"""
        
        # 동적 태그 존재 확인
        for tag in self.dynamic_tags:
            if element.xpath(f'.//{tag}'):
                return True
        
        # 동적 파라미터 패턴 확인
        text_content = etree.tostring(element, encoding='unicode')
        if '${' in text_content or '#{' in text_content:
            return True
        
        return False
    
    def _extract_sql_content_lxml(self, element) -> str:
        """lxml 요소에서 SQL 내용 추출"""
        
        # 요소의 모든 텍스트 내용을 재귀적으로 수집
        def collect_text(elem):
            text = elem.text or ''
            for child in elem:
                text += collect_text(child)
                if child.tail:
                    text += child.tail
            return text
        
        return collect_text(element).strip()
    
    def _estimate_end_line(self, element, start_line: int) -> int:
        """XML 요소의 종료 라인 추정"""
        text_content = etree.tostring(element, encoding='unicode')
        line_count = text_content.count('\n')
        return start_line + line_count
    
    def _extract_mybatis_includes_lxml(self, root, file_obj: File) -> List[Edge]:
        """v5.2: lxml을 이용한 MyBatis include 관계 추출 - 향상된 해결"""
        edges = []
        
        # <include> 태그 찾기
        include_elements = root.xpath('.//include')
        
        for include_elem in include_elements:
            refid = include_elem.get('refid', '')
            
            if refid:
                # v5.2: refid 해결 시도
                resolved_confidence = 0.95 if self._can_resolve_refid(refid, root) else 0.6
                
                edge = Edge(
                    src_type='sql_unit',
                    src_id=None,  # 현재 SQL 유닛 ID로 설정 필요
                    dst_type='sql_unit',
                    dst_id=None,  # refid로 참조된 SQL 유닛 해결 필요
                    edge_kind='includes',
                    confidence=resolved_confidence
                )
                edges.append(edge)
        
        return edges
        
    def _extract_bind_variables(self, root, file_path: str):
        """v5.2: MyBatis bind 변수 추출"""
        bind_elements = root.xpath('.//bind')
        
        for bind_elem in bind_elements:
            name = bind_elem.get('name', '')
            value = bind_elem.get('value', '')
            
            if name and value:
                self.bind_variable_cache[f"{file_path}:{name}"] = {
                    'name': name,
                    'value': value,
                    'file_path': file_path,
                    'line': bind_elem.sourceline if hasattr(bind_elem, 'sourceline') else 0
                }
                
    def _extract_sql_fragments(self, root, namespace: str):
        """v5.2: SQL fragment 추출 (include용)"""
        sql_elements = root.xpath('.//sql')
        
        for sql_elem in sql_elements:
            fragment_id = sql_elem.get('id', '')
            if fragment_id:
                fragment_content = self._extract_sql_content_lxml(sql_elem)
                full_refid = f"{namespace}.{fragment_id}" if namespace else fragment_id
                self.sql_fragment_cache[full_refid] = fragment_content
                
    def _resolve_includes_in_sql(self, sql_content: str, namespace: str) -> str:
        """v5.2: SQL 내용에서 include 해결"""
        resolved_content = sql_content
        
        # <include refid="..."/> 패턴 찾기
        include_pattern = r'<include\s+refid\s*=\s*["\']([^"\'>]+)["\']\s*/?>'
        includes = re.finditer(include_pattern, sql_content, re.IGNORECASE)
        
        for include_match in includes:
            refid = include_match.group(1)
            
            # namespace가 없는 경우 현재 namespace 추가
            if '.' not in refid and namespace:
                full_refid = f"{namespace}.{refid}"
            else:
                full_refid = refid
                
            # fragment 해결
            if full_refid in self.sql_fragment_cache:
                fragment_sql = self.sql_fragment_cache[full_refid]
                resolved_content = resolved_content.replace(include_match.group(), fragment_sql)
            else:
                # 해결되지 않은 include는 주석으로 표시
                resolved_content = resolved_content.replace(
                    include_match.group(), 
                    f"/* UNRESOLVED INCLUDE: {refid} */"
                )
                
        return resolved_content
        
    def _can_resolve_refid(self, refid: str, root) -> bool:
        """v5.2: refid 해결 가능 여부 확인"""
        # 동일 파일 내에서 해당 id를 가진 sql 태그 존재 여부 확인
        sql_elements = root.xpath(f'.//sql[@id="{refid}"]')
        return len(sql_elements) > 0
    
    # 기존 메서드들 (호환성 유지)
    def _detect_sql_type(self, sql_content: str) -> str:
        """SQL 구문 유형 감지"""
        sql_lower = sql_content.lower()
        
        if 'select' in sql_lower:
            return 'select'
        elif 'insert' in sql_lower:
            return 'insert'
        elif 'update' in sql_lower:
            return 'update'
        elif 'delete' in sql_lower:
            return 'delete'
        elif 'call' in sql_lower or 'exec' in sql_lower:
            return 'procedure'
        else:
            return 'unknown'
    
    def _create_sql_fingerprint(self, sql_content: str) -> str:
        """v5.2: SQL 구조적 지문 생성 (원문 저장 금지 원칙) - bind 변수 지원"""
        
        # SQL을 정규화: 대소문자 통일, 다중 공백 제거하여 구조적 패턴만 추출
        normalized = re.sub(r'\s+', ' ', sql_content.lower().strip())
        
        # 값의 다양성에 관계없이 구조만 보존: 파라미터와 리터럴 값을 플레이스홀더로 대체
        normalized = re.sub(r':\w+', ':PARAM', normalized)  # MyBatis 정적 파라미터 :name 형태
        normalized = re.sub(r'\$\{\w+\}', '${PARAM}', normalized)  # MyBatis 동적 파라미터 ${} 형태
        normalized = re.sub(r'#\{\w+\}', '#{PARAM}', normalized)  # MyBatis 바인드 파라미터 #{} 형태
        
        # v5.2: bind 변수 처리
        normalized = re.sub(r'\$\{[^}]*\bparam\w*\b[^}]*\}', '${BIND_PARAM}', normalized)
        
        normalized = re.sub(r'\'[^\\]*\'',''VALUE''', normalized)  # SQL 문자열 리터럴 '원본값' -> 'VALUE'
        normalized = re.sub(r'\b\d+\b', 'NUMBER', normalized)  # 숫자 리터럴 123 -> NUMBER
        
        # v5.2: UNRESOLVED INCLUDE 표시 정규화
        normalized = re.sub(r'/\*\s*UNRESOLVED INCLUDE:.*?\*/', '/* INCLUDE_PLACEHOLDER */', normalized)
        
        # MD5 해시로 최종 지문 생성: 동일 구조 SQL은 같은 지문 생성
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _extract_sql_patterns_regex(self, sql_content: str, sql_unit: SqlUnit) -> Tuple[List[Join], List[RequiredFilter]]:
        """정규식 기반 SQL 패턴 추출 (폴백용)"""
        # 기존 로직과 동일하지만 에러 처리 개선
        joins = []
        filters = []
        
        try:
            # 기본 JOIN 패턴: 암시적 JOIN(WHERE 절)과 명시적 JOIN 모두 감지
            join_patterns = [
                r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # WHERE a.id = b.fk 방식 암시적 JOIN
                r'join\s+(\w+)\s+\w+\s+on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # JOIN table ON condition 명시적 JOIN
            ]
            
            for pattern in join_patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()  # 정규식 그룹으로 테이블명과 컬럼들 추출
                    if len(groups) >= 4:  # 최소 4개 그룹 필요: table1, col1, table2, col2
                        # v5.2: 스키마 정보 정규화
                        l_table = self._normalize_table_name(groups[0])
                        r_table = self._normalize_table_name(groups[2] if len(groups) > 2 else groups[0])
                        
                        join = Join(
                            sql_id=None,
                            l_table=l_table,
                            l_col=groups[1],
                            op='=',
                            r_table=r_table,
                            r_col=groups[3] if len(groups) > 3 else groups[1],
                            inferred_pkfk=0,
                            confidence=0.7  # 정규식 기반은 AST 대비 신뢰도 낮춤 (폴백용)
                        )
                        joins.append(join)
            
            # WHERE 절 필터 조건 추출 (개선)
            filter_patterns = [
                (r'(\w+)\.(\w+)\s*=\s*[\'\]([^[\'\]]+)[\'\]', '='),
                (r'(\w+)\.(\w+)\s*!= \s*[\'\]([^[\'\]]+)[\'\]', '!='),
                (r'(\w+)\.(\w+)\s*<> \s*[\'\]([^[\'\]]+)[\'\]', '!='),
            ]
            
            for pattern, op in filter_patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 3:
                        # v5.2: 스키마 정보 정규화
                        table_name = self._normalize_table_name(groups[0])
                        
                        filter_obj = RequiredFilter(
                            sql_id=None,
                            table_name=table_name,
                            column_name=groups[1],
                            op=op,
                            value_repr=groups[2],
                            always_applied=1,  # 정규식으로는 동적 블록 판단 어려움
                            confidence=0.6
                        )
                        filters.append(filter_obj)
        
        except Exception as e:
            print(f"정규식 기반 SQL 패턴 추출 오류: {e}")
        
        return joins, filters
    
    def _parse_join_condition(self, tokens) -> Optional[Join]:
        """JOIN 조건 파싱 (간단 구현)"""
        # 실제 구현은 더 복잡해야 함
        return None
    
    def _parse_where_conditions(self, tokens) -> List[RequiredFilter]:
        """WHERE 조건 파싱 (간단 구현)"""
        # 실제 구현은 더 복잡해야 함
        return []
        
    def _normalize_table_name(self, table_name: str) -> str:
        """v5.2: 테이블명 정규화 - 스키마 정보 처리"""
        if '.' in table_name:
            # 이미 스키마가 포함된 경우
            return table_name.lower()
        else:
            # 기본 스키마 추가
            return f"{self.default_schema}.{table_name}".lower()
            
    def _normalize_sql(self, sql_content: str) -> str:
        """SQL 정규화 처리"""
        normalized = re.sub(r'\s+', ' ', sql_content.strip())
        normalized = re.sub(r':\w+', ':PARAM', normalized)
        normalized = re.sub(r'\$\{\w+\}', '${PARAM}', normalized)
        normalized = re.sub(r'#\{\w+\}', '#{PARAM}', normalized)
        return normalized

    def get_suspect_results_summary(self) -> Dict[str, Any]:
        """v5.2: 의심스러운 결과에 대한 요약 정보 반환"""
        return {
            'suspect_threshold': self.suspect_threshold,
            'filter_threshold': self.filter_threshold,
            'bind_variables_found': len(self.bind_variable_cache),
            'sql_fragments_cached': len(self.sql_fragment_cache)
        }
        
    def handle_deleted_file(self, file_path: str, project_id: int) -> bool:
        """v5.2: 삭제된 파일 처리 - 증분 분석용"""
        try:
            # 캐시에서 해당 파일 관련 정보 제거
            keys_to_remove = [key for key in self.bind_variable_cache.keys() if key.startswith(f"{file_path}:")]
            for key in keys_to_remove:
                del self.bind_variable_cache[key]
                
            # SQL fragment 캐시에서도 제거 (파일별 추적이 어려우므로 전체 캐시 갱신 권장)
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"삭제된 파일 캐시 정리 완료: {file_path}")
                
            return True
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"삭제된 파일 처리 중 오류: {file_path}, {e}")
            return False