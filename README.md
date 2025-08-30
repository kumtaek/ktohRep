# Source Analyzer - 프로젝트 개요 및 빠른 시작 가이드

Source Analyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. 코드의 메타데이터를 추출하여 다양한 다이어그램(의존성 그래프, ERD, 컴포넌트, 클래스, 시퀀스 다이어그램)을 생성하며, 이를 JSON, CSV, Markdown(Mermaid), HTML 형식으로 내보낼 수 있습니다. 폐쇄망 환경에 최적화되어 설계되었으며, 내장된 OWASP 및 CWE 취약점 문서를 통해 보안 분석 및 가이드도 제공합니다.

## 🚀 주요 기능

**참고**: 모든 명령줄 인자에 대한 상세 설명은 `README_detailed.md`를 참조하십시오.

*   **정적 코드 분석**: Java 클래스/메서드, JSP/MyBatis SQL 구문, 파일/모듈 간의 관계 및 의존성 추출.
*   **다양한 시각화**:
    *   **의존성 그래프**: 파일, 클래스, SQL 단위 간의 호출 및 사용 관계.
    *   **ERD (Entity-Relationship Diagram)**: SQL 구문에서 추출된 테이블 및 조인 관계.
    *   **컴포넌트 다이어그램**: 시스템의 주요 컴포넌트 및 그 관계.
    *   **클래스 다이어그램**: Java 클래스의 구조, 상속, 구현 관계.
    *   **시퀀스 다이어그램**: 특정 메서드 호출 흐름 추적.
*   **유연한 내보내기**: 생성된 시각화 데이터를 JSON, CSV, Markdown(Mermaid), HTML 형식으로 내보내어 다양한 문서화 및 공유 요구사항 충족.
*   **메타데이터 보고서**: 분석된 메타데이터를 Markdown 형식의 요약 및 상세 보고서로 내보냅니다 (`--export-md` 옵션).
*   **오프라인 보안 문서**: OWASP Top 10 및 CWE 취약점 설명을 내장하여 오프라인 환경에서도 보안 가이드 및 샘플 제공. 웹 대시보드를 통해 API로 접근 가능.
*   **증분 분석**: 변경된 파일만 재분석하여 대규모 프로젝트의 분석 시간 단축.
*   **신뢰도 기반 분석**: 추출된 메타데이터 및 관계에 대한 신뢰도 점수를 제공하여 분석 결과의 정확성 판단 지원.

## 📦 오프라인 설치 가이드

Source Analyzer는 폐쇄망 환경에서 운영될 수 있도록 설계되었습니다. 다음 절차에 따라 온라인 환경에서 필요한 의존성을 준비한 후, 오프라인 환경에서 설치를 진행할 수 있습니다.

### 1. 사전 준비 (온라인 환경)

1.  **Python 3.10+ 설치**:
    *   공식 Python 웹사이트에서 Python 3.10 이상 버전을 다운로드하여 설치합니다.
    *   설치 시 "Add Python to PATH" 옵션을 선택하는 것이 좋습니다.

2.  **가상 환경 생성 및 pip 업그레이드**:
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -U pip
    ```

3.  **필수 의존성 휠(Wheel) 파일 생성**:
    *   `requirements.txt`에 명시된 모든 패키지의 휠 파일을 다운로드하여 오프라인 저장소를 만듭니다.
    ```bash
    .venv/Scripts/pip wheel -r requirements.txt -w wheelhouse/
    ```

4.  **추가 필수 패키지들**:
    다음 패키지들이 requirements.txt에 포함되어 있는지 확인하세요:
    ```
    # 핵심 의존성
    sqlalchemy>=1.4.0      # 데이터베이스 ORM
    pyyaml>=6.0            # 설정 파일 파싱
    javalang>=0.13.0       # Java 소스 파싱
    sqlparse>=0.4.4        # SQL 파싱
    lxml>=4.9.0            # XML 처리
    psutil>=5.9.0          # 시스템 모니터링
    
    # 웹 대시보드
    flask>=2.3.0           # 웹 프레임워크
    flask-cors>=4.0.0      # CORS 지원
    werkzeug>=2.3.0        # Flask 의존성
    jinja2>=3.1.0          # 템플릿 엔진
    markdown>=3.4.0        # Markdown 렌더링
    pygments>=2.16.0       # 코드 하이라이팅
    
    # HTTP 및 데이터 처리
    httpx>=0.24.0          # HTTP 클라이언트
    requests>=2.31.0       # HTTP 요청
    pydantic>=1.10.0       # 데이터 검증
    pandas>=1.5.0          # 데이터 조작
    numpy>=1.24.0          # 수치 연산
    
    # LLM 통합
    openai>=1.35.0         # LLM 클라이언트
    
    # 테스트 도구
    pytest>=7.0.0
    pytest-asyncio>=0.20.0
    ```

5.  **(선택) 웹 대시보드 프런트엔드 준비**:
    *   `web-dashboard/frontend` 디렉토리에서 `npm install` 및 `npm run build`를 실행하여 정적 파일을 미리 빌드합니다.
    ```bash
    cd web-dashboard/frontend
    npm install
    npm run build
    ```
    *   빌드된 `dist` 폴더를 오프라인 환경으로 가져갑니다.

### 2. 오프라인 설치 (운영 환경)

1.  **온라인에서 준비한 파일 전송**:
    *   `SourceAnalyzer.git` 프로젝트 폴더 전체와 `wheelhouse/` 디렉토리 (및 선택적으로 `web-dashboard/frontend/dist` 폴더)를 오프라인 환경으로 전송합니다.
2.  **가상 환경 생성 및 pip 업그레이드**:
    *   온라인 환경과 동일하게 가상 환경을 생성하고 `pip`를 최신 버전으로 업그레이드합니다.
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -U pip
    ```
