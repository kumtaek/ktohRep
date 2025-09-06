# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:31:36
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_119 as processData()
  participant n2_method_17 as processData()
  participant n3_method_221 as processData()
  participant n4_method_323 as processData()
  participant n5_method_425 as processData()
  participant n6_method_527 as processData()

  n2_method_17->>n1_method_119: inferred_sequence (10%)
  n1_method_119->>n3_method_221: inferred_sequence (10%)
  n3_method_221->>n4_method_323: inferred_sequence (10%)
  n4_method_323->>n5_method_425: inferred_sequence (10%)
  n5_method_425->>n6_method_527: inferred_sequence (10%)
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
  method:17: processData() (method)
  method:119: processData() (method)
  method:221: processData() (method)
  method:323: processData() (method)
  method:425: processData() (method)
  method:527: processData() (method)
```

엣지 목록 (5)
```json
  method:17 -> method:119 (inferred_sequence)
  method:119 -> method:221 (inferred_sequence)
  method:221 -> method:323 (inferred_sequence)
  method:323 -> method:425 (inferred_sequence)
  method:425 -> method:527 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:31:36*