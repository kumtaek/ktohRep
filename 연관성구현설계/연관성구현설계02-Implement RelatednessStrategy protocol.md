Implement RelatednessStrategy protocol
8월 30일
kumtaek/ktohRep
master
+66
-41

아카이브에 보관

공유하기

PR 만들기


1. `phase1/relatedness/strategies/base.py`에 `RelatednessStrategy` 프로토콜 구현
2. 기존 연관성 로직을 `EdgeStrategy`, `DirStrategy`, `NamingStrategy` 등 별도 클래스(각각 `strategies/edge.py` 등)로 분리
3. `calculate_relatedness.py`에서 전략 목록을 순회하도록 수정하여 확장 가능성 확보
복사
Summary
Introduced a RelatednessStrategy protocol defining a unified apply interface for relatedness computations

Extracted edge-based logic into a dedicated EdgeStrategy class that scores direct relationships such as foreign keys, inheritance and calls

Added placeholder DirStrategy and NamingStrategy classes and updated the calculator to build and iterate a strategy list for extensible processing

Testing
✅ python -m pytest


파일 (7)개

phase1/relatedness/__init__.py
신규

phase1/relatedness/strategies/__init__.py
신규

phase1/relatedness/strategies/base.py
신규

phase1/relatedness/strategies/dir.py
신규

phase1/relatedness/strategies/edge.py
신규

phase1/relatedness/strategies/naming.py
신규

phase1/scripts/calculate_relatedness.py
+12
-41



phase1/relatedness/__init__.py
신규

내용 없음
phase1/relatedness/strategies/__init__.py
신규

내용 없음
phase1/relatedness/strategies/base.py
신규
+8
-0

"""Base protocol for relatedness strategies."""
from typing import Protocol, Callable, Any

class RelatednessStrategy(Protocol):
    """Protocol that all relatedness strategies must follow."""
    def apply(self, session: Any, project_id: int, update_score: Callable[[str, str, float, str], None]) -> None:
        """Apply the strategy using the given database session and update callback."""
        ...
phase1/relatedness/strategies/dir.py
신규
+7
-0

"""Placeholder strategy for directory-based relatedness."""
from .base import RelatednessStrategy

class DirStrategy(RelatednessStrategy):
    """Calculates relatedness based on directory proximity."""
    def apply(self, session, project_id: int, update_score):  # pragma: no cover - not implemented
        print("  - Applying directory proximity strategy (not implemented)")
phase1/relatedness/strategies/edge.py
신규
+32
-0

"""Strategy for relatedness based on direct edges."""
from phase1.models.database import Edge
from .base import RelatednessStrategy


class EdgeStrategy(RelatednessStrategy):
    """Calculates relatedness using existing direct edges (calls, FKs, etc.)."""

    def apply(self, session, project_id: int, update_score):
        print("  - Applying direct edge strategy...")
        try:
            edges = session.query(Edge).filter(Edge.project_id == project_id).all()
            print(f"    Found {len(edges)} edges to process.")

            score_map = {
                'fk': 0.95,
                'inherits': 0.9,
                'implements': 0.9,
                'call': 0.7,
                'use_table': 0.75,
                'include': 0.6,
            }

            for edge in edges:
                if not all([edge.source_type, edge.source_id, edge.target_type, edge.target_id]):
                    continue
                score = score_map.get(edge.edge_kind, 0.5)  # Default score for other edges
                node1_key = f"{edge.source_type}:{edge.source_id}"
                node2_key = f"{edge.target_type}:{edge.target_id}"
                update_score(node1_key, node2_key, score, f"edge_{edge.edge_kind}")
        except Exception as exc:
            print(f"    Error in EdgeStrategy: {exc}")
phase1/relatedness/strategies/naming.py
신규
+7
-0

"""Placeholder strategy for naming-based relatedness."""
from .base import RelatednessStrategy

class NamingStrategy(RelatednessStrategy):
    """Calculates relatedness based on naming conventions."""
    def apply(self, session, project_id: int, update_score):  # pragma: no cover - not implemented
        print("  - Applying naming convention strategy (not implemented)")
phase1/scripts/calculate_relatedness.py
+12
-41

# phase1/scripts/calculate_relatedness.py

import os
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

