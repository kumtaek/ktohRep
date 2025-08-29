# Visual Dataflow v2 구현 내역 요약 (005)

본 문서는 Visual_dataflow_001~004 문서를 검토한 뒤, 최신 개선안(004) 우선으로 구현한 결과를 요약합니다. 구현은 로컬 파일만 수정했으며, 커밋은 사용자가 진행하시면 됩니다.

## 구현 요약
- Graph/Component Mermaid Export 개선
  - 그룹 스타일 적용: JSP/Controller/Service/Mapper/DB 색상·테두리 클래스 정의 및 노드별 `class` 적용.
  - 미해결 호출 시각화: `call_unresolved`를 회색 점선(`-.->`)으로 축약 표기.
  - DB 테이블 모양 수정: Mermaid 이중 원형 표기(`id(( LABEL ))`)로 안정화.
  - 라벨 안전화: 길이 제한 내에서 sanitize 처리, 필요 시 `<br/>`로 메트릭 노출.
- Hotspot 레이어(LOC/복잡도 근사)
  - 빌더에서 노드 메타에 `meta.loc`, `meta.complexity_est`, `meta.hotspot_bin` 추가.
  - 복잡도 근사: 아웃바운드 호출 수(견고/간단) 기반.
  - Mermaid Export 시 `class n hotspot_low|med|high|crit` 적용 + Legend 안내.
- 취약점 레이어(최대 심각도 기준)
  - `VizDB.fetch_vulnerabilities(project_id)` 추가: target_type별 조인으로 프로젝트 범위 레코드 로드.
  - 빌더에서 `meta.vuln_counts`, `meta.vuln_max_severity` 생성.
  - Mermaid Export 시 `class n vuln_low|medium|high|critical` 적용 + Legend 안내.
- 필터/컨텍스트 메타 노출
  - 빌더 결과에 `metadata.filters` 삽입(kinds, min_confidence, focus, depth, max_nodes)
  - Markdown Export에 필터 정보 표시.
- CLI/Exporter 사소 수정
  - `--keep-edge-kinds` 기본값 오기(‘includes’)를 `include`로 정정.
  - Exporter의 keep_edge_kinds 기본도 동일하게 정정.

## 변경 파일
- `visualize/exporters/mermaid_exporter.py`
  - 그룹/Hotspot/취약점 스타일 정의 및 `class` 적용 로직 추가.
  - 테이블 노드 형태를 `(( LABEL ))`로 고정.
  - 미해결 호출을 점선으로 단순 표기.
  - Graph/Component 범례에 스타일 레이어 안내 추가.
- `visualize/builders/dependency_graph.py`
  - 노드/엣지 구성 후, 아웃바운드 호출 수 기반의 `complexity_est` 계산.
  - LOC/복잡도 기반 `hotspot_bin` 산정.
  - 프로젝트 범위 취약점 로딩 및 노드 메타에 취약점 정보 결합.
  - `metadata.filters` 주입.
- `visualize/data_access.py`
  - `fetch_vulnerabilities(project_id)` 신규 추가(파일/클래스/메서드/SQL 단위별 조인 필터).
- `visualize/cli.py`
  - Mermaid Export 호출 시 `metadata.filters` 전달.
  - `--keep-edge-kinds` 기본값을 `include,call,use_table`로 정정.

## 사용 예시
- 데이터 흐름(그래프) — 최신 프리셋 반영
```
python -m visualize.cli graph \
  --project-id 1 \
  --kinds use_table,include,call \
  --min-confidence 0.5 \
  --out out/graph.html \
  --export-mermaid out/graph.md \
  --export-strategy balanced \
  --keep-edge-kinds include,call,use_table
```
- 시퀀스
```
python -m visualize.cli sequence \
  --project-id 1 \
  --start-file OrderController.java \
  --start-method submit \
  --depth 3 \
  --out out/seq.html \
  --export-mermaid out/seq.md
```
- ERD
```
python -m visualize.cli erd \
  --project-id 1 \
  --out out/erd.html \
  --export-mermaid out/erd.md
```

## 테스트 자산
- 샘플 DB 스키마 통합/이동: `DB_SCHEMA` → `PROJECT/sampleSrc/DB_SCHEMA/`
  - 스키마 형식 통합: 
    - `ALL_TABLES.csv` = OWNER,TABLE_NAME,COMMENTS (테이블 코멘트 포함)
    - `ALL_TAB_COLUMNS.csv` = OWNER,TABLE_NAME,COLUMN_NAME,DATA_TYPE,NULLABLE,COLUMN_COMMENTS
    - `PK_INFO.csv` = OWNER,TABLE_NAME,COLUMN_NAME,POSITION
  - 별도 `ALL_TAB_COMMENTS.csv`, `ALL_COL_COMMENTS.csv` 제거
- 엔드투엔드 테스트 가이드: `testcase.md` (분석 실행 → 그래프/ERD/시퀀스 생성 → 취약점 오버레이 시드)

## 구현 선택 사유
- Mermaid 안정성 우선: 004 개선안 기준으로 라벨/클래스/선언 순서를 준수하고, 점선/색상 규칙을 표준화하여 GitHub/VS Code에서 실패를 줄였습니다.
- Hotspot 근사치: 실제 CC 미보유 상황에서 가장 안전한 근사(아웃바운드 호출 수)를 사용. LOC는 파일/일부 엔티티에서만 바로 얻을 수 있어 기본값(0) + 복잡도 보정 규칙으로 bin을 산정했습니다. 추후 CodeMetric(CC/LOC) 테이블 활용 또는 AST 기반 정밀 복잡도로 교체 가능하도록 키를 `complexity_est`로 유지했습니다.
- 취약점 레이어 병행: 스타일 우선순위(배경=Hotspot, 테두리=Vuln)를 적용해 겹침 충돌을 최소화. 빌더에서 최대 심각도만 계산하여 단순/명확하게 반영했습니다.
- 문서 일관성: `--keep-edge-kinds`의 오기를 정정하여 문서/코드의 엣지 명칭을 통일했습니다. Markdown에 필터 정보를 함께 기록해 재현성과 리뷰 편의를 높였습니다.

## 한계 및 후속 권고
- 복잡도/LOC 정밀도: 현재 복잡도는 근사치이며, LOC도 엔티티별 보강이 필요합니다. `CodeMetric` 활용 또는 AST/파서 확장을 통해 품질 개선을 권장합니다.
- Mermaid 스케일: 큰 그래프는 여전히 렌더링에 취약할 수 있습니다. `--export-strategy minimal`, `--max-nodes`, `--depth`, `--focus`를 적극 권장합니다.
- 라벨 길이: 긴 FQN/메서드명은 기본 truncate 됩니다. 필요 시 `--mermaid-label-max`를 늘려 주세요.
- 옵션 노출: `--vuln-overlay`, `--hotspot-metric` 등의 세부 옵션은 아직 CLI에 직접 노출하지 않았습니다. 요구 시 추가 가능합니다.

---

문의/수정이 필요하면 알려 주세요. 추가적으로 Mermaid 샘플 분할/TOC 구성, 대화형 HTML에서의 width/height 매핑(정밀 Hotspot)도 확장 가능합니다.
