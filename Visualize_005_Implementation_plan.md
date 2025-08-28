# Source Analyzer 시각화 고도화 구현 기획 (Visualize_005)

**범위**: ERD/시퀀스/내보내기 기능 고도화 + Phase1 보강 포인트  
**대상 버전**: v1.1  
**작성일자**: 2025-08-29

## 목표 요약

- DB/SQL 강화: 컬럼 툴팁/코멘트/샘플 조인 페어, SQLERD 부분 ERD, 스키마 코멘트 표출
- 시퀀스 고도화: JSP→SQL→TABLE 흐름과 정적 call 체인 병합(미해소 콜 점선)
- 내보내기/데이터: 현재 서브그래프 JSON/CSV로 추출

---

## 1. DB/SQL 강화

### 1.1 컬럼 툴팁/코멘트/샘플 조인 페어

- 요구사항
  
  - ERD에서 테이블 노드 클릭 시 사이드 패널에 다음 표시
    - PK/FK 컬럼 구분 리스트, 컬럼 코멘트, 데이터 타입/NULL 허용
    - 샘플 조인 페어(해당 테이블이 다른 테이블과 조인된 상위 N개 페어, 빈도/신뢰도 포함)
  - 노드 hover 시 간단 툴팁: PK 컬럼 요약, 코멘트 요약(최대 100자)

- 데이터 모델/Phase1 보강
  
  - `DbTable`, `DbColumn`에 코멘트 보관 필요
    - 선택 1) 컬럼 추가: `DbTable.table_comment`, `DbColumn.column_comment`
    - 선택 2) 별도 테이블: `DbTableComment`, `DbColumnComment` (owner/table/column 키)
  - 권장: 간단성 위해 선택 1) 채택
  - Ingestion: `DB_SCHEMA/ALL_TAB_COMMENTS.csv`, `ALL_COL_COMMENTS.csv`에서 로드하여 업데이트

- 시각화 데이터 확장
  
  - `build_erd_json()`에서 각 테이블 노드 meta에 다음 필드 추가
    - `columns: [{ name, data_type, nullable, is_pk, comment }]`
    - `comment: string` (table comment)
    - `sample_joins: [{ other_table, l_col, r_col, frequency, confidence }]` 상위 5개

- UI/템플릿
  
  - `erd_view.html` 패널 렌더에 컬럼 그리드/조인 페어 섹션 추가
  - Hover 툴팁은 간단 텍스트로 표시, 클릭 시 상세 패널 오픈

- 코드 스니펫
  
  ```python
  # phase1/src/models/database.py (권장 변경)
  class DbTable(Base):
    __tablename__ = 'db_tables'
    table_id = Column(Integer, primary_key=True)
    owner = Column(String(128))
    table_name = Column(String(128), nullable=False)
    status = Column(String(50))
    table_comment = Column(Text)  # NEW
  ```

class DbColumn(Base):
    __tablename__ = 'db_columns'
    column_id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('db_tables.table_id'), nullable=False)
    column_name = Column(String(128), nullable=False)
    data_type = Column(String(128))
    nullable = Column(String(1))  # Y/N
    column_comment = Column(Text)  # NEW

```
```python
# phase1/src/core/db_schema_loader.py (신규/개선) - CSV 로딩 예시
import csv
from models.database import DbTable, DbColumn

def load_table_comments(session, path):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            owner = (row.get('OWNER') or '').upper()
            table = (row.get('TABLE_NAME') or '').upper()
            comment = row.get('COMMENTS')
            t = (session.query(DbTable)
                    .filter(DbTable.table_name == table,
                            (DbTable.owner == owner) | (owner == ''))
                    .first())
            if t:
                t.table_comment = comment
    session.commit()

def load_column_comments(session, path):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            owner = (row.get('OWNER') or '').upper()
            table = (row.get('TABLE_NAME') or '').upper()
            column = (row.get('COLUMN_NAME') or '').upper()
            comment = row.get('COMMENTS')
            q = (session.query(DbColumn)
                    .join(DbTable, DbColumn.table_id == DbTable.table_id)
                    .filter(DbTable.table_name == table,
                            (DbTable.owner == owner) | (owner == ''),
                            DbColumn.column_name == column))
            c = q.first()
            if c:
                c.column_comment = comment
    session.commit()
