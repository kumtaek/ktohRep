# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:35:29
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_139 as getComplexReport()
  participant n2_method_241 as getComplexReport()
  participant n3_method_343 as getComplexReport()
  participant n4_method_37 as getComplexReport()
  participant n5_method_445 as getComplexReport()
  participant n6_method_547 as getComplexReport()

  n4_method_37->>n1_method_139: inferred_sequence (10%)
  n1_method_139->>n2_method_241: inferred_sequence (10%)
  n2_method_241->>n3_method_343: inferred_sequence (10%)
  n3_method_343->>n5_method_445: inferred_sequence (10%)
  n5_method_445->>n6_method_547: inferred_sequence (10%)
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
  method:37: getComplexReport() (method)
  method:139: getComplexReport() (method)
  method:241: getComplexReport() (method)
  method:343: getComplexReport() (method)
  method:445: getComplexReport() (method)
  method:547: getComplexReport() (method)
```

엣지 목록 (5)
```json
  method:37 -> method:139 (inferred_sequence)
  method:139 -> method:241 (inferred_sequence)
  method:241 -> method:343 (inferred_sequence)
  method:343 -> method:445 (inferred_sequence)
  method:445 -> method:547 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:35:29*