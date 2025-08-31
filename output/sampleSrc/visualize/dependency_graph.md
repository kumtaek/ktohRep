# Source Analyzer GRAPH Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: GRAPH
- 생성 시각: 2025-08-31 21:54:33
- 노드 수: 0
- 엣지 수: 0

## 적용된 필터

- kinds: use_table,include,extends,implements
- min_confidence: 0.5
- depth: 2
- max_nodes: 2000

## 다이어그램

```mermaid
graph TD


  %% Dynamic Cluster Styling
  classDef JSP fill:#ffebee,stroke:#d32f2f
  classDef Controller fill:#e3f2fd,stroke:#1976d2
  classDef Service fill:#e8f5e8,stroke:#388e3c
  classDef Mapper fill:#f3e5f5,stroke:#7b1fa2
  classDef DB fill:#fff9c4,stroke:#f9a825

  %% Hotspot styling
  classDef hotspot_low fill:#e8f5e9,stroke:#43a047
  classDef hotspot_med fill:#fffde7,stroke:#f9a825
  classDef hotspot_high fill:#ffe0b2,stroke:#fb8c00,stroke-width:2px
  classDef hotspot_crit fill:#ffebee,stroke:#e53935,stroke-width:3px

  %% Vulnerability styling
  classDef vuln_low stroke:#8bc34a,stroke-width:2px,stroke-dasharray:2 2
  classDef vuln_medium stroke:#fbc02d,stroke-width:2px
  classDef vuln_high stroke:#fb8c00,stroke-width:3px
  classDef vuln_critical stroke:#e53935,stroke-width:4px
```

## 범례

### Graph 범례


### 스타일 레이어
- Hotspot(채움): low/med/high/crit
- 취약점(테두리): low/medium/high/critical
- 그룹 색상: JSP/Controller/Service/Mapper/DB

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (0)
```json
```

엣지 목록 (0)
```json
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-08-31 21:54:33*