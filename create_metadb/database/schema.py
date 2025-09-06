"""
데이터베이스 스키마 정의

최적화된 메타정보 데이터베이스의 스키마를 정의합니다.
"""

class DatabaseSchema:
    """데이터베이스 스키마 정의"""
    
    @staticmethod
    def get_schema_sql() -> str:
        """전체 스키마 SQL 반환"""
        return """
-- 1. 핵심 관계 테이블
CREATE TABLE IF NOT EXISTS core_relationships (
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

-- 2. 비즈니스 분류 테이블
CREATE TABLE IF NOT EXISTS business_classifications (
    classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    component_type VARCHAR(20) NOT NULL,  -- 'class', 'method', 'file', 'sql_unit'
    component_id INTEGER NOT NULL,
    component_name VARCHAR(200) NOT NULL,
    business_domain VARCHAR(50),          -- 'user_management', 'order_processing'
    architecture_layer VARCHAR(30),       -- 'controller', 'service', 'repository', 'entity'
    functional_category VARCHAR(50),      -- 'crud', 'search', 'authentication'
    complexity_level VARCHAR(20),         -- 'beginner', 'intermediate', 'advanced'
    learning_priority INTEGER,            -- 1-5점
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);

-- 3. LLM 요약 테이블
CREATE TABLE IF NOT EXISTS llm_summaries (
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

-- 4. 파일 인덱스 테이블
CREATE TABLE IF NOT EXISTS file_index (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_type VARCHAR(20),                -- 'java', 'jsp', 'xml', 'sql'
    file_size INTEGER,
    package_name VARCHAR(200),            -- Java 패키지명
    class_name VARCHAR(200),              -- 주요 클래스명
    business_context VARCHAR(100),        -- 비즈니스 컨텍스트
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);

-- 5. SQL 단위 인덱스 테이블
CREATE TABLE IF NOT EXISTS sql_unit_index (
    sql_unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    sql_name VARCHAR(200) NOT NULL,
    sql_path VARCHAR(500) NOT NULL,
    sql_type VARCHAR(30),                 -- 'select', 'insert', 'update', 'delete'
    business_domain VARCHAR(50),          -- 비즈니스 도메인
    related_tables TEXT,                  -- 관련 테이블 목록 (JSON)
    join_relationships TEXT,              -- 조인 관계 정보 (JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);

-- 6. 프로젝트 메타데이터 테이블
CREATE TABLE IF NOT EXISTS project_metadata (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(100) NOT NULL,
    project_path VARCHAR(500) NOT NULL,
    total_files INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    total_relationships INTEGER DEFAULT 0,
    last_analysis DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),               -- 변동분 감지용 해시값
    del_yn CHAR(1) DEFAULT 'N'            -- 삭제 플래그 (Y: 삭제됨, N: 유효)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_core_relationships_src ON core_relationships(src_name, src_type);
CREATE INDEX IF NOT EXISTS idx_core_relationships_dst ON core_relationships(dst_name, dst_type);
CREATE INDEX IF NOT EXISTS idx_core_relationships_type ON core_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_core_relationships_del_yn ON core_relationships(del_yn);

CREATE INDEX IF NOT EXISTS idx_business_classifications_component ON business_classifications(component_name, component_type);
CREATE INDEX IF NOT EXISTS idx_business_classifications_domain ON business_classifications(business_domain);
CREATE INDEX IF NOT EXISTS idx_business_classifications_layer ON business_classifications(architecture_layer);
CREATE INDEX IF NOT EXISTS idx_business_classifications_del_yn ON business_classifications(del_yn);

CREATE INDEX IF NOT EXISTS idx_llm_summaries_target ON llm_summaries(target_name, target_type);
CREATE INDEX IF NOT EXISTS idx_llm_summaries_type ON llm_summaries(summary_type);
CREATE INDEX IF NOT EXISTS idx_llm_summaries_del_yn ON llm_summaries(del_yn);

CREATE INDEX IF NOT EXISTS idx_file_index_path ON file_index(file_path);
CREATE INDEX IF NOT EXISTS idx_file_index_name ON file_index(file_name);
CREATE INDEX IF NOT EXISTS idx_file_index_type ON file_index(file_type);
CREATE INDEX IF NOT EXISTS idx_file_index_del_yn ON file_index(del_yn);

CREATE INDEX IF NOT EXISTS idx_sql_unit_index_name ON sql_unit_index(sql_name);
CREATE INDEX IF NOT EXISTS idx_sql_unit_index_type ON sql_unit_index(sql_type);
CREATE INDEX IF NOT EXISTS idx_sql_unit_index_domain ON sql_unit_index(business_domain);
CREATE INDEX IF NOT EXISTS idx_sql_unit_index_del_yn ON sql_unit_index(del_yn);

-- 삭제된 데이터 조회를 위한 뷰
CREATE VIEW IF NOT EXISTS v_valid_relationships AS
SELECT * FROM core_relationships 
WHERE NVL(del_yn, 'N') <> 'Y';

CREATE VIEW IF NOT EXISTS v_valid_classifications AS
SELECT * FROM business_classifications 
WHERE NVL(del_yn, 'N') <> 'Y';

CREATE VIEW IF NOT EXISTS v_valid_summaries AS
SELECT * FROM llm_summaries 
WHERE NVL(del_yn, 'N') <> 'Y';

CREATE VIEW IF NOT EXISTS v_valid_files AS
SELECT * FROM file_index 
WHERE NVL(del_yn, 'N') <> 'Y';

CREATE VIEW IF NOT EXISTS v_valid_sql_units AS
SELECT * FROM sql_unit_index 
WHERE NVL(del_yn, 'N') <> 'Y';
"""
    
    @staticmethod
    def get_clean_schema_sql() -> str:
        """스키마 정리 SQL 반환"""
        return """
-- 모든 테이블 삭제
DROP VIEW IF EXISTS v_valid_relationships;
DROP VIEW IF EXISTS v_valid_classifications;
DROP VIEW IF EXISTS v_valid_summaries;
DROP VIEW IF EXISTS v_valid_files;
DROP VIEW IF EXISTS v_valid_sql_units;

DROP TABLE IF EXISTS core_relationships;
DROP TABLE IF EXISTS business_classifications;
DROP TABLE IF EXISTS llm_summaries;
DROP TABLE IF EXISTS file_index;
DROP TABLE IF EXISTS sql_unit_index;
DROP TABLE IF EXISTS project_metadata;
"""
    
    @staticmethod
    def get_clear_deleted_sql() -> str:
        """삭제된 데이터 정리 SQL 반환"""
        return """
-- del_yn='Y'인 데이터만 물리적 삭제
DELETE FROM core_relationships WHERE del_yn = 'Y';
DELETE FROM business_classifications WHERE del_yn = 'Y';
DELETE FROM llm_summaries WHERE del_yn = 'Y';
DELETE FROM file_index WHERE del_yn = 'Y';
DELETE FROM sql_unit_index WHERE del_yn = 'Y';
DELETE FROM project_metadata WHERE del_yn = 'Y';
"""
