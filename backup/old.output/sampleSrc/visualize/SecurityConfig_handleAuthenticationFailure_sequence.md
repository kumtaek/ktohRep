# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:30:05
- 노드 수: 8
- 엣지 수: 12

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_115 as handleAuthenticat...
  participant n2_method_13 as handleAuthenticat...
  participant n3_method_14 as SecurityConfig.ge...
  participant n4_method_15 as SecurityConfig.ge...
  participant n5_method_217 as handleAuthenticat...
  participant n6_method_319 as handleAuthenticat...
  participant n7_method_421 as handleAuthenticat...
  participant n8_method_523 as handleAuthenticat...

  n2_method_13->>n3_method_14: call (80%)
  n1_method_115->>n3_method_14: call (80%)
  n5_method_217->>n3_method_14: call (80%)
  n6_method_319->>n3_method_14: call (80%)
  n7_method_421->>n3_method_14: call (80%)
  n8_method_523->>n3_method_14: call (80%)
  n3_method_14->>n4_method_15: call (80%)
  n3_method_14->>n4_method_15: call (80%)
  n3_method_14->>n4_method_15: call (80%)
  n3_method_14->>n4_method_15: call (80%)
  n3_method_14->>n4_method_15: call (80%)
  n3_method_14->>n4_method_15: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (8)
```json
  method:13: handleAuthenticationFailure() (method)
  method:115: handleAuthenticationFailure() (method)
  method:217: handleAuthenticationFailure() (method)
  method:319: handleAuthenticationFailure() (method)
  method:421: handleAuthenticationFailure() (method)
  method:523: handleAuthenticationFailure() (method)
  method:14: SecurityConfig.getClientIP() (method)
  method:15: SecurityConfig.getCurrentRequest() (method)
```

엣지 목록 (12)
```json
  method:13 -> method:14 (call)
  method:115 -> method:14 (call)
  method:217 -> method:14 (call)
  method:319 -> method:14 (call)
  method:421 -> method:14 (call)
  method:523 -> method:14 (call)
  method:14 -> method:15 (call)
  method:14 -> method:15 (call)
  method:14 -> method:15 (call)
  method:14 -> method:15 (call)
  method:14 -> method:15 (call)
  method:14 -> method:15 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:30:05*