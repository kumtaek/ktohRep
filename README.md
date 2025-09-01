# SourceAnalyzer - 통합 소스코드 분석 및 시각화 플랫폼

SourceAnalyzer는 Java, JSP, MyBatis, SQL 코드베이스를 분석하고 시각화하는 강력한 오프라인 도구입니다. **LLM 기반 코드 분석**, **고도화된 대화형 시각화**, **보안 취약점 검출** 기능을 제공하며, 폐쇄망 환경에 최적화되어 설계되었습니다.

## 🚀 주요 기능

### 핵심 분석 엔진
- **소스코드 분석**: Java, JSP, MyBatis, SQL 파일의 메타데이터 자동 추출
- **LLM 기반 분석**: 코드 요약, 테이블 명세, 조인 관계 자동 분석
- **증분 분석**: 변경된 파일만 재분석하여 대규모 프로젝트 처리 최적화
- **신뢰도 평가**: 분석 결과의 정확성을 수치로 제공

### 고도화된 시각화
- **의존성 그래프**: 파일, 클래스, 메서드 간의 호출 및 참조 관계
- **ERD (Enhanced)**: SQL에서 추출된 테이블 관계 + 조인 분석 + 툴팁 상세정보
- **클래스 다이어그램**: Java 클래스 구조, 상속, 구현 관계
- **시퀀스 다이어그램**: 메서드 호출 흐름 + 자동 시작점 발견
- **컴포넌트 다이어그램**: 시스템 아키텍처 구조 분석

### 대화형 UI 기능
- **검색 및 필터링**: 실시간 요소 검색 및 하이라이트
- **레이아웃 전환**: fcose, dagre, circle, grid 알고리즘 지원
- **줌 및 팬**: 마우스 휠 줌, 드래그 이동
- **툴팁 상세정보**: 테이블, 클래스, 메서드 상세 정보 표시
- **포커스 모드**: 특정 요소 중심의 관계 탐색

### 보안 및 품질 관리
- **취약점 검출**: CWE 기반 보안 취약점 자동 탐지
- **OWASP 가이드**: Top 10 취약점별 상세 가이드 및 대응책
- **품질 리포트**: 코드 품질 지표 및 개선 권고사항

## 🏃‍♂️ 빠른 시작

### 1. 환경 설정
```bash
# Python 가상환경 생성 및 활성화
python -m venv venvSrcAnalyzer
venvSrcAnalyzer\Scripts\activate
pip install -r requirements.txt
```

### 2. 원클릭 데모 실행 (권장)
```bash
# 모든 기능을 자동으로 시연
run_quick_demo.bat
```

### 3. 단계별 실행
```bash
# 1단계: 소스코드 분석
run_analyzer.bat sampleSrc

# 2단계: LLM 기반 고급 분석
run_llm_analysis.bat --project-name sampleSrc

# 3단계: 고도화된 시각화 생성
run_enhanced_visualize_only.bat --project-name sampleSrc

# 4단계: 보안 분석 및 문서 생성
run_download_vulnerability_docs.bat --project-name sampleSrc
```

## 📊 시각화 샘플

### ERD (Enhanced) - 개선된 엔터티 관계도
- 테이블 간 조인 관계 자동 분석
- 마우스 오버 시 컬럼 상세정보 표시
- Force-directed 및 Hierarchical 레이아웃 지원

### 의존성 그래프 - 코드 의존성 시각화
- 파일, 클래스, 메서드 수준의 의존관계
- 순환 참조 감지 및 하이라이트
- 신뢰도 기반 엣지 두께 조절

### 시퀀스 다이어그램 - 호출 흐름 추적
- 메서드 호출 순서 자동 추적
- 시작점 자동 발견 기능
- Mermaid 및 HTML 동시 출력

## 🛠️ 주요 스크립트

| 스크립트 | 기능 | 설명 |
|---------|------|------|
| `run_quick_demo.bat` | **전체 데모** | 모든 기능을 한 번에 시연 (권장) |
| `run_complete_analysis.bat` | **통합 분석** | 분석 + LLM + 시각화 일괄 실행 |
| `run_analyzer.bat` | 소스 분석 | 코드 파싱 및 메타데이터 추출 |
| `run_llm_analysis.bat` | LLM 분석 | 코드 요약 및 명세서 생성 |
| `run_enhanced_visualize_only.bat` | **고도화 시각화** | 개선된 UI/UX 시각화 생성 |
| `run_download_vulnerability_docs.bat` | 보안 문서 | 취약점 보고서 및 OWASP 가이드 |

## 📁 출력 구조

```
output/{project_name}/
├── visualize/                    # 시각화 파일
│   ├── erd.html                 # ERD (대화형)
│   ├── graph.html               # 의존성 그래프
│   ├── class.html               # 클래스 다이어그램
│   ├── sequence.html            # 시퀀스 다이어그램
│   └── *.md                     # Mermaid 다이어그램
├── vulnerability_docs/           # 보안 문서
│   ├── 취약점보고서.md          # 종합 보안 분석 보고서
│   ├── OWASP_도움말.md          # OWASP Top 10 가이드
│   └── CWE-*.md                 # 개별 취약점 분석
├── 소스코드명세서.md            # LLM 생성 코드 명세
└── 소스명세서.md                # 프로젝트 요약 문서
```

