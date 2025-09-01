# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-02 01:00:50
- 노드 수: 5
- 엣지 수: 4

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_10 as IntegratedService...
  participant n2_method_6 as doWork()
  participant n3_method_7 as IntegratedService...
  participant n4_method_8 as IntegratedService...
  participant n5_method_9 as IntegratedService...

  n2_method_6->>n4_method_8: call (80%)
  n2_method_6->>n5_method_9: call (80%)
  n2_method_6->>n3_method_7: call (80%)
  n2_method_6->>n1_method_10: call (80%)
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
  method:6: doWork() (method)
  method:8: IntegratedService.calculateOrderTotal() (method)
  method:9: IntegratedService.getFormattedId() (method)
  method:7: IntegratedService.getStaticUserData() (method)
  method:10: IntegratedService.log() (method)
```

엣지 목록 (4)
```json
  method:6 -> method:8 (call)
  method:6 -> method:9 (call)
  method:6 -> method:7 (call)
  method:6 -> method:10 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-02 01:00:50*