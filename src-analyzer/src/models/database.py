"""
Database models for Source Analyzer metadata storage
Based on PRD v2.0 schema specification
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Real, Boolean,
    ForeignKey, Index, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Project(Base):
    """프로젝트 정보"""
    __tablename__ = 'projects'
    
    project_id = Column(Integer, primary_key=True)
    root_path = Column(Text, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="project")


class File(Base):
    """파일 정보"""
    __tablename__ = 'files'
    
    file_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    path = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    hash = Column(String(64), nullable=True)  # SHA-256 hash
    loc = Column(Integer, nullable=True)  # Lines of Code
    mtime = Column(DateTime, nullable=True)  # Modification time
    
    # Relationships
    project = relationship("Project", back_populates="files")
    classes = relationship("JavaClass", back_populates="file")
    sql_units = relationship("SQLUnit", back_populates="file")


class JavaClass(Base):
    """Java 클래스 정보"""
    __tablename__ = 'classes'
    
    class_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    fqn = Column(Text, nullable=True)  # Fully Qualified Name
    name = Column(String(255), nullable=False)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    modifiers = Column(Text, nullable=True)  # public, private, etc.
    annotations = Column(Text, nullable=True)  # JSON string of annotations
    
    # Relationships
    file = relationship("File", back_populates="classes")
    methods = relationship("JavaMethod", back_populates="java_class")


class JavaMethod(Base):
    """Java 메소드 정보"""
    __tablename__ = 'methods'
    
    method_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.class_id'), nullable=False)
    name = Column(String(255), nullable=False)
    signature = Column(Text, nullable=True)
    return_type = Column(String(255), nullable=True)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    annotations = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    java_class = relationship("JavaClass", back_populates="methods")


class SQLUnit(Base):
    """SQL 유닛 (MyBatis 매퍼, 직접 SQL 등)"""
    __tablename__ = 'sql_units'
    
    sql_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    origin = Column(String(100), nullable=True)  # mybatis, direct, etc.
    mapper_ns = Column(String(255), nullable=True)  # MyBatis namespace
    stmt_id = Column(String(255), nullable=True)  # Statement ID
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    stmt_kind = Column(String(50), nullable=True)  # select, insert, update, delete, procedure, function
    normalized_fingerprint = Column(Text, nullable=True)  # Structure-based fingerprint instead of original SQL
    
    # Relationships
    file = relationship("File", back_populates="sql_units")
    joins = relationship("Join", back_populates="sql_unit")
    required_filters = relationship("RequiredFilter", back_populates="sql_unit")


class DBTable(Base):
    """데이터베이스 테이블 정보 (CSV에서 로드)"""
    __tablename__ = 'db_tables'
    
    table_id = Column(Integer, primary_key=True)
    owner = Column(String(128), nullable=True)
    table_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=True)
    
    # Relationships
    columns = relationship("DBColumn", back_populates="table")
    primary_keys = relationship("DBPrimaryKey", back_populates="table")


class DBColumn(Base):
    """데이터베이스 컬럼 정보"""
    __tablename__ = 'db_columns'
    
    column_id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('db_tables.table_id'), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(128), nullable=True)
    nullable = Column(String(10), nullable=True)  # Y/N
    
    # Relationships
    table = relationship("DBTable", back_populates="columns")


class DBPrimaryKey(Base):
    """데이터베이스 기본키 정보"""
    __tablename__ = 'db_pk'
    
    table_id = Column(Integer, ForeignKey('db_tables.table_id'), primary_key=True)
    column_name = Column(String(255), primary_key=True)
    pk_pos = Column(Integer, nullable=True)  # Primary key position
    
    # Relationships
    table = relationship("DBTable", back_populates="primary_keys")


class DBView(Base):
    """데이터베이스 뷰 정보"""
    __tablename__ = 'db_views'
    
    view_id = Column(Integer, primary_key=True)
    owner = Column(String(128), nullable=True)
    view_name = Column(String(255), nullable=False)
    text = Column(Text, nullable=True)  # View definition SQL


class Edge(Base):
    """의존성 및 호출 그래프 엣지"""
    __tablename__ = 'edges'
    
    edge_id = Column(Integer, primary_key=True)
    src_type = Column(String(50), nullable=False)  # method, class, sql_unit, table, etc.
    src_id = Column(Integer, nullable=False)
    dst_type = Column(String(50), nullable=False)
    dst_id = Column(Integer, nullable=False)
    edge_kind = Column(String(100), nullable=False)  # call, use_table, use_column, call_sql, calls_sp, references_view, write_table, extends, implements
    confidence = Column(Real, nullable=True)  # 0.0 to 1.0


class Join(Base):
    """조인 조건 정보"""
    __tablename__ = 'joins'
    
    join_id = Column(Integer, primary_key=True)
    sql_id = Column(Integer, ForeignKey('sql_units.sql_id'), nullable=False)
    l_table = Column(String(255), nullable=True)
    l_col = Column(String(255), nullable=True)
    op = Column(String(10), nullable=True)  # =, <>, <, >, etc.
    r_table = Column(String(255), nullable=True)
    r_col = Column(String(255), nullable=True)
    inferred_pkfk = Column(Integer, default=0)  # 0 or 1
    confidence = Column(Real, nullable=True)
    
    # Relationships
    sql_unit = relationship("SQLUnit", back_populates="joins")


class RequiredFilter(Base):
    """필수 필터 조건"""
    __tablename__ = 'required_filters'
    
    filter_id = Column(Integer, primary_key=True)
    sql_id = Column(Integer, ForeignKey('sql_units.sql_id'), nullable=False)
    table_name = Column(String(255), nullable=True)
    column_name = Column(String(255), nullable=True)
    op = Column(String(10), nullable=True)  # =, <>, IN, etc.
    value_repr = Column(String(500), nullable=True)  # 'N', :param, etc.
    always_applied = Column(Integer, default=0)  # 0 or 1
    confidence = Column(Real, nullable=True)
    
    # Relationships
    sql_unit = relationship("SQLUnit", back_populates="required_filters")


class Summary(Base):
    """요약 및 분석 결과"""
    __tablename__ = 'summaries'
    
    summary_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)  # method, class, sql_unit, table, etc.
    target_id = Column(Integer, nullable=False)
    summary_type = Column(String(100), nullable=False)  # logic, vuln, perf, db_comment_suggestion
    lang = Column(String(10), nullable=True)  # ko, en
    content = Column(Text, nullable=True)
    confidence = Column(Real, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EnrichmentLog(Base):
    """LLM 보강 이력"""
    __tablename__ = 'enrichment_logs'
    
    enrich_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    pre_conf = Column(Real, nullable=True)  # Confidence before LLM
    post_conf = Column(Real, nullable=True)  # Confidence after LLM
    model = Column(String(100), nullable=True)  # qwen2.5-7b, qwen2.5-32b-quant
    prompt_id = Column(String(100), nullable=True)
    params = Column(Text, nullable=True)  # JSON string of parameters
    created_at = Column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    """임베딩용 청크"""
    __tablename__ = 'chunks'
    
    chunk_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    token_count = Column(Integer, nullable=True)
    hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Embedding(Base):
    """임베딩 벡터 정보"""
    __tablename__ = 'embeddings'
    
    chunk_id = Column(Integer, ForeignKey('chunks.chunk_id'), primary_key=True)
    model = Column(String(100), nullable=True)
    dim = Column(Integer, nullable=True)  # Vector dimension
    faiss_vector_id = Column(Integer, nullable=True)  # FAISS index ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunk = relationship("Chunk")


# Create indexes as specified in PRD
Index('idx_edges_src', Edge.src_type, Edge.src_id)
Index('idx_edges_dst', Edge.dst_type, Edge.dst_id)  
Index('idx_sql_units_file', SQLUnit.file_id)
Index('idx_joins_sql', Join.sql_id)
Index('idx_filters_sql', RequiredFilter.sql_id)


def create_database_engine(database_url: str = "sqlite:///./data/metadata.db"):
    """Create SQLAlchemy engine and return engine, SessionLocal"""
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def init_database(engine):
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # Test database creation
    engine, SessionLocal = create_database_engine()
    init_database(engine)
    print("Database initialized successfully!")