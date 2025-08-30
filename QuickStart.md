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

### 1. 전체 분석 및 시각화 (Full Analysis and Visualization)

프로젝트의 전체 코드를 분석하고 사용 가능한 모든 시각화를 생성하려면 다음 명령어를 사용합니다:

```bash
python phase1/src/main.py --all --input-path "PROJECT/sampleSrc" --output-dir "visualize/output"
```

이 명령어는 다음을 수행합니다:
*   지정된 `--input-path`에 있는 전체 코드베이스를 분석합니다.
*   지원되는 모든 다이어그램(의존성 그래프, ERD, 시퀀스 다이어그램 등)을 생성합니다.
*   생성된 모든 시각화 결과는 `--output-dir`에 저장됩니다.

### 2. 부분 분석 및 시각화 (Partial Analysis and Visualization)

특정 분석 또는 시각화 작업만 선택하여 실행할 수 있습니다.

#### ⚙️ 주요 파라미터 설명:

**참고**: 아래 파라미터 중 **(필수)**는 반드시 지정해야 하며, **(중요)**는 일반적으로 설정하는 것이 좋습니다.

*   `--analyze-code`: 코드 분석만 수행하고 시각화는 생성하지 않습니다.
*   `--generate-erd`: ERD(Entity-Relationship Diagram)를 생성합니다.
*   `--generate-callgraph`: 호출 그래프(Call Graph)를 생성합니다.
*   `--generate-sequencediagram`: 시퀀스 다이어그램(Sequence Diagram)을 생성합니다.
*   `--input-path <경로>`: 분석할 소스 코드 디렉토리를 지정합니다. **(필수)**
    *   예: `"C:/Users/YourProject/src"`
*   `--output-dir <경로>`: 생성된 시각화 결과가 저장될 디렉토리를 지정합니다. **(중요)**
    *   기본값: `visualize/output`
*   `--config <경로>`: 사용자 정의 설정 파일을 지정합니다. **(고급)**
    *   기본값: `config/config.yaml`
*   `--project-name <이름>`: 분석 결과를 저장할 프로젝트의 이름을 지정합니다. **(권장)**
    *   분석 결과 데이터베이스에 저장될 프로젝트 식별 이름입니다.

#### 📝 예시:

**a) 코드 분석만 수행:**

```bash
python phase1/src/main.py --analyze-code --input-path "path/to/your/project" --project-name "MyAnalysis"
```

**b) 특정 입력 경로에 대해 ERD와 호출 그래프만 생성:**

```bash
python phase1/src/main.py --generate-erd --generate-callgraph --input-path "path/to/your/project" --output-dir "visualize/output" --project-name "MyCustomProject"
```

**c) 시퀀스 다이어그램을 생성하고 사용자 정의 출력 디렉토리에 저장:**

```bash
python phase1/src/main.py --generate-sequencediagram --input-path "path/to/your/project" --output-dir "my_custom_output" --project-name "MySequenceProject"
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

`visualize/cli.py --help` 명령어를 통해 사전 분석된 데이터를 기반으로 특정 시각화를 생성하는 자세한 옵션을 확인할 수 있습니다.

## 🌐 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 내장된 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **환경변수**: 웹 대시보드 백엔드 실행 시 다음 환경변수를 설정하여 서버 동작을 제어할 수 있습니다. **(중요)**
    *   `HOST`: 서버가 바인딩될 IP 주소 (예: `0.0.0.0` for all interfaces).
    *   `PORT`: 서버가 수신 대기할 포트 번호 (예: `8000`).
    *   `ALLOWED_ORIGINS`: CORS(Cross-Origin Resource Sharing)를 허용할 프런트엔드 도메인 목록 (예: `http://127.0.0.1:3000`).
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

## 📚 다음 단계 및 추가 정보

더 자세한 내부 구조, 데이터 모델, 상세 오프라인 설치 절차 및 트러블슈팅 가이드는 `README_detailed.md`를 참고하세요.