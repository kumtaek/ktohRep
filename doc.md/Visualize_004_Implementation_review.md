# Source Analyzer 시각화 구현 리뷰 (v1.0)

**검토 대상**: Visualize_003_Implementation.md 및 `visualize/` 구현 일체  
**검토 일자**: 2025-08-29  
**요약 판단**: 계획 대비 구현 충실도와 구조화가 우수하며, 즉시 사용 가능한 수준. 다만 DB 스키마/타입 불일치, 일부 에지 케이스 처리, 오프라인 의존성, 성능 최적화 포인트 등 개선 필요.

## 강점
- **모듈화/확장성**: CLI(`visualize/cli.py`) – 빌더(`builders/*`) – 렌더러(`templates/render.py`) – 뷰어(HTML) 분리가 명확. 새로운 시각화 추가 용이.
- **기능 충실도**: 의존성/ERD/컴포넌트/시퀀스 4종 시각화와 툴바(검색/PNG 내보내기/레이아웃 토글 등) 구현 완료.
- **사용성**: `visualize_cli.py` 엔트리 제공, Windows/Unix 경로 처리 배려, 포커스/깊이/노드상한 옵션 제공.
- **메타 강화 토대**: `phase1/src/database/metadata_enhancement_engine.py`와 `EdgeHint` 모델 도입으로 점진 개선 설계 반영.
- **ERD 품질**: 조인 패턴 빈도+PK 교차검증 기반 `fk_inferred/join_inferred` 시각적 차별화가 합리적.

## 발견된 문제/리스크
- DB 스키마 불일치: `Edge` 모델이 `dst_id`를 `nullable=False(Integer)`로 정의. 그러나 메타 보강 시 미해결 콜을 `dst_id=None`으로 `edges`에 추가함.
  - 위치: `phase1/src/models/database.py` (`Edge.dst_id`), `metadata_enhancement_engine._resolve_method_calls()`
  - 영향: 커밋 시 제약 위반/런타임 예외 가능. 미해결 엣지는 `edges`가 아닌 `edge_hints`에 남겨야 함.
- 시퀀스 빌더의 타입 처리 버그: `table` 노드에 대해 `int(node_id)` 캐스팅 수행.
  - 위치: `visualize/builders/sequence_diagram.py` `_trace_call_sequence()`
  - 영향: `dst_type == 'table'`일 때 테이블 식별자가 문자열(또는 owner.table)인 경우 변환 실패. 또한 `VizDB.get_node_details('table', ...)`가 현재 테이블 ID/이름을 혼용함.
- `VizDB.get_node_details('table', ...)` 구현 부정확: 인자로 들어온 값을 테이블 이름처럼 취급해 메타를 구성. 실제 스키마는 `DbTable.table_id` 기반 사용이 타당.
  - 위치: `visualize/data_access.py` `get_node_details()`
  - 영향: 라벨/패널 정보가 부정확하거나 빈 값 표기.
- 엣지-프로젝트 범위 필터 쿼리 복잡도/이식성: `fetch_edges()`의 `join(File, or_(...))` + `in_(subquery())` 구성이 DB별 최적화/이식성 측면에서 불안정.
  - 위치: `visualize/data_access.py` `fetch_edges()`
  - 영향: 대규모 프로젝트에서 성능 저하 가능. 쿼리 플랜 예측 어려움.
- 외부 CDN 의존: 뷰어에서 `unpkg.com`의 Cytoscape/Dagre 로드.
  - 위치: `visualize/templates/*.html`
  - 영향: 오프라인/폐쇄망 환경에서 미동작. 버전 고정/무결성 보장 미흡.
- 에러/로그 처리: CLI가 `print` 중심. 실패 시 표준 에러/반환코드/로깅 일관성 보완 필요.
- 사소하지만 주의: `requirements.txt`에 `sqlite3` 명시(내장 모듈) → `pip` 에러 유발 가능.

