# Phase1 Analyzer Testcases

본 문서는 phase1 분석 파이프라인(파서/메타DB 저장/그래프 빌드)의 수동 테스트 시나리오입니다. PROJECT의 샘플 소스는 본 테스트를 위해 일부 추가되었습니다.

## 0. 사전 준비

- Python 3.10+, `pip install -r requirements.txt`
- 설정: `config/config.yaml` (기본 사용)
- 분석 대상: `PROJECT/sampleSrc`

## 1. 실행

```bash
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

기대 결과:
- `data/metadata.db` 생성
- 콘솔/로그에 분석 요약 출력

## 2. MyBatis 조인 추출 검증 (v1.4 확장)

대상 파일: `PROJECT/sampleSrc/src/main/resources/mybatis/TestJoinMapper.xml`

체크 포인트:
- `sql_units`에 `selectUserOrders`, `selectUserOrdersWithInclude`, `selectCompositeJoin` 등록
- **v1.4 신규**: 동적 SQL 처리 검증
  - `selectDynamicChoose`: `<bind>`, `<choose>/<when>/<otherwise>` 처리
  - `selectWithForeach`: `<foreach>` IN 표현으로 요약
  - `selectWithNestedInclude`: 중첩된 `<include>`과 `<where>/<if>` 처리
- `joins`에 다음 패턴 존재:
  - `SAMPLE.USERS.USER_ID = SAMPLE.ORDERS.USER_ID`
  - `SAMPLE.ORDER_ITEMS.ORDER_ID = SAMPLE.ORDERS.ORDER_ID`
  - `SAMPLE.ORDER_ITEMS.PRODUCT_ID = SAMPLE.PRODUCTS.PRODUCT_ID`

검증 방법(예: sqlite3):
```sql
.open data/metadata.db
select * from sql_units where stmt_id in ('selectUserOrders','selectUserOrdersWithInclude','selectCompositeJoin');
select l_table,l_col,r_table,r_col from joins;
```

## 3. JSP include / JSP SQL 검출 검증

대상 파일: `PROJECT/sampleSrc/src/main/webapp/WEB-INF/jsp/test/testPage.jsp`

체크 포인트:
- JSP SQL 패턴 1건 이상 검출(`sql_units.origin='jsp'`)
- include 후보(헤더/통합헤더) 추출 → 빌드 후 `edges.edge_kind='include'` 추가(보강 시)

예시 질의:
```sql
select origin, stmt_id from sql_units where file_id in (
  select file_id from files where path like '%/WEB-INF/jsp/test/testPage.jsp'
);
```

## 4. Java 호출/오버로드/정적 임포트 검증(보강 시)

대상 파일:
- `PROJECT/sampleSrc/src/main/java/com/example/service/OverloadService.java`
- `PROJECT/sampleSrc/src/main/java/com/example/util/Texts.java`
- `PROJECT/sampleSrc/src/main/java/com/example/service/impl/ListServiceImpl1.java`

체크 포인트:
- `classes/methods`에 OverloadService, find(int), find(String), process() 등록
- call 힌트(edge_hints) 생성 → 그래프 빌드 후 `edges(edge_kind='call')`로 일부 해소
- static import(`Texts.isEmpty`)는 낮은 confidence로 후보 연결 또는 보류

예시 질의:
```sql
select name, signature from methods m join classes c on m.class_id=c.class_id where c.name='OverloadService';
select count(*) from edges where edge_kind='call';
```

## 5. 테이블 사용(use_table) / PK-FK 추론 검증

체크 포인트:
- `edges(edge_kind='use_table')`가 sql_unit→db_table로 생성
- 빈도/PK 교차검증(보강 시)로 `joins.inferred_pkfk=1` 및 confidence 보정

예시 질의:
```sql
select edge_kind,count(*) from edges group by edge_kind;
select inferred_pkfk, count(*) from joins group by inferred_pkfk;
```

## 6. 로그/에러 확인

- 파일: `logs/analyzer.log`
- 실패/예외 로그가 없는지 확인

## 7. v1.4 신규 기능 테스트

### 7.1 동적 SQL 해석 테스트
```bash
# 동적 SQL이 포함된 매퍼에서 조건/분기 보존 확인
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

검증 항목:
- `<bind>` 변수가 정규화된 SQL에 적절히 치환
- `<choose>/<when>` 분기가 대표 분기로 요약되고 주석 보존
- `<foreach>` 블록이 `IN (:list[])` 형태로 요약

### 7.2 Mermaid 내보내기 개선 테스트
```bash
# 다양한 export strategy 테스트
python visualize_cli.py graph --project-id 1 --out test_full.html --export-strategy full
python visualize_cli.py graph --project-id 1 --out test_balanced.html --export-strategy balanced --min-confidence 0.4
python visualize_cli.py class --project-id 1 --out test_class.html --class-methods-max 5 --class-attrs-max 8
```

### 7.3 세션 관리 개선 검증
- 병렬 분석 N회 반복 후 DB 연결/커서 수 정상 유지 확인
- 예외 유발 테스트에서 리소스 누수 없음 확인

## 8. 주의/한계

- javalang 미설치 시 Java 파싱 스킵될 수 있음(requirements 설치 필요)
- DB_SCHEMA CSV가 충분하지 않으면 PK 교차검증 결과가 달라질 수 있음
- v1.4에서 추가된 DynamicSqlResolver는 lxml이 필요함

