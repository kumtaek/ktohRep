"""
SQL 조인 분석기

복잡한 SQL 쿼리의 조인 관계를 분석하고 LLM을 활용한 고급 분석을 제공합니다.
"""

import logging
from typing import Dict, List, Any, Optional
from create_metadb.parsers.sql.join_analyzer import SqlJoinAnalyzer as BaseJoinAnalyzer
from create_metadb.llm import LLMClient

class SqlJoinAnalyzer:
    """하이브리드 SQL 조인 분석기 (규칙 기반 + LLM 보조)"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.rule_analyzer = BaseJoinAnalyzer()
        self.logger = logging.getLogger(f"SqlJoinAnalyzer")
        
        # 복잡도 임계값
        self.complexity_threshold = 3  # 조인 수가 3개 이상일 때 LLM 사용
    
    async def analyze_join_relationships(self, sql_content: str) -> List[Dict]:
        """조인 관계 분석 (규칙 기반 + LLM 보조)"""
        try:
            # 1. 규칙 기반 분석
            rule_based_results = self.rule_analyzer.extract_join_relationships(sql_content)
            
            # 2. 복잡도 분석
            complexity_info = self.rule_analyzer.analyze_join_complexity(sql_content)
            
            # 3. 복잡한 쿼리인 경우 LLM 보조 분석
            if (complexity_info['total_joins'] >= self.complexity_threshold and 
                self.llm_client):
                
                self.logger.info(f"복잡한 쿼리 감지 (조인 {complexity_info['total_joins']}개), LLM 분석 시작")
                
                llm_results = await self._analyze_with_llm(sql_content)
                rule_based_results.extend(llm_results)
            
            # 4. 결과 통합 및 정리
            final_results = self._merge_analysis_results(rule_based_results, complexity_info)
            
            self.logger.info(f"조인 관계 분석 완료: {len(final_results)}개")
            return final_results
            
        except Exception as e:
            self.logger.error(f"조인 관계 분석 실패: {e}")
            return []
    
    async def _analyze_with_llm(self, sql_content: str) -> List[Dict]:
        """LLM을 활용한 조인 분석"""
        try:
            if not self.llm_client:
                return []
            
            # LLM 분석 요청
            llm_response = await self.llm_client.analyze_sql_joins(sql_content)
            
            # LLM 응답을 조인 관계 형태로 변환
            llm_relationships = self._convert_llm_response_to_relationships(llm_response)
            
            return llm_relationships
            
        except Exception as e:
            self.logger.error(f"LLM 조인 분석 실패: {e}")
            return []
    
    def _convert_llm_response_to_relationships(self, llm_response: Dict[str, Any]) -> List[Dict]:
        """LLM 응답을 조인 관계 형태로 변환"""
        relationships = []
        
        try:
            join_relationships = llm_response.get('join_relationships', [])
            
            for join_rel in join_relationships:
                relationship = {
                    'join_type': join_rel.get('join_type', 'unknown'),
                    'table_name': join_rel.get('table2', ''),
                    'condition': join_rel.get('condition', ''),
                    'related_tables': [join_rel.get('table1', ''), join_rel.get('table2', '')],
                    'join_columns': [{
                        'table1': join_rel.get('table1', ''),
                        'column1': '',
                        'table2': join_rel.get('table2', ''),
                        'column2': '',
                        'condition_type': 'equality'
                    }],
                    'business_purpose': join_rel.get('business_purpose', ''),
                    'source': 'llm'
                }
                relationships.append(relationship)
            
        except Exception as e:
            self.logger.error(f"LLM 응답 변환 실패: {e}")
        
        return relationships
    
    def _merge_analysis_results(self, rule_results: List[Dict], 
                              complexity_info: Dict[str, Any]) -> List[Dict]:
        """분석 결과 통합"""
        merged_results = []
        
        # 규칙 기반 결과 추가
        for result in rule_results:
            result['source'] = 'rule_based'
            result['complexity_level'] = complexity_info.get('complexity_level', 'unknown')
            merged_results.append(result)
        
        # 중복 제거 (같은 테이블 조합)
        unique_results = []
        seen_combinations = set()
        
        for result in merged_results:
            related_tables = tuple(sorted(result.get('related_tables', [])))
            if related_tables not in seen_combinations:
                seen_combinations.add(related_tables)
                unique_results.append(result)
        
        return unique_results
    
    def get_join_recommendations(self, relationships: List[Dict]) -> List[str]:
        """조인 관계 기반 권장사항 생성"""
        recommendations = []
        
        try:
            # 규칙 기반 권장사항
            rule_recommendations = self.rule_analyzer.get_join_recommendations(relationships)
            recommendations.extend(rule_recommendations)
            
            # 복잡도 기반 권장사항
            complexity_recommendations = self._get_complexity_recommendations(relationships)
            recommendations.extend(complexity_recommendations)
            
            # 비즈니스 목적 기반 권장사항
            business_recommendations = self._get_business_recommendations(relationships)
            recommendations.extend(business_recommendations)
            
        except Exception as e:
            self.logger.error(f"권장사항 생성 실패: {e}")
        
        return list(set(recommendations))  # 중복 제거
    
    def _get_complexity_recommendations(self, relationships: List[Dict]) -> List[str]:
        """복잡도 기반 권장사항"""
        recommendations = []
        
        total_joins = len(relationships)
        
        if total_joins >= 5:
            recommendations.append("매우 복잡한 조인 구조: 쿼리 분할 또는 뷰 생성 고려")
            recommendations.append("성능 최적화를 위한 인덱스 전략 검토 필요")
        elif total_joins >= 3:
            recommendations.append("복잡한 조인 구조: 실행 계획 분석 권장")
        
        # 조인 타입별 권장사항
        join_types = [rel.get('join_type', '') for rel in relationships]
        
        if join_types.count('cross_join') > 0:
            recommendations.append("CROSS JOIN 사용: 카테시안 곱으로 인한 성능 이슈 주의")
        
        if join_types.count('left_join') > 3:
            recommendations.append("LEFT JOIN 다수 사용: 인덱스 최적화 및 NULL 처리 검토")
        
        return recommendations
    
    def _get_business_recommendations(self, relationships: List[Dict]) -> List[str]:
        """비즈니스 목적 기반 권장사항"""
        recommendations = []
        
        # 비즈니스 목적이 있는 조인들 분석
        business_joins = [rel for rel in relationships if rel.get('business_purpose')]
        
        if len(business_joins) < len(relationships) * 0.5:
            recommendations.append("일부 조인의 비즈니스 목적이 불분명: 문서화 필요")
        
        # 테이블별 조인 빈도 분석
        table_join_count = {}
        for rel in relationships:
            for table in rel.get('related_tables', []):
                table_join_count[table] = table_join_count.get(table, 0) + 1
        
        # 자주 조인되는 테이블들
        frequent_tables = [table for table, count in table_join_count.items() if count >= 3]
        if frequent_tables:
            recommendations.append(f"자주 조인되는 테이블들 {frequent_tables}: 관계 최적화 검토")
        
        return recommendations
    
    def generate_join_summary(self, relationships: List[Dict]) -> Dict[str, Any]:
        """조인 관계 요약 생성"""
        summary = {
            'total_joins': len(relationships),
            'join_types': {},
            'tables_involved': set(),
            'complexity_level': 'simple',
            'recommendations': []
        }
        
        try:
            # 조인 타입별 통계
            for rel in relationships:
                join_type = rel.get('join_type', 'unknown')
                summary['join_types'][join_type] = summary['join_types'].get(join_type, 0) + 1
                
                # 관련 테이블들 추가
                summary['tables_involved'].update(rel.get('related_tables', []))
            
            # 복잡도 레벨 결정
            if summary['total_joins'] >= 5:
                summary['complexity_level'] = 'complex'
            elif summary['total_joins'] >= 3:
                summary['complexity_level'] = 'moderate'
            
            # 권장사항 생성
            summary['recommendations'] = self.get_join_recommendations(relationships)
            
            # set을 list로 변환
            summary['tables_involved'] = list(summary['tables_involved'])
            
        except Exception as e:
            self.logger.error(f"조인 요약 생성 실패: {e}")
        
        return summary
