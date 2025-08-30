# visualize/data_access.py
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

# Add phase1 to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
phase1_path = project_root / "phase1"
sys.path.insert(0, str(phase1_path))

from models.database import DatabaseManager, File, Class, Method, SqlUnit, Join, RequiredFilter, Edge, DbTable, DbColumn, DbPk, VulnerabilityFix, Project
from sqlalchemy import and_, or_, func
import yaml


class VizDB:
    def __init__(self, config: Dict[str, Any], project_name: Optional[str] = None):
        self.config = config
        self.project_name = project_name
        
        # 새로운 database config 구조에서 project database 사용
        if 'project' in config.get('database', {}):
            # 새로운 구조: database.project
            project_db_config = config['database']['project'].copy()
            db_config = {'database': project_db_config}
        else:
            # 기존 구조 호환성
            db_config = config
        
        self.dbm = DatabaseManager(db_config)
        self.dbm.initialize()

    def session(self):
        """Get database session"""
        return self.dbm.get_session()

    def get_project_id_by_name(self, project_name: str) -> Optional[int]:
        """Get project_id by project name"""
        session = self.session()
        try:
            project = session.query(Project).filter(Project.name == project_name).first()
            return project.project_id if project else None
        finally:
            session.close()

    def load_project_files(self, project_id: int) -> List[File]:
        """Load all files for a project"""
        session = self.session()
        try:
            return session.query(File).filter(File.project_id == project_id).all()
        finally:
            session.close()

    def _get_project_scoped_ids(self, session, project_id: int) -> Dict[str, List[int]]:
        """Get all project-scoped IDs for efficient edge filtering"""
        # Get file IDs
        file_ids = [f.file_id for f in session.query(File.file_id).filter(File.project_id == project_id).all()]
        
        # Get class IDs
        class_ids = [c.class_id for c in session.query(Class.class_id).join(File).filter(File.project_id == project_id).all()]
        
        # Get method IDs  
        method_ids = [m.method_id for m in session.query(Method.method_id).join(Class).join(File).filter(File.project_id == project_id).all()]
        
        # Get SQL unit IDs
        sql_ids = [s.sql_id for s in session.query(SqlUnit.sql_id).join(File).filter(File.project_id == project_id).all()]
        
        return {
            'file_ids': file_ids,
            'class_ids': class_ids,
            'method_ids': method_ids,
            'sql_ids': sql_ids
        }

    def fetch_edges(self, project_id: int, kinds: List[str] = None, min_conf: float = 0.0) -> List[Edge]:
        """Fetch edges with optional filtering by kind and confidence (optimized)"""
        session = self.session()
        try:
            # Step 1: Get all project-scoped IDs in memory (much faster)
            project_ids = self._get_project_scoped_ids(session, project_id)
            
            # Step 2: Filter edges using simple IN clauses
            query = session.query(Edge).filter(
                or_(
                    and_(Edge.src_type == 'file', Edge.src_id.in_(project_ids['file_ids'])),
                    and_(Edge.src_type == 'class', Edge.src_id.in_(project_ids['class_ids'])),
                    and_(Edge.src_type == 'method', Edge.src_id.in_(project_ids['method_ids'])),
                    and_(Edge.src_type == 'sql_unit', Edge.src_id.in_(project_ids['sql_ids']))
                )
            )
            
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
    
    def fetch_columns(self) -> List[DbColumn]:
        """Fetch all column information"""
        session = self.session()
        try:
            return session.query(DbColumn).all()
        finally:
            session.close()
    
    def fetch_sample_joins_for_table(self, table_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch sample join information for a specific table"""
        session = self.session()
        try:
            # Get join patterns for this table - both as left and right table
            joins = session.query(Join).join(SqlUnit).join(File).filter(
                or_(
                    func.upper(Join.left_table).like(f'%{table_id}%'),  # Simplified for now
                    func.upper(Join.right_table).like(f'%{table_id}%')
                )
            ).limit(limit * 2).all()  # Get more to filter and rank
            
            # Process and rank joins by frequency
            join_patterns = {}
            for join in joins:
                key = f"{join.left_table}|{join.right_table}|{join.left_column}|{join.right_column}"
                if key not in join_patterns:
                    join_patterns[key] = {
                        'left_table': join.left_table,
                        'right_table': join.right_table,
                        'left_column': join.left_column,
                        'right_column': join.right_column,
                        'frequency': 0,
                        'confidence': join.confidence
                    }
                join_patterns[key]['frequency'] += 1
                join_patterns[key]['confidence'] = max(join_patterns[key]['confidence'], join.confidence)
            
            # Sort by frequency and return top N
            sorted_joins = sorted(join_patterns.values(), key=lambda x: (-x['frequency'], -x['confidence']))
            return sorted_joins[:limit]
            
        finally:
            session.close()

    def fetch_required_filters(self, project_id: int, sql_id: int = None) -> List[RequiredFilter]:
        """Fetch required filters, optionally for a specific SQL unit"""
        session = self.session()
        try:
            query = session.query(RequiredFilter).join(SqlUnit).join(File).filter(File.project_id == project_id)
            
            if sql_id:
                query = query.filter(RequiredFilter.sql_id == sql_id)
                
            return query.all()
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

    def fetch_vulnerabilities(self, project_id: int) -> List[VulnerabilityFix]:
        """Fetch vulnerability fixes related to a project by resolving target relations.

        Joins per target_type to ensure entries belong to the given project:
        - file -> File.project_id
        - class -> Class -> File.project_id
        - method -> Method -> Class -> File.project_id
        - sql_unit -> SqlUnit -> File.project_id
        """
        session = self.session()
        try:
            results: List[VulnerabilityFix] = []

            # file targets
            q_file = session.query(VulnerabilityFix).join(
                File, (VulnerabilityFix.target_type == 'file') & (VulnerabilityFix.target_id == File.file_id)
            ).filter(File.project_id == project_id)
            results.extend(q_file.all())

            # class targets
            q_class = session.query(VulnerabilityFix).join(
                Class, (VulnerabilityFix.target_type == 'class') & (VulnerabilityFix.target_id == Class.class_id)
            ).join(File, Class.file_id == File.file_id).filter(File.project_id == project_id)
            results.extend(q_class.all())

            # method targets
            q_method = session.query(VulnerabilityFix).join(
                Method, (VulnerabilityFix.target_type == 'method') & (VulnerabilityFix.target_id == Method.method_id)
            ).join(Class, Method.class_id == Class.class_id).join(File, Class.file_id == File.file_id).\
                filter(File.project_id == project_id)
            results.extend(q_method.all())

            # sql_unit targets
            q_sql = session.query(VulnerabilityFix).join(
                SqlUnit, (VulnerabilityFix.target_type == 'sql_unit') & (VulnerabilityFix.target_id == SqlUnit.sql_id)
            ).join(File, SqlUnit.file_id == File.file_id).filter(File.project_id == project_id)
            results.extend(q_sql.all())

            return results
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
                # Handle table nodes by table_id or name lookup
                if isinstance(node_id, int):
                    # Lookup by table_id
                    table = session.query(DbTable).filter(DbTable.table_id == node_id).first()
                else:
                    # Lookup by table name (fallback)
                    table = session.query(DbTable).filter(DbTable.table_name.ilike(f'%{node_id}%')).first()
                
                if table:
                    return {
                        'name': f"{table.owner}.{table.table_name}" if table.owner else table.table_name,
                        'type': 'table',
                        'owner': table.owner,
                        'table_name': table.table_name,
                        'table_id': table.table_id,
                        'status': getattr(table, 'status', 'VALID')
                    }
                else:
                    # Fallback for unknown table
                    return {
                        'name': str(node_id),
                        'type': 'table'
                    }
        finally:
            session.close()
        return None
