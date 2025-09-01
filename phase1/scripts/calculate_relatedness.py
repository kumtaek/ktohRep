# phase1/scripts/calculate_relatedness.py

import os
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Callable, List, Dict, Tuple

# Add project root to path to allow imports from phase1
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from phase1.models.database import DatabaseManager, File, Class, Method, SqlUnit, Edge, DbTable, Project, Relatedness 

class RelatednessStrategy(ABC):
    """
    Abstract base class defining the interface for relatedness calculation strategies.
    Each strategy implements a specific algorithm for calculating relatedness scores.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of this strategy for logging purposes."""
        pass
    
    @abstractmethod
    def apply(self, session, project_id: int, update_callback: Callable[[str, str, float, str], None]):
        """
        Apply this strategy to calculate relatedness scores.
        
        Args:
            session: Database session
            project_id: ID of the project to analyze
            update_callback: Function to call with (node1_key, node2_key, score, reason)
        """
        pass


class DirectEdgeStrategy(RelatednessStrategy):
    """Strategy for calculating relatedness based on existing direct edges (calls, FKs, etc.)."""
    
    @property
    def name(self) -> str:
        return "DirectEdge"
    
    def apply(self, session, project_id: int, update_callback: Callable[[str, str, float, str], None]):
        """Calculate relatedness based on existing direct edges."""
        print(f"  - Applying {self.name} strategy...")
        try:
            edges = session.query(Edge).filter(Edge.project_id == project_id).all()
            print(f"    Found {len(edges)} edges to process.")

            score_map = {
                'fk': 0.95,
                'inherits': 0.9,
                'implements': 0.9,
                'call': 0.7,
                'use_table': 0.75,
                'include': 0.6
            }

            processed_count = 0
            for edge in edges:
                if not all([edge.src_type, edge.src_id, edge.dst_type, edge.dst_id]):
                    continue

                score = score_map.get(edge.edge_kind, 0.5)
                node1_key = f"{edge.src_type}:{edge.src_id}"
                node2_key = f"{edge.dst_type}:{edge.dst_id}"
                update_callback(node1_key, node2_key, score, f"edge_{edge.edge_kind}")
                processed_count += 1
            
            print(f"    Processed {processed_count} valid edges.")
            
        except Exception as e:
            print(f"    Error in {self.name} strategy: {e}")


class DirectoryProximityStrategy(RelatednessStrategy):
    """Strategy for calculating relatedness based on directory proximity."""
    
    @property
    def name(self) -> str:
        return "DirectoryProximity"
    
    def apply(self, session, project_id: int, update_callback: Callable[[str, str, float, str], None]):
        """Calculate relatedness based on directory proximity."""
        print(f"  - Applying {self.name} strategy...")
        try:
            files_by_dir = defaultdict(list)
            all_files = session.query(File).filter(File.project_id == project_id).all()
            print(f"    Found {len(all_files)} files to process.")

            for file_obj in all_files:
                if file_obj.path:
                    dir_name = os.path.dirname(file_obj.path)
                    files_by_dir[dir_name].append(f"file:{file_obj.file_id}")

            pairs_processed = 0
            for dir_name, nodes_in_dir in files_by_dir.items():
                if len(nodes_in_dir) > 1:
                    for node1_key, node2_key in combinations(nodes_in_dir, 2):
                        update_callback(node1_key, node2_key, 0.6, 'directory_proximity')
                        pairs_processed += 1
            
            print(f"    Processed {pairs_processed} file pairs from {len(files_by_dir)} directories.")
            
        except Exception as e:
            print(f"    Error in {self.name} strategy: {e}")


class NamingConventionStrategy(RelatednessStrategy):
    """Strategy for calculating relatedness based on naming conventions."""
    
    @property
    def name(self) -> str:
        return "NamingConvention"
    
    def apply(self, session, project_id: int, update_callback: Callable[[str, str, float, str], None]):
        """Calculate relatedness based on naming conventions."""
        print(f"  - Applying {self.name} strategy...")
        try:
            # Get all entities with names
            entities = []
            
            # Add files
            files = session.query(File).filter(File.project_id == project_id).all()
            for f in files:
                if f.path:
                    filename = os.path.basename(f.path)
                    name_without_ext = os.path.splitext(filename)[0]
                    entities.append({'type': 'file', 'id': f.file_id, 'name': name_without_ext})
            
            # Add classes
            classes = session.query(Class).join(File).filter(File.project_id == project_id).all()
            for c in classes:
                entities.append({'type': 'class', 'id': c.class_id, 'name': c.name})
            
            print(f"    Found {len(entities)} entities to analyze.")
            
            # Group entities by base name
            nodes_by_base_name = defaultdict(list)
            common_suffixes = ['Service', 'Controller', 'Repository', 'DAO', 'DTO', 'VO', 'Impl', 'Test']
            
            for entity in entities:
                base_name = entity['name']
                for suffix in common_suffixes:
                    if base_name.endswith(suffix):
                        base_name = base_name[:-len(suffix)]
                        break
                nodes_by_base_name[base_name].append(entity)
            
            pairs_processed = 0
            for base_name, related_entities in nodes_by_base_name.items():
                if len(related_entities) > 1:
                    for entity1, entity2 in combinations(related_entities, 2):
                        node1_key = f"{entity1['type']}:{entity1['id']}"
                        node2_key = f"{entity2['type']}:{entity2['id']}"
                        update_callback(node1_key, node2_key, 0.8, 'naming_convention')
                        pairs_processed += 1
            
            print(f"    Processed {pairs_processed} related pairs from naming patterns.")
            
        except Exception as e:
            print(f"    Error in {self.name} strategy: {e}")