```

```python
# visualize/builders/erd.py (발췌) - meta 보강
pk_cols_map = { t.table_id: {pk.column_name for pk in pk_info if pk.table_id == t.table_id} }
columns = (
    db.session()
    .query(DbColumn)
    .all()
)
cols_by_table = {}
for c in columns:
    cols_by_table.setdefault(c.table_id, []).append({
        'name': c.column_name,
        'data_type': c.data_type,
        'nullable': c.nullable,
        'is_pk': c.column_name in pk_cols_map.get(c.table_id, set()),
        'comment': getattr(c, 'column_comment', None)
    })
# ... 테이블 루프 내에서
table_meta = {
    'owner': table.owner,
    'table_name': table.table_name,
    'status': getattr(table, 'status', 'VALID'),
    'pk_columns': list(pk_cols_map.get(table.table_id, set())),
    'comment': getattr(table, 'table_comment', None),  # NEW
    'columns': cols_by_table.get(table.table_id, [])   # NEW
}
# 샘플 조인 페어 상위 5개 계산 후 meta['sample_joins']에 추가
```

```html
<!-- visualize/templates/erd_view.html (발췌) - 패널 확장 -->
<div id="info-content"></div>
<script>
// ... 노드 클릭 핸들러 내
if (data.meta) {
  if (data.meta.comment) html += `<p><strong>Comment:</strong> ${data.meta.comment}</p>`;
  if (data.meta.columns?.length) {
    html += `<p><strong>Columns:</strong></p><table><tr><th>Name</th><th>Type</th><th>PK</th><th>Null</th><th>Comment</th></tr>`;
    data.meta.columns.slice(0, 50).forEach(col => {
      html += `<tr><td>${col.name}</td><td>${col.data_type||''}</td><td>${col.is_pk?'✓':''}</td><td>${col.nullable||''}</td><td>${col.comment||''}</td></tr>`;
    });
    html += `</table>`;
  }
  if (data.meta.sample_joins?.length) {
    html += `<p><strong>Sample Joins:</strong></p><ul>`;
    data.meta.sample_joins.forEach(j => {
      html += `<li>${j.other_table} (${j.l_col} = ${j.r_col}) · freq ${j.frequency} · conf ${Math.round(j.confidence*100)}%</li>`;
    });
    html += `</ul>`;
  }
}
</script>
```

### 1.2 SQLERD 추적 (부분 ERD)

- 요구사항
  
  - 특정 `sql_unit` 기준으로 “조인 대상 테이블 + 필수필터(RequiredFilter)”만 포함한 미니 ERD 생성
  - 기존 `--from-sql mapper_ns:stmt_id` 확장: 필수필터 목록을 사이드 패널에 표시, 해당 컬럼 하이라이트

- 구현 설계
  
  - `build_erd_json(project_id, from_sql=...)` 경로에서
    - `joins` 중 `sql_id == target_sql.sql_id`만 사용
    - `required_filters` 조회하여 meta에 `required_filters: [{table, column, op, value_repr}]` 추가
    - 노드 목록을 “언급된 테이블만”으로 필터
  - UI에서 필수필터 컬럼에 칩/하이라이트 스타일 적용

- 코드 스니펫
  
  ```python
  # visualize/builders/erd.py (발췌)
  filters = db.session().query(RequiredFilter).\
    join(SqlUnit).join(File).\
    filter(File.project_id==project_id, RequiredFilter.sql_id==target_sql.sql_id).all()
  ```

# 노드 meta에 필수필터 추가

filters_by_table = {}
for f in filters:
    filters_by_table.setdefault(f.table_name.upper(), []).append({
        'column': f.column_name.upper(), 'op': f.op, 'value': f.value_repr,
        'always': bool(f.always_applied)
    })

# 노드 생성 시

meta = nodes_dict[node_id]['meta']
meta['required_filters'] = filters_by_table.get(table_key_upper, [])

```
```css
/* visualize/templates/erd_view.html - 하이라이트 예시 */
node[type = "table"][data.has_required_filters = true] { border-color: #ef6c00; border-width: 3; }
```

---

## 2. 시퀀스 고도화 (하이브리드)

### 2.1 요구사항

- JSP→SQL→TABLE 기본 흐름과 정적 call 체인을 병합하여 하나의 시퀀스 그래프 생성
- 미해소 콜(`call_unresolved` 또는 힌트 수준)은 점선/회색으로 표현
- 시작점 미지정 시 기존 기본 흐름 유지, 지정 시 우선 call 체인 추적 후 SQL/TABLE까지 확장

