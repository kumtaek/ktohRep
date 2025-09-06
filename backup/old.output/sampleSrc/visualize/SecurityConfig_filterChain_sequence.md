# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:29:27
- 노드 수: 9
- 엣지 수: 18

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_106 as filterChain()
  participant n2_method_208 as filterChain()
  participant n3_method_310 as filterChain()
  participant n4_method_4 as filterChain()
  participant n5_method_412 as filterChain()
  participant n6_method_514 as filterChain()
  participant n7_method_6 as SecurityConfig.jw...
  participant n8_method_7 as SecurityConfig.cu...
  participant n9_method_8 as SecurityConfig.cu...

  n4_method_4->>n7_method_6: call (80%)
  n4_method_4->>n8_method_7: call (80%)
  n4_method_4->>n9_method_8: call (80%)
  n1_method_106->>n7_method_6: call (80%)
  n1_method_106->>n8_method_7: call (80%)
  n1_method_106->>n9_method_8: call (80%)
  n2_method_208->>n7_method_6: call (80%)
  n2_method_208->>n8_method_7: call (80%)
  n2_method_208->>n9_method_8: call (80%)
  n3_method_310->>n7_method_6: call (80%)
  n3_method_310->>n8_method_7: call (80%)
  n3_method_310->>n9_method_8: call (80%)
  n5_method_412->>n7_method_6: call (80%)
  n5_method_412->>n8_method_7: call (80%)
  n5_method_412->>n9_method_8: call (80%)
  n6_method_514->>n7_method_6: call (80%)
  n6_method_514->>n8_method_7: call (80%)
  n6_method_514->>n9_method_8: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (9)
```json
  method:4: filterChain() (method)
  method:106: filterChain() (method)
  method:208: filterChain() (method)
  method:310: filterChain() (method)
  method:412: filterChain() (method)
  method:514: filterChain() (method)
  method:6: SecurityConfig.jwtAuthenticationFilter() (method)
  method:7: SecurityConfig.customAuthenticationEntryPoint() (method)
  method:8: SecurityConfig.customAccessDeniedHandler() (method)
```

엣지 목록 (18)
```json
  method:4 -> method:6 (call)
  method:4 -> method:7 (call)
  method:4 -> method:8 (call)
  method:106 -> method:6 (call)
  method:106 -> method:7 (call)
  method:106 -> method:8 (call)
  method:208 -> method:6 (call)
  method:208 -> method:7 (call)
  method:208 -> method:8 (call)
  method:310 -> method:6 (call)
  method:310 -> method:7 (call)
  method:310 -> method:8 (call)
  method:412 -> method:6 (call)
  method:412 -> method:7 (call)
  method:412 -> method:8 (call)
  method:514 -> method:6 (call)
  method:514 -> method:7 (call)
  method:514 -> method:8 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:29:27*