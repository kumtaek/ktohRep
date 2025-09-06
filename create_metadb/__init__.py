"""
Create MetaDB - 신규입사자 지원을 위한 최적화된 메타정보 생성 시스템

이 패키지는 기존 phase1 시스템과 완전히 독립적으로 동작하며,
성능 최적화와 신규입사자 지원에 특화된 메타정보를 생성합니다.

주요 기능:
- 핵심 관계 추출 (calls, dependency, import, foreign_key, join)
- SQL 조인 관계 분석 (규칙 기반 + LLM 보조)
- LLM 요약 생성 (비즈니스 목적, 기술적 내용, 학습 가이드)
- 비즈니스 분류 (도메인, 아키텍처 레이어, 기능 카테고리)
- 변동분 처리 (해시값 비교로 변경된 파일만 분석)
- 삭제 관리 (논리적 삭제 플래그)
"""

__version__ = "1.0.0"
__author__ = "SourceAnalyzer Team"
__description__ = "Optimized metadata generation system for new hire support"

# 환경 변수 설정
import os
CREATE_METADB_PATH = os.path.dirname(os.path.abspath(__file__))
