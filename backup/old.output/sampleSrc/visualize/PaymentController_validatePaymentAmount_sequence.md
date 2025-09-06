# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:35:05
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_136 as validatePaymentAm...
  participant n2_method_238 as validatePaymentAm...
  participant n3_method_34 as validatePaymentAm...
  participant n4_method_340 as validatePaymentAm...
  participant n5_method_442 as validatePaymentAm...
  participant n6_method_544 as validatePaymentAm...

  n3_method_34->>n1_method_136: inferred_sequence (10%)
  n1_method_136->>n2_method_238: inferred_sequence (10%)
  n2_method_238->>n4_method_340: inferred_sequence (10%)
  n4_method_340->>n5_method_442: inferred_sequence (10%)
  n5_method_442->>n6_method_544: inferred_sequence (10%)
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
  method:34: validatePaymentAmount() (method)
  method:136: validatePaymentAmount() (method)
  method:238: validatePaymentAmount() (method)
  method:340: validatePaymentAmount() (method)
  method:442: validatePaymentAmount() (method)
  method:544: validatePaymentAmount() (method)
```

엣지 목록 (5)
```json
  method:34 -> method:136 (inferred_sequence)
  method:136 -> method:238 (inferred_sequence)
  method:238 -> method:340 (inferred_sequence)
  method:340 -> method:442 (inferred_sequence)
  method:442 -> method:544 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:35:05*