# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:58
- 노드 수: 5
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_63 as convertDateFormat()
  participant n2_unresolved as unresolved: DateT...
  participant n3_unresolved as unresolved: Local...
  participant n4_unresolved as unresolved: Local...
  participant n5_unresolved as unresolved: e.get...

  n1_method_63->>n4_unresolved: call (80%)
  n1_method_63->>n2_unresolved: call (80%)
  n1_method_63->>n3_unresolved: call (80%)
  n1_method_63->>n2_unresolved: call (80%)
  n1_method_63->>n5_unresolved: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (5)
```json
  method:63: convertDateFormat() (method)
  unresolved:LocalDate.parse: unresolved: LocalDate.parse (unresolved)
  unresolved:DateTimeFormatter.ofPattern: unresolved: DateTimeFormatter.ofPattern (unresolved)
  unresolved:LocalDate.format: unresolved: LocalDate.format (unresolved)
  unresolved:e.getMessage: unresolved: e.getMessage (unresolved)
```

엣지 목록 (5)
```json
  method:63 -> unresolved:LocalDate.parse (call)
  method:63 -> unresolved:DateTimeFormatter.ofPattern (call)
  method:63 -> unresolved:LocalDate.format (call)
  method:63 -> unresolved:DateTimeFormatter.ofPattern (call)
  method:63 -> unresolved:e.getMessage (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:58*