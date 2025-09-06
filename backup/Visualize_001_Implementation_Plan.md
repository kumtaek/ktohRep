# Source Analyzer Visualization Implementation Plan (v0.0.1)

본 문서는 phase1 결과 메타데이터를 기반으로 TODO1 범위의 시각화(의존성 그래프, 시퀀스, 컴포넌트, ERD)를 `./visualize` 폴더에 구현하기 위한 상세 설계서입니다. 개발자는 기존 .md 문서의 맥락을 숙지하고 있다는 전제하에, 바로 구현 가능한 수준의 코드 스니펫과 알고리즘을 포함합니다.

## 1) 목표와 범위

- 목표: 메타DB(SQLite/Oracle)에 적재된 분석 결과를 선택·필터링하여 브라우저에서 인터랙티브하게 시각화하고 PNG로 내보내기
- 범위 (TODO1)
  - 의존성 그래프: 파일/클래스/메서드/SQL/테이블 간 관계(use_table/include/extends/implements/일부 call)
  - 시퀀스 다이어그램: 초기 버전은 JSP→SQL→TABLE 흐름 중심, Java 메서드 호출 보강 후 확장
  - 컴포넌트 다이어그램: Controller/Service/Repository/Mapper/JSP/DB 간 상호작용
  - ERD: 테이블 간 PK/FK(추론) 관계, 선택적 부분 ERD
  - 뷰어 요구: 확대/축소/드래그, 검색·필터, PNG export
- 필요 메타 보강: 메서드 호출 해소, JSP/MyBatis include 해소, 컴포넌트 라벨링(패키지 규칙)

## 1-1) 재정리: 개발 순서 로드맵(우선순위 기준)

1) Visualize 스캐폴딩 생성 + ERD/의존 그래프(사용 테이블 중심) 구현 및 동작 확인
2) SQL 조인키 도출 강화: alias 해소, 스키마 정규화, PK 교차검증, 복합키 추론 + confidence 보정
3) JSP/MyBatis include 해소(파일/SQL fragment) → include 엣지 정착
4) Java 메서드 호출 해소(edge_hints 기반) + 오버로드/정적 임포트/동적 바인딩 휴리스틱 적용
5) 컴포넌트 다이어그램(규칙 기반 그룹핑, 집계 엣지)
6) 시퀀스 다이어그램 1차(JSP→SQL→TABLE), 2차(Java call 체인 반영)
7) 성능/UX: BFS·노드 cap·검색·PNG export 최적화 및 설정화

아래 각 장의 상세 구현을 위 순서대로 참고해 단계별로 진행합니다.

## 2) 현재 데이터와 격차

- 보유 스키마: `projects, files, classes, methods, sql_units, joins, required_filters, db_tables, db_columns, db_pk, db_views, edges, summaries, enrichment_logs ...`
- 강점: SQL→TABLE(use_table) 엣지, 조인/필터, DB 스키마가 비교적 충실 → ERD/SQL 중심 시각화는 바로 가능
- 격차:
  - Java method→method call 엣지가 DB에 충분히 정착되지 않음(파서 단계에서 dst_id 없음 → 저장 시 필터됨)
  - JSP/MyBatis include 엣지도 유사
  - 컴포넌트 레벨 집계 메타 부재(규칙 기반 라벨링 필요)

### 2.1) 상세 개선안과 코드 스니펫

아래 개선은 TODO1의 “시각화를 위한 메타정보 보완”을 충족하기 위한 최소·안정적 변경입니다. 기존 스키마를 크게 흔들지 않고, 보조 테이블 `edge_hints`를 통해 해소 전 힌트를 저장하고, 빌드 단계에서 최종 `edges`로 해소합니다.

#### 2.1.1 보조 테이블 추가: `edge_hints`

목적: 파서 단계에서 알 수 없는 대상(메서드 호출, include 대상 파일 등)의 힌트를 안전하게 저장 → 그래프 빌드 단계에서 해소.

```python
# phase1/src/models/database.py (스니펫)
from sqlalchemy import Text

class EdgeHint(Base):
    __tablename__ = 'edge_hints'

    hint_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    src_type = Column(String(50), nullable=False)   # 'method' | 'file' | 'sql_unit' ...
    src_id = Column(Integer, nullable=False)
    hint_type = Column(String(50), nullable=False) # 'method_call' | 'jsp_include' | 'mybatis_include'
    hint = Column(Text, nullable=False)            # JSON: { called_name, arg_count, target_path, namespace, line, ... }
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

# 인덱스 권장
Index('idx_edge_hints_project', EdgeHint.project_id)
Index('idx_edge_hints_type', EdgeHint.hint_type)
```

마이그레이션: SQLite는 `Base.metadata.create_all()`로 자동 생성. Oracle 환경은 DDL 반영 필요.

#### 2.1.2 Java 메서드 호출 힌트 저장(파서) → 해소(엔진)

1) 파서에서 호출 명/인자 수 캡처

```python
# phase1/src/parsers/java_parser.py (스니펫)
def _find_method_invocations(self, node) -> List[Dict[str, Any]]:
    invocations = []
    if isinstance(node, javalang.tree.MethodInvocation):
        name = node.member
        arg_count = len(node.arguments or [])
        invocations.append({ 'name': name, 'arg_count': arg_count, 'line': getattr(node, 'position', None).line if getattr(node, 'position', None) else None })
    # 재귀 순회 동일
    ...
    return invocations

def _extract_method(self, node, class_obj):
    ...
    call_infos = self._find_method_invocations(node.body)
    # edges 대신 call 힌트를 반환하도록 인터페이스 확장(기존 edges 병행 가능)
    method_obj._call_infos = call_infos  # 일시 부착: save 단계에서 꺼내 edge_hints로 저장
    return method_obj, []
```

