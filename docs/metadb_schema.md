# 메타데이터베이스 스키마 문서

## 📋 개요

**문서 작성일**: 2025-01-19 17:30  
**분석 대상**: sampleSrc 프로젝트 메타DB  
**스키마 버전**: 현재 운영 중인 스키마  
**총 테이블 수**: 25개

## 🗂️ 테이블 구조 개요

### 📊 테이블 분류

| 분류 | 테이블 수 | 테이블 목록 |
|------|-----------|-------------|
| **프로젝트 관리** | 1개 | projects |
| **파일 관리** | 1개 | files |
| **코드 구조** | 3개 | classes, methods, java_imports |
| **SQL 분석** | 3개 | sql_units, joins, required_filters |
| **데이터베이스 스키마** | 4개 | db_tables, db_columns, db_pk, db_views |
| **관계 및 연결** | 2개 | edges, edge_hints |
| **코드 품질** | 4개 | chunks, duplicates, duplicate_instances, code_metrics |
| **AI/LLM 관련** | 3개 | summaries, embeddings, enrichment_logs |
| **보안 및 취약점** | 1개 | vulnerability_fixes |
| **분석 결과** | 2개 | parse_results, relatedness |
| **시스템** | 1개 | sqlite_stat1 |

## 📋 상세 테이블 스키마

### 1. 프로젝트 관리

#### projects
프로젝트 기본 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| project_id | INTEGER | PK, NOT NULL | 프로젝트 고유 ID |
| root_path | TEXT | NOT NULL | 프로젝트 루트 경로 |
| name | VARCHAR(255) | NULL | 프로젝트 이름 |
| created_at | DATETIME | NULL | 생성일시 |
| updated_at | DATETIME | NULL | 수정일시 |

### 2. 파일 관리

#### files
프로젝트 내 파일 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| file_id | INTEGER | PK, NOT NULL | 파일 고유 ID |
| project_id | INTEGER | NOT NULL, FK | 프로젝트 ID |
| path | TEXT | NOT NULL | 파일 경로 |
| language | VARCHAR(50) | NULL | 프로그래밍 언어 |
| hash | VARCHAR(64) | NULL | 파일 해시값 |
| loc | INTEGER | NULL | 코드 라인 수 |
| mtime | DATETIME | NULL | 수정 시간 |
| llm_summary | TEXT | NULL | LLM 요약 |
| llm_summary_confidence | FLOAT | NULL | LLM 요약 신뢰도 |

**인덱스**: idx_files_project (project_id)

### 3. 코드 구조

#### classes
Java 클래스 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| class_id | INTEGER | PK, NOT NULL | 클래스 고유 ID |
| file_id | INTEGER | NOT NULL, FK | 파일 ID |
| fqn | TEXT | NULL | Fully Qualified Name |
| name | VARCHAR(255) | NOT NULL | 클래스명 |
| start_line | INTEGER | NULL | 시작 라인 |
| end_line | INTEGER | NULL | 종료 라인 |
| modifiers | TEXT | NULL | 접근 제어자 |
| annotations | TEXT | NULL | 어노테이션 |
| llm_summary | TEXT | NULL | LLM 요약 |
| llm_summary_confidence | FLOAT | NULL | LLM 요약 신뢰도 |

**인덱스**: idx_classes_file (file_id)

#### methods
Java 메서드 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| method_id | INTEGER | PK, NOT NULL | 메서드 고유 ID |
| class_id | INTEGER | NOT NULL, FK | 클래스 ID |
| name | VARCHAR(255) | NOT NULL | 메서드명 |
| signature | TEXT | NULL | 메서드 시그니처 |
| return_type | VARCHAR(255) | NULL | 반환 타입 |
| start_line | INTEGER | NULL | 시작 라인 |
| end_line | INTEGER | NULL | 종료 라인 |
| annotations | TEXT | NULL | 어노테이션 |
| parameters | TEXT | NULL | 매개변수 |
| modifiers | TEXT | NULL | 접근 제어자 |
| llm_summary | TEXT | NULL | LLM 요약 |
| llm_summary_confidence | FLOAT | NULL | LLM 요약 신뢰도 |

