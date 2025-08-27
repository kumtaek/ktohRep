# Source Analyzer - Metadata Generation Engine

PRD v2.0 기반 소스코드 메타정보 생성 및 영향평가 도구의 1단계 구현체입니다.

## 주요 기능

### ✅ 구현 완료 (1단계)
- **다중 언어 파싱**: Java, JSP, MyBatis XML, SQL (Oracle 방언) 지원
- **메타정보 추출**: 클래스, 메소드, SQL 문, 조인/필터 조건 등
- **의존성 분석**: 호출 관계, 테이블 사용, include 관계 등
- **데이터베이스 스키마 로드**: Oracle CSV 파일에서 테이블/컬럼 정보 로드
- **SQLite 저장**: 원문 비저장 원칙하에 구조적 메타정보만 저장
- **증분 분석**: 파일 해시 기반 변경 감지 및 증분 분석
- **멀티스레드 처리**: 파일 단위 병렬 파싱

### 🔄 계획중 (2단계)
- RAG 기반 자연어 질의응답 API
- vLLM(Qwen2.5) 통합
- FAISS 임베딩 인덱스
- FastAPI 웹 서비스

## 시스템 요구사항

- Python 3.10+
- Java 8+ (javalang 라이브러리용)
- SQLite 3
- 최소 4GB RAM (대규모 프로젝트의 경우 8GB+ 권장)

## 설치 및 설정

### 1. 의존성 설치
```bash
cd src-analyzer
pip install -r requirements.txt
```

### 2. 설정 파일 편집
`config/config.yaml` 파일에서 프로젝트 경로 및 파싱 옵션 설정

### 3. 프로젝트 구조 준비
```
PROJECT/
└── your-project/
    ├── src/
    │   ├── main/java/
    │   ├── main/webapp/
    │   └── main/resources/
    └── DB_SCHEMA/
        ├── ALL_TABLES.csv
        ├── ALL_TAB_COLUMNS.csv
        ├── ALL_TAB_COMMENTS.csv
        ├── ALL_COL_COMMENTS.csv
        ├── PK_INFO.csv
        └── ALL_VIEWS.csv
```

## 사용법

### 기본 사용법
```bash
# 샘플 프로젝트 생성 및 분석
python main.py --create-sample

# 특정 프로젝트 분석
python main.py --project /path/to/your/project --name "project-name"

# 분석된 프로젝트 목록 조회
python main.py --list

# 스키마 로드 없이 분석 (소스코드만)
python main.py --project /path/to/project --no-schema
```

### 고급 사용법
```bash
# 커스텀 설정 파일 사용
python main.py --config /path/to/config.yaml --project /path/to/project

# 도움말
python main.py --help
```

## 아키텍처

### 데이터베이스 스키마
- **프로젝트/파일**: 기본 파일 정보 및 해시
- **Java 구조**: 클래스, 메소드, 어노테이션
- **SQL 구조**: SQL 문, 조인 조건, 필터 조건
- **의존성 그래프**: 호출/참조/사용 관계
- **DB 스키마**: 테이블/컬럼/PK/뷰 정보

### 파싱 엔진
- **JavaSourceParser**: javalang 기반 Java AST 분석
- **JSPMyBatisAnalyzer**: BeautifulSoup + lxml 기반 JSP/XML 파싱
- **SQLParser**: sqlparse 기반 Oracle SQL 분석

### 의존성 분석
- Java 메소드 호출 관계
- MyBatis 매퍼와 Java 클래스 연결
- SQL과 데이터베이스 테이블 관계
- JSP include 및 Java 클래스 사용

## 출력 결과

### 메타정보
- 파일별 LOC, 해시, 수정시간
- 클래스/메소드 구조 및 시그니처
- SQL 문 구조 및 정규화된 지문
- 조인 조건 및 필수 필터 추출

### 의존성 그래프
- `edges` 테이블에 모든 의존성 관계 저장
- 엣지 종류: calls, uses_table, includes, calls_sql 등
- 신뢰도 점수 (0.0~1.0) 포함

### 통계 정보
```
Project Statistics:
  total_files: 45
  java_files: 23
  jsp_files: 8
  mybatis_files: 12
  sql_files: 2
  total_classes: 18
  total_methods: 156
  total_sql_units: 34
  calls_count: 89
  uses_table_count: 67
```

## 성능 특성

### 처리량 (예상)
- **소규모** (10K LOC): ~30초
- **중규모** (100K LOC): ~5분
- **대규모** (1M LOC): ~30분

### 메모리 사용량
- **SQLite DB**: 1~3GB (1M LOC 기준)
- **런타임 메모리**: 2~4GB

## 데이터베이스 스키마 CSV 형식

### ALL_TABLES.csv
```csv
OWNER,TABLE_NAME,STATUS
SAMPLE,CUSTOMERS,VALID
SAMPLE,ORDERS,VALID
```

### ALL_TAB_COLUMNS.csv  
```csv
OWNER,TABLE_NAME,COLUMN_NAME,DATA_TYPE,NULLABLE
SAMPLE,CUSTOMERS,CUSTOMER_ID,NUMBER,N
SAMPLE,CUSTOMERS,NAME,VARCHAR2,N
```

### PK_INFO.csv
```csv
OWNER,TABLE_NAME,COLUMN_NAME,POSITION
SAMPLE,CUSTOMERS,CUSTOMER_ID,1
SAMPLE,ORDERS,ORDER_ID,1
```

## 개발 로드맵

### Phase 1 (완료)
- [x] 메타정보 추출 엔진
- [x] 의존성 분석
- [x] SQLite 저장
- [x] CSV 스키마 로더

### Phase 2 (계획)
- [ ] FastAPI 웹 서비스
- [ ] FAISS 임베딩 인덱스
- [ ] vLLM 통합
- [ ] RAG 기반 질의응답

### Phase 3 (향후)
- [ ] PL/SQL 저장프로시저 분석
- [ ] Python/JavaScript 지원 확장
- [ ] 보안 취약점 분석
- [ ] 웹 UI 대시보드

## 문제해결

### 일반적인 오류
1. **javalang import error**: `pip install javalang` 실행
2. **SQLite 권한 오류**: `data/` 디렉토리 권한 확인
3. **CSV 파일 없음**: `--no-schema` 옵션 사용 또는 샘플 파일 생성

### 성능 개선
1. **파싱 속도**: `config.yaml`에서 `thread_count` 증가
2. **메모리 사용량**: `max_file_size_mb` 제한
3. **대용량 파일**: 파일별 크기 제한 설정

## 기여 방법

1. 이슈 등록 또는 기능 요청
2. 브랜치 생성 (`feature/new-feature`)
3. 변경사항 커밋
4. 풀 리퀘스트 생성

## 라이선스

이 프로젝트는 내부 개발용으로 제작되었습니다.