2) 저장 단계에서 힌트 보관

```python
# phase1/src/database/metadata_engine.py (스니펫)
from ..models.database import EdgeHint
import json

async def save_java_analysis(...):
    ...
    # 클래스/메서드 insert 후
    for m in methods:
        if hasattr(m, '_call_infos'):
            for ci in (m._call_infos or []):
                h = EdgeHint(
                    project_id=file_obj.project_id,
                    src_type='method', src_id=m.method_id,
                    hint_type='method_call',
                    hint=json.dumps({ 'called_name': ci.get('name'), 'arg_count': ci.get('arg_count'), 'line': ci.get('line') }),
                    confidence=0.8
                )
                session.add(h)
    session.commit()
```

3) 빌드 단계에서 해소

```python
# phase1/src/database/metadata_engine.py (스니펫 개선)
from sqlalchemy import and_, func
from ..models.database import EdgeHint, Edge, Method, Class, File
import json

async def _resolve_method_calls(self, session, project_id:int):
    hints = session.query(EdgeHint).filter(and_(EdgeHint.project_id==project_id, EdgeHint.hint_type=='method_call')).all()
    for h in hints:
        data = json.loads(h.hint)
        called = (data.get('called_name') or '').strip()
        argc   = int(data.get('arg_count') or 0)
        src = session.query(Method).filter(Method.method_id==h.src_id).first()
        if not src or not called:
            continue
        # 1) 동일 클래스
        candidates = session.query(Method).filter(and_(Method.class_id==src.class_id, Method.name==called)).all()
        m = _choose_overload(candidates, argc)
        if not m:
            # 2) 동일 패키지
            cls = session.query(Class).filter(Class.class_id==src.class_id).first()
            if cls and cls.fqn:
                pkg = cls.fqn.rsplit('.',1)[0]
                candidates = session.query(Method).join(Class).join(File).\
                    filter(and_(Method.name==called, Class.fqn.like(f"{pkg}.%"), File.project_id==project_id)).all()
                m = _choose_overload(candidates, argc)
        if not m:
            # 3) 전역 fallback
            candidates = session.query(Method).join(Class).join(File).\
                filter(and_(Method.name==called, File.project_id==project_id)).all()
            m = _choose_overload(candidates, argc)
        if m:
            session.add(Edge(src_type='method', src_id=h.src_id, dst_type='method', dst_id=m.method_id, edge_kind='call', confidence=min(1.0, h.confidence+0.2)))
        else:
            # 미해소: 낮은 신뢰도의 보류 엣지로 남김(필요 시 유지)
            session.add(Edge(src_type='method', src_id=h.src_id, dst_type='method', dst_id=None, edge_kind='call', confidence=max(0.1, h.confidence-0.3)))
        session.delete(h)  # 소비 후 제거
    session.commit()

def _choose_overload(candidates, argc):
    if not candidates: return None
    # 서명 파싱 비용을 줄이기 위해 괄호 내 파라미터 수만 우선 비교
    def count_params(signature:str)->int:
        try:
            inside = signature[signature.index('(')+1:signature.rindex(')')]
            return 0 if not inside.strip() else inside.count(',')+1
        except Exception:
            return 0
    scored = sorted(candidates, key=lambda m: (count_params(m.signature)==argc, m.method_id), reverse=True)
    return scored[0]
```

> 주: 서명 타입 일치까지 확장하려면 파라미터 타입 토큰화를 추가(11장 오버로드 항목 참조). 초기에는 arg_count 우선이 비용 대비 효과적입니다.

#### 2.1.3 JSP/MyBatis include 해소

1) 파서에서 include 힌트 생성

```python
# phase1/src/parsers/jsp_mybatis_parser.py (스니펫)
includes = self.dependency_tracker.extract_jsp_includes(content, file_obj.path)
# includes: { target_file, line_number, ... }
file_obj._include_hints = includes
```

2) 저장 단계에서 힌트 저장

```python
# phase1/src/database/metadata_engine.py (save_jsp_mybatis_analysis 내부)
from ..models.database import EdgeHint
import json

if hasattr(file_obj, '_include_hints'):
    for inc in (file_obj._include_hints or []):
        session.add(EdgeHint(
            project_id=file_obj.project_id, src_type='file', src_id=file_obj.file_id,
            hint_type='jsp_include', hint=json.dumps(inc), confidence=0.9
        ))
```

3) 빌드 단계에서 파일 매핑

```python
async def _resolve_includes(self, session, project_id:int):
    hints = session.query(EdgeHint).filter(and_(EdgeHint.project_id==project_id, EdgeHint.hint_type=='jsp_include')).all()
    for h in hints:
        data = json.loads(h.hint)
        target = (data.get('target_file') or '').replace('\\','/')
        f = session.query(File).filter(and_(File.project_id==project_id, File.path==target)).first()
        if f:
            session.add(Edge(src_type='file', src_id=h.src_id, dst_type='file', dst_id=f.file_id, edge_kind='include', confidence=h.confidence))
        session.delete(h)
    session.commit()
```

> MyBatis `<include refid>`는 XML 파서가 이미 `_resolve_includes_in_sql`로 SQL을 치환하지만, 문서 그래프 측면에서 “정의→사용”을 별도 엣지로 표현하려면 유사한 `edge_hints(hint_type='mybatis_include', hint={'refid':..., 'namespace':...})`를 추가하고, 매퍼 내 `<sql id>` 정의로 해소하는 규칙을 추가합니다.

