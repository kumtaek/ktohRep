Add fetch_relatedness method and update graph
8월 30일
kumtaek/ktohRep
master
+34
-4

아카이브에 보관

공유하기

PR 만들기


* File: `visualize/data_access.py`
* Add `fetch_relatedness(project_id, min_score)` returning `Relatedness` records.
* In `build_dependency_graph_json`, call `fetch_relatedness` and append edges with `kind='related'` and `confidence=score`.
* Ensure edges include source/target IDs matching existing node IDs.
복사
Summary
Introduced a fetch_relatedness helper in VizDB to retrieve relatedness records for a project while optionally filtering by minimum score

Expanded the dependency graph builder to create nodes for edge endpoints and append “related” edges with confidence scores, ensuring both endpoints already exist in the node map

Testing
✅ pytest


파일 (2)개

visualize/builders/dependency_graph.py
+22
-3

visualize/data_access.py
+12
-1


visualize/builders/dependency_graph.py
+22
-3

@@ -7,56 +7,75 @@ from ..clustering import AdvancedClusterer

def build_dependency_graph_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], kinds: List[str], min_conf: float,
                               focus: str = None, depth: int = 2, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build dependency graph JSON for visualization"""
    print(f"의존성 그래프 생성: 프로젝트 {project_id}")
    print(f"  종류: {kinds}")
    print(f"  최소 신뢰도: {min_conf}")
    print(f"  포커스: {focus}")
    print(f"  최대 깊이: {depth}")
    print(f"  최대 노드 수: {max_nodes}")
    
    db = VizDB(config, project_name)
    
    # Fetch edges based on criteria
    edges = db.fetch_edges(project_id, kinds, min_conf)
    print(f"  엣지 {len(edges)}개 조회")
    
    # Build node and edge collections
    nodes_dict = {}
    json_edges = []
    
    for edge in edges:
        # Create source node ID
        src_id = f"{edge.src_type}:{edge.src_id}"
        dst_id = f"{edge.dst_type}:{edge.dst_id}" if edge.dst_id else f"unknown:{edge.edge_kind}"
        

        # Get node details and add nodes
        src_details = db.get_node_details(edge.src_type, edge.src_id)
        dst_details = db.get_node_details(edge.dst_type, edge.dst_id) if edge.dst_id else None
        
        nodes_list = list(nodes_dict.values())
        if src_id not in nodes_dict and src_details:
            nodes_dict[src_id] = create_node(src_id, edge.src_type, _get_node_label(edge.src_type, src_details),
                                             group=None, meta=src_details)
        if dst_id not in nodes_dict and dst_details:
            nodes_dict[dst_id] = create_node(dst_id, edge.dst_type, _get_node_label(edge.dst_type, dst_details),
                                             group=None, meta=dst_details)
        json_edges.append(
            create_edge(f"{edge.edge_kind}:{edge.edge_id}", src_id, dst_id, edge.edge_kind, edge.confidence)
        )

    # Append relatedness edges
    related = db.fetch_relatedness(project_id, min_conf)
    for rel in related:
        src_id = f"{rel.node1_type}:{rel.node1_id}"
        dst_id = f"{rel.node2_type}:{rel.node2_id}"
        if src_id in nodes_dict and dst_id in nodes_dict:
            json_edges.append(
                create_edge(f"related:{rel.relatedness_id}", src_id, dst_id, 'related', rel.score)
            )

    nodes_list = list(nodes_dict.values())
    print(f"  노드 {len(nodes_list)}개 생성")

    # Initialize the clusterer with all nodes and edges
    clusterer = AdvancedClusterer(nodes_list, json_edges)

    # Assign cluster IDs to all nodes
    for node in nodes_list:
        node['group'] = clusterer.get_cluster_id(node['id'])
    
    # Apply focus filtering if specified
    if focus:
        nodes_list, json_edges = filter_nodes_by_focus(nodes_list, json_edges, focus, depth)
        print(f"  포커스 필터 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")
    
    # Apply node limit
    if len(nodes_list) > max_nodes:
        nodes_list, json_edges = limit_nodes(nodes_list, json_edges, max_nodes)
        print(f"  노드 제한 적용 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")

    # --- Meta enrichment: Hotspot bins & Vulnerability overlay ---
    # Complexity estimate: out-degree (call edges) as simple proxy
    out_degree: Dict[str, int] = {}
    for e in json_edges:
        if e.get('kind') == 'call':
            out_degree[e['source']] = out_degree.get(e['source'], 0) + 1
visualize/data_access.py
+12
-1

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
from models.database import DatabaseManager, File, Class, Method, SqlUnit, Join, RequiredFilter, Edge, DbTable, DbColumn, DbPk, VulnerabilityFix, Project, Relatedness
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

@@ -81,50 +81,61 @@ class VizDB:
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

    def fetch_relatedness(self, project_id: int, min_score: float = 0.0) -> List[Relatedness]:
        """Fetch relatedness records for a project with optional score filtering"""
        session = self.session()
        try:
            query = session.query(Relatedness).filter(Relatedness.project_id == project_id)
            if min_score > 0:
                query = query.filter(Relatedness.score >= min_score)
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
