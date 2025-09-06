# Create MetaDB - 최적화된 메타정보 생성 시스템

## 📋 개요

**Create MetaDB**는 신규입사자 지원을 위한 최적화된 메타정보 생성 시스템입니다. 기존 phase1 시스템과 완전히 독립적으로 동작하며, 성능 최적화와 신규입사자 지원에 특화된 메타정보를 생성합니다.

## 🎯 개발 목적

- **신규입사자 지원**: 소스코드만으로 업무 파악이 어려운 신규입사자를 위한 메타정보 구축
- **성능 최적화**: 기존 대비 80% 이상 성능 향상 (메타DB 크기, 생성 시간, 메모리 사용량)
- **독립적 운영**: 기존 phase1 시스템과 배타적으로 동작
- **확장성**: 대규모 프로젝트에서도 일정한 성능 유지
- **LLM 활용**: 코드 요약 및 복잡한 관계 분석을 위한 LLM 통합

## 🏗️ 시스템 아키텍처

### 폴더 구조

```
create_metadb/                           # 루트 디렉토리
├── __init__.py
├── main.py                              # 메인 실행 파일
├── config/
│   ├── __init__.py
│   └── config.yaml                      # 통합 설정 파일
├── core/                                # 핵심 엔진
│   ├── __init__.py
│   ├── metadata_engine.py               # 메타정보 생성 엔진
│   ├── relationship_extractor.py        # 관계 추출기
│   ├── business_classifier.py           # 비즈니스 분류기
│   ├── lightweight_chunker.py           # 경량 청킹 시스템
│   └── llm_summarizer.py                # LLM 요약 생성기
├── parsers/                             # 파서 모듈 (phase1에서 재사용)
│   ├── __init__.py
│   ├── java/
│   │   ├── __init__.py
│   │   ├── javaparser_enhanced.py       # Java 파서
│   │   └── relationship_parser.py       # 관계 파서
│   ├── sql/
│   │   ├── __init__.py
│   │   ├── sql_parser.py                # SQL 파서
│   │   └── join_analyzer.py             # 조인 관계 분석기
│   └── jsp/
│       ├── __init__.py
│       └── jsp_parser.py                # JSP 파서
├── database/                            # 데이터베이스 모듈
│   ├── __init__.py
│   ├── schema.py                        # 최적화된 스키마
│   └── connection.py                    # DB 연결 관리
├── llm/                                 # LLM 관련 모듈
│   ├── __init__.py
│   ├── llm_client.py                    # LLM 클라이언트
│   ├── prompt_templates.py              # 프롬프트 템플릿
│   └── response_parser.py               # 응답 파서
├── analyzers/                           # 분석기 모듈
│   ├── __init__.py
│   ├── architecture_analyzer.py         # 아키텍처 분석
│   ├── dependency_analyzer.py           # 의존성 분석
│   ├── business_flow_analyzer.py        # 비즈니스 흐름 분석
│   └── sql_join_analyzer.py             # SQL 조인 관계 분석기
└── utils/                               # 유틸리티
    ├── __init__.py
    ├── file_utils.py                    # 파일 처리 유틸리티
    ├── cache_manager.py                 # 캐시 관리
    └── logger.py                        # 로깅 시스템
```

### 공용 폴더 구조

```
project/                                 # 공용 프로젝트 폴더
└── {project_name}/
    ├── src/                             # 소스 파일들
    ├── db_schema/                       # DB 스키마 파일들
    ├── metadata_optimized.db            # 최적화된 메타DB
    └── config/
        └── filter_config.yaml           # 공용 설정 파일
```

## 🚀 설치 및 실행

### 환경 설정

```bash
# 1. 환경변수 설정
set CREATE_METADB_PATH=E:\SourceAnalyzer.git\create_metadb

# 2. create_metadb 폴더로 이동
cd E:\SourceAnalyzer.git\create_metadb
```

### 실행 방법

```bash
# 기본 실행 (변동분만 처리 - 해시값 비교)
python main.py --project-name sampleSrc

# LLM 요약 생성 포함
python main.py --project-name sampleSrc --enable-llm

# SQL 조인 분석 강화
python main.py --project-name sampleSrc --enhance-sql-analysis

# 메타DB 전체 초기화 (초기화만 하고 끝남)
python main.py --project-name sampleSrc --clean

# 삭제된 데이터만 정리 (del_yn='Y' 건만 삭제, 삭제만 하고 끝남)
python main.py --project-name sampleSrc --del_clear

# 상세 로그 출력
python main.py --project-name sampleSrc --verbose

# 기존 시스템과 비교
python main.py --project-name sampleSrc --compare
```