# Add project root to path to allow imports from phase1
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from phase1.models.database import DatabaseManager, File, Class, Method, SqlUnit, Edge, DbTable
# Note: Relatedness model needs to be created first in database.py
# from phase1.models.relatedness import Relatedness 
from phase1.models.database import DatabaseManager
from phase1.relatedness.strategies.edge import EdgeStrategy
from phase1.relatedness.strategies.dir import DirStrategy
from phase1.relatedness.strategies.naming import NamingStrategy

class RelatednessCalculator:
    """
    Analyzes various project entities to calculate and store a 'relatedness' score
    between them. This score is used for intelligent visualization clustering.
    """
    def __init__(self, project_name: str, config: dict):
        self.project_name = project_name
        self.config = config
        self.dbm = DatabaseManager(self.config)
        self.session = self.dbm.get_session()
        self.project_id = self._get_project_id()

        if not self.project_id:
            raise ValueError(f"Project '{self.project_name}' not found in the database.")

        # {(node1_key, node2_key): (score, reason)}
        self.relatedness_scores = defaultdict(lambda: (0.0, 'none'))
        self.strategies = [EdgeStrategy(), DirStrategy(), NamingStrategy()]

    def _get_project_id(self):
        from phase1.models.database import Project
        project = self.session.query(Project).filter_by(name=self.project_name).first()
        return project.project_id if project else None

    def run(self):
        """Executes the entire relatedness calculation pipeline."""
        print(f"Starting relatedness calculation for project: {self.project_name} (ID: {self.project_id})")
        
        self.apply_direct_edge_strategy()
        # self.apply_directory_proximity_strategy() # To be implemented
        # self.apply_naming_convention_strategy() # To be implemented

        try:
            for strategy in self.strategies:
                strategy.apply(self.session, self.project_id, self._update_score)
        finally:
            self.session.close()

        print(f"Total related pairs found: {len(self.relatedness_scores)}")
        # self.store_scores_to_db() # To be implemented
        print("Calculation finished.")

    def _update_score(self, node1_key: str, node2_key: str, score: float, reason: str):
        """Updates the score for a pair of nodes if the new score is higher."""
        if not node1_key or not node2_key or node1_key == node2_key:
            return
            
        key = tuple(sorted((node1_key, node2_key)))
        
        current_score, _ = self.relatedness_scores[key]
        if score > current_score:
            self.relatedness_scores[key] = (score, reason)

    def apply_direct_edge_strategy(self):
        """
        Calculates relatedness based on existing direct edges (calls, FKs, etc.).
        This is the most reliable and efficient source of relatedness.
        """
        print("  - Applying direct edge strategy...")
        try:
            edges = self.session.query(Edge).filter(Edge.project_id == self.project_id).all()
            print(f"    Found {len(edges)} edges to process.")

            score_map = {
                'fk': 0.95,
                'inherits': 0.9,
                'implements': 0.9,
                'call': 0.7,
                'use_table': 0.75,
                'include': 0.6
            }

            for edge in edges:
                if not all([edge.source_type, edge.source_id, edge.target_type, edge.target_id]):
                    continue

                score = score_map.get(edge.edge_kind, 0.5) # Default score for other edges
                node1_key = f"{edge.source_type}:{edge.source_id}"
                node2_key = f"{edge.target_type}:{edge.target_id}"
                self._update_score(node1_key, node2_key, score, f"edge_{edge.edge_kind}")
        except Exception as e:
            print(f"    Error in apply_direct_edge_strategy: {e}")
        finally:
            self.session.close()


# Main execution block
if __name__ == '__main__':
    import yaml
    from pathlib import Path

    # This allows running the script directly for testing
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Replace with the actual project name you want to analyze
    # You might need to pass this as a command-line argument
    project_name_to_analyze = "default_project" # <-- Replace this
    
    try:
        # In a real scenario, you might get the project name from sys.argv
        if len(sys.argv) > 1:
            project_name_to_analyze = sys.argv[1]
        else:
            print(f"Usage: python {sys.argv[0]} <project_name>")
            print(f"Defaulting to '{project_name_to_analyze}' for now.")

        calculator = RelatednessCalculator(project_name_to_analyze, config)
        calculator.run()
    except ValueError as ve: