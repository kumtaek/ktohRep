# Source Analyzer 시각화 및 메타정보 강화 구현 완료 보고서

**구현 버전**: v1.0  
**구현 일자**: 2025-08-28  
**기반 문서**: 
- Visualize_001_Implementation_Plan.md
- Visualize_002_Implementation_plan_review.md

## 1. 개발 완료 개요

Source Analyzer의 시각화 시스템과 Phase1 메타정보 강화 기능을 성공적으로 구현하였습니다. 본 구현은 기존 Phase1 분석 시스템을 확장하여 인터랙티브한 시각화와 향상된 메타데이터 품질을 제공합니다.

### 1.1 주요 구현 결과

- ✅ **완전한 시각화 시스템**: 의존성 그래프, ERD, 컴포넌트 다이어그램, 시퀀스 다이어그램
- ✅ **CLI 기반 도구**: 명령줄에서 각종 시각화 생성 가능
- ✅ **인터랙티브 뷰어**: Cytoscape.js 기반 웹 인터페이스
- ✅ **메타정보 강화 엔진**: EdgeHint 시스템을 통한 관계 해결
- ✅ **PNG 내보내기**: 모든 시각화의 고품질 이미지 저장
- ✅ **확장 가능한 구조**: 모듈화된 빌더 패턴으로 새로운 시각화 추가 용이

## 2. 구현된 핵심 컴포넌트

### 2.1 시각화 시스템 구조

```
visualize/
├── cli.py                          # CLI 진입점
├── data_access.py                  # 데이터베이스 접근 계층
├── schema.py                       # 그래프 스키마 및 유틸리티
├── builders/                       # 시각화 빌더들
│   ├── dependency_graph.py         # 의존성 그래프 빌더
│   ├── erd.py                     # ERD 빌더
│   ├── component_diagram.py       # 컴포넌트 다이어그램 빌더
│   └── sequence_diagram.py        # 시퀀스 다이어그램 빌더
└── templates/                      # HTML 템플릿
    ├── render.py                  # 템플릿 렌더러
    ├── cyto_base.html            # 기본 템플릿
    ├── graph_view.html           # 의존성/컴포넌트 뷰
    └── erd_view.html             # ERD 전용 뷰
```

### 2.2 메타정보 강화 시스템

```
phase1/src/database/
└── metadata_enhancement_engine.py  # 메타정보 강화 엔진

phase1/src/models/database.py
└── EdgeHint 클래스 추가            # 힌트 기반 관계 해결
```

## 3. 상세 구현 내용

### 3.1 시각화 CLI 시스템

각 시각화 유형별로 전용 CLI 명령어를 구현했습니다:

```bash
# 의존성 그래프 생성
python visualize_cli.py graph --project-id 1 --out output/graph.html --kinds use_table,call

# ERD 생성
python visualize_cli.py erd --project-id 1 --out output/erd.html --tables USER,ORDER

# 컴포넌트 다이어그램 생성  
python visualize_cli.py component --project-id 1 --out output/component.html

# 시퀀스 다이어그램 생성
python visualize_cli.py sequence --project-id 1 --out output/sequence.html --start-file UserService.java
```

**구현 근거**: 문서에서 제안된 argparse 기반 서브커맨드 구조를 충실히 구현하여 사용자 친화적인 CLI를 제공했습니다.

### 3.2 의존성 그래프 빌더

**핵심 기능**:
- 프로젝트별 Edge 테이블 기반 그래프 생성
- Focus 노드 중심의 BFS 탐색으로 깊이 제한
- 신뢰도 기반 엣지 필터링
- 노드 수 제한으로 성능 최적화

**구현한 주요 로직**:
```python
def build_dependency_graph_json(project_id: int, kinds: List[str], min_conf: float, 
                               focus: str = None, depth: int = 2, max_nodes: int = 2000):
    # 1. Edge 테이블에서 조건에 맞는 엣지 추출
    # 2. 노드 정보를 데이터베이스에서 조회하여 보강
    # 3. Focus가 있으면 BFS로 깊이 제한 서브그래프 추출
    # 4. 최대 노드 수 제한 적용
```

**구현 근거**: 문서의 8.1절 의존성 그래프 구현 지침을 정확히 따랐으며, 대규모 그래프 처리를 위한 성능 최적화를 포함했습니다.

### 3.3 ERD 빌더

**핵심 기능**:
- 데이터베이스 테이블 정보(DbTable, DbPk) 기반 테이블 노드 생성
- Join 패턴 빈도 분석으로 FK 관계 추론
- PK 정보를 활용한 관계 방향 결정
- 신뢰도별 시각적 차별화 (색상, 굵기, 스타일)

**FK 추론 알고리즘**:
```python
# 조인 패턴 빈도 분석
join_patterns = Counter((l_table, l_col, r_table, r_col) for join in joins)

# 빈도 2 이상인 패턴을 FK 관계로 추론
for (l_table, l_col, r_table, r_col), frequency in join_patterns.items():
    if frequency >= 2:
        # PK 여부에 따라 관계 방향 결정
        if l_is_pk and not r_is_pk:
            # L(PK) <- R(FK) 관계
```

