"""
응답 파서

LLM 응답을 파싱하고 구조화된 데이터로 변환합니다.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional

class ResponseParser:
    """LLM 응답 파서"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"ResponseParser")
    
    def parse_summary_response(self, response: str, summary_type: str) -> Dict[str, Any]:
        """요약 응답 파싱"""
        try:
            parsed = {
                'summary_type': summary_type,
                'content': response,
                'sections': self._extract_sections(response),
                'key_points': self._extract_key_points(response),
                'confidence_score': self._calculate_confidence_score(response)
            }
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"요약 응답 파싱 실패: {e}")
            return self._get_fallback_summary(summary_type, response)
    
    def parse_sql_analysis_response(self, response: str) -> Dict[str, Any]:
        """SQL 분석 응답 파싱"""
        try:
            # JSON 응답인지 확인
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # 구조화된 텍스트 응답 파싱
            return self._parse_structured_sql_response(response)
            
        except Exception as e:
            self.logger.error(f"SQL 분석 응답 파싱 실패: {e}")
            return self._get_fallback_sql_analysis()
    
    def parse_relationship_analysis_response(self, response: str) -> Dict[str, Any]:
        """관계 분석 응답 파싱"""
        try:
            parsed = {
                'architecture_position': self._extract_architecture_position(response),
                'dependencies': self._extract_dependencies(response),
                'impact_components': self._extract_impact_components(response),
                'importance_level': self._extract_importance_level(response),
                'recommendations': self._extract_recommendations(response)
            }
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"관계 분석 응답 파싱 실패: {e}")
            return self._get_fallback_relationship_analysis()
    
    def parse_impact_analysis_response(self, response: str) -> Dict[str, Any]:
        """임팩트 분석 응답 파싱"""
        try:
            parsed = {
                'direct_impact': self._extract_direct_impact(response),
                'indirect_impact': self._extract_indirect_impact(response),
                'database_changes': self._extract_database_changes(response),
                'test_changes': self._extract_test_changes(response),
                'deployment_notes': self._extract_deployment_notes(response),
                'risk_level': self._calculate_risk_level(response)
            }
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"임팩트 분석 응답 파싱 실패: {e}")
            return self._get_fallback_impact_analysis()
    
    def parse_learning_path_response(self, response: str) -> Dict[str, Any]:
        """학습 경로 응답 파싱"""
        try:
            parsed = {
                'prerequisites': self._extract_prerequisites(response),
                'learning_steps': self._extract_learning_steps(response),
                'practical_exercises': self._extract_practical_exercises(response),
                'resources': self._extract_resources(response),
                'estimated_time': self._extract_estimated_time(response)
            }
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"학습 경로 응답 파싱 실패: {e}")
            return self._get_fallback_learning_path()
    
    def _extract_sections(self, response: str) -> List[Dict[str, str]]:
        """응답에서 섹션 추출"""
        sections = []
        
        # 번호가 매겨진 섹션 찾기
        section_pattern = r'(\d+)\.\s*([^:]+):\s*([^\n]+(?:\n(?!\d+\.)[^\n]*)*)'
        matches = re.finditer(section_pattern, response, re.MULTILINE)
        
        for match in matches:
            sections.append({
                'number': int(match.group(1)),
                'title': match.group(2).strip(),
                'content': match.group(3).strip()
            })
        
        return sections
    
    def _extract_key_points(self, response: str) -> List[str]:
        """핵심 포인트 추출"""
        key_points = []
        
        # 불릿 포인트나 대시로 시작하는 항목들
        bullet_pattern = r'[-•]\s*([^\n]+)'
        matches = re.findall(bullet_pattern, response)
        key_points.extend(matches)
        
        # 번호가 매겨진 항목들
        numbered_pattern = r'\d+\.\s*([^\n]+)'
        matches = re.findall(numbered_pattern, response)
        key_points.extend(matches)
        
        return [point.strip() for point in key_points if point.strip()]
    
    def _calculate_confidence_score(self, response: str) -> float:
        """신뢰도 점수 계산"""
        # 응답 길이 기반 신뢰도
        length_score = min(len(response) / 500, 1.0)
        
        # 구조화 정도 기반 신뢰도
        structure_score = 0.0
        if re.search(r'\d+\.', response):  # 번호가 매겨진 항목
            structure_score += 0.3
        if re.search(r'[-•]', response):  # 불릿 포인트
            structure_score += 0.2
        if len(self._extract_sections(response)) >= 3:  # 충분한 섹션
            structure_score += 0.3
        if len(self._extract_key_points(response)) >= 3:  # 충분한 핵심 포인트
            structure_score += 0.2
        
        return min(length_score + structure_score, 1.0)
    
    def _parse_structured_sql_response(self, response: str) -> Dict[str, Any]:
        """구조화된 SQL 응답 파싱"""
        parsed = {
            "join_relationships": [],
            "complexity_level": "unknown",
            "recommendations": []
        }
        
        # 조인 관계 추출
        join_pattern = r'(\w+)\s+(?:JOIN|join)\s+(\w+)'
        join_matches = re.finditer(join_pattern, response)
        
        for match in join_matches:
            parsed["join_relationships"].append({
                "table1": match.group(1),
                "table2": match.group(2),
                "join_type": "unknown",
                "condition": "",
                "business_purpose": ""
            })
        
        # 복잡도 레벨 추출
        complexity_pattern = r'(?:복잡도|complexity)[:\s]*(\w+)'
        complexity_match = re.search(complexity_pattern, response, re.IGNORECASE)
        if complexity_match:
            parsed["complexity_level"] = complexity_match.group(1).lower()
        
        # 권장사항 추출
        recommendation_pattern = r'권장사항[:\s]*([^\n]+)'
        recommendation_matches = re.findall(recommendation_pattern, response)
        parsed["recommendations"] = recommendation_matches
        
        return parsed
    
    def _extract_architecture_position(self, response: str) -> str:
        """아키텍처 위치 추출"""
        position_pattern = r'(?:위치|position)[:\s]*([^\n]+)'
        match = re.search(position_pattern, response, re.IGNORECASE)
        return match.group(1).strip() if match else "unknown"
    
    def _extract_dependencies(self, response: str) -> List[str]:
        """의존성 추출"""
        dependency_pattern = r'의존성[:\s]*([^\n]+)'
        match = re.search(dependency_pattern, response, re.IGNORECASE)
        if match:
            return [dep.strip() for dep in match.group(1).split(',')]
        return []
    
    def _extract_impact_components(self, response: str) -> List[str]:
        """영향받는 컴포넌트 추출"""
        impact_pattern = r'영향[:\s]*([^\n]+)'
        match = re.search(impact_pattern, response, re.IGNORECASE)
        if match:
            return [comp.strip() for comp in match.group(1).split(',')]
        return []
    
    def _extract_importance_level(self, response: str) -> str:
        """중요도 레벨 추출"""
        importance_pattern = r'(?:중요도|importance)[:\s]*([^\n]+)'
        match = re.search(importance_pattern, response, re.IGNORECASE)
        return match.group(1).strip() if match else "medium"
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """권장사항 추출"""
        return self._extract_key_points(response)
    
    def _extract_direct_impact(self, response: str) -> List[str]:
        """직접 영향 추출"""
        direct_pattern = r'직접[:\s]*([^\n]+)'
        match = re.search(direct_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_indirect_impact(self, response: str) -> List[str]:
        """간접 영향 추출"""
        indirect_pattern = r'간접[:\s]*([^\n]+)'
        match = re.search(indirect_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_database_changes(self, response: str) -> List[str]:
        """데이터베이스 변경사항 추출"""
        db_pattern = r'데이터베이스[:\s]*([^\n]+)'
        match = re.search(db_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_test_changes(self, response: str) -> List[str]:
        """테스트 변경사항 추출"""
        test_pattern = r'테스트[:\s]*([^\n]+)'
        match = re.search(test_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_deployment_notes(self, response: str) -> List[str]:
        """배포 주의사항 추출"""
        deploy_pattern = r'배포[:\s]*([^\n]+)'
        match = re.search(deploy_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _calculate_risk_level(self, response: str) -> str:
        """위험도 레벨 계산"""
        high_risk_keywords = ['위험', '심각', '중요', 'critical', 'high risk']
        medium_risk_keywords = ['주의', '검토', 'caution', 'medium risk']
        
        response_lower = response.lower()
        
        for keyword in high_risk_keywords:
            if keyword in response_lower:
                return "high"
        
        for keyword in medium_risk_keywords:
            if keyword in response_lower:
                return "medium"
        
        return "low"
    
    def _extract_prerequisites(self, response: str) -> List[str]:
        """선행 학습 사항 추출"""
        prereq_pattern = r'선행[:\s]*([^\n]+)'
        match = re.search(prereq_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_learning_steps(self, response: str) -> List[Dict[str, str]]:
        """학습 단계 추출"""
        steps = []
        step_pattern = r'(\d+)\.\s*([^\n]+)'
        matches = re.finditer(step_pattern, response)
        
        for match in matches:
            steps.append({
                'step': int(match.group(1)),
                'description': match.group(2).strip()
            })
        
        return steps
    
    def _extract_practical_exercises(self, response: str) -> List[str]:
        """실습 방법 추출"""
        exercise_pattern = r'실습[:\s]*([^\n]+)'
        match = re.search(exercise_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_resources(self, response: str) -> List[str]:
        """학습 자료 추출"""
        resource_pattern = r'자료[:\s]*([^\n]+)'
        match = re.search(resource_pattern, response, re.IGNORECASE)
        if match:
            return [item.strip() for item in match.group(1).split(',')]
        return []
    
    def _extract_estimated_time(self, response: str) -> str:
        """예상 학습 시간 추출"""
        time_pattern = r'시간[:\s]*([^\n]+)'
        match = re.search(time_pattern, response, re.IGNORECASE)
        return match.group(1).strip() if match else "미정"
    
    def _get_fallback_summary(self, summary_type: str, response: str) -> Dict[str, Any]:
        """폴백 요약"""
        return {
            'summary_type': summary_type,
            'content': response,
            'sections': [],
            'key_points': [],
            'confidence_score': 0.3
        }
    
    def _get_fallback_sql_analysis(self) -> Dict[str, Any]:
        """폴백 SQL 분석"""
        return {
            "join_relationships": [],
            "complexity_level": "unknown",
            "recommendations": ["수동 분석이 필요합니다."]
        }
    
    def _get_fallback_relationship_analysis(self) -> Dict[str, Any]:
        """폴백 관계 분석"""
        return {
            'architecture_position': "unknown",
            'dependencies': [],
            'impact_components': [],
            'importance_level': "medium",
            'recommendations': []
        }
    
    def _get_fallback_impact_analysis(self) -> Dict[str, Any]:
        """폴백 임팩트 분석"""
        return {
            'direct_impact': [],
            'indirect_impact': [],
            'database_changes': [],
            'test_changes': [],
            'deployment_notes': [],
            'risk_level': "medium"
        }
    
    def _get_fallback_learning_path(self) -> Dict[str, Any]:
        """폴백 학습 경로"""
        return {
            'prerequisites': [],
            'learning_steps': [],
            'practical_exercises': [],
            'resources': [],
            'estimated_time': "미정"
        }
