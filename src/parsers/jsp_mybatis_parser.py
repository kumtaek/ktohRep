"""
JSP 및 MyBatis XML 파서
JSP 파일과 MyBatis 매퍼 XML 파일에서 SQL 구문과 의존성을 추출합니다.
"""

import hashlib
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json

from ..models.database import File, SqlUnit, Edge, Join, RequiredFilter
from ..utils.confidence_calculator import ConfidenceCalculator

class JspMybatisParser:
    """JSP와 MyBatis XML 파일을 파싱하는 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        
        # MyBatis 동적 태그 패턴
        self.dynamic_tags = ['if', 'choose', 'when', 'otherwise', 'foreach', 'where', 'set', 'trim']
        
        # SQL 패턴
        self.sql_pattern = re.compile(
            r'<(select|insert|update|delete)\s+[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>',
            re.IGNORECASE | re.DOTALL
        )
        
        # JSP 스크립틀릿 SQL 패턴
        self.jsp_sql_pattern = re.compile(
            r'<%.*?(?:select|insert|update|delete).*?%>',
            re.IGNORECASE | re.DOTALL
        )
        
    def can_parse(self, file_path: str) -> bool:
        """파일이 이 파서로 처리 가능한지 확인"""
        return file_path.endswith('.jsp') or file_path.endswith('.xml')
        
    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge]]:
        """
        JSP 또는 MyBatis XML 파일을 파싱하여 메타데이터 추출
        
        Args:
            file_path: 파싱할 파일 경로
            project_id: 프로젝트 ID
            
        Returns:
            Tuple of (File, SqlUnits, Joins, RequiredFilters, Edges)
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
            
            if file_path.endswith('.jsp'):
                return self._parse_jsp(content, file_obj)
            elif file_path.endswith('.xml'):
                return self._parse_mybatis_xml(content, file_obj)
            else:
                return file_obj, [], [], [], []
                
        except Exception as e:
            print(f"파일 파싱 오류 {file_path}: {e}")
            return file_obj, [], [], [], []
            
    def _parse_jsp(self, content: str, file_obj: File) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge]]:
        """JSP 파일 파싱"""
        
        sql_units = []
        joins = []
        filters = []
        edges = []
        
        # JSP 스크립틀릿에서 SQL 구문 찾기
        sql_matches = self.jsp_sql_pattern.finditer(content)
        
        for i, match in enumerate(sql_matches):
            start_pos = match.start()
            end_pos = match.end()
            sql_content = match.group()
            
            # 라인 번호 계산
            start_line = content[:start_pos].count('\n') + 1
            end_line = content[:end_pos].count('\n') + 1
            
            # SQL 유닛 생성
            sql_unit = SqlUnit(
                file_id=None,  # 파일 저장 후 설정
                origin='jsp',
                mapper_ns=None,
                stmt_id=f'jsp_sql_{i+1}',
                start_line=start_line,
                end_line=end_line,
                stmt_kind=self._detect_sql_type(sql_content),
                normalized_fingerprint=self._create_sql_fingerprint(sql_content)
            )
            
            sql_units.append(sql_unit)
            
            # SQL에서 조인과 필터 추출
            sql_joins, sql_filters = self._extract_sql_patterns(sql_content, sql_unit)
            joins.extend(sql_joins)
            filters.extend(sql_filters)
            
        # JSP include 관계 추출
        include_edges = self._extract_jsp_includes(content, file_obj)
        edges.extend(include_edges)
        
        return file_obj, sql_units, joins, filters, edges
        
    def _parse_mybatis_xml(self, content: str, file_obj: File) -> Tuple[File, List[SqlUnit], List[Join], List[RequiredFilter], List[Edge]]:
        """MyBatis XML 파일 파싱"""
        
        sql_units = []
        joins = []
        filters = []
        edges = []
        
        try:
            # XML 파싱
            root = ET.fromstring(content)
            
            # 네임스페이스 추출
            namespace = root.get('namespace', '')
            
            # SQL 구문 태그들 처리
            for stmt_type in ['select', 'insert', 'update', 'delete', 'sql']:
                elements = root.findall(f'.//{stmt_type}')
                
                for element in elements:
                    stmt_id = element.get('id', '')
                    
                    # 요소의 위치 추정 (XML에서는 정확한 라인 번호 어려움)
                    start_line, end_line = self._estimate_xml_line_numbers(element, content)
                    
                    # SQL 내용 추출
                    sql_content = self._extract_sql_content(element)
                    
                    # SQL 유닛 생성
                    sql_unit = SqlUnit(
                        file_id=None,
                        origin='mybatis',
                        mapper_ns=namespace,
                        stmt_id=stmt_id,
                        start_line=start_line,
                        end_line=end_line,
                        stmt_kind=stmt_type,
                        normalized_fingerprint=self._create_sql_fingerprint(sql_content)
                    )
                    
                    sql_units.append(sql_unit)
                    
                    # 동적 SQL 분석
                    if self._has_dynamic_sql(element):
                        # 동적 SQL의 경우 모든 가능한 변형을 고려 (superset 전략)
                        expanded_sql = self._expand_dynamic_sql(element)
                        sql_joins, sql_filters = self._extract_sql_patterns(expanded_sql, sql_unit)
                    else:
                        # 정적 SQL 처리
                        sql_joins, sql_filters = self._extract_sql_patterns(sql_content, sql_unit)
                        
                    joins.extend(sql_joins)
                    filters.extend(sql_filters)
                    
            # <include> 태그 의존성 추출
            include_edges = self._extract_mybatis_includes(root, file_obj)
            edges.extend(include_edges)
            
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            
        return file_obj, sql_units, joins, filters, edges
        
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
        """SQL 구조적 지문 생성 (원문 저장 금지 원칙)"""
        
        # SQL을 정규화하여 구조적 패턴만 추출
        normalized = re.sub(r'\s+', ' ', sql_content.lower().strip())
        
        # 파라미터와 리터럴 값을 플레이스홀더로 대체
        normalized = re.sub(r':\w+', ':PARAM', normalized)  # MyBatis 파라미터
        normalized = re.sub(r'\$\{\w+\}', '${PARAM}', normalized)  # MyBatis 동적 파라미터
        normalized = re.sub(r"'[^']*'", "'VALUE'", normalized)  # 문자열 리터럴
        normalized = re.sub(r'\b\d+\b', 'NUMBER', normalized)  # 숫자 리터럴
        
        # 해시 생성
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
        
    def _extract_sql_patterns(self, sql_content: str, sql_unit: SqlUnit) -> Tuple[List[Join], List[RequiredFilter]]:
        """SQL에서 조인 조건과 필수 필터 추출"""
        
        joins = []
        filters = []
        
        try:
            # 단순한 정규식 기반 조인 패턴 추출
            join_patterns = [
                r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # table1.col1 = table2.col2
                r'join\s+(\w+)\s+\w+\s+on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # JOIN table ON ...
            ]
            
            for pattern in join_patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 4:
                        join = Join(
                            sql_id=None,  # SQL 유닛 저장 후 설정
                            l_table=groups[0],
                            l_col=groups[1],
                            op='=',
                            r_table=groups[2] if len(groups) > 2 else groups[0],
                            r_col=groups[3] if len(groups) > 3 else groups[1],
                            inferred_pkfk=0,  # PK-FK 관계는 별도 분석 필요
                            confidence=0.8
                        )
                        joins.append(join)
                        
            # WHERE 절 필터 조건 추출
            where_patterns = [
                r'(\w+)\.(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]',  # table.col = 'value'
                r'(\w+)\.(\w+)\s*=\s*:\w+',  # table.col = :param
                r'(\w+)\.(\w+)\s*!=\s*[\'"]([^\'"]+)[\'"]',  # table.col != 'value'
                r'(\w+)\.(\w+)\s*<>\s*[\'"]([^\'"]+)[\'"]',  # table.col <> 'value'
            ]
            
            for pattern in where_patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        op = '='
                        if '!=' in match.group() or '<>' in match.group():
                            op = '!='
                            
                        value_repr = groups[2] if len(groups) > 2 else ':param'
                        
                        # 동적 태그 외부에 있는지 확인 (항상 적용되는 필터인지)
                        always_applied = 1 if not self._is_in_dynamic_block(match.start(), sql_content) else 0
                        
                        filter_obj = RequiredFilter(
                            sql_id=None,
                            table_name=groups[0],
                            column_name=groups[1],
                            op=op,
                            value_repr=value_repr,
                            always_applied=always_applied,
                            confidence=0.7
                        )
                        filters.append(filter_obj)
                        
        except Exception as e:
            print(f"SQL 패턴 추출 오류: {e}")
            
        return joins, filters
        
    def _has_dynamic_sql(self, element: ET.Element) -> bool:
        """요소가 동적 SQL을 포함하는지 확인"""
        
        # 동적 태그가 있는지 확인
        for tag in self.dynamic_tags:
            if element.find(f'.//{tag}') is not None:
                return True
                
        # 동적 파라미터 패턴 확인
        text_content = ET.tostring(element, encoding='unicode')
        if '${' in text_content or '#{' in text_content:
            return True
            
        return False
        
    def _expand_dynamic_sql(self, element: ET.Element) -> str:
        """동적 SQL을 최대 포함 형태로 확장 (superset 전략)"""
        
        # 모든 동적 블록을 포함하는 형태로 SQL 생성
        # 이는 누락을 최소화하기 위한 보수적 접근
        
        text_content = ET.tostring(element, encoding='unicode')
        
        # <if> 태그 내용을 모두 포함
        text_content = re.sub(r'<if[^>]*>(.*?)</if>', r'\1', text_content, flags=re.DOTALL)
        
        # <choose> 태그에서 모든 <when> 조건을 포함
        text_content = re.sub(r'<when[^>]*>(.*?)</when>', r'\1', text_content, flags=re.DOTALL)
        
        # <foreach> 태그를 단일 항목으로 처리
        text_content = re.sub(r'<foreach[^>]*>(.*?)</foreach>', r'\1', text_content, flags=re.DOTALL)
        
        # XML 태그 제거
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        
        return text_content
        
    def _is_in_dynamic_block(self, position: int, sql_content: str) -> bool:
        """주어진 위치가 동적 SQL 블록 내부에 있는지 확인"""
        
        # 간단한 구현: 동적 태그 패턴을 찾아서 위치 비교
        dynamic_blocks = []
        
        for tag in self.dynamic_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            for match in re.finditer(pattern, sql_content, re.DOTALL | re.IGNORECASE):
                dynamic_blocks.append((match.start(), match.end()))
                
        # 주어진 위치가 동적 블록 내부에 있는지 확인
        for start, end in dynamic_blocks:
            if start <= position <= end:
                return True
                
        return False
        
    def _extract_jsp_includes(self, content: str, file_obj: File) -> List[Edge]:
        """JSP include 관계 추출"""
        
        edges = []
        
        # JSP include 패턴들
        include_patterns = [
            r'<%@\s*include\s+file\s*=\s*["\']([^"\']+)["\']',  # <%@ include file="..." %>
            r'<jsp:include\s+page\s*=\s*["\']([^"\']+)["\']',    # <jsp:include page="..." />
        ]
        
        for pattern in include_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                included_file = match.group(1)
                
                edge = Edge(
                    src_type='file',
                    src_id=None,  # 파일 저장 후 설정
                    dst_type='file',
                    dst_id=None,  # 포함된 파일 해결 필요
                    edge_kind='includes',
                    confidence=0.9
                )
                edges.append(edge)
                
        return edges
        
    def _extract_mybatis_includes(self, root: ET.Element, file_obj: File) -> List[Edge]:
        """MyBatis include 관계 추출"""
        
        edges = []
        
        # <include> 태그 찾기
        include_elements = root.findall('.//include')
        
        for include_elem in include_elements:
            refid = include_elem.get('refid', '')
            
            if refid:
                edge = Edge(
                    src_type='sql_unit',
                    src_id=None,  # 현재 SQL 유닛 ID로 설정 필요
                    dst_type='sql_unit',
                    dst_id=None,  # refid로 참조된 SQL 유닛 해결 필요
                    edge_kind='includes',
                    confidence=0.95
                )
                edges.append(edge)
                
        return edges
        
    def _extract_sql_content(self, element: ET.Element) -> str:
        """XML 요소에서 SQL 내용 추출"""
        
        # 요소의 모든 텍스트 내용을 재귀적으로 수집
        def collect_text(elem):
            text = elem.text or ''
            for child in elem:
                text += collect_text(child)
                if child.tail:
                    text += child.tail
            return text
            
        return collect_text(element).strip()
        
    def _estimate_xml_line_numbers(self, element: ET.Element, content: str) -> Tuple[int, int]:
        """XML 요소의 라인 번호 추정"""
        
        # XML 파싱에서는 정확한 라인 번호를 얻기 어려움
        # 요소 ID나 태그명을 이용해 대략적인 위치 추정
        
        element_text = ET.tostring(element, encoding='unicode')
        
        # 내용에서 요소 위치 찾기
        start_pos = content.find(element_text[:100])  # 처음 100자로 검색
        if start_pos == -1:
            return 1, 1
            
        start_line = content[:start_pos].count('\n') + 1
        end_line = start_line + element_text.count('\n')
        
        return start_line, end_line