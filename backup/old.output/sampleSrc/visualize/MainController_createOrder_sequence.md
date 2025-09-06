# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:31:49
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_123 as createOrder()
  participant n2_method_21 as createOrder()
  participant n3_method_225 as createOrder()
  participant n4_method_327 as createOrder()
  participant n5_method_429 as createOrder()
  participant n6_method_531 as createOrder()

  n2_method_21->>n1_method_123: inferred_sequence (10%)
  n1_method_123->>n3_method_225: inferred_sequence (10%)
  n3_method_225->>n4_method_327: inferred_sequence (10%)
  n4_method_327->>n5_method_429: inferred_sequence (10%)
  n5_method_429->>n6_method_531: inferred_sequence (10%)
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
  method:21: createOrder() (method)
  method:123: createOrder() (method)
  method:225: createOrder() (method)
  method:327: createOrder() (method)
  method:429: createOrder() (method)
  method:531: createOrder() (method)
```

엣지 목록 (5)
```json
  method:21 -> method:123 (inferred_sequence)
  method:123 -> method:225 (inferred_sequence)
  method:225 -> method:327 (inferred_sequence)
  method:327 -> method:429 (inferred_sequence)
  method:429 -> method:531 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:31:49*