# Source Analyzer Visualization Testcases

본 문서는 시각화 모듈의 기능 검증을 위한 테스트 시나리오입니다. 개발자는 .md 설계를 숙지하고 있으며, 아래 케이스는 실제 실행 관점에서 작성되었습니다.

주의: 본 문서는 구현 완료 후 수행을 전제로 하며, `visualize` CLI와 빌더/템플릿이 동작한다는 가정하에 기술합니다.

## 0. 사전 준비

-   Python 3.10+, `pip install -r requirements.txt`
-   설정 파일: `config/config.yaml` (기본 그대로 사용)
-   메타DB 초기화용 분석 실행:
    -   명령: `python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml`
    -   기대: `data/metadata.db` 생성, 로그는 `logs/analyzer.log`
-   성공 기준(대략):
    -   프로젝트/파일/SQL 단위가 DB에 적재됨
    -   `joins`, `required_filters`, `db_tables`, `db_pk` 등이 존재

## 1. ERD 시나리오

### TC-ERD-01 기본 ERD 생성
-   목적: 전체 테이블 기반 ERD 생성
-   명령: `python -m visualize erd --project-id 1 --out visualize/output/erd_all.html`
-   기대:
    -   HTML 파일 생성, 테이블 노드 다수 표시
    -   노드 라벨: `OWNER.TABLE` 형식(대문자)

### TC-ERD-02 소유자/테이블 필터
-   목적: 특정 오너/테이블만 표현
-   명령: `python -m visualize erd --project-id 1 --owners SAMPLE --tables USERS,ORDERS --out visualize/output/erd_subset.html`
-   기대: `SAMPLE.USERS`, `SAMPLE.ORDERS` 노드만 존재, 기타 노드는 없음

### TC-ERD-03 FK 추론 시각화
-   목적: 조인 패턴 기반 FK 추론 엣지 확인
-   명령: `python -m visualize erd --project-id 1 --out visualize/output/erd_fk.html`
-   기대:
    -   `fk_inferred` 엣지가 표시되고, confidence>0.85인 엣지는 진한 색/굵기
    -   동일 테이블 페어에 복수 컬럼 조인(복합키 후보) 시 confidence가 소폭 상향

### TC-ERD-04 SQL 기반 부분 ERD
-   목적: 특정 쿼리가 참조하는 테이블만 부분 ERD 생성
-   명령 예: `python -m visualize erd --project-id 1 --from-sql UserMapper:selectUser --out visualize/output/erd_from_sql.html`
-   기대: 해당 SQL이 참조하는 테이블만 노드로 표시

## 2. 의존성 그래프 시나리오

### TC-GRAPH-01 테이블 사용 그래프
-   목적: SQL→TABLE 의존 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table --out visualize/output/graph_use_table.html`
-   기대: `sql` 타입 노드에서 `table` 노드로 향하는 엣지 존재

### TC-GRAPH-02 include 그래프
-   목적: JSP/JSP 및 MyBatis include 엣지 표시
-   명령: `python -m visualize graph --project-id 1 --kinds include --out visualize/output/graph_include.html`
-   기대: 파일 간 include 엣지 존재(뷰어 클릭 시 대상 경로 표시)

### TC-GRAPH-03 confidence 필터
-   목적: `--min-confidence` 적용 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table,include --min-confidence 0.9 --out visualize/output/graph_conf90.html`
-   기대: 낮은 신뢰도의 엣지는 제외되어 그래프가 간결해짐

### TC-GRAPH-04 포커스/깊이 제한
-   목적: 특정 노드를 기준으로 BFS 제한 적용
-   명령: `python -m visualize graph --project-id 1 --kinds use_table --focus SAMPLE.USERS --depth 1 --out visualize/output/graph_focus_users.html`
-   기대: `SAMPLE.USERS`와 1단계 이웃만 표시