**인덱스**: idx_methods_class (class_id)

#### java_imports
Java import 문 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| import_id | INTEGER | PK, NOT NULL | Import 고유 ID |
| file_id | INTEGER | NOT NULL, FK | 파일 ID |
| class_fqn | TEXT | NULL | Import된 클래스 FQN |
| static | INTEGER | NULL | Static import 여부 |

### 4. SQL 분석

#### sql_units
SQL 쿼리 단위 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| sql_id | INTEGER | PK, NOT NULL | SQL 고유 ID |
| file_id | INTEGER | NOT NULL, FK | 파일 ID |
| origin | VARCHAR(50) | NULL | SQL 출처 |
| mapper_ns | VARCHAR(255) | NULL | MyBatis 매퍼 네임스페이스 |
| stmt_id | VARCHAR(255) | NULL | SQL 문 ID |
| start_line | INTEGER | NULL | 시작 라인 |
| end_line | INTEGER | NULL | 종료 라인 |
| stmt_kind | VARCHAR(50) | NULL | SQL 문 종류 (SELECT, INSERT, UPDATE, DELETE) |
| normalized_fingerprint | TEXT | NULL | 정규화된 SQL 지문 |
| llm_summary | TEXT | NULL | LLM 요약 |
| llm_summary_confidence | FLOAT | NULL | LLM 요약 신뢰도 |

**인덱스**: idx_sql_units_file (file_id)

#### joins
SQL JOIN 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| join_id | INTEGER | PK, NOT NULL | JOIN 고유 ID |
| sql_id | INTEGER | NOT NULL, FK | SQL ID |
| l_table | VARCHAR(128) | NULL | 왼쪽 테이블 |
| l_col | VARCHAR(128) | NULL | 왼쪽 컬럼 |
| op | VARCHAR(10) | NULL | 연산자 |
| r_table | VARCHAR(128) | NULL | 오른쪽 테이블 |
| r_col | VARCHAR(128) | NULL | 오른쪽 컬럼 |
| inferred_pkfk | INTEGER | NULL | 추론된 PK-FK 관계 |
| confidence | FLOAT | NULL | 신뢰도 |

**인덱스**: idx_joins_sql (sql_id)

#### required_filters
SQL WHERE 조건 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| filter_id | INTEGER | PK, NOT NULL | 필터 고유 ID |
| sql_id | INTEGER | NOT NULL, FK | SQL ID |
| table_name | VARCHAR(128) | NULL | 테이블명 |
| column_name | VARCHAR(128) | NULL | 컬럼명 |
| op | VARCHAR(10) | NULL | 연산자 |
| value_repr | VARCHAR(255) | NULL | 값 표현 |
| always_applied | INTEGER | NULL | 항상 적용 여부 |
| confidence | FLOAT | NULL | 신뢰도 |

**인덱스**: idx_filters_sql (sql_id)

### 5. 데이터베이스 스키마

#### db_tables
데이터베이스 테이블 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| table_id | INTEGER | PK, NOT NULL | 테이블 고유 ID |
| owner | VARCHAR(128) | NULL | 테이블 소유자 |
| table_name | VARCHAR(128) | NOT NULL | 테이블명 |
| status | VARCHAR(50) | NULL | 테이블 상태 |
| table_comment | TEXT | NULL | 테이블 주석 |
| llm_comment | TEXT | NULL | LLM 생성 주석 |
| llm_comment_confidence | FLOAT | NULL | LLM 주석 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |
| updated_at | DATETIME | NULL | 수정일시 |

#### db_columns
데이터베이스 컬럼 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| column_id | INTEGER | PK, NOT NULL | 컬럼 고유 ID |
| table_id | INTEGER | NOT NULL, FK | 테이블 ID |
| column_name | VARCHAR(128) | NOT NULL | 컬럼명 |
| data_type | VARCHAR(128) | NULL | 데이터 타입 |
| nullable | VARCHAR(1) | NULL | NULL 허용 여부 |
| column_comment | TEXT | NULL | 컬럼 주석 |
| llm_comment | TEXT | NULL | LLM 생성 주석 |
| llm_comment_confidence | FLOAT | NULL | LLM 주석 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |
| updated_at | DATETIME | NULL | 수정일시 |

