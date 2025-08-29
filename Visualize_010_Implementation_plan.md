# Source Analyzer 구현 계획 (Visualize_010)

- 계획 버전: v1.4 (제안)
- 문서 생성: 2025-08-29
- 관련 문서: Visualize_009_Implementation.md의 [TODO] 해결 계획서

---

## 개요

본 계획서는 Visualize_009_Implementation.md에 남아있는 다음 [TODO] 항목을 해결하기 위한 설계·구현 방법과 검증 방안을 상세히 제시합니다. 소스 코드 변경은 본 문서에 제안·스니펫 형태로만 포함하며, 실제 수정은 별도 커밋에서 진행합니다.

- [TODO] JSP/MyBatis 동적 SQL 처리 오류
- [TODO] 데이터베이스 세션 관리 불완전
- [TODO] Mermaid 내보내기 단순화 오류
- [TODO] 트랜잭션 경계 모호성
- [TODO] 문서-구현 불일치 (설정 예제 오류)

---

## 공통 전제 및 원칙

- 성능 유지: 대용량 JSP/XML 및 병렬 분석(스레드풀) 환경에서 안정적으로 동작.
- 정확도 우선: 동적 SQL 처리 시 손실 최소화, 과다검출 억제.
- 원자성 보장: 파일 단위 저장과 향상(Enhancement) 단계의 트랜잭션 경계 명확화.
- 설정 일관: README의 설정 값이 실제 코드에 반영되고, 런타임 로그로 확인 가능.

---

## 1) JSP/MyBatis 동적 SQL 처리 개선

### 문제 요약

- 정규식 기반 전개에서 `<if>`, `<choose>/<when>/<otherwise>`, `<foreach>`, `<trim>/<where>/<set>`, `<bind>`, `<include>` 등 MyBatis 동적 요소의 조건/구조 정보가 손실되거나 엣지·필터 추출이 누락됨.

### 설계 요지

- lxml 기반 AST 처리 파이프라인을 도입하여, “조건 보존”과 “분기 요약”을 병행.
- `<include>`/`<bind>`는 해석·인라인 하되, 순환 참조 캐시로 보호.
- `<choose>`/`<when>`/`<otherwise>`는 “대표 경로 전개”+“optional 메타”로 표현.
- `<foreach>`는 IN/OR 요약 표현으로 정규화(예: `col IN (:param[])`).
- 결과 SQL은 플레이스홀더 정규화 후 `normalized_fingerprint`에 반영.

### 주요 변경 파일(제안)

- `phase1/src/parsers/jsp_mybatis_parser.py`

### 구현 상세 및 스니펫

- 새 유틸: DynamicSqlResolver (lxml Element → 정규화된 텍스트)

