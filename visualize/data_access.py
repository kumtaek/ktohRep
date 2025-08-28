# visualize/data_access.py
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

# Add phase1 to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
phase1_path = project_root / "phase1" / "src"
sys.path.insert(0, str(phase1_path))

from models.database import DatabaseManager, File, Class, Method, SqlUnit, Join, RequiredFilter, Edge, DbTable, DbColumn, DbPk
from sqlalchemy import and_, or_, func
import yaml


class VizDB:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = project_root / "config" / "config.yaml"
        
        self.config = self._load_config(config_path)
        self.dbm = DatabaseManager(self.config)
        self.dbm.initialize()

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            # Return default SQLite config
            return {
                'database': {
                    'type': 'sqlite',
                    'sqlite': {
                        'path': str(project_root / "data" / "metadata.db")
                    }
                }
            }

    def session(self):
        """Get database session"""
        return self.dbm.get_session()

    def load_project_files(self, project_id: int) -> List[File]:
        """Load all files for a project"""
        session = self.session()
        try:
            return session.query(File).filter(File.project_id == project_id).all()
        finally:
            session.close()

    def fetch_edges(self, project_id: int, kinds: List[str] = None, min_conf: float = 0.0) -> List[Edge]:
        """Fetch edges with optional filtering by kind and confidence"""
        session = self.session()
        try:
            # Build base query - join with File to filter by project
            query = session.query(Edge).join(File, 
                or_(
                    and_(Edge.src_type == 'file', Edge.src_id == File.file_id),
                    and_(Edge.src_type == 'class', Edge.src_id.in_(
                        session.query(Class.class_id).join(File).filter(File.project_id == project_id).subquery()
                    )),
                    and_(Edge.src_type == 'method', Edge.src_id.in_(
                        session.query(Method.method_id).join(Class).join(File).filter(File.project_id == project_id).subquery()
                    )),
                    and_(Edge.src_type == 'sql_unit', Edge.src_id.in_(
                        session.query(SqlUnit.sql_id).join(File).filter(File.project_id == project_id).subquery()
                    ))
                )
            ).filter(File.project_id == project_id)
            
            # Apply confidence filter
            if min_conf > 0:
                query = query.filter(Edge.confidence >= min_conf)
            
            # Apply kind filter
            if kinds:
                query = query.filter(Edge.edge_kind.in_(kinds))
                
            return query.all()
        finally:
            session.close()

    def fetch_tables(self) -> List[DbTable]:
        """Fetch all database tables"""
        session = self.session()
        try:
            return session.query(DbTable).all()
        finally:
            session.close()

    def fetch_pk(self) -> List[DbPk]:
        """Fetch all primary key information"""
        session = self.session()
        try:
            return session.query(DbPk).all()
        finally:
            session.close()

    def fetch_joins_for_project(self, project_id: int) -> List[Join]:
        """Fetch all joins for a specific project"""
        session = self.session()
        try:
            return session.query(Join).join(SqlUnit).join(File).\
                filter(File.project_id == project_id).all()
        finally:
            session.close()

    def fetch_methods_by_project(self, project_id: int) -> List[Method]:
        """Fetch all methods for a project"""
        session = self.session()
        try:
            return session.query(Method).join(Class).join(File).\
                filter(File.project_id == project_id).all()
        finally:
            session.close()

    def fetch_sql_units_by_project(self, project_id: int) -> List[SqlUnit]:
        """Fetch all SQL units for a project"""
        session = self.session()
        try:
            return session.query(SqlUnit).join(File).\
                filter(File.project_id == project_id).all()
        finally:
            session.close()

    def get_node_details(self, node_type: str, node_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific node"""
        session = self.session()
        try:
            if node_type == 'method':
                method = session.query(Method).filter(Method.method_id == node_id).first()
                if method:
                    cls = session.query(Class).filter(Class.class_id == method.class_id).first()
                    file = session.query(File).filter(File.file_id == cls.file_id).first() if cls else None
                    return {
                        'name': method.name,
                        'signature': method.signature,
                        'class': cls.fqn if cls else None,
                        'file': file.path if file else None,
                        'line': method.start_line
                    }
            elif node_type == 'class':
                cls = session.query(Class).filter(Class.class_id == node_id).first()
                if cls:
                    file = session.query(File).filter(File.file_id == cls.file_id).first()
                    return {
                        'name': cls.name,
                        'fqn': cls.fqn,
                        'file': file.path if file else None,
                        'line': cls.start_line
                    }
            elif node_type == 'file':
                file = session.query(File).filter(File.file_id == node_id).first()
                if file:
                    return {
                        'path': file.path,
                        'language': file.language,
                        'loc': file.loc
                    }
            elif node_type == 'sql_unit':
                sql = session.query(SqlUnit).filter(SqlUnit.sql_id == node_id).first()
                if sql:
                    file = session.query(File).filter(File.file_id == sql.file_id).first()
                    return {
                        'stmt_id': sql.stmt_id,
                        'mapper_ns': sql.mapper_ns,
                        'stmt_kind': sql.stmt_kind,
                        'file': file.path if file else None,
                        'line': sql.start_line
                    }
            elif node_type == 'table':
                # For table nodes, node_id might be the table name
                return {
                    'name': node_id,
                    'type': 'table'
                }
        finally:
            session.close()
        return None