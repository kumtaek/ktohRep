# SourceAnalyzer 빠른 시작 가이드

SourceAnalyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. 이 가이드는 SourceAnalyzer를 사용하여 코드 분석 및 시각화를 빠르게 시작하는 방법을 설명합니다.

## 🚀 사전 준비

1.  **Python 3.10+ 설치**:
    *   SourceAnalyzer는 Python 3.10 이상 버전에서 동작합니다. 시스템에 Python이 설치되어 있는지 확인하십시오.

## 📦 설치

프로젝트 파일이 준비된 환경에서 다음 단계를 따릅니다.

1.  **가상 환경 생성 및 의존성 설치**:
    ```bash
    python -m venv venvSrcAnalyzer
    .\venvSrcAnalyzer\Scripts\activate
    pip install -r requirements.txt
    ```
    *   이 명령은 프로젝트에 필요한 모든 Python 라이브러리를 설치합니다.

## 💡 사용법

**참고**: 모든 명령줄 인자에 대한 상세 설명은 `README_detailed.md`를 참조하십시오.

### 1. 전체 분석 및 시각화 (Full Analysis and Visualization)

프로젝트의 전체 코드를 분석하고 사용 가능한 모든 시각화를 생성하려면 다음 명령어를 사용합니다:

```bash
# Windows
run_analyzer.bat sampleSrc --all

# Linux/Mac
./run_analyzer.sh sampleSrc --all
```

**디렉토리 구조**:
분석할 프로젝트는 다음과 같은 구조로 준비해야 합니다:
```
./                                # 프로젝트 루트
├── data/                        # 글로벌 메타데이터 (phase1 시스템 데이터)
│   └── metadata.db             # 시스템 전체 메타데이터
├── logs/                        # 글로벌 로그 (phase1 시스템 로그)
│   └── analyzer.log            # 시스템 분석 로그
├── project/                     # 프로젝트별 소스 및 데이터
│   └── sampleSrc/              # 프로젝트명 디렉토리
│       ├── src/                # 소스 코드 (Java, JSP 파일들)
│       ├── data/               # 프로젝트별 분석 데이터
│       │   └── metadata.db     # 프로젝트 분석 결과
│       └── db_schema/          # DB 스키마 CSV 파일들 (선택사항)
│           ├── ALL_TABLES.csv
│           ├── ALL_TAB_COLUMNS.csv
│           └── ALL_CONSTRAINTS.csv
└── output/                      # 사용자 결과물 확인 위치
    └── sampleSrc/              # 프로젝트별 출력
        ├── visualize/          # 시각화 파일들
        └── logs/               # 프로젝트 분석 로그
```

이 명령어는 다음을 수행합니다:
*   `./project/<프로젝트명>/src/` 디렉토리에 있는 전체 코드베이스를 분석합니다.
*   지원되는 모든 다이어그램(의존성 그래프, ERD, 시퀀스 다이어그램 등)을 생성합니다.
*   생성된 모든 시각화 결과는 `./output/<프로젝트명>/visualize/`에 저장됩니다.

### 2. 부분 분석 및 시각화 (Partial Analysis and Visualization)

특정 분석 또는 시각화 작업만 선택하여 실행할 수 있습니다.

#### ⚙️ 주요 파라미터 설명:

**참고**: 아래 파라미터 중 **(필수)**는 반드시 지정해야 하며, **(중요)**는 일반적으로 설정하는 것이 좋습니다.

*   `--analyze-code`: 코드 분석만 수행하고 시각화는 생성하지 않습니다.
*   `--generate-erd`: ERD(Entity-Relationship Diagram)를 생성합니다.
*   `--generate-callgraph`: 호출 그래프(Call Graph)를 생성합니다.
*   `--generate-sequencediagram`: 시퀀스 다이어그램(Sequence Diagram)을 생성합니다.
*   `<project_name>`: 분석할 프로젝트의 이름을 지정합니다. **(필수)**
    *   프로젝트 파일들은 `./project/<project_name>/src/` 디렉토리에 위치해야 합니다.
    *   예: `sampleSrc` (분석할 소스는 `./project/sampleSrc/src/`에 위치)
