# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:59
- 노드 수: 4
- 엣지 수: 3

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_62 as getCurrentDate()
  participant n2_unresolved as unresolved: DateT...
  participant n3_unresolved as unresolved: Local...
  participant n4_unresolved as unresolved: com.e...

  n1_method_62->>n3_unresolved: call (80%)
  n1_method_62->>n4_unresolved: call (80%)
  n1_method_62->>n2_unresolved: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (4)
```json
  method:62: getCurrentDate() (method)
  unresolved:LocalDate.now: unresolved: LocalDate.now (unresolved)
  unresolved:com.example.util.DateUtil.format: unresolved: com.example.util.DateUtil.format (unresolved)
  unresolved:DateTimeFormatter.ofPattern: unresolved: DateTimeFormatter.ofPattern (unresolved)
```

엣지 목록 (3)
```json
  method:62 -> unresolved:LocalDate.now (call)
  method:62 -> unresolved:com.example.util.DateUtil.format (call)
  method:62 -> unresolved:DateTimeFormatter.ofPattern (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:59*