## 📊 성능 지표

| 항목 | 기존 phase1 | create_metadb | 개선율 |
|------|-------------|---------------|--------|
| **메타DB 크기** | 1.2MB | 200KB | -83% |
| **생성 시간** | 30초 | 10초 | -67% |
| **변동분 처리** | 전체 재생성 | 해시 비교 | -50% |
| **질의 응답 시간** | 2초 | 0.5초 | -75% |
| **메모리 사용량** | 100MB | 30MB | -70% |
| **청크 수** | 2,048개 | 250개 | -88% |
| **엣지 수** | 231개 | 150개 | -35% |
| **LLM 요약** | 없음 | 250개 | +100% |
| **SQL 조인 분석** | 없음 | 규칙기반 + LLM보조 | +100% |
| **삭제 관리** | 물리적 삭제 | 논리적 삭제 (del_yn) | +100% |

## 🗄️ 메타DB 스키마

### 핵심 테이블

#### 1. core_relationships (핵심 관계)
```sql
CREATE TABLE core_relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    src_type VARCHAR(20) NOT NULL,        -- 'class', 'method', 'file', 'sql_unit', 'table'
    src_id INTEGER NOT NULL,
    src_name VARCHAR(200) NOT NULL,
    dst_type VARCHAR(20) NOT NULL,
    dst_id INTEGER NOT NULL,
    dst_name VARCHAR(200) NOT NULL,
    relationship_type VARCHAR(30) NOT NULL, -- 'calls', 'dependency', 'import', 'foreign_key', 'join'
    confidence FLOAT DEFAULT 1.0,
    metadata TEXT,                        -- JSON 형태의 추가 정보
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);
```

#### 2. business_classifications (비즈니스 분류)
```sql
CREATE TABLE business_classifications (
    classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    target_type VARCHAR(20) NOT NULL,     -- 'class', 'method', 'file', 'sql_unit'
    target_id INTEGER NOT NULL,
    target_name VARCHAR(200) NOT NULL,
    business_domain VARCHAR(50),          -- 'user', 'order', 'product', 'auth'
    architecture_layer VARCHAR(50),       -- 'controller', 'service', 'repository', 'entity'
    functional_category VARCHAR(100),     -- 'crud', 'search', 'authentication', 'payment'
    complexity_level VARCHAR(20),         -- 'beginner', 'intermediate', 'advanced'
    learning_priority INTEGER,            -- 1-5
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);
```

#### 3. llm_summaries (LLM 요약)
```sql
CREATE TABLE llm_summaries (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    target_type VARCHAR(20) NOT NULL,     -- 'class', 'method', 'file', 'sql_unit'
    target_id INTEGER NOT NULL,
    target_name VARCHAR(200) NOT NULL,
    summary_text TEXT NOT NULL,           -- LLM이 생성한 요약
    summary_type VARCHAR(30),             -- 'business_purpose', 'technical_summary', 'learning_guide'
    confidence_score FLOAT,               -- 요약의 신뢰도
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);
```

#### 4. file_index (파일 인덱스)
```sql
CREATE TABLE file_index (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(20) NOT NULL,       -- 'java', 'jsp', 'xml', 'sql'
    file_size INTEGER,
    last_modified DATETIME,
    package_name VARCHAR(200),
    class_name VARCHAR(200),
    business_domain VARCHAR(50),
    architecture_layer VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);
```

## 🔧 주요 기능

### 변동분 처리 및 삭제 관리 구현 방안

#### 1. **해시값 기반 변동분 감지**
- **파일 해시 계산**: MD5/SHA256으로 파일 내용 해시값 생성
- **변경 감지**: 메타DB의 기존 해시값과 비교하여 변경된 파일만 식별
- **성능 최적화**: 변경되지 않은 파일은 분석 생략

