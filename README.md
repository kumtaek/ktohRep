# 소스 분석기 - 1단계 메타정보 생성 시스템

레거시 Java/JSP/MyBatis/Oracle 소스 코드를 정적 분석하여 메타정보를 생성하는 시스템입니다.

## 프로젝트 개요

### 주요 특징
- **원문 비저장 원칙**: 소스 코드 원문을 저장하지 않고 경로, 라인 범위, 구조 정보만 메타데이터로 저장
- **다중 언어 지원**: Java, JSP, MyBatis XML, SQL(Oracle 방언) 분석
- **신뢰도 추적**: 모든 분석 결과에 신뢰도 점수 포함
- **증분 분석**: 변경된 파일만 재분석하는 효율적인 처리
- **병렬 처리**: 멀티스레드를 통한 고성능 분석

### 분석 대상
- **Java**: 클래스, 메서드, 어노테이션, 의존성 관계
- **JSP**: 스크립틀릿 내 SQL, include 관계
- **MyBatis XML**: SQL 매퍼, 동적 SQL, 조인 조건, 필터 조건
- **DB 스키마**: Oracle 메타데이터 (CSV 형태)

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
│   └── metadata_engine.py   # 메타데이터 저장 엔진
└── utils/
    ├── confidence_calculator.py # 신뢰도 계산기
    └── csv_loader.py        # DB 스키마 CSV 로더
```

## 설치 및 실행

### 1. 의존성 설치 (온라인 환경)

인터넷 연결이 가능한 환경에서는 다음 명령으로 Python 의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

### 2. 오프라인 설치 가이드 (폐쇄망 환경)

본 시스템은 폐쇄망 환경에서 운영될 수 있도록 설계되었습니다. 모든 외부 의존성은 사전에 다운로드하여 오프라인으로 설치해야 합니다.

#### 2.1. Python 패키지

1.  **Wheelhouse 생성**: 인터넷 연결이 가능한 환경에서 다음 명령을 사용하여 모든 Python 패키지의 휠(wheel) 파일을 다운로드합니다.
    ```bash
    pip wheel -r requirements.txt -w ./wheelhouse
    # 2단계 LLM/RAG 관련 패키지 (requirements.txt에서 주석 해제 후)
    # pip wheel -r requirements.txt -w ./wheelhouse --only-binary :all:
    ```
2.  **오프라인 설치**: 생성된 `wheelhouse` 폴더를 폐쇄망 환경으로 옮긴 후, 다음 명령으로 설치합니다.
    ```bash
    pip install --no-index --find-links=./wheelhouse -r requirements.txt
    ```
    **참고**: `lxml` 패키지는 빌드 환경에 따라 컴파일이 필요할 수 있습니다. `pip wheel` 명령 시 `lxml`에 대한 특정 플랫폼용 휠이 생성되었는지 확인하고, 필요한 경우 `lxml` 공식 문서(https://lxml.de/installation.html)를 참조하여 오프라인 빌드 방법을 따릅니다.

#### 2.2. JavaScript 시각화 라이브러리

시각화 모듈(`visualize/`)은 Cytoscape.js, Dagre.js 등의 JavaScript 라이브러리를 사용합니다. 이들은 `visualize/static/vendor/` 경로에 로컬로 번들링되어야 합니다.

1.  **에셋 다운로드**: 인터넷 연결이 가능한 환경에서 다음 스크립트를 실행하여 필요한 JavaScript 에셋을 다운로드합니다.
    ```bash
    python visualize/static/vendor/download_assets.py
    ```
    이 스크립트는 `visualize/static/vendor/` 폴더에 `cytoscape.min.js`, `dagre.min.js`, `cytoscape-dagre.js` 등을 다운로드합니다.
2.  **오프라인 배치**: 다운로드된 `visualize/static/vendor/` 폴더 전체를 폐쇄망 환경으로 옮겨 시스템의 `visualize/static/vendor/` 경로에 배치합니다.

#### 2.3. Java 개발 환경 (JDK)

Java 소스 코드(`*.java`)를 파싱하기 위해 `javalang` 라이브러리가 사용됩니다. `javalang` 자체는 Python 라이브러리이지만, Java 소스 코드 분석의 맥락상 Java 개발 환경(JDK)이 필요할 수 있습니다. 폐쇄망 환경에 맞는 JDK를 설치합니다.

#### 2.4. Oracle 11g 데이터베이스

운영 환경에서 Oracle 11g 데이터베이스를 사용하는 경우, 표준 오프라인 설치 절차에 따라 설치 및 구성합니다. `cx_oracle` Python 패키지는 Oracle Client 라이브러리에 의존하므로, Oracle Client도 오프라인으로 설치해야 합니다.

#### 2.5. LLM 관련 (2단계 개발 시 필요)

현재 1단계 메타정보 생성 시스템에서는 LLM이 직접 사용되지 않습니다. 2단계 LLM 기반 질의응답 및 영향평가 기능 개발 시 다음 항목들이 추가로 필요합니다.

1.  **LLM 및 임베딩 모델**: Qwen2.5 (7B/32B), BGE-m3, ko-sentence-transformers, BGE reranker v2와 같은 모델 가중치 파일을 Hugging Face 등에서 직접 다운로드하여 특정 경로(예: `models/llm`, `models/embedding`)에 배치해야 합니다.
2.  **vLLM 설치**: LLM 서빙을 위한 vLLM 및 해당 종속성(CUDA, PyTorch 등)을 오프라인으로 설치합니다. vLLM 공식 문서를 참조하여 폐쇄망 환경에 맞는 설치 방법을 따릅니다.
3.  **Python 패키지**: `openai`, `langchain`, `faiss-cpu`, `sentence-transformers`, `fastapi`, `uvicorn` 등 2단계 관련 Python 패키지들을 `requirements.txt`에서 주석 해제 후 2.1. Python 패키지 섹션의 오프라인 설치 절차를 따릅니다.

`config/config.yaml` 파일에서 데이터베이스와 분석 옵션을 설정합니다.

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
    parser_type: "javaparser"
```