```python
# phase1/src/parsers/jsp_mybatis_parser.py (새 유틸 클래스 추가)
from lxml import etree
from typing import Dict, Tuple, List

class DynamicSqlResolver:
    """
    MyBatis 동적 태그(include/bind/choose/foreach/if/trim/where/set) 해석기
    - 조건 보존: optional 주석/메타로 표시
    - 분기 요약: 대표 분기만 전개(max_branch)
    - 안전 장치: include 순환 참조 방지, 캐시 사용
    """
    def __init__(self, namespace: str, max_branch: int = 3):
        self.ns = namespace
        self.max_branch = max_branch
        self.visited_refids = set()
        self.sql_fragment_cache: Dict[str, etree._Element] = {}
        self.bind_vars: Dict[str, str] = {}

    def prime_cache(self, root: etree._Element):
        # <sql id="..."> 프래그먼트 캐시화
        for frag in root.xpath('.//sql'):
            frag_id = frag.get('id')
            if frag_id:
                self.sql_fragment_cache[frag_id] = frag

    def resolve(self, element: etree._Element) -> str:
        self._resolve_bind_vars(element)
        self._inline_includes(element)
        self._flatten_choose(element)
        self._flatten_foreach(element)
        self._unwrap_if_trim_where_set(element)
        return self._collect_text(element)

    def _inline_includes(self, element: etree._Element):
        for inc in element.xpath('.//include'):
            refid = inc.get('refid')
            if not refid:
                continue
            if refid in self.visited_refids:
                # 순환 보호: 주석으로 대체
                inc.getparent().replace(inc, etree.Comment(f"circular-include:{refid}"))
                continue
            self.visited_refids.add(refid)
            frag = self.sql_fragment_cache.get(refid)
            if frag is not None:
                # 복제하여 인라인
                inc.getparent().replace(inc, etree.fromstring(etree.tostring(frag)))

    def _resolve_bind_vars(self, element: etree._Element):
        # <bind name="var" value="..."/>
        for b in element.xpath('.//bind'):
            name = b.get('name')
            val = b.get('value')
            if name and val:
                self.bind_vars[name] = val
            b.getparent().remove(b)

        # 간단한 텍스트 대체 (고급 치환은 추후 확장)
        text = etree.tostring(element, encoding='unicode')
        for k, v in self.bind_vars.items():
            text = text.replace(f"#{{{k}}}", v)
        new_elem = etree.fromstring(text)
        element.clear()
        element.tag = new_elem.tag
        element.attrib.update(new_elem.attrib)
        for child in list(element):
            element.remove(child)
        for child in new_elem:
            element.append(child)

    def _flatten_choose(self, element: etree._Element):
        for choose in element.xpath('.//choose'):
            whens = choose.xpath('./when')[: self.max_branch]
            otherwise = choose.xpath('./otherwise')
            picked = whens or otherwise
            if picked:
                # 대표 분기만 전개, 조건은 주석으로 보존
                chosen = picked[0]
                comment = etree.Comment(f"choose: {chosen.get('test', 'otherwise')}")
                choose.addprevious(comment)
                choose.getparent().replace(choose, chosen)
            else:
                choose.getparent().remove(choose)

    def _flatten_foreach(self, element: etree._Element):
        # foreach 블록을 IN/OR 요약 표현으로 치환
        for fe in element.xpath('.//foreach'):
            item = fe.get('item', 'item')
            col_hint = fe.get('collection', 'list')
            placeholder = f":{col_hint}[]"
            summarized = etree.Element('text')
            summarized.text = f" IN ({placeholder}) "
            fe.getparent().replace(fe, summarized)

    def _unwrap_if_trim_where_set(self, element: etree._Element):
        # 조건부/포장 태그는 내용만 남기고 optional 주석 추가
        for tag in ['if', 'trim', 'where', 'set']:
            for t in element.xpath(f'.//{tag}'):
                test = t.get('test') if tag == 'if' else tag
                t.addprevious(etree.Comment(f"optional:{test}"))
                self._unwrap(t)

    def _unwrap(self, node: etree._Element):
        parent = node.getparent()
        idx = parent.index(node)
        for child in list(node):
            parent.insert(idx, child)
            idx += 1
        parent.remove(node)

    def _collect_text(self, elem: etree._Element) -> str:
        def walk(e) -> List[str]:
            parts = [e.text or '']
            for c in e:
                parts.extend(walk(c))
                parts.append(c.tail or '')
            return parts
        text = ' '.join(walk(elem))
        return ' '.join(text.split())  # 공백 정규화
```

- 파서 통합: MyBatis XML 경로에 해석 적용

```python
# phase1/src/parsers/jsp_mybatis_parser.py (_parse_mybatis_xml 내부, 요소 처리 직전)
parser = etree.XMLParser(recover=True)
root = etree.fromstring(content.encode('utf-8'), parser)
namespace = root.get('namespace', '')

resolver = DynamicSqlResolver(namespace, max_branch=self.config.get('mybatis', {}).get('max_branch', 3))
resolver.prime_cache(root)

for stmt_type in ['select', 'insert', 'update', 'delete', 'sql']:
    for element in root.xpath(f'.//{stmt_type}'):
        start_line = int(element.sourceline or 0)
        sql_text = resolver.resolve(element)
        normalized = self._normalize_sql(sql_text)  # ${}/#{} 등 플레이스홀더 정규화
        sql_unit = SqlUnit(
            file_id=None,
            origin='mybatis',
            mapper_ns=namespace or None,
            stmt_id=element.get('id', f'{stmt_type}_{start_line}'),
            start_line=start_line,
            end_line=self._estimate_end_line(element, start_line),
            stmt_kind=stmt_type,
            normalized_fingerprint=self._create_sql_fingerprint(normalized)
        )
        sql_units.append(sql_unit)
        joins_found, filters_found = self._extract_sql_patterns_advanced(normalized, sql_unit)
        joins.extend(joins_found)
        filters.extend(filters_found)
```