#### 2.1.4 컴포넌트 라벨링 규칙 적용

저장 스키마 변경 없이, 뷰 빌더에서 파일 경로/패키지명으로 그룹을 결정합니다.

```python
# visualize/builders/component_diagram.py (스니펫)
import re
RULES = {
  'Controller': [r'.*\\.controller\\..*', r'.*Controller\\.java$'],
  'Service':    [r'.*\\.service\\..*', r'.*Service\\.java$'],
  'Repository': [r'.*\\.repository\\..*', r'.*Repository\\.java$'],
  'Mapper':     [r'.*Mapper\\.xml$'],
  'JSP':        [r'.*/WEB-INF/jsp/.*\\.jsp$'],
  'DB':         [r'^TABLE:']
}

def decide_group(path:str, fqn:str|None)->str:
    for g, pats in RULES.items():
        for p in pats:
            if re.match(p, fqn or path):
                return g
    return 'Code'
```

집계 엣지는 동일 그룹 간 엣지를 합치고 weight/confidence 평균을 계산해 시각적 단순화 제공합니다.

---

## 16) SQL 조인키 도출 개선(상세)

목표: 쿼리에서 테이블별 실제 조인 키를 더 정확히 도출하고, ERD 및 의존 그래프에 반영. 현행 regex/기초 sqlparse 추출을 강화하기 위해 아래를 수행합니다.

개선 항목(개발 순서 2단계에 해당)
- Alias 해소: `FROM ... table t` / `JOIN table b ON ...` 등 별칭→실테이블 매핑
- Owner/스키마 정규화: `OWNER.TABLE` 일관 처리 + `config.database.default_schema` 활용
- PK 교차검증: `DbPk`/`DbColumn` 기반으로 조인 컬럼 조합의 PK↔FK 가능성을 검증해 `inferred_pkfk`와 confidence 보정
- 복합키 추론: 동일 테이블 페어에 2개 이상 컬럼 조인 시 복합키로 마킹
- Confidence 정책: 검출 근거(명시 JOIN, PK 일치 여부, 빈도)에 따른 가중치

### 16.1 Alias 맵 추출(sqlparse 기반)

```python
# phase1/src/parsers/jsp_mybatis_parser.py (스니펫)
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

def _extract_alias_map(self, statement) -> dict:
    """SELECT/JOIN 구문에서 별칭 -> 실테이블 매핑 생성"""
    alias = {}
    def process_identifier(token: Identifier):
        # 예: schema.table AS t  또는 table t
        real_name = token.get_real_name()  # table
        alias_name = token.get_alias() or real_name
        if real_name:
            alias[alias_name.lower()] = self._normalize_table_name(real_name)

    for token in statement.tokens:
        if isinstance(token, IdentifierList):
            for ident in token.get_identifiers():
                process_identifier(ident)
        elif isinstance(token, Identifier):
            process_identifier(token)
        elif token.ttype is Keyword and token.value.upper() in ('FROM','JOIN','INNER JOIN','LEFT JOIN','RIGHT JOIN','FULL JOIN'):
            # 인접 토큰에서 Identifier를 탐색
            pass
        elif hasattr(token, 'tokens'):
            # 서브쿼리/그룹 내부 재귀
            alias.update(self._extract_alias_map(token))
    return alias

def _resolve_identifier_to_table(self, name:str, alias_map:dict)->str:
    # name: 't' 또는 'schema.table'
    if not name:
        return name
    key = name.lower()
    if key in alias_map:
        return alias_map[key]
    return self._normalize_table_name(name)
```

JOIN/WHERE 조건 추출 시 `table_alias.column` 형태의 `table_alias`를 위 맵으로 실테이블로 치환합니다.

### 16.2 JOIN 조건 추출 시 Alias 적용

```python
def _extract_joins_from_statement(self, statement, sql_unit) -> List[Join]:
    joins = []
    alias_map = self._extract_alias_map(statement)
    # 기존 탐색 로직은 유지하되, 조건에서 좌/우 테이블명을 치환
    for cond in self._find_join_conditions(statement):  # cond: (lt, lc, rt, rc)
        lt = self._resolve_identifier_to_table(cond.l_table, alias_map)
        rt = self._resolve_identifier_to_table(cond.r_table, alias_map)
        joins.append(Join(sql_id=None, l_table=lt, l_col=cond.l_col, r_table=rt, r_col=cond.r_col, op='=', inferred_pkfk=0, confidence=0.75))
    return joins
```

`_find_join_conditions`는 기존 `_parse_join_condition` 확장으로 `JOIN ... ON a.id=b.id`와 WHERE 암시적 조인 `a.id=b.id`를 모두 커버하도록 개선합니다.

### 16.3 스키마/Owner 정규화

```python
def _normalize_table_name(self, table_name: str) -> str:
    # 공백/따옴표 제거
    tn = table_name.strip().strip('"')
    if '.' in tn:
        owner, t = tn.split('.',1)
        return f"{owner.upper()}.{t.upper()}"
    default = self.default_schema or 'SAMPLE'
    return f"{default.upper()}.{tn.upper()}"
```

이 정규화는 이후 DB 스키마 매칭과 ERD 노드 ID 일관성에 필수입니다.

### 16.4 PK 교차검증 및 Confidence 보정

조인 조건이 실제 PK↔FK 관계일 가능성을 높이기 위해 `DbPk`/`DbColumn`를 교차 확인합니다.

