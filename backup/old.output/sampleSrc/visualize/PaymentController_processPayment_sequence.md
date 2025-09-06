# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:34:41
- 노드 수: 7
- 엣지 수: 6

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_133 as processPayment()
  participant n2_method_235 as processPayment()
  participant n3_method_31 as processPayment()
  participant n4_method_337 as processPayment()
  participant n5_method_34 as PaymentController...
  participant n6_method_439 as processPayment()
  participant n7_method_541 as processPayment()

  n3_method_31->>n5_method_34: call (80%)
  n1_method_133->>n5_method_34: call (80%)
  n2_method_235->>n5_method_34: call (80%)
  n4_method_337->>n5_method_34: call (80%)
  n6_method_439->>n5_method_34: call (80%)
  n7_method_541->>n5_method_34: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (7)
```json
  method:31: processPayment() (method)
  method:133: processPayment() (method)
  method:235: processPayment() (method)
  method:337: processPayment() (method)
  method:439: processPayment() (method)
  method:541: processPayment() (method)
  method:34: PaymentController.validatePaymentAmount() (method)
```

엣지 목록 (6)
```json
  method:31 -> method:34 (call)
  method:133 -> method:34 (call)
  method:235 -> method:34 (call)
  method:337 -> method:34 (call)
  method:439 -> method:34 (call)
  method:541 -> method:34 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:34:41*