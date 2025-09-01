# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:50
- 노드 수: 3
- 엣지 수: 2

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_42 as calculateOrderTot...
  participant n2_unresolved as unresolved: com.c...
  participant n3_unresolved as unresolved: com.s...

  n1_method_42->>n3_unresolved: call (80%)
  n1_method_42->>n2_unresolved: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (3)
```json
  method:42: calculateOrderTotal() (method)
  unresolved:com.selectOrderById: unresolved: com.selectOrderById (unresolved)
  unresolved:com.calculateOrderAmount: unresolved: com.calculateOrderAmount (unresolved)
```

엣지 목록 (2)
```json
  method:42 -> unresolved:com.selectOrderById (call)
  method:42 -> unresolved:com.calculateOrderAmount (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:50*