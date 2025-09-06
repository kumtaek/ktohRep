# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:45:55
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_191 as processComplexBus...
  participant n2_method_293 as processComplexBus...
  participant n3_method_395 as processComplexBus...
  participant n4_method_497 as processComplexBus...
  participant n5_method_599 as processComplexBus...
  participant n6_method_89 as processComplexBus...

  n6_method_89->>n1_method_191: inferred_sequence (10%)
  n1_method_191->>n2_method_293: inferred_sequence (10%)
  n2_method_293->>n3_method_395: inferred_sequence (10%)
  n3_method_395->>n4_method_497: inferred_sequence (10%)
  n4_method_497->>n5_method_599: inferred_sequence (10%)
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
  method:89: processComplexBusiness() (method)
  method:191: processComplexBusiness() (method)
  method:293: processComplexBusiness() (method)
  method:395: processComplexBusiness() (method)
  method:497: processComplexBusiness() (method)
  method:599: processComplexBusiness() (method)
```

엣지 목록 (5)
```json
  method:89 -> method:191 (inferred_sequence)
  method:191 -> method:293 (inferred_sequence)
  method:293 -> method:395 (inferred_sequence)
  method:395 -> method:497 (inferred_sequence)
  method:497 -> method:599 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:45:55*