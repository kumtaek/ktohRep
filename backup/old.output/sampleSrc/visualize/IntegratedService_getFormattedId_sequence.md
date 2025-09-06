# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:36:30
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_146 as getFormattedId()
  participant n2_method_248 as getFormattedId()
  participant n3_method_350 as getFormattedId()
  participant n4_method_44 as getFormattedId()
  participant n5_method_452 as getFormattedId()
  participant n6_method_554 as getFormattedId()

  n4_method_44->>n1_method_146: inferred_sequence (10%)
  n1_method_146->>n2_method_248: inferred_sequence (10%)
  n2_method_248->>n3_method_350: inferred_sequence (10%)
  n3_method_350->>n5_method_452: inferred_sequence (10%)
  n5_method_452->>n6_method_554: inferred_sequence (10%)
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
  method:44: getFormattedId() (method)
  method:146: getFormattedId() (method)
  method:248: getFormattedId() (method)
  method:350: getFormattedId() (method)
  method:452: getFormattedId() (method)
  method:554: getFormattedId() (method)
```

엣지 목록 (5)
```json
  method:44 -> method:146 (inferred_sequence)
  method:146 -> method:248 (inferred_sequence)
  method:248 -> method:350 (inferred_sequence)
  method:350 -> method:452 (inferred_sequence)
  method:452 -> method:554 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:36:30*