# Source Analyzer - 프로젝트 개요 및 빠른 시작 가이드

Source Analyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. 코드의 메타데이터를 추출하여 다양한 다이어그램(의존성 그래프, ERD, 컴포넌트, 클래스, 시퀀스 다이어그램)을 생성하며, 이를 JSON, CSV, Markdown(Mermaid), HTML 형식으로 내보낼 수 있습니다. 폐쇄망 환경에 최적화되어 설계되었으며, 내장된 OWASP 및 CWE 취약점 문서를 통해 보안 분석 및 가이드도 제공합니다.

## 주요 기능

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

## 오프라인 설치 가이드

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

4.  **(선택) 웹 대시보드 프런트엔드 준비**:
    *   `web-dashboard/frontend` 디렉토리에서 `npm install` 및 `npm run build`를 실행하여 정적 파일을 미리 빌드합니다.
    *   빌드된 `dist` 폴더를 오프라인 환경으로 가져갑니다.

### 2. 오프라인 설치 (운영 환경)

1.  **온라인에서 준비한 파일 전송**:
    *   `SourceAnalyzer.git` 프로젝트 폴더 전체와 `wheelhouse/` 디렉토리 (및 선택적으로 `web-dashboard/frontend/dist` 폴더)를 오프라인 환경으로 전송합니다.
2.  **가상 환경 생성 및 pip 업그레이드**:
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -U pip
    ```
3.  **오프라인 의존성 설치**:
    ```bash
    .venv/Scripts/pip install --no-index --find-links wheelhouse -r requirements.txt
    ```

## 사용법 및 CLI 예시

### 1단계: 소스코드 분석 (`run_analyzer.bat`)

소스코드를 분석하여 데이터베이스에 메타데이터를 구축합니다.

```bash
# 기본 분석: sampleSrc 프로젝트를 분석합니다.
# (분석할 소스는 ./project/sampleSrc/src/ 에 위치해야 합니다.)
.un_analyzer.bat --project-name sampleSrc

# 증분 분석: 변경된 파일만 분석하여 시간 단축
.un_analyzer.bat --project-name sampleSrc --incremental

# 분석 후 Markdown 보고서 자동 생성
.un_analyzer.bat --project-name sampleSrc --export-md

# 분석과 모든 시각화 동시 실행
.un_analyzer.bat --project-name sampleSrc --all
```

### 2단계: 시각화 생성 (`run_visualize.bat`)

분석된 데이터를 바탕으로 다양한 다이어그램을 생성합니다. 모든 시각화는 관련 항목들이 인접하게 배치되는 개선된 레이아웃 알고리즘을 사용합니다.

**기본 사용법:**
```bash
# [기본] 모든 시각화 생성
# 아무런 명령어를 지정하지 않으면 'sequence'를 제외한 모든 다이어그램을 생성합니다.
# 결과물은 ./output/sampleSrc/visualize/ 폴더에 HTML 파일로 저장됩니다.
.un_visualize.bat --project-name sampleSrc

# [선택] 특정 시각화만 생성 (예: ERD)
.un_visualize.bat erd --project-name sampleSrc
```

**상세 예시:**

*   **의존성 그래프 (`graph`)**
    ```bash
    # 특정 파일(MyService.java)을 중심으로 1단계 깊이의 의존성 그래프 생성
    .un_visualize.bat graph --project-name sampleSrc --focus MyService.java --depth 1
    ```

*   **ERD (`erd`)**
    ```bash
    # 특정 테이블(USER_INFO, ORDERS)만 포함하는 ERD 생성
    .un_visualize.bat erd --project-name sampleSrc --tables "USER_INFO,ORDERS"
    ```

*   **클래스 다이어그램 (`class`)**
    ```bash
    # 특정 모듈(com/example/user)에 대한 클래스 다이어그램 생성
    .un_visualize.bat class --project-name sampleSrc --modules "com/example/user"
    ```

*   **시퀀스 다이어그램 (`sequence`)**
    ```bash
    # (1) 사용 가능한 시작 파일 목록 확인 (가이드 모드)
    .un_visualize.bat sequence --project-name sampleSrc

    # (2) 확인된 정보를 바탕으로 시퀀스 다이어그램 생성
    .un_visualize.bat sequence --project-name sampleSrc --start-file "com/example/MyController.java" --start-method "myMethod"
    ```

*   **연관성 그래프 (`relatedness`)**
    ```bash
    # 최소 점수 0.6 이상인 관계만 표시
    .un_visualize.bat relatedness --project-name sampleSrc --min-score 0.6

    # 연관성 분석 통계만 확인
    .un_visualize.bat relatedness --project-name sampleSrc --summary
    ```

*   **다양한 출력 옵션**
    ```bash
    # HTML과 Mermaid(.md)로 동시에 출력
    .un_visualize.bat erd --project-name sampleSrc --export-html --export-mermaid

    # 지정된 파일명으로 HTML 출력
    .un_visualize.bat erd --project-name sampleSrc --export-html my_erd.html
    ```

### 시각화 특징

- **개선된 레이아웃**: 모든 시각화는 fcose 물리 시뮬레이션 알고리즘을 기본으로 사용하여 관련성이 높은 요소들이 자동으로 클러스터링됩니다.
- **적응형 간격**: 신뢰도와 관계 강도에 따라 요소 간 거리가 동적으로 조정됩니다.
- **상호작용**: 노드 클릭 시 상세 정보 표시, 더블클릭으로 포커스 이동, 검색 기능 지원.
- **다중 레이아웃**: fcose, cose, circle, grid 레이아웃 간 실시간 전환 가능.

### 출력 파일 위치

모든 시각화 결과는 `./output/{project_name}/visualize/` 폴더에 생성됩니다:
- `graph.html` - 의존성 그래프 (인터랙티브)
- `erd.html` - 엔터티 관계도 (인터랙티브) 
- `class.html` - 클래스 다이어그램 (인터랙티브)
- `component.html` - 컴포넌트 다이어그램 (인터랙티브)
- `*.md` - Mermaid 다이어그램 (Markdown)

    .un_visualize.bat erd --project-name sampleSrc --export-html my_erd.html
    ```

## 웹 대시보드 (선택 사항)

웹 대시보드는 분석 결과를 웹 UI로 조회하고, 오프라인 문서를 API로 제공하는 기능을 합니다.

*   **백엔드 실행**: `python web-dashboard/backend/app.py`
*   **config.yaml 설정**: `server` 섹션을 통한 서버 설정 및 CORS 제어.
*   **오프라인 문서 API**: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}` 엔드포인트를 통해 내장된 취약점 문서에 접근할 수 있습니다.

