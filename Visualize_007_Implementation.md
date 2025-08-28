# 시각화 MD/Mermaid Export 구현 완료 보고서 (Visualize_007)

- 구현 버전: v1.2
- 완료 일시: 2025-08-28
- 기준 문서: Visualize_005_Implementation_plan.md, Visualize_006_Implementation.md, md, mermaid 개발 이력.log

---

## 개요

본 단계에서는 시각화 결과를 Markdown과 Mermaid 형식으로 내보내는 기능을 완성하고, CLI와 메시지 현지화(한글화)를 진행했습니다. 또한 Mermaid 단독(.mmd/.mermaid) 출력도 지원하여 CI/문서 파이프라인에 유연하게 활용 가능하도록 했습니다.

---

## 주요 변경 사항

- visualize/exporters/mermaid_exporter.py
  - 신규 파일 재작성(정리): Mermaid 코드 생성기 + Markdown 문서 빌더 통합
  - export_to_markdown(data, diagram_type, title, metadata): 전체 MD 문서 생성
  - export_mermaid(data, diagram_type): Mermaid 코드만 생성(.mmd 용)
  - 다이어그램 유형 지원: erd, sequence, graph, component
  - ID/라벨 정제, 범례(한글) 및 원본 데이터(소규모) 섹션 포함
  - Mermaid 호환 화살표/에지 표기 정비

- visualize/cli.py
  - --export-mermaid 옵션 확장: 경로 확장자에 따라 .md(전체 문서) 또는 .mmd(Mermaid 코드만) 출력
  - CLI 도움말/로그 한글화, 실행 로그 메시지 정돈

- 시각화 빌더/유틸 한글화(일부)
  - visualize/builders/dependency_graph.py, visualize/builders/erd.py: 진행 로그 한글화
  - visualize/data_access.py, visualize/templates/render.py: 경고/에러 메시지 한글화

---

## 사용 방법

1) 의존성 그래프 HTML + Mermaid/Markdown 동시 출력 예시

```
python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html \
  --kinds use_table,include --min-confidence 0.5 --max-nodes 1000 \
  --export-mermaid visualize/output/graph.md
```

2) Mermaid 코드(.mmd)만 출력 예시(ERD)

```
python visualize_cli.py erd --project-id 1 --out visualize/output/erd.html \
  --export-mermaid visualize/output/erd.mmd
```

3) 시퀀스/컴포넌트 다이어그램도 동일하게 동작

```
python visualize_cli.py sequence --project-id 1 --out visualize/output/seq.html \
  --depth 3 --export-mermaid visualize/output/sequence.md

python visualize_cli.py component --project-id 1 --out visualize/output/comp.html \
  --export-mermaid visualize/output/component.mermaid
```

---

## Mermaid 문법 적용 세부

- ERD: `erDiagram` 문법, 테이블/컬럼 표기, 추론 FK/조인 관계 표시
  - 필수 필터 컬럼: "REQ" 마크
  - 컬럼 과다 시 최대 10개까지 표기(가독성)

- 시퀀스: `sequenceDiagram`
  - 해석된 호출: `->>` / 미해석 호출: `-->>`
  - `participant`로 노드 등록 후 호출 순서대로 메시지 기록

- 의존/컴포넌트 그래프: `graph TD/TB`
  - 해석된 엣지: `A -->|kind| B`
  - 미해석 엣지: `A -. kind .-> B`
  - 타입별 노드 스타일(classDef) 적용

---

## 테스트/검증 요약

- 샘플 DB(data/metadata.db) 기준
  - 각 명령(graph/erd/component/sequence)으로 HTML 렌더링 + Mermaid 내보내기 확인
  - .md 문서와 .mmd 코드가 Mermaid Live Editor에서 파싱되는지 검증(수동)
  - 대형 그래프의 경우 Markdown 원본 데이터 섹션이 자동 생략되는지 확인

---

## 한계/주의 사항

- 매우 큰 그래프에서는 Mermaid 렌더러(뷰어) 성능 제약 가능
- 라벨 길이 제한(기본 20자)으로 말줄임표 처리 → 원본은 MD의 "원본 데이터" 섹션에서 일부 확인 가능
- ERD 컬럼 10개 제한은 가독성 목적이며, 필요 시 설정화 후보

---

## 후속 작업 권고

- 템플릿(HTML) UI 문자열의 완전 한글화 및 일부 글자깨짐(모지바케) 정리
- Mermaid 출력 옵션(레이아웃, 라벨 길이, 컬럼 수) 설정화
- Mermaid/Markdown 산출물 샘플과 README 고도화(스크린샷/예시 추가)

