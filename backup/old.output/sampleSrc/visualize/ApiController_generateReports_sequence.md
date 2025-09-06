# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:31:11
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_120 as generateReports()
  participant n2_method_18 as generateReports()
  participant n3_method_222 as generateReports()
  participant n4_method_324 as generateReports()
  participant n5_method_426 as generateReports()
  participant n6_method_528 as generateReports()

  n2_method_18->>n1_method_120: inferred_sequence (10%)
  n1_method_120->>n3_method_222: inferred_sequence (10%)
  n3_method_222->>n4_method_324: inferred_sequence (10%)
  n4_method_324->>n5_method_426: inferred_sequence (10%)
  n5_method_426->>n6_method_528: inferred_sequence (10%)
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
  method:18: generateReports() (method)
  method:120: generateReports() (method)
  method:222: generateReports() (method)
  method:324: generateReports() (method)
  method:426: generateReports() (method)
  method:528: generateReports() (method)
```

엣지 목록 (5)
```json
  method:18 -> method:120 (inferred_sequence)
  method:120 -> method:222 (inferred_sequence)
  method:222 -> method:324 (inferred_sequence)
  method:324 -> method:426 (inferred_sequence)
  method:426 -> method:528 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:31:11*