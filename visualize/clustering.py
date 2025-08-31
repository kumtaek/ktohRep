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
        # 노드 ID를 키로 하는 노드 맵을 생성합니다.
        self.node_map = {node['id']: node for node in nodes}
        # 계산된 클러스터 ID를 캐시합니다: {node_id: cluster_id}
        self.clusters = {}
        # 클러스터링 프로세스를 시작합니다.
        self._build_clusters()

    def get_cluster_id(self, node_id: str) -> str:
        """
        주어진 노드에 대한 계산된 클러스터 ID를 반환합니다.
        """
        # 노드 ID에 해당하는 클러스터 ID를 반환하고, 없으면 "Default"를 반환합니다.
        return self.clusters.get(node_id, "Default")

    def _build_clusters(self):
        """
        클러스터링 프로세스를 조정하는 메인 메서드입니다.
        우선순위에 따라 다양한 전략을 적용합니다.
        """
        # 전략 1: 규칙 기반 클러스터링을 적용합니다.
        self._apply_rule_based_clustering()

        # 전략 2: AI/LLM 기반 클러스터링 (향후 구현 예정)
        # self._apply_ai_based_clustering()

    def _apply_rule_based_clustering(self):
        """
        노드를 그룹화하기 위한 결정론적 규칙 세트를 적용합니다.
        - 데이터베이스 테이블 및 관련 SQL 매퍼를 함께 그룹화합니다.
        - 컨트롤러와 해당 기본 서비스/리포지토리를 함께 그룹화합니다.
        - 디렉토리 구조를 기반으로 파일을 그룹화합니다.
        """
        
        # 1. 디렉토리 구조를 기반으로 그룹화합니다 (기준선).
        for node in self.nodes:
            node_id = node['id']
            if node.get('type') in ('file', 'class', 'method'):
                path_str = (node.get('meta') or {}).get('file')
                if path_str:
                    # 부모 디렉토리를 그룹 이름으로 사용합니다.
                    parent_dir = str(Path(path_str).parent)
                    # CSS 클래스로 사용하기 위해 이름을 정리합니다.
                    cluster_name = self._sanitize_name(parent_dir)
                    self.clusters[node_id] = cluster_name
        
        # 2. DB 관련 항목을 함께 그룹화합니다.
        db_tables = {n['id']: n for n in self.nodes if n['type'] == 'table'}
        sql_units = {n['id']: n for n in self.nodes if n['type'] == 'sql_unit'}
        
        # 각 테이블과 관련 SQL에 대한 클러스터를 생성합니다.
        for table_id, table_node in db_tables.items():
            # 테이블 자체를 기반으로 클러스터 이름을 생성합니다.
            table_cluster_name = self._sanitize_name(table_node['label'])
            self.clusters[table_id] = table_cluster_name
            
            # 이 테이블을 사용하는 모든 SQL 단위를 찾습니다.
            for edge in self.edges:
                if edge['kind'] == 'use_table' and edge['target'] == table_id:
                    sql_unit_id = edge['source']
                    if sql_unit_id in sql_units:
                        self.clusters[sql_unit_id] = table_cluster_name

    def _sanitize_name(self, name: str) -> str:
        """
        클러스터 이름(및 CSS 클래스)으로 사용될 문자열을 정리합니다.
        """
        # 일반적인 경로 구분자와 특수 문자를 밑줄로 대체합니다.
        sanitized = name.replace('\\', '_').replace('/', '_').replace('.', '_')
        # 다른 영숫자가 아닌 문자를 제거합니다.
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized

    def get_all_cluster_defs(self) -> Dict[str, str]:
        """
        모든 고유한 클러스터 ID와 생성된 색상을 포함하는 딕셔너리를 반환합니다.
        이는 Mermaid에서 `classDef`를 생성하는 데 사용됩니다.
        """
        # 고유한 클러스터 ID를 가져와 정렬합니다.
        unique_clusters = sorted(list(set(self.clusters.values())))
        # 클러스터 수에 해당하는 색상 팔레트를 생성합니다.
        colors = self._generate_palette(len(unique_clusters))
        
        cluster_defs = {}
        # 각 클러스터에 대한 Mermaid classDef 형식을 생성합니다.
        for i, cluster_id in enumerate(unique_clusters):
            color = colors[i]
            # Mermaid classDef 형식: `classDef cluster_id fill:#xxxxxx,stroke:#333`
            cluster_defs[cluster_id] = f"fill:{color},stroke:#333,stroke-width:2px"
            
        return cluster_defs

    def _generate_palette(self, n_colors: int) -> List[str]:
        """

        시각적으로 구별되는 색상 팔레트를 생성합니다.
        간단한 HSV 기반 색상 생성입니다.
        """
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            # 파스텔 톤 색상을 위해 고정된 채도와 명도를 사용합니다.
            saturation = 0.7 
            value = 0.95
            
            # HSV를 RGB로 변환합니다.
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
