# 소스 분석기 - 정적 분석/시각화 도구

이 문서는 한국어 독자 기준으로 재정리되었습니다. 아래 요약과 빠른 시작을 참고하세요.

## 빠른 시작

### 1) 의존성 설치
```bash
pip install -r requirements.txt
```

### 2) 시각화 생성 예시
```bash
# 의존성 그래프 (HTML)
python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html \
  --kinds use_table,include --min-confidence 0.5 --max-nodes 1000

# ERD (HTML) + Mermaid 문서(.md)
python visualize_cli.py erd --project-id 1 --out visualize/output/erd.html \
  --export-mermaid visualize/output/erd.md

# 클래스 다이어그램 (신규 v1.3)
python visualize_cli.py class --project-id 1 --out visualize/output/class.html \
  --modules "database,models" --export-mermaid visualize/output/class.md

# Mermaid 코드(.mmd)만 출력
python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html \
  --kinds use_table,include --export-mermaid visualize/output/graph.mmd
```

### 3) 지원되는 시각화 유형 (5종)
- **의존성 그래프**: 파일 간 호출, import, extends 관계
- **ERD**: 데이터베이스 테이블과 관계
- **컴포넌트 다이어그램**: 모듈/패키지 단위 구조 
- **시퀀스 다이어그램**: 메서드 호출 흐름
- **클래스 다이어그램**: Python 클래스 구조와 상속 관계 (v1.3 신규)

### 4) Mermaid 내보내기 옵션 (v1.4 확장)
- `--mermaid-label-max` 라벨 최대 길이(기본 20)
- `--mermaid-erd-max-cols` ERD 컬럼 최대 표기 수(기본 10)
- `--export-strategy` full|balanced|minimal 프리셋(기본 balanced)
- `--class-methods-max` 클래스 다이어그램 메서드 최대 수(기본 10)
- `--class-attrs-max` 클래스 다이어그램 속성 최대 수(기본 10)
- `--keep-edge-kinds` 보존할 엣지 종류(기본 includes,call,use_table)

---

## 버전 히스토리

### v1.4 (2025-08-29) - 동적 SQL 처리 및 시각화 개선
- **JSP/MyBatis 동적 SQL 처리 개선**: lxml 기반 AST 처리로 조건/구조 정보 보존
- **데이터베이스 세션 관리 개선**: scoped_session과 transaction boundary 명확화
- **Mermaid 내보내기 단순화**: export strategy와 overflow 요약 기능 추가
- **트랜잭션 경계 개선**: 단일 begin 경계로 원자성 보장
- **설정 문서 정합성**: parser_type 실제 구현과 일치

### v1.3 - 클래스 다이어그램 및 한글 인코딩 지원
### v1.2 - Web Dashboard 및 시각화 확장
### v1.1 - 초기 시각화 구현

---

## 프로젝트 개요

### 주요 목표
- **멀티 빅데이터 분석**: 레거시 코드를 자동 파싱하여 경로, 호출 범위, 구조 정보를 메타데이터로 생성
- **다양한 언어 지원**: Java, JSP, MyBatis XML, SQL(Oracle 방언) 분석
- **신뢰도 추론**: 모든 분석 결과에 신뢰도 수치 포함
- **증분 분석**: 변경된 파일만 재분석하는 효율적인 처리
- **병렬 분석**: 멀티스레드를 통한 고성능 분석

### 분석 대상
- **Java**: 클래스 메서드, 어노테이션, 의존성 관계
- **JSP**: 스크립틀릿 SQL, include 관계
- **MyBatis XML**: SQL 매핑, 동적 SQL, 조인 조건, 필터 조건
- **DB 스키마**: Oracle 메타데이터(CSV 형태)
- **Python**: 클래스, 메서드, 상속 관계 (v1.3 신규)

## 시스템 구조

