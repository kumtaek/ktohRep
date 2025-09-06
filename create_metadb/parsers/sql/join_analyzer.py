"""
SQL 조인 분석기

SQL 쿼리에서 조인 관계를 분석하여 테이블 간 관계를 추출합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class SqlJoinAnalyzer:
    """SQL 조인 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"SqlJoinAnalyzer")
        
        # 조인 패턴 정의
        self.join_patterns = {
            'inner_join': r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'left_join': r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'right_join': r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'full_join': r'FULL\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'cross_join': r'CROSS\s+JOIN\s+(\w+)',
            'join': r'JOIN\s+(\w+)\s+ON\s+([^)]+)'  # 기본 JOIN
        }
        
        # 테이블 별칭 패턴
        self.alias_pattern = r'(\w+)\s+AS\s+(\w+)'
        
        # 조인 조건 패턴
        self.condition_patterns = {
            'equality': r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',
            'inequality': r'(\w+)\.(\w+)\s*[<>]=?\s*(\w+)\.(\w+)',
            'like': r'(\w+)\.(\w+)\s+LIKE\s+(\w+)\.(\w+)',
            'in': r'(\w+)\.(\w+)\s+IN\s*\([^)]+\)'
        }
    
    def extract_join_relationships(self, sql_content: str) -> List[Dict]:
        """SQL에서 조인 관계 추출"""
        relationships = []
        
        try:
            # 1. 테이블 별칭 매핑 생성
            alias_mapping = self._extract_table_aliases(sql_content)
            
            # 2. 각 조인 타입별로 분석
            for join_type, pattern in self.join_patterns.items():
                matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.DOTALL)
                
                for match in matches:
                    if join_type == 'cross_join':
                        # CROSS JOIN은 조건이 없음
                        table_name = match.group(1)
                        relationship = self._create_join_relationship(
                            join_type, table_name, '', alias_mapping
                        )
                    else:
                        # 일반 JOIN은 조건이 있음
                        table_name = match.group(1)
                        join_condition = match.group(2)
                        relationship = self._create_join_relationship(
                            join_type, table_name, join_condition, alias_mapping
                        )
                    
                    if relationship:
                        relationships.append(relationship)
            
            self.logger.info(f"조인 관계 추출 완료: {len(relationships)}개")
            
        except Exception as e:
            self.logger.error(f"조인 관계 추출 실패: {e}")
        
        return relationships
    
    def _extract_table_aliases(self, sql_content: str) -> Dict[str, str]:
        """테이블 별칭 매핑 추출"""
        alias_mapping = {}
        
        # FROM 절에서 별칭 추출
        from_pattern = r'FROM\s+(\w+)(?:\s+AS\s+(\w+))?'
        from_matches = re.finditer(from_pattern, sql_content, re.IGNORECASE)
        
        for match in from_matches:
            table_name = match.group(1)
            alias = match.group(2) if match.group(2) else table_name
            alias_mapping[alias] = table_name
        
        # JOIN 절에서 별칭 추출
        for join_type, pattern in self.join_patterns.items():
            if join_type == 'cross_join':
                continue
                
            matches = re.finditer(pattern, sql_content, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                # 별칭이 있는지 확인
                alias_match = re.search(self.alias_pattern, match.group(0), re.IGNORECASE)
                if alias_match:
                    alias = alias_match.group(2)
                    alias_mapping[alias] = table_name
                else:
                    alias_mapping[table_name] = table_name
        
        return alias_mapping
    
    def _create_join_relationship(self, join_type: str, table_name: str, 
                                join_condition: str, alias_mapping: Dict[str, str]) -> Optional[Dict]:
        """조인 관계 객체 생성"""
        try:
            # 테이블명 정규화 (별칭 해결)
            actual_table = alias_mapping.get(table_name, table_name)
            
            relationship = {
                'join_type': join_type,
                'table_name': actual_table,
                'alias': table_name if table_name != actual_table else None,
                'condition': join_condition,
                'related_tables': [],
                'join_columns': []
            }
            
            # 조인 조건 분석
            if join_condition:
                self._analyze_join_condition(join_condition, relationship, alias_mapping)
            
            return relationship
            
        except Exception as e:
            self.logger.error(f"조인 관계 생성 실패: {e}")
            return None
    
    def _analyze_join_condition(self, condition: str, relationship: Dict, alias_mapping: Dict[str, str]):
        """조인 조건 분석"""
        # 등호 조건 분석
        equality_matches = re.finditer(self.condition_patterns['equality'], condition, re.IGNORECASE)
        
        for match in equality_matches:
            table1_alias = match.group(1)
            column1 = match.group(2)
            table2_alias = match.group(3)
            column2 = match.group(4)
            
            # 실제 테이블명으로 변환
            actual_table1 = alias_mapping.get(table1_alias, table1_alias)
            actual_table2 = alias_mapping.get(table2_alias, table2_alias)
            
            # 관련 테이블 추가
            if actual_table1 not in relationship['related_tables']:
                relationship['related_tables'].append(actual_table1)
            if actual_table2 not in relationship['related_tables']:
                relationship['related_tables'].append(actual_table2)
            
            # 조인 컬럼 정보 추가
            join_column = {
                'table1': actual_table1,
                'column1': column1,
                'table2': actual_table2,
                'column2': column2,
                'condition_type': 'equality'
            }
            relationship['join_columns'].append(join_column)
    
    def analyze_join_complexity(self, sql_content: str) -> Dict[str, Any]:
        """조인 복잡도 분석"""
        complexity_info = {
            'total_joins': 0,
            'join_types': {},
            'table_count': 0,
            'complexity_level': 'simple'
        }
        
        try:
            # 조인 수 계산
            for join_type, pattern in self.join_patterns.items():
                matches = list(re.finditer(pattern, sql_content, re.IGNORECASE))
                count = len(matches)
                complexity_info['join_types'][join_type] = count
                complexity_info['total_joins'] += count
            
            # 테이블 수 계산
            tables = set()
            for join_type, pattern in self.join_patterns.items():
                matches = re.finditer(pattern, sql_content, re.IGNORECASE)
                for match in matches:
                    table_name = match.group(1)
                    tables.add(table_name)
            
            # FROM 절의 테이블도 추가
            from_matches = re.finditer(r'FROM\s+(\w+)', sql_content, re.IGNORECASE)
            for match in from_matches:
                tables.add(match.group(1))
            
            complexity_info['table_count'] = len(tables)
            
            # 복잡도 레벨 결정
            if complexity_info['total_joins'] >= 5 or complexity_info['table_count'] >= 6:
                complexity_info['complexity_level'] = 'complex'
            elif complexity_info['total_joins'] >= 3 or complexity_info['table_count'] >= 4:
                complexity_info['complexity_level'] = 'moderate'
            else:
                complexity_info['complexity_level'] = 'simple'
            
        except Exception as e:
            self.logger.error(f"조인 복잡도 분석 실패: {e}")
        
        return complexity_info
    
    def get_join_recommendations(self, relationships: List[Dict]) -> List[str]:
        """조인 관계 기반 권장사항 생성"""
        recommendations = []
        
        try:
            # 조인 타입별 권장사항
            join_types = [rel['join_type'] for rel in relationships]
            
            if 'cross_join' in join_types:
                recommendations.append("CROSS JOIN 사용 시 주의: 카테시안 곱으로 인한 성능 이슈 가능")
            
            if join_types.count('left_join') > 3:
                recommendations.append("LEFT JOIN이 많습니다: 인덱스 최적화 검토 필요")
            
            if len(relationships) > 5:
                recommendations.append("복잡한 조인 구조: 쿼리 분할 또는 뷰 생성 고려")
            
            # 조인 컬럼 분석
            for rel in relationships:
                if not rel['join_columns']:
                    recommendations.append(f"테이블 {rel['table_name']}: 조인 조건이 명확하지 않음")
            
        except Exception as e:
            self.logger.error(f"조인 권장사항 생성 실패: {e}")
        
        return recommendations