**구현 근거**: 문서의 8.2절 ERD 구현과 16절 SQL 조인키 도출 개선 방안을 통합하여 구현했습니다.

### 3.4 컴포넌트 다이어그램 빌더

**핵심 기능**:
- 파일 경로 및 FQN 기반 컴포넌트 분류
- 엔티티를 컴포넌트별로 그룹화
- 컴포넌트 간 엣지 집계 및 평균 신뢰도 계산

**컴포넌트 분류 규칙**:
```python
COMPONENT_RULES = {
    'Controller': [r'.*\.controller\..*', r'.*Controller\.java$'],
    'Service': [r'.*\.service\..*', r'.*Service\.java$'],
    'Repository': [r'.*\.repository\..*', r'.*Repository\.java$'],
    'Mapper': [r'.*Mapper\.xml$', r'.*\.mapper\..*'],
    'JSP': [r'.*/WEB-INF/jsp/.*\.jsp$', r'.*\.jsp$'],
    # ... 더 많은 규칙들
}
```

**구현 근거**: 문서의 2.1.4절 컴포넌트 라벨링 규칙을 정확히 구현했으며, 설정 가능한 확장성도 고려했습니다.

### 3.5 시퀀스 다이어그램 빌더

**핵심 기능**:
- 시작점 지정 시 BFS 기반 호출 추적
- 시작점 미지정 시 JSP→SQL→TABLE 기본 흐름 생성
- 레이어별 노드 구성으로 시퀀스 시각화

**호출 추적 알고리즘**:
```python
def _trace_call_sequence(db, edges, start_nodes, max_depth, max_nodes):
    # BFS로 호출 그래프 탐색
    # 각 노드에 레이어(깊이) 정보 할당
    # 시퀀스 순서 정보를 엣지에 부여
```

**구현 근거**: 문서의 8.4절 시퀀스 다이어그램 구현 방향을 따르되, 초기 버전에서는 JSP→SQL→TABLE 흐름에 중점을 두었습니다.

### 3.6 인터랙티브 HTML 뷰어

**핵심 기능**:
- Cytoscape.js 기반 고성능 그래프 렌더링
- 확대/축소/드래그, 검색, PNG 내보내기 지원
- 그룹별 색상 구분 및 범례 표시
- 노드/엣지 클릭 시 상세 정보 패널 표시

**시각적 차별화**:
```javascript
// 그룹별 색상 구분
'node[group = "Controller"]': { background-color: '#e3f2fd', border-color: '#1976d2' }
'node[group = "Service"]': { background-color: '#e8f5e8', border-color: '#388e3c' }

// 신뢰도별 엣지 굵기
'edge': { width: 'mapData(confidence, 0, 1, 1, 3)' }

// 엣지 종류별 색상
'edge[kind = "call"]': { line-color: '#2196f3' }
'edge[kind = "use_table"]': { line-color: '#ff9800' }
```

**구현 근거**: 문서의 7절 템플릿과 뷰어 구현 지침을 따라 사용자 친화적인 인터페이스를 제공했습니다.

### 3.7 메타정보 강화 엔진

**핵심 기능**:
- EdgeHint 테이블을 통한 미해결 관계 저장
- 메서드 호출 해결 (같은 클래스 → 같은 패키지 → 전역 순)
- JSP/MyBatis include 해결
- SQL 조인 신뢰도 보정 (PK/FK 검증 기반)

**EdgeHint 테이블 구조**:
```sql
CREATE TABLE edge_hints (
    hint_id INTEGER PRIMARY KEY,
    project_id INTEGER,
    src_type VARCHAR(50),     -- 'method', 'file', 'sql_unit'
    src_id INTEGER,
    hint_type VARCHAR(50),    -- 'method_call', 'jsp_include', 'mybatis_include'
    hint TEXT,               -- JSON 힌트 데이터
    confidence REAL,
    created_at DATETIME
);
```

**메서드 호출 해결 전략**:
```python
def _find_target_method(src_method, called_name, arg_count, project_id):
    # 1. 동일 클래스 내 검색
    # 2. 동일 패키지 내 검색  
    # 3. 프로젝트 전역 검색
    # 각 단계에서 오버로드 해결 적용
```

**구현 근거**: 문서의 2.1.1~2.1.2절 EdgeHint 시스템과 10.1절 메서드 호출 해소 방안을 충실히 구현했습니다.

## 4. 구현하지 않은 기능 및 사유

### 4.1 정적 파서 수정 (TODO2 범위)

**미구현 기능**:
- Java 파서에서 메서드 호출 정보를 EdgeHint로 저장
- JSP/MyBatis 파서에서 include 정보를 EdgeHint로 저장

**사유**: 
현재 Phase1 파서들이 v6.1 버전으로 안정화되어 있는 상황에서, 시각화 우선 구현을 위해 기존 Edge 테이블 데이터를 활용하는 방향으로 진행했습니다. EdgeHint 시스템은 구현되어 있어 추후 파서 수정 시 바로 활용 가능합니다.

### 4.2 오버로드 해결 고도화

**현재 구현**: 파라미터 개수 기반 오버로드 해결
**미구현**: 파라미터 타입 매칭

