# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:40:57
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_160 as selectOrderById()
  participant n2_method_262 as selectOrderById()
  participant n3_method_364 as selectOrderById()
  participant n4_method_466 as selectOrderById()
  participant n5_method_568 as selectOrderById()
  participant n6_method_58 as selectOrderById()

  n6_method_58->>n1_method_160: inferred_sequence (10%)
  n1_method_160->>n2_method_262: inferred_sequence (10%)
  n2_method_262->>n3_method_364: inferred_sequence (10%)
  n3_method_364->>n4_method_466: inferred_sequence (10%)
  n4_method_466->>n5_method_568: inferred_sequence (10%)
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
  method:58: selectOrderById() (method)
  method:160: selectOrderById() (method)
  method:262: selectOrderById() (method)
  method:364: selectOrderById() (method)
  method:466: selectOrderById() (method)
  method:568: selectOrderById() (method)
```

엣지 목록 (5)
```json
  method:58 -> method:160 (inferred_sequence)
  method:160 -> method:262 (inferred_sequence)
  method:262 -> method:364 (inferred_sequence)
  method:364 -> method:466 (inferred_sequence)
  method:466 -> method:568 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:40:57*