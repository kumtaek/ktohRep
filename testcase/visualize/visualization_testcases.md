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

---
name: TC-ERD-01 기본 ERD 생성
kind: visualize_cli
params:
  command: erd
  project-id: 1
  out: output/visualize/erd_all.html
expected:
  files_exist:
    - visualize\output\erd_all.html
---
### TC-ERD-02 소유자/테이블 필터

---
name: TC-ERD-02 소유자/테이블 필터
kind: visualize_cli
params:
  command: erd
  project-id: 1
  owners: SAMPLE
  tables: USERS,ORDERS
  out: output/visualize/erd_subset.html
expected:
  files_exist:
    - visualize\output\erd_subset.html
---
### TC-ERD-03 FK 추론 시각화

---
name: TC-ERD-03 FK 추론 시각화
kind: visualize_cli
params:
  command: erd
  project-id: 1
  out: output/visualize/erd_fk.html
expected:
  files_exist:
    - visualize\output\erd_fk.html
---
### TC-ERD-04 SQL 기반 부분 ERD

---
name: TC-ERD-04 SQL 기반 부분 ERD
kind: visualize_cli
params:
  command: erd
  project-id: 1
  from-sql: UserMapper:selectUser
  out: output/visualize/erd_from_sql.html
expected:
  files_exist:
    - visualize\output\erd_from_sql.html
---
### TC-GRAPH-01 테이블 사용 그래프

---
name: TC-GRAPH-01 테이블 사용 그래프
kind: visualize_cli
params:
  command: graph
  project-id: 1
  kinds: use_table
  out: output/visualize/graph_use_table.html
expected:
  files_exist:
    - visualize\output\graph_use_table.html
---
### TC-GRAPH-02 include 그래프

---
name: TC-GRAPH-02 include 그래프
kind: visualize_cli
params:
  command: graph
  project-id: 1
  kinds: include
  out: output/visualize/graph_include.html
expected:
  files_exist:
    - visualize\output\graph_include.html
---
### TC-GRAPH-03 confidence 필터

---
name: TC-GRAPH-03 confidence 필터
kind: visualize_cli
params:
  command: graph
  project-id: 1
  kinds: use_table,include
  min-confidence: 0.9
  out: output/visualize/graph_conf90.html
expected:
  files_exist:
    - visualize\output\graph_conf90.html
---
### TC-GRAPH-04 포커스/깊이 제한

---
name: TC-GRAPH-04 포커스/깊이 제한
kind: visualize_cli
params:
  command: graph
  project-id: 1
  kinds: use_table
  focus: SAMPLE.USERS
  depth: 1
  out: output/visualize/graph_focus_users.html
expected:
  files_exist:
    - visualize\output\graph_focus_users.html
---
### TC-GRAPH-05 노드 상한(max_nodes)

---
name: TC-GRAPH-05 노드 상한(max_nodes)
kind: visualize_cli
params:
  command: graph
  project-id: 1
  kinds: use_table,include
  max-nodes: 200
  out: output/visualize/graph_cap200.html
expected:
  files_exist:
    - visualize\output\graph_cap200.html
---
### TC-COMP-01 기본 컴포넌트 표시

---
name: TC-COMP-01 기본 컴포넌트 표시
kind: visualize_cli
params:
  command: component
  project-id: 1
  out: output/visualize/components.html
expected:
  files_exist:
    - visualize\output\components.html
---
### TC-COMP-02 규칙 튜닝
-   목적: 규칙 변경 시 그룹핑 변화 확인
-   절차: `config/config.yaml`에 `visualize.component_rules` 추가/수정 → 재실행
-   기대: 해당 규칙에 따라 그룹 배정이 달라짐

## 4. 시퀀스(흐름) 다이어그램 시나리오

### TC-SEQ-01 JSP 중심 흐름

---
name: TC-SEQ-01 JSP 중심 흐름
kind: visualize_cli
params:
  command: sequence
  project-id: 1
  start-file: PROJECT/sampleSrc/src/main/webapp/WEB-INF/jsp/user/userList.jsp
  out: output/visualize/seq_jsp.html
expected:
  files_exist:
    - visualize\output\seq_jsp.html
---
### TC-SEQ-02 메서드 호출 반영(보강 후)

---
name: TC-SEQ-02 메서드 호출 반영(보강 후)
kind: visualize_cli
params:
  command: sequence
  project-id: 1
  start-method: com.example.service.UserService.listUsers
  depth: 3
  out: output/visualize/seq_java.html
expected:
  files_exist:
    - visualize\output\seq_java.html
---
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

-   각 케이스 수행 후 `output/visualize/*.html` 스냅샷 보관
-   필요 시 브라우저 콘솔에 `DATA.nodes.length`, `DATA.edges.length`로 개수 확인
-   DB 확인은 `sqlite3 data/metadata.db` 또는 DB 클라이언트 사용
