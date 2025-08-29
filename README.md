# Source Analyzer - 프로젝트 개요 및 빠른 시작 가이드

Source Analyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. 코드의 메타데이터를 추출하여 다양한 다이어그램(의존성 그래프, ERD, 컴포넌트, 클래스, 시퀀스 다이어그램)을 생성하며, 이를 JSON, CSV, Markdown(Mermaid), HTML 형식으로 내보낼 수 있습니다. 폐쇄망 환경에 최적화되어 설계되었으며, 내장된 OWASP 및 CWE 취약점 문서를 통해 보안 분석 및 가이드도 제공합니다.

## 🚀 주요 기능

*   **정적 코드 분석**: Java 클래스/메서드, JSP/MyBatis SQL 구문, 파일/모듈 간의 관계 및 의존성 추출.
*   **다양한 시각화**:
    *   **의존성 그래프**: 파일, 클래스, SQL 단위 간의 호출 및 사용 관계.
    *   **ERD (Entity-Relationship Diagram)**: SQL 구문에서 추출된 테이블 및 조인 관계.
    *   **컴포넌트 다이어그램**: 시스템의 주요 컴포넌트 및 그 관계.
    *   **클래스 다이어그램**: Java 클래스의 구조, 상속, 구현 관계.
    *   **시퀀스 다이어그램**: 특정 메서드 호출 흐름 추적.
*   **유연한 내보내기**: 생성된 시각화 데이터를 JSON, CSV, Markdown(Mermaid), HTML 형식으로 내보내어 다양한 문서화 및 공유 요구사항 충족.
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
3.  **의존성 휠(Wheel) 파일 생성**:
    *   `requirements.txt`에 명시된 모든 패키지의 휠 파일을 다운로드하여 오프라인 저장소를 만듭니다.
    ```bash
    .venv/Scripts/pip wheel -r requirements.txt -w wheelhouse/
    ```
    *   **참고**: `web-dashboard`를 사용할 경우 `fastapi`와 `uvicorn`도 `requirements.txt`에 포함되어 있어야 합니다.
4.  **(선택) 웹 대시보드 프런트엔드 준비**:
    *   `web-dashboard/frontend` 디렉토리에서 `npm install` 및 `npm run build`를 실행하여 정적 파일을 미리 빌드합니다. 빌드된 `dist` 폴더를 오프라인 환경으로 가져갑니다.

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
    *   필요한 환경변수(예: `HOST`, `PORT`, `ALLOWED_ORIGINS`)를 설정한 후 백엔드 서버를 실행합니다.
    ```bash
    HOST=0.0.0.0 PORT=8000 ALLOWED_ORIGINS=http://127.0.0.1:3000 .venv/Scripts/python web-dashboard/backend/app.py
    ```
5.  **(선택) 웹 대시보드 프런트엔드 배포**:
    *   사전 빌드된 프런트엔드 정적 파일(`dist` 폴더)을 오프라인 웹 서버(예: Nginx, Apache)에 배포하거나, 백엔드 서버에서 정적 파일을 서빙하도록 설정합니다.

## 🚀 빠른 시작 예시

### 1. 프로젝트 분석 실행

```bash
# 프로젝트 경로를 지정하여 분석을 실행합니다.
# 예시: PROJECT/sampleSrc 디렉토리를 분석
python phase1/src/main.py PROJECT/sampleSrc --project-name "MySampleProject"
```

### 2. 의존성 그래프 시각화 (Mermaid Markdown)

```bash
# 프로젝트 ID 1번의 의존성 그래프를 Mermaid Markdown으로 내보냅니다.
python visualize/cli.py graph --project-id 1 --export-mermaid ./out/dependency_graph.md
```

### 3. ERD 시각화 (Mermaid Markdown)

```bash
# 프로젝트 ID 1번의 ERD를 Mermaid Markdown으로 내보냅니다.
python visualize/cli.py erd --project-id 1 --export-mermaid ./out/erd.md
```

## 🌐 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **환경변수**: `HOST`, `PORT`, `RELOAD`, `ALLOWED_ORIGINS`를 통해 서버 설정 및 CORS 제어.
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

---

자세한 내부 구조, 데이터 모델, 상세 오프라인 설치 절차 및 트러블슈팅 가이드는 `README_detailed.md`를 참고하세요.