### 2.2 설계

- 데이터 수집
  - `edges`: `call`, `call_unresolved`, `call_sql`, `use_table`
  - 시작 메서드/파일에서 BFS로 `call` 체인 추적
  - `call_sql`을 통해 SQL 유닛으로, 이어서 `use_table`로 테이블로 확장
- 병합 전략
  - 동일 노드 키(`{type}:{id}`) 기준 중복 제거, 레이어는 ‘최초 도달 깊이’ 사용
  - `call_unresolved`는 confidence 하향 및 스타일 dashed

### 2.3 코드 스니펫

```python
# visualize/builders/sequence_diagram.py (핵심 변경)
edges = db.fetch_edges(project_id, ['call','call_unresolved','call_sql','use_table'], 0.0)

# get_node_details 캐스팅 가드
node_type, raw_id = target_id.split(':', 1)
node_id = int(raw_id) if node_type in ('file','class','method','sql_unit') and raw_id.isdigit() else raw_id

# unresolved edge 스타일 플래그
edge_kind = edge_info['kind']
edge_meta = {'unresolved': edge_kind == 'call_unresolved'}
sequence_edges.append({
  'id': edge_id,
  'source': current_id,
  'target': target_id,
  'kind': edge_kind,
  'confidence': edge_info['confidence'],
  'meta': edge_meta,
  'sequence_order': len(sequence_edges),
  'depth': current_depth
})
```

```html
<!-- visualize/templates/graph_view.html - 스타일 추가 -->
{
  selector: 'edge[kind = "call_unresolved"]',
  style: { 'line-color': '#9e9e9e', 'target-arrow-color': '#9e9e9e', 'line-style': 'dashed' }
}
```

---

## 3. 내보내기/데이터 (JSON/CSV)

### 3.1 요구사항

- 현재 생성된 서브그래프를 JSON/CSV로 함께 저장
- CSV는 `nodes.csv`(id,label,type,group,...)와 `edges.csv`(id,source,target,kind,confidence,...) 2파일 출력

### 3.2 CLI 확장

- 모든 서브커맨드에 옵션 추가: `--export-json path`, `--export-csv-dir dir`

### 3.3 구현 스니펫

```python
# visualize/cli.py (발췌)

def add_common(sp):
    sp.add_argument('--project-id', type=int, required=True)
    sp.add_argument('--out', required=True)
    sp.add_argument('--min-confidence', type=float, default=0.5)
    sp.add_argument('--max-nodes', type=int, default=2000)
    sp.add_argument('--export-json')
    sp.add_argument('--export-csv-dir')

# ... 결과 생성 후
if args.export_json:
    with open(args.export_json, 'w', encoding='utf-8') as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)

if args.export_csv_dir:
    Path(args.export_csv_dir).mkdir(parents=True, exist_ok=True)
    _export_csv(args.export_csv_dir, data)
```

```python
# visualize/templates/render.py 또는 utils.py (신규)
import csv

def _export_csv(dir_path: str, data: dict):
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    with open(Path(dir_path)/'nodes.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id','label','type','group'])
        w.writeheader()
        for n in nodes:
            w.writerow({k: n.get(k) for k in ['id','label','type','group']})
    with open(Path(dir_path)/'edges.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id','source','target','kind','confidence'])
        w.writeheader()
        for e in edges:
            w.writerow({k: e.get(k) for k in ['id','source','target','kind','confidence']})
```

---

## 4. Phase1 개선 제안 (시각화 품질 직결)

- 스키마 코멘트 적재
  - 위 1.1의 `table_comment/column_comment` 반영 및 CSV 로더 추가
- 조인/테이블 정규화 강화
  - OWNER/TABLE/컬럼명 대문자 정규화 일관성 확보, alias 해소 로직 보완
- RequiredFilter 충실화
  - 상수/바인딩 구분, `always_applied` 판단 기준 명확화 → ERD 필터 표시에 신뢰도 제공
- Call 해소 파이프라인 정리
  - 미해결 콜은 `edges`가 아닌 `edge_hints`로 유지 또는 별도 `edges_unresolved` 테이블 사용
  - 대안: `Edge.dst_id` nullable로 전환(+뷰어에서 점선 처리) → 마이그레이션 필요
