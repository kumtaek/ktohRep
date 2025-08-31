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
.un_analyzer.bat --project-name sampleSrc

# 증분 분석: 변경된 파일만 분석하여 시간 단축
.un_analyzer.bat --project-name sampleSrc --incremental

# 분석 후 Markdown 보고서 자동 생성
.un_analyzer.bat --project-name sampleSrc --export-md

# 분석과 모든 시각화 동시 실행
.un_analyzer.bat --project-name sampleSrc --all

# LLM 기반 코드 요약 및 테이블/컬럼 주석 생성
.un_llm_analysis.bat --project-name sampleSrc
```

### 2단계: 시각화 생성 (`run_visualize.bat`)

분석된 데이터를 바탕으로 다양한 다이어그램을 생성합니다. 모든 시각화는 관련 항목들이 인접하게 배치되는 개선된 레이아웃 알고리즘을 사용하며, 적절한 간격으로 배치되어 가독성이 향상되었습니다.

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

*   **시퀀스 다이어그램 (`sequence`)**: 특정 메서드 호출 흐름 추적 및 자동 시작점 발견 및 폴백 다이어그램 생성 기능 포함.
    ```bash
    # (1) 사용 가능한 시작 파일 목록 확인 (가이드 모드)
    .\run_visualize.bat sequence --project-name sampleSrc

    # (2) 확인된 정보를 바탕으로 시퀀스 다이어그램 생성
    .\run_visualize.bat sequence --project-name sampleSrc --start-file "com/example/MyController.java" --start-method "myMethod"
    ```

*   **자동 시퀀스 다이어그램 생성 (`run_auto_sequence.bat`)**
    ```bash
    # 기본 실행 (sampleSrc 프로젝트)
    .\run_auto_sequence.bat sampleSrc

    # 특정 프로젝트 실행
    .\run_auto_sequence.bat [프로젝트명]
    ```

*   **조인 관계 분석 (`run_analyze_joins.bat`)**
    ```bash
    # 기본 실행 (sampleSrc 프로젝트)
    .\run_analyze_joins.bat sampleSrc

    # 특정 프로젝트 실행
    .\run_analyze_joins.bat [프로젝트명]
    ```

*   **관계 분석 (`run_relationships.bat`)**
    ```bash
    # 기본 실행 (sampleSrc 프로젝트)
    .\run_relationships.bat sampleSrc

    # 특정 프로젝트 실행
    .\run_relationships.bat [프로젝트명]
    ```

*   **LLM 요약 생성 (`run_summarize.bat`)**
    ```bash
    # 기본 실행 (sampleSrc 프로젝트)
    .\run_summarize.bat --project-name sampleSrc

    # 특정 프로젝트 실행
    .\run_summarize.bat --project-name [프로젝트명]
    ```

*   **연관성 시각화 예시 (`run_visualize_relatedness_example.bat`)**
    ```bash
    # 기본 실행 (sampleSrc 프로젝트)
    .\run_visualize_relatedness_example.bat sampleSrc

    # 특정 프로젝트 실행
    .\run_visualize_relatedness_example.bat [프로젝트명]
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

### 시각화 특징

- **개선된 레이아웃**: fcose 물리 시뮬레이션 알고리즘으로 관련성 높은 요소들이 자동 클러스터링됩니다.
- **적응형 간격**: 신뢰도와 관계 강도에 따라 요소 간 거리가 동적으로 조정됩니다.
- **상호작용**: 노드 클릭으로 상세 정보 확인, 더블클릭으로 포커스 이동, 검색 기능 지원.
- **다중 레이아웃**: fcose, cose, circle, grid 레이아웃 간 실시간 전환 가능.

### 출력 파일 위치

모든 시각화 결과는 `./output/{project_name}/visualize/` 폴더에 생성됩니다:
- `graph.html` - 의존성 그래프 (인터랙티브)
- `erd.html` - 엔터티 관계도 (인터랙티브)
- `class.html` - 클래스 다이어그램 (인터랙티브)
- `component.html` - 컴포넌트 다이어그램 (인터랙티브)
- `sequence.html` - 시퀀스 다이어그램 (인터랙티브)
- `relatedness.html` - 연관성 그래프 (인터랙티브)
- `*.md` - Mermaid 다이어그램 (Markdown)
- `table_specification.md` - 테이블 사양 (Markdown)
- `auto_sequence_*.json` - 자동 생성 시퀀스 다이어그램 (JSON)
- `auto_sequence_*.md` - 자동 생성 시퀀스 다이어그램 (Markdown)
- `auto_sequence_index.html` - 자동 생성 시퀀스 다이어그램 인덱스 (HTML)