```python
# phase1/src/database/metadata_engine.py (스니펫)
async def _validate_pk_fk(self, session, l_table:str, l_col:str, r_table:str, r_col:str) -> tuple[bool, bool]:
    # (left_is_pk, right_is_pk)
    from ..models.database import DbTable, DbPk
    def is_pk(owner_table:str, col:str)->bool:
        owner, tbl = owner_table.split('.',1)
        t = session.query(DbTable).filter(and_(DbTable.owner==owner, DbTable.table_name==tbl)).first()
        if not t: return False
        return session.query(DbPk).filter(and_(DbPk.table_id==t.table_id, DbPk.column_name==col.upper())).first() is not None
    return is_pk(l_table, l_col), is_pk(r_table, r_col)

async def _infer_pk_fk_relationships(self, session, project_id: int):
    # 기존 빈도 기반 + PK 교차검증 병합
    joins = session.query(Join).join(SqlUnit).join(File).filter(File.project_id==project_id).all()
    # 복합키 후보 묶기
    from collections import defaultdict
    pairs = defaultdict(list)
    for j in joins:
        key = (j.l_table, j.r_table)
        pairs[key].append((j.l_col, j.r_col, j.join_id))
    for (lt, rt), cols in pairs.items():
        # 복합키: 동일 테이블 페어에서 2개 이상 컬럼 매칭
        is_composite = len(cols) >= 2
        for (lc, rc, jid) in cols:
            left_pk, right_pk = await self._validate_pk_fk(session, lt, lc, rt, rc)
            j = session.query(Join).filter(Join.join_id==jid).first()
            # confidence 정책
            conf = j.confidence
            if left_pk ^ right_pk:  # 한쪽이 PK
                conf = max(conf, 0.85)
                j.inferred_pkfk = 1
            if left_pk and right_pk:  # PK↔PK (조인 관행 상 비정상, 낮춤)
                conf = min(conf, 0.6)
            if is_composite:
                conf = min(1.0, conf + 0.05)
            j.confidence = conf
    session.commit()
```

설명:
- 한쪽만 PK인 경우(FK→PK) 가능성이 높으므로 `inferred_pkfk=1`, confidence 상향(≥0.85)
- 양쪽 모두 PK면 비정형 조인이므로 confidence 하향
- 동일 테이블 페어에서 2개 이상 컬럼 조인 시 복합키 힌트로 소폭 상향

### 16.5 ERD/의존 그래프 반영

- ERD: `fk_inferred` 엣지의 confidence를 `Join.confidence`에 비례시켜 색/굵기 차등 표현(뷰어 레벨 스타일 추가)
- 의존 그래프: SQL→TABLE 엣지 외에, (선택) TABLE↔TABLE(FK 관계) 엣지를 얇은 선으로 추가 가능(기본 off)

```html
/* visualize/templates/erd_view.html 스타일 예시 */
<style>
  edge[kind = 'fk_inferred'][confidence > 0.85] { line-color:#2e7d32; target-arrow-color:#2e7d32; width:2; }
  edge[kind = 'fk_inferred'][confidence <= 0.85] { line-color:#9e9e9e; target-arrow-color:#9e9e9e; width:1; }
  node[type = 'table'] { shape:round-rectangle; background-color:#fff3e0; border-color:#ffb74d; border-width:1; }
}</style>
```

### 16.6 테스트 시나리오

1) `PROJECT/sampleSrc`의 `OrderMapper.xml` 등 다중 조인 쿼리로 분석 수행
2) DB_SCHEMA에 PK_INFO.csv 포함(DB_Pk 로드 확인)
3) `visualize erd`로 부분 ERD 출력 → FK 추론 색상·굵기 확인
4) `visualize graph --kinds use_table`로 SQL→TABLE 관계 확인

### 16.7 한계와 추후 항목

- 별칭이 서브쿼리/CTE에 중첩된 경우 추가 재귀 필요
- VIEW의 내재 SQL까지 추적하려면 `db_views.text` 파싱(차후)
- FK 메타테이블이 없는 환경(순수 CSV)에서는 빈도 기반 보조 규칙 유지


## 3) 디렉터리 구조 (./visualize)

```
visualize/
  cli.py                      # CLI 엔트리 포인트
  data_access.py              # DB 연결 및 조회 유틸
  schema.py                   # 시각화 JSON 스키마 정의
  filters.py                  # 포커스/깊이/검색/노드 cap 필터
  builders/
    dependency_graph.py       # 의존성 그래프 빌더
    sequence_diagram.py       # 시퀀스(흐름) 그래프 빌더
    component_diagram.py      # 컴포넌트 그래프 빌더
    erd.py                    # ERD 빌더
  templates/
    cyto_base.html            # 공통 템플릿(컨트롤/스타일/PNG export)
    graph_view.html           # 일반 그래프용
    erd_view.html             # ERD 전용 스타일
  static/
    cytoscape.min.js
    cytoscape-dagre.js
    style.css
  output/.gitkeep             # 결과물 출력 폴더
```

참고: 에셋은 로컬 파일을 기본으로 하고, 대안으로 CDN을 주석으로 안내.

## 4) 표준 그래프 JSON 스키마

```jsonc
{
  "nodes": [
    { "id": "n1", "type": "method", "label": "UserService.findUser()", "group": "Service", "meta": {"file": ".../UserService.java", "line": 120} },
    { "id": "t_USERS", "type": "table", "label": "SAMPLE.USERS", "group": "DB", "meta": {"owner": "SAMPLE"} }
  ],
  "edges": [
    { "id": "e1", "source": "n1", "target": "t_USERS", "kind": "use_table", "confidence": 0.9 }
  ]
}
```

