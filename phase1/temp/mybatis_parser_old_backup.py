"""
MyBatis 파서
MyBatis XML 파일에서 SQL 쿼리, 매핑, 동적 쿼리 등을 추출합니다.
재현율을 높이기 위해 다양한 패턴을 처리합니다.
"""

import re
from typing import Dict, List, Any, Set
from ..base_parser import BaseParser
from utils.table_alias_resolver import get_table_alias_resolver

class MyBatisParser(BaseParser):
    """MyBatis 전용 파서 - 재현율 우선"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # MyBatis XML 태그 패턴
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
        
        # MyBatis 동적 쿼리 태그 패턴
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
        
        # SQL 쿼리 패턴
        self.sql_patterns = {
            'tables': [
                re.compile(r'\bFROM\s+([^JOIN]+?)(?=\b(?:JOIN|WHERE|GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
                re.compile(r'\bJOIN\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\b(?:LEFT|RIGHT|FULL|INNER|OUTER|CROSS)\s+JOIN\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\bUPDATE\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\bINSERT\s+(?:INTO\s+)?(\w+(?:\.\w+)?)', re.IGNORECASE),
                re.compile(r'\bDELETE\s+FROM\s+(\w+(?:\.\w+)?)', re.IGNORECASE),
            ],
            'columns': [
                re.compile(r'\bSELECT\s+(.+?)\s+FROM', re.IGNORECASE | re.DOTALL),
                re.compile(r'\b(\w+)\.(\w+)\b', re.IGNORECASE),
                re.compile(r'\b(\w+)\s+AS\s+(\w+)', re.IGNORECASE),
                re.compile(r'\bSET\s+(.+?)(?=\bWHERE\b|$)', re.IGNORECASE | re.DOTALL),
            ],
            'where_conditions': [
                re.compile(r'\bWHERE\s+(.+?)(?=\b(?:GROUP|ORDER|HAVING|$))', re.IGNORECASE | re.DOTALL),
            ],
            'parameters': [
                re.compile(r'#\{([^}]+)\}', re.IGNORECASE),
                re.compile(r'\$\{([^}]+)\}', re.IGNORECASE),
            ]
        }
        
        # MyBatis 설정 패턴
        self.config_patterns = {
            'typeAliases': re.compile(r'<typeAlias\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
            'environments': re.compile(r'<environment\s+([^>]*?)>(.*?)</environment>', re.IGNORECASE | re.DOTALL),
            'dataSource': re.compile(r'<dataSource\s+([^>]*?)>(.*?)</dataSource>', re.IGNORECASE | re.DOTALL),
            'mappers': re.compile(r'<mapper\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
        }
    
    def _get_parser_type(self) -> str:
        return 'mybatis'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        MyBatis XML 파일을 파싱하여 메타데이터 추출 (재현율 우선)
        
        Args:
            content: MyBatis XML 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 1. 기본 SQL 처리
        processed_content = content
        
        # 2. 테이블 별칭 해석
        alias_resolver = get_table_alias_resolver(context.get('default_schema', 'DEFAULT'))
        alias_mapping = alias_resolver.extract_table_alias_mapping(processed_content)
        
        # 3. 정규화 (주석 제거)
        normalized_content = self._remove_comments(processed_content)
        
        result = {
            'sql_units': self._extract_sql_statements_aggressive(normalized_content),
            'dynamic_queries': self._extract_dynamic_queries_aggressive(normalized_content),
            'result_maps': self._extract_result_maps_aggressive(normalized_content),
            'parameter_maps': self._extract_parameter_maps_aggressive(normalized_content),
            'sql_fragments': self._extract_sql_fragments_aggressive(normalized_content),
            'tables': self._extract_tables_aggressive(normalized_content),
            'columns': self._extract_columns_aggressive(normalized_content),
            'parameters': self._extract_parameters_aggressive(normalized_content),
            'mybatis_config': self._extract_mybatis_config_aggressive(normalized_content),
            'file_metadata': {'default_schema': context.get('default_schema', 'DEFAULT')},
            'confidence': 0.9,
            # 동적 쿼리 및 별칭 정보 추가
            'dynamic_blocks': [],
            'alias_mapping': alias_mapping,
            'original_content': content,
            'processed_content': processed_content
        }
        
        # 4. 별칭을 실제 테이블명으로 해석하여 테이블 목록 업데이트
        resolved_tables = set()
        for table in result['tables']:
            resolved_table = alias_resolver.resolve_table_alias(table, alias_mapping)
            resolved_tables.add(resolved_table)
        result['resolved_tables'] = list(resolved_tables)
        
        return result
    
    def _extract_sql_statements_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """SQL 구문을 공격적으로 추출 (재현율 우선)"""
        sql_statements = []
        
        # 1. SELECT 구문 추출
        select_matches = self.mybatis_tags['select'].finditer(content)
        for match in select_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_statements.append({
                'type': 'select',
                'id': self._extract_attribute(attributes, 'id'),
                'parameterType': self._extract_attribute(attributes, 'parameterType'),
                'resultType': self._extract_attribute(attributes, 'resultType'),
                'resultMap': self._extract_attribute(attributes, 'resultMap'),
                'sql_content': sql_content.strip(),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'tables': self._extract_tables_from_sql(sql_content),
                'columns': self._extract_columns_from_sql(sql_content),
                'parameters': self._extract_parameters_from_sql(sql_content)
            })
        
        # 2. INSERT 구문 추출
        insert_matches = self.mybatis_tags['insert'].finditer(content)
        for match in insert_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_statements.append({
                'type': 'insert',
                'id': self._extract_attribute(attributes, 'id'),
                'parameterType': self._extract_attribute(attributes, 'parameterType'),
                'sql_content': sql_content.strip(),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'tables': self._extract_tables_from_sql(sql_content),
                'columns': self._extract_columns_from_sql(sql_content),
                'parameters': self._extract_parameters_from_sql(sql_content)
            })
        
        # 3. UPDATE 구문 추출
        update_matches = self.mybatis_tags['update'].finditer(content)
        for match in update_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_statements.append({
                'type': 'update',
                'id': self._extract_attribute(attributes, 'id'),
                'parameterType': self._extract_attribute(attributes, 'parameterType'),
                'sql_content': sql_content.strip(),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'tables': self._extract_tables_from_sql(sql_content),
                'columns': self._extract_columns_from_sql(sql_content),
                'parameters': self._extract_parameters_from_sql(sql_content)
            })
        
        # 4. DELETE 구문 추출
        delete_matches = self.mybatis_tags['delete'].finditer(content)
        for match in delete_matches:
            attributes = match.group(1)
            sql_content = match.group(2)
            
            sql_statements.append({
                'type': 'delete',
                'id': self._extract_attribute(attributes, 'id'),
                'parameterType': self._extract_attribute(attributes, 'parameterType'),
                'sql_content': sql_content.strip(),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0),
                'tables': self._extract_tables_from_sql(sql_content),
                'columns': self._extract_columns_from_sql(sql_content),
                'parameters': self._extract_parameters_from_sql(sql_content)
            })
        
        return sql_statements
    
    def _extract_dynamic_queries_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """동적 쿼리를 공격적으로 추출 (재현율 우선)"""
        dynamic_queries = []
        
        # 1. if 태그 추출
        if_matches = self.dynamic_tags['if'].finditer(content)
        for match in if_matches:
            test_condition = match.group(1)
            if_content = match.group(2)
            
            dynamic_queries.append({
                'type': 'if',
                'test_condition': test_condition,
                'content': if_content.strip(),
                'full_text': match.group(0),
                'dynamic_type': 'conditional'
            })
        
        # 2. choose-when-otherwise 태그 추출
        choose_matches = self.dynamic_tags['choose'].finditer(content)
        for match in choose_matches:
            choose_content = match.group(1)
            
            # when 태그들 추출
            when_matches = self.dynamic_tags['when'].finditer(choose_content)
            when_clauses = []
            for when_match in when_matches:
                when_clauses.append({
                    'test_condition': when_match.group(1),
                    'content': when_match.group(2).strip()
                })
            
            # otherwise 태그 추출
            otherwise_match = self.dynamic_tags['otherwise'].search(choose_content)
            otherwise_content = otherwise_match.group(1).strip() if otherwise_match else ""
            
            dynamic_queries.append({
                'type': 'choose',
                'when_clauses': when_clauses,
                'otherwise_content': otherwise_content,
                'full_text': match.group(0),
                'dynamic_type': 'switch'
            })
        
        # 3. where 태그 추출
        where_matches = self.dynamic_tags['where'].finditer(content)
        for match in where_matches:
            where_content = match.group(1)
            
            dynamic_queries.append({
                'type': 'where',
                'content': where_content.strip(),
                'full_text': match.group(0),
                'dynamic_type': 'where_clause'
            })
        
        # 4. set 태그 추출
        set_matches = self.dynamic_tags['set'].finditer(content)
        for match in set_matches:
            set_content = match.group(1)
            
            dynamic_queries.append({
                'type': 'set',
                'content': set_content.strip(),
                'full_text': match.group(0),
                'dynamic_type': 'set_clause'
            })
        
        # 5. foreach 태그 추출
        foreach_matches = self.dynamic_tags['foreach'].finditer(content)
        for match in foreach_matches:
            foreach_attrs = match.group(1)
            foreach_content = match.group(2)
            
            dynamic_queries.append({
                'type': 'foreach',
                'collection': self._extract_attribute(foreach_attrs, 'collection'),
                'item': self._extract_attribute(foreach_attrs, 'item'),
                'index': self._extract_attribute(foreach_attrs, 'index'),
                'separator': self._extract_attribute(foreach_attrs, 'separator'),
                'content': foreach_content.strip(),
                'full_text': match.group(0),
                'dynamic_type': 'iteration'
            })
        
        # 6. trim 태그 추출
        trim_matches = self.dynamic_tags['trim'].finditer(content)
        for match in trim_matches:
            trim_attrs = match.group(1)
            trim_content = match.group(2)
            
            dynamic_queries.append({
                'type': 'trim',
                'prefix': self._extract_attribute(trim_attrs, 'prefix'),
                'suffix': self._extract_attribute(trim_attrs, 'suffix'),
                'prefixOverrides': self._extract_attribute(trim_attrs, 'prefixOverrides'),
                'suffixOverrides': self._extract_attribute(trim_attrs, 'suffixOverrides'),
                'content': trim_content.strip(),
                'full_text': match.group(0),
                'dynamic_type': 'trim'
            })
        
        # 7. bind 태그 추출
        bind_matches = self.dynamic_tags['bind'].finditer(content)
        for match in bind_matches:
            bind_attrs = match.group(1)
            
            dynamic_queries.append({
                'type': 'bind',
                'name': self._extract_attribute(bind_attrs, 'name'),
                'value': self._extract_attribute(bind_attrs, 'value'),
                'full_text': match.group(0),
                'dynamic_type': 'variable_binding'
            })
        
        return dynamic_queries
    
    def _extract_result_maps_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """ResultMap을 공격적으로 추출 (재현율 우선)"""
        result_maps = []
        
        result_map_matches = self.mybatis_tags['resultMap'].finditer(content)
        for match in result_map_matches:
            attributes = match.group(1)
            result_map_content = match.group(2)
            
            # result 태그들 추출
            result_pattern = r'<result\s+([^>]*?)>'
            result_matches = re.finditer(result_pattern, result_map_content, re.IGNORECASE)
            results = []
            
            for result_match in result_matches:
                result_attrs = result_match.group(1)
                results.append({
                    'property': self._extract_attribute(result_attrs, 'property'),
                    'column': self._extract_attribute(result_attrs, 'column'),
                    'javaType': self._extract_attribute(result_attrs, 'javaType'),
                    'jdbcType': self._extract_attribute(result_attrs, 'jdbcType'),
                    'attributes': self._parse_xml_attributes(result_attrs)
                })
            
            # association 태그들 추출
            association_pattern = r'<association\s+([^>]*?)>(.*?)</association>'
            association_matches = re.finditer(association_pattern, result_map_content, re.IGNORECASE | re.DOTALL)
            associations = []
            
            for assoc_match in association_matches:
                assoc_attrs = assoc_match.group(1)
                assoc_content = assoc_match.group(2)
                associations.append({
                    'property': self._extract_attribute(assoc_attrs, 'property'),
                    'javaType': self._extract_attribute(assoc_attrs, 'javaType'),
                    'resultMap': self._extract_attribute(assoc_attrs, 'resultMap'),
                    'content': assoc_content.strip(),
                    'attributes': self._parse_xml_attributes(assoc_attrs)
                })
            
            # collection 태그들 추출
            collection_pattern = r'<collection\s+([^>]*?)>(.*?)</collection>'
            collection_matches = re.finditer(collection_pattern, result_map_content, re.IGNORECASE | re.DOTALL)
            collections = []
            
            for coll_match in collection_matches:
                coll_attrs = coll_match.group(1)
                coll_content = coll_match.group(2)
                collections.append({
                    'property': self._extract_attribute(coll_attrs, 'property'),
                    'javaType': self._extract_attribute(coll_attrs, 'javaType'),
                    'resultMap': self._extract_attribute(coll_attrs, 'resultMap'),
                    'content': coll_content.strip(),
                    'attributes': self._parse_xml_attributes(coll_attrs)
                })
            
            result_maps.append({
                'id': self._extract_attribute(attributes, 'id'),
                'type': self._extract_attribute(attributes, 'type'),
                'extends': self._extract_attribute(attributes, 'extends'),
                'results': results,
                'associations': associations,
                'collections': collections,
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0)
            })
        
        return result_maps
    
    def _extract_parameter_maps_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """ParameterMap을 공격적으로 추출 (재현율 우선)"""
        parameter_maps = []
        
        parameter_map_matches = self.mybatis_tags['parameterMap'].finditer(content)
        for match in parameter_map_matches:
            attributes = match.group(1)
            parameter_map_content = match.group(2)
            
            # parameter 태그들 추출
            parameter_pattern = r'<parameter\s+([^>]*?)>'
            parameter_matches = re.finditer(parameter_pattern, parameter_map_content, re.IGNORECASE)
            parameters = []
            
            for param_match in parameter_matches:
                param_attrs = param_match.group(1)
                parameters.append({
                    'property': self._extract_attribute(param_attrs, 'property'),
                    'javaType': self._extract_attribute(param_attrs, 'javaType'),
                    'jdbcType': self._extract_attribute(param_attrs, 'jdbcType'),
                    'mode': self._extract_attribute(param_attrs, 'mode'),
                    'attributes': self._parse_xml_attributes(param_attrs)
                })
            
            parameter_maps.append({
                'id': self._extract_attribute(attributes, 'id'),
                'type': self._extract_attribute(attributes, 'type'),
                'parameters': parameters,
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0)
            })
        
        return parameter_maps
    
    def _extract_sql_fragments_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """SQL 조각을 공격적으로 추출 (재현율 우선)"""
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
                'full_text': match.group(0)
            })
        
        # include 태그 추출
        include_matches = self.mybatis_tags['include'].finditer(content)
        for match in include_matches:
            attributes = match.group(1)
            
            sql_fragments.append({
                'type': 'include',
                'refid': self._extract_attribute(attributes, 'refid'),
                'attributes': self._parse_xml_attributes(attributes),
                'full_text': match.group(0)
            })
        
        return sql_fragments
    
    def _extract_tables_aggressive(self, content: str) -> List[str]:
        """테이블명을 공격적으로 추출 (재현율 우선)"""
        tables = set()
        
        # 모든 SQL 구문에서 테이블 추출
        for sql_stmt in self._extract_sql_statements_aggressive(content):
            tables.update(sql_stmt.get('tables', []))
        
        # 직접적인 테이블 패턴 매칭
        for pattern in self.sql_patterns['tables']:
            matches = pattern.finditer(content)
            for match in matches:
                table_ref = match.group(1).strip()
                # 스키마.테이블 형태에서 테이블명만 추출
                if '.' in table_ref:
                    table_ref = table_ref.split('.')[-1]
                tables.add(table_ref.upper())
        
        return list(tables)
    
    def _extract_columns_aggressive(self, content: str) -> List[str]:
        """컬럼명을 공격적으로 추출 (재현율 우선)"""
        columns = set()
        
        # 모든 SQL 구문에서 컬럼 추출
        for sql_stmt in self._extract_sql_statements_aggressive(content):
            columns.update(sql_stmt.get('columns', []))
        
        # 직접적인 컬럼 패턴 매칭
        for pattern in self.sql_patterns['columns']:
            matches = pattern.finditer(content)
            for match in matches:
                if len(match.groups()) >= 2:
                    table_name = match.group(1)
                    column_name = match.group(2)
                    if not self._is_sql_keyword(table_name):
                        columns.add(f"{table_name.upper()}.{column_name.upper()}")
        
        return list(columns)
    
    def _extract_parameters_aggressive(self, content: str) -> List[str]:
        """파라미터를 공격적으로 추출 (재현율 우선)"""
        parameters = set()
        
        # 모든 SQL 구문에서 파라미터 추출
        for sql_stmt in self._extract_sql_statements_aggressive(content):
            parameters.update(sql_stmt.get('parameters', []))
        
        # 직접적인 파라미터 패턴 매칭
        for pattern in self.sql_patterns['parameters']:
            matches = pattern.finditer(content)
            for match in matches:
                param_name = match.group(1)
                parameters.add(param_name)
        
        return list(parameters)
    
    def _extract_mybatis_config_aggressive(self, content: str) -> Dict[str, Any]:
        """MyBatis 설정을 공격적으로 추출 (재현율 우선)"""
        mybatis_config = {
            'typeAliases': [],
            'environments': [],
            'dataSource': [],
            'mappers': []
        }
        
        # TypeAliases 추출
        type_alias_matches = self.config_patterns['typeAliases'].finditer(content)
        for match in type_alias_matches:
            attributes = match.group(1)
            mybatis_config['typeAliases'].append({
                'alias': self._extract_attribute(attributes, 'alias'),
                'type': self._extract_attribute(attributes, 'type'),
                'attributes': self._parse_xml_attributes(attributes)
            })
        
        # Environments 추출
        environment_matches = self.config_patterns['environments'].finditer(content)
        for match in environment_matches:
            attributes = match.group(1)
            env_content = match.group(2)
            mybatis_config['environments'].append({
                'id': self._extract_attribute(attributes, 'id'),
                'default': self._extract_attribute(attributes, 'default'),
                'content': env_content.strip(),
                'attributes': self._parse_xml_attributes(attributes)
            })
        
        # DataSource 추출
        data_source_matches = self.config_patterns['dataSource'].finditer(content)
        for match in data_source_matches:
            attributes = match.group(1)
            ds_content = match.group(2)
            mybatis_config['dataSource'].append({
                'type': self._extract_attribute(attributes, 'type'),
                'content': ds_content.strip(),
                'attributes': self._parse_xml_attributes(attributes)
            })
        
        # Mappers 추출
        mapper_matches = self.config_patterns['mappers'].finditer(content)
        for match in mapper_matches:
            attributes = match.group(1)
            mybatis_config['mappers'].append({
                'resource': self._extract_attribute(attributes, 'resource'),
                'url': self._extract_attribute(attributes, 'url'),
                'class': self._extract_attribute(attributes, 'class'),
                'attributes': self._parse_xml_attributes(attributes)
            })
        
        return mybatis_config
    
    def _extract_tables_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 테이블명 추출"""
        tables = set()
        
        for pattern in self.sql_patterns['tables']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                table_ref = match.group(1).strip()
                # 스키마.테이블 형태에서 테이블명만 추출
                if '.' in table_ref:
                    table_ref = table_ref.split('.')[-1]
                tables.add(table_ref.upper())
        
        return list(tables)
    
    def _extract_columns_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 컬럼명 추출"""
        columns = set()
        
        for pattern in self.sql_patterns['columns']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                if len(match.groups()) >= 2:
                    table_name = match.group(1)
                    column_name = match.group(2)
                    if not self._is_sql_keyword(table_name):
                        columns.add(f"{table_name.upper()}.{column_name.upper()}")
        
        return list(columns)
    
    def _extract_parameters_from_sql(self, sql_content: str) -> List[str]:
        """SQL 내용에서 파라미터 추출"""
        parameters = set()
        
        for pattern in self.sql_patterns['parameters']:
            matches = pattern.finditer(sql_content)
            for match in matches:
                param_name = match.group(1)
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
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'mybatis'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)
