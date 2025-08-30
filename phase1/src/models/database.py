"""
Database models for metadata storage following PRD v4.0 schema.
Supports both SQLite (development) and Oracle 11g (production).
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean, 
    DateTime, ForeignKey, Index, CLOB
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, synonym
from datetime import datetime
import json
from typing import Dict, List, Optional, Any

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    project_id = Column(Integer, primary_key=True)
    root_path = Column(Text, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = 'files'
    
    file_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    path = Column(Text, nullable=False)
    language = Column(String(50))
    hash = Column(String(64))  # SHA-256 hash for change detection
    loc = Column(Integer)  # Lines of code
    mtime = Column(DateTime)  # Modification time
    
    # Relationships
    project = relationship("Project", back_populates="files")
    classes = relationship("Class", back_populates="file", cascade="all, delete-orphan")
    sql_units = relationship("SqlUnit", back_populates="file", cascade="all, delete-orphan")

class Class(Base):
    __tablename__ = 'classes'
    
    class_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    fqn = Column(Text)  # Fully qualified name
    name = Column(String(255), nullable=False)
    start_line = Column(Integer)
    end_line = Column(Integer)
    modifiers = Column(Text)  # JSON array of modifiers
    annotations = Column(Text)  # JSON array of annotations
    
    # Relationships  
    file = relationship("File", back_populates="classes")
    methods = relationship("Method", back_populates="class_", cascade="all, delete-orphan")

class Method(Base):
    __tablename__ = 'methods'
    
    method_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.class_id'), nullable=False)
    name = Column(String(255), nullable=False)
    signature = Column(Text)
    return_type = Column(String(255))
    start_line = Column(Integer)
    end_line = Column(Integer)
    annotations = Column(Text)  # JSON array of annotations
    parameters = Column(Text)   # JSON or string-joined parameter list
    modifiers = Column(Text)    # JSON array of modifiers
    
    # Relationships
    class_ = relationship("Class", back_populates="methods")

class SqlUnit(Base):
    __tablename__ = 'sql_units'
    
    sql_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    origin = Column(String(50))  # mybatis, jsp, etc.
    mapper_ns = Column(String(255))  # MyBatis namespace
    stmt_id = Column(String(255))  # Statement ID
    start_line = Column(Integer)
    end_line = Column(Integer)
    stmt_kind = Column(String(50))  # select, insert, update, delete, procedure, function
    normalized_fingerprint = Column(Text)  # Structural fingerprint (not original SQL)
    
    # Relationships
    file = relationship("File", back_populates="sql_units")
    joins = relationship("Join", back_populates="sql_unit", cascade="all, delete-orphan")
    filters = relationship("RequiredFilter", back_populates="sql_unit", cascade="all, delete-orphan")

class DbTable(Base):
    __tablename__ = 'db_tables'
    
    table_id = Column(Integer, primary_key=True)
    owner = Column(String(128))
    table_name = Column(String(128), nullable=False)
    status = Column(String(50))
    table_comment = Column(Text)  # Table comment/description
    
    # Relationships
    columns = relationship("DbColumn", back_populates="table", cascade="all, delete-orphan")
    pk_columns = relationship("DbPk", back_populates="table", cascade="all, delete-orphan")

class DbColumn(Base):
    __tablename__ = 'db_columns'
    
    column_id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('db_tables.table_id'), nullable=False)
    column_name = Column(String(128), nullable=False)
    data_type = Column(String(128))
    nullable = Column(String(1))  # Y/N
    column_comment = Column(Text)  # Column comment/description
    
    # Relationships
    table = relationship("DbTable", back_populates="columns")

class DbPk(Base):
    __tablename__ = 'db_pk'
    
    table_id = Column(Integer, ForeignKey('db_tables.table_id'), primary_key=True)
    column_name = Column(String(128), primary_key=True)
    pk_pos = Column(Integer)  # Position in composite key
    
    # Relationships
    table = relationship("DbTable", back_populates="pk_columns")

class DbView(Base):
    __tablename__ = 'db_views'
    
    view_id = Column(Integer, primary_key=True)
    owner = Column(String(128))
    view_name = Column(String(128), nullable=False)
    text = Column(CLOB)  # View definition SQL

class Edge(Base):
    __tablename__ = 'edges'
    
    edge_id = Column(Integer, primary_key=True)
    src_type = Column(String(50), nullable=False)  # method, class, sql_unit, etc.
    src_id = Column(Integer, nullable=False)
    dst_type = Column(String(50), nullable=False)
    dst_id = Column(Integer, nullable=True)  # Allow NULL for unresolved edges
    edge_kind = Column(String(50), nullable=False)  # call, use_table, use_column, etc.
    confidence = Column(Float, default=1.0)
    meta = Column(Text)  # JSON metadata for hints (e.g., called_name)
    created_at = Column(DateTime, default=datetime.utcnow)

# Recommended indexes for performance
Index('ix_edges_src', Edge.src_type, Edge.src_id)
Index('ix_edges_dst', Edge.dst_type, Edge.dst_id)
Index('ix_edges_kind', Edge.edge_kind)

class Join(Base):
    __tablename__ = 'joins'
    
    join_id = Column(Integer, primary_key=True)
    sql_id = Column(Integer, ForeignKey('sql_units.sql_id'), nullable=False)
    l_table = Column(String(128))  # Left table
    l_col = Column(String(128))    # Left column
    op = Column(String(10))        # Operator (=, !=, etc.)
    r_table = Column(String(128))  # Right table  
    r_col = Column(String(128))    # Right column
    inferred_pkfk = Column(Integer, default=0)  # 1 if inferred PK-FK relationship
    confidence = Column(Float, default=1.0)
    
    # Relationships
    sql_unit = relationship("SqlUnit", back_populates="joins")

    # SQLAlchemy synonyms for visualize layer compatibility
    left_table = synonym('l_table')
    left_column = synonym('l_col')
    right_table = synonym('r_table')
    right_column = synonym('r_col')

class RequiredFilter(Base):
    __tablename__ = 'required_filters'
    
    filter_id = Column(Integer, primary_key=True)
    sql_id = Column(Integer, ForeignKey('sql_units.sql_id'), nullable=False)
    table_name = Column(String(128))
    column_name = Column(String(128))
    op = Column(String(10))  # =, !=, LIKE, etc.
    value_repr = Column(String(255))  # 'N', :param, etc.
    always_applied = Column(Integer, default=0)  # 1 if always applied
    confidence = Column(Float, default=1.0)
    
    # Relationships
    sql_unit = relationship("SqlUnit", back_populates="filters")

class Summary(Base):
    __tablename__ = 'summaries'
    
    summary_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)  # method, class, sql_unit, etc.
    target_id = Column(Integer, nullable=False)
    summary_type = Column(String(50), nullable=False)  # logic, vuln, perf, db_comment_suggestion
    lang = Column(String(10))  # ko, en
    content = Column(Text)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class EnrichmentLog(Base):
    __tablename__ = 'enrichment_logs'
    
    enrich_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    pre_conf = Column(Float)   # Confidence before LLM enrichment
    post_conf = Column(Float)  # Confidence after LLM enrichment
    model = Column(String(100))  # LLM model used
    prompt_id = Column(String(100))  # Prompt template ID
    params = Column(Text)  # JSON parameters used
    created_at = Column(DateTime, default=datetime.utcnow)

class Chunk(Base):
    __tablename__ = 'chunks'
    
    chunk_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    content = Column(Text)  # Chunked content for embedding
    token_count = Column(Integer)
    hash = Column(String(64))  # Content hash
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = 'embeddings'
    
    chunk_id = Column(Integer, ForeignKey('chunks.chunk_id'), primary_key=True)
    model = Column(String(100), nullable=False)  # Embedding model name
    dim = Column(Integer)  # Vector dimension
    faiss_vector_id = Column(Integer)  # ID in FAISS index
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunk = relationship("Chunk", back_populates="embedding")

# (Optional) Java import declarations to assist resolution
class JavaImport(Base):
    __tablename__ = 'java_imports'
    
    import_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    class_fqn = Column(Text)  # imported FQN
    static = Column(Integer, default=0)

class EdgeHint(Base):
    """Edge hints for resolving relationships during build phase"""
    __tablename__ = 'edge_hints'
    
    hint_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    src_type = Column(String(50), nullable=False)   # 'method', 'file', 'sql_unit'
    src_id = Column(Integer, nullable=False)
    hint_type = Column(String(50), nullable=False)  # 'method_call', 'jsp_include', 'mybatis_include'
    hint = Column(Text, nullable=False)             # JSON: { called_name, arg_count, target_path, namespace, line, ... }
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

class VulnerabilityFix(Base):
    __tablename__ = 'vulnerability_fixes'
    
    fix_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    vulnerability_type = Column(String(100))  # sql_injection, xss, etc.
    severity = Column(String(20))  # critical, high, medium, low
    owasp_category = Column(String(10))  # A01, A02, etc.
    cwe_id = Column(String(20))  # CWE-89, CWE-79, etc.
    reference_urls = Column(Text)  # JSON array of URLs
    description = Column(Text)
    fix_description = Column(Text)
    original_code = Column(Text)  # Vulnerable code snippet
    fixed_code = Column(Text)     # Fixed code snippet
    start_line = Column(Integer)
    end_line = Column(Integer)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class CodeMetric(Base):
    __tablename__ = 'code_metrics'
    
    metric_id = Column(Integer, primary_key=True)
    target_type = Column(String(50), nullable=False)  # file, class, method
    target_id = Column(Integer, nullable=False)
    metric_type = Column(String(50), nullable=False)  # complexity, loc, duplication
    metric_name = Column(String(100), nullable=False)  # cyclomatic_complexity, lines_of_code
    value = Column(Float, nullable=False)
    threshold = Column(Float)  # Warning threshold
    severity = Column(String(20))  # info, warning, error
    created_at = Column(DateTime, default=datetime.utcnow)

class Duplicate(Base):
    __tablename__ = 'duplicates'
    
    duplicate_id = Column(Integer, primary_key=True)
    hash_signature = Column(String(64), nullable=False)  # Hash of duplicate code block
    token_count = Column(Integer)
    line_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    instances = relationship("DuplicateInstance", back_populates="duplicate", cascade="all, delete-orphan")

class DuplicateInstance(Base):
    __tablename__ = 'duplicate_instances'
    
    instance_id = Column(Integer, primary_key=True)
    duplicate_id = Column(Integer, ForeignKey('duplicates.duplicate_id'), nullable=False)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    
    # Relationships
    duplicate = relationship("Duplicate", back_populates="instances")
    file = relationship("File")

class ParseResultModel(Base):
    __tablename__ = 'parse_results'
    
    result_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
    parser_type = Column(String(50), nullable=False)  # javalang, tree_sitter, antlr
    success = Column(Boolean, default=True)
    parse_time = Column(Float)  # Seconds
    ast_complete = Column(Boolean, default=False)
    partial_ast = Column(Boolean, default=False)
    fallback_used = Column(Boolean, default=False)
    error_message = Column(Text)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File")

# Indexes for performance
Index('idx_edges_src', Edge.src_type, Edge.src_id)
Index('idx_edges_dst', Edge.dst_type, Edge.dst_id)
Index('idx_sql_units_file', SqlUnit.file_id)
Index('idx_joins_sql', Join.sql_id)
Index('idx_filters_sql', RequiredFilter.sql_id)
Index('idx_vuln_fixes_target', VulnerabilityFix.target_type, VulnerabilityFix.target_id)
Index('idx_edge_hints_project', EdgeHint.project_id)
Index('idx_edge_hints_type', EdgeHint.hint_type)

class DatabaseManager:
    """Database manager for handling SQLite/Oracle connections and operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = None
        self.Session = None
        
    def initialize(self):
        """Initialize database connection and create tables."""
        db_config = self.config['database']
        
        db_url = ""
        engine_args = {}

        if db_config['type'] == 'sqlite':
            sqlite_config = db_config['sqlite']
            db_url = f"sqlite:///{sqlite_config['path']}"
            
            # Enable WAL mode for better concurrency
            if sqlite_config.get('wal_mode', False):
                engine_args['connect_args'] = {'check_same_thread': False}
                
        elif db_config['type'] == 'oracle':
            oracle_config = db_config['oracle']
            db_url = (f"oracle+cx_oracle://{oracle_config['username']}:"
                     f"{oracle_config['password']}@{oracle_config['host']}:"
                     f"{oracle_config['port']}/{oracle_config['service_name']}")
            engine_args = {}
        else:
            raise ValueError(f"Unsupported database type: {db_config['type']}")
            
        self.engine = create_engine(db_url, **engine_args)
        
        # Create all tables first
        Base.metadata.create_all(self.engine)
        
        # Thread-local scoped session for better concurrency
        self.Session = scoped_session(sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        ))
        
    def get_session(self):
        """Get a new database session."""
        return self.Session()
        
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
