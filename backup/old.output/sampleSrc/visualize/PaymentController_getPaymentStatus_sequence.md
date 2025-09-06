# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:34:15
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_134 as getPaymentStatus()
  participant n2_method_236 as getPaymentStatus()
  participant n3_method_32 as getPaymentStatus()
  participant n4_method_338 as getPaymentStatus()
  participant n5_method_440 as getPaymentStatus()
  participant n6_method_542 as getPaymentStatus()

  n3_method_32->>n1_method_134: inferred_sequence (10%)
  n1_method_134->>n2_method_236: inferred_sequence (10%)
  n2_method_236->>n4_method_338: inferred_sequence (10%)
  n4_method_338->>n5_method_440: inferred_sequence (10%)
  n5_method_440->>n6_method_542: inferred_sequence (10%)
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
  method:32: getPaymentStatus() (method)
  method:134: getPaymentStatus() (method)
  method:236: getPaymentStatus() (method)
  method:338: getPaymentStatus() (method)
  method:440: getPaymentStatus() (method)
  method:542: getPaymentStatus() (method)
```

엣지 목록 (5)
```json
  method:32 -> method:134 (inferred_sequence)
  method:134 -> method:236 (inferred_sequence)
  method:236 -> method:338 (inferred_sequence)
  method:338 -> method:440 (inferred_sequence)
  method:440 -> method:542 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:34:15*