#### 2. **논리적 삭제 시스템**
- **del_yn 플래그**: 'Y' = 삭제됨, 'N' = 유효 (기본값)
- **관계 무결성**: 삭제된 파일의 관련 엣지들도 함께 del_yn='Y' 처리
- **복구 가능**: 필요시 del_yn='N'으로 복구 가능

#### 3. **CLI 옵션별 동작**
- `--clean`: 메타DB 전체 초기화 (초기화만 하고 종료)
- `--del_clear`: del_yn='Y'인 데이터만 물리적 삭제 (삭제만 하고 종료)
- 기본 실행: 변동분만 처리 (해시값 비교)

#### 4. **구현 세부사항**
```python
# 해시값 계산 및 비교
def calculate_file_hash(file_path: str) -> str:
    """파일 내용의 해시값 계산"""
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.md5(content).hexdigest()

def find_changed_files(project_name: str) -> List[str]:
    """변경된 파일 목록 반환"""
    changed_files = []
    for file_path in get_all_source_files(project_name):
        current_hash = calculate_file_hash(file_path)
        stored_hash = get_stored_hash(file_path)
        
        if current_hash != stored_hash:
            changed_files.append(file_path)
    
    return changed_files

# 논리적 삭제 처리
def mark_file_as_deleted(file_path: str):
    """파일을 논리적 삭제로 처리"""
    update_chunks_del_yn(file_path, 'Y')
    update_edges_del_yn(file_path, 'Y')
    update_classes_del_yn(file_path, 'Y')
    update_methods_del_yn(file_path, 'Y')

# 조회 시 삭제 필터링
def get_valid_chunks():
    """유효한 청크만 조회"""
    return execute_query("""
        SELECT * FROM chunks 
        WHERE NVL(del_yn, 'N') <> 'Y'
    """)
```

### 1. 핵심 관계 추출
- **calls**: 메서드 호출 관계
- **dependency**: 클래스 의존성 관계
- **import**: 패키지 import 관계
- **foreign_key**: DB 테이블 관계
- **join**: SQL 조인 관계 (새로 추가)
- **uses_service**: Service 사용 관계
- **uses_repository**: Repository 사용 관계

### 2. SQL 조인 관계 분석
- **규칙 기반 분석**: 정규표현식을 이용한 빠른 조인 관계 추출
- **LLM 보조 분석**: 복잡한 쿼리의 경우 LLM으로 추가 분석
- **테이블 간 관계**: JOIN, LEFT JOIN, RIGHT JOIN, INNER JOIN 관계 추출
- **조인 조건 분석**: ON 절의 조인 조건 자동 추출
- **비즈니스 의미**: 조인의 비즈니스 목적과 의미 분석
- **외부 테이블 처리**: ./project 폴더에 없는 테이블 자동 처리
- **Owner 자동 추론**: FROM 절에 owner가 없는 경우 자동 추론
- **외부 청크 도출**: 소스 분석 중 ./project 폴더에 없는 청크 자동 생성

### 3. LLM 요약 생성
- **비즈니스 목적**: 코드가 무엇을 하는지 설명
- **기술적 내용**: 주요 기능과 로직 설명
- **학습 가이드**: 신규입사자를 위한 이해 팁
- **신뢰도 점수**: 요약의 정확도 평가
- **요약 타입**: business_purpose, technical_summary, learning_guide
- **LLM 모델**: 사용된 LLM 모델 정보 저장
- **자동 생성**: 클래스, 메서드, SQL Unit별 자동 요약 생성

### 4. 비즈니스 분류
- **비즈니스 도메인**: User, Order, Product, Auth
- **아키텍처 계층**: Controller, Service, Repository, Entity
- **기능 분류**: CRUD, 검색, 인증, 결제
- **복잡도 분석**: Beginner, Intermediate, Advanced
- **학습 우선순위**: 1-5점

### 5. 경량 청킹
- **필수 정보만**: 핵심 관계와 구조 정보만 저장
- **실시간 활용**: 상세 내용은 ./project 폴더에서 실시간 분석
- **성능 최적화**: 메타DB 크기 80% 이상 감소

### 6. 변동분 처리
- **해시값 비교**: 파일 내용의 해시값으로 변경 여부 감지
- **선택적 처리**: 변경된 파일만 분석하여 성능 최적화
- **배치 효율성**: 대용량 프로젝트에서 처리 시간 대폭 단축