- JSP 스크립틀릿/표현식 추출 강화: AdvancedSqlExtractor 활용 및 정규식 폴백 병행(현 구조 유지).

```python
# phase1/src/parsers/jsp_mybatis_parser.py (_parse_jsp 내부 발췌)
extracts = self.advanced_sql_extractor.extract_sql_from_jsp(content)
for i, ex in enumerate(extracts, start=1):
    sql_unit = SqlUnit(
        file_id=None,
        origin='jsp',
        mapper_ns=None,
        stmt_id=f'jsp_sql_{ex["line_number"]}_{i}',
        start_line=ex['line_number'],
        end_line=ex['line_number'],
        stmt_kind=self._detect_sql_type(ex['sql_content']),
        normalized_fingerprint=self._create_sql_fingerprint(ex['sql_content'])
    )
    sql_units.append(sql_unit)
    j, f = self._extract_sql_patterns_advanced(ex['sql_content'], sql_unit)
    joins.extend(j); filters.extend(f)
```

### 테스트 및 수용 기준

- 샘플 매퍼(`PROJECT/sampleSrc/.../mybatis/*.xml`) 대상: 조인/필터/인클루드 엣지 카운트가 기존 대비 동일 이상.
- `<choose>`/`<foreach>` 포함 케이스에서 손실/과다 전개가 없고, Optional 메타(주석)로 불확실성 표시.
- `${}` 사용 케이스에 SQL Injection 경고 유지(`SqlInjectionDetector`).

---

## 2) 데이터베이스 세션 관리 불완전 개선

### 문제 요약

- 롤백 후 `close()` 누락, 스레드풀 병렬 환경에서 세션 경계가 불명확하여 연결/커서 고갈 위험.

### 설계 요지

- 세션 팩토리: `scoped_session(sessionmaker(..., expire_on_commit=False))` 적용.
- 트랜잭션: 저장 루틴은 `with session.begin():` 경계로 원자성 보장, 산발적 `commit()` 제거.
- 컨텍스트: 동기/비동기 컨텍스트 매니저는 내부에서 `begin()` 사용으로 일원화.

### 구현 스니펫

```python
# phase1/src/models/database.py (DatabaseManager.initialize)
from sqlalchemy.orm import scoped_session, sessionmaker

self.engine = create_engine(db_url, **engine_args)
Base.metadata.create_all(self.engine)

# Thread-local scoped session
self.Session = scoped_session(sessionmaker(
    bind=self.engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
))

def get_session(self):
    return self.Session()
```

```python
# phase1/src/database/metadata_engine.py (_get_sync_session 개선 예)
from contextlib import contextmanager

@contextmanager
def _get_sync_session(self):
    session = self.db_manager.get_session()
    try:
        with session.begin():
            yield session
    except Exception:
        # session.begin() 컨텍스트가 자동 롤백
        raise
    finally:
        session.close()
```

```python
# 저장 루틴 사용 예 (_save_jsp_mybatis_analysis_sync 발췌)
with self._get_sync_session() as session:
    # 모든 add/flush/edge/persist가 단일 트랜잭션 경계 안에서 수행됨
    session.add(file_obj)
    session.flush()
    # ...
    # 명시 commit() 불필요 (begin() 컨텍스트가 커밋)
```

### 테스트 및 수용 기준

- 병렬 분석 N회 반복 후 DB 연결/커서 수 정상, `database is locked`(SQLite)·커서 고갈(Oracle) 미발생.
- 예외 유발 테스트에서 리소스 누수 없이 다음 작업 정상 진행.

---

## 3) Mermaid 내보내기 단순화 개선

### 문제 요약

- 단순화 과정에서 중요 엣지(교차 그룹, 고신뢰)가 제거되거나 클래스 다이어그램 속성/메서드 제한이 일괄 적용되어 가독성이 저하.

### 설계 요지

- Export 전략: `full | balanced | minimal` 프리셋 도입.
- 세분화 파라미터: `class_methods_max`, `class_attrs_max`, `min_confidence`, `keep_edge_kinds`.
- Overflow 안내: 잘린 항목은 Markdown 하단에 요약 섹션으로 제공.

### 구현 스니펫

