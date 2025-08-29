# Source Analyzer (소스 분석기) - 요약 버전

## 1. 프로젝트 개요

Source Analyzer는 소스 코드의 메타정보를 추출하고 분석하여 시스템 구조와 의존성을 이해하는 데 도움을 주는 도구입니다. 특히, LLM(Large Language Model)을 활용하여 분석 결과의 정확성을 개선하는 것을 목표로 합니다.

### 주요 기능
*   **다국어 파싱**: Java, JSP/MyBatis, SQL 등 다양한 소스 코드 파싱.
*   **메타정보 추출**: 클래스, 메서드, SQL 구문, 의존성 등 핵심 메타정보 생성.
*   **신뢰도 측정**: 분석 결과에 대한 신뢰도 점수 부여.
*   **증분 분석**: 변경된 파일만 효율적으로 재분석.
*   **코드 시각화**: 분석된 메타데이터를 다양한 다이어그램으로 시각화.

### 향후 계획
*   LLM 기반 코드 분석 및 설명 강화.
*   벡터 스토어를 활용한 코드 검색 및 추천.
*   분석 결과를 제공하는 웹 API 및 UI 개발.

## 2. 설치 및 실행

### 2.1. 환경 설정
1.  Python 3.x 환경을 준비합니다.
2.  프로젝트 루트에서 다음 명령어로 필수 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

### 2.2. 설정 파일 및 DB 스키마 준비
*   `config/config.yaml`: 데이터베이스, 파서, 파일 필터링 등 핵심 설정을 프로젝트에 맞게 수정합니다.
*   `DB_SCHEMA` 디렉토리: 데이터베이스 테이블 및 컬럼 정보를 담은 CSV 파일들을 준비합니다.

### 2.3. 소스 분석기 실행
`main.py` 스크립트를 실행하여 프로젝트를 분석합니다.

```bash
python phase1/src/main.py [분석할_프로젝트_경로] [옵션]
```

**예시:**
```bash
# 'PROJECT/sampleSrc' 디렉토리를 분석
python phase1/src/main.py PROJECT/sampleSrc

# 증분 분석 모드로 실행
python phase1/src/main.py PROJECT/sampleSrc --incremental
```

## 3. 시각화

`visualize/cli.py` 스크립트를 통해 분석된 메타데이터를 다양한 다이어그램으로 시각화할 수 있습니다. 생성된 다이어그램은 HTML 웹 페이지 또는 Mermaid Markdown 형식으로 내보낼 수 있습니다.

### 지원 다이어그램
*   **의존성 그래프**: 파일, 클래스, 메서드 간의 호출 및 사용 관계.
*   **ERD (Entity-Relationship Diagram)**: 데이터베이스 테이블 및 관계.
*   **컴포넌트 다이어그램**: 시스템의 주요 컴포넌트 및 상호작용.
*   **시퀀스 다이어그램**: 특정 호출 흐름에 대한 시퀀스.
*   **클래스 다이어그램**: Python 코드의 클래스 구조, 멤버, 상속 관계.

**예시:**
```bash
# 프로젝트 ID 1번의 의존성 그래프를 'output/dependency_graph.html'로 저장
python visualize/cli.py graph --project-id 1 --out output/dependency_graph.html

# 프로젝트 ID 1번의 ERD를 Mermaid Markdown으로 내보내기
python visualize/cli.py erd --project-id 1 --out output/erd.html --export-mermaid output/erd.md
```