```
src/
├── models/
│   └── database.py          # SQLAlchemy 모델 정의
├── parsers/
│   ├── java_parser.py       # Java AST 파서
│   ├── jsp_mybatis_parser.py # JSP/MyBatis XML 파서
│   └── sql_parser.py        # SQL 구문 파서
├── database/
│   └── metadata_engine.py   # 메타데이터 관리 엔진
├── utils/
│   ├── confidence_calculator.py # 신뢰도 계산기
│   └── csv_loader.py        # DB 스키마 CSV 로더
└── visualize/
    ├── builders/
    │   ├── class_diagram.py   # 클래스 다이어그램 빌더 (v1.3 신규)
    │   ├── dependency_graph.py
    │   ├── erd.py
    │   ├── component_diagram.py
    │   └── sequence_diagram.py
    ├── templates/
    │   ├── class_view.html    # 클래스 다이어그램 템플릿 (v1.3 신규)
    │   ├── graph_view.html
    │   └── erd_view.html
    └── exporters/
        └── mermaid_exporter.py # Mermaid 내보내기
```

## 설치 및 실행

### 1. 의존성 설치 (온라인 환경)

인터넷이 가능한 환경에서는 다음 명령으로 Python 의존성을 설치합니다:

```bash
pip install -r requirements.txt
```

### 2. 오프라인 설치 가이드 (에어갭 환경)

본 시스템은 에어갭 환경에서 운영되도록 설계되었습니다. 모든 외부 의존성을 사전에 다운로드하여 오프라인으로 설치해야 합니다.

#### 2.1. Python 패키지

1. **Wheelhouse 생성**: 인터넷이 가능한 환경에서 다음 명령을 사용하여 모든 Python 패키지를 wheel 파일로 다운로드합니다:
   ```bash
   pip wheel -r requirements.txt -w ./wheelhouse
   ```

2. **오프라인 설치**: 생성된 `wheelhouse` 폴더를 에어갭 환경으로 복사 후 다음 명령으로 설치합니다:
   ```bash
   pip install --no-index --find-links=./wheelhouse -r requirements.txt
   ```

#### 2.2. JavaScript 시각화 라이브러리

시각화 모듈(`visualize/`)은 Cytoscape.js, Dagre.js 등의 JavaScript 라이브러리를 사용합니다. 이들은 `visualize/static/vendor/` 경로에 로컬 번들링되어야 합니다.

1. **자산 다운로드**: 인터넷이 가능한 환경에서 다음 스크립트를 실행하여 필요한 JavaScript 자산을 다운로드합니다:
   ```bash
   python visualize/static/vendor/download_assets.py
   ```

2. **오프라인 배치**: 다운로드된 `visualize/static/vendor/` 폴더 전체를 에어갭 환경으로 복사하여 시스템의 `visualize/static/vendor/` 경로에 배치합니다.

### 3. 설정 파일

`config/config.yaml` 파일에서 데이터베이스 및 분석 옵션을 설정합니다:

```yaml
# 데이터베이스 설정
database:
  type: sqlite  # 개발용
  sqlite:
    path: "./data/metadata.db"
    
# 파서 설정  
parsers:
  java:
    enabled: true
    parser_type: "javalang"   # 또는 "tree-sitter" (설치 필요)
  python:
    enabled: true
    parser_type: "ast"
```

### 4. 프로젝트 분석 실행

```bash
python main.py /path/to/your/project --project-name "MyProject"
```

### 5. DB 스키마 준비

프로젝트 폴더 하위에 `DB_SCHEMA` 폴더를 생성하고 다음 CSV 파일들을 배치합니다:

```
PROJECT/
└── your-project/
    └── DB_SCHEMA/
        ├── ALL_TABLES.csv
        ├── ALL_TAB_COLUMNS.csv
        ├── ALL_TAB_COMMENTS.csv
        ├── ALL_COL_COMMENTS.csv
        └── PK_INFO.csv
```

## 시각화 사용법

분석(DB 구축)이 완료된 후 `visualize` 모듈을 사용해 다양한 다이어그램을 HTML로 생성할 수 있습니다.

### 1) 시각화 생성 (HTML + Mermaid)

