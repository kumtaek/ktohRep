# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:33:15
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_132 as getOrderStatistics()
  participant n2_method_234 as getOrderStatistics()
  participant n3_method_30 as getOrderStatistics()
  participant n4_method_336 as getOrderStatistics()
  participant n5_method_438 as getOrderStatistics()
  participant n6_method_540 as getOrderStatistics()

  n3_method_30->>n1_method_132: inferred_sequence (10%)
  n1_method_132->>n2_method_234: inferred_sequence (10%)
  n2_method_234->>n4_method_336: inferred_sequence (10%)
  n4_method_336->>n5_method_438: inferred_sequence (10%)
  n5_method_438->>n6_method_540: inferred_sequence (10%)
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
  method:30: getOrderStatistics() (method)
  method:132: getOrderStatistics() (method)
  method:234: getOrderStatistics() (method)
  method:336: getOrderStatistics() (method)
  method:438: getOrderStatistics() (method)
  method:540: getOrderStatistics() (method)
```

엣지 목록 (5)
```json
  method:30 -> method:132 (inferred_sequence)
  method:132 -> method:234 (inferred_sequence)
  method:234 -> method:336 (inferred_sequence)
  method:336 -> method:438 (inferred_sequence)
  method:438 -> method:540 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:33:15*