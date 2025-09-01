# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-02 01:01:05
- 노드 수: 2
- 엣지 수: 2

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_48 as OverloadService.f...
  participant n2_method_50 as process()

  n2_method_50->>n1_method_48: call (80%)
  n2_method_50->>n1_method_48: call (80%)
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
  method:50: process() (method)
  method:48: OverloadService.find() (method)
```

엣지 목록 (2)
```json
  method:50 -> method:48 (call)
  method:50 -> method:48 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-02 01:01:05*