## 🎯 고급 기능

### LLM 기반 분석 (Claude, GPT 지원)
```bash
# 코드 요약 생성
run_summarize.bat sampleSrc

# 테이블 조인 관계 분석
run_analyze_joins.bat sampleSrc

# 테이블 명세서 자동 생성
"venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py table-spec --project-name sampleSrc
```

### 고급 시각화 옵션
```bash
# 특정 테이블만 ERD 생성
run_visualize.bat erd --project-name sampleSrc --tables "USER_INFO,ORDERS"

# 특정 파일 중심 의존성 그래프
run_visualize.bat graph --project-name sampleSrc --focus MyService.java --depth 2

# 자동 시퀀스 다이어그램 생성
run_auto_sequence.bat sampleSrc
```

### 보안 분석
```bash
# 취약점 검출 실행
run_analyzer.bat sampleSrc --security-scan

# 보안 문서 생성
run_download_vulnerability_docs.bat sampleSrc
```

## 🔧 환경 요구사항

### 필수 요구사항
- **Python 3.10+**: 메인 분석 엔진
- **메모리**: 최소 4GB RAM (대규모 프로젝트 시 8GB+ 권장)
- **디스크**: 프로젝트 크기의 2-3배 여유 공간

### 선택 요구사항
- **LLM API**: Claude 3.5 Sonnet 또는 GPT-4 (config.yaml 설정 필요)
- **Node.js 18+**: 웹 대시보드 사용 시

## 🌟 새로운 기능 (v2.0+)

### 1. 고도화된 ERD
- **조인 관계선**: SQL 분석 결과 기반 자동 연결
- **상세 툴팁**: 테이블/컬럼 정보 마우스오버 표시
- **레이아웃 최적화**: Force-directed와 Hierarchical 전환

### 2. LLM 통합 분석
- **자동 요약**: 코드 기능 및 구조 자연어 설명
- **테이블 명세**: 데이터베이스 스키마 자동 문서화
- **조인 추론**: MyBatis SQL에서 테이블 관계 자동 추출

### 3. 보안 강화
- **CWE 매핑**: 코드 패턴 기반 취약점 자동 검출
- **OWASP 가이드**: 오프라인 환경용 보안 가이드 내장
- **취약점 보고서**: 발견된 이슈의 우선순위 및 해결 방안

### 4. 성능 최적화
- **증분 분석**: 변경 파일만 재처리로 10배 빠른 분석
- **병렬 처리**: 멀티코어 CPU 활용 최적화
- **메모리 관리**: 대용량 프로젝트 처리 개선

## 🏗️ 아키텍처

```
SourceAnalyzer/
├── phase1/                      # 핵심 분석 엔진
│   ├── parsers/                # Java, JSP, SQL 파서
│   ├── llm/                    # LLM 통합 모듈
│   └── tools/                  # CLI 도구
├── visualize/                   # 시각화 엔진
│   ├── builders/               # 다이어그램 생성기
│   ├── renderers/              # HTML 렌더러
│   └── templates/              # UI 템플릿
├── config/                      # 설정 파일
├── testcase/                    # 테스트 케이스
└── output/                      # 분석 결과 출력
```

## 🤝 활용 사례

### 1. 레거시 시스템 분석
- 기존 Java/JSP 프로젝트의 구조 파악
- 데이터베이스 스키마 리버스 엔지니어링
- 컴포넌트 간 의존성 분석

### 2. 시스템 리팩토링
- 순환 참조 및 강결합 구간 식별
- 모듈화 전략 수립
- API 설계 가이드 제공

### 3. 보안 감사
- 코드 수준 취약점 자동 검출
- OWASP Top 10 기준 보안 점검
- 개발팀 보안 교육 자료 생성

### 4. 문서화 자동화
- 시스템 아키텍처 문서 자동 생성
- API 명세서 추출
- 데이터베이스 스키마 문서화

## 📚 참고 문서

- **[QuickStart.md](QuickStart.md)**: 빠른 시작 가이드
- **[README_detailed.md](README_detailed.md)**: 상세 사용법 및 옵션
- **[구현설명.md](구현설명.md)**: 시스템 아키텍처 및 구현 세부사항
- **[실행스크립트.md](실행스크립트.md)**: 배치 스크립트 상세 설명

## 🔗 지원 및 피드백

SourceAnalyzer는 지속적으로 발전하고 있는 프로젝트입니다. 사용 중 문제점이나 개선 요청사항이 있으시면:

1. **이슈 리포팅**: GitHub Issues를 통한 버그 리포트
2. **기능 제안**: 새로운 기능에 대한 아이디어 제안
3. **문서 개선**: 사용법 문서의 오탈자나 설명 부족 부분 제보

**폐쇄망 환경 최적화** - 인터넷 연결 없이도 완전한 기능 제공