### TC-GRAPH-05 노드 상한(max_nodes)
-   목적: 대규모 그래프 상한 적용 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table,include --max-nodes 200 --out visualize/output/graph_cap200.html`
-   기대: 200개 내 노드로 잘림(툴바/경고 표시)

## 3. 컴포넌트 다이어그램 시나리오

### TC-COMP-01 기본 컴포넌트 표시
-   목적: 규칙 기반 그룹핑 확인
-   명령: `python -m visualize component --project-id 1 --out visualize/output/components.html`
-   기대:
    -   컨트롤러/서비스/레포지토리/매퍼/JSP/DB 그룹 노드 색 구분
    -   교차 컴포넌트 엣지(집계) 표시, 툴팁에 집계 수/평균 confidence

### TC-COMP-02 규칙 튜닝
-   목적: 규칙 변경 시 그룹핑 변화 확인
-   절차: `config/config.yaml`에 `visualize.component_rules` 추가/수정 → 재실행
-   기대: 해당 규칙에 따라 그룹 배정이 달라짐

## 4. 시퀀스(흐름) 다이어그램 시나리오

### TC-SEQ-01 JSP 중심 흐름
-   목적: JSP→SQL→TABLE 흐름 표시
-   명령: `python -m visualize sequence --project-id 1 --start-file PROJECT/sampleSrc/src/main/webapp/WEB-INF/jsp/user/userList.jsp --out visualize/output/seq_jsp.html`
-   기대: 시작 JSP에서 관련 SQL, 그 SQL이 참조하는 TABLE로의 흐름이 레이어로 배치

### TC-SEQ-02 메서드 호출 반영(보강 후)
-   목적: Java call 해소 후 Controller→Service→Repository/Mapper 흐름 포함
-   명령: `python -m visualize sequence --project-id 1 --start-method com.example.service.UserService.listUsers --depth 3 --out visualize/output/seq_java.html`
-   기대: 메서드 간 call 체인이 시간축 유사 계층으로 표현(미해소 호출은 낮은 confidence 또는 점선 스타일)

## 5. 메타 보강 기능 시나리오

### TC-META-01 edge_hints 생성/소비(메서드 호출)
-   목적: 파서→edge_hints→edges(call) 파이프라인 검증
-   절차:
    1)  분석 실행 전 `data/metadata.db` 삭제(신규 분석)
    2)  분석 실행 후 DB 확인: `edge_hints(hint_type='method_call')` 존재
    3)  `build_dependency_graph()` 수행(분석 과정에서 자동)
    4)  DB 확인: `edges(edge_kind='call', dst_id not null)` 증가, 해당 `edge_hints`는 삭제됨
-   기대: call 엣지가 생성되고 hints는 소비됨

### TC-META-02 include 힌트 해소
-   목적: JSP include 힌트→include 엣지 검증
-   절차: 위와 동일 플로우로 `edge_hints('jsp_include')`가 `edges('include')`로 전환되는지 확인

## 6. SQL 조인키 도출 강화 시나리오

### TC-JOIN-01 별칭(alias) 해소
-   목적: `a.id=b.user_id` 형태에서 a,b→OWNER.TABLE 치환 확인
-   방법: MyBatis XML이나 JSP에 다음과 유사한 테스트 쿼리를 임시 추가 후 분석:
    ```sql
    SELECT * FROM USERS u JOIN ORDERS o ON u.USER_ID = o.USER_ID
    ```
-   기대: `joins`에 `SAMPLE.USERS.USER_ID = SAMPLE.ORDERS.USER_ID` 저장, ERD에 fk_inferred 후보 표시

### TC-JOIN-02 스키마 정규화
-   목적: `owner.table`/`table` 혼재 시 OWNER 대문자/테이블 대문자로 정규화
-   기대: ERD/그래프의 테이블 라벨이 일관되게 `OWNER.TABLE`

### TC-JOIN-03 PK 교차검증
-   목적: `DbPk` 기준으로 한쪽이 PK인 조인에서 inferred_pkfk=1 & confidence 상향
-   절차: `DB_SCHEMA/PK_INFO.csv`에 USERS.USER_ID가 PK임을 확인
-   기대: USERS(USER_ID)↔ORDERS(USER_ID) 조인 시 inferred_pkfk=1, confidence≥0.85

### TC-JOIN-04 복합키 추론
-   목적: 동일 페어에서 두 컬럼 이상 조인 시 복합키 후보 상향
-   방법: 테스트 쿼리(예: ORDER_ITEMS(ORDER_ID, PRODUCT_ID)↔ORDERS(ORDER_ID) & PRODUCTS(PRODUCT_ID))를 포함한 매퍼를 임시 추가
-   기대: 동일 페어 빈도≥2 → confidence 소폭 상향, 스타일 반영

## 7. 정확성(오버로드/정적 임포트/동적 바인딩)

### TC-CALL-01 오버로드 구분
-   목적: 동일 메서드명 다른 시그니처에서 arg_count 우선 매칭 동작 확인
-   방법: `UserService`에 `find(int id)`/`find(String id)` 존재 시, 호출 인자 유형에 따라 다른 대상 매칭 여부 확인
-   기대: 인자 수/유형이 맞는 메서드로 우선 연결(confidence 가중치 상향)

### TC-CALL-02 정적 임포트
-   목적: qualifier 없는 호출이 static import된 유틸로 연결되는지 확인
-   방법: `import static com.example.util.Texts.isEmpty;` 후 `isEmpty(name)` 호출
-   기대: `Texts.isEmpty`로 resolve 또는 후보 다중 생성(낮은 confidence)

### TC-CALL-03 동적 바인딩
-   목적: 인터페이스 타입 수신자의 구현 후보 분산 연결
-   방법: `ListService` 인터페이스와 `ListServiceImpl1/2` 구현, 호출 시 두 구현 중 후보 엣지 생성
-   기대: 복수 call 엣지 생성, confidence 분산(예: 0.5/개수)

## 8. Confidence/필터링/성능

### TC-CF-01 min-confidence 필터링
-   목적: 낮은 신뢰도 엣지 제거 확인(그래프 간결화)
-   명령: `--min-confidence 0.9` vs `0.5` 비교
-   기대: 0.9에서 엣지 수가 현저히 감소

### TC-CF-02 suspect 마킹 유지
-   목적: `_SUSPECT` stmt_id 포함 여부 및 시각화 라벨 확인
-   기대: 라벨에 `_SUSPECT` 접미사 표기 또는 다른 스타일 적용

### TC-PERF-01 노드 cap 성능 확인
-   목적: 1000+ 노드 시 레이아웃 시간/상호작용 확인
-   명령: `--max-nodes 500`/`2000` 변경하여 반응성 비교
-   기대: cap이 낮을수록 렌더가 빨라짐

## 9. PNG Export

### TC-PNG-01 PNG 내보내기
-   목적: 뷰어 버튼으로 PNG 저장 확인
-   절차: 임의 그래프 열기 → `Export PNG` 클릭 → 파일 저장 확인
-   기대: `graph.png` 다운로드, 해상도(scale=2) 적용됨

## 10. 예외/에지 케이스

### TC-EX-01 DB 스키마 미존재
-   목적: DB_SCHEMA 누락 시 안전한 경고/동작 확인
-   절차: 임시로 DB_SCHEMA 경로를 비우고 분석
-   기대: 경고 로그 후 계속 진행, ERD는 비어 있거나 제한적으로 생성

### TC-EX-02 잘못된 owners/tables 인자
-   목적: 존재하지 않는 테이블 필터 지정 시 빈 그래프 처리
-   기대: 빈 노드/엣지로 HTML 생성하되 오류 없이 로딩됨

## 11. 검증 레코딩 가이드

-   각 케이스 수행 후 `visualize/output/*.html` 스냅샷 보관
-   필요 시 브라우저 콘솔에 `DATA.nodes.length`, `DATA.edges.length`로 개수 확인
-   DB 확인은 `sqlite3 data/metadata.db` 또는 DB 클라이언트 사용