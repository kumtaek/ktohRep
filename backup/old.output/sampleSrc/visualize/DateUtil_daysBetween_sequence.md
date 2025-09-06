# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:48:20
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_201 as daysBetween()
  participant n2_method_303 as daysBetween()
  participant n3_method_405 as daysBetween()
  participant n4_method_507 as daysBetween()
  participant n5_method_609 as daysBetween()
  participant n6_method_99 as daysBetween()

  n6_method_99->>n1_method_201: inferred_sequence (10%)
  n1_method_201->>n2_method_303: inferred_sequence (10%)
  n2_method_303->>n3_method_405: inferred_sequence (10%)
  n3_method_405->>n4_method_507: inferred_sequence (10%)
  n4_method_507->>n5_method_609: inferred_sequence (10%)
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
  method:99: daysBetween() (method)
  method:201: daysBetween() (method)
  method:303: daysBetween() (method)
  method:405: daysBetween() (method)
  method:507: daysBetween() (method)
  method:609: daysBetween() (method)
```

엣지 목록 (5)
```json
  method:99 -> method:201 (inferred_sequence)
  method:201 -> method:303 (inferred_sequence)
  method:303 -> method:405 (inferred_sequence)
  method:405 -> method:507 (inferred_sequence)
  method:507 -> method:609 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:48:20*