- type: file|class|method|sql|table|view|component
- group: 시각적 그룹(Controller/Service/Repository/Mapper/JSP/DB 등)
- edge.kind: call|include|use_table|use_column|extends|implements|mapper_of|renders|fk_inferred 등

## 5) Data Access (SQLAlchemy)

```python
# visualize/data_access.py
from typing import Dict, Any, List, Tuple
from phase1.src.models.database import DatabaseManager, File, Class, Method, SqlUnit, Join, RequiredFilter, Edge, DbTable, DbColumn, DbPk

class VizDB:
    def __init__(self, config: Dict[str, Any]):
        self.dbm = DatabaseManager(config)
        self.dbm.initialize()

    def session(self):
        return self.dbm.get_session()

    def load_project(self, project_id: int):
        s = self.session()
        try:
            files = s.query(File).filter(File.project_id==project_id).all()
            return files
        finally:
            s.close()

    def fetch_edges(self, project_id: int, kinds: List[str], min_conf: float):
        s = self.session()
        try:
            q = s.query(Edge).filter(Edge.confidence >= min_conf)
            if kinds:
                from sqlalchemy import or_
                q = q.filter(or_(*[Edge.edge_kind==k for k in kinds]))
            return q.all()
        finally:
            s.close()

    def fetch_tables(self):
        s = self.session()
        try:
            return s.query(DbTable).all()
        finally:
            s.close()

    def fetch_pk(self):
        s = self.session()
        try:
            return s.query(DbPk).all()
        finally:
            s.close()

    def fetch_joins_for_project(self, project_id: int):
        s = self.session()
        try:
            from phase1.src.models.database import SqlUnit
            return s.query(Join).join(SqlUnit).join(File).\
                filter(File.project_id==project_id).all()
        finally:
            s.close()
```

## 6) CLI 설계 (서브커맨드)

```python
# visualize/cli.py
import argparse, json, os
from .builders.dependency_graph import build_dependency_graph_json
from .builders.erd import build_erd_json
from .builders.component_diagram import build_component_graph_json
from .builders.sequence_diagram import build_sequence_graph_json
from .templates.render import render_html

def main():
    p = argparse.ArgumentParser(prog='visualize')
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--project-id', type=int, required=True)
        sp.add_argument('--out', required=True, help='output html path')
        sp.add_argument('--min-confidence', type=float, default=0.5)
        sp.add_argument('--max-nodes', type=int, default=2000)
    
    g = sub.add_parser('graph')
    add_common(g)
    g.add_argument('--kinds', default='use_table,include,extends,implements')
    g.add_argument('--focus', help='start node (name/path/table)')
    g.add_argument('--depth', type=int, default=2)

    e = sub.add_parser('erd')
    add_common(e)
    e.add_argument('--tables', help='comma separated')
    e.add_argument('--owners', help='comma separated')
    e.add_argument('--from-sql', help='mapper_ns:stmt_id')

    c = sub.add_parser('component')
    add_common(c)

    s = sub.add_parser('sequence')
    add_common(s)
    s.add_argument('--start-file')
    s.add_argument('--start-method')
    s.add_argument('--depth', type=int, default=3)

    args = p.parse_args()
    kinds = args.kinds.split(',') if getattr(args, 'kinds', None) else []

    if args.cmd == 'graph':
        data = build_dependency_graph_json(args.project_id, kinds, args.min_confidence, args.focus, args.depth, args.max_nodes)
        html = render_html('graph_view.html', data)
    elif args.cmd == 'erd':
        data = build_erd_json(args.project_id, args.tables, args.owners, args.from_sql)
        html = render_html('erd_view.html', data)
    elif args.cmd == 'component':
        data = build_component_graph_json(args.project_id, args.min_confidence, args.max_nodes)
        html = render_html('graph_view.html', data)
    else:  # sequence
        data = build_sequence_graph_json(args.project_id, args.start_file, args.start_method, args.depth, args.max_nodes)
        html = render_html('graph_view.html', data)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    main()
```

## 7) 템플릿과 뷰어 (Cytoscape.js)

```html
<!-- visualize/templates/cyto_base.html (개요) -->
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Source Analyzer Viz</title>
  <style>
    body, html { margin:0; height:100%; }
    #toolbar { padding:8px; border-bottom:1px solid #ddd; }
    #cy { width:100%; height:calc(100% - 42px); }
    .node-component { background-color:#e0f7fa; }
    .node-db { background-color:#ffe0b2; }
  </style>
  <script src="../static/cytoscape.min.js"></script>
  <script src="../static/cytoscape-dagre.js"></script>
  <script>
    const DATA = __DATA_PLACEHOLDER__;
  </script>
  </head>
<body>
  <div id="toolbar">
    <button onclick="cy.fit()">Fit</button>
    <button onclick="exportPng()">Export PNG</button>
    <input id="q" placeholder="Search" oninput="searchNode(this.value)">
  </div>
  <div id="cy"></div>
  <script>
    const elements = [];
    for (const n of DATA.nodes) {
      elements.push({ data: { id:n.id, label:n.label, type:n.type, group:n.group }});
    }
    for (const e of DATA.edges) {
      elements.push({ data: { id:e.id, source:e.source, target:e.target, kind:e.kind, confidence:e.confidence }});
    }

    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements,
      style: [
        { selector:'node', style:{ 'label':'data(label)', 'font-size':10, 'text-wrap':'wrap', 'text-max-width':160 }},
        { selector:'edge', style:{ 'curve-style':'bezier','width':1,'line-color':'#999','target-arrow-shape':'triangle','target-arrow-color':'#999'}},
        { selector:'node[group = "DB"]', style:{ 'background-color':'#ffb74d' }},
        { selector:'node[type = "component"]', style:{ 'shape':'round-rectangle','background-color':'#80deea' }}
      ],
      layout: { name:'dagre', rankDir:'LR', nodeSep: 30, rankSep: 60 }
    });

    function exportPng(){
      const png64 = cy.png({ full:true, scale:2 });
      const a = document.createElement('a');
      a.href = png64; a.download = 'graph.png'; a.click();
    }
    function searchNode(q){
      cy.nodes().unselect();
      if(!q) return;
      cy.nodes().filter(n=> (n.data('label')||'').toLowerCase().includes(q.toLowerCase())).select();
    }
  </script>
</body>
</html>
```