```python
# visualize/exporters/mermaid_exporter.py (생성자 파라미터 확장)
class MermaidExporter:
    def __init__(self, label_max: int = 20, erd_cols_max: int = 10,
                 class_methods_max: int = 10, class_attrs_max: int = 10,
                 min_confidence: float = 0.0, keep_edge_kinds: tuple = ("includes","call","use_table")):
        self.max_label_length = label_max
        self.erd_cols_max = erd_cols_max
        self.class_methods_max = class_methods_max
        self.class_attrs_max = class_attrs_max
        self.min_confidence = min_confidence
        self.keep_edge_kinds = set(keep_edge_kinds)
        # ...
```

```python
# 클래스 다이어그램 제한 분리 적용 (발췌)
attributes = meta.get('attributes', [])[: self.class_attrs_max]
methods = [m for m in meta.get('methods', []) if not m.get('is_special')][: self.class_methods_max]
```

```python
# 엣지 필터링 (공통 적용)
def _filter_edges(self, edges: list) -> tuple[list, list]:
    kept, dropped = [], []
    for e in edges:
        if (e.get('confidence', 1.0) >= self.min_confidence) or (e.get('kind') in self.keep_edge_kinds):
            kept.append(e)
        else:
            dropped.append(e)
    return kept, dropped
```

```python
# Markdown 문서에 overflow/드롭 요약 추가 (발췌)
kept_edges, dropped_edges = self._filter_edges(data.get('edges', []))
# 기존 mermaid_content는 kept_edges로 생성
if dropped_edges:
    md_lines.extend([
        "",
        "## 단순화로 제외된 항목",
        f"- 제외 엣지: {len(dropped_edges)}",
        "<details>",
        "<summary>목록 보기</summary>",
        "",
    ])
    for e in dropped_edges[:50]:
        md_lines.append(f"- {e.get('source')} -[{e.get('kind','edge')}]-> {e.get('target')} (conf={e.get('confidence',1.0):.2f})")
    md_lines.extend(["</details>", ""]) 
```

```bash
# visualize_cli.py (예: 옵션)
--export-strategy balanced \
  --min-confidence 0.4 \
  --keep-edge-kinds includes,call,use_table
```

### 테스트 및 수용 기준

- 동일 데이터셋에서 full/balanced/minimal 비교 시 교차 그룹/핵심 엣지는 항상 보존.
- Mermaid Live Editor에서 모두 정상 렌더.

---

## 4) 트랜잭션 경계 모호성 제거

### 문제 요약

- 파일 저장과 엔티티 저장, 엣지 생성이 분산된 커밋으로 처리되어 부분 반영 가능성 존재.

### 설계 요지

- 저장 루틴(파일 단위): 단일 `with session.begin():` 경계로 원자성 보장.
- 향상 엔진 단계(메서드 호출/인클루드/조인 강화): 단계별 독립 트랜잭션, 실패 시 해당 단계만 롤백.

### 구현 스니펫

```python
# phase1/src/database/metadata_engine.py (_save_java_analysis_sync/_save_jsp_mybatis_analysis_sync 공통 패턴)
with self.db_manager.get_session() as session:
    with session.begin():
        session.add(file_obj)
        session.flush()
        # classes/methods/sql_units/joins/filters/edges 저장 일괄 수행
        # 유효성 필터링 후 add()
        # 수동 commit() 호출 불필요
```

```python
# phase1/src/database/metadata_enhancement_engine.py (단계별 begin)
def _resolve_method_calls(...):
    with self.session.begin():
        # 힌트→엣지 생성, 힌트 제거

def _resolve_jsp_includes(...):
    with self.session.begin():
        # JSP include 힌트 처리

def _resolve_mybatis_includes(...):
    with self.session.begin():
        # MyBatis include 힌트 처리

def _enhance_sql_joins(...):
    with self.session.begin():
        # PK/FK 검증 및 confidence 조정
```

### 테스트 및 수용 기준

- 중간 예외 유발 시 해당 단위 전부 롤백되어 DB 무결성 유지.
- 카운트/인덱스 일관성(에지 수, 조인 수, 필터 수)이 맞음.

---

## 5) 문서-구현 불일치(설정 예제) 정합성 확보

### 문제 요약

- `README.md`의 `parser_type` 예시가 실제 코드에서 반영되지 않음. `java_parser.py` 내 `parser_used` 미정의 버그.

### 설계 요지

- 지원 값 표준화:
  - Java: `javalang` | `tree-sitter` | `javaparser`(예정)
