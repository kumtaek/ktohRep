# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:34:03
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_128 as updateOrderStatus()
  participant n2_method_230 as updateOrderStatus()
  participant n3_method_26 as updateOrderStatus()
  participant n4_method_332 as updateOrderStatus()
  participant n5_method_434 as updateOrderStatus()
  participant n6_method_536 as updateOrderStatus()

  n3_method_26->>n1_method_128: inferred_sequence (10%)
  n1_method_128->>n2_method_230: inferred_sequence (10%)
  n2_method_230->>n4_method_332: inferred_sequence (10%)
  n4_method_332->>n5_method_434: inferred_sequence (10%)
  n5_method_434->>n6_method_536: inferred_sequence (10%)
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
  method:26: updateOrderStatus() (method)
  method:128: updateOrderStatus() (method)
  method:230: updateOrderStatus() (method)
  method:332: updateOrderStatus() (method)
  method:434: updateOrderStatus() (method)
  method:536: updateOrderStatus() (method)
```

엣지 목록 (5)
```json
  method:26 -> method:128 (inferred_sequence)
  method:128 -> method:230 (inferred_sequence)
  method:230 -> method:332 (inferred_sequence)
  method:332 -> method:434 (inferred_sequence)
  method:434 -> method:536 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:34:03*