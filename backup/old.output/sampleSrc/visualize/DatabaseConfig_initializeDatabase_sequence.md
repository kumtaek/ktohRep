# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:28:22
- 노드 수: 7
- 엣지 수: 6

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_105 as initializeDatabase()
  participant n2_method_2 as DatabaseConfig.ge...
  participant n3_method_207 as initializeDatabase()
  participant n4_method_3 as initializeDatabase()
  participant n5_method_309 as initializeDatabase()
  participant n6_method_411 as initializeDatabase()
  participant n7_method_513 as initializeDatabase()

  n4_method_3->>n2_method_2: call (80%)
  n1_method_105->>n2_method_2: call (80%)
  n3_method_207->>n2_method_2: call (80%)
  n5_method_309->>n2_method_2: call (80%)
  n6_method_411->>n2_method_2: call (80%)
  n7_method_513->>n2_method_2: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (7)
```json
  method:3: initializeDatabase() (method)
  method:105: initializeDatabase() (method)
  method:207: initializeDatabase() (method)
  method:309: initializeDatabase() (method)
  method:411: initializeDatabase() (method)
  method:513: initializeDatabase() (method)
  method:2: DatabaseConfig.getConnectionString() (method)
```

엣지 목록 (6)
```json
  method:3 -> method:2 (call)
  method:105 -> method:2 (call)
  method:207 -> method:2 (call)
  method:309 -> method:2 (call)
  method:411 -> method:2 (call)
  method:513 -> method:2 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:28:22*