- Python: `ast`
- 구성값 반영 로직을 파서에서 일원화하고, 가용성(라이브러리 설치 여부)에 따라 안전 폴백.
- 런타임 로깅으로 선택 파서 출력.

### 구현 스니펫

```python
# phase1/src/parsers/java_parser.py (parse_file 상단)
parser_cfg = (self.config.get('java', {}) or {}).get('parser_type', 'javalang').lower()

def _select_parser() -> str:
    if parser_cfg == 'tree-sitter' and self.tree_sitter_parser:
        return 'tree_sitter'
    if parser_cfg == 'javalang' and javalang is not None:
        return 'javalang'
    # 폴백: 사용 가능 항목 우선
    if self.tree_sitter_parser:
        return 'tree_sitter'
    if javalang is not None:
        return 'javalang'
    return 'none'

parser_used = _select_parser()
if parser_used == 'none':
    # 로깅 후 빈 결과 반환
    print('No available Java parser (javalang/tree-sitter)')
    return file_obj, [], [], []
```

```python
# 분기 사용 (기존 미정의 분기 교정)
if parser_used == 'javalang':
    tree = javalang.parse.parse(content)
    # ... 기존 javalang 추출 경로 ...
elif parser_used == 'tree_sitter':
    # self._extract_with_tree_sitter(tree, ...)
    # ... Tree-sitter 경로 ...
```

```yaml
# README.md 설정 예시 정합화
java:
  enabled: true
  parser_type: "javalang"   # 또는 "tree-sitter" (설치 필요)

python:
  enabled: true
  parser_type: "ast"
```

### 테스트 및 수용 기준

- `parser_type` 값을 바꿔 실행 시, 로그에 실제 선택 파서가 정확히 출력.
- 라이브러리 미설치 환경에서 안전 폴백 동작.

---

## 검증 계획(전반)

- 정확도 회귀: `PROJECT/sampleSrc` 기반 스냅샷 비교(조인/필터/엣지 카운트, 미해결 엣지 감소).
- 성능 회귀: 50+ 파일, 200+ 클래스 규모에서 처리 시간/메모리 현수준 유지.
- 보안 경고: `${}`/EL 기반 SQL 조합 시 SQLi 경고 유지, `#{}`는 경고 완화.
- Mermaid 렌더: GitHub/Live Editor에서 문서 렌더 정상.

---

## 리스크 및 완화

- include 순환 참조: refid 방문 캐시로 차단, 주석 대체.
- 분기 폭발: `max_branch` 제한, worst-case 요약.
- 세션 경합: scoped_session + begin 경계로 원자성/분리성 확보.
- 과다 단순화: `keep_edge_kinds`로 핵심 엣지 보존, dropped 목록 제공.

---

## 작업 순서 제안 및 일정(예)

1) 문서-구현 불일치 교정(단기) — 0.5일
2) 세션/트랜잭션 경계 정리 — 0.5일
3) Mermaid 단순화 개선 — 0.5일
4) MyBatis 동적 SQL 처리기 도입 — 1.5일
5) 통합 테스트/회귀/튜닝 — 1.0일

총 4.0일 (버퍼 제외), 기능 플래그로 점진 반영 가능.

---

## 수용 기준(Definition of Done)

- [TODO] 5건 모두에 대해 코드 구현+단위 테스트 또는 수기 검증 체크리스트 통과.
- 설정과 실행 결과(로그)의 일치 확인.
- 대용량/병렬 시나리오에서 오류·누수 미발생.
- Mermaid 출력의 가독성 향상 및 핵심 엣지 보존.

---

## 파일별 변경 요약(예정)

- `phase1/src/parsers/jsp_mybatis_parser.py`: DynamicSqlResolver 추가, MyBatis/JSP 처리 경로 통합 강화.
- `phase1/src/models/database.py`: DatabaseManager의 scoped_session 도입.
- `phase1/src/database/metadata_engine.py`: 저장 루틴 begin 경계 적용.
- `phase1/src/database/metadata_enhancement_engine.py`: 단계별 트랜잭션 경계 적용.
- `visualize/exporters/mermaid_exporter.py`: 단순화 전략/파라미터 확장, overflow 요약.
- `phase1/src/parsers/java_parser.py`, `README.md`: parser_type 정합화.

본 문서는 구현 가이드입니다. 실제 코드 반영 시 본 계획을 기준으로 커밋 단위를 작게 유지하고, 각 단계 종료마다 회귀 검증을 수행합니다.