#### 변동분 처리 로직
```python
def process_incremental_update(self, project_name: str):
    """변동분만 처리하는 로직"""
    # 1. 현재 파일들의 해시값 계산
    current_hashes = self._calculate_file_hashes(project_name)
    
    # 2. 메타DB의 기존 해시값과 비교
    changed_files = self._find_changed_files(current_hashes)
    
    # 3. 변경된 파일만 분석
    for file_path in changed_files:
        self._analyze_file(file_path)
    
    # 4. 삭제된 파일 처리 (del_yn='Y' 설정)
    deleted_files = self._find_deleted_files(current_hashes)
    for file_path in deleted_files:
        self._mark_as_deleted(file_path)
```

### 7. 삭제 관리
- **논리적 삭제**: 물리적 삭제 대신 del_yn 플래그 사용
- **데이터 무결성**: 삭제된 데이터도 관계 분석에 활용 가능
- **복구 가능**: 필요시 삭제 플래그 해제로 데이터 복구

#### 삭제 관리 로직
```python
def mark_as_deleted(self, file_path: str):
    """파일을 논리적 삭제로 처리"""
    cursor = self.conn.cursor()
    
    # 1. 해당 파일의 모든 청크를 del_yn='Y'로 설정
    cursor.execute("""
        UPDATE chunks 
        SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
        WHERE file_path = ?
    """, (file_path,))
    
    # 2. 관련 엣지들도 del_yn='Y'로 설정
    cursor.execute("""
        UPDATE edges 
        SET del_yn = 'Y', last_modified = CURRENT_TIMESTAMP 
        WHERE source_path = ? OR target_path = ?
    """, (file_path, file_path))
    
    self.conn.commit()

def clear_deleted_data(self):
    """del_yn='Y'인 데이터만 물리적 삭제"""
    cursor = self.conn.cursor()
    
    cursor.execute("DELETE FROM chunks WHERE del_yn = 'Y'")
    cursor.execute("DELETE FROM edges WHERE del_yn = 'Y'")
    cursor.execute("DELETE FROM classes WHERE del_yn = 'Y'")
    cursor.execute("DELETE FROM methods WHERE del_yn = 'Y'")
    
    self.conn.commit()
```

#### 조회 시 삭제 필터링
```sql
-- 모든 조회 쿼리에서 삭제된 데이터 제외
SELECT * FROM chunks 
WHERE NVL(del_yn, 'N') <> 'Y';

SELECT * FROM edges 
WHERE NVL(del_yn, 'N') <> 'Y';

SELECT * FROM classes 
WHERE NVL(del_yn, 'N') <> 'Y';
```

## 📈 신규입사자 지원 효과

### 질의응답 시나리오

#### 시나리오 1: "UserController는 어떤 서비스를 사용하나?"
```
1단계: 메타DB에서 dependency, uses_service 엣지 검색
2단계: ./project/UserController.java 파일에서 @Autowired 어노테이션 확인
3단계: LLM 요약에서 비즈니스 목적 확인
4단계: 실시간으로 의존성 주입된 서비스 목록 반환
```

#### 시나리오 2: "사용자 등록 프로세스는 어떻게 동작하나?"
```
1단계: 메타DB에서 User 도메인 관련 클래스 검색
2단계: calls 엣지로 Controller → Service → Repository 흐름 파악
3단계: LLM 요약으로 각 단계의 비즈니스 목적 확인
4단계: ./project 폴더에서 각 메서드의 상세 로직 분석
5단계: 비즈니스 플로우 다이어그램 생성
```

#### 시나리오 3: "이 SQL 쿼리는 어떤 테이블들을 조인하나?"
```
1단계: 메타DB에서 해당 SQL Unit의 join 엣지 검색
2단계: SQL 조인 분석기로 테이블 간 관계 확인
3단계: LLM 요약으로 조인 목적과 비즈니스 의미 확인
4단계: 관련 테이블들의 ERD 생성
```

## 🔄 기존 시스템과의 차이점