템플릿 렌더링은 단순 치환(`__DATA_PLACEHOLDER__` → JSON.dump)로 충분.

## 8) Builders 알고리즘 및 스니펫

### 8.1 의존성 그래프

입력: `project_id, kinds, min_confidence, focus, depth, max_nodes`

로직:
1) `Edge`에서 종류/신뢰도 필터 후 수집(초기 전체)
2) `focus`가 있으면 해당 노드를 기준 BFS로 `depth` 제한 서브그래프 추출
3) 노드 cap(`max_nodes`) 적용 및 미적용 시 경고

```python
# visualize/builders/dependency_graph.py
from ..data_access import VizDB
from ..schema import to_json

def build_dependency_graph_json(project_id:int, kinds, min_conf:float, focus:str, depth:int, max_nodes:int):
    db = VizDB(_load_config())
    edges = db.fetch_edges(project_id, kinds, min_conf)
    # 노드 구성: src/dst 타입 추정이 필요한 경우 lookup 구현
    nodes = {}
    def add_node(id, type_, label, group, meta=None):
        if id not in nodes:
            nodes[id] = { 'id': id, 'type': type_, 'label': label, 'group': group, 'meta': meta or {} }

    json_edges = []
    for e in edges:
        # 예시: 타입/라벨은 후술하는 helper로 보강
        sid = f"{e.src_type}:{e.src_id}"; tid = f"{e.dst_type}:{e.dst_id}"
        json_edges.append({ 'id': f"edge:{e.edge_id}", 'source': sid, 'target': tid, 'kind': e.edge_kind, 'confidence': e.confidence })
        add_node(sid, e.src_type, sid, _guess_group(e.src_type))
        add_node(tid, e.dst_type, tid, _guess_group(e.dst_type))

    if focus:
        nodes, json_edges = _bfs_limit(nodes, json_edges, focus, depth)

    nodes_list = list(nodes.values())[:max_nodes]
    return { 'nodes': nodes_list, 'edges': json_edges }
```

### 8.2 ERD

입력: `project_id, tables, owners, from_sql`

로직:
1) `DbTable`, `DbPk` 로드
2) `joins` 패턴에서 반복 출현/PK 조합을 근거로 FK 추론 → `fk_inferred` 엣지 생성 (기존 `metadata_engine._infer_pk_fk_relationships`와 동일 규칙 사용)
3) 선택 필터(`tables, owners, from_sql`) 적용

```python
# visualize/builders/erd.py
from ..data_access import VizDB

def build_erd_json(project_id:int, tables:str, owners:str, from_sql:str):
    db = VizDB(_load_config())
    tbls = db.fetch_tables()
    pks = db.fetch_pk()
    joins = db.fetch_joins_for_project(project_id)

    wanted_tables = set(t.strip().upper() for t in (tables.split(',') if tables else []))
    wanted_owners = set(o.strip().upper() for o in (owners.split(',') if owners else []))

    nodes = {}
    def add_table(t):
        key = f"{t.owner}.{t.table_name}" if t.owner else t.table_name
        nodes[key] = { 'id': key, 'type':'table', 'label': key, 'group':'DB', 'meta': {} }

    for t in tbls:
        if wanted_tables and t.table_name.upper() not in wanted_tables: continue
        if wanted_owners and (t.owner or '').upper() not in wanted_owners: continue
        add_table(t)

    edges = []
    # 간단한 FK 추론: 동일 패턴 다발 → 관계 성립
    from collections import Counter
    cnt = Counter([ (j.l_table, j.l_col, j.r_table, j.r_col) for j in joins ])
    for (lt, lc, rt, rc), freq in cnt.items():
        if freq >= 2:
            sid = f"{j_owner(nodes, lt)}.{lt}"; tid = f"{j_owner(nodes, rt)}.{rt}"
            if sid in nodes and tid in nodes:
                edges.append({ 'id': f"fk:{lt}.{lc}->{rt}.{rc}", 'source': sid, 'target': tid, 'kind':'fk_inferred', 'confidence': 0.7 })

    return { 'nodes': list(nodes.values()), 'edges': edges }
```

### 8.3 컴포넌트 다이어그램

컴포넌트 규칙(초기값, 설정 가능):

```python
RULES = {
  'Controller': [r'.*\.controller\..*', r'.*Controller\.java$'],
  'Service':    [r'.*\.service\..*', r'.*Service\.java$'],
  'Repository': [r'.*\.repository\..*', r'.*Repository\.java$'],
  'Mapper':     [r'.*Mapper\.xml$'],
  'JSP':        [r'.*/WEB-INF/jsp/.*\.jsp$'],
  'DB':         ['TABLE:*']
}
```

