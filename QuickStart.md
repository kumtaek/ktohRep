# SourceAnalyzer 빠른 시작 가이드

SourceAnalyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. LLM 기반 코드 분석, 고도화된 시각화, 보안 취약점 검출 기능을 제공합니다.

## 주요 기능
- **소스코드 분석**: Java, JSP, MyBatis, SQL 파일 파싱 및 메타데이터 추출
- **LLM 기반 분석**: 코드 요약, 테이블 명세, 조인 관계 자동 분석
- **고도화된 시각화**: ERD, 클래스 다이어그램, 의존성 그래프, 시퀀스 다이어그램
- **보안 분석**: 취약점 검출 및 OWASP 가이드 제공
- **대화형 UI**: 검색, 필터링, 줌, 레이아웃 전환 기능

## 사전 준비

1. **Python 3.10+ 설치**:
   - SourceAnalyzer는 Python 3.10 이상 버전에서 동작합니다.

## 설치

프로젝트 파일이 준비된 환경에서 다음 단계를 따릅니다.

1. **가상 환경 생성 및 의존성 설치**:
   ```bash
   python -m venv venvSrcAnalyzer
   .\venvSrcAnalyzer\Scripts\activate
   pip install -r requirements.txt
   ```

## 빠른 시작 - 원클릭 데모

가장 빠르게 SourceAnalyzer를 체험하려면:

```bash
# 모든 기능을 자동으로 시연하는 데모 스크립트
run_quick_demo.bat
```

이 명령어는 다음을 자동으로 실행합니다:
1. 샘플 프로젝트 분석
2. LLM 기반 요약 생성
3. 모든 시각화 생성
4. 결과 파일 확인

## 사용법 및 CLI 예시

**참고**: 모든 명령줄 인자에 대한 상세 설명은 `README_detailed.md`를 참조하십시오.

### 1단계: 소스코드 분석

소스코드를 분석하여 데이터베이스에 메타데이터를 구축합니다.

```bash
# 기본 분석: sampleSrc 프로젝트를 분석합니다.
# (분석할 소스는 ./testcase/sampleSrc/ 에 위치해야 합니다.)
run_analyzer.bat sampleSrc

# 증분 분석: 변경된 파일만 분석하여 시간 단축
run_analyzer.bat sampleSrc --incremental

# 통합 분석: 분석 + LLM 처리 + 시각화를 한 번에 실행
run_complete_analysis.bat sampleSrc
```

### 2단계: LLM 기반 고급 분석

```bash
# LLM 기반 코드 요약 및 테이블/컬럼 주석 생성
run_llm_analysis.bat sampleSrc

# 코드 요약만 실행
run_summarize.bat sampleSrc

# 테이블 조인 관계 분석
run_analyze_joins.bat sampleSrc
```

### 3단계: 시각화 생성

분석된 데이터를 바탕으로 다양한 다이어그램을 생성합니다.

**기본 사용법:**
```bash
# 모든 시각화 생성 (고도화 버전)
run_enhanced_visualize_only.bat sampleSrc

# 특정 시각화만 생성 (예: ERD)
run_visualize.bat erd sampleSrc

# 그래프만 생성
run_visualize.bat graph sampleSrc
```

**상세 예시:**

- **의존성 그래프 (`graph`)**
  ```bash
  # 특정 파일을 중심으로 의존성 그래프 생성
  # 특정 파일을 중심으로 의존성 그래프 생성
run_visualize.bat graph sampleSrc --focus MyService.java --depth 1
  ```

- **ERD (`erd`)**
  ```bash
  # 특정 테이블만 포함하는 ERD 생성
  run_visualize.bat erd --project-name sampleSrc --tables "USER_INFO,ORDERS"
  ```

- **클래스 다이어그램 (`class`)**
  ```bash
  # 특정 모듈에 대한 클래스 다이어그램 생성
  run_visualize.bat class sampleSrc --modules "com/example/user"
  ```

- **시퀀스 다이어그램 (`sequence`)**
  ```bash
  # 자동 시퀀스 다이어그램 생성
  run_auto_sequence.bat sampleSrc
  
  # 특정 메서드 호출 흐름 추적
  run_visualize.bat sequence --project-name sampleSrc --start-file "com/example/MyController.java" --start-method "myMethod"
  ```

### 4단계: 보안 분석

```bash
# 취약점 보고서 및 OWASP 가이드 생성
run_download_vulnerability_docs.bat sampleSrc
```

## 고급 기능

### 시각화 특징
- **개선된 레이아웃**: fcose 물리 시뮬레이션 알고리즘으로 관련성 높은 요소들이 자동 클러스터링
- **적응형 간격**: 신뢰도와 관계 강도에 따라 요소 간 거리가 동적으로 조정
- **상호작용**: 노드 클릭으로 상세 정보 확인, 더블클릭으로 포커스 이동, 검색 기능
- **다중 레이아웃**: fcose, cose, circle, grid 레이아웃 간 실시간 전환 가능

### 출력 파일 위치

모든 결과는 `./output/{project_name}/` 폴더에 생성됩니다:

#### 시각화 파일 (`visualize/`)
- `graph.html` - 의존성 그래프 (대화형)
- `erd.html` - 엔터티 관계도 (대화형)
- `class.html` - 클래스 다이어그램 (대화형)
- `sequence.html` - 시퀀스 다이어그램 (대화형)
- `*.md` - Mermaid 다이어그램 (마크다운)

#### 문서 파일
- `소스코드명세서.md` - 코드 구조 및 기능 명세
- `소스명세서.md` - 전체 프로젝트 요약

#### 보안 문서 (`vulnerability_docs/`)
- `취약점보고서.md` - 발견된 취약점 분석 보고서
- `OWASP_도움말.md` - OWASP Top 10 기반 보안 가이드
- `CWE-*.md` - 개별 취약점별 상세 분석

## 주요 실행 스크립트 요약

| 스크립트 | 기능 |
|---------|------|
| `run_quick_demo.bat` | 전체 기능 데모 (권장) |
| `run_analyzer.bat` | 소스코드 분석 |
| `run_complete_analysis.bat` | 통합 분석 실행 |
| `run_llm_analysis.bat` | LLM 기반 분석 |
| `run_enhanced_visualize_only.bat` | 고도화된 시각화 생성 |
| `run_download_vulnerability_docs.bat` | 보안 문서 생성 |

## 문제 해결

일반적인 문제와 해결 방법:

1. **가상환경 오류**: `venvSrcAnalyzer` 디렉토리 확인
2. **설정 파일 없음**: `config/config.yaml` 파일 존재 여부 확인
3. **소스 파일 없음**: `testcase/sampleSrc/` 디렉토리에 분석할 소스코드 배치
4. **Python 버전**: Python 3.10 이상 사용

더 자세한 사용법은 `README_detailed.md`를 참조하세요. 참조하세요.