class RelatednessCalculator:
    """
    Context class for the Strategy pattern that manages relatedness calculation.
    Uses multiple strategies to calculate and store relatedness scores between entities.
    """
    
    def __init__(self, project_name: str, config: dict):
        self.project_name = project_name
        self.config = config
        db_config = self.config.get('database', {}).get('project', {})
        self.dbm = DatabaseManager(db_config)
        self.dbm.initialize()  # Ensure database is initialized
        self.session = self.dbm.get_session()
        self.project_id = self._get_project_id()

        if not self.project_id:
            raise ValueError(f"Project '{self.project_name}' not found in the database.")

        # Memory storage for final scores: {(node1_key, node2_key): (score, reason)}
        self.relatedness_scores = defaultdict(lambda: (0.0, 'none'))
        
        # Initialize strategies
        self.strategies: List[RelatednessStrategy] = [
            DirectEdgeStrategy(),
            DirectoryProximityStrategy(), 
            NamingConventionStrategy(),
            # LLMStrategy() can be added later
        ]

    def _get_project_id(self) -> int:
        """Get project ID from database."""
        project = self.session.query(Project).filter_by(name=self.project_name).first()
        return project.project_id if project else None

    def run(self):
        """Execute the entire relatedness calculation pipeline using all strategies."""
        print(f"Starting relatedness calculation for project: {self.project_name} (ID: {self.project_id})")
        
        # Execute all strategies
        for strategy in self.strategies:
            try:
                strategy.apply(self.session, self.project_id, self._update_score)
            except Exception as e:
                print(f"Error in strategy {strategy.name}: {e}")
                continue

        print(f"Total related pairs found: {len(self.relatedness_scores)}")
        
        # Store final results to database
        self.store_scores_to_db()
        print("Relatedness calculation completed successfully.")

    def _update_score(self, node1_key: str, node2_key: str, score: float, reason: str):
        """
        Callback function for strategies to update scores.
        Only updates if the new score is higher (strongest relationship wins).
        """
        if not node1_key or not node2_key or node1_key == node2_key:
            return
            
        # Ensure consistent ordering for the key
        key = tuple(sorted((node1_key, node2_key)))
        
        current_score, _ = self.relatedness_scores[key]
        if score > current_score:
            self.relatedness_scores[key] = (score, reason)

    def store_scores_to_db(self):
        """Store all calculated relatedness scores to the database efficiently."""
        print("  - Storing scores to database...")
        
        if not self.relatedness_scores:
            print("    No relatedness scores to store.")
            return

        try:
            # First, delete existing relatedness data for this project for a clean slate
            self.session.query(Relatedness).filter(
                Relatedness.project_id == self.project_id
            ).delete(synchronize_session=False)
            print(f"    Deleted old relatedness data for project {self.project_id}.")

            # Prepare data for bulk insert
            insert_data = []
            for (node1_key, node2_key), (score, reason) in self.relatedness_scores.items():
                if score <= 0.0:
                    continue
                
                try:
                    node1_type, node1_id_str = node1_key.split(':', 1)
                    node2_type, node2_id_str = node2_key.split(':', 1)
                    node1_id = int(node1_id_str)
                    node2_id = int(node2_id_str)
                    
                    insert_data.append({
                        'project_id': self.project_id,
                        'node1_type': node1_type,
                        'node1_id': node1_id,
                        'node2_type': node2_type,
                        'node2_id': node2_id,
                        'score': score,
                        'reason': reason
                    })
                except (ValueError, IndexError) as e:
                    print(f"    Skipping invalid key format: {node1_key}, {node2_key} - Error: {e}")
                    continue
            
            # Bulk insert the data
            if insert_data:
                self.session.bulk_insert_mappings(Relatedness, insert_data)
                self.session.commit()
                print(f"    Successfully stored {len(insert_data)} new relatedness records.")
            else:
                print("    No valid new relatedness data to store.")
                
        except Exception as e:
            print(f"    Error storing scores to database: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()


# Main execution block
if __name__ == '__main__':
    import yaml
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(description='코드 연관성 계산 도구')
    parser.add_argument('--project-name', required=True, help='분석 대상 프로젝트 이름')
    args = parser.parse_args()

    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(os.path.expandvars(f.read())) or {}

    project_name_to_analyze = args.project_name
    
    # Substitute project name in config
    import json
    config_str = json.dumps(config)
    config_str = config_str.replace("{project_name}", project_name_to_analyze)
    config = json.loads(config_str)
    
    try:
        calculator = RelatednessCalculator(project_name_to_analyze, config)
        calculator.run()
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