로직: 엔티티를 컴포넌트로 매핑하고, 엣지는 컴포넌트 단위로 집계(가중치=엣지 수/평균 confidence)

### 8.4 시퀀스(흐름) 다이어그램

초기: JSP → SQL(Unit) → TABLE 흐름을 레이어드 레이아웃으로 표현. Java call 보강 후, Controller → Service → Repository/Mapper → DB 흐름 확장.

## 9) 필터·포커스·성능

- BFS 기반 포커스/깊이 제한: 시작 노드에서 `depth` 단계까지만 확장
- `max_nodes` cap: 초과 시 UI 경고 및 더 좁은 필터 안내
- `min_confidence`: 신뢰도 기반 필터링 기본값 0.5

```python
def _bfs_limit(nodes:dict, edges:list, focus_label:str, depth:int):
    # label/id 모두 지원
    label_to_id = { n['label']: n['id'] for n in nodes.values() }
    start = label_to_id.get(focus_label, focus_label)
    adj = {}
    for e in edges:
        adj.setdefault(e['source'], set()).add(e['target'])
        adj.setdefault(e['target'], set()).add(e['source'])
    from collections import deque
    q = deque([(start,0)]); seen={start}
    kept_nodes=set(); kept_edges=[]
    while q:
        u,d = q.popleft(); kept_nodes.add(u)
        if d==depth: continue
        for v in adj.get(u,()):
            if v not in seen:
                seen.add(v); q.append((v,d+1))
            kept_nodes.add(v)
    for e in edges:
        if e['source'] in kept_nodes and e['target'] in kept_nodes:
            kept_edges.append(e)
    return ({ nid:n for nid,n in nodes.items() if nid in kept_nodes }, kept_edges)
```

## 10) 메타데이터 보강 (TODO1 내 권장)

### 10.1 Java 메서드 호출 해소

문제: 파서가 call 엣지를 생성하되 `dst_id` 미결 → 저장 시 필터되어 시각화에 부족.

권장 방안:
1) 파서에서 호출 대상명을 엣지 메타(예: `edge.metadata['called_method_name']`)에 저장
2) `MetadataEngine.build_dependency_graph()`에서 대상 메서드를 탐색해 `dst_id`를 채우고 update/insert
3) 매칭 규칙(우선순위):
   - 동일 클래스(Method.class_id 동일)
   - 동일 패키지 내 같은 이름
   - 프로젝트 전체에서 같은 이름 (confidence 감소)
   - 오버로드 존재 시, 파라미터 수·타입 일치 우선

코드 스케치:

```python
# phase1/src/database/metadata_engine.py (개념 스니펫)
async def _resolve_method_calls(self, session, project_id:int):
    unresolved = session.query(Edge).filter(and_(Edge.edge_kind=='call', Edge.dst_id.is_(None))).all()
    for e in unresolved:
        src = session.query(Method).filter(Method.method_id==e.src_id).first()
        if not src: continue
        called = getattr(e, 'metadata', {}).get('called_method_name', '')
        if not called: continue
        # 1) 같은 클래스 내
        m = session.query(Method).filter(and_(Method.class_id==src.class_id, Method.name==called)).first()
        if not m:
            # 2) 같은 패키지 내 (Class.fqn prefix 매칭)
            cls = session.query(Class).filter(Class.class_id==src.class_id).first()
            if cls and cls.fqn:
                pkg = cls.fqn.rsplit('.',1)[0]
                m = session.query(Method).join(Class).join(File).\
                    filter(and_(Method.name==called, Class.fqn.like(f"{pkg}.%"), File.project_id==project_id)).first()
        if not m:
            # 3) 프로젝트 전체 fallback
            m = session.query(Method).join(Class).join(File).\
                filter(and_(Method.name==called, File.project_id==project_id)).first()
        if m:
            e.dst_type='method'; e.dst_id=m.method_id; e.confidence=min(1.0, e.confidence+0.2)
        else:
            e.confidence=max(0.1, e.confidence-0.3)
    session.commit()
```

추가 정확도(아래 11장 세부): 오버로드·정적 임포트·동적 바인딩 대응.

### 10.2 JSP/MyBatis include 해소

파서에서 include 엣지 후보 생성 → build 단계에서 대상 파일 식별 후 저장.

```python
# 파일 경로 기반 해소
target_file = session.query(File).filter(and_(File.project_id==project_id, File.path==edge_meta['target_file'])).first()
if target_file:
    e.dst_type='file'; e.dst_id=target_file.file_id; e.confidence=0.9
```

### 10.3 컴포넌트 라벨링

패키지·경로 규칙을 설정(`config.visualize.component_rules`)하고, 조회 시 `group` 필드를 채우거나 뷰어에서 on-the-fly로 결정.

## 11) 정확성 개선: 오버로드/정적 임포트/동적 바인딩

시각화의 품질은 call 해소 정확도에 크게 좌우됩니다. 현실적·경량 해법과 신뢰도 조정 방안을 제안합니다.

### 11.1 오버로드(Overload) 해소

- 소스: `javalang` AST에서 `MethodInvocation`는 인자 리스트 정보를 제공. `MethodDeclaration`는 파라미터 타입/수 보유.
- 전략:
  1) 파라미터 수 우선 매칭
  2) 타입 문자열 매칭(간단 erasure: 제네릭 제거, 배열/varargs 정규화)
  3) 가변 인자(varargs): 마지막 파라미터가 `T...`이면 `n>=len(params)-1` 허용
  4) 다수 후보 시: 접근 제어자(public 우선)와 동일 클래스/패키지 우선, 나머지는 낮은 confidence로 보존