- 인덱스/성능
  - `edges(src_type,src_id)`, `(dst_type,dst_id)`, `joins(sql_id)` 등 인덱스 재점검
  - `fetch_edges` 쿼리 단순화: 프로젝트 소속 ID 집합 사전 계산 후 필터

예시(미해결 엣지 유지):

```python
# phase1/src/database/metadata_enhancement_engine.py (발췌)
if not target_method:
    # 힌트 보강(재시도용)으로 전환, edges 미삽입
    hint.confidence = max(0.1, hint.confidence - 0.1)
    continue
```

---

## 5. 검증 계획

- 유닛: ERD 빌더 컬럼/코멘트/필터 필드 포함 여부, 샘플 조인 페어 계산 검증
- 통합: `--from-sql` 부분 ERD 생성 및 필터 하이라이트 확인
- 시퀀스: 시작 메서드 지정 시 call+SQL+TABLE 병합 결과 노드/엣지 개수, 점선 스타일 확인
- 내보내기: JSON/CSV 파일 유효성, 엣지/노드 수 일치
- 오프라인: 로컬 자산 사용 로드 확인

---

## 6. 마일스톤/우선순위

- M1: ERD 컬럼/코멘트/샘플 조인(백엔드/뷰) + SQLERD 필수필터 노출
- M2: 하이브리드 시퀀스 병합 + call_unresolved 스타일
- M3: 내보내기(JSON/CSV) + CLI 옵션
- M4: Phase1 보강(코멘트 적재/정규화/힌트 파이프라인) 반영

## 7. 리스크/대응

- DB 마이그레이션: `DbTable/DbColumn` 컬럼 추가 시 마이그레이션 스크립트 필요 → dev는 자동 생성, prod는 DDL 사전 합의
- 대규모 ERD 성능: 컬럼 리스트가 많을 때 패널 렌더 성능 저하 → 상위 50개 제한/지연 렌더
- CSV/JSON 내보내기 경로 권한/쓰기 실패 → CLI 에러 처리/가이드 메시지 강화

---

본 기획안은 현 구현 구조를 유지하면서 사용자 가치가 높은 3개 축을 최소 침습으로 확장하는 것을 목표로 한다. Phase1 데이터 충실화와 가벼운 마이그레이션을 병행하면 시각화 정확도/설명력/활용성이 크게 향상될 것으로 예상한다.

---

## 8. 오프라인/CDN 의존성 제거

- 문제점
  
  - 뷰어(HTML 템플릿)에서 Cytoscape.js, Dagre.js를 unpkg 등 외부 CDN에서 로드 → 오프라인/폐쇄망 환경에서 로딩 실패로 시각화 불가.

- 권장 사항/작업
  
  - 라이브러리 로컬 번들링: `visualize/static/vendor/` 아래에 다음 파일을 포함
    - `vendor/cytoscape/cytoscape.umd.min.js`
    - `vendor/dagre/dagre.min.js` (또는 `cytoscape-dagre.js` 사용 시 해당 플러그인 파일 포함)
  - 템플릿 스크립트 경로를 로컬로 교체
    - Flask/Jinja 사용 시: `{{ url_for('static', filename='vendor/cytoscape/cytoscape.umd.min.js') }}`
    - 정적 파일 직접 서빙 시: 상대경로 `./static/vendor/cytoscape/cytoscape.umd.min.js`
  - 패키징/배포 산출물에 `visualize/static/vendor/**` 포함

- 템플릿 수정 예시
  
  ```html
  <!-- Before -->
  <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.umd.min.js"></script>
  <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
  ```

<!-- After (Flask/Jinja) -->

<script src="{{ url_for('static', filename='vendor/cytoscape/cytoscape.umd.min.js') }}"></script>

<script src="{{ url_for('static', filename='vendor/dagre/dagre.min.js') }}"></script>

<!-- After (정적 HTML) -->

<script src="./static/vendor/cytoscape/cytoscape.umd.min.js"></script>

<script src="./static/vendor/dagre/dagre.min.js"></script>

```
- 검증
  - 인터넷 차단 환경에서 ERD/시퀀스/그래프 뷰 정상 로드 확인
  - 네트워크 탭에 외부 CDN 요청이 없는지 확인

---

## 9. CLI 에러/로그 처리 개선

- 문제점
  - `visualize/cli.py`가 `print` 중심으로 동작하고, 예외/실패 시 표준 에러 스트림, 반환 코드, 일관된 로깅 체계가 부족.

- 권장 사항
  - 공통 옵션 추가: `--verbose`(중복 지정으로 단계 상승), `--quiet`, `--log-file PATH`
  - 로깅 초기화 유틸 추가: 콘솔(레벨 가변) + 파일 핸들러 구성, 포맷 통일
  - 예외 처리 가이드: 사용자 액션 힌트 포함하여 stderr로 출력, 종료 코드 표준화

- 구현 스니펫
```python
# visualize/cli.py (추가/개선)
import sys, logging