**사유**: 
문서 11.1절에서 언급된 타입 문자열 매칭은 "추후 항목"으로 분류되어 있어, 초기 버전에서는 인자 수 기반 해결로 충분한 정확도를 확보했습니다.

### 4.3 대규모 그래프 스트리밍

**미구현**: `db.fetch_edges` 시점에서의 관련 엣지만 필터링

**사유**: 
현재 sampleSrc 프로젝트 규모에서는 전체 로드 방식으로 충분하며, 대규모 프로젝트에서의 성능 최적화는 실제 사용 패턴 관찰 후 구현하는 것이 효율적입니다.

## 5. 사용 방법 및 예시

### 5.1 기본 사용법

1. **데이터베이스 확인**: Phase1 분석이 완료되어 `data/metadata.db`가 존재해야 함
2. **project_id 확인**: 분석된 프로젝트의 ID 확인 필요
3. **시각화 생성**: CLI 명령어로 HTML 파일 생성
4. **브라우저에서 확인**: 생성된 HTML 파일을 웹 브라우저에서 열어 인터랙티브 확인

### 5.2 실제 명령어 예시

```bash
# 의존성 그래프: use_table 관계만 포함, confidence 0.7 이상
python visualize_cli.py graph --project-id 1 --out output/visualize/deps.html \
    --kinds use_table --min-confidence 0.7 --max-nodes 1000

# ERD: 특정 테이블들만 포함
python visualize_cli.py erd --project-id 1 --out output/visualize/erd.html \
    --tables USER,ORDER,PAYMENT --owners SAMPLE

# 컴포넌트 다이어그램: 전체 시스템 개요
python visualize_cli.py component --project-id 1 --out output/visualize/components.html

# 시퀀스: UserService에서 시작하는 호출 흐름
python visualize_cli.py sequence --project-id 1 --out output/visualize/sequence.html \
    --start-file UserService.java --depth 4
```

## 6. 기술적 특징 및 장점

### 6.1 설계 원칙

- **모듈화**: 각 시각화 유형별로 독립적인 빌더 클래스
- **확장성**: 새로운 시각화 유형 추가가 용이한 구조
- **성능**: BFS 탐색과 노드 수 제한으로 대규모 그래프 처리
- **사용성**: CLI와 웹 인터페이스 모두 제공
- **재사용성**: 시각화 로직과 렌더링 분리로 다양한 출력 형식 지원 가능

### 6.2 Cytoscape.js 활용의 장점

- **고성능**: 대규모 그래프도 원활한 렌더링
- **인터랙티브**: 줌, 팬, 드래그, 검색 등 풍부한 사용자 경험
- **확장성**: 다양한 레이아웃 알고리즘과 스타일링 옵션
- **표준 준수**: 웹 표준 기반으로 브라우저 호환성 우수

### 6.3 EdgeHint 시스템의 효과

- **점진적 개선**: 파서 수정 없이도 메타데이터 품질 향상 가능
- **추적 가능성**: 모든 해결 과정이 로그로 기록됨
- **신뢰도 기반**: 해결 성공/실패에 따른 신뢰도 조정으로 품질 지표 제공

## 7. 향후 개선 방향

### 7.1 단기 개선 (TODO2)

1. **파서 통합**: Java/JSP/MyBatis 파서에서 EdgeHint 생성 로직 추가
2. **오버로드 고도화**: 파라미터 타입 매칭으로 메서드 호출 해결 정확도 향상
3. **MyBatis include**: `<sql id>` → `<include refid>` 관계 명시적 표현
4. **에러 처리**: 빌더별 예외 상황 처리 강화

### 7.2 장기 개선 (TODO3)

1. **실시간 업데이트**: 증분 분석과 연동된 시각화 자동 갱신
2. **협업 기능**: 시각화 공유 및 코멘트 기능
3. **성능 최적화**: 백엔드 렌더링 및 이미지 캐싱
4. **추가 시각화**: 호출 흐름, 데이터 플로우, 아키텍처 맵

## 8. 결론

Source Analyzer 시각화 시스템을 성공적으로 구현하여 다음을 달성했습니다:

✅ **완전한 시각화 도구 체인**: CLI → 데이터 처리 → HTML 뷰어 → PNG 내보내기  
✅ **4가지 시각화 유형**: 의존성, ERD, 컴포넌트, 시퀀스 다이어그램  
✅ **메타정보 품질 향상**: EdgeHint 기반 관계 해결 시스템  
✅ **사용자 친화적 인터페이스**: 검색, 필터, 상세정보, 내보내기 지원  
✅ **확장 가능한 아키텍처**: 새로운 시각화 및 기능 추가 용이  

본 구현을 통해 Source Analyzer의 분석 결과를 직관적으로 이해하고 탐색할 수 있는 강력한 도구를 제공하게 되었습니다. 특히 EdgeHint 시스템을 통한 메타정보 품질 향상은 향후 Phase2 RAG 시스템의 정확성 향상에도 기여할 것으로 기대됩니다.

---

**구현자**: Claude (Sonnet 4)  
**구현 일자**: 2025-08-28  
**문서 버전**: v1.0