```python
def _normalize_type(t:str)->str:
    return (t or '').replace('[]','').split('<')[0]

def _score_overload(candidates, arg_types:list)->tuple:
    # (score, method) 높은 점수 우선
    best = []
    for m in candidates:
        m_types = [_normalize_type(p) for p in m.signature_param_types]
        s = 0
        if len(arg_types)==len(m_types): s += 2
        s += sum(1 for a,b in zip(arg_types,m_types) if _normalize_type(a)==b)
        best.append((s, m))
    return max(best) if best else (0,None)
```

신뢰도 조정: 완전 일치(+0.2), 수만 일치(+0.1), 미일치(-0.2) 등 가중치 적용.

### 11.2 정적 임포트(Static Import)

- `import static com.foo.Util.*;` 또는 `import static com.foo.Util.method;` 형태
- 전략:
  - CompilationUnit의 import 목록을 파싱해 static import를 수집
  - 수신자(qualifier) 없는 호출이면서 static import로 메서드가 노출된 경우, 해당 클래스 후보에 우선 연결
  - 다수 후보 시 동일 이름을 가진 유틸리티 클래스 집합 구성 → 모두 후보로 두되 낮은 confidence

### 11.3 동적 바인딩(Dynamic Binding)

- 호출 수신자의 정적 타입으로 우선 해소(필드/지역변수 선언 타입)
- 인터페이스 타입인 경우:
  - 프로젝트 내 구현 클래스 목록에서 동일 메서드명을 가진 구현체들을 후보로 생성
  - 각 후보로 엣지를 복수 생성하되 confidence를 분산(예: 0.5/개수)
  - 구현체 수 과다 시 상위 N개(패키지 근접/이름 유사도)만 유지
- 리플렉션/프록시/프레임워크 바인딩은 “ambiguous_call” 메타로 남기고 낮은 confidence 부여

향후(2차): 간단한 points-to/타입 전파, Spring Bean 스캔(컴포넌트 스캔 + @Autowired/@Inject)로 레이어 간 call 보강.

## 12) PNG Export

- HTML 뷰어에서 `cy.png()` 사용(전체/현재뷰, scale=2)
- 버튼 제공 및 단축키(optional)
- 2차: headless export 필요시 `pyppeteer`로 렌더-스크린샷 파이프라인 제공

## 13) 설정 추가(선택)

`config/config.yaml` 예시 항목:

```yaml
visualize:
  max_nodes: 2000
  min_confidence: 0.5
  component_rules:
    Controller: [".*\\.controller\\..*", ".*Controller\\.java$"]
    Service:    [".*\\.service\\..*", ".*Service\\.java$"]
    Repository: [".*\\.repository\\..*", ".*Repository\\.java$"]
    Mapper:     [".*Mapper\\.xml$"]
    JSP:        [".*/WEB-INF/jsp/.*\\.jsp$"]
```

## 14) 구현 단계 (마일스톤)

1) 스캐폴딩 생성(폴더/파일/템플릿 최소본) 및 CLI `graph`/`erd` 동작 확인
2) 컴포넌트 빌더 추가(규칙 하드코딩 → 설정화)
3) 시퀀스(초안: JSP→SQL→TABLE 흐름)
4) 메타 보강 1: JSP/MyBatis include 해소, Java call 기본 해소(이름/패키지 우선)
5) 정확성 1: 오버로드/정적 임포트/동적 바인딩 휴리스틱 + confidence 가중치 반영
6) 대용량 대응: BFS/노드 cap·검색·경고 UX 정리
7) 테스트/튜닝: `PROJECT/sampleSrc`로 케이스 점검, 스냅샷 산출

## 15) 테스트 플로우

1) 분석 수행 → 메타DB 생성(`data/metadata.db`)
2) ERD: `python -m visualize erd --project-id 1 --out visualize/output/erd.html`
3) 그래프: `python -m visualize graph --project-id 1 --kinds use_table,include --out visualize/output/dep.html`
4) 컴포넌트: `python -m visualize component --project-id 1 --out visualize/output/components.html`
5) 시퀀스: `python -m visualize sequence --project-id 1 --start-file <jsp path> --out visualize/output/seq.html`

## 부록 A) 템플릿 렌더러

```python
# visualize/templates/render.py
import json, os

def render_html(template_name:str, data:dict)->str:
    here = os.path.dirname(__file__)
    base = os.path.join(here, template_name)
    with open(base, 'r', encoding='utf-8') as f:
        tpl = f.read()
    return tpl.replace('__DATA_PLACEHOLDER__', json.dumps(data))
```

## 부록 B) 그룹 추정 헬퍼

```python
def _guess_group(type_:str)->str:
    return {
        'table':'DB', 'view':'DB', 'sql_unit':'Mapper', 'method':'Code', 'class':'Code', 'file':'Code', 'component':'Component'
    }.get(type_.lower(), 'Code')
```

---

본 설계를 기반으로 `./visualize` 초기 구현(템플릿, CLI, ERD/그래프 빌더)부터 진행한 뒤, 메타 보강(호출 해소/인클루드 해소)을 같은 브랜치에서 이어가면 TODO1 요구(시각화, PNG, 선택 생성)가 1차로 충족됩니다. 이후 정확성 개선(오버로드/정적·동적 해석)과 자동 PNG(헤드리스) 등 2차 항목을 점진적으로 반영합니다.
