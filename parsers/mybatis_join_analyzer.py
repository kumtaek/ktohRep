"""
MyBatis XML JOIN 관계 분석기
MyBatis XML 파일을 분석해서 테이블 간 JOIN 관계를 추출하는 기능
"""
import re
import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

class MyBatisJoinAnalyzer:
    """MyBatis XML에서 JOIN 관계를 분석하는 클래스"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.logger = logging.getLogger(__name__)
    
    def analyze_mybatis_joins(self, project_id: int, xml_file_path: str, 
                            loaded_tables: Dict) -> Dict:
        """
        MyBatis XML 파일에서 JOIN 관계를 분석하여 메타DB에 저장
        
        Args:
            project_id: 프로젝트 ID
            xml_file_path: MyBatis XML 파일 경로
            loaded_tables: 이미 로드된 테이블 정보 {table_name: component_id}
        """
        try:
            # XML 파일 파싱
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            joins_found = []
            dummy_tables_created = {}
            
            # 모든 SQL 쿼리 태그를 분석
            for sql_element in root.findall('.//select') + root.findall('.//update') + \
                              root.findall('.//insert') + root.findall('.//delete'):
                
                # SQL 텍스트 추출 (하위 요소들의 텍스트도 포함)
                sql_text = self._extract_sql_text(sql_element)
                if not sql_text:
                    continue
                
                # JOIN 관계 추출
                join_relationships = self._extract_join_relationships(sql_text)
                
                for join_rel in join_relationships:
                    source_table = join_rel['source_table']
                    target_table = join_rel['target_table']
                    join_type = join_rel['join_type']
                    join_condition = join_rel['join_condition']
                    
                    # 테이블 ID 확인 및 더미 생성
                    source_table_id = self._get_or_create_table(
                        project_id, source_table, loaded_tables, dummy_tables_created
                    )
                    target_table_id = self._get_or_create_table(
                        project_id, target_table, loaded_tables, dummy_tables_created
                    )
                    
                    if source_table_id and target_table_id:
                        # JOIN 관계를 데이터베이스에 저장
                        self.metadata_engine.add_relationship(
                            project_id=project_id,
                            src_component_id=source_table_id,
                            dst_component_id=target_table_id,
                            relationship_type='join',
                            confidence=0.9
                        )
                        
                        joins_found.append({
                            'source_table': source_table,
                            'target_table': target_table,
                            'join_type': join_type,
                            'join_condition': join_condition,
                            'xml_file': Path(xml_file_path).name
                        })
            
            # 중복 제거
            unique_joins = self._remove_duplicate_joins(joins_found)
            
            self.logger.info(f"MyBatis XML에서 {len(unique_joins)}개 JOIN 관계 추출 완료")
            self.logger.info(f"더미 테이블 {len(dummy_tables_created)}개 생성 완료")
            
            return {
                'success': True,
                'joins_found': unique_joins,
                'dummy_tables_created': dummy_tables_created,
                'join_count': len(unique_joins),
                'dummy_table_count': len(dummy_tables_created),
                'xml_file': xml_file_path
            }
            
        except Exception as e:
            self.logger.error(f"MyBatis JOIN 분석 실패 ({xml_file_path}): {e}")
            return {
                'success': False,
                'error': str(e),
                'joins_found': [],
                'dummy_tables_created': {},
                'xml_file': xml_file_path
            }
    
    def _extract_sql_text(self, sql_element) -> str:
        """XML 요소에서 완전한 SQL 텍스트를 추출"""
        def get_all_text(elem):
            text = elem.text or ''
            for child in elem:
                text += get_all_text(child)
                if child.tail:
                    text += child.tail
            return text
        
        sql_text = get_all_text(sql_element)
        # XML 특수 문자 처리
        sql_text = sql_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return sql_text.strip()
    
    def _extract_join_relationships(self, sql_text: str) -> List[Dict]:
        """SQL 텍스트에서 JOIN 관계를 추출 (explicit JOIN과 implicit JOIN 모두 지원)"""
        joins = []
        
        # 1. Explicit JOIN 패턴 정규식들
        explicit_join_patterns = [
            # INNER JOIN table_name alias ON condition
            r'(?:INNER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
            
            # LEFT JOIN table_name alias ON condition  
            r'LEFT\s+(?:OUTER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
            
            # RIGHT JOIN table_name alias ON condition
            r'RIGHT\s+(?:OUTER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
            
            # FULL OUTER JOIN table_name alias ON condition
            r'FULL\s+OUTER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?'
        ]
        
        # FROM 절에서 테이블 추출
        from_match = re.search(r'FROM\s+(.+?)(?:\s+WHERE|\s+LEFT\s+JOIN|\s+RIGHT\s+JOIN|\s+INNER\s+JOIN|\s+JOIN|\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', sql_text, re.IGNORECASE | re.DOTALL)
        
        main_table = None
        all_tables = []
        
        if from_match:
            from_clause = from_match.group(1).strip()
            
            # 2. Implicit JOIN 패턴 검사 (쉼표로 구분된 테이블들)
            if ',' in from_clause and 'JOIN' not in from_clause.upper():
                # Oracle 스타일 implicit join: FROM table1 t1, table2 t2, table3 t3
                table_parts = [part.strip() for part in from_clause.split(',')]
                
                for part in table_parts:
                    # 테이블명과 별칭 추출
                    table_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?', part.strip())
                    if table_match:
                        table_name = table_match.group(1)
                        alias = table_match.group(2) if table_match.group(2) else table_name
                        all_tables.append({'name': table_name, 'alias': alias})
                
                # 첫 번째 테이블을 메인 테이블로, 나머지는 조인 대상으로 처리
                if all_tables:
                    main_table = all_tables[0]['name']
                    
                    # WHERE 절에서 조인 조건 추출
                    where_conditions = self._extract_where_conditions(sql_text)
                    
                    for table_info in all_tables[1:]:
                        # implicit join에서는 WHERE 절 조건을 찾아서 조인 조건으로 사용
                        join_condition = self._find_join_condition(where_conditions, main_table, table_info['name'], all_tables)
                        
                        joins.append({
                            'source_table': main_table,
                            'target_table': table_info['name'],
                            'join_type': 'INNER',  # implicit join은 기본적으로 INNER JOIN
                            'join_condition': join_condition,
                            'target_alias': table_info['alias']
                        })
            else:
                # 단일 테이블 FROM 절
                single_table_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?', from_clause.strip())
                if single_table_match:
                    main_table = single_table_match.group(1)
        
        # 3. Explicit JOIN 패턴 매칭
        for pattern in explicit_join_patterns:
            matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                target_table = match.group(1)
                alias = match.group(2) if match.group(2) else target_table
                join_condition = match.group(3).strip() if match.group(3) else ''
                
                # JOIN 타입 결정
                join_type = 'INNER'
                if 'LEFT' in pattern:
                    join_type = 'LEFT'
                elif 'RIGHT' in pattern:
                    join_type = 'RIGHT'
                elif 'FULL' in pattern:
                    join_type = 'FULL OUTER'
                
                # 메인 테이블과의 관계로 저장
                if main_table and main_table != target_table:
                    joins.append({
                        'source_table': main_table,
                        'target_table': target_table,
                        'join_type': join_type,
                        'join_condition': join_condition,
                        'target_alias': alias
                    })
        
        return joins
    
    def _extract_where_conditions(self, sql_text: str) -> str:
        """WHERE 절 조건을 추출"""
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', 
                               sql_text, re.IGNORECASE | re.DOTALL)
        if where_match:
            return where_match.group(1).strip()
        return ''
    
    def _find_join_condition(self, where_conditions: str, main_table: str, 
                           target_table: str, all_tables: List[Dict]) -> str:
        """WHERE 절에서 두 테이블 간의 조인 조건을 찾음"""
        if not where_conditions:
            return ''
        
        # 테이블명과 별칭 매핑 생성
        table_aliases = {}
        for table_info in all_tables:
            table_aliases[table_info['name']] = table_info['alias']
            table_aliases[table_info['alias']] = table_info['name']
        
        main_alias = table_aliases.get(main_table, main_table)
        target_alias = table_aliases.get(target_table, target_table)
        
        # 조인 조건 패턴들 (Oracle 스타일)
        join_patterns = [
            # t1.id = t2.id 형태
            rf'{main_alias}\.(\w+)\s*=\s*{target_alias}\.(\w+)',
            rf'{target_alias}\.(\w+)\s*=\s*{main_alias}\.(\w+)',
            # table1.id = table2.id 형태
            rf'{main_table}\.(\w+)\s*=\s*{target_table}\.(\w+)',
            rf'{target_table}\.(\w+)\s*=\s*{main_table}\.(\w+)'
        ]
        
        conditions = []
        for pattern in join_patterns:
            matches = re.finditer(pattern, where_conditions, re.IGNORECASE)
            for match in matches:
                conditions.append(match.group(0))
        
        # AND나 OR로 구분된 조건들을 분리하여 관련 조건만 추출
        if conditions:
            return ' AND '.join(conditions)
        
        # 조건을 찾지 못한 경우 전체 WHERE 절 반환 (참고용)
        return f"[implicit join condition from WHERE clause]"
    
    def _get_or_create_table(self, project_id: int, table_name: str, 
                           loaded_tables: Dict, dummy_tables_created: Dict) -> Optional[int]:
        """테이블 ID를 반환하거나 없으면 더미 생성"""
        # 이미 로드된 테이블인지 확인
        if table_name in loaded_tables:
            return loaded_tables[table_name]
        
        # 이미 더미로 생성된 테이블인지 확인
        if table_name in dummy_tables_created:
            return dummy_tables_created[table_name]
        
        # 더미 테이블 생성
        component_id = self.metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name=table_name,
            component_type='table_dummy',
            line_start=None,
            line_end=None
        )
        
        dummy_tables_created[table_name] = component_id
        loaded_tables[table_name] = component_id
        
        # 더미 테이블 비즈니스 태그 (선택적) - component_id가 유효한 경우만
        if component_id:
            try:
                domain = self._classify_table_domain(table_name)
                if domain:
                    self.metadata_engine.add_business_tag(
                        project_id, component_id, domain, 'data_dummy'
                    )
            except Exception as e:
                self.logger.warning(f"더미 테이블 비즈니스 태그 추가 실패: {e}")
        
        self.logger.info(f"JOIN 참조를 위한 더미 테이블 생성: {table_name} (ID: {component_id})")
        return component_id
    
    def _classify_table_domain(self, table_name: str) -> Optional[str]:
        """테이블명으로 비즈니스 도메인 분류"""
        name_lower = table_name.lower()
        
        if any(keyword in name_lower for keyword in ['user', 'member', 'customer', 'account']):
            return 'user'
        elif any(keyword in name_lower for keyword in ['order', 'cart', 'purchase', 'payment']):
            return 'order'
        elif any(keyword in name_lower for keyword in ['product', 'item', 'goods', 'inventory']):
            return 'product'
        elif any(keyword in name_lower for keyword in ['payment', 'billing', 'invoice']):
            return 'payment'
        elif any(keyword in name_lower for keyword in ['category', 'type', 'code', 'status']):
            return 'reference'
        else:
            return None
    
    def _remove_duplicate_joins(self, joins: List[Dict]) -> List[Dict]:
        """중복 JOIN 관계 제거"""
        seen = set()
        unique_joins = []
        
        for join in joins:
            # 양방향 관계를 고려한 키 생성
            key1 = (join['source_table'], join['target_table'], join['join_type'])
            key2 = (join['target_table'], join['source_table'], join['join_type'])
            
            if key1 not in seen and key2 not in seen:
                seen.add(key1)
                unique_joins.append(join)
        
        return unique_joins
    
    def analyze_multiple_mybatis_files(self, project_id: int, xml_directory: str, 
                                     loaded_tables: Dict) -> Dict:
        """여러 MyBatis XML 파일을 한번에 분석"""
        try:
            all_joins = []
            all_dummy_tables = {}
            processed_files = []
            
            xml_files = list(Path(xml_directory).glob('**/*.xml'))
            
            for xml_file in xml_files:
                result = self.analyze_mybatis_joins(
                    project_id, str(xml_file), loaded_tables
                )
                
                if result['success']:
                    all_joins.extend(result['joins_found'])
                    all_dummy_tables.update(result['dummy_tables_created'])
                    processed_files.append(str(xml_file))
            
            # 전체 중복 제거
            unique_joins = self._remove_duplicate_joins(all_joins)
            
            self.logger.info(f"{len(processed_files)}개 MyBatis XML 파일 분석 완료")
            self.logger.info(f"총 {len(unique_joins)}개 고유 JOIN 관계 발견")
            
            return {
                'success': True,
                'joins_found': unique_joins,
                'dummy_tables_created': all_dummy_tables,
                'processed_files': processed_files,
                'join_count': len(unique_joins),
                'dummy_table_count': len(all_dummy_tables),
                'file_count': len(processed_files)
            }
            
        except Exception as e:
            self.logger.error(f"다중 MyBatis 파일 분석 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'joins_found': [],
                'dummy_tables_created': {},
                'processed_files': []
            }