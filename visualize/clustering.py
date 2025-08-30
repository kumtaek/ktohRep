# visualize/clustering.py
from typing import Dict, List, Any, Optional
import os
from pathlib import Path

class AdvancedClusterer:
    """
    Analyzes graph nodes and edges to determine logical clusters for visualization.
    This replaces the simple `guess_group` function with more sophisticated,
    multi-layered logic.
    """

    def __init__(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        self.nodes = nodes
        self.edges = edges
        self.node_map = {node['id']: node for node in nodes}
        self.clusters = {}  # Cache for computed cluster IDs: {node_id: cluster_id}
        self._build_clusters()

    def get_cluster_id(self, node_id: str) -> str:
        """
        Returns the calculated cluster ID for a given node.
        """
        return self.clusters.get(node_id, "Default")

    def _build_clusters(self):
        """
        Main method to orchestrate the clustering process.
        It applies different strategies in order of precedence.
        """
        # Strategy 1: Rule-based clustering (Phase 1 from plan)
        self._apply_rule_based_clustering()

        # Strategy 2: AI/LLM-based clustering (Future placeholder)
        # self._apply_ai_based_clustering()

    def _apply_rule_based_clustering(self):
        """
        Applies a set of deterministic rules to group nodes.
        - Groups database tables and related SQL mappers together.
        - Groups controllers and their primary service/repository together.
        - Groups files based on their directory structure.
        """
        
        # 1. Group by directory structure (as a baseline)
        for node in self.nodes:
            node_id = node['id']
            if node.get('type') in ('file', 'class', 'method'):
                path_str = (node.get('meta') or {}).get('file')
                if path_str:
                    # Use the parent directory as the group
                    parent_dir = str(Path(path_str).parent)
                    # Sanitize for use as a CSS class
                    cluster_name = self._sanitize_name(parent_dir)
                    self.clusters[node_id] = cluster_name
        
        # 2. Group DB-related items together
        db_tables = {n['id']: n for n in self.nodes if n['type'] == 'table'}
        sql_units = {n['id']: n for n in self.nodes if n['type'] == 'sql_unit'}
        
        # Create a cluster for each table and its related SQLs
        for table_id, table_node in db_tables.items():
            # Cluster name based on the table itself
            table_cluster_name = self._sanitize_name(table_node['label'])
            self.clusters[table_id] = table_cluster_name
            
            # Find all SQL units that use this table
            for edge in self.edges:
                if edge['kind'] == 'use_table' and edge['target'] == table_id:
                    sql_unit_id = edge['source']
                    if sql_unit_id in sql_units:
                        self.clusters[sql_unit_id] = table_cluster_name

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitizes a string to be used as a cluster name (and CSS class).
        """
        # Replace common path separators and special characters
        sanitized = name.replace('\\', '_').replace('/', '_').replace('.', '_')
        # Remove any other non-alphanumeric characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized

    def get_all_cluster_defs(self) -> Dict[str, str]:
        """
        Returns a dictionary of all unique cluster IDs and a generated color for them.
        This is used to create the `classDef` in Mermaid.
        """
        unique_clusters = sorted(list(set(self.clusters.values())))
        colors = self._generate_palette(len(unique_clusters))
        
        cluster_defs = {}
        for i, cluster_id in enumerate(unique_clusters):
            color = colors[i]
            # Mermaid classDef format: `classDef cluster_id fill:#xxxxxx,stroke:#333`
            cluster_defs[cluster_id] = f"fill:{color},stroke:#333,stroke-width:2px"
            
        return cluster_defs

    def _generate_palette(self, n_colors: int) -> List[str]:
        """

        Generates a palette of visually distinct colors.
        Simple HSV-based color generation.
        """
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            # Using fixed saturation and value for pastel-like colors
            saturation = 0.7 
            value = 0.95
            
            # HSV to RGB conversion
            h_i = int(hue * 6)
            f = hue * 6 - h_i
            p = value * (1 - saturation)
            q = value * (1 - f * saturation)
            t = value * (1 - (1 - f) * saturation)
            
            if h_i == 0:
                r, g, b = value, t, p
            elif h_i == 1:
                r, g, b = q, value, p
            elif h_i == 2:
                r, g, b = p, value, t
            elif h_i == 3:
                r, g, b = p, q, value
            elif h_i == 4:
                r, g, b = t, p, value
            else:
                r, g, b = value, p, q
                
            colors.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
            
        return colors