```bash
# 의존성 그래프
python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html \
  --kinds use_table,include --min-confidence 0.5 --max-nodes 1000 \
  --export-mermaid visualize/output/graph.md

# ERD (전체 또는 특정 SQL 기준)
python visualize_cli.py erd --project-id 1 --out visualize/output/erd.html \
  --export-mermaid visualize/output/erd.md

python visualize_cli.py erd --project-id 1 --out visualize/output/erd_from_sql.html \
  --from-sql MapperNamespace:selectUser

# 컴포넌트 다이어그램
python visualize_cli.py component --project-id 1 --out visualize/output/components.html \
  --export-mermaid visualize/output/components.md

# 시퀀스(호출 추적) 다이어그램
python visualize_cli.py sequence --project-id 1 --out visualize/output/sequence.html \
  --start-file UserService.java --depth 3 \
  --export-mermaid visualize/output/sequence.md

# 클래스 다이어그램 (v1.3 신규)
python visualize_cli.py class --project-id 1 --out visualize/output/class.html \
  --modules "database,models" --include-private --max-methods 15 \
  --export-mermaid visualize/output/class.md
```

### 2) 클래스 다이어그램 상세 옵션 (v1.3)

```bash
# 전체 프로젝트 Python 파일 분석
python visualize_cli.py class --project-id 1 --out class.html

# 특정 모듈만 포함
python visualize_cli.py class --project-id 1 --modules "src.models,src.database" --out class.html

# Private 멤버 포함하여 상세 분석
python visualize_cli.py class --project-id 1 --include-private --max-methods 20 --out class.html

# Mermaid 코드만 출력
python visualize_cli.py class --project-id 1 --export-mermaid class.mmd --out /dev/null
```

**클래스 다이어그램 특징**:
- Python AST 기반 정확한 파싱
- 클래스, 메서드, 속성, 상속 관계 자동 추출
- Private/Public 멤버 구분 시각화
- 추상 클래스, 프로퍼티, 정적 메서드 표시
- Mermaid `classDiagram` 문법 완전 지원

### 3) Mermaid 내보내기

모든 다이어그램은 Mermaid 형식으로 내보낼 수 있습니다:

- **`.md` 파일**: 완전한 문서 (제목, 범례, Mermaid 코드블록 포함)
- **`.mmd` 또는 `.mermaid` 파일**: Mermaid 코드만

```bash
# 완전한 Markdown 문서
python visualize_cli.py erd --project-id 1 --out erd.html --export-mermaid erd.md

# Mermaid 코드만 (GitHub/GitLab 등에서 직접 렌더링 가능)
python visualize_cli.py class --project-id 1 --out class.html --export-mermaid class.mmd
```

### 4) CI/CD 자동화 예시

```yaml
# .github/workflows/visualize.yml
name: Generate Documentation
on: [push]
jobs:
  visualize:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Analyze project
      run: python main.py . --project-name "MyApp"
    - name: Generate visualizations
      run: |
        python visualize_cli.py erd --project-id 1 --out docs/erd.html --export-mermaid docs/erd.md
        python visualize_cli.py class --project-id 1 --out docs/class.html --export-mermaid docs/class.md
        python visualize_cli.py graph --project-id 1 --out docs/deps.html --export-mermaid docs/deps.md
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

## 주요 기능

### 1. 다중 언어 파싱 지원
- **Java**: JavaParser를 사용한 AST 기반 분석
- **Python**: AST 기반 클래스 구조 분석 (v1.3)
- **JSP/MyBatis**: ANTLR 기반 구문 분석
- **SQL**: Oracle 방언 지원

### 2. 신뢰도 기반 분석
- AST 정보 기반 신뢰도 계산
- 정적 규칙 매칭 신뢰도
- DB 스키마 매칭 신뢰도
- 복잡성에 따른 신뢰도 조정

### 3. 메타데이터 관리
- 파일, 클래스 메서드 구조 정보
- SQL 구문, 조인, 필터 조건
- 의존성 그래프 (호출, 참조 관계)
- 분석 신뢰도 및 로그

### 4. 고성능 처리
- 병렬 파싱 및 분석
- 증분 분석 (변경된 파일만)
- 메모리 효율적인 청크 처리
- 대용량 프로젝트 지원

## 명령어 옵션

```bash
# 메인 분석 도구
python main.py [OPTIONS] PROJECT_PATH

인수:
  PROJECT_PATH          분석할 프로젝트 경로

