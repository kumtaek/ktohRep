# PRD 차이점 보고서 (prd_v2_reformatted.md vs 최종 PRD)

본 문서는 `prd_v2_reformatted.md`와 검토 후 작성된 최종 PRD 사이의 차이점을 정리한 보고서입니다.

---

## 1. 임베딩 모델 관련
- **최종본**: 후보 모델만 제시 (BAAI/bge-m3, ko-sentence-transformers, codet5p-770m)
- **검토 PRD**: 한국어 + 코드 이중 모델 전략 또는 BGE 단일 사용 권장

## 2. 재현율 vs 정밀도 정책
- **최종본**: 재현율 우선, 누락 최소화 강조
- **검토 PRD**: API 옵션으로 precision/recall 모드 전환 제안

## 3. 보안 분석/취약점 탐지
- **최종본**: 취약점 테이블 정의 수준
- **검토 PRD**: OWASP Top10 및 사내 보안 기준 매핑 권장

## 4. 시각화 기술 스택
- **최종본**: Neo4j 고려 수준
- **검토 PRD**: 프론트엔드 구현 라이브러리(D3.js, Cytoscape.js)까지 제안

## 5. 파서(Parsing) 기술
- **최종본**: javalang, sqlparse, regex 기반
- **검토 PRD**: JavaParser, tree-sitter, JSQLParser/SQLGlot 등 구체적 제안

## 6. LLM 활용 방식
- **최종본**: 선택적 보강, enrichment log 기록
- **검토 PRD**: Guardrail 구체화 (JSON 출력, temperature=0 고정 등)

---

**결론**: 최종본의 기본 방향은 올바르며, 검토본은 이를 보완해 구체적인 기술 선택 및 운영 가이드를 강화한 차이가 있습니다.
