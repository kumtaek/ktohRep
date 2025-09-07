# SourceAnalyzer HTML 리포트 생성 가이드

## 개요
SourceAnalyzer는 이제 2가지 형태의 HTML 리포트를 별도로 생성할 수 있습니다:
1. **ERD (Entity Relationship Diagram)** - 데이터베이스 구조 분석
2. **시스템 아키텍처** - 컴포넌트 구조 및 관계 분석

## 실행 스크립트

### 1. ERD HTML 리포트 생성
```bash
python generate_erd_html.py
```

**생성되는 내용:**
- 데이터베이스 테이블 구조 다이어그램 (Mermaid)
- 테이블별 상세 정보 (컬럼, Primary Key, Foreign Key)
- 테이블 간 관계 분석 (JOIN 관계)
- 확대/축소/드래그 기능
- SVG 다운로드 기능

**출력 파일:** `./project/sampleSrc/report/erd_mermaid_[timestamp].html`

### 2. 아키텍처 HTML 리포트 생성
```bash
python generate_architecture_html.py
```

**생성되는 내용:**
- 시스템 아키텍처 구조 다이어그램 (계층별 Mermaid)
- 컴포넌트 관계 분석 (의존성, 구현, 호출 관계)
- 구성 요소 통계 테이블
- 확대/축소/드래그 기능
- SVG 다운로드 기능

**출력 파일:** `./project/sampleSrc/report/architecture_mermaid_[timestamp].html`

### 3. 통합 리포트 생성 (기존)
```bash
python test_reports_auto.py
```

**생성되는 내용:**
- 텍스트 리포트 (ERD, Architecture, Visual, Combined)
- HTML 리포트 (통합 버전)

## 특징

### 화면 레이아웃 최적화
- **컨테이너 폭:** 1400px (넓은 화면 활용)
- **반응형 디자인:** 윈도우 크기에 맞춰 자동 조정
- **여백 최소화:** 컨텐츠 영역 최대 활용

### 오프라인 환경 완전 지원
- 외부 CDN 의존성 없음
- 로컬 Mermaid JavaScript 라이브러리 내장
- 폐쇄망에서도 정상 동작

### 인터랙티브 다이어그램
- Mermaid를 활용한 다이어그램 생성
- 확대/축소/드래그 기능
- SVG 다운로드 기능
- 브라우저 호환성 최대화

## 파일 구조
```
E:\SourceAnalyzer.git\
├── generate_erd_html.py                    # ERD HTML 생성 스크립트
├── generate_architecture_html.py           # 아키텍처 HTML 생성 스크립트
├── parsers/mermaid_html_reporter.py        # Mermaid 기반 HTML 리포터
├── static/mermaid.min.js                   # 오프라인용 Mermaid JavaScript
└── project/sampleSrc/report/               # HTML 출력 디렉토리
    ├── erd_mermaid_[timestamp].html        # ERD 리포트
    └── architecture_mermaid_[timestamp].html # 아키텍처 리포트
```

## 실행 예시

### ERD 리포트 생성
```
ERD HTML 리포트 생성기
==================================================
메타데이터 엔진 초기화 중...

1단계: 테이블 메타데이터 수집
------------------------------
CSV 테이블: 5개
JOIN 관계: 15개

2단계: ERD HTML 리포트 생성
------------------------------
[OK] ERD HTML 리포트 생성 완료!
   파일 위치: ./project/sampleSrc/report/erd_mermaid_20250907_110400.html
   테이블: 5개
   JOIN 관계: 15개
   파일 크기: 28,815 bytes

브라우저에서 확인: file:///E:\SourceAnalyzer.git\project\sampleSrc\report\erd_mermaid_20250907_110400.html
```

### 아키텍처 리포트 생성
```
아키텍처 HTML 리포트 생성기
==================================================
메타데이터 엔진 초기화 중...

1단계: 메타데이터 수집
------------------------------
CSV 테이블: 5개
JOIN 관계: 15개
Java 파일: 16개 분석 완료
비즈니스 태그 생성 완료

2단계: 아키텍처 HTML 리포트 생성
------------------------------
[OK] 아키텍처 HTML 리포트 생성 완료!
   파일 위치: ./project/sampleSrc/report/architecture_mermaid_20250907_110409.html
   테이블: 5개
   JOIN 관계: 15개
   Java 관계: 253개
   파일 크기: 29,536 bytes

브라우저에서 확인: file:///E:\SourceAnalyzer.git\project\sampleSrc\report\architecture_mermaid_20250907_110409.html
```

## HTML 리포트 특징

### ERD 리포트
- 데이터베이스 테이블 구조 시각화 (Mermaid 다이어그램)
- 테이블별 컬럼 상세 정보 카드
- Primary Key, Foreign Key 구분 표시
- 테이블 간 관계 다이어그램
- 확대/축소/드래그 기능
- SVG 다운로드 기능

### 아키텍처 리포트  
- 계층별 컴포넌트 배치 (Controller, Service, Mapper, Model)
- 의존성 관계 분석 (Dependency, Implements, Calls)
- 구성 요소 통계 테이블
- Mermaid 다이어그램으로 아키텍처 시각화
- 확대/축소/드래그 기능
- SVG 다운로드 기능

## 브라우저 지원
- Chrome, Firefox, Edge, Safari
- Internet Explorer 11+
- 모바일 브라우저 지원

## 문제 해결

### 파일이 생성되지 않는 경우
1. `./project/sampleSrc/report/` 디렉토리 자동 생성 확인
2. 메타데이터 파일 (`metadata_optimized.db`) 존재 확인
3. CSV 파일 (`sample_tables_no_fk.csv`) 존재 확인

### 다이어그램이 표시되지 않는 경우
- SVG 방식 사용으로 렌더링 오류 없음
- JavaScript 오류 시 브라우저 콘솔 확인

## 추가 옵션
기존 텍스트 리포트와 함께 사용 가능:
```bash
python test_reports_auto.py    # 모든 형태의 리포트 생성
```

생성되는 모든 리포트:
- ERD_Report_[timestamp].txt
- Architecture_Report_[timestamp].txt  
- Visual_Architecture_Report_[timestamp].txt
- Combined_Report_[timestamp].txt
- erd_mermaid_[timestamp].html
- architecture_mermaid_[timestamp].html