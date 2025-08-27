"""
JSP and MyBatis XML parser
Handles JSP pages, JSTL tags, and MyBatis mapper XML files
"""

import os
import hashlib
import re
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class JSPParsingResult:
    """JSP 파싱 결과"""
    file_info: Dict
    includes: List[Dict]  # jsp:include, @include
    scriptlets: List[Dict]  # Java code in scriptlets
    el_expressions: List[Dict]  # EL expressions
    jstl_tags: List[Dict]  # JSTL tags
    dependencies: List[Dict]
    confidence: float


@dataclass
class MyBatisParsingResult:
    """MyBatis XML 파싱 결과"""
    file_info: Dict
    namespace: str
    statements: List[Dict]  # select, insert, update, delete
    sql_fragments: List[Dict]  # <sql> elements
    result_maps: List[Dict]  # <resultMap> elements
    dependencies: List[Dict]
    confidence: float


class JSPParser:
    """JSP 파일 파서"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_file_size_mb = self.config.get('max_file_size_mb', 10)
    
    def can_parse(self, file_path: str) -> bool:
        """파일 파싱 가능 여부 확인"""
        return file_path.endswith(('.jsp', '.jspx'))
    
    def calculate_file_hash(self, content: str) -> str:
        """파일 내용의 SHA-256 해시 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def count_lines(self, content: str) -> int:
        """코드 라인 수 계산"""
        return len([line for line in content.splitlines() if line.strip()])
    
    def extract_includes(self, content: str) -> List[Dict]:
        """JSP include 추출"""
        includes = []
        
        # jsp:include 태그 추출
        jsp_include_pattern = r'<jsp:include\s+page="([^"]+)"'
        for match in re.finditer(jsp_include_pattern, content, re.IGNORECASE):
            includes.append({
                'type': 'jsp:include',
                'target': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # @include 지시어 추출
        include_pattern = r'<%@\s*include\s+file="([^"]+)"'
        for match in re.finditer(include_pattern, content, re.IGNORECASE):
            includes.append({
                'type': '@include',
                'target': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return includes
    
    def extract_scriptlets(self, content: str) -> List[Dict]:
        """스크립틀릿 추출"""
        scriptlets = []
        
        # <% ... %> 스크립틀릿
        scriptlet_pattern = r'<%(?![@=!])(.*?)%>'
        for match in re.finditer(scriptlet_pattern, content, re.DOTALL):
            scriptlets.append({
                'type': 'scriptlet',
                'content': match.group(1).strip(),
                'start_line': content[:match.start()].count('\n') + 1,
                'end_line': content[:match.end()].count('\n') + 1
            })
        
        # <%= ... %> 표현식
        expression_pattern = r'<%=(.*?)%>'
        for match in re.finditer(expression_pattern, content, re.DOTALL):
            scriptlets.append({
                'type': 'expression',
                'content': match.group(1).strip(),
                'start_line': content[:match.start()].count('\n') + 1,
                'end_line': content[:match.end()].count('\n') + 1
            })
        
        return scriptlets
    
    def extract_el_expressions(self, content: str) -> List[Dict]:
        """EL 표현식 추출"""
        el_expressions = []
        
        # ${...} 표현식
        el_pattern = r'\$\{([^}]+)\}'
        for match in re.finditer(el_pattern, content):
            el_expressions.append({
                'type': 'el_expression',
                'content': match.group(1).strip(),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return el_expressions
    
    def extract_jstl_tags(self, content: str) -> List[Dict]:
        """JSTL 태그 추출"""
        jstl_tags = []
        
        # JSTL 태그 패턴 (c:, fmt:, sql:, xml: 등)
        jstl_pattern = r'<(c|fmt|sql|xml|fn):(\w+)([^>]*)/?>'
        for match in re.finditer(jstl_pattern, content, re.IGNORECASE):
            jstl_tags.append({
                'prefix': match.group(1),
                'tag_name': match.group(2),
                'attributes': match.group(3).strip(),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return jstl_tags
    
    def parse_file(self, file_path: str, project_id: int) -> JSPParsingResult:
        """JSP 파일 파싱"""
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 기본 파일 정보
            file_stat = os.stat(file_path)
            file_info = {
                'project_id': project_id,
                'path': os.path.relpath(file_path),
                'language': 'jsp',
                'hash': self.calculate_file_hash(content),
                'loc': self.count_lines(content),
                'mtime': datetime.fromtimestamp(file_stat.st_mtime)
            }
            
            # JSP 요소 추출
            includes = self.extract_includes(content)
            scriptlets = self.extract_scriptlets(content)
            el_expressions = self.extract_el_expressions(content)
            jstl_tags = self.extract_jstl_tags(content)
            
            # 의존성 정보
            dependencies = []
            for include in includes:
                dependencies.append({
                    'type': 'include',
                    'target': include['target'],
                    'line': include['line']
                })
            
            # 신뢰도 계산
            confidence = 0.8  # JSP는 비교적 간단한 구조
            if len(scriptlets) > 0 or len(el_expressions) > 0:
                confidence = 0.9
            
            return JSPParsingResult(
                file_info=file_info,
                includes=includes,
                scriptlets=scriptlets,
                el_expressions=el_expressions,
                jstl_tags=jstl_tags,
                dependencies=dependencies,
                confidence=confidence
            )
            
        except Exception as e:
            file_info['hash'] = 'error'
            file_info['loc'] = 0
            
            return JSPParsingResult(
                file_info=file_info,
                includes=[],
                scriptlets=[],
                el_expressions=[],
                jstl_tags=[],
                dependencies=[],
                confidence=0.0
            )


class MyBatisParser:
    """MyBatis XML 매퍼 파서"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.namespace_extraction = self.config.get('namespace_extraction', True)
        self.dynamic_sql_analysis = self.config.get('dynamic_sql_analysis', True)
    
    def can_parse(self, file_path: str) -> bool:
        """MyBatis XML 파일인지 확인"""
        if not file_path.endswith('.xml'):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # MyBatis 매퍼 파일 특성 검사
                return 'mapper' in content.lower() and ('namespace' in content or 'select' in content)
        except:
            return False
    
    def calculate_file_hash(self, content: str) -> str:
        """파일 내용의 SHA-256 해시 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def count_lines(self, content: str) -> int:
        """코드 라인 수 계산"""
        return len([line for line in content.splitlines() if line.strip()])
    
    def extract_sql_statements(self, root: ET.Element) -> List[Dict]:
        """SQL 문 추출"""
        statements = []
        
        # select, insert, update, delete, procedure 태그 찾기
        sql_tags = ['select', 'insert', 'update', 'delete', 'procedure', 'function']
        
        for tag_name in sql_tags:
            for element in root.findall(f'.//{tag_name}'):
                stmt_id = element.get('id', 'unknown')
                sql_content = element.text or ''
                
                # 동적 SQL 태그들도 포함
                for child in element:
                    if child.text:
                        sql_content += child.text
                    if child.tail:
                        sql_content += child.tail
                
                statement = {
                    'id': stmt_id,
                    'type': tag_name,
                    'sql_content': sql_content.strip(),
                    'attributes': dict(element.attrib),
                    'has_dynamic_sql': self._has_dynamic_sql(element),
                    'parameter_type': element.get('parameterType'),
                    'result_type': element.get('resultType'),
                    'result_map': element.get('resultMap')
                }
                statements.append(statement)
        
        return statements
    
    def _has_dynamic_sql(self, element: ET.Element) -> bool:
        """동적 SQL 태그 포함 여부 확인"""
        dynamic_tags = ['if', 'choose', 'when', 'otherwise', 'trim', 'where', 'set', 'foreach']
        
        for tag in dynamic_tags:
            if element.find(f'.//{tag}') is not None:
                return True
        return False
    
    def extract_sql_fragments(self, root: ET.Element) -> List[Dict]:
        """<sql> 프래그먼트 추출"""
        fragments = []
        
        for sql_element in root.findall('.//sql'):
            fragment_id = sql_element.get('id', 'unknown')
            content = sql_element.text or ''
            
            fragments.append({
                'id': fragment_id,
                'content': content.strip()
            })
        
        return fragments
    
    def extract_result_maps(self, root: ET.Element) -> List[Dict]:
        """<resultMap> 추출"""
        result_maps = []
        
        for rm_element in root.findall('.//resultMap'):
            rm_id = rm_element.get('id', 'unknown')
            rm_type = rm_element.get('type', '')
            
            # result 매핑 정보
            results = []
            for result in rm_element.findall('.//result'):
                results.append({
                    'property': result.get('property'),
                    'column': result.get('column'),
                    'jdbc_type': result.get('jdbcType')
                })
            
            result_maps.append({
                'id': rm_id,
                'type': rm_type,
                'results': results
            })
        
        return result_maps
    
    def extract_includes(self, root: ET.Element) -> List[Dict]:
        """<include> 참조 추출"""
        includes = []
        
        for include_element in root.findall('.//include'):
            ref_id = include_element.get('refid')
            if ref_id:
                includes.append({
                    'type': 'sql_include',
                    'target': ref_id
                })
        
        return includes
    
    def parse_file(self, file_path: str, project_id: int) -> MyBatisParsingResult:
        """MyBatis XML 파일 파싱"""
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 기본 파일 정보
            file_stat = os.stat(file_path)
            file_info = {
                'project_id': project_id,
                'path': os.path.relpath(file_path),
                'language': 'mybatis',
                'hash': self.calculate_file_hash(content),
                'loc': self.count_lines(content),
                'mtime': datetime.fromtimestamp(file_stat.st_mtime)
            }
            
            # XML 파싱
            try:
                root = ET.fromstring(content)
            except ET.ParseError as e:
                # XML 파싱 실패
                return MyBatisParsingResult(
                    file_info=file_info,
                    namespace='',
                    statements=[],
                    sql_fragments=[],
                    result_maps=[],
                    dependencies=[],
                    confidence=0.1
                )
            
            # 네임스페이스 추출
            namespace = root.get('namespace', '')
            
            # SQL 문 추출
            statements = self.extract_sql_statements(root)
            sql_fragments = self.extract_sql_fragments(root)
            result_maps = self.extract_result_maps(root)
            
            # 의존성 정보
            dependencies = self.extract_includes(root)
            
            # 신뢰도 계산
            confidence = 0.9 if namespace and statements else 0.7
            
            return MyBatisParsingResult(
                file_info=file_info,
                namespace=namespace,
                statements=statements,
                sql_fragments=sql_fragments,
                result_maps=result_maps,
                dependencies=dependencies,
                confidence=confidence
            )
            
        except Exception as e:
            file_info['hash'] = 'error'
            file_info['loc'] = 0
            
            return MyBatisParsingResult(
                file_info=file_info,
                namespace='',
                statements=[],
                sql_fragments=[],
                result_maps=[],
                dependencies=[],
                confidence=0.0
            )


class JSPMyBatisAnalyzer:
    """JSP와 MyBatis 통합 분석기"""
    
    def __init__(self, config: Dict = None):
        self.jsp_parser = JSPParser(config)
        self.mybatis_parser = MyBatisParser(config)
    
    def parse_directory(self, directory_path: str, project_id: int) -> Tuple[List[JSPParsingResult], List[MyBatisParsingResult]]:
        """디렉토리 내 JSP 및 MyBatis 파일 파싱"""
        jsp_results = []
        mybatis_results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if self.jsp_parser.can_parse(file_path):
                    try:
                        result = self.jsp_parser.parse_file(file_path, project_id)
                        jsp_results.append(result)
                    except Exception as e:
                        print(f"Error parsing JSP {file_path}: {e}")
                
                elif self.mybatis_parser.can_parse(file_path):
                    try:
                        result = self.mybatis_parser.parse_file(file_path, project_id)
                        mybatis_results.append(result)
                    except Exception as e:
                        print(f"Error parsing MyBatis {file_path}: {e}")
        
        return jsp_results, mybatis_results
    
    def analyze_jsp_java_connections(self, jsp_results: List[JSPParsingResult], java_results: List) -> List[Dict]:
        """JSP와 Java 코드 간 연결 분석 (향후 구현)"""
        # TODO: JSP scriptlet에서 Java 클래스/메소드 사용 분석
        return []
    
    def analyze_mybatis_java_connections(self, mybatis_results: List[MyBatisParsingResult], java_results: List) -> List[Dict]:
        """MyBatis와 Java 코드 간 연결 분석 (향후 구현)"""
        # TODO: MyBatis 매퍼와 Java DAO/Service 연결 분석
        return []


if __name__ == "__main__":
    # 테스트 코드
    analyzer = JSPMyBatisAnalyzer()
    
    # 샘플 프로젝트 파싱 테스트
    sample_project_path = "./PROJECT/sample-app"
    if os.path.exists(sample_project_path):
        jsp_results, mybatis_results = analyzer.parse_directory(sample_project_path, project_id=1)
        
        print(f"Parsed {len(jsp_results)} JSP files")
        print(f"Parsed {len(mybatis_results)} MyBatis files")
        
        # JSP 결과 출력
        for result in jsp_results[:2]:
            print(f"\nJSP File: {result.file_info['path']}")
            print(f"Includes: {len(result.includes)}")
            print(f"Scriptlets: {len(result.scriptlets)}")
            print(f"EL Expressions: {len(result.el_expressions)}")
            print(f"JSTL Tags: {len(result.jstl_tags)}")
        
        # MyBatis 결과 출력
        for result in mybatis_results[:2]:
            print(f"\nMyBatis File: {result.file_info['path']}")
            print(f"Namespace: {result.namespace}")
            print(f"Statements: {len(result.statements)}")
            print(f"SQL Fragments: {len(result.sql_fragments)}")
    else:
        print("Sample project not found")