### 3. 프로젝트 분석 실행

```bash
python main.py /path/to/your/project --project-name "MyProject"
```

### 4. DB 스키마 준비

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

## 주요 기능

### 1. Java 소스 분석
- JavaParser를 사용한 AST 기반 분석
- 클래스, 메서드, 어노테이션 추출
- 메서드 호출 관계 분석
- Spring Framework 어노테이션 처리

### 2. MyBatis XML 분석
- SQL 매퍼 구문 추출 (`<select>`, `<insert>`, `<update>`, `<delete>`)
- 동적 SQL 태그 처리 (`<if>`, `<choose>`, `<foreach>`)
- 조인 조건 자동 추출
- 필수 필터 조건 식별

### 3. 신뢰도 기반 분석
- AST 품질 기반 신뢰도 계산
- 정적 규칙 매칭 신뢰도
- DB 스키마 매칭 신뢰도
- 복잡도에 따른 신뢰도 조정

### 4. 메타데이터 저장
- 파일, 클래스, 메서드 구조 정보
- SQL 구문, 조인, 필터 조건
- 의존성 그래프 (호출, 참조 관계)
- 분석 신뢰도 및 로그

## 데이터베이스 스키마

주요 테이블:
- `projects`: 프로젝트 정보
- `files`: 소스 파일 메타데이터 
- `classes`: Java 클래스 정보
- `methods`: Java 메서드 정보
- `sql_units`: SQL 구문 정보
- `joins`: 조인 조건
- `required_filters`: 필수 필터 조건
- `edges`: 의존성 관계 그래프

## 명령행 옵션

```bash
python main.py [OPTIONS] PROJECT_PATH

인수:
  PROJECT_PATH          분석할 프로젝트 경로

옵션:
  --config CONFIG       설정 파일 경로 (기본값: ./config/config.yaml)
  --project-name NAME   프로젝트 이름 (기본값: 폴더명)
  --incremental         증분 분석 모드
  --help                도움말 표시
```

## 분석 결과 예시

```
==========================================
분석 완료!
프로젝트: insurance-system
분석된 파일 수: 234
Java 파일: 156
JSP 파일: 23
XML 파일: 55
클래스 수: 198
메서드 수: 1,247  
SQL 구문 수: 134
==========================================
```

## 설정 옵션

### 파서 설정
```yaml
parsers:
  java:
    enabled: true
    parser_type: "javaparser"  # 또는 "tree-sitter"
    
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
  chunk_size: 512         # 청킹 크기
  confidence_threshold: 0.5 # 신뢰도 임계값
```

