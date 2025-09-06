# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:43:52
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_179 as calculateOrderTot...
  participant n2_method_281 as calculateOrderTot...
  participant n3_method_383 as calculateOrderTot...
  participant n4_method_485 as calculateOrderTot...
  participant n5_method_587 as calculateOrderTot...
  participant n6_method_77 as calculateOrderTot...

  n6_method_77->>n1_method_179: inferred_sequence (10%)
  n1_method_179->>n2_method_281: inferred_sequence (10%)
  n2_method_281->>n3_method_383: inferred_sequence (10%)
  n3_method_383->>n4_method_485: inferred_sequence (10%)
  n4_method_485->>n5_method_587: inferred_sequence (10%)
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
  method:77: calculateOrderTotal() (method)
  method:179: calculateOrderTotal() (method)
  method:281: calculateOrderTotal() (method)
  method:383: calculateOrderTotal() (method)
  method:485: calculateOrderTotal() (method)
  method:587: calculateOrderTotal() (method)
```

엣지 목록 (5)
```json
  method:77 -> method:179 (inferred_sequence)
  method:179 -> method:281 (inferred_sequence)
  method:281 -> method:383 (inferred_sequence)
  method:383 -> method:485 (inferred_sequence)
  method:485 -> method:587 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:43:52*