# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:48:08
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_200 as convertDateFormat()
  participant n2_method_302 as convertDateFormat()
  participant n3_method_404 as convertDateFormat()
  participant n4_method_506 as convertDateFormat()
  participant n5_method_608 as convertDateFormat()
  participant n6_method_98 as convertDateFormat()

  n6_method_98->>n1_method_200: inferred_sequence (10%)
  n1_method_200->>n2_method_302: inferred_sequence (10%)
  n2_method_302->>n3_method_404: inferred_sequence (10%)
  n3_method_404->>n4_method_506: inferred_sequence (10%)
  n4_method_506->>n5_method_608: inferred_sequence (10%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (6)
```json
  method:98: convertDateFormat() (method)
  method:200: convertDateFormat() (method)
  method:302: convertDateFormat() (method)
  method:404: convertDateFormat() (method)
  method:506: convertDateFormat() (method)
  method:608: convertDateFormat() (method)
```

엣지 목록 (5)
```json
  method:98 -> method:200 (inferred_sequence)
  method:200 -> method:302 (inferred_sequence)
  method:302 -> method:404 (inferred_sequence)
  method:404 -> method:506 (inferred_sequence)
  method:506 -> method:608 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:48:08*