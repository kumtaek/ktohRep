"""
Spring Framework 파서
Spring 관련 파일에서 어노테이션, 빈 정의, 의존성 등을 추출합니다.
재현율을 높이기 위해 다양한 패턴을 처리합니다.
"""

import re
from typing import Dict, List, Any, Set
from ..base_parser import BaseParser
from phase1.utils.table_alias_resolver import get_table_alias_resolver

class SpringParser(BaseParser):
    """Spring Framework 전용 파서 - 재현율 우선"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Spring 어노테이션 패턴
        self.spring_annotations = {
            'stereotypes': [
                '@Component', '@Service', '@Repository', '@Controller', '@RestController',
                '@Configuration', '@Bean', '@Autowired', '@Qualifier', '@Value',
                '@RequestMapping', '@GetMapping', '@PostMapping', '@PutMapping', '@DeleteMapping',
                '@PathVariable', '@RequestParam', '@RequestBody', '@ResponseBody',
                '@Transactional', '@Cacheable', '@Scheduled', '@EventListener'
            ],
            'patterns': [
                re.compile(r'@(\w+)(?:\(([^)]*)\))?', re.IGNORECASE),
                re.compile(r'@(\w+)\s*\{([^}]*)\}', re.IGNORECASE | re.DOTALL),
            ]
        }
        
        # Spring XML 설정 패턴
        self.spring_xml_patterns = {
            'bean_definitions': [
                re.compile(r'<bean\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<bean\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'component_scans': [
                re.compile(r'<context:component-scan\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<context:component-scan\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'property_placeholders': [
                re.compile(r'<context:property-placeholder\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<context:property-placeholder\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ],
            'imports': [
                re.compile(r'<import\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
                re.compile(r'<import\s+([^>]*?)/>', re.IGNORECASE | re.DOTALL),
            ]
        }
        
        # Spring Boot 설정 패턴
        self.spring_boot_patterns = {
            'application_properties': [
                re.compile(r'(\w+\.\w+)\s*=\s*(.+)', re.IGNORECASE),
                re.compile(r'(\w+\.\w+)\s*:\s*(.+)', re.IGNORECASE),
            ],
            'application_yml': [
                re.compile(r'(\w+):\s*(.+)', re.IGNORECASE),
                re.compile(r'(\w+\.\w+):\s*(.+)', re.IGNORECASE),
            ]
        }
        
        # 의존성 패턴
        self.dependency_patterns = {
            'maven_dependencies': [
                re.compile(r'<dependency>([^<]*?)</dependency>', re.IGNORECASE | re.DOTALL),
            ],
            'gradle_dependencies': [
                re.compile(r'implementation\s+[\'"]([^\'"]+)[\'"]', re.IGNORECASE),
                re.compile(r'compile\s+[\'"]([^\'"]+)[\'"]', re.IGNORECASE),
                re.compile(r'api\s+[\'"]([^\'"]+)[\'"]', re.IGNORECASE),
            ]
        }
    
    def _get_parser_type(self) -> str:
        return 'spring'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spring 관련 파일을 파싱하여 메타데이터 추출 (재현율 우선)
        
        Args:
            content: Spring 관련 파일 내용
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 1. 기본 SQL 처리
        processed_content = content
        
        # 2. 테이블 별칭 해석
        alias_resolver = get_table_alias_resolver(context.get('default_schema', 'DEFAULT'))
        alias_mapping = alias_resolver.extract_table_alias_mapping(processed_content)
        
        # 3. 정규화
        normalized_content = self._normalize_content(processed_content)
        
        result = {
            'spring_annotations': self._extract_spring_annotations_aggressive(normalized_content),
            'bean_definitions': self._extract_bean_definitions_aggressive(normalized_content),
            'component_scans': self._extract_component_scans_aggressive(normalized_content),
            'property_placeholders': self._extract_property_placeholders_aggressive(normalized_content),
            'spring_boot_config': self._extract_spring_boot_config_aggressive(normalized_content),
            'dependencies': self._extract_dependencies_aggressive(normalized_content),
            'web_endpoints': self._extract_web_endpoints_aggressive(normalized_content),
            'database_config': self._extract_database_config_aggressive(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence,
            # 동적 쿼리 및 별칭 정보 추가
            'dynamic_blocks': dynamic_result.dynamic_blocks,
            'alias_mapping': alias_mapping,
            'original_content': content,
            'processed_content': processed_content
        }
        
        # 4. 별칭을 실제 테이블명으로 해석
        resolved_tables = set()
        for table in dynamic_result.table_references:
            resolved_table = alias_resolver.resolve_table_alias(table, alias_mapping)
            resolved_tables.add(resolved_table)
        result['resolved_tables'] = list(resolved_tables)
        
        return result
    
    def _extract_spring_annotations_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """Spring 어노테이션을 공격적으로 추출 (재현율 우선)"""
        annotations = []
        
        # 1. 모든 어노테이션 추출
        for pattern in self.spring_annotations['patterns']:
            matches = pattern.finditer(content)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                # Spring 관련 어노테이션인지 확인
                is_spring_annotation = any(
                    spring_anno.lower() in annotation_name.lower() 
                    for spring_anno in self.spring_annotations['stereotypes']
                )
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0),
                    'is_spring': is_spring_annotation,
                    'type': 'annotation'
                })
        
        return annotations
    
    def _extract_bean_definitions_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """Bean 정의를 공격적으로 추출 (재현율 우선)"""
        bean_definitions = []
        
        for pattern in self.spring_xml_patterns['bean_definitions']:
            matches = pattern.finditer(content)
            for match in matches:
                bean_attrs = match.group(1)
                attributes = self._parse_xml_attributes(bean_attrs)
                
                bean_definitions.append({
                    'id': attributes.get('id', ''),
                    'class': attributes.get('class', ''),
                    'scope': attributes.get('scope', 'singleton'),
                    'attributes': attributes,
                    'full_text': match.group(0),
                    'type': 'bean_definition'
                })
        
        return bean_definitions
    
    def _extract_component_scans_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """Component Scan을 공격적으로 추출 (재현율 우선)"""
        component_scans = []
        
        for pattern in self.spring_xml_patterns['component_scans']:
            matches = pattern.finditer(content)
            for match in matches:
                scan_attrs = match.group(1)
                attributes = self._parse_xml_attributes(scan_attrs)
                
                component_scans.append({
                    'base_package': attributes.get('base-package', ''),
                    'name_generator': attributes.get('name-generator', ''),
                    'scope_resolver': attributes.get('scope-resolver', ''),
                    'attributes': attributes,
                    'full_text': match.group(0),
                    'type': 'component_scan'
                })
        
        return component_scans
    
    def _extract_property_placeholders_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """Property Placeholder를 공격적으로 추출 (재현율 우선)"""
        property_placeholders = []
        
        for pattern in self.spring_xml_patterns['property_placeholders']:
            matches = pattern.finditer(content)
            for match in matches:
                placeholder_attrs = match.group(1)
                attributes = self._parse_xml_attributes(placeholder_attrs)
                
                property_placeholders.append({
                    'location': attributes.get('location', ''),
                    'file_encoding': attributes.get('file-encoding', ''),
                    'ignore_unresolvable': attributes.get('ignore-unresolvable', 'false'),
                    'attributes': attributes,
                    'full_text': match.group(0),
                    'type': 'property_placeholder'
                })
        
        return property_placeholders
    
    def _extract_spring_boot_config_aggressive(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        """Spring Boot 설정을 공격적으로 추출 (재현율 우선)"""
        spring_boot_config = {
            'properties': [],
            'yml_config': []
        }
        
        # 1. application.properties 형식
        for pattern in self.spring_boot_patterns['application_properties']:
            matches = pattern.finditer(content)
            for match in matches:
                key = match.group(1)
                value = match.group(2)
                
                spring_boot_config['properties'].append({
                    'key': key,
                    'value': value,
                    'type': 'property'
                })
        
        # 2. application.yml 형식
        for pattern in self.spring_boot_patterns['application_yml']:
            matches = pattern.finditer(content)
            for match in matches:
                key = match.group(1)
                value = match.group(2)
                
                spring_boot_config['yml_config'].append({
                    'key': key,
                    'value': value,
                    'type': 'yml'
                })
        
        return spring_boot_config
    
    def _extract_dependencies_aggressive(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        """의존성을 공격적으로 추출 (재현율 우선)"""
        dependencies = {
            'maven': [],
            'gradle': []
        }
        
        # 1. Maven 의존성
        for pattern in self.dependency_patterns['maven_dependencies']:
            matches = pattern.finditer(content)
            for match in matches:
                dependency_content = match.group(1)
                
                # groupId, artifactId, version 추출
                group_id = self._extract_xml_tag_value(dependency_content, 'groupId')
                artifact_id = self._extract_xml_tag_value(dependency_content, 'artifactId')
                version = self._extract_xml_tag_value(dependency_content, 'version')
                scope = self._extract_xml_tag_value(dependency_content, 'scope')
                
                dependencies['maven'].append({
                    'group_id': group_id,
                    'artifact_id': artifact_id,
                    'version': version,
                    'scope': scope or 'compile',
                    'type': 'maven'
                })
        
        # 2. Gradle 의존성
        for pattern in self.dependency_patterns['gradle_dependencies']:
            matches = pattern.finditer(content)
            for match in matches:
                dependency_string = match.group(1)
                
                # group:artifact:version 형식 파싱
                parts = dependency_string.split(':')
                if len(parts) >= 2:
                    group_id = parts[0]
                    artifact_id = parts[1]
                    version = parts[2] if len(parts) > 2 else ''
                    
                    dependencies['gradle'].append({
                        'group_id': group_id,
                        'artifact_id': artifact_id,
                        'version': version,
                        'scope': 'implementation',
                        'type': 'gradle'
                    })
        
        return dependencies
    
    def _extract_web_endpoints_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """웹 엔드포인트를 공격적으로 추출 (재현율 우선)"""
        web_endpoints = []
        
        # Spring MVC 어노테이션 패턴
        endpoint_patterns = [
            r'@RequestMapping\s*\(([^)]*)\)',
            r'@GetMapping\s*\(([^)]*)\)',
            r'@PostMapping\s*\(([^)]*)\)',
            r'@PutMapping\s*\(([^)]*)\)',
            r'@DeleteMapping\s*\(([^)]*)\)',
        ]
        
        for pattern in endpoint_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                mapping_value = match.group(1)
                
                # HTTP 메서드와 경로 추출
                http_method = self._extract_http_method(pattern)
                path = self._extract_path_from_mapping(mapping_value)
                
                web_endpoints.append({
                    'http_method': http_method,
                    'path': path,
                    'mapping_value': mapping_value,
                    'full_text': match.group(0),
                    'type': 'web_endpoint'
                })
        
        return web_endpoints
    
    def _extract_database_config_aggressive(self, content: str) -> Dict[str, Any]:
        """데이터베이스 설정을 공격적으로 추출 (재현율 우선)"""
        database_config = {
            'datasource': {},
            'jpa': {},
            'mybatis': {},
            'hibernate': {}
        }
        
        # 데이터소스 설정 추출
        datasource_patterns = [
            r'spring\.datasource\.(\w+)\s*=\s*(.+)',
            r'spring\.datasource\.(\w+)\s*:\s*(.+)',
        ]
        
        for pattern in datasource_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                key = match.group(1)
                value = match.group(2)
                database_config['datasource'][key] = value
        
        # JPA 설정 추출
        jpa_patterns = [
            r'spring\.jpa\.(\w+)\s*=\s*(.+)',
            r'spring\.jpa\.(\w+)\s*:\s*(.+)',
        ]
        
        for pattern in jpa_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                key = match.group(1)
                value = match.group(2)
                database_config['jpa'][key] = value
        
        # MyBatis 설정 추출
        mybatis_patterns = [
            r'mybatis\.(\w+)\s*=\s*(.+)',
            r'mybatis\.(\w+)\s*:\s*(.+)',
        ]
        
        for pattern in mybatis_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                key = match.group(1)
                value = match.group(2)
                database_config['mybatis'][key] = value
        
        return database_config
    
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
    
    def _extract_xml_tag_value(self, content: str, tag_name: str) -> str:
        """XML 태그에서 특정 태그의 값을 추출"""
        pattern = rf'<{tag_name}>(.*?)</{tag_name}>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''
    
    def _extract_http_method(self, pattern: str) -> str:
        """HTTP 메서드 추출"""
        if 'GetMapping' in pattern:
            return 'GET'
        elif 'PostMapping' in pattern:
            return 'POST'
        elif 'PutMapping' in pattern:
            return 'PUT'
        elif 'DeleteMapping' in pattern:
            return 'DELETE'
        else:
            return 'ANY'
    
    def _extract_path_from_mapping(self, mapping_value: str) -> str:
        """매핑 값에서 경로 추출"""
        # value 속성에서 경로 추출
        value_match = re.search(r'value\s*=\s*["\']([^"\']*)["\']', mapping_value, re.IGNORECASE)
        if value_match:
            return value_match.group(1)
        
        # 경로가 직접 지정된 경우
        path_match = re.search(r'["\']([^"\']*)["\']', mapping_value)
        if path_match:
            return path_match.group(1)
        
        return ''
    
    def _remove_comments(self, content: str) -> str:
        """Spring 관련 주석 제거"""
        # XML 주석 제거
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # Java 주석 제거
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입을 반환"""
        return 'spring'
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구문을 파싱하여 메타데이터를 추출"""
        return self.parse_content(sql_content, context)
