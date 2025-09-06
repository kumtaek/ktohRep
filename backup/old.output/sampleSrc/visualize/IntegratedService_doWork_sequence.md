# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:36:18
- 노드 수: 10
- 엣지 수: 24

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_143 as doWork()
  participant n2_method_245 as doWork()
  participant n3_method_347 as doWork()
  participant n4_method_41 as doWork()
  participant n5_method_42 as IntegratedService...
  participant n6_method_43 as IntegratedService...
  participant n7_method_44 as IntegratedService...
  participant n8_method_449 as doWork()
  participant n9_method_45 as IntegratedService...
  participant n10_method_551 as doWork()

  n4_method_41->>n6_method_43: call (80%)
  n4_method_41->>n7_method_44: call (80%)
  n4_method_41->>n5_method_42: call (80%)
  n4_method_41->>n9_method_45: call (80%)
  n1_method_143->>n6_method_43: call (80%)
  n1_method_143->>n7_method_44: call (80%)
  n1_method_143->>n5_method_42: call (80%)
  n1_method_143->>n9_method_45: call (80%)
  n2_method_245->>n6_method_43: call (80%)
  n2_method_245->>n7_method_44: call (80%)
  n2_method_245->>n5_method_42: call (80%)
  n2_method_245->>n9_method_45: call (80%)
  n3_method_347->>n6_method_43: call (80%)
  n3_method_347->>n7_method_44: call (80%)
  n3_method_347->>n5_method_42: call (80%)
  n3_method_347->>n9_method_45: call (80%)
  n8_method_449->>n6_method_43: call (80%)
  n8_method_449->>n7_method_44: call (80%)
  n8_method_449->>n5_method_42: call (80%)
  n8_method_449->>n9_method_45: call (80%)
  n10_method_551->>n6_method_43: call (80%)
  n10_method_551->>n7_method_44: call (80%)
  n10_method_551->>n5_method_42: call (80%)
  n10_method_551->>n9_method_45: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (10)
```json
  method:41: doWork() (method)
  method:143: doWork() (method)
  method:245: doWork() (method)
  method:347: doWork() (method)
  method:449: doWork() (method)
  method:551: doWork() (method)
  method:43: IntegratedService.calculateOrderTotal() (method)
  method:44: IntegratedService.getFormattedId() (method)
  method:42: IntegratedService.getStaticUserData() (method)
  method:45: IntegratedService.log() (method)
```

엣지 목록 (24)
```json
  method:41 -> method:43 (call)
  method:41 -> method:44 (call)
  method:41 -> method:42 (call)
  method:41 -> method:45 (call)
  method:143 -> method:43 (call)
  method:143 -> method:44 (call)
  method:143 -> method:42 (call)
  method:143 -> method:45 (call)
  method:245 -> method:43 (call)
  method:245 -> method:44 (call)
  method:245 -> method:42 (call)
  method:245 -> method:45 (call)
  method:347 -> method:43 (call)
  method:347 -> method:44 (call)
  method:347 -> method:42 (call)
  method:347 -> method:45 (call)
  method:449 -> method:43 (call)
  method:449 -> method:44 (call)
  method:449 -> method:42 (call)
  method:449 -> method:45 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:36:18*