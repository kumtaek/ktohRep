# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:34:28
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_137 as processPartialRef...
  participant n2_method_239 as processPartialRef...
  participant n3_method_341 as processPartialRef...
  participant n4_method_35 as processPartialRef...
  participant n5_method_443 as processPartialRef...
  participant n6_method_545 as processPartialRef...

  n4_method_35->>n1_method_137: inferred_sequence (10%)
  n1_method_137->>n2_method_239: inferred_sequence (10%)
  n2_method_239->>n3_method_341: inferred_sequence (10%)
  n3_method_341->>n5_method_443: inferred_sequence (10%)
  n5_method_443->>n6_method_545: inferred_sequence (10%)
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
  method:35: processPartialRefund() (method)
  method:137: processPartialRefund() (method)
  method:239: processPartialRefund() (method)
  method:341: processPartialRefund() (method)
  method:443: processPartialRefund() (method)
  method:545: processPartialRefund() (method)
```

엣지 목록 (5)
```json
  method:35 -> method:137 (inferred_sequence)
  method:137 -> method:239 (inferred_sequence)
  method:239 -> method:341 (inferred_sequence)
  method:341 -> method:443 (inferred_sequence)
  method:443 -> method:545 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:34:28*