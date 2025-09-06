# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:33:27
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_126 as getOrders()
  participant n2_method_228 as getOrders()
  participant n3_method_24 as getOrders()
  participant n4_method_330 as getOrders()
  participant n5_method_432 as getOrders()
  participant n6_method_534 as getOrders()

  n3_method_24->>n1_method_126: inferred_sequence (10%)
  n1_method_126->>n2_method_228: inferred_sequence (10%)
  n2_method_228->>n4_method_330: inferred_sequence (10%)
  n4_method_330->>n5_method_432: inferred_sequence (10%)
  n5_method_432->>n6_method_534: inferred_sequence (10%)
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
  method:24: getOrders() (method)
  method:126: getOrders() (method)
  method:228: getOrders() (method)
  method:330: getOrders() (method)
  method:432: getOrders() (method)
  method:534: getOrders() (method)
```

엣지 목록 (5)
```json
  method:24 -> method:126 (inferred_sequence)
  method:126 -> method:228 (inferred_sequence)
  method:228 -> method:330 (inferred_sequence)
  method:330 -> method:432 (inferred_sequence)
  method:432 -> method:534 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:33:27*