#### db_pk
데이터베이스 Primary Key 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| table_id | INTEGER | PK, NOT NULL, FK | 테이블 ID |
| column_name | VARCHAR(128) | PK, NOT NULL | 컬럼명 |
| pk_pos | INTEGER | NULL | PK 위치 |
| created_at | DATETIME | NULL | 생성일시 |
| updated_at | DATETIME | NULL | 수정일시 |

**인덱스**: sqlite_autoindex_db_pk_1 (UNIQUE)

#### db_views
데이터베이스 뷰 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| view_id | INTEGER | PK, NOT NULL | 뷰 고유 ID |
| owner | VARCHAR(128) | NULL | 뷰 소유자 |
| view_name | VARCHAR(128) | NOT NULL | 뷰명 |
| text | CLOB | NULL | 뷰 정의 텍스트 |

### 6. 관계 및 연결

#### edges
코드 요소 간 관계 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| edge_id | INTEGER | PK, NOT NULL | 관계 고유 ID |
| project_id | INTEGER | NOT NULL, FK | 프로젝트 ID |
| src_type | VARCHAR(50) | NOT NULL | 소스 타입 |
| src_id | INTEGER | NOT NULL | 소스 ID |
| dst_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| dst_id | INTEGER | NULL | 대상 ID |
| edge_kind | VARCHAR(50) | NOT NULL | 관계 종류 |
| confidence | FLOAT | NULL | 신뢰도 |
| meta | TEXT | NULL | 메타데이터 |
| created_at | DATETIME | NULL | 생성일시 |

**인덱스**: 
- ix_edges_kind (edge_kind)
- ix_edges_src (src_type, src_id)
- idx_edges_src (src_type, src_id)
- ix_edges_project (project_id)
- idx_edges_dst (dst_type, dst_id)
- ix_edges_dst (dst_type, dst_id)

#### edge_hints
관계 추론 힌트 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| hint_id | INTEGER | PK, NOT NULL | 힌트 고유 ID |
| project_id | INTEGER | NOT NULL, FK | 프로젝트 ID |
| src_type | VARCHAR(50) | NOT NULL | 소스 타입 |
| src_id | INTEGER | NOT NULL | 소스 ID |
| hint_type | VARCHAR(50) | NOT NULL | 힌트 타입 |
| hint | TEXT | NOT NULL | 힌트 내용 |
| confidence | FLOAT | NULL | 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |

**인덱스**: 
- idx_edge_hints_type (hint_type)
- idx_edge_hints_project (project_id)

### 7. 코드 품질

#### chunks
코드 청크 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| chunk_id | INTEGER | PK, NOT NULL | 청크 고유 ID |
| target_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| target_id | INTEGER | NOT NULL | 대상 ID |
| content | TEXT | NULL | 청크 내용 |
| token_count | INTEGER | NULL | 토큰 수 |
| hash | VARCHAR(64) | NULL | 해시값 |
| created_at | DATETIME | NULL | 생성일시 |

**인덱스**: idx_chunks_target (target_type, target_id)

#### duplicates
중복 코드 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| duplicate_id | INTEGER | PK, NOT NULL | 중복 고유 ID |
| hash_signature | VARCHAR(64) | NOT NULL | 해시 시그니처 |
| token_count | INTEGER | NULL | 토큰 수 |
| line_count | INTEGER | NULL | 라인 수 |
| created_at | DATETIME | NULL | 생성일시 |

#### duplicate_instances
중복 코드 인스턴스 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| instance_id | INTEGER | PK, NOT NULL | 인스턴스 고유 ID |
| duplicate_id | INTEGER | NOT NULL, FK | 중복 ID |
| file_id | INTEGER | NOT NULL, FK | 파일 ID |
| start_line | INTEGER | NOT NULL | 시작 라인 |
| end_line | INTEGER | NOT NULL | 종료 라인 |

