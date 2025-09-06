# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:37:07
- 노드 수: 11
- 엣지 수: 30

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_142 as startProcess()
  participant n2_method_244 as startProcess()
  participant n3_method_346 as startProcess()
  participant n4_method_40 as startProcess()
  participant n5_method_41 as IntegratedService...
  participant n6_method_42 as IntegratedService...
  participant n7_method_43 as IntegratedService...
  participant n8_method_44 as IntegratedService...
  participant n9_method_448 as startProcess()
  participant n10_method_45 as IntegratedService...
  participant n11_method_550 as startProcess()

  n4_method_40->>n5_method_41: call (80%)
  n1_method_142->>n5_method_41: call (80%)
  n2_method_244->>n5_method_41: call (80%)
  n3_method_346->>n5_method_41: call (80%)
  n9_method_448->>n5_method_41: call (80%)
  n11_method_550->>n5_method_41: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
  n5_method_41->>n7_method_43: call (80%)
  n5_method_41->>n8_method_44: call (80%)
  n5_method_41->>n6_method_42: call (80%)
  n5_method_41->>n10_method_45: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (11)
```json
  method:40: startProcess() (method)
  method:142: startProcess() (method)
  method:244: startProcess() (method)
  method:346: startProcess() (method)
  method:448: startProcess() (method)
  method:550: startProcess() (method)
  method:41: IntegratedService.doWork() (method)
  method:43: IntegratedService.calculateOrderTotal() (method)
  method:44: IntegratedService.getFormattedId() (method)
  method:42: IntegratedService.getStaticUserData() (method)
  method:45: IntegratedService.log() (method)
```

엣지 목록 (30)
```json
  method:40 -> method:41 (call)
  method:142 -> method:41 (call)
  method:244 -> method:41 (call)
  method:346 -> method:41 (call)
  method:448 -> method:41 (call)
  method:550 -> method:41 (call)
  method:41 -> method:43 (call)
  method:41 -> method:44 (call)
  method:41 -> method:42 (call)
  method:41 -> method:45 (call)
  method:41 -> method:43 (call)
  method:41 -> method:44 (call)
  method:41 -> method:42 (call)
  method:41 -> method:45 (call)
  method:41 -> method:43 (call)
  method:41 -> method:44 (call)
  method:41 -> method:42 (call)
  method:41 -> method:45 (call)
  method:41 -> method:43 (call)
  method:41 -> method:44 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:37:07*