옵션:
  --config CONFIG       설정 파일 경로 (기본값: ./config/config.yaml)
  --project-name NAME   프로젝트 이름 (기본값: 폴더명)
  --incremental         증분 분석 모드
  --help                도움말 표시

# 시각화 도구
python visualize_cli.py [COMMAND] [OPTIONS]

명령어:
  graph                의존성 그래프 생성
  erd                  ERD 생성  
  component            컴포넌트 다이어그램 생성
  sequence             시퀀스 다이어그램 생성
  class                클래스 다이어그램 생성 (v1.3)

공통 옵션:
  --project-id ID      프로젝트 ID (필수)
  --out PATH           출력 HTML 파일 경로 (필수)
  --export-mermaid PATH  Mermaid 내보내기 (.md/.mmd)
  --min-confidence NUM  최소 신뢰도 임계값 (기본값: 0.5)
  --max-nodes NUM      최대 노드 수 (기본값: 2000)
```

## 설정 옵션

### 파서 설정
```yaml
parsers:
  java:
    enabled: true
    parser_type: "javalang"   # 또는 "tree-sitter" (설치 필요)
    
  python:
    enabled: true
    parser_type: "ast"
    
  jsp:
    enabled: true
    parser_type: "antlr"
    
  sql:
    enabled: true
    oracle_dialect: true
```

### 처리 설정
```yaml
processing:
  max_workers: 4          # 병렬 처리 워커 수
  chunk_size: 512         # 청크 크기
  confidence_threshold: 0.5 # 신뢰도 임계값
```

### 파일 필터 설정
```yaml
file_patterns:
  include:
    - "**/*.java"
    - "**/*.py"    # v1.3
    - "**/*.jsp"
    - "**/*.xml"
  exclude:
    - "**/target/**"
    - "**/build/**"
    - "**/__pycache__/**"  # v1.3
```

## 버전 히스토리

### v1.3 (Visualize_008) - 2025-08-28
- ✅ **클래스 다이어그램 신규 추가**: Python 클래스 구조 자동 분석
- ✅ **한글 인코딩 문제 완전 해결**: CLI 및 메시지 한글화
- ✅ **HTML 템플릿 버그 수정**: ERD 검색 기능 안정화
- ✅ **Mermaid 클래스 다이어그램 지원**: `classDiagram` 문법 완전 지원

### v1.2 (Visualize_007) - 2025-08-28
- ✅ **Mermaid/Markdown 내보내기 완성**: .md/.mmd 동시 지원
- ✅ **CLI 한글화**: 사용자 인터페이스 현지화
- ✅ **다이어그램 유형 확장**: ERD, 시퀀스, 그래프, 컴포넌트 지원

### v1.1 - 이전 버전
- 기본 시각화 기능 구현
- HTML 기반 인터랙티브 다이어그램
- 데이터베이스 메타데이터 분석

## 문제 해결

### 한글 인코딩 문제
v1.3에서 해결되었습니다. 만약 여전히 문제가 발생하면:
```bash
# Windows
chcp 65001
python visualize_cli.py --help

# Linux/Mac
export LANG=ko_KR.UTF-8
python visualize_cli.py --help
```

### 메모리 부족
대용량 프로젝트의 경우:
```bash
# 노드 수 제한
python visualize_cli.py graph --project-id 1 --max-nodes 500 --out graph.html

# 신뢰도 임계값 상향 조정
python visualize_cli.py erd --project-id 1 --min-confidence 0.8 --out erd.html
```

### Python 파일 분석 제한
현재 Python AST 파서는:
- ✅ 지원: 클래스, 메서드, 상속, 속성, 데코레이터
- ❌ 제한: 동적 속성 (`setattr`, `exec` 등)
- ❌ 제한: 런타임 임포트

## 라이선스

이 프로젝트는 테스트 및 분석을 위한 도구입니다.

---

## 관련 문서

- 구현 완료 보고서: `Visualize_008_Implementation.md` (최신)
- 이전 버전: `Visualize_007_Implementation.md`, `Visualize_007_Implementation_review.md`
- 향후 개발 계획: 다국어 클래스 분석, 고급 관계 추론, 성능 최적화