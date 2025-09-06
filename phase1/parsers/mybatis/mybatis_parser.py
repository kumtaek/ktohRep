"""
Enhanced MyBatis Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 MyBatis XML 파서
- 중복 방지 및 정확도 향상
- 정확한 SQL 추출 및 include 태그 처리
- 동적 쿼리 처리 개선
- MyBatis 공식 문서 기반 패턴 매칭
"""

import re
import hashlib
from typing import Dict, List, Any, Set, Tuple
from phase1.parsers.base_parser import BaseParser
from phase1.utils.table_alias_resolver import get_table_alias_resolver

class MyBatisParser(BaseParser):
    """
    Enhanced MyBatis Parser (Context7 기반)
    Context7 라이브러리 문서를 참조하여 개발된 개선된 MyBatis XML 파서
    - 중복 방지 및 정확도 향상
    - 정확한 SQL 추출 및 include 태그 처리  
    - 동적 쿼리 처리 개선
    - MyBatis 공식 문서 기반 패턴 매칭
    """
    
    # 클래스 레벨 중복 방지 집합 (전역 공유)
    _global_processed_sql_ids = set()
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # MyBatis XML 태그 패턴 (Context7 기반)
        self.mybatis_tags = {
            'select': re.compile(r'<select\s+([^>]*?)>(.*?)</select>', re.IGNORECASE | re.DOTALL),
            'insert': re.compile(r'<insert\s+([^>]*?)>(.*?)</insert>', re.IGNORECASE | re.DOTALL),
            'update': re.compile(r'<update\s+([^>]*?)>(.*?)</update>', re.IGNORECASE | re.DOTALL),
            'delete': re.compile(r'<delete\s+([^>]*?)>(.*?)</delete>', re.IGNORECASE | re.DOTALL),
            'resultMap': re.compile(r'<resultMap\s+([^>]*?)>(.*?)</resultMap>', re.IGNORECASE | re.DOTALL),
            'parameterMap': re.compile(r'<parameterMap\s+([^>]*?)>(.*?)</parameterMap>', re.IGNORECASE | re.DOTALL),
            'sql': re.compile(r'<sql\s+([^>]*?)>(.*?)</sql>', re.IGNORECASE | re.DOTALL),
            'include': re.compile(r'<include\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
        }
        
        # MyBatis 동적 쿼리 태그 패턴 (Context7 기반)
        self.dynamic_tags = {
            'if': re.compile(r'<if\s+test\s*=\s*["\']([^"\']*)["\']>(.*?)</if>', re.IGNORECASE | re.DOTALL),
            'choose': re.compile(r'<choose>(.*?)</choose>', re.IGNORECASE | re.DOTALL),
            'when': re.compile(r'<when\s+test\s*=\s*["\']([^"\']*)["\']>(.*?)</when>', re.IGNORECASE | re.DOTALL),
            'otherwise': re.compile(r'<otherwise>(.*?)</otherwise>', re.IGNORECASE | re.DOTALL),
            'where': re.compile(r'<where>(.*?)</where>', re.IGNORECASE | re.DOTALL),
            'set': re.compile(r'<set>(.*?)</set>', re.IGNORECASE | re.DOTALL),
            'foreach': re.compile(r'<foreach\s+([^>]*?)>(.*?)</foreach>', re.IGNORECASE | re.DOTALL),
            'trim': re.compile(r'<trim\s+([^>]*?)>(.*?)</trim>', re.IGNORECASE | re.DOTALL),
            'bind': re.compile(r'<bind\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
        }
        
        # SQL 쿼리 패턴 (개선된 버전)
        self.sql_patterns = {
            'tables': [
                re.compile(r'\bFROM\s+([^\s,()]+?)(?=\s+(?:JOIN|WHERE|GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bJOIN\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\b(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s+JOIN\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bUPDATE\s+([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bINSERT\s+(?:INTO\s+)?([^\s,()]+)', re.IGNORECASE),
                re.compile(r'\bDELETE\s+FROM\s+([^\s,()]+)', re.IGNORECASE),
            ],
            'columns': [
                re.compile(r'\bSELECT\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
                re.compile(r'\b(\w+)\.(\w+)\b', re.IGNORECASE),
                re.compile(r'\b(\w+)\s+AS\s+(\w+)', re.IGNORECASE),
                re.compile(r'\bSET\s+(.+?)(?=\bWHERE\b|$)', re.IGNORECASE | re.DOTALL),
            ],
            'parameters': [
                re.compile(r'#\{([^}]+)\}', re.IGNORECASE),
                re.compile(r'\$\{([^}]+)\}', re.IGNORECASE),
            ]
        }
        
        # 중복 방지를 위한 집합
        self._processed_sql_ids = set()
        self._sql_fragments_cache = {}
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'mybatis'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced MyBatis XML 파일 파싱
        """
        # 1. SQL 조각 캐시 구축
        self._build_sql_fragments_cache(content)
        
        # 2. 기본 SQL 처리
        processed_content = content
        
        # 3. 테이블 별칭 해석
        alias_resolver = get_table_alias_resolver(context.get('default_schema', 'DEFAULT'))
        alias_mapping = alias_resolver.extract_table_alias_mapping(processed_content)
        
        # 4. 정규화 (주석 제거)
        normalized_content = self._remove_comments(processed_content)
        
        # 5. 중복 방지를 위한 집합 초기화
        self._processed_sql_ids.clear()
        
        result = {
            'sql_units': self._extract_sql_statements_enhanced(normalized_content, context),  # context 전달
            'dynamic_queries': self._extract_dynamic_queries_enhanced(normalized_content),
            'dynamic_patterns': self._extract_dynamic_query_patterns(normalized_content),
            'result_maps': self._extract_result_maps_enhanced(normalized_content),
            'parameter_maps': self._extract_parameter_maps_enhanced(normalized_content),
            'sql_fragments': self._extract_sql_fragments_enhanced(normalized_content),
            'tables': self._extract_tables_enhanced(normalized_content),
            'columns': self._extract_columns_enhanced(normalized_content),
            'parameters': self._extract_parameters_enhanced(normalized_content),
            'mybatis_config': self._extract_mybatis_config_enhanced(normalized_content),
            'joins': self._extract_joins_enhanced(normalized_content),
            'file_metadata': {'default_schema': context.get('default_schema', 'DEFAULT')},
            'confidence': 0.95,  # 향상된 신뢰도
            'dynamic_blocks': [],
            'alias_mapping': alias_mapping,
            'original_content': content,
            'processed_content': processed_content
        }
        
        # 6. 별칭을 실제 테이블명으로 해석하여 테이블 목록 업데이트
        resolved_tables = set()
        for table in result['tables']:
            resolved_table = alias_resolver.resolve_table_alias(table, alias_mapping)
            resolved_tables.add(resolved_table)
        result['resolved_tables'] = list(resolved_tables)
        
        return result
    
    def _extract_joins_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """JOIN 정보를 향상된 방식으로 추출"""
        joins = []
        
        # JOIN 패턴들
        join_patterns = [
            r'JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
            r'OUTER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        ]
        
        for pattern in join_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                table = match.group(1)
                left_col = match.group(2)
                right_col = match.group(3)
                joins.append({
                    'table': table,
                    'left_column': left_col,
                    'right_column': right_col,
                    'join_type': 'INNER' if 'INNER' in pattern else 'LEFT' if 'LEFT' in pattern else 'RIGHT' if 'RIGHT' in pattern else 'OUTER' if 'OUTER' in pattern else 'JOIN'
                })
        
        return joins
    
    def _build_sql_fragments_cache(self, content: str) -> None:
        """SQL 조각 캐시 구축"""
        self._sql_fragments_cache.clear()
        
        sql_matches = self.mybatis_tags['sql'].finditer(content)
        for match in sql_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_id = self._extract_attribute(attributes, 'id')
            if sql_id:
                self._sql_fragments_cache[sql_id] = sql_content.strip()
    
    def _extract_sql_statements_enhanced(self, content: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Enhanced SQL 구문 추출 (context 포함)"""
        sql_statements = []
        
        # 1. SELECT 구문 추출
        select_matches = self.mybatis_tags['select'].finditer(content)
        for match in select_matches:
            sql_unit = self._process_sql_statement(match, 'select', content, context)  # context 전달
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 2. INSERT 구문 추출
        insert_matches = self.mybatis_tags['insert'].finditer(content)
        for match in insert_matches:
            sql_unit = self._process_sql_statement(match, 'insert', content, context)  # context 전달
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 3. UPDATE 구문 추출
        update_matches = self.mybatis_tags['update'].finditer(content)
        for match in update_matches:
            sql_unit = self._process_sql_statement(match, 'update', content, context)  # context 전달
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        # 4. DELETE 구문 추출
        delete_matches = self.mybatis_tags['delete'].finditer(content)
        for match in delete_matches:
            sql_unit = self._process_sql_statement(match, 'delete', content, context)  # context 전달
            if sql_unit and self._is_unique_sql_unit(sql_unit):
                sql_statements.append(sql_unit)
        
        return sql_statements
    
    def _process_sql_statement(self, match: re.Match, stmt_type: str, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """SQL 구문 처리 (file_path 포함)"""
        attributes = match.group(1)
        sql_content = match.group(2)
        
        # context에서 file_path 추출
        file_path = context.get('file_path', '') if context else ''
        
        # include 태그 처리
        processed_sql = self._process_include_tags(sql_content)
        
        # 동적 쿼리 처리
        processed_sql = self._process_dynamic_sql(processed_sql)
        
        # SQL 정규화
        normalized_sql = self._normalize_sql(processed_sql)
        
        # 고유 ID 생성
        sql_id = self._extract_attribute(attributes, 'id')
        unique_id = self._generate_unique_id(sql_id, stmt_type, normalized_sql)
        
        sql_unit = {
            'type': stmt_type,
            'id': sql_id,
            'file_path': file_path,  # file_path 추가
            'parameterType': self._extract_attribute(attributes, 'parameterType'),
            'resultType': self._extract_attribute(attributes, 'resultType'),
            'resultMap': self._extract_attribute(attributes, 'resultMap'),
            'sql_content': processed_sql.strip(),
            'normalized_sql': normalized_sql,
            'attributes': self._parse_xml_attributes(attributes),
            'full_text': match.group(0),
            'tables': self._extract_tables_from_sql(processed_sql),
            'columns': self._extract_columns_from_sql(processed_sql),
            'parameters': self._extract_parameters_from_sql(processed_sql),
            'has_dynamic_content': self._has_dynamic_content(processed_sql),
            'has_include_tags': '<include' in processed_sql,
            'line_number': self._get_line_number(content, match.start())
        }
        
        # Enhanced unique_id 생성 (file_path 포함)
        sql_unit['unique_id'] = self._generate_enhanced_unique_id(sql_unit)
        
        return sql_unit
    
    def _process_include_tags(self, sql_content: str) -> str:
        """include 태그 처리"""
        processed_sql = sql_content
        
        # include 태그 찾기
        include_matches = self.mybatis_tags['include'].finditer(sql_content)
        for match in include_matches:
            attributes = match.group(1)
            refid = self._extract_attribute(attributes, 'refid')
            
            if refid and refid in self._sql_fragments_cache:
                # include 태그를 실제 SQL 조각으로 교체
                fragment_content = self._sql_fragments_cache[refid]
                processed_sql = processed_sql.replace(match.group(0), fragment_content)
        
        return processed_sql
    
    def _process_dynamic_sql(self, sql_content: str) -> str:
        """동적 SQL 처리 (Context7 기반 개선)"""
        processed_sql = sql_content
        
        # Context7 기반 동적 태그 처리 - 더 정확한 패턴 매칭
        for tag_name, pattern in self.dynamic_tags.items():
            if tag_name in ['if', 'when']:
                # if, when 태그: test 조건과 내용이 있음 (group 1: attributes, group 2: content)
                processed_sql = pattern.sub(r'\2', processed_sql)
            elif tag_name in ['otherwise', 'where', 'set']:
                # otherwise, where, set 태그: 내용만 있음 (group 1: content)
                processed_sql = pattern.sub(r'\1', processed_sql)
            elif tag_name == 'foreach':
                # foreach 태그: 속성과 내용이 있음 (group 1: attributes, group 2: content)
                processed_sql = pattern.sub(r'\2', processed_sql)
            elif tag_name == 'bind':
                # bind 태그 제거 (no content to keep)
                processed_sql = pattern.sub('', processed_sql)
            elif tag_name == 'trim':
                # trim 태그: 속성과 내용이 있음 (group 1: attributes, group 2: content)
                processed_sql = pattern.sub(r'\2', processed_sql)
        
        return processed_sql
    
    def _has_dynamic_content(self, sql_content: str) -> bool:
        """동적 쿼리 내용 포함 여부 확인 (Context7 기반 개선)"""
        dynamic_indicators = ['<if', '<choose', '<when', '<otherwise', '<where', '<set', '<foreach', '<trim', '<bind']
        return any(indicator in sql_content for indicator in dynamic_indicators)
    
    def _extract_dynamic_query_patterns(self, sql_content: str) -> List[Dict[str, Any]]:
        """Context7 기반 다이나믹 쿼리 패턴 추출"""
        dynamic_patterns = []
        
        # MyBatis 동적 태그별 패턴 분석
        for tag_name, pattern in self.dynamic_tags.items():
            matches = pattern.finditer(sql_content)
            for match in matches:
                pattern_info = {
                    'tag_type': tag_name,
                    'full_match': match.group(0),
                    'attributes': match.group(1) if len(match.groups()) > 0 else '',
                    'content': match.group(2) if len(match.groups()) > 1 else '',
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'unique_id': self._generate_dynamic_pattern_id(tag_name, match.group(0))
                }
                dynamic_patterns.append(pattern_info)
        
        return dynamic_patterns
    
    def _generate_dynamic_pattern_id(self, tag_type: str, content: str) -> str:
        """다이나믹 패턴 고유 ID 생성 (Context7 기반)"""
        combined = f"dynamic_{tag_type}_{content}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _generate_unique_id(self, sql_id: str, stmt_type: str, normalized_sql: str) -> str:
        """고유 ID 생성"""
        if not sql_id:
            # ID가 없는 경우 SQL 내용으로 해시 생성
            content_hash = hashlib.md5(normalized_sql.encode('utf-8')).hexdigest()[:8]
            return f"{stmt_type}_{content_hash}"
        
        return f"{stmt_type}_{sql_id}"
    
    def _is_unique_sql_unit(self, sql_unit: Dict[str, Any]) -> bool:
        """전역 중복 SQL Unit 체크"""
        # 더 정확한 unique_id 생성
        unique_id = self._generate_enhanced_unique_id(sql_unit)
        
        if unique_id in MyBatisParser._global_processed_sql_ids:
            return False
        
        MyBatisParser._global_processed_sql_ids.add(unique_id)
        return True
    
    def _generate_enhanced_unique_id(self, sql_unit: Dict[str, Any]) -> str:
        """향상된 고유 ID 생성 (A 답변파일 기반 강화)"""
        # 파일경로 + SQL ID + 정규화된 SQL 내용으로 고유성 보장
        file_path = sql_unit.get('file_path', '')
        sql_id = sql_unit.get('id', '')
        sql_content = sql_unit.get('sql', '')
        
        # A 답변파일 기반 강화된 정규화
        normalized_sql = self._normalize_sql_enhanced(sql_content)
        
        combined = f"{file_path}:{sql_id}:{normalized_sql}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def _normalize_sql_enhanced(self, sql: str) -> str:
        """A 답변파일 기반 강화된 SQL 정규화"""
        if not sql:
            return ""
        
        # 1. 주석 제거
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)  # -- 주석
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)  # /* */ 주석
        
        # 2. 플레이스홀더 정규화
        sql = re.sub(r'#\{[^}]+\}', '?', sql)  # #{param} -> ?
        sql = re.sub(r'\$\{[^}]+\}', '?', sql)  # ${param} -> ?
        
        # 3. 공백 정규화
        sql = re.sub(r'\s+', ' ', sql)  # 연속 공백을 단일 공백으로
        sql = sql.strip().lower()  # 앞뒤 공백 제거 및 소문자 변환
        
        return sql
    
    @classmethod
    def reset_global_cache(cls):
        """전역 캐시 초기화 (프로젝트 시작 시 호출)"""
        cls._global_processed_sql_ids.clear()
    
    def _get_line_number(self, content: str, position: int) -> int:
        """위치에 해당하는 라인 번호 반환"""
        return content[:position].count('\n') + 1
    
    def _extract_dynamic_queries_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced 동적 쿼리 추출"""
        dynamic_queries = []
        
        for tag_name, pattern in self.dynamic_tags.items():
            matches = pattern.finditer(content)
            for match in matches:
                dynamic_query = {
                    'type': tag_name,
                    'full_text': match.group(0),
                    'line_number': self._get_line_number(content, match.start())
                }
                
                if tag_name in ['if', 'when']:
                    dynamic_query['test_condition'] = match.group(1)
                    dynamic_query['content'] = match.group(2).strip()
                elif tag_name in ['choose', 'where', 'set', 'otherwise']:
                    dynamic_query['content'] = match.group(1).strip()
                elif tag_name == 'foreach':
                    dynamic_query['attributes'] = self._parse_xml_attributes(match.group(1))
                    dynamic_query['content'] = match.group(2).strip()
                elif tag_name == 'trim':
                    dynamic_query['attributes'] = self._parse_xml_attributes(match.group(1))
                    dynamic_query['content'] = match.group(2).strip()
                elif tag_name == 'bind':
                    dynamic_query['attributes'] = self._parse_xml_attributes(match.group(1))
                
                dynamic_queries.append(dynamic_query)
        
        return dynamic_queries
    
    def _extract_result_maps_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced ResultMap 추출"""
        result_maps = []
        
        result_map_matches = self.mybatis_tags['resultMap'].finditer(content)
        for match in result_map_matches:
            attributes = match.group(1)
            result_map_content = match.group(2)
            
            result_map = {
                'id': self._extract_attribute(attributes, 'id'),
                'type': self._extract_attribute(attributes, 'type'),
                'extends': self._extract_attribute(attributes, 'extends'),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'line_number': self._get_line_number(content, match.start()),
                'results': self._extract_result_elements(result_map_content),
                'associations': self._extract_association_elements(result_map_content),
                'collections': self._extract_collection_elements(result_map_content)
            }
            
            result_maps.append(result_map)
        
        return result_maps
    
    def _extract_result_elements(self, content: str) -> List[Dict[str, Any]]:
        """result 요소 추출"""
        results = []
        result_pattern = r'<result\s+([^>]*?)>'
        result_matches = re.finditer(result_pattern, content, re.IGNORECASE)
        
        for match in result_matches:
            result_attrs = match.group(1)
            results.append({
                'property': self._extract_attribute(result_attrs, 'property'),
                'column': self._extract_attribute(result_attrs, 'column'),
                'javaType': self._extract_attribute(result_attrs, 'javaType'),
                'jdbcType': self._extract_attribute(result_attrs, 'jdbcType'),
                'attributes': self._parse_xml_attributes(result_attrs)
            })
        
        return results
    
    def _extract_association_elements(self, content: str) -> List[Dict[str, Any]]:
        """association 요소 추출"""
        associations = []
        association_pattern = r'<association\s+([^>]*?)>(.*?)</association>'
        association_matches = re.finditer(association_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in association_matches:
            assoc_attrs = match.group(1)
            assoc_content = match.group(2)
            associations.append({
                'property': self._extract_attribute(assoc_attrs, 'property'),
                'javaType': self._extract_attribute(assoc_attrs, 'javaType'),
                'resultMap': self._extract_attribute(assoc_attrs, 'resultMap'),
                'content': assoc_content.strip(),
                'attributes': self._parse_xml_attributes(assoc_attrs)
            })
        
        return associations
    
    def _extract_collection_elements(self, content: str) -> List[Dict[str, Any]]:
        """collection 요소 추출"""
        collections = []
        collection_pattern = r'<collection\s+([^>]*?)>(.*?)</collection>'
        collection_matches = re.finditer(collection_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in collection_matches:
            coll_attrs = match.group(1)
            coll_content = match.group(2)
            collections.append({
                'property': self._extract_attribute(coll_attrs, 'property'),
                'javaType': self._extract_attribute(coll_attrs, 'javaType'),
                'resultMap': self._extract_attribute(coll_attrs, 'resultMap'),
                'content': coll_content.strip(),
                'attributes': self._parse_xml_attributes(coll_attrs)
            })
        
        return collections
    
    def _extract_parameter_maps_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced ParameterMap 추출"""
        parameter_maps = []
        
        parameter_map_matches = self.mybatis_tags['parameterMap'].finditer(content)
        for match in parameter_map_matches:
            attributes = match.group(1)
            parameter_map_content = match.group(2)
            
            parameter_map = {
                'id': self._extract_attribute(attributes, 'id'),
                'type': self._extract_attribute(attributes, 'type'),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'line_number': self._get_line_number(content, match.start()),
                'parameters': self._extract_parameter_elements(parameter_map_content)
            }
            
            parameter_maps.append(parameter_map)
        
        return parameter_maps
    
    def _extract_parameter_elements(self, content: str) -> List[Dict[str, Any]]:
        """parameter 요소 추출"""
        parameters = []
        parameter_pattern = r'<parameter\s+([^>]*?)>'
        parameter_matches = re.finditer(parameter_pattern, content, re.IGNORECASE)
        
        for match in parameter_matches:
            param_attrs = match.group(1)
            parameters.append({
                'property': self._extract_attribute(param_attrs, 'property'),
                'javaType': self._extract_attribute(param_attrs, 'javaType'),
                'jdbcType': self._extract_attribute(param_attrs, 'jdbcType'),
                'mode': self._extract_attribute(param_attrs, 'mode'),
                'attributes': self._parse_xml_attributes(param_attrs)
            })
        
        return parameters
    
    def _extract_sql_fragments_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced SQL 조각 추출"""
        sql_fragments = []
        
        # sql 태그 추출
        sql_matches = self.mybatis_tags['sql'].finditer(content)
        for match in sql_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_fragments.append({
                'id': self._extract_attribute(attributes, 'id'),
                'content': sql_content.strip(),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'line_number': self._get_line_number(content, match.start())
            })
        
        return sql_fragments
    
    def _extract_tables_enhanced(self, content: str) -> List[str]:
        """Enhanced 테이블명 추출"""
        tables = set()
        
        # 모든 SQL 구문에서 테이블 추출
        for sql_stmt in self._extract_sql_statements_enhanced(content):
            tables.update(sql_stmt.get('tables', []))
        
        return list(tables)
    
    def _extract_columns_enhanced(self, content: str) -> List[str]:
        """Enhanced 컬럼명 추출"""
        columns = set()
        
        # 모든 SQL 구문에서 컬럼 추출
        for sql_stmt in self._extract_sql_statements_enhanced(content):
            columns.update(sql_stmt.get('columns', []))
        
        return list(columns)
    
    def _extract_parameters_enhanced(self, content: str) -> List[str]:
        """Enhanced 파라미터 추출"""
        parameters = set()
        
        # 모든 SQL 구문에서 파라미터 추출
        for sql_stmt in self._extract_sql_statements_enhanced(content):
            parameters.update(sql_stmt.get('parameters', []))
        
        return list(parameters)
    
    def _extract_mybatis_config_enhanced(self, content: str) -> Dict[str, Any]:
        """Enhanced MyBatis 설정 추출"""
        return {
            'typeAliases': [],
            'environments': [],
            'dataSource': [],
            'mappers': []
        }
    
    def _extract_tables_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 테이블명 추출 (개선된 버전)"""
        tables = set()
        
        for pattern in self.sql_patterns['tables']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                table_ref = match.group(1).strip()
                # 스키마.테이블 형태에서 테이블명만 추출
                if '.' in table_ref:
                    table_ref = table_ref.split('.')[-1]
                # 특수문자 제거
                table_ref = re.sub(r'[^\w]', '', table_ref)
                if table_ref and not self._is_sql_keyword(table_ref):
                    tables.add(table_ref.upper())
        
        return list(tables)
    
    def _extract_columns_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 컬럼명 추출 (개선된 버전)"""
        columns = set()
        
        for pattern in self.sql_patterns['columns']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                if len(match.groups()) >= 2:
                    table_name = match.group(1)
                    column_name = match.group(2)
                    if not self._is_sql_keyword(table_name) and not self._is_sql_keyword(column_name):
                        columns.add(f"{table_name.upper()}.{column_name.upper()}")
        
        return list(columns)
    
    def _extract_parameters_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 파라미터 추출 (개선된 버전)"""
        parameters = set()
        
        for pattern in self.sql_patterns['parameters']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                param_name = match.group(1)
                if param_name and not self._is_sql_keyword(param_name):
                    parameters.add(param_name)
        
        return list(parameters)
    
    def _extract_attribute(self, attributes: str, attr_name: str) -> str:
        """XML 속성에서 특정 속성값 추출"""
        pattern = rf'{attr_name}\s*=\s*["\']([^"\']*)["\']'
        match = re.search(pattern, attributes, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_xml_attributes(self, attr_string: str) -> Dict[str, str]:
        """XML 속성 문자열을 파싱하여 딕셔너리로 변환"""
        attributes = {}
        
        if not attr_string.strip():
            return attributes
        
        # XML 속성 패턴: name="value" 또는 name='value'
        attr_pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        attr_matches = re.finditer(attr_pattern, attr_string, re.IGNORECASE)
        
        for match in attr_matches:
            attr_name = match.group(1).lower()
            attr_value = match.group(2)
            attributes[attr_name] = attr_value
        
        return attributes
    
    def _remove_comments(self, content: str) -> str:
        """MyBatis XML 주석 제거"""
        # XML 주석 제거
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        return content
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)
