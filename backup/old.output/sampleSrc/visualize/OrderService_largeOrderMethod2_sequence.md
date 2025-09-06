# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:44:41
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_183 as largeOrderMethod2()
  participant n2_method_285 as largeOrderMethod2()
  participant n3_method_387 as largeOrderMethod2()
  participant n4_method_489 as largeOrderMethod2()
  participant n5_method_591 as largeOrderMethod2()
  participant n6_method_81 as largeOrderMethod2()

  n6_method_81->>n1_method_183: inferred_sequence (10%)
  n1_method_183->>n2_method_285: inferred_sequence (10%)
  n2_method_285->>n3_method_387: inferred_sequence (10%)
  n3_method_387->>n4_method_489: inferred_sequence (10%)
  n4_method_489->>n5_method_591: inferred_sequence (10%)
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
  method:81: largeOrderMethod2() (method)
  method:183: largeOrderMethod2() (method)
  method:285: largeOrderMethod2() (method)
  method:387: largeOrderMethod2() (method)
  method:489: largeOrderMethod2() (method)
  method:591: largeOrderMethod2() (method)
```

엣지 목록 (5)
```json
  method:81 -> method:183 (inferred_sequence)
  method:183 -> method:285 (inferred_sequence)
  method:285 -> method:387 (inferred_sequence)
  method:387 -> method:489 (inferred_sequence)
  method:489 -> method:591 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:44:41*