3.  **오프라인 의존성 설치**:
    *   미리 생성한 `wheelhouse/` 디렉토리를 사용하여 의존성을 설치합니다.
    ```bash
    .venv/Scripts/pip install --no-index --find-links wheelhouse -r requirements.txt
    ```
4.  **(선택) 웹 대시보드 백엔드 실행**:
    *   `config/config.yaml`의 server 섹션에서 설정을 조정한 후 백엔드 서버를 실행합니다.
    ```yaml
    # config/config.yaml
    server:
      host: "0.0.0.0"
      port: 8000
      cors:
        enabled: true
        allow_origins: ["http://127.0.0.1:3000", "http://localhost:3000"]
    ```
    ```bash
    .venv/Scripts/python web-dashboard/backend/app.py
    ```
5.  **(선택) 웹 대시보드 프런트엔드 배포**:
    *   사전 빌드된 프런트엔드 정적 파일(`dist` 폴더)을 오프라인 웹 서버(예: Nginx, Apache)에 배포하거나, 백엔드 서버에서 정적 파일을 서빙하도록 설정합니다.

---

## 오프라인 환경에서 프런트엔드 의존성 설치

프런트엔드 개발 환경에서 인터넷 연결이 불가능한 경우, 다음 단계를 따라 의존성을 설치할 수 있습니다.

1.  **온라인 환경에서 의존성 번들 생성:**
    *   인터넷에 연결된 개발 환경에서 `web-dashboard/frontend` 디렉토리로 이동합니다.
    *   `npm install`을 실행하여 모든 의존성을 설치하고 `package-lock.json` 파일을 생성합니다.
    *   `npm pack` 또는 `npm-bundle`과 같은 도구를 사용하여 프로젝트의 모든 의존성을 하나의 아카이브 파일로 묶습니다. (예: `npm-bundle` 사용 시 `npm bundle`)

2.  **오프라인 환경으로 번들 전송:**
    *   생성된 의존성 번들 파일 (예: `project-name-1.0.0.tgz` 또는 `bundle.tar.gz`)을 오프라인 개발 환경의 `web-dashboard/frontend` 디렉토리로 전송합니다.

3.  **오프라인 환경에서 의존성 설치:**
    *   오프라인 개발 환경에서 `web-dashboard/frontend` 디렉토리로 이동합니다.
    *   전송된 번들 파일을 사용하여 의존성을 설치합니다. (예: `npm install ./project-name-1.0.0.tgz` 또는 `npm unbundle` 후 `npm install`)

**참고:** `react-markdown`과 같이 새로운 패키지를 추가하는 경우, 해당 패키지는 온라인 환경에서 먼저 `npm install react-markdown`을 실행하여 캐시에 저장하거나, 패키지 파일을 직접 다운로드하여 로컬에 준비해두는 과정이 필요합니다. `npm install` 명령은 인터넷 연결이 필요합니다.

---

## 🤖 LLM 보강 기능 상세 가이드

Source Analyzer는 LLM을 활용하여 낮은 신뢰도를 가진 메타데이터를 자동으로 보강하는 기능을 제공합니다.

### LLM 설정 파라미터 상세 설명

LLM 보강 기능은 `config/phase1/config.yaml`의 `llm_assist` 섹션에서 설정할 수 있습니다:

```yaml
llm_assist:
  enabled: true                    # LLM 보강 기능 활성화 여부
  provider: "auto"                 # LLM 제공자 선택
  low_conf_threshold: 0.6          # 보강 대상 신뢰도 임계값
  max_calls_per_run: 50            # 실행당 최대 LLM 호출 횟수
  file_max_lines: 1200             # LLM 처리 파일 최대 라인 수
  temperature: 0.0                 # LLM 응답 창의성 조절
  max_tokens: 512                  # 응답 최대 토큰 수
  strict_json: true                # 엄격한 JSON 형식 요구
  cache: true                      # 응답 캐싱 활성화
  cache_dir: "./output/llm_cache"  # 캐시 저장 디렉토리
  dry_run: false                   # 드라이 런 모드
  fallback_to_ollama: true         # vLLM 실패 시 Ollama 대체
```

### 파라미터별 효과 및 사용 사례

#### 1. **provider (LLM 제공자)**
- **auto**: 사용 가능한 첫 번째 제공자 자동 선택
- **ollama**: Ollama 서버 사용 (로컬 모델)
- **vllm**: vLLM 서버 사용 (고성능)
- **openai**: OpenAI 호환 엔드포인트 사용

