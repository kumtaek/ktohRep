# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:34:53
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_135 as processRefund()
  participant n2_method_237 as processRefund()
  participant n3_method_33 as processRefund()
  participant n4_method_339 as processRefund()
  participant n5_method_441 as processRefund()
  participant n6_method_543 as processRefund()

  n3_method_33->>n1_method_135: inferred_sequence (10%)
  n1_method_135->>n2_method_237: inferred_sequence (10%)
  n2_method_237->>n4_method_339: inferred_sequence (10%)
  n4_method_339->>n5_method_441: inferred_sequence (10%)
  n5_method_441->>n6_method_543: inferred_sequence (10%)
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
  method:33: processRefund() (method)
  method:135: processRefund() (method)
  method:237: processRefund() (method)
  method:339: processRefund() (method)
  method:441: processRefund() (method)
  method:543: processRefund() (method)
```

엣지 목록 (5)
```json
  method:33 -> method:135 (inferred_sequence)
  method:135 -> method:237 (inferred_sequence)
  method:237 -> method:339 (inferred_sequence)
  method:339 -> method:441 (inferred_sequence)
  method:441 -> method:543 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:34:53*