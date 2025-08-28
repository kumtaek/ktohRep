# Source Analyzer 시각화 고도화 구현 완료 (Visualize_006)

**구현 버전**: v1.1  
**구현 완료일**: 2025-08-28  
**기반 문서**: Visualize_004_Implementation_review.md, Visualize_005_Implementation_plan.md

---

## 구현 요약

Visualize_004에서 식별된 치명적 이슈와 Visualize_005에서 계획한 고도화 기능을 모두 구현하였습니다. 이번 구현으로 시각화 시스템의 안정성과 사용성이 대폭 향상되었습니다.

### 🔴 치명적 이슈 해결 (100% 완료)
- DB 스키마 불일치 수정
- 시퀀스 빌더 타입 캐스팅 버그 수정  
- 테이블 메타정보 처리 오류 수정

### 🟡 중요 개선사항 (100% 완료)
- 오프라인 CDN 의존성 제거
- CLI 에러 처리 및 로깅 개선

### 💡 추가 가치 기능 (100% 완료)
- ERD 컬럼 상세정보 및 샘플 조인 표시
- 하이브리드 시퀀스 다이어그램
- JSON/CSV 내보내기

---

## 상세 구현 내역

### 1. 치명적 이슈 해결

#### 1.1 DB 스키마 불일치 해결
**문제**: Edge 모델의 dst_id가 nullable=False인데, 미해결 콜을 dst_id=None으로 저장하려 함

**해결책**:
```python
# phase1/src/models/database.py
class Edge(Base):
    # 변경 전: dst_id = Column(Integer, nullable=False)  
    dst_id = Column(Integer, nullable=True)  # Allow NULL for unresolved edges
```

**사유**: 미해결 엣지를 별도 테이블로 분리하는 것보다, NULL을 허용하여 단일 테이블에서 관리하는 것이 쿼리 성능과 유지보수에 유리함.

#### 1.2 시퀀스 빌더 타입 캐스팅 버그 수정
**문제**: 테이블 노드에 대해 부적절한 int() 캐스팅 수행

**해결책**:
```python
# visualize/builders/sequence_diagram.py
# 변경 전: target_details = db.get_node_details(node_type, int(node_id))
# 변경 후:
node_type, raw_id = target_id.split(':', 1)
try:
    node_id = int(raw_id) if node_type in ('file', 'class', 'method', 'sql_unit') and raw_id.isdigit() else raw_id
except ValueError:
    node_id = raw_id
target_details = db.get_node_details(node_type, node_id)
```

**사유**: 테이블 노드의 ID가 문자열일 수 있으므로, 노드 타입에 따른 안전한 캐스팅 로직 적용.

#### 1.3 테이블 메타정보 처리 수정
**문제**: get_node_details('table', ...)가 테이블 ID를 이름으로 잘못 처리

**해결책**:
```python
# visualize/data_access.py
elif node_type == 'table':
    if isinstance(node_id, int):
        # Lookup by table_id
        table = session.query(DbTable).filter(DbTable.table_id == node_id).first()
    else:
        # Lookup by table name (fallback)
        table = session.query(DbTable).filter(DbTable.table_name.ilike(f'%{node_id}%')).first()
```

**사유**: 테이블 참조가 ID 기반인지 이름 기반인지에 따른 적절한 조회 로직 구분.

### 2. DB 테이블/컬럼 코멘트 지원

#### 2.1 모델 확장
```python
# phase1/src/models/database.py
class DbTable(Base):
    # ... 기존 필드들
    table_comment = Column(Text)  # 추가

class DbColumn(Base):
    # ... 기존 필드들  
    column_comment = Column(Text)  # 추가
```

#### 2.2 코멘트 로더 구현
```python
# phase1/src/core/db_comment_loader.py - 신규 파일
class DbCommentLoader:
    def load_table_comments(self, csv_path: str) -> Dict[str, int]
    def load_column_comments(self, csv_path: str) -> Dict[str, int]
    def load_comments_from_directory(self, data_dir: str) -> Dict[str, Dict[str, int]]
```

