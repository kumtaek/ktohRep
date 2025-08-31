# SourceAnalyzer 빠른 시작 가이드

SourceAnalyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. 이 가이드는 SourceAnalyzer를 사용하여 코드 분석 및 시각화를 빠르게 시작하는 방법을 설명합니다.

## 사전 준비

1.  **Python 3.10+ 설치**:
    *   SourceAnalyzer는 Python 3.10 이상 버전에서 동작합니다. 시스템에 Python이 설치되어 있는지 확인하십시오.

## 설치

프로젝트 파일이 준비된 환경에서 다음 단계를 따릅니다.

1.  **가상 환경 생성 및 의존성 설치**:
    ```bash
    python -m venv venvSrcAnalyzer
    .\venvSrcAnalyzer\Scripts\activate
    pip install -r requirements.txt
    ```
    *   이 명령은 프로젝트에 필요한 모든 Python 라이브러리를 설치합니다.

## 사용법 및 CLI 예시

**참고**: 모든 명령줄 인자에 대한 상세 설명은 `README_detailed.md`를 참조하십시오.

### 1단계: 소스코드 분석 (`run_analyzer.bat`)

소스코드를 분석하여 데이터베이스에 메타데이터를 구축합니다.

```bash
# 기본 분석: sampleSrc 프로젝트를 분석합니다.
# (분석할 소스는 ./project/sampleSrc/src/ 에 위치해야 합니다.)
.\run_analyzer.bat --project-name sampleSrc

# 증분 분석: 변경된 파일만 분석하여 시간 단축
.\run_analyzer.bat --project-name sampleSrc --incremental

# 분석 후 Markdown 보고서 자동 생성
.\run_analyzer.bat --project-name sampleSrc --export-md

# 분석과 모든 시각화 동시 실행
.\run_analyzer.bat --project-name sampleSrc --all
```

### 2단계: 시각화 생성 (`run_visualize.bat`)

분석된 데이터를 바탕으로 다양한 다이어그램을 생성합니다.

**기본 사용법:**
```bash
# [기본] 모든 시각화 생성
# 아무런 명령어를 지정하지 않으면 'sequence'를 제외한 모든 다이어그램을 생성합니다.
# 결과물은 ./output/sampleSrc/visualize/ 폴더에 HTML 파일로 저장됩니다.
.\run_visualize.bat --project-name sampleSrc

# [선택] 특정 시각화만 생성 (예: ERD)
.\run_visualize.bat erd --project-name sampleSrc
```

**상세 예시:**

*   **의존성 그래프 (`graph`)**
    ```bash
    # 특정 파일(MyService.java)을 중심으로 1단계 깊이의 의존성 그래프 생성
    .\run_visualize.bat graph --project-name sampleSrc --focus MyService.java --depth 1
    ```

*   **ERD (`erd`)**
    ```bash
    # 특정 테이블(USER_INFO, ORDERS)만 포함하는 ERD 생성
    .\run_visualize.bat erd --project-name sampleSrc --tables "USER_INFO,ORDERS"
    ```

*   **클래스 다이어그램 (`class`)**
    ```bash
    # 특정 모듈(com/example/user)에 대한 클래스 다이어그램 생성
    .\run_visualize.bat class --project-name sampleSrc --modules "com/example/user"
    ```

*   **시퀀스 다이어그램 (`sequence`)**
    ```bash
    # (1) 사용 가능한 시작 파일 목록 확인 (가이드 모드)
    .\run_visualize.bat sequence --project-name sampleSrc

    # (2) 확인된 정보를 바탕으로 시퀀스 다이어그램 생성
    .\run_visualize.bat sequence --project-name sampleSrc --start-file "com/example/MyController.java" --start-method "myMethod"
    ```

*   **연관성 그래프 (`relatedness`)**
    ```bash
    # 최소 점수 0.6 이상인 관계만 표시
    .\run_visualize.bat relatedness --project-name sampleSrc --min-score 0.6

    # 연관성 분석 통계만 확인
    .\run_visualize.bat relatedness --project-name sampleSrc --summary
    ```

*   **다양한 출력 옵션**
    ```bash
    # HTML과 Mermaid(.md)로 동시에 출력
    .\run_visualize.bat erd --project-name sampleSrc --export-html --export-mermaid

    # 지정된 파일명으로 HTML 출력
    .\run_visualize.bat erd --project-name sampleSrc --export-html my_erd.html
    ```

## 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **설정**: 웹 대시보드 백엔드 서버의 모든 설정(호스트, 포트, CORS 등)은 `config/config.yaml` 파일의 `server` 섹션에서 관리됩니다.
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

## 다음 단계 및 추가 정보

더 자세한 내부 구조, 데이터 모델, 상세 오프라인 설치 절차 및 트러블슈팅 가이드는 `README_detailed.md`를 참고하세요.
