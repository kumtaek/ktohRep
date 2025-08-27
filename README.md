# 소스 분석기 - 1단계 메타정보 생성 시스템

레거시 Java/JSP/MyBatis/Oracle 소스 코드를 정적 분석하여 메타정보를 생성하는 시스템입니다.

## 프로젝트 개요

### 주요 특징
- **원문 비저장 원칙**: 소스 코드 원문을 저장하지 않고 경로, 라인 범위, 구조 정보만 메타데이터로 저장
- **다중 언어 지원**: Java, JSP, MyBatis XML, SQL(Oracle 방언) 분석
- **신뢰도 추적**: 모든 분석 결과에 신뢰도 점수 포함
- **증분 분석**: 변경된 파일만 재분석하는 효율적인 처리
- **병렬 처리**: 멀티스레드를 통한 고성능 분석

### 분석 대상
- **Java**: 클래스, 메서드, 어노테이션, 의존성 관계
- **JSP**: 스크립틀릿 내 SQL, include 관계
- **MyBatis XML**: SQL 매퍼, 동적 SQL, 조인 조건, 필터 조건
- **DB 스키마**: Oracle 메타데이터 (CSV 형태)

## 시스템 구조

```
src/
├── models/
│   └── database.py          # SQLAlchemy 모델 정의
├── parsers/
│   ├── java_parser.py       # Java AST 파서
│   ├── jsp_mybatis_parser.py # JSP/MyBatis XML 파서
│   └── sql_parser.py        # SQL 구문 파서
├── database/
│   └── metadata_engine.py   # 메타데이터 저장 엔진
└── utils/
    ├── confidence_calculator.py # 신뢰도 계산기
    └── csv_loader.py        # DB 스키마 CSV 로더
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 설정 파일 수정

`config/config.yaml` 파일에서 데이터베이스와 분석 옵션을 설정합니다.

```yaml
# 데이터베이스 설정
database:
  type: sqlite  # 개발용
  sqlite:
    path: "./data/metadata.db"
    
# 파서 설정  
parsers:
  java:
    enabled: true
    parser_type: "javaparser"
```

### 3. 프로젝트 분석 실행

```bash
python main.py /path/to/your/project --project-name "MyProject"
```

### 4. DB 스키마 준비

프로젝트 폴더 하위에 `DB_SCHEMA` 폴더를 생성하고 다음 CSV 파일들을 배치합니다:

```
PROJECT/
└── your-project/
    └── DB_SCHEMA/
        ├── ALL_TABLES.csv
        ├── ALL_TAB_COLUMNS.csv
        ├── ALL_TAB_COMMENTS.csv
        ├── ALL_COL_COMMENTS.csv
        └── PK_INFO.csv
```

## 주요 기능

### 1. Java 소스 분석
- JavaParser를 사용한 AST 기반 분석
- 클래스, 메서드, 어노테이션 추출
- 메서드 호출 관계 분석
- Spring Framework 어노테이션 처리

### 2. MyBatis XML 분석
- SQL 매퍼 구문 추출 (`<select>`, `<insert>`, `<update>`, `<delete>`)
- 동적 SQL 태그 처리 (`<if>`, `<choose>`, `<foreach>`)
- 조인 조건 자동 추출
- 필수 필터 조건 식별

### 3. 신뢰도 기반 분석
- AST 품질 기반 신뢰도 계산
- 정적 규칙 매칭 신뢰도
- DB 스키마 매칭 신뢰도
- 복잡도에 따른 신뢰도 조정

### 4. 메타데이터 저장
- 파일, 클래스, 메서드 구조 정보
- SQL 구문, 조인, 필터 조건
- 의존성 그래프 (호출, 참조 관계)
- 분석 신뢰도 및 로그

## 데이터베이스 스키마

주요 테이블:
- `projects`: 프로젝트 정보
- `files`: 소스 파일 메타데이터 
- `classes`: Java 클래스 정보
- `methods`: Java 메서드 정보
- `sql_units`: SQL 구문 정보
- `joins`: 조인 조건
- `required_filters`: 필수 필터 조건
- `edges`: 의존성 관계 그래프

## 명령행 옵션

```bash
python main.py [OPTIONS] PROJECT_PATH

인수:
  PROJECT_PATH          분석할 프로젝트 경로

옵션:
  --config CONFIG       설정 파일 경로 (기본값: ./config/config.yaml)
  --project-name NAME   프로젝트 이름 (기본값: 폴더명)
  --incremental         증분 분석 모드
  --help                도움말 표시
```

## 분석 결과 예시

```
==========================================
분석 완료!
프로젝트: insurance-system
분석된 파일 수: 234
Java 파일: 156
JSP 파일: 23
XML 파일: 55
클래스 수: 198
메서드 수: 1,247  
SQL 구문 수: 134
==========================================
```

## 설정 옵션

### 파서 설정
```yaml
parsers:
  java:
    enabled: true
    parser_type: "javaparser"  # 또는 "tree-sitter"
    
  jsp:
    enabled: true
    parser_type: "antlr"
    
  sql:
    enabled: true
    oracle_dialect: true
```

### 처리 설정
```yaml
processing:
  max_workers: 4          # 병렬 처리 워커 수
  chunk_size: 512         # 청킹 크기
  confidence_threshold: 0.5 # 신뢰도 임계값
```

### 파일 패턴 설정
```yaml
file_patterns:
  include:
    - "**/*.java"
    - "**/*.jsp"
    - "**/*.xml"
  exclude:
    - "**/target/**"
    - "**/build/**"
```

## 로깅 및 모니터링

- 분석 진행 상황 실시간 로깅
- 오류 파일 및 원인 추적
- 분석 성능 메트릭
- 신뢰도 분포 통계

## 향후 계획

- Tree-sitter 기반 다국어 파서 지원
- LLM 보강 기능 (2단계)
- 벡터 임베딩 및 RAG 기능 (2단계)
- 웹 대시보드 UI
- Oracle 운영 환경 배포

## 라이선스

이 프로젝트는 내부 사용을 위한 소스 분석 도구입니다.