**사유**: CSV 파일(ALL_TAB_COMMENTS.csv, ALL_COL_COMMENTS.csv)에서 Oracle 스키마 코멘트를 자동으로 로드할 수 있는 유틸리티 제공.

### 3. 오프라인 CDN 자산 구현

#### 3.1 자산 다운로드 스크립트
```python
# visualize/static/vendor/download_assets.py - 신규 파일
class AssetDownloader:
    def download_cytoscape_assets(self) -> List[Dict[str, str]]
```

다운로드된 자산:
- cytoscape@3.23.0 (360KB)
- cytoscape-dagre@2.4.0 (12KB)  
- dagre@0.8.5 (284KB)

#### 3.2 템플릿 수정
```html
<!-- 변경 전: CDN 링크 -->
<script src="https://unpkg.com/cytoscape@3.23.0/dist/cytoscape.min.js"></script>

<!-- 변경 후: 로컬 자산 -->
<script src="./static/vendor/cytoscape/cytoscape.min.js"></script>
```

**적용 파일**: cyto_base.html, erd_view.html, graph_view.html

**사유**: 폐쇄망/오프라인 환경에서도 시각화가 정상 동작하도록 보장.

### 4. CLI 에러 처리 및 로깅 개선

#### 4.1 로깅 시스템 추가
```python
# visualize/cli.py
def setup_logging(args) -> logging.Logger:
    # 레벨별 로깅: -q (WARNING), 기본 (WARNING), -v (INFO), -vv (DEBUG)
    # 파일 로깅: --log-file 옵션
```

#### 4.2 에러 처리 강화
```python
def main():
    try:
        # 주요 로직
    except KeyboardInterrupt:
        return 130
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1
```

#### 4.3 JSON/CSV 내보내기 기능
```bash
# 사용 예시
python -m visualize erd --project-id 1 --out result.html \
    --export-json data.json \
    --export-csv-dir ./csv_output/
```

**출력**: nodes.csv, edges.csv 파일 생성

**사유**: 분석 결과를 다른 도구에서 재사용할 수 있도록 표준 형식으로 내보내기 지원.

### 5. ERD 컬럼 상세정보 및 샘플 조인

#### 5.1 데이터 조회 강화
```python
# visualize/data_access.py
def fetch_columns(self) -> List[DbColumn]
def fetch_sample_joins_for_table(self, table_id: int, limit: int = 5) -> List[Dict[str, Any]]
```

#### 5.2 ERD 메타데이터 확장
```python
# visualize/builders/erd.py
table_meta = {
    'owner': table.owner,
    'table_name': table.table_name, 
    'comment': getattr(table, 'table_comment', None),  # 추가
    'columns': table_columns,  # 추가
    'sample_joins': sample_joins  # 추가
}
```

#### 5.3 UI 개선
테이블 노드 클릭 시 표시되는 정보:
- 테이블 코멘트
- 컬럼 상세 정보 (이름, 타입, PK 여부, NULL 허용, 코멘트)
- 샘플 조인 패턴 (빈도, 신뢰도 포함)

**사유**: 데이터베이스 스키마에 대한 이해도를 높이고, 실제 조인 패턴을 통해 FK 관계를 추론할 수 있도록 지원.

### 6. 하이브리드 시퀀스 다이어그램

#### 6.1 엣지 타입 확장
```python
# visualize/builders/sequence_diagram.py
edges = db.fetch_edges(project_id, ['call', 'call_unresolved', 'use_table', 'call_sql'], 0.0)
```

#### 6.2 미해결 엣지 스타일링
```python
sequence_edges.append({
    'id': edge_id,
    'source': current_id,
    'target': target_id,
    'kind': edge_info['kind'],
    'meta': {
        'unresolved': is_unresolved,
        'style': 'dashed' if is_unresolved else 'solid'
    }
})
```

#### 6.3 CSS 스타일 추가
```css
/* graph_view.html */
edge[kind = "call_unresolved"] {
    line-color: #9e9e9e;
    target-arrow-color: #9e9e9e;
    line-style: dashed;
    opacity: 0.7;
}
```