### 파일 패턴 설정
```yaml
file_patterns:
  include:
    - "**/*.java"
    - "**/*.jsp"
    - "**/*.xml"
  exclude:
    - "**/target/**"
    - "**/build/**"
```

## 로깅 및 모니터링

- 분석 진행 상황 실시간 로깅
- 오류 파일 및 원인 추적
- 분석 성능 메트릭
- 신뢰도 분포 통계

## 향후 계획

- Tree-sitter 기반 다국어 파서 지원
- LLM 보강 기능 (2단계)
- 벡터 임베딩 및 RAG 기능 (2단계)
- 웹 대시보드 UI
- Oracle 운영 환경 배포

## 라이선스

이 프로젝트는 내부 사용을 위한 소스 분석 도구입니다.

---

## 시각화(Visualize) 사용법 및 배치 PNG 안내

분석(DB 구축)이 끝난 후, `visualize` 모듈을 사용해 ERD/의존성/컴포넌트/시퀀스 다이어그램을 HTML로 생성할 수 있습니다. 엔트리 포인트는 저장소 루트의 `visualize_cli.py`입니다.

### 1) 시각화 생성(HTML)

```bash
# 의존성 그래프 (use_table, include 등 지정)
python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html \
  --kinds use_table,include --min-confidence 0.5 --max-nodes 1000

# ERD 전체 또는 부분(특정 SQL 기준)
python visualize_cli.py erd --project-id 1 --out visualize/output/erd.html
python visualize_cli.py erd --project-id 1 --out visualize/output/erd_from_sql.html \
  --from-sql MapperNamespace:selectUser

# 컴포넌트 다이어그램
python visualize_cli.py component --project-id 1 --out visualize/output/components.html

# 시퀀스(흐름) 다이어그램
python visualize_cli.py sequence --project-id 1 --out visualize/output/sequence.html \
  --start-file UserService.java --depth 3
```

생성된 HTML은 브라우저에서 열어 인터랙티브하게 탐색할 수 있으며, 상단 툴바에서 PNG로 내보내기(수동)도 지원합니다.

### 2) 배치 PNG 생성(CI 아티팩트 용)

CI에서 HTML을 일괄 렌더링하여 PNG로 아카이브하려면 헤드리스 브라우저를 사용하는 방법을 권장합니다. 아래는 Python Playwright 예시입니다.

```bash
pip install playwright && playwright install chromium
```

```python
# tools/export_png_batch.py (예시 스니펫)
import base64, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def export_html_to_png(html_path: Path, png_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.as_uri())
        # 뷰어 내 cy.png() 실행(페이지에 따라 id가 다를 수 있음)
        b64 = page.evaluate("() => cy.png({full: true, scale: 2, bg: 'white'})")
        png_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.write_bytes(base64.b64decode(b64.split(',')[1] if ',' in b64 else b64))
        browser.close()

if __name__ == '__main__':
    out_dir = Path('visualize/output')
    for html in out_dir.glob('*.html'):
        export_html_to_png(html, out_dir / (html.stem + '.png'))
```

CI 예시(GitHub Actions):

```yaml
- name: Export visualization PNGs
  run: |
    pip install playwright && python -m playwright install chromium
    python visualize_cli.py erd --project-id 1 --out visualize/output/erd.html
    python visualize_cli.py graph --project-id 1 --out visualize/output/graph.html --kinds use_table
    python visualize_cli.py component --project-id 1 --out visualize/output/components.html
    python visualize_cli.py sequence --project-id 1 --out visualize/output/sequence.html --depth 3
    python tools/export_png_batch.py
- name: Upload PNG artifacts
  uses: actions/upload-artifact@v4
  with:
    name: visualize-pngs
    path: visualize/output/*.png
```

참고: 오프라인/폐쇄망 환경에서는 뷰어 HTML 내 CDN 스크립트(예: cytoscape, dagre)를 로컬 번들로 교체하는 것을 권장합니다.

### 3) 관련 문서
- 구현 완료 보고: `Visualize_003_Implementation.md`
- 구현 리뷰: `Visualize_004_Implementation_review.md`
- 향후 구현 기획: `Visualize_005_Implementation_plan.md`
