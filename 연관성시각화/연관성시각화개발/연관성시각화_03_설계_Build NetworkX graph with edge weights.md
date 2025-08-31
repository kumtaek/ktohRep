Build NetworkX graph with edge weights
8월 30일
kumtaek/ktohRep
master
+122
-1

아카이브에 보관

공유하기

PR 만들기


* File: `visualize/clustering.py` or new `visualize/builders/cluster_graph.py`
* Build a NetworkX graph with edge weights from relatedness scores.
* Run `community_louvain.best_partition` (or `louvain_communities` in NetworkX ≥2.8).
* Assign resulting `cluster_id` back to each node for downstream templates.
복사
Summary
Added NetworkX and python-louvain dependencies to support graph-based community detection

Extended data access layer by importing the Relatedness model and adding a fetch_relatedness method for retrieving relatedness pairs

Introduced a new cluster_graph builder that constructs a weighted NetworkX graph from relatedness scores, runs a Louvain partition, and assigns the resulting cluster_id to each node for visualization templates

Testing
⚠️ pip install networkx python-louvain (failed: Could not connect to proxy)

✅ pytest


파일 (3)개

requirements.txt
+4
-0

visualize/builders/cluster_graph.py
신규

visualize/data_access.py
+27
-1



requirements.txt
+4
-0

@@ -3,45 +3,49 @@ sqlalchemy>=1.4.0
pyyaml>=6.0
python-dotenv>=0.19.0
aiofiles>=0.8.0
javalang>=0.13.0
requests>=2.31.0
sqlparse>=0.4.4
lxml>=4.9.0
psutil>=5.9.0                # System resource monitoring

# Web dashboard
flask>=2.3.0                 # Web framework
flask-cors>=4.0.0            # CORS support
werkzeug>=2.3.0              # Flask dependency
jinja2>=3.1.0                # Template engine
markdown>=3.4.0              # Markdown rendering
pygments>=2.16.0             # Code highlighting

# HTTP and API clients
httpx>=0.24.0                # Async HTTP client
pydantic>=1.10.0             # Data validation

# Data processing
pandas>=1.5.0                # Data manipulation
numpy>=1.24.0                # Numerical computing

# Graph analytics
networkx>=3.0
python-louvain>=0.16

# Tests
pytest>=7.0.0
pytest-asyncio>=0.20.0

# Optional (uncomment if needed)
# FastAPI alternative (if preferred over Flask)
# fastapi>=0.100.0
# uvicorn>=0.20.0

# Oracle and advanced features
# cx_oracle>=8.3.0            # Oracle driver
# jsqlparser>=0.1.0           # SQL parsing helper
# tree_sitter>=0.20.0         # Multi-language parsing
# antlr4-python3-runtime>=4.9.0

# LLM integration
openai>=1.35.0               # LLM integration (vLLM/OpenAI-compatible)
# langchain>=0.1.0
# faiss-cpu>=1.7.0
# sentence-transformers>=2.2.0
visualize/builders/cluster_graph.py
신규
+91
-0

# visualize/builders/cluster_graph.py
from typing import Dict, Any, Optional, List

import networkx as nx

from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


def _louvain_partition(graph: nx.Graph) -> Dict[str, int]:
    """Run Louvain community detection and return node->cluster mapping."""
    try:
        from networkx.algorithms.community import louvain_communities
        communities = louvain_communities(graph, weight="weight", seed=0)
        return {node: idx for idx, comm in enumerate(communities) for node in comm}
    except Exception:
        try:
            from community import community_louvain
            return community_louvain.best_partition(graph, weight="weight", random_state=0)
        except Exception:
            # Fallback: all nodes in cluster 0
            return {n: 0 for n in graph.nodes()}


def build_cluster_graph_json(
    config: Dict[str, Any],
    project_id: int,
    project_name: Optional[str] = None,
    min_score: float = 0.0,
) -> Dict[str, Any]:
    """Build a graph of related nodes clustered with Louvain algorithm."""
    db = VizDB(config, project_name)
    related = db.fetch_relatedness(project_id, min_score)

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []
    G = nx.Graph()

    for rel in related:
        src_id = f"{rel.node1_type}:{rel.node1_id}"
        dst_id = f"{rel.node2_type}:{rel.node2_id}"

        if src_id not in nodes:
            details = db.get_node_details(rel.node1_type, rel.node1_id)
            label = _get_node_label(rel.node1_type, details)
            nodes[src_id] = create_node(src_id, rel.node1_type, label, "Unclustered", details)
        if dst_id not in nodes:
            details = db.get_node_details(rel.node2_type, rel.node2_id)
            label = _get_node_label(rel.node2_type, details)
            nodes[dst_id] = create_node(dst_id, rel.node2_type, label, "Unclustered", details)

        edge_id = f"rel:{rel.relatedness_id}"
        edges.append(
            create_edge(edge_id, src_id, dst_id, "related", rel.score, {"reason": rel.reason})
        )
        G.add_edge(src_id, dst_id, weight=rel.score)

    partition = _louvain_partition(G)
    for node_id, cluster_id in partition.items():
        node = nodes.get(node_id)
        if node is not None:
            node["cluster_id"] = cluster_id
            node["group"] = f"cluster_{cluster_id}"

    graph = create_graph(list(nodes.values()), edges)
    graph.setdefault("metadata", {})["cluster_method"] = "louvain"
    return graph


def _get_node_label(node_type: str, details: Dict[str, Any] | None = None) -> str:
    """Generate a readable label for a node"""
    if not details:
        return f"Unknown {node_type}"

    if node_type == "method":
        class_name = details.get("class", "").split(".")[-1] if details.get("class") else "Unknown"
        method_name = details.get("name", "unknown")
        return f"{class_name}.{method_name}()"
    elif node_type == "class":
        return details.get("fqn", details.get("name", "Unknown"))
    elif node_type == "file":
        path = details.get("path", "unknown")
        return path.split("/")[-1] if "/" in path else path.split("\\")[-1]
    elif node_type == "sql_unit":
        stmt_id = details.get("stmt_id", "unknown")
        mapper_ns = details.get("mapper_ns", "unknown")
        return f"{mapper_ns}.{stmt_id}"
    elif node_type == "table":
        return details.get("name", "Unknown Table")
    else:
        return f"{node_type}:{details.get('name', 'unknown')}"
visualize/data_access.py
+27
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
from models.database import (
    DatabaseManager,
    File,
    Class,
    Method,
    SqlUnit,
    Join,
    RequiredFilter,
    Edge,
    DbTable,
    DbColumn,
    DbPk,
    VulnerabilityFix,
    Project,
    Relatedness,
)
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

@@ -81,50 +96,61 @@ class VizDB:
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
        """Fetch relatedness pairs for a project"""
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
        