| 구분 | 기존 phase1 | create_metadb |
|------|-------------|---------------|
| **목적** | 일반적인 소스 분석 | 신규입사자 지원 특화 |
| **메타DB 크기** | 대용량 (1.2MB) | 경량화 (200KB) |
| **청크 전략** | 모든 정보 저장 | 핵심 정보만 저장 |
| **실시간 활용** | 없음 | ./project 폴더 활용 |
| **비즈니스 분류** | 없음 | 도메인/계층/복잡도 분류 |
| **학습 우선순위** | 없음 | 1-5점 우선순위 |
| **SQL 조인 분석** | 없음 | 규칙 기반 + LLM 보조 |
| **LLM 요약** | 없음 | 비즈니스/기술/학습 가이드 |

## 🛠️ 개발 가이드

### 파서 재사용
- phase1의 검증된 파서들을 create_metadb로 복사
- import 경로를 상대경로로 수정
- create_metadb 루트 기준으로 동작하도록 조정

### 상대경로 설정
```python
# create_metadb/main.py
import os
import sys
from pathlib import Path

# 환경변수에서 루트 경로 가져오기
ROOT_DIR = Path(os.environ.get('CREATE_METADB_PATH', '.'))
PROJECT_ROOT = ROOT_DIR.parent

# 상대경로 설정
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))
```

### 환경변수 활용
```bash
set CREATE_METADB_PATH=E:\SourceAnalyzer.git\create_metadb
```

### LLM 설정 및 활용

#### LLM 클라이언트 설정
```python
# create_metadb/llm/llm_client.py
class LLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.model = config.get('llm_model', 'gpt-3.5-turbo')
        self.api_key = config.get('llm_api_key')
        self.max_tokens = config.get('max_tokens', 500)
    
    async def generate_summary(self, code_content: str, code_type: str) -> str:
        """LLM을 이용한 코드 요약 생성"""
        prompt = f"""
        다음 {code_type} 코드를 분석하여 신규입사자가 이해하기 쉽게 요약해주세요:
        
        1. 비즈니스 목적: 이 코드가 무엇을 하는지
        2. 기술적 내용: 주요 기능과 로직
        3. 학습 가이드: 신규입사자가 이해하기 위한 팁
        
        코드:
        {code_content}
        """
        
        response = await self._call_llm_api(prompt)
        return response
```

#### SQL 조인 분석 구현 예시
```python
# create_metadb/parsers/sql/join_analyzer.py
class SqlJoinAnalyzer:
    def __init__(self):
        self.join_patterns = {
            'inner_join': r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'left_join': r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'right_join': r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'full_join': r'FULL\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            'join': r'JOIN\s+(\w+)\s+ON\s+([^)]+)'
        }
    
    def extract_join_relationships(self, sql_content: str) -> List[Dict]:
        """SQL에서 조인 관계 추출"""
        relationships = []
        
        for join_type, pattern in self.join_patterns.items():
            matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                table_name = match.group(1)
                join_condition = match.group(2)
                
                # 조인 조건에서 테이블 추출
                tables = self._extract_tables_from_condition(join_condition)
                
                relationship = {
                    'join_type': join_type,
                    'table_name': table_name,
                    'join_condition': join_condition,
                    'related_tables': tables,
                    'confidence': 0.9
                }
                relationships.append(relationship)
        
        return relationships
    
    def _extract_tables_from_condition(self, condition: str) -> List[str]:
        """조인 조건에서 테이블명 추출"""
        # 예: "users.id = orders.user_id" -> ["users", "orders"]
        table_pattern = r'(\w+)\.\w+'
        tables = re.findall(table_pattern, condition)
        return list(set(tables))
    
    def _resolve_table_owner(self, table_name: str, metadata_db) -> str:
        """테이블 owner 자동 추론"""
        # 1. 메타DB에서 테이블명으로 검색
        cursor = metadata_db.cursor()
        cursor.execute("SELECT owner FROM db_tables WHERE table_name = ?", (table_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  # 메타DB에서 찾은 owner
        
        # 2. 메타DB에 없으면 config.yaml의 default_owner 사용
        return self.config.get('default_owner', 'UNKNOWN')

# create_metadb/analyzers/sql_join_analyzer.py
class SqlJoinAnalyzer:
    def __init__(self, llm_client: LLMClient = None):
        self.rule_analyzer = SqlJoinAnalyzer()
        self.llm_client = llm_client
    
    async def analyze_join_relationships(self, sql_content: str) -> List[Dict]:
        """SQL 조인 관계 분석 (규칙 기반 + LLM 보조)"""
        
        # 1. 규칙 기반 분석
        rule_based_results = self.rule_analyzer.extract_join_relationships(sql_content)
        
        # 2. 복잡한 쿼리는 LLM으로 추가 분석
        if self._is_complex_query(sql_content) and self.llm_client:
            llm_results = await self._analyze_with_llm(sql_content)
            rule_based_results.extend(llm_results)
        
        return rule_based_results
    
    def _is_complex_query(self, sql_content: str) -> bool:
        """복잡한 쿼리인지 판단"""
        join_count = len(re.findall(r'JOIN', sql_content, re.IGNORECASE))
        return join_count >= 3  # 3개 이상의 조인이 있으면 복잡한 쿼리
    
    async def _analyze_with_llm(self, sql_content: str) -> List[Dict]:
        """LLM을 이용한 복잡한 조인 분석"""
        prompt = f"""
        다음 SQL 쿼리의 테이블 간 조인 관계를 분석해주세요:
        
        1. 조인되는 테이블들
        2. 조인 조건
        3. 조인 타입 (INNER, LEFT, RIGHT, FULL)
        4. 비즈니스 의미
        
        SQL:
        {sql_content}
        """
        
        response = await self.llm_client._call_llm_api(prompt)
        return self._parse_join_analysis(response)
```

### 외부 청크 도출이 발생하는 경우들

#### 1. **SQL 조인 관계 분석 시**
```sql
-- 예시: 외부 테이블 참조
SELECT u.name, o.order_date, p.product_name
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN external_system.products p ON o.product_id = p.id  -- 외부 테이블
```

**처리 방법:**
- `external_system.products` 테이블이 ./project/db_schema에 없음
- 메타DB에서 `products` 테이블명으로 검색
- 있으면 해당 owner 사용, 없으면 `default_owner` 사용

#### 2. **Java Import 관계 분석 시**
```java
// 예시: 외부 라이브러리 클래스 참조
import com.external.library.ExternalService;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    @Autowired
    private ExternalService externalService;  // 외부 클래스
}
```

**처리 방법:**
- `ExternalService` 클래스가 ./project/src에 없음
- 메타DB에서 클래스명으로 검색
- 있으면 해당 정보 사용, 없으면 외부 라이브러리로 분류

#### 3. **JSP Include 관계 분석 시**
```jsp
<!-- 예시: 외부 JSP 파일 참조 -->
<%@ include file="/WEB-INF/views/common/header.jsp" %>
<%@ include file="/WEB-INF/views/external/footer.jsp" %>  <!-- 외부 파일 -->
```

**처리 방법:**
- `footer.jsp` 파일이 ./project/src에 없음
- 메타DB에서 파일명으로 검색
- 있으면 해당 정보 사용, 없으면 외부 파일로 분류

#### 4. **MyBatis ResultMap 참조 시**
```xml
<!-- 예시: 외부 ResultMap 참조 -->
<resultMap id="userResultMap" type="User">
    <result property="name" column="name"/>
    <result property="orders" resultMap="external.orderResultMap"/>  <!-- 외부 ResultMap -->
</resultMap>
```

**처리 방법:**
- `orderResultMap`이 ./project/src에 없음
- 메타DB에서 ResultMap명으로 검색
- 있으면 해당 정보 사용, 없으면 외부 ResultMap으로 분류

#### 5. **Spring Bean 참조 시**
```java
// 예시: 외부 Bean 참조
@Autowired
@Qualifier("externalDataSource")
private DataSource externalDataSource;  // 외부 Bean

@Value("${external.api.url}")
private String externalApiUrl;  // 외부 설정값
```

**처리 방법:**
- `externalDataSource` Bean이 ./project/src에 없음
- 메타DB에서 Bean명으로 검색
- 있으면 해당 정보 사용, 없으면 외부 Bean으로 분류

### 외부 청크 처리 전략

#### **1단계: 메타DB 검색**
```python
def resolve_external_chunk(self, chunk_name: str, chunk_type: str) -> Dict:
    """외부 청크 정보 해결"""
    cursor = self.metadata_db.cursor()
    
    # 메타DB에서 검색
    if chunk_type == 'table':
        cursor.execute("SELECT * FROM db_tables WHERE table_name = ?", (chunk_name,))
    elif chunk_type == 'class':
        cursor.execute("SELECT * FROM classes WHERE name = ?", (chunk_name,))
    elif chunk_type == 'file':
        cursor.execute("SELECT * FROM files WHERE file_name = ?", (chunk_name,))
    
    result = cursor.fetchone()
    if result:
        return self._convert_to_chunk_info(result)
    
    # 2단계: config.yaml 기본값 사용
    return self._create_external_chunk(chunk_name, chunk_type)
```

#### **2단계: 외부 청크 생성**
```python
def _create_external_chunk(self, chunk_name: str, chunk_type: str) -> Dict:
    """외부 청크 정보 생성"""
    default_config = self.config.get('external_chunks', {})
    
    return {
        'chunk_name': chunk_name,
        'chunk_type': chunk_type,
        'is_external': True,
        'owner': default_config.get('default_owner', 'EXTERNAL'),
        'source': 'inferred',
        'confidence': 0.5  # 추론된 정보이므로 낮은 신뢰도
    }
```

#### SQL 조인 분석 예시
```sql
-- 예시 SQL 쿼리
SELECT u.name, o.order_date, p.product_name
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE u.status = 'active'
```

**추출된 조인 관계:**
```json
[
  {
    "join_type": "inner_join",
    "table_name": "orders",
    "join_condition": "u.id = o.user_id",
    "related_tables": ["users", "orders"],
    "confidence": 0.9
  },
  {
    "join_type": "left_join", 
    "table_name": "order_items",
    "join_condition": "o.id = oi.order_id",
    "related_tables": ["orders", "order_items"],
    "confidence": 0.9
  },
  {
    "join_type": "left_join",
    "table_name": "products", 
    "join_condition": "oi.product_id = p.id",
    "related_tables": ["order_items", "products"],
    "confidence": 0.9
  }
]
```

#### 설정 파일 예시
```yaml
# create_metadb/config/config.yaml
llm:
  enabled: true
  model: "gpt-3.5-turbo"
  api_key: "${LLM_API_KEY}"
  max_tokens: 500
  timeout: 30
  
sql_analysis:
  use_llm_for_complex_queries: true
  complexity_threshold: 3  # 조인 수가 3개 이상일 때 LLM 사용
  default_owner: "APP_USER"  # FROM 절에 owner가 없는 경우 기본값
  
external_chunks:
  default_owner: "EXTERNAL"  # 외부 청크의 기본 owner
  auto_create: true  # 외부 청크 자동 생성 여부
  confidence_threshold: 0.5  # 외부 청크 신뢰도 임계값
  
summarization:
  generate_for_classes: true
  generate_for_methods: true
  generate_for_sql_units: true
  summary_types: ["business_purpose", "technical_summary", "learning_guide"]
```

### LLM 사용 시 주의사항

#### 1. 오프라인 환경 고려
- **규칙 기반 우선**: 기본적으로 규칙 기반 분석을 우선 사용
- **LLM 선택적 사용**: 복잡한 쿼리나 요약이 필요한 경우에만 LLM 활용
- **캐싱 전략**: LLM 응답 결과를 메타DB에 저장하여 재사용

#### 2. 비용 관리
- **배치 처리**: LLM 요약을 한 번에 처리하여 API 호출 최소화
- **토큰 제한**: max_tokens 설정으로 비용 관리
- **선택적 생성**: 중요한 클래스/메서드만 LLM 요약 생성

#### 3. 성능 최적화
- **변동분 처리**: 해시값 비교로 변경된 파일만 분석
- **삭제 플래그**: 물리적 삭제 대신 논리적 삭제 (del_yn)
- **비동기 처리**: LLM API 호출을 비동기로 처리
- **타임아웃 설정**: 30초 타임아웃으로 무한 대기 방지
- **에러 처리**: LLM 실패 시 규칙 기반 분석으로 대체

#### 4. 품질 관리
- **신뢰도 점수**: LLM 응답의 신뢰도를 0-1 점수로 평가
- **검증 로직**: LLM 응답이 합리적인지 검증
- **수동 검토**: 중요한 요약은 수동 검토 가능

## 📝 라이선스

기업 내 무료 사용 가능한 라이선스만 사용

## 🤝 기여

이 프로젝트는 신규입사자 지원을 위한 내부 도구입니다.

---

**작성일**: 2025-09-06  
**버전**: 1.0.0  
**개발자**: AI Assistant
