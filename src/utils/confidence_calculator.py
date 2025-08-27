"""
신뢰도 계산기
정적 분석 결과의 신뢰도를 계산하는 유틸리티
"""

from typing import Dict, List, Any, Optional
import re

class ConfidenceCalculator:
    """분석 결과의 신뢰도를 계산하는 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 신뢰도 가중치 설정
        self.weights = {
            'ast': 0.4,      # AST 기반 분석
            'static': 0.3,   # 정적 규칙 기반
            'db': 0.2,       # DB 스키마 매칭
            'llm': 0.1       # LLM 보강
        }
        
        # 복잡도에 따른 감점 요소
        self.complexity_factors = {
            'dynamic_sql': -0.2,      # 동적 SQL
            'reflection': -0.3,       # 리플렉션 사용
            'complex_expression': -0.1, # 복잡한 표현식
            'dynamic_params': -0.15,  # 동적 파라미터
            'conditional_logic': -0.1  # 조건부 로직
        }
        
    def calculate_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """
        분석 결과의 신뢰도 계산
        
        Args:
            analysis_result: 분석 결과 딕셔너리
            
        Returns:
            신뢰도 점수 (0.0 ~ 1.0)
        """
        
        base_confidence = 0.0
        
        # 각 분석 방법별 신뢰도 계산
        if 'ast_quality' in analysis_result:
            ast_score = self._calculate_ast_confidence(analysis_result['ast_quality'])
            base_confidence += self.weights['ast'] * ast_score
            
        if 'static_rules' in analysis_result:
            static_score = self._calculate_static_confidence(analysis_result['static_rules'])
            base_confidence += self.weights['static'] * static_score
            
        if 'db_match' in analysis_result:
            db_score = self._calculate_db_confidence(analysis_result['db_match'])
            base_confidence += self.weights['db'] * db_score
            
        if 'llm_enrichment' in analysis_result:
            llm_score = self._calculate_llm_confidence(analysis_result['llm_enrichment'])
            base_confidence += self.weights['llm'] * llm_score
            
        # 복잡도 기반 감점 적용
        complexity_penalty = self._calculate_complexity_penalty(analysis_result)
        final_confidence = max(0.0, min(1.0, base_confidence + complexity_penalty))
        
        return final_confidence
        
    def _calculate_ast_confidence(self, ast_quality: Dict[str, Any]) -> float:
        """AST 분석 품질에 따른 신뢰도 계산"""
        
        confidence = 1.0
        
        # 파싱 성공 여부
        if not ast_quality.get('parse_success', True):
            confidence *= 0.3
            
        # AST 노드 완성도
        node_completeness = ast_quality.get('node_completeness', 1.0)
        confidence *= node_completeness
        
        # 타입 정보 존재 여부
        if ast_quality.get('has_type_info', False):
            confidence *= 1.1  # 보너스
        else:
            confidence *= 0.9
            
        # 어노테이션 정보 존재 여부
        if ast_quality.get('has_annotations', False):
            confidence *= 1.05
            
        return min(1.0, confidence)
        
    def _calculate_static_confidence(self, static_rules: Dict[str, Any]) -> float:
        """정적 규칙 기반 신뢰도 계산"""
        
        confidence = 0.5  # 기본값
        
        # 매칭된 패턴 수
        pattern_matches = static_rules.get('pattern_matches', 0)
        if pattern_matches > 0:
            confidence += min(0.4, pattern_matches * 0.1)
            
        # 규칙 적용 성공률
        success_rate = static_rules.get('success_rate', 0.5)
        confidence = confidence * success_rate
        
        # 예외 케이스 존재 여부
        if static_rules.get('has_exceptions', False):
            confidence *= 0.8
            
        return confidence
        
    def _calculate_db_confidence(self, db_match: Dict[str, Any]) -> float:
        """DB 스키마 매칭 신뢰도 계산"""
        
        confidence = 0.0
        
        # 테이블 매칭 여부
        if db_match.get('table_matched', False):
            confidence += 0.5
            
        # 컬럼 매칭 비율
        column_match_rate = db_match.get('column_match_rate', 0.0)
        confidence += 0.3 * column_match_rate
        
        # PK-FK 관계 확인 여부
        if db_match.get('pk_fk_confirmed', False):
            confidence += 0.2
            
        return confidence
        
    def _calculate_llm_confidence(self, llm_enrichment: Dict[str, Any]) -> float:
        """LLM 보강 결과 신뢰도 계산"""
        
        # LLM 자체 신뢰도 점수
        llm_confidence = llm_enrichment.get('confidence', 0.5)
        
        # 사용된 모델에 따른 가중치
        model = llm_enrichment.get('model', 'unknown')
        if '32b' in model.lower():
            llm_confidence *= 1.2  # 큰 모델 보너스
        elif '7b' in model.lower():
            llm_confidence *= 1.0
        else:
            llm_confidence *= 0.8  # 알려지지 않은 모델 페널티
            
        # 검증 가능한 증거 존재 여부
        if llm_enrichment.get('has_evidence', False):
            llm_confidence *= 1.1
        else:
            llm_confidence *= 0.9
            
        return min(1.0, llm_confidence)
        
    def _calculate_complexity_penalty(self, analysis_result: Dict[str, Any]) -> float:
        """복잡도에 따른 감점 계산"""
        
        penalty = 0.0
        
        # 각 복잡도 요소 확인 및 감점 적용
        for factor, score_impact in self.complexity_factors.items():
            if analysis_result.get(factor, False):
                penalty += score_impact
                
        # 추가 복잡도 분석
        if 'code_content' in analysis_result:
            content = analysis_result['code_content']
            penalty += self._analyze_code_complexity(content)
            
        return penalty
        
    def _analyze_code_complexity(self, code_content: str) -> float:
        """코드 내용 기반 복잡도 분석"""
        
        penalty = 0.0
        
        # 동적 SQL 패턴
        if re.search(r'\$\{.*?\}', code_content):
            penalty -= 0.15
            
        # 리플렉션 사용
        if re.search(r'\.getClass\(\)|Class\.forName|\.getDeclaredMethod', code_content):
            penalty -= 0.25
            
        # 복잡한 조건문
        if_count = len(re.findall(r'\bif\b', code_content, re.IGNORECASE))
        if if_count > 5:
            penalty -= min(0.2, (if_count - 5) * 0.02)
            
        # try-catch 블록 (예외 처리가 많으면 복잡)
        try_count = len(re.findall(r'\btry\b', code_content, re.IGNORECASE))
        if try_count > 2:
            penalty -= min(0.1, (try_count - 2) * 0.02)
            
        # 중첩된 루프
        nested_loops = len(re.findall(r'for.*for|while.*while|for.*while|while.*for', 
                                    code_content, re.IGNORECASE | re.DOTALL))
        if nested_loops > 0:
            penalty -= min(0.15, nested_loops * 0.05)
            
        return penalty
        
    def calculate_join_confidence(self, join_info: Dict[str, Any]) -> float:
        """조인 조건의 신뢰도 계산"""
        
        confidence = 0.5  # 기본값
        
        # 명시적 JOIN 키워드 사용
        if join_info.get('explicit_join', False):
            confidence += 0.3
        else:
            confidence += 0.1  # WHERE 절 조인
            
        # 동등 조건 여부
        if join_info.get('equality_condition', False):
            confidence += 0.2
        else:
            confidence -= 0.1  # 비동등 조인은 신뢰도 낮음
            
        # 테이블명 확인 가능 여부
        if join_info.get('tables_identified', False):
            confidence += 0.2
        else:
            confidence -= 0.2
            
        # 컬럼명 확인 가능 여부  
        if join_info.get('columns_identified', False):
            confidence += 0.2
        else:
            confidence -= 0.2
            
        # 동적 조건 존재 여부
        if join_info.get('dynamic_condition', False):
            confidence -= 0.3
            
        return max(0.0, min(1.0, confidence))
        
    def calculate_filter_confidence(self, filter_info: Dict[str, Any]) -> float:
        """필터 조건의 신뢰도 계산"""
        
        confidence = 0.6  # 기본값
        
        # 항상 적용되는 조건인지
        if filter_info.get('always_applied', False):
            confidence += 0.3
        else:
            confidence -= 0.1
            
        # 상수 값 여부
        if filter_info.get('constant_value', False):
            confidence += 0.2
        elif filter_info.get('parameter_value', False):
            confidence += 0.1
        else:
            confidence -= 0.1  # 복잡한 표현식
            
        # 연산자 타입
        operator = filter_info.get('operator', '=')
        if operator in ['=', '!=', '<>', 'IS NULL', 'IS NOT NULL']:
            confidence += 0.1
        elif operator in ['LIKE', 'IN', 'NOT IN']:
            confidence += 0.05
        else:
            confidence -= 0.05
            
        # 테이블.컬럼 형태로 명시되었는지
        if filter_info.get('qualified_column', False):
            confidence += 0.15
        else:
            confidence -= 0.1
            
        return max(0.0, min(1.0, confidence))
        
    def update_confidence_with_enrichment(self, 
                                        original_confidence: float, 
                                        enrichment_result: Dict[str, Any]) -> float:
        """LLM 보강 결과로 신뢰도 업데이트"""
        
        llm_confidence = enrichment_result.get('confidence', 0.5)
        model_quality = enrichment_result.get('model_quality', 0.5)
        evidence_strength = enrichment_result.get('evidence_strength', 0.5)
        
        # 보강 델타 계산
        delta = (llm_confidence * model_quality * evidence_strength - 0.5) * 0.3
        
        # 최종 신뢰도 계산 (최대 1.0을 넘지 않음)
        final_confidence = min(1.0, original_confidence + delta)
        
        return final_confidence