def add_common(sp):
    sp.add_argument('--project-id', type=int, required=True)
    sp.add_argument('--out', required=True)
    sp.add_argument('--min-confidence', type=float, default=0.5)
    sp.add_argument('--max-nodes', type=int, default=2000)
    sp.add_argument('--export-json')
    sp.add_argument('--export-csv-dir')
    sp.add_argument('-v', '--verbose', action='count', default=0,
                    help='-v: INFO, -vv: DEBUG')
    sp.add_argument('-q', '--quiet', action='store_true', help='경고 이상만 출력')
    sp.add_argument('--log-file', help='로그 파일 경로')

def setup_logging(args):
    level = logging.WARNING if args.quiet else (logging.DEBUG if args.verbose >= 2 else logging.INFO if args.verbose == 1 else logging.WARNING)
    handlers = [logging.StreamHandler(sys.stderr)]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding='utf-8'))
    logging.basicConfig(level=level,
                        handlers=handlers,
                        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                        datefmt='%H:%M:%S')
    return logging.getLogger('visualize.cli')

def main():
    parser = build_parser()
    try:
        args = parser.parse_args()
        logger = setup_logging(args)
        return dispatch(args, logger)
    except KeyboardInterrupt:
        print('Interrupted by user', file=sys.stderr)
        return 130
    except SystemExit as e:
        # argparse가 사용법 에러로 호출한 경우
        return e.code if isinstance(e.code, int) else 2
    except FileNotFoundError as e:
        print(f"ERROR: 파일을 찾을 수 없습니다: {e}", file=sys.stderr)
        print("확인: 경로/권한/--project-id 인자", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: 실행 중 예기치 않은 오류: {e}", file=sys.stderr)
        print("확인: 입력 인자, 데이터 준비 상태, --verbose 로 상세 로그", file=sys.stderr)
        return 1
```

- 반환 코드 표준화
  
  - 0: 정상, 1: 일반 오류(처리 중 예외), 2: 인자/사용법 오류, 130: 사용자 인터럽트

- 검증
  
  - 실패 시 stderr 출력/반환 코드 확인, `--log-file`에 기록되는지 확인
  - `-v/-vv/-q` 별 로그 레벨 동작 확인





## ※ 추가 검토 필요

  🔴 치명적 이슈 (우선 해결 필요)

1. DB 스키마 불일치: Edge.dst_id가 nullable=False인데 미해결 콜을 dst_id=None으로 저장하려 함

2. 타입 캐스팅 버그: 시퀀스 빌더에서 테이블 노드에 대해 부적절한 int() 캐스팅 수행

3. 테이블 메타정보 처리 오류: get_node_details('table', ...)가 테이블 ID를 이름으로 잘못 처리
   
   
   
   🟡 중요 개선사항

4. 오프라인 의존성: CDN 기반 라이브러리 로딩으로 폐쇄망에서 동작 불가

5. 성능 최적화: 복잡한 조인 쿼리로 인한 대규모 프로젝트에서의 성능 저하

6. CLI 품질: 에러 처리, 로깅, 반환 코드 개선 필요
   
   
   
   💡 추가 가치 기능

7. ERD 고도화: 컬럼 상세 정보, 코멘트, 샘플 조인 표시

8. 시퀀스 통합: JSP→SQL→TABLE 흐름과 정적 call 체인 병합

9. 데이터 내보내기: JSON/CSV 형식으로 분석 결과 저장
   
   
   
   더 좋은 아이디어들:
   
   🚀 혁신적 개선안

10. 적응형 시각화: 데이터 복잡도에 따른 자동 레이아웃 선택 및 성능 최적화

11. 인터랙티브 필터링: 실시간 신뢰도/깊이 조절로 동적 그래프 탐색

12. 코드 컨텍스트 연결: 노드 클릭 시 실제 소스코드 위치로 직접 연결

13. 메모리 기반 캐싱: 세션별 분석 결과 캐싱으로 반복 탐색 가속화
