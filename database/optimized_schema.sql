-- 최적화된 메타데이터 스키마 (필수 정보만 저장)
-- ./project 폴더의 파일들을 동적으로 활용하여 성능 최적화

-- 프로젝트 메타데이터 (기본 정보만)
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(100) NOT NULL,
    project_path VARCHAR(500) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_analysis DATETIME,
    total_files INTEGER DEFAULT 0
);

-- 파일 인덱스 (검색을 위한 최소 정보만)
CREATE TABLE IF NOT EXISTS files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,           -- 상대경로
    file_name VARCHAR(200) NOT NULL,
    file_type VARCHAR(20),                     -- java, jsp, sql
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    hash_value VARCHAR(64),                    -- 변경 감지용
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- 코드 구성 요소 (클래스, 메서드 등의 기본 정보만)
CREATE TABLE IF NOT EXISTS components (
    component_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    component_name VARCHAR(200) NOT NULL,
    component_type VARCHAR(20) NOT NULL,       -- class, method, interface
    line_start INTEGER,                        -- 시작 라인
    line_end INTEGER,                          -- 종료 라인
    parent_component_id INTEGER,               -- 상위 컴포넌트 (메서드의 클래스 등)
    hash_value VARCHAR(64),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (file_id) REFERENCES files(file_id),
    FOREIGN KEY (parent_component_id) REFERENCES components(component_id)
);

-- 핵심 관계 정보 (필수적인 관계만)
CREATE TABLE IF NOT EXISTS relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    src_component_id INTEGER NOT NULL,
    dst_component_id INTEGER NOT NULL,
    relationship_type VARCHAR(30) NOT NULL,    -- calls, extends, implements, imports
    confidence FLOAT DEFAULT 1.0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (src_component_id) REFERENCES components(component_id),
    FOREIGN KEY (dst_component_id) REFERENCES components(component_id)
);

-- 비즈니스 분류 (핵심 카테고리만)
CREATE TABLE IF NOT EXISTS business_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    component_id INTEGER NOT NULL,
    domain VARCHAR(50),                        -- user, order, product
    layer VARCHAR(30),                         -- controller, service, dao
    priority INTEGER DEFAULT 3,               -- 1-5 (중요도)
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (component_id) REFERENCES components(component_id)
);

-- 인덱스 생성 (검색 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);
CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);
CREATE INDEX IF NOT EXISTS idx_components_name ON components(component_name);
CREATE INDEX IF NOT EXISTS idx_components_type ON components(component_type);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_business_tags_domain ON business_tags(domain);
CREATE INDEX IF NOT EXISTS idx_business_tags_layer ON business_tags(layer);

-- 뷰 생성 (조회 편의성)
CREATE VIEW IF NOT EXISTS v_component_details AS
SELECT 
    c.component_id,
    c.component_name,
    c.component_type,
    f.file_path,
    f.file_name,
    c.line_start,
    c.line_end,
    bt.domain,
    bt.layer,
    bt.priority
FROM components c
JOIN files f ON c.file_id = f.file_id
LEFT JOIN business_tags bt ON c.component_id = bt.component_id;

-- 관계 뷰
CREATE VIEW IF NOT EXISTS v_relationships AS
SELECT 
    r.relationship_id,
    r.relationship_type,
    src.component_name as src_name,
    src.component_type as src_type,
    srcf.file_path as src_file,
    dst.component_name as dst_name,
    dst.component_type as dst_type,
    dstf.file_path as dst_file,
    r.confidence
FROM relationships r
JOIN components src ON r.src_component_id = src.component_id
JOIN components dst ON r.dst_component_id = dst.component_id
JOIN files srcf ON src.file_id = srcf.file_id
JOIN files dstf ON dst.file_id = dstf.file_id;