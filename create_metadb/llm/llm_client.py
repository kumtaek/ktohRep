"""
LLM 클라이언트

OpenAI API를 통한 LLM 요약 생성 및 분석 기능을 제공합니다.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
import openai
from openai import AsyncOpenAI

class LLMClient:
    """LLM 클라이언트"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"LLMClient")
        
        # OpenAI 클라이언트 초기화
        api_key = os.getenv('LLM_API_KEY') or config.get('api_key')
        if not api_key:
            raise ValueError("LLM API 키가 설정되지 않았습니다. LLM_API_KEY 환경변수를 설정하거나 config에서 api_key를 제공하세요.")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = config.get('max_tokens', 500)
        self.timeout = config.get('timeout', 30)
        
        self.logger.info(f"LLM 클라이언트 초기화 완료: {self.model}")
    
    async def generate_summary(self, code_content: str, code_type: str, 
                             summary_type: str = 'business_purpose') -> str:
        """코드 요약 생성"""
        try:
            prompt = self._build_summary_prompt(code_content, code_type, summary_type)
            
            response = await self._call_llm_api(prompt)
            
            if response:
                return self._parse_summary_response(response, summary_type)
            else:
                return self._get_fallback_summary(code_type, summary_type)
                
        except Exception as e:
            self.logger.error(f"LLM 요약 생성 실패: {e}")
            return self._get_fallback_summary(code_type, summary_type)
    
    async def analyze_sql_joins(self, sql_content: str) -> Dict[str, Any]:
        """SQL 조인 분석 (복잡한 쿼리용)"""
        try:
            prompt = self._build_sql_analysis_prompt(sql_content)
            
            response = await self._call_llm_api(prompt)
            
            if response:
                return self._parse_sql_analysis_response(response)
            else:
                return self._get_fallback_sql_analysis()
                
        except Exception as e:
            self.logger.error(f"SQL 조인 분석 실패: {e}")
            return self._get_fallback_sql_analysis()
    
    async def generate_business_context(self, component_name: str, 
                                      relationships: List[Dict]) -> str:
        """비즈니스 컨텍스트 생성"""
        try:
            prompt = self._build_business_context_prompt(component_name, relationships)
            
            response = await self._call_llm_api(prompt)
            
            if response:
                return response.strip()
            else:
                return f"{component_name}은 시스템의 핵심 컴포넌트입니다."
                
        except Exception as e:
            self.logger.error(f"비즈니스 컨텍스트 생성 실패: {e}")
            return f"{component_name}은 시스템의 핵심 컴포넌트입니다."
    
    async def _call_llm_api(self, prompt: str) -> Optional[str]:
        """LLM API 호출"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 소프트웨어 개발 전문가입니다. 신규입사자가 이해하기 쉽게 설명해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"LLM API 호출 실패: {e}")
            return None
    
    def _build_summary_prompt(self, code_content: str, code_type: str, summary_type: str) -> str:
        """요약 생성 프롬프트 구성"""
        prompts = {
            'business_purpose': f"""
다음 {code_type} 코드의 비즈니스 목적을 신규입사자가 이해하기 쉽게 설명해주세요:

{code_content}

다음 형식으로 답변해주세요:
1. 이 코드는 무엇을 하나요? (핵심 기능)
2. 언제 사용되나요? (사용 시나리오)
3. 신규입사자가 알아야 할 핵심 포인트는?
""",
            'technical_summary': f"""
다음 {code_type} 코드의 기술적 내용을 신규입사자가 이해하기 쉽게 설명해주세요:

{code_content}

다음 형식으로 답변해주세요:
1. 주요 기술 요소는 무엇인가요?
2. 핵심 로직은 어떻게 동작하나요?
3. 주의해야 할 기술적 포인트는?
""",
            'learning_guide': f"""
다음 {code_type} 코드를 신규입사자가 학습할 때 도움이 되는 가이드를 제공해주세요:

{code_content}

다음 형식으로 답변해주세요:
1. 학습 순서는 어떻게 해야 하나요?
2. 관련해서 알아야 할 개념들은?
3. 실습해볼 수 있는 방법은?
"""
        }
        
        return prompts.get(summary_type, prompts['business_purpose'])
    
    def _build_sql_analysis_prompt(self, sql_content: str) -> str:
        """SQL 분석 프롬프트 구성"""
        return f"""
다음 SQL 쿼리의 조인 관계를 분석해주세요:

{sql_content}

다음 JSON 형식으로 답변해주세요:
{{
    "join_relationships": [
        {{
            "table1": "테이블명1",
            "table2": "테이블명2", 
            "join_type": "INNER/LEFT/RIGHT",
            "condition": "조인 조건",
            "business_purpose": "비즈니스 목적"
        }}
    ],
    "complexity_level": "simple/moderate/complex",
    "recommendations": ["권장사항1", "권장사항2"]
}}
"""
    
    def _build_business_context_prompt(self, component_name: str, relationships: List[Dict]) -> str:
        """비즈니스 컨텍스트 프롬프트 구성"""
        relationship_text = "\n".join([
            f"- {rel.get('relationship_type', '')}: {rel.get('target_name', '')}"
            for rel in relationships
        ])
        
        return f"""
{component_name} 컴포넌트의 비즈니스 컨텍스트를 설명해주세요.

관계 정보:
{relationship_text}

다음 관점에서 설명해주세요:
1. 이 컴포넌트의 비즈니스 역할
2. 다른 컴포넌트와의 관계에서의 의미
3. 신규입사자가 이해해야 할 비즈니스 맥락
"""
    
    def _parse_summary_response(self, response: str, summary_type: str) -> str:
        """요약 응답 파싱"""
        # 응답이 너무 길면 요약
        if len(response) > self.max_tokens:
            return response[:self.max_tokens] + "..."
        
        return response.strip()
    
    def _parse_sql_analysis_response(self, response: str) -> Dict[str, Any]:
        """SQL 분석 응답 파싱"""
        try:
            # JSON 응답 파싱 시도
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                # JSON이 아닌 경우 기본 구조로 변환
                return {
                    "join_relationships": [],
                    "complexity_level": "unknown",
                    "recommendations": [response[:200]]
                }
        except json.JSONDecodeError:
            return self._get_fallback_sql_analysis()
    
    def _get_fallback_summary(self, code_type: str, summary_type: str) -> str:
        """폴백 요약 생성"""
        fallbacks = {
            'business_purpose': f"이 {code_type}은 시스템의 핵심 기능을 담당합니다.",
            'technical_summary': f"이 {code_type}은 표준적인 구현 패턴을 따릅니다.",
            'learning_guide': f"이 {code_type}을 이해하려면 관련 기술 문서를 참고하세요."
        }
        
        return fallbacks.get(summary_type, f"이 {code_type}에 대한 요약을 생성할 수 없습니다.")
    
    def _get_fallback_sql_analysis(self) -> Dict[str, Any]:
        """폴백 SQL 분석 결과"""
        return {
            "join_relationships": [],
            "complexity_level": "unknown",
            "recommendations": ["SQL 분석을 위해 수동 검토가 필요합니다."]
        }