#### code_metrics
코드 메트릭 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| metric_id | INTEGER | PK, NOT NULL | 메트릭 고유 ID |
| target_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| target_id | INTEGER | NOT NULL | 대상 ID |
| metric_type | VARCHAR(50) | NOT NULL | 메트릭 타입 |
| metric_name | VARCHAR(100) | NOT NULL | 메트릭명 |
| value | FLOAT | NOT NULL | 메트릭 값 |
| threshold | FLOAT | NULL | 임계값 |
| severity | VARCHAR(20) | NULL | 심각도 |
| created_at | DATETIME | NULL | 생성일시 |

### 8. AI/LLM 관련

#### summaries
요약 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| summary_id | INTEGER | PK, NOT NULL | 요약 고유 ID |
| target_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| target_id | INTEGER | NOT NULL | 대상 ID |
| summary_type | VARCHAR(50) | NOT NULL | 요약 타입 |
| lang | VARCHAR(10) | NULL | 언어 |
| content | TEXT | NULL | 요약 내용 |
| confidence | FLOAT | NULL | 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |

#### embeddings
임베딩 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| chunk_id | INTEGER | PK, NOT NULL, FK | 청크 ID |
| model | VARCHAR(100) | NOT NULL | 모델명 |
| dim | INTEGER | NULL | 차원 수 |
| faiss_vector_id | INTEGER | NULL | FAISS 벡터 ID |
| created_at | DATETIME | NULL | 생성일시 |

#### enrichment_logs
LLM 보강 로그를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| enrich_id | INTEGER | PK, NOT NULL | 보강 고유 ID |
| target_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| target_id | INTEGER | NOT NULL | 대상 ID |
| pre_conf | FLOAT | NULL | 보강 전 신뢰도 |
| post_conf | FLOAT | NULL | 보강 후 신뢰도 |
| model | VARCHAR(100) | NULL | 모델명 |
| prompt_id | VARCHAR(100) | NULL | 프롬프트 ID |
| params | TEXT | NULL | 파라미터 |
| created_at | DATETIME | NULL | 생성일시 |

### 9. 보안 및 취약점

#### vulnerability_fixes
보안 취약점 수정 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| fix_id | INTEGER | PK, NOT NULL | 수정 고유 ID |
| target_type | VARCHAR(50) | NOT NULL | 대상 타입 |
| target_id | INTEGER | NOT NULL | 대상 ID |
| vulnerability_type | VARCHAR(100) | NULL | 취약점 타입 |
| severity | VARCHAR(20) | NULL | 심각도 |
| owasp_category | VARCHAR(10) | NULL | OWASP 카테고리 |
| cwe_id | VARCHAR(20) | NULL | CWE ID |
| reference_urls | TEXT | NULL | 참조 URL |
| description | TEXT | NULL | 설명 |
| fix_description | TEXT | NULL | 수정 설명 |
| original_code | TEXT | NULL | 원본 코드 |
| fixed_code | TEXT | NULL | 수정된 코드 |
| start_line | INTEGER | NULL | 시작 라인 |
| end_line | INTEGER | NULL | 종료 라인 |
| confidence | FLOAT | NULL | 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |

**인덱스**: idx_vuln_fixes_target (target_type, target_id)

### 10. 분석 결과

#### parse_results
파싱 결과 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| result_id | INTEGER | PK, NOT NULL | 결과 고유 ID |
| file_id | INTEGER | NOT NULL, FK | 파일 ID |
| parser_type | VARCHAR(50) | NOT NULL | 파서 타입 |
| success | BOOLEAN | NULL | 성공 여부 |
| parse_time | FLOAT | NULL | 파싱 시간 |
| ast_complete | BOOLEAN | NULL | AST 완성 여부 |
| partial_ast | BOOLEAN | NULL | 부분 AST 여부 |
| fallback_used | BOOLEAN | NULL | 폴백 사용 여부 |
| error_message | TEXT | NULL | 에러 메시지 |
| confidence | FLOAT | NULL | 신뢰도 |
| created_at | DATETIME | NULL | 생성일시 |

