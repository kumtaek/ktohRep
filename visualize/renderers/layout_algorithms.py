# visualize/renderers/layout_algorithms.py
from typing import Dict, List, Any, Tuple, Optional
import math
import random
from dataclasses import dataclass

@dataclass
class NodePosition:
    x: float
    y: float
    id: str
    width: float = 100
    height: float = 60

@dataclass
class EdgeInfo:
    source: str
    target: str
    weight: float = 1.0
    length: float = 150

class LayoutAlgorithm:
    """레이아웃 알고리즘 기본 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def calculate_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, NodePosition]:
        """노드 레이아웃 계산 - 하위 클래스에서 구현"""
        raise NotImplementedError

class ForceDirectedLayout(LayoutAlgorithm):
    """포스 디렉티드 레이아웃 알고리즘"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.iterations = self.config.get('iterations', 500)
        self.node_repulsion = self.config.get('node_repulsion', 20000)
        self.edge_attraction = self.config.get('edge_attraction', 0.1)
        self.damping = self.config.get('damping', 0.9)
        self.min_distance = self.config.get('min_distance', 100)
        self.center_gravity = self.config.get('center_gravity', 0.01)
    
    def calculate_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, NodePosition]:
        """포스 디렉티드 알고리즘으로 노드 위치 계산"""
        
        # 노드 위치 초기화 (원형 배치)
        positions = {}
        node_count = len(nodes)
        radius = max(200, node_count * 30)
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / node_count if node_count > 0 else 0
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # 노드 크기 계산
            width = self._calculate_node_width(node)
            height = self._calculate_node_height(node)
            
            positions[node['id']] = NodePosition(x, y, node['id'], width, height)
        
        # 속도 벡터 초기화
        velocities = {node_id: {'x': 0, 'y': 0} for node_id in positions.keys()}
        
        # 엣지 정보 전처리
        edge_map = {}
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            weight = edge.get('confidence', 0.5)
            
            edge_map[(source_id, target_id)] = weight
            edge_map[(target_id, source_id)] = weight  # 무방향 그래프로 처리
        
        # 포스 디렉티드 시뮬레이션
        for iteration in range(self.iterations):
            forces = {node_id: {'x': 0, 'y': 0} for node_id in positions.keys()}
            
            # 척력 계산 (모든 노드 쌍)
            node_ids = list(positions.keys())
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    node1_id = node_ids[i]
                    node2_id = node_ids[j]
                    
                    pos1 = positions[node1_id]
                    pos2 = positions[node2_id]
                    
                    dx = pos1.x - pos2.x
                    dy = pos1.y - pos2.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        # 겹침 방지를 위한 최소 거리
                        min_dist = max(self.min_distance, 
                                     (pos1.width + pos2.width) / 2 + 20)
                        
                        if distance < min_dist:
                            # 매우 가까운 경우 강한 척력 적용
                            force_magnitude = self.node_repulsion / (distance * distance) * 2
                        else:
                            force_magnitude = self.node_repulsion / (distance * distance)
                        
                        fx = (dx / distance) * force_magnitude
                        fy = (dy / distance) * force_magnitude
                        
                        forces[node1_id]['x'] += fx
                        forces[node1_id]['y'] += fy
                        forces[node2_id]['x'] -= fx
                        forces[node2_id]['y'] -= fy
            
            # 인력 계산 (연결된 노드들)
            for (source_id, target_id), weight in edge_map.items():
                if source_id in positions and target_id in positions:
                    pos1 = positions[source_id]
                    pos2 = positions[target_id]
                    
                    dx = pos2.x - pos1.x
                    dy = pos2.y - pos1.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        ideal_distance = 150 + weight * 100  # 가중치에 따른 이상적 거리
                        force_magnitude = self.edge_attraction * (distance - ideal_distance)
                        
                        fx = (dx / distance) * force_magnitude
                        fy = (dy / distance) * force_magnitude
                        
                        forces[source_id]['x'] += fx
                        forces[source_id]['y'] += fy
                        forces[target_id]['x'] -= fx
                        forces[target_id]['y'] -= fy
            
            # 중심으로 끌어당기는 힘
            for node_id, pos in positions.items():
                forces[node_id]['x'] -= pos.x * self.center_gravity
                forces[node_id]['y'] -= pos.y * self.center_gravity
            
            # 속도 및 위치 업데이트
            total_energy = 0
            for node_id in positions.keys():
                # 속도 업데이트
                velocities[node_id]['x'] = velocities[node_id]['x'] * self.damping + forces[node_id]['x'] * 0.1
                velocities[node_id]['y'] = velocities[node_id]['y'] * self.damping + forces[node_id]['y'] * 0.1
                
                # 위치 업데이트
                positions[node_id].x += velocities[node_id]['x'] * 0.1
                positions[node_id].y += velocities[node_id]['y'] * 0.1
                
                # 에너지 계산
                total_energy += velocities[node_id]['x']**2 + velocities[node_id]['y']**2
            
            # 수렴 체크
            if iteration > 50 and total_energy < 1.0:
                break
        
        return positions
    
    def _calculate_node_width(self, node: Dict) -> float:
        """노드 너비 계산"""
        label = node.get('label', '')
        base_width = 120
        text_width = len(label) * 8
        
        # 메타 정보에 따른 추가 너비
        meta = node.get('meta', {})
        if meta.get('columns'):
            max_column_width = max((len(col.get('name', '')) for col in meta['columns']), default=0) * 7
            text_width = max(text_width, max_column_width)
        
        return max(base_width, text_width + 40)
    
    def _calculate_node_height(self, node: Dict) -> float:
        """노드 높이 계산"""
        base_height = 60
        meta = node.get('meta', {})
        
        if meta.get('columns'):
            column_count = len(meta['columns'])
            column_height = min(column_count * 18, 200)  # 최대 높이 제한
            return base_height + column_height
        
        return base_height