**사유**: 정적 분석으로 해결되지 않은 메서드 호출도 시각적으로 구분하여 표시함으로써 코드 흐름의 완전성을 높임.

---

## 성능 및 품질 개선

### 성능 최적화
1. **쿼리 최적화**: 컬럼 조회 시 테이블별 그룹핑으로 N+1 문제 방지
2. **메모리 효율**: 샘플 조인은 상위 5개로 제한하여 메모리 사용량 제어
3. **렌더링 최적화**: 컬럼 표시는 최대 50개로 제한

### 사용성 개선  
1. **에러 메시지**: 구체적인 해결 방법 포함된 친화적 에러 메시지
2. **로깅**: 단계별 진행상황과 상세 디버깅 정보 제공
3. **오프라인 지원**: 네트워크 없이도 완전한 시각화 기능 제공

---

## 검증 및 테스트

### 기능 검증
- [✅] 치명적 이슈: dst_id=NULL 엣지 삽입 시 오류 없음 확인
- [✅] 타입 캐스팅: 테이블 노드에 대한 안전한 처리 확인  
- [✅] 오프라인: 인터넷 차단 상태에서 정상 로딩 확인
- [✅] 로깅: -v/-vv/-q 옵션별 적절한 로그 레벨 출력 확인
- [✅] Export: JSON/CSV 파일 정상 생성 및 내용 검증

### 회귀 테스트
기존 기능들이 모두 정상 동작함을 확인:
- ERD 생성 및 FK 관계 추론
- 의존성 그래프 생성
- 컴포넌트 다이어그램
- 시퀀스 다이어그램

---

## 마이그레이션 가이드

### 데이터베이스 마이그레이션
기존 데이터베이스를 사용하는 경우 다음 DDL 실행 필요:

```sql
-- SQLite
ALTER TABLE db_tables ADD COLUMN table_comment TEXT;
ALTER TABLE db_columns ADD COLUMN column_comment TEXT;
ALTER TABLE edges MODIFY dst_id INTEGER NULL;

-- Oracle  
ALTER TABLE db_tables ADD (table_comment CLOB);
ALTER TABLE db_columns ADD (column_comment CLOB);
ALTER TABLE edges MODIFY (dst_id NUMBER NULL);
```

### 코멘트 데이터 로딩
```python
from phase1.src.core.db_comment_loader import DbCommentLoader

loader = DbCommentLoader(session)
results = loader.load_comments_from_directory('./data/')
print(f"Loaded {results['table_comments']['loaded']} table comments")
print(f"Loaded {results['column_comments']['loaded']} column comments")
```

### 오프라인 자산 준비
```bash
cd visualize/static/vendor
python download_assets.py
```

---

## 향후 개발 방향

### 단기 개선 사항
1. **성능 모니터링**: 대규모 프로젝트(1000+ 테이블)에서의 성능 측정 및 최적화
2. **UI/UX**: 컬럼 테이블의 정렬, 필터링 기능 추가
3. **접근성**: 키보드 네비게이션 및 스크린 리더 지원 강화

### 장기 발전 방향
1. **실시간 업데이트**: 소스코드 변경 감지 및 실시간 시각화 갱신
2. **협업 기능**: 다중 사용자 환경에서의 분석 결과 공유
3. **AI 통합**: LLM 기반 코드 설명 및 리팩토링 제안

---

## 결론

Visualize_006 구현을 통해 Source Analyzer의 시각화 시스템이 안정적이고 실용적인 수준으로 발전했습니다. 

**주요 성과**:
- ✅ 9개 중요 이슈 100% 해결 완료
- ✅ 오프라인 환경 지원으로 운영 안정성 확보  
- ✅ 풍부한 메타데이터 제공으로 분석 효율성 향상
- ✅ 표준 형식 내보내기로 확장성 확보

이제 실제 프로젝트에서 신뢰성 있게 사용할 수 있는 시각화 도구로 거듭났으며, 향후 더욱 발전된 분석 기능의 토대가 마련되었습니다.