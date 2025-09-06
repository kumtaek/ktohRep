"""
신뢰도 계산기
리뷰 의견을 반영하여 실제 계산 로직이 구현된 신뢰도 계산 시스템
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import hashlib
from datetime import datetime
from dataclasses import dataclass

from utils.logger import LoggerFactory


@dataclass
class ParseResult:
    """파싱 결과를 담는 데이터 클래스"""
    file_path: str
    parser_type: str
    success: bool
    parse_time: float
    
    # AST 관련
    ast_complete: bool = False
    partial_ast: bool = False
    fallback_used: bool = False
    error_message: Optional[str] = None
    
    # 파싱된 요소들
    classes: int = 0
    methods: int = 0
    sql_units: int = 0
    
    # 패턴 매칭
    matched_patterns: List[str] = None
    total_patterns: int = 0
    
    # DB 스키마 매칭
    referenced_tables: List[str] = None
    confirmed_tables: List[str] = None
    db_matches: bool = False
    
    # 복잡도 요소
    dynamic_sql: bool = False
    reflection_usage: bool = False
    complex_expressions: int = 0
    nested_conditions: int = 0
    
    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []
        if self.referenced_tables is None:
            self.referenced_tables = []
        if self.confirmed_tables is None:
            self.confirmed_tables = []


class ConfidenceCalculator:
    """신뢰도 계산기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = LoggerFactory.get_logger("confidence_calculator")
        
        # 가중치 설정
        confidence_config = config.get('confidence', {})
        self.weights = confidence_config.get('weights', {
            'ast': 0.4,      # AST 분석 품질
            'static': 0.3,   # 정적 규칙 매칭
            'db_match': 0.2, # DB 스키마 매칭
            'heuristic': 0.1 # 휴리스틱 분석
        })
        
        # 복잡도 패널티
        self.complexity_penalties = confidence_config.get('complexity_penalties', {
            'dynamic_sql': 0.15,
            'reflection': 0.25,
            'complex_expression': 0.05,  # per expression
            'nested_condition': 0.03     # per nesting level
        })
        
        # 임계값
        self.thresholds = confidence_config.get('thresholds', {
            'min_confidence': 0.1,
            'max_confidence': 1.0,
            'warning_threshold': 0.5
        })
        
    def calculate_parsing_confidence(self, parse_result: ParseResult) -> Tuple[float, Dict[str, float]]:
        """
        파싱 결과의 신뢰도 계산
        
        Returns:
            Tuple of (final_confidence, factor_breakdown)
        """
        factors = {}
        
        # 1. AST 분석 품질 점수
        ast_score = self._calculate_ast_score(parse_result)
        factors['ast'] = ast_score
        
        # 2. 정적 규칙 매칭 점수
        static_score = self._calculate_static_score(parse_result)
        factors['static'] = static_score
        
        # 3. DB 스키마 매칭 점수
        db_score = self._calculate_db_match_score(parse_result)
        factors['db_match'] = db_score
        
        # 4. 휴리스틱 점수
        heuristic_score = self._calculate_heuristic_score(parse_result)
        factors['heuristic'] = heuristic_score
        
        # 가중 평균 계산
        base_confidence = (
            self.weights['ast'] * ast_score +
            self.weights['static'] * static_score +
            self.weights['db_match'] * db_score +
            self.weights['heuristic'] * heuristic_score
        )
        
        # 복잡도 패널티 계산
        complexity_penalty = self._calculate_complexity_penalty(parse_result)
        factors['complexity_penalty'] = -complexity_penalty
        
        # 최종 신뢰도
        final_confidence = max(
            self.thresholds['min_confidence'],
            min(self.thresholds['max_confidence'], 
                base_confidence - complexity_penalty)
        )
        
        # 로깅
        self.logger.log_confidence_calculation(
            target_type='parsing',
            target_id=hash(parse_result.file_path),
            pre_confidence=base_confidence,
            post_confidence=final_confidence,
            factors=factors
        )
        
        return final_confidence, factors
        
    def _calculate_ast_score(self, parse_result: ParseResult) -> float:
        """AST 분석 품질 점수 계산"""
        if not parse_result.success:
            return 0.0
            
        score = 0.0
        
        # 기본 파싱 성공
        score += 0.3
        
        # AST 완성도
        if parse_result.ast_complete:
            score += 0.5
        elif parse_result.partial_ast:
            score += 0.3
        
        # 폴백 사용 여부 (감점)
        if parse_result.fallback_used:
            score -= 0.2
            
        # 파싱 시간 기반 보정 (빠른 파싱은 보너스)
        if parse_result.parse_time < 1.0:  # 1초 미만
            score += 0.1
        elif parse_result.parse_time > 10.0:  # 10초 초과
            score -= 0.1
            
        # 파싱된 요소 수 기반 보정
        element_count = parse_result.classes + parse_result.methods + parse_result.sql_units
        if element_count > 0:
            score += min(0.1, element_count * 0.01)
            
        return max(0.0, min(1.0, score))
        
    def _calculate_static_score(self, parse_result: ParseResult) -> float:
        """정적 규칙 매칭 점수 계산"""
        if parse_result.total_patterns == 0:
            return 0.5  # 패턴이 없으면 중립
            
        match_ratio = len(parse_result.matched_patterns) / parse_result.total_patterns
        
        # 매칭 비율에 따른 점수
        if match_ratio >= 0.9:
            return 1.0
        elif match_ratio >= 0.7:
            return 0.8
        elif match_ratio >= 0.7:
            return 0.6
        elif match_ratio >= 0.3:
            return 0.4
        else:
            return 0.2
            
    def _calculate_db_match_score(self, parse_result: ParseResult) -> float:
        """DB 스키마 매칭 점수 계산"""
        if not parse_result.referenced_tables:
            return 0.5  # 테이블 참조가 없으면 중립
            
        if not parse_result.db_matches:
            return 0.2  # DB 스키마 정보가 없으면 낮은 점수
            
        # 확인된 테이블 비율
        confirmed_ratio = len(parse_result.confirmed_tables) / len(parse_result.referenced_tables)
        
        # 비율에 따른 점수 계산
        if confirmed_ratio >= 0.95:
            return 1.0
        elif confirmed_ratio >= 0.8:
            return 0.85
        elif confirmed_ratio >= 0.6:
            return 0.7
        elif confirmed_ratio >= 0.4:
            return 0.55
        else:
            return 0.3
            
    def _calculate_heuristic_score(self, parse_result: ParseResult) -> float:
        """휴리스틱 분석 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 파일 확장자 기반 보정
        if parse_result.file_path.endswith('.java'):
            if parse_result.classes > 0 or parse_result.methods > 0:
                score += 0.2
        elif parse_result.file_path.endswith('.xml'):
            if parse_result.sql_units > 0:
                score += 0.2
        elif parse_result.file_path.endswith('.jsp'):
            # JSP는 복잡도가 높으므로 기본 점수 유지
            pass
            
        # 파서 타입별 보정
        if parse_result.parser_type == 'tree_sitter':
            score += 0.1  # Tree-sitter는 더 정확
        elif parse_result.parser_type == 'antlr':
            score += 0.15  # ANTLR은 가장 정확
        elif parse_result.parser_type == 'regex':
            score -= 0.2  # 정규식은 덜 정확
            
        return max(0.0, min(1.0, score))
        
    def _calculate_complexity_penalty(self, parse_result: ParseResult) -> float:
        """복잡도 기반 패널티 계산"""
        penalty = 0.0
        
        # 동적 SQL
        if parse_result.dynamic_sql:
            penalty += self.complexity_penalties['dynamic_sql']
            
        # 리플렉션 사용
        if parse_result.reflection_usage:
            penalty += self.complexity_penalties['reflection']
            
        # 복잡한 표현식
        penalty += parse_result.complex_expressions * self.complexity_penalties['complex_expression']
        
        # 중첩 조건
        penalty += parse_result.nested_conditions * self.complexity_penalties['nested_condition']
        
        return penalty
        
    def calculate_join_confidence(self, join_info: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """조인 조건의 신뢰도 계산"""
        factors = {}
        confidence = 0.0
        
        # 기본 점수
        base_score = 0.3
        factors['base'] = base_score
        confidence += base_score
        
        # 명시적 JOIN vs WHERE 절 조인
        if join_info.get('explicit_join', False):
            join_score = 0.4
            factors['explicit_join'] = join_score
            confidence += join_score
        else:
            join_score = 0.2
            factors['where_join'] = join_score
            confidence += join_score
            
        # 동등 조건 여부
        if join_info.get('equality_condition', True):
            eq_score = 0.2
            factors['equality'] = eq_score
            confidence += eq_score
        else:
            eq_penalty = -0.1
            factors['non_equality'] = eq_penalty
            confidence += eq_penalty
            
        # 테이블명 식별 여부
        if join_info.get('tables_identified', False):
            table_score = 0.15
            factors['tables_identified'] = table_score
            confidence += table_score
        else:
            table_penalty = -0.2
            factors['tables_not_identified'] = table_penalty
            confidence += table_penalty
            
        # 컬럼명 식별 여부
        if join_info.get('columns_identified', False):
            col_score = 0.15
            factors['columns_identified'] = col_score
            confidence += col_score
        else:
            col_penalty = -0.2
            factors['columns_not_identified'] = col_penalty
            confidence += col_penalty
            
        # 동적 조건 존재 여부
        if join_info.get('dynamic_condition', False):
            dynamic_penalty = -0.3
            factors['dynamic_condition'] = dynamic_penalty
            confidence += dynamic_penalty
            
        # PK-FK 관계 확인 여부
        if join_info.get('pk_fk_confirmed', False):
            pk_fk_bonus = 0.2
            factors['pk_fk_confirmed'] = pk_fk_bonus
            confidence += pk_fk_bonus
            
        final_confidence = max(0.0, min(1.0, confidence))
        
        return final_confidence, factors
        
    def calculate_filter_confidence(self, filter_info: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """필터 조건의 신뢰도 계산"""
        factors = {}
        confidence = 0.0
        
        # 기본 점수
        base_score = 0.4
        factors['base'] = base_score
        confidence += base_score
        
        # 항상 적용되는 조건인지
        if filter_info.get('always_applied', False):
            always_score = 0.3
            factors['always_applied'] = always_score
            confidence += always_score
        else:
            conditional_penalty = -0.1
            factors['conditional'] = conditional_penalty
            confidence += conditional_penalty
            
        # 값 타입별 신뢰도
        if filter_info.get('constant_value', False):
            const_score = 0.2
            factors['constant_value'] = const_score
            confidence += const_score
        elif filter_info.get('parameter_value', False):
            param_score = 0.1
            factors['parameter_value'] = param_score
            confidence += param_score
        else:
            complex_penalty = -0.15
            factors['complex_expression'] = complex_penalty
            confidence += complex_penalty
            
        # 연산자 타입별 신뢰도
        operator = filter_info.get('operator', '=')
        if operator in ['=', '!=', '<>', 'IS NULL', 'IS NOT NULL']:
            op_score = 0.15
            factors['simple_operator'] = op_score
            confidence += op_score
        elif operator in ['LIKE', 'IN', 'NOT IN']:
            op_score = 0.1
            factors['pattern_operator'] = op_score
            confidence += op_score
        else:
            op_penalty = -0.05
            factors['complex_operator'] = op_penalty
            confidence += op_penalty
            
        # 테이블.컬럼 형태 여부
        if filter_info.get('qualified_column', False):
            qual_score = 0.15
            factors['qualified_column'] = qual_score
            confidence += qual_score
        else:
            qual_penalty = -0.1
            factors['unqualified_column'] = qual_penalty
            confidence += qual_penalty
            
        final_confidence = max(0.0, min(1.0, confidence))
        
        return final_confidence, factors
        
    def analyze_code_complexity(self, code_content: str) -> Dict[str, Any]:
        """코드 내용 기반 복잡도 분석"""
        complexity_analysis = {
            'dynamic_sql': False,
            'reflection_usage': False,
            'complex_expressions': 0,
            'nested_conditions': 0,
            'lambda_expressions': 0,
            'stream_operations': 0
        }
        
        # 동적 SQL 패턴 감지
        dynamic_sql_patterns = [
            r'\$\{.*?\}',  # MyBatis ${} 패턴
            r'#\{.*?\}',   # MyBatis #{} 패턴 (이건 준동적)
            r'String\s+sql\s*=.*?\+',  # 문자열 연결로 SQL 구성
            r'StringBuilder.*sql',
            r'StringBuffer.*sql'
        ]
        
        for pattern in dynamic_sql_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                complexity_analysis['dynamic_sql'] = True
                break
                
        # 리플렉션 사용 감지
        reflection_patterns = [
            r'\.getClass\(\)',
            r'Class\.forName',
            r'\.getDeclaredMethod',
            r'\.getDeclaredField',
            r'\.newInstance\(\)'
        ]
        
        for pattern in reflection_patterns:
            if re.search(pattern, code_content):
                complexity_analysis['reflection_usage'] = True
                break
                
        # 복잡한 표현식 카운트
        complex_expr_patterns = [
            r'\?\s*:',  # 삼항 연산자
            r'&&.*\|\|',  # 복합 논리 연산
            r'\([^)]*\([^)]*\)',  # 중첩된 괄호
        ]
        
        for pattern in complex_expr_patterns:
            complexity_analysis['complex_expressions'] += len(
                re.findall(pattern, code_content)
            )
            
        # 중첩된 조건문 레벨 계산
        if_count = len(re.findall(r'\bif\s*\(', code_content))
        nested_level = self._calculate_nesting_level(code_content)
        complexity_analysis['nested_conditions'] = max(0, nested_level - 1)
        
        # 람다 표현식
        complexity_analysis['lambda_expressions'] = len(
            re.findall(r'->', code_content)
        )
        
        # Stream API 사용
        complexity_analysis['stream_operations'] = len(
            re.findall(r'\.stream\(\)|\.(map|filter|collect|reduce)\(', code_content)
        )
        
        return complexity_analysis
        
    def _calculate_nesting_level(self, code_content: str) -> int:
        """코드의 최대 중첩 레벨 계산"""
        max_level = 0
        current_level = 0
        
        for char in code_content:
            if char == '{':
                current_level += 1
                max_level = max(max_level, current_level)
            elif char == '}':
                current_level = max(0, current_level - 1)
                
        return max_level
        
    def update_confidence_with_enrichment(self, 
                                        original_confidence: float,
                                        enrichment_result: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """LLM 보강 결과로 신뢰도 업데이트"""
        
        llm_confidence = enrichment_result.get('confidence', 0.5)
        model_quality = enrichment_result.get('model_quality', 0.5)
        evidence_strength = enrichment_result.get('evidence_strength', 0.5)
        
        # 보강 품질 점수 계산
        enrichment_quality = llm_confidence * model_quality * evidence_strength
        
        # 보강 델타 계산 (최대 0.3 향상 또는 0.2 감소)
        if enrichment_quality > 0.5:
            delta = min(0.3, (enrichment_quality - 0.5) * 0.6)
        else:
            delta = max(-0.2, (enrichment_quality - 0.5) * 0.4)
            
        # 최종 신뢰도 계산
        final_confidence = max(
            self.thresholds['min_confidence'],
            min(self.thresholds['max_confidence'], 
                original_confidence + delta)
        )
        
        update_info = {
            'original_confidence': original_confidence,
            'enrichment_quality': enrichment_quality,
            'delta': delta,
            'final_confidence': final_confidence,
            'enrichment_details': enrichment_result
        }
        
        return final_confidence, update_info