# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:47:44
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_102 as helper()
  participant n2_method_204 as helper()
  participant n3_method_306 as helper()
  participant n4_method_408 as helper()
  participant n5_method_510 as helper()
  participant n6_method_612 as helper()

  n1_method_102->>n2_method_204: inferred_sequence (10%)
  n2_method_204->>n3_method_306: inferred_sequence (10%)
  n3_method_306->>n4_method_408: inferred_sequence (10%)
  n4_method_408->>n5_method_510: inferred_sequence (10%)
  n5_method_510->>n6_method_612: inferred_sequence (10%)
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
  method:102: helper() (method)
  method:204: helper() (method)
  method:306: helper() (method)
  method:408: helper() (method)
  method:510: helper() (method)
  method:612: helper() (method)
```

엣지 목록 (5)
```json
  method:102 -> method:204 (inferred_sequence)
  method:204 -> method:306 (inferred_sequence)
  method:306 -> method:408 (inferred_sequence)
  method:408 -> method:510 (inferred_sequence)
  method:510 -> method:612 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:47:44*