"""
프롬프트 템플릿

LLM 요청을 위한 다양한 프롬프트 템플릿을 제공합니다.
"""

from typing import Dict, List, Any

class PromptTemplates:
    """프롬프트 템플릿 관리자"""
    
    @staticmethod
    def get_class_summary_prompt(class_content: str, class_name: str) -> str:
        """클래스 요약 프롬프트"""
        return f"""
다음 Java 클래스 '{class_name}'의 비즈니스 목적을 신규입사자가 이해하기 쉽게 설명해주세요:

{class_content}

다음 형식으로 답변해주세요:
1. 이 클래스는 무엇을 하나요? (핵심 기능)
2. 언제 사용되나요? (사용 시나리오)
3. 신규입사자가 알아야 할 핵심 포인트는?
4. 관련된 다른 클래스들과의 관계는?
"""
    
    @staticmethod
    def get_method_summary_prompt(method_content: str, method_name: str) -> str:
        """메서드 요약 프롬프트"""
        return f"""
다음 Java 메서드 '{method_name}'의 기능을 신규입사자가 이해하기 쉽게 설명해주세요:

{method_content}

다음 형식으로 답변해주세요:
1. 이 메서드는 무엇을 하나요? (핵심 기능)
2. 입력과 출력은 무엇인가요?
3. 호출하는 곳과 호출되는 곳은?
4. 주의해야 할 예외 상황은?
"""
    
    @staticmethod
    def get_sql_summary_prompt(sql_content: str, sql_name: str) -> str:
        """SQL 요약 프롬프트"""
        return f"""
다음 SQL '{sql_name}'의 비즈니스 목적을 신규입사자가 이해하기 쉽게 설명해주세요:

{sql_content}

다음 형식으로 답변해주세요:
1. 이 쿼리는 무엇을 조회/수정하나요?
2. 어떤 비즈니스 요구사항을 만족하나요?
3. 성능상 주의해야 할 점은?
4. 관련된 테이블들의 관계는?
"""
    
    @staticmethod
    def get_jsp_summary_prompt(jsp_content: str, jsp_name: str) -> str:
        """JSP 요약 프롬프트"""
        return f"""
다음 JSP 페이지 '{jsp_name}'의 기능을 신규입사자가 이해하기 쉽게 설명해주세요:

{jsp_content}

다음 형식으로 답변해주세요:
1. 이 페이지는 무엇을 표시하나요?
2. 사용자와 어떤 상호작용을 하나요?
3. 어떤 데이터를 처리하나요?
4. 관련된 백엔드 컴포넌트는?
"""
    
    @staticmethod
    def get_relationship_analysis_prompt(component_name: str, relationships: List[Dict]) -> str:
        """관계 분석 프롬프트"""
        relationship_text = "\n".join([
            f"- {rel.get('relationship_type', '')}: {rel.get('target_name', '')}"
            for rel in relationships
        ])
        
        return f"""
'{component_name}' 컴포넌트의 관계를 분석해주세요:

관계 정보:
{relationship_text}

다음 관점에서 분석해주세요:
1. 이 컴포넌트의 아키텍처상 위치
2. 의존성 관계의 의미
3. 변경 시 영향받을 수 있는 컴포넌트들
4. 신규입사자가 이해해야 할 관계의 중요도
"""
    
    @staticmethod
    def get_impact_analysis_prompt(component_name: str, change_description: str) -> str:
        """임팩트 분석 프롬프트"""
        return f"""
'{component_name}' 컴포넌트에 다음과 같은 변경을 가할 때의 영향도를 분석해주세요:

변경 내용: {change_description}

다음 관점에서 분석해주세요:
1. 직접적으로 영향받는 컴포넌트들
2. 간접적으로 영향받을 수 있는 컴포넌트들
3. 데이터베이스 스키마 변경 필요성
4. 테스트 케이스 수정 필요성
5. 배포 시 주의사항
"""
    
    @staticmethod
    def get_learning_path_prompt(component_name: str, complexity_level: str) -> str:
        """학습 경로 프롬프트"""
        return f"""
'{component_name}' 컴포넌트(복잡도: {complexity_level})를 신규입사자가 학습할 수 있는 경로를 제안해주세요:

다음 형식으로 답변해주세요:
1. 선행 학습 필요 사항
2. 단계별 학습 순서
3. 실습 방법
4. 관련 문서나 자료
5. 예상 학습 시간
"""
    
    @staticmethod
    def get_code_review_prompt(code_content: str, review_focus: str = "general") -> str:
        """코드 리뷰 프롬프트"""
        focus_guidance = {
            "general": "전반적인 코드 품질",
            "performance": "성능 최적화",
            "security": "보안 취약점",
            "maintainability": "유지보수성",
            "readability": "가독성"
        }
        
        focus = focus_guidance.get(review_focus, "전반적인 코드 품질")
        
        return f"""
다음 코드를 {focus} 관점에서 리뷰해주세요:

{code_content}

다음 형식으로 답변해주세요:
1. 잘된 점
2. 개선이 필요한 점
3. 구체적인 개선 방안
4. 신규입사자가 주의해야 할 점
"""
    
    @staticmethod
    def get_business_flow_prompt(flow_components: List[str]) -> str:
        """비즈니스 플로우 프롬프트"""
        components_text = "\n".join([f"- {comp}" for comp in flow_components])
        
        return f"""
다음 컴포넌트들로 구성된 비즈니스 플로우를 설명해주세요:

{components_text}

다음 형식으로 답변해주세요:
1. 전체 플로우의 목적
2. 각 컴포넌트의 역할
3. 데이터 흐름
4. 예외 처리 방법
5. 신규입사자가 이해해야 할 핵심 포인트
"""
    
    @staticmethod
    def get_troubleshooting_prompt(error_description: str, component_name: str) -> str:
        """문제 해결 프롬프트"""
        return f"""
'{component_name}' 컴포넌트에서 다음과 같은 문제가 발생했습니다:

{error_description}

다음 형식으로 답변해주세요:
1. 가능한 원인들
2. 확인해야 할 사항들
3. 단계별 해결 방법
4. 예방 방법
5. 신규입사자가 주의해야 할 점
"""
