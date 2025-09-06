# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:29:40
- 노드 수: 7
- 엣지 수: 6

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_116 as getClientIP()
  participant n2_method_14 as getClientIP()
  participant n3_method_15 as SecurityConfig.ge...
  participant n4_method_218 as getClientIP()
  participant n5_method_320 as getClientIP()
  participant n6_method_422 as getClientIP()
  participant n7_method_524 as getClientIP()

  n2_method_14->>n3_method_15: call (80%)
  n1_method_116->>n3_method_15: call (80%)
  n4_method_218->>n3_method_15: call (80%)
  n5_method_320->>n3_method_15: call (80%)
  n6_method_422->>n3_method_15: call (80%)
  n7_method_524->>n3_method_15: call (80%)
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
  method:14: getClientIP() (method)
  method:116: getClientIP() (method)
  method:218: getClientIP() (method)
  method:320: getClientIP() (method)
  method:422: getClientIP() (method)
  method:524: getClientIP() (method)
  method:15: SecurityConfig.getCurrentRequest() (method)
```

엣지 목록 (6)
```json
  method:14 -> method:15 (call)
  method:116 -> method:15 (call)
  method:218 -> method:15 (call)
  method:320 -> method:15 (call)
  method:422 -> method:15 (call)
  method:524 -> method:15 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:29:40*