class HierarchicalLayout(LayoutAlgorithm):
    """계층적 레이아웃 알고리즘"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.level_height = self.config.get('level_height', 200)
        self.node_spacing = self.config.get('node_spacing', 150)
        self.center_alignment = self.config.get('center_alignment', True)
    
    def calculate_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, NodePosition]:
        """계층적 레이아웃으로 노드 위치 계산"""
        
        # 노드 의존성 그래프 구축
        node_map = {node['id']: node for node in nodes}
        dependencies = {node['id']: set() for node in nodes}
        dependents = {node['id']: set() for node in nodes}
        
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            
            if source_id in dependencies and target_id in dependencies:
                dependencies[target_id].add(source_id)
                dependents[source_id].add(target_id)
        
        # 위상 정렬을 사용하여 레벨 결정
        levels = self._topological_sort_levels(nodes, dependencies)
        
        # 각 레벨에서 노드 위치 계산
        positions = {}
        canvas_width = self._calculate_canvas_width(levels)
        
        for level_index, level_nodes in enumerate(levels):
            y = level_index * self.level_height
            
            # 노드 너비 계산
            node_widths = []
            for node_id in level_nodes:
                node = node_map[node_id]
                width = self._calculate_node_width(node)
                height = self._calculate_node_height(node)
                node_widths.append((node_id, width, height))
            
            # 노드들을 수평으로 배치
            total_width = sum(width for _, width, _ in node_widths) + (len(node_widths) - 1) * self.node_spacing
            start_x = (canvas_width - total_width) / 2 if self.center_alignment else 0
            
            current_x = start_x
            for node_id, width, height in node_widths:
                x = current_x + width / 2
                positions[node_id] = NodePosition(x, y, node_id, width, height)
                current_x += width + self.node_spacing
        
        return positions
    
    def _topological_sort_levels(self, nodes: List[Dict], dependencies: Dict[str, set]) -> List[List[str]]:
        """위상 정렬을 사용하여 노드들을 레벨별로 분류"""
        levels = []
        remaining_nodes = set(node['id'] for node in nodes)
        temp_dependencies = {node_id: deps.copy() for node_id, deps in dependencies.items()}
        
        while remaining_nodes:
            # 의존성이 없는 노드들 찾기
            current_level = []
            for node_id in list(remaining_nodes):
                if not temp_dependencies[node_id]:
                    current_level.append(node_id)
            
            if not current_level:
                # 순환 의존성이 있는 경우 임의로 선택
                current_level = [list(remaining_nodes)[0]]
            
            levels.append(current_level)
            
            # 현재 레벨 노드들 제거
            for node_id in current_level:
                remaining_nodes.remove(node_id)
                
                # 다른 노드들의 의존성에서 제거
                for deps in temp_dependencies.values():
                    deps.discard(node_id)
        
        return levels
    
    def _calculate_canvas_width(self, levels: List[List[str]]) -> float:
        """캔버스 너비 계산"""
        max_width = 0
        for level_nodes in levels:
            level_width = len(level_nodes) * 150 + (len(level_nodes) - 1) * self.node_spacing
            max_width = max(max_width, level_width)
        
        return max(max_width, 800)
    
    def _calculate_node_width(self, node: Dict) -> float:
        """노드 너비 계산"""
        return max(120, len(node.get('label', '')) * 8 + 40)
    
    def _calculate_node_height(self, node: Dict) -> float:
        """노드 높이 계산"""
        base_height = 60
        meta = node.get('meta', {})
        
        if meta.get('columns'):
            column_count = len(meta['columns'])
            return base_height + min(column_count * 15, 150)
        
        return base_height

class GridLayout(LayoutAlgorithm):
    """그리드 레이아웃 알고리즘"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.grid_spacing = self.config.get('grid_spacing', 200)
        self.aspect_ratio = self.config.get('aspect_ratio', 4/3)  # 너비:높이 비율
    
    def calculate_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, NodePosition]:
        """그리드 레이아웃으로 노드 위치 계산"""
        
        node_count = len(nodes)
        if node_count == 0:
            return {}
        
        # 그리드 크기 계산
        cols = math.ceil(math.sqrt(node_count * self.aspect_ratio))
        rows = math.ceil(node_count / cols)
        
        positions = {}
        
        # 노드들을 연결성 기준으로 정렬
        sorted_nodes = self._sort_nodes_by_connectivity(nodes, edges)
        
        for i, node in enumerate(sorted_nodes):
            row = i // cols
            col = i % cols
            
            # 중앙 정렬을 위한 오프셋 계산
            x_offset = -(cols - 1) * self.grid_spacing / 2
            y_offset = -(rows - 1) * self.grid_spacing / 2
            
            x = col * self.grid_spacing + x_offset
            y = row * self.grid_spacing + y_offset
            
            width = self._calculate_node_width(node)
            height = self._calculate_node_height(node)
            
            positions[node['id']] = NodePosition(x, y, node['id'], width, height)
        
        return positions
    
    def _sort_nodes_by_connectivity(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """연결성 기준으로 노드 정렬"""
        # 각 노드의 연결 수 계산
        connectivity = {node['id']: 0 for node in nodes}
        
        for edge in edges:
            if edge['source'] in connectivity:
                connectivity[edge['source']] += 1
            if edge['target'] in connectivity:
                connectivity[edge['target']] += 1
        
        # 연결성 높은 순으로 정렬
        return sorted(nodes, key=lambda n: connectivity[n['id']], reverse=True)
    
    def _calculate_node_width(self, node: Dict) -> float:
        """노드 너비 계산"""
        return max(120, len(node.get('label', '')) * 8 + 40)
    
    def _calculate_node_height(self, node: Dict) -> float:
        """노드 높이 계산"""
        base_height = 60
        meta = node.get('meta', {})
        
        if meta.get('columns'):
            column_count = len(meta['columns'])
            return base_height + min(column_count * 15, 150)
        
        return base_height

class CollisionDetector:
    """노드 겹침 감지 및 해결"""
    
    def __init__(self, padding: float = 20):
        self.padding = padding
    
    def detect_collisions(self, positions: Dict[str, NodePosition]) -> List[Tuple[str, str]]:
        """노드 간 겹침 감지"""
        collisions = []
        node_ids = list(positions.keys())
        
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                node1_id = node_ids[i]
                node2_id = node_ids[j]
                
                if self._nodes_overlap(positions[node1_id], positions[node2_id]):
                    collisions.append((node1_id, node2_id))
        
        return collisions
    
    def resolve_collisions(self, positions: Dict[str, NodePosition]) -> Dict[str, NodePosition]:
        """노드 겹침 해결"""
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            collisions = self.detect_collisions(positions)
            if not collisions:
                break
            
            # 각 겹침에 대해 노드들을 밀어냄
            for node1_id, node2_id in collisions:
                self._separate_nodes(positions[node1_id], positions[node2_id])
            
            iteration += 1
        
        return positions
    
    def _nodes_overlap(self, node1: NodePosition, node2: NodePosition) -> bool:
        """두 노드가 겹치는지 확인"""
        # 노드 경계 계산 (패딩 포함)
        left1 = node1.x - node1.width/2 - self.padding
        right1 = node1.x + node1.width/2 + self.padding
        top1 = node1.y - node1.height/2 - self.padding
        bottom1 = node1.y + node1.height/2 + self.padding
        
        left2 = node2.x - node2.width/2 - self.padding
        right2 = node2.x + node2.width/2 + self.padding
        top2 = node2.y - node2.height/2 - self.padding
        bottom2 = node2.y + node2.height/2 + self.padding
        
        # 겹침 확인
        return not (right1 < left2 or right2 < left1 or bottom1 < top2 or bottom2 < top1)
    
    def _separate_nodes(self, node1: NodePosition, node2: NodePosition):
        """겹치는 두 노드를 분리"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            # 완전히 겹치는 경우 임의 방향으로 분리
            angle = random.random() * 2 * math.pi
            dx = math.cos(angle)
            dy = math.sin(angle)
            distance = 1
        
        # 필요한 최소 거리 계산
        min_distance = (node1.width + node2.width) / 2 + (node1.height + node2.height) / 2 + self.padding * 2
        
        if distance < min_distance:
            # 분리해야 하는 거리
            separation_distance = min_distance - distance
            
            # 정규화된 방향 벡터
            unit_x = dx / distance
            unit_y = dy / distance
            
            # 각 노드를 반대 방향으로 이동
            move_distance = separation_distance / 2
            
            node1.x -= unit_x * move_distance
            node1.y -= unit_y * move_distance
            
            node2.x += unit_x * move_distance
            node2.y += unit_y * move_distance