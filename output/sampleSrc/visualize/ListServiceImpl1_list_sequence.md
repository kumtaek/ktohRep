# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-02 01:01:10
- 노드 수: 2
- 엣지 수: 1

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_66 as list()
  participant n2_method_67 as ListServiceImpl1....

  n1_method_66->>n2_method_67: call (80%)
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
  method:66: list() (method)
  method:67: ListServiceImpl1.helper() (method)
```

엣지 목록 (1)
```json
  method:66 -> method:67 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-02 01:01:10*