**사용 사례**:
```yaml
# 로컬 환경에서 빠른 테스트
provider: "ollama"

# 고성능 운영 환경
provider: "vllm"
```

#### 2. **low_conf_threshold (신뢰도 임계값)**
- **0.6**: 60% 미만 신뢰도 파일만 보강 (기본값)
- **0.8**: 80% 미만 파일 보강 (더 많은 보강)
- **0.4**: 40% 미만 파일만 보강 (선택적 보강)

**효과**:
- 낮은 값: 확실히 필요한 경우만 보강 → 빠른 처리
- 높은 값: 더 많은 파일 보강 → 높은 품질, 느린 처리

#### 3. **temperature (창의성 조절)**
- **0.0**: 완전히 결정적, 일관된 응답 (권장)
- **0.1**: 매우 보수적, 약간의 변화
- **0.5**: 균형잡힌 응답
- **1.0**: 창의적이지만 불안정한 응답

**사용 사례**:
```yaml
# 정확한 메타데이터 추출 (권장)
temperature: 0.0

# 다양한 설명이 필요한 경우
temperature: 0.3
```

#### 4. **max_calls_per_run (호출 횟수 제한)**
- **50**: 기본값, 중간 크기 프로젝트에 적합
- **20**: 빠른 처리 우선, 작은 프로젝트
- **100**: 대규모 프로젝트, 시간 여유 있는 경우

**효과**: 처리 시간과 비용 제어

#### 5. **file_max_lines (파일 크기 제한)**
- **1200**: 기본값, 대부분의 파일 처리 가능
- **800**: 빠른 처리, 메모리 절약
- **2000**: 큰 파일도 포함, 느린 처리

### 성능 최적화 시나리오

#### 시나리오 1: 빠른 처리 우선
```yaml
llm_assist:
  enabled: true
  provider: "ollama"
  low_conf_threshold: 0.4      # 정말 필요한 경우만
  max_calls_per_run: 20        # 적은 호출
  file_max_lines: 800          # 작은 파일만
  temperature: 0.0             # 빠른 응답
  max_tokens: 256              # 짧은 응답
  cache: true                  # 캐시 활용
```

#### 시나리오 2: 품질 우선
```yaml
llm_assist:
  enabled: true
  provider: "vllm"
  low_conf_threshold: 0.7      # 더 많은 보강
  max_calls_per_run: 100       # 충분한 호출
  file_max_lines: 1500         # 큰 파일 처리
  temperature: 0.0             # 정확한 응답
  max_tokens: 1024             # 상세한 응답
  cache: true                  # 재사용 효율성
```

#### 시나리오 3: 개발/테스트 환경
```yaml
llm_assist:
  enabled: true
  provider: "auto"
  dry_run: true                # 실제 호출 없음
  log_prompt: true             # 디버깅용 로그
  cache: false                 # 항상 최신 결과
```

### LLM 보강 결과 확인

보강 작업의 결과는 다음과 같은 방법으로 확인할 수 있습니다:

```bash
# 보강 로그 확인
cat logs/analyzer.log | grep "LLM assist"

# 신뢰도 변화 확인 
# Windows
run_analyzer.bat --confidence-report confidence_report.json

# Linux/Mac
./run_analyzer.sh --confidence-report confidence_report.json

# 캐시 사용량 확인
ls -la output/llm_cache/
```

---

## 🚀 빠른 시작 예시

### 1. 프로젝트 분석 실행

```bash
# 프로젝트명을 지정하여 분석을 실행합니다.
# 프로젝트 파일들은 ./project/<프로젝트명>/src/ 디렉토리에 위치해야 합니다.
```bash
# Windows
run_analyzer.bat --project-name sampleSrc

# Linux/Mac
./run_analyzer.sh --project-name sampleSrc
```

# --all 옵션으로 분석과 시각화를 한번에 실행
run_analyzer.bat --project-name sampleSrc --all

# 메타데이터를 Markdown 보고서로 내보내기 (기본 경로 사용)
run_analyzer.bat --project-name sampleSrc --export-md
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

### 2. 의존성 그래프 시각화 (Mermaid Markdown)

```bash
# 프로젝트 ID 1번의 의존성 그래프를 Mermaid Markdown으로 내보냅니다.
# 출력 파일은 ./output/<프로젝트명>/visualize/ 디렉토리에 저장됩니다.
python visualize/cli.py graph --project-name sampleSrc --export-mermaid dependency_graph.md
```

### 3. ERD 시각화 (Mermaid Markdown)

```bash
# 프로젝트 ID 1번의 ERD를 Mermaid Markdown으로 내보냅니다.
# 출력 파일은 ./output/<프로젝트명>/visualize/ 디렉토리에 저장됩니다.
python visualize/cli.py erd --project-name sampleSrc --export-mermaid erd.md
```

## 🌐 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **config.yaml 설정**: `server` 섹션을 통한 서버 설정 및 CORS 제어.
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

---

자세한 내부 구조, 데이터 모델, 상세 오프라인 설치 절차 및 트러블슈팅 가이드는 `README_detailed.md`를 참고하세요.