*   `--config <경로>`: 사용자 정의 설정 파일을 지정합니다. **(고급)**
    *   기본값: `config/config.yaml`
    *   프로젝트별 경로 템플릿을 통해 자동으로 경로가 설정됩니다.
*   `--export-md`: 분석된 메타데이터를 Markdown 형식의 보고서로 내보냅니다. (지정하지 않으면 `./output/<프로젝트명>/reports`에 저장)

#### 📝 예시:

**a) 코드 분석만 수행:**

```bash
# Windows
run_analyzer.bat --project-name sampleSrc --analyze-code

# Linux/Mac  
./run_analyzer.sh MyAnalysis --analyze-code
```

참고: 소스 코드는 `./project/MyAnalysis/src/` 디렉토리에 위치해야 합니다.

**b) 특정 프로젝트에 대해 ERD와 호출 그래프만 생성:**

```bash
# Windows
run_analyzer.bat --project-name sampleSrc --generate-erd --generate-callgraph

# Linux/Mac
./run_analyzer.sh MyCustomProject --generate-erd --generate-callgraph
```

참고: 출력은 `./project/MyCustomProject/output/visualize/` 디렉토리에 저장됩니다.

**c) 시퀀스 다이어그램만 생성:**

```bash
# Windows
run_analyzer.bat --project-name sampleSrc --generate-sequencediagram

# Linux/Mac
./run_analyzer.sh MySequenceProject --generate-sequencediagram
```

참고: 출력은 `./project/MySequenceProject/output/visualize/` 디렉토리에 저장됩니다.

#### d) 메타데이터를 Markdown 보고서로 내보내기:

```bash
# Windows
run_analyzer.bat --project-name sampleSrc --export-md

# Linux/Mac
./run_analyzer.sh --project-name sampleSrc --export-md

# e) 특정 소스 경로를 지정하여 분석:
# Windows
run_analyzer.bat --project-name sampleSrc --source-path "C:\MyProject\SourceCode" --analyze-code

# Linux/Mac
./run_analyzer.sh --project-name sampleSrc --source-path "/home/user/myproject/source" --analyze-code
```

### 3. `config.yaml`을 통한 고급 설정

`config/config.yaml` 파일은 SourceAnalyzer의 동작을 세밀하게 제어할 수 있는 핵심 설정 파일입니다. 이 파일을 수정하여 분석 대상, 제외 규칙, 시각화 옵션 등을 정의할 수 있습니다.

*   **주요 설정 항목 (예시)**:
    *   `analysis_targets`: 분석할 파일 확장자 목록 (예: `.java`, `.jsp`, `.xml`).
    *   `exclude_dirs`: 분석에서 제외할 디렉토리 목록.
    *   `visualization_options`: 각 다이어그램 유형별 세부 설정.
*   `config.yaml` 파일을 직접 열어 내용을 확인하고 필요에 따라 수정하십시오.

### 4. 시각화만 별도로 실행 (Pre-analyzed Data)

이미 분석을 수행하여 필요한 중간 데이터가 생성된 경우, `visualize/cli.py` 스크립트를 사용하여 시각화만 별도로 생성할 수 있습니다.

```bash
python visualize/cli.py --help
```

**예시: 특정 프로젝트의 시각화 생성**
```bash
# 의존성 그래프를 Mermaid 형식으로 내보내기
python visualize/cli.py graph --project-name sampleSrc --export-mermaid dependency_graph.md

# ERD를 HTML과 Mermaid 형식으로 내보내기
python visualize/cli.py erd --project-name sampleSrc --export-html erd.html --export-mermaid erd.md
```

참고: 출력 파일들은 `./output/<프로젝트명>/visualize/` 디렉토리에 저장됩니다.

## 🌐 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 내장된 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **설정**: 웹 대시보드 백엔드 서버의 모든 설정(호스트, 포트, CORS 등)은 `config/config.yaml` 파일의 `server` 섹션에서 관리됩니다.
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

## 📚 다음 단계 및 추가 정보

더 자세한 내부 구조, 데이터 모델, 상세 오프라인 설치 절차 및 트러블슈팅 가이드는 `README_detailed.md`를 참고하세요.