#### relatedness
코드 요소 간 관련성 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| relatedness_id | INTEGER | PK, NOT NULL | 관련성 고유 ID |
| project_id | INTEGER | NOT NULL, FK | 프로젝트 ID |
| node1_type | VARCHAR(50) | NOT NULL | 노드1 타입 |
| node1_id | INTEGER | NOT NULL | 노드1 ID |
| node2_type | VARCHAR(50) | NOT NULL | 노드2 타입 |
| node2_id | INTEGER | NOT NULL | 노드2 ID |
| score | FLOAT | NOT NULL | 관련성 점수 |
| reason | VARCHAR(100) | NOT NULL | 관련성 이유 |
| created_at | DATETIME | NULL | 생성일시 |

**인덱스**: 
- idx_relatedness_score (score)
- idx_relatedness_project_nodes (project_id, node1_type, node1_id, node2_type, node2_id) UNIQUE

### 11. 시스템

#### sqlite_stat1
SQLite 통계 정보를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| tbl | - | NULL | 테이블명 |
| idx | - | NULL | 인덱스명 |
| stat | - | NULL | 통계 정보 |

## 🔗 외래키 관계

### 주요 관계도

```
projects (1) ←→ (N) files
files (1) ←→ (N) classes
files (1) ←→ (N) methods
files (1) ←→ (N) java_imports
files (1) ←→ (N) sql_units
files (1) ←→ (N) parse_results
files (1) ←→ (N) duplicate_instances

classes (1) ←→ (N) methods

sql_units (1) ←→ (N) joins
sql_units (1) ←→ (N) required_filters

db_tables (1) ←→ (N) db_columns
db_tables (1) ←→ (N) db_pk

chunks (1) ←→ (1) embeddings

duplicates (1) ←→ (N) duplicate_instances

projects (1) ←→ (N) edges
projects (1) ←→ (N) edge_hints
projects (1) ←→ (N) relatedness
```

## 📊 현재 데이터 현황

### sampleSrc 프로젝트 기준

| 테이블 | 레코드 수 | 주요 내용 |
|--------|-----------|-----------|
| projects | 2개 | sampleSrc 프로젝트 (중복 생성) |
| files | 64개 | Java(32), JSP(16), XML(8), CSV(8) |
| classes | 32개 | Java 클래스 정보 |
| methods | 0개 | **메서드 파싱 실패** |
| sql_units | 840개 | SQL 쿼리 단위 (과다 분할) |
| edges | 235개 | 코드 요소 간 관계 |
| db_tables | 30개 | DB 테이블 (과다 계산) |
| db_columns | 91개 | DB 컬럼 정보 |
| chunks | 2543개 | 코드 청크 |

## 🚨 주요 이슈

### 1. 메서드 파싱 실패
- **문제**: methods 테이블에 0개 레코드
- **원인**: Java 메서드 파싱 로직 오류
- **해결방안**: 파서 개선 필요

### 2. SQL Units 과다 분할
- **문제**: 840개 (실제 16개 추정)
- **원인**: 동적 쿼리 파싱 시 과도한 분할
- **해결방안**: SQL 파싱 로직 개선

### 3. DB 테이블 과다 계산
- **문제**: 30개 (실제 13개)
- **원인**: JOIN에서 발견되는 모든 테이블명을 INFERRED로 생성
- **해결방안**: 테이블 필터링 로직 개선

### 4. 프로젝트 중복 생성
- **문제**: projects 테이블에 2개 레코드
- **원인**: 중복 분석 실행
- **해결방안**: 중복 방지 로직 추가

## 💡 개선 제안

### 1. 파싱 정확도 향상
- Java 메서드 파싱 로직 개선
- SQL 동적 쿼리 파싱 정확도 향상
- 테이블 추론 로직 개선

### 2. 중복 방지 강화
- 프로젝트 중복 생성 방지
- SQL Units 중복 분할 방지
- 테이블 중복 생성 방지

### 3. 성능 최적화
- 인덱스 최적화
- 불필요한 테이블 정리
- 쿼리 성능 개선

---

**문서 작성자**: SourceAnalyzer AI Assistant  
**최종 수정일**: 2025-01-19 17:30  
**다음 검토 예정**: 스키마 개선 후