## 개선 제안 (우선순위순)
- 스키마/로직 합치: 미해결 콜을 `edges`에 기록하지 말고 `edge_hints`로 유지. 필요 시 `edges_unresolved` 별도 테이블 또는 `Edge.dst_id`를 `nullable=True`로 완화하되, 뷰어에선 시각적 구분.
- `get_node_details('table', ...)` 정정: `node_id`를 `DbTable.table_id`로 해석해 `DbTable/DbPk/DbColumn` 참조, 라벨은 `OWNER.TABLE`로 반환. 문자열 이름을 사용하는 경로가 있다면 별도 함수로 분리.
- 시퀀스 빌더 캐스팅 가드: `_trace_call_sequence()`에서 `node_type == 'table'`일 때 `int()` 변환 금지. `try/except`로 안전 처리하거나 타입별 분기.
- `fetch_edges()` 단순화/성능: 
  - 1) 먼저 프로젝트 소속 `file_id/class_id/method_id/sql_id` 집합을 구해 메모리에 올린 뒤, `OR` 대신 두 단계 필터로 분리. 
  - 2) 또는 `edges`에 `project_id` 칼럼 추가(정규화된冗長)로 빠른 필터 지원.
- 오프라인 자산 번들링: Cytoscape/Dagre를 `visualize/templates/assets/`로 번들하고 템플릿에서 로컬 로드. 무결성 해시(SRI) 또는 버전 고정 표기.
- CLI 품질: `argparse`에 `--verbose/--quiet`, `--log-file` 옵션, 표준 에러 출력, 반환코드 준수. 예외 메시지에 원인/조치 힌트 포함.
- 스타일/접근성: 대규모 그래프에서 성능 좋은 `cose-bilkent`(옵션) 추가, 노드/엣지 툴팁 지연 렌더링, 키보드 네비게이션(검색 후 ↑/↓ 이동) 보강.
- 구성 분리: 컴포넌트 분류 규칙을 코드 상수 → 설정(`config.visualize.component_rules`)로 이전하고 미스매치 로깅.

## 제안 패치 스케치
- `visualize/data_access.py`
  - `get_node_details('table', table_id: int)`에서 `DbTable` 조회 후 `{ owner, table_name, status, pk_columns }` 채움.
- `visualize/builders/sequence_diagram.py`
  - `_trace_call_sequence()` 내 `node_type == 'table'` 분기 시 `target_details = db.get_node_details('table', node_id)`로 호출(캐스팅 제거) 및 실패 시 라벨 폴백.
- `phase1/src/database/metadata_enhancement_engine.py`
  - 미해결 콜은 `edges` 추가 대신 confidence 낮춘 `edge_hints` 유지 또는 별도 테이블 사용. 현행 유지가 필요하면 `Edge.dst_id`를 nullable로 변경(마이그레이션 포함).
- `visualize/templates/*.html`
  - CDN → 로컬 에셋 로딩 옵션 추가. 네트워크 실패 시 경고/대체 처리.

## 검증 체크리스트 (제안)
- 기능 회귀: `visualize/testcase/testcase.md`의 TC-ERD/GRAPH/COMP/SEQ 전부 재실행.
- DB 제약: `dst_id IS NULL` 엣지 삽입 시도 시 실패 재현 → 설계 재결정(위 개선안 적용).
- 대규모 샘플: `--max-nodes` 200/1000/2000에서 레이아웃/상호작용 시간 측정.
- 오프라인: 네트워크 차단 상태로 시각화 HTML 로드 확인.
- Windows 경로: JSP/매퍼 경로 매칭(`\`/`/`) 케이스 검증.

## 결론
전반적으로 기획 문서와 일치하는 구조와 기능을 안정적으로 구현했습니다. 핵심 리스크는 DB 스키마와 미해결 엣지 처리 불일치, 테이블 노드 메타 처리/캐스팅 문제이며, 비교적 국소적인 수정으로 해결 가능합니다. 위 개선안을 반영하면 실사용/대규모 데이터셋에서도 신뢰성·성능·운영편의성이 한층 강화될 것으로 판단합니다.

