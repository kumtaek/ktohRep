# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:39:03
- 노드 수: 2
- 엣지 수: 1

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_47 as largeOrderMethod3()
  participant n2_unresolved as unresolved: Syste...

  n1_method_47->>n2_unresolved: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (2)
```json
  method:47: largeOrderMethod3() (method)
  unresolved:System.out.println: unresolved: System.out.println (unresolved)
```

엣지 목록 (1)
```json
  method:47 -> unresolved:System.out.println (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:39:03*