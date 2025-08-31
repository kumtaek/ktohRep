# visualize/schema.py
from typing import Dict, List, Any, Optional


def create_node(id: str, type: str, label: str, group: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """표준화된 노드 딕셔너리를 생성합니다."""
    return {
        'id': id,
        'type': type,
        'label': label,
        'group': group,
        'meta': meta or {}
    }


def create_edge(id: str, source: str, target: str, kind: str, confidence: float = 1.0, 
                meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """표준화된 엣지 딕셔너리를 생성합니다."""
    return {
        'id': id,
        'source': source,
        'target': target,
        'kind': kind,
        'confidence': confidence,
        'meta': meta or {}
    }


def create_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """완전한 그래프 구조를 생성합니다."""
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'node_types': list(set(n['type'] for n in nodes)),
            'edge_kinds': list(set(e['kind'] for e in edges))
        }
    }


def guess_group(type_: str, path: str = None, fqn: str = None) -> str:
    """노드의 그룹/컴포넌트 카테고리를 추측합니다."""
    if type_ in ('table', 'view'):
        return 'DB'
    elif type_ == 'sql_unit':
        return 'Mapper'
    elif type_ in ('method', 'class'):
        if fqn:
            fqn_lower = fqn.lower()
            if 'controller' in fqn_lower:
                return 'Controller'
            elif 'service' in fqn_lower:
                return 'Service'
            elif 'repository' in fqn_lower:
                return 'Repository'
            elif 'mapper' in fqn_lower:
                return 'Mapper'
            elif 'util' in fqn_lower:
                return 'Util'
        return 'Code'
    elif type_ == 'file':
        if path:
            path_lower = path.lower()
            if path_lower.endswith('.jsp'):
                return 'JSP'
            elif 'controller' in path_lower:
                return 'Controller'
            elif 'service' in path_lower:
                return 'Service'
            elif 'repository' in path_lower:
                return 'Repository'
            elif 'mapper' in path_lower:
                return 'Mapper'
            elif 'util' in path_lower:
                return 'Util'
            elif path_lower.endswith('.xml') and 'mapper' in path_lower:
                return 'Mapper'
        return 'Code'
    else:
        return 'Unknown'


def filter_nodes_by_focus(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                         focus: str, depth: int = 2) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """BFS를 사용하여 포커스 노드와 깊이별로 노드와 엣지를 필터링합니다."""
    # 포커스 노드가 없으면 원본 노드와 엣지를 반환합니다.
    if not focus:
        return nodes, edges
    
    # 인접 맵을 구축합니다.
    adj = {}
    for edge in edges:
        src, dst = edge['source'], edge['target']
        if src not in adj:
            adj[src] = set()
        if dst not in adj:
            adj[dst] = set()
        adj[src].add(dst)
        adj[dst].add(src)  # 탐색을 위해 무방향으로 설정합니다.
    
    # 포커스 노드를 찾습니다.
    node_map = {node['id']: node for node in nodes}
    focus_node = None
    
    # 먼저 정확한 ID 일치를 시도합니다.
    if focus in node_map:
        focus_node = focus
    else:
        # 라벨 일치를 시도합니다.
        for node in nodes:
            if node['label'] == focus or focus in node['label']:
                focus_node = node['id']
                break
    
    # 포커스 노드를 찾을 수 없으면 경고를 출력하고 원본 노드와 엣지를 반환합니다.
    if not focus_node:
        print(f"경고: 포커스 노드 '{focus}'를 찾을 수 없습니다.")
        return nodes, edges
    
    # BFS를 사용하여 깊이 내의 노드를 찾습니다.
    from collections import deque
    queue = deque([(focus_node, 0)])
    visited = {focus_node}
    kept_nodes = {focus_node}
    
    while queue:
        current, current_depth = queue.popleft()
        
        if current_depth < depth:
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    kept_nodes.add(neighbor)
                    queue.append((neighbor, current_depth + 1))
    
    # 필터링된 노드와 엣지를 반환합니다.
    filtered_nodes = [node for node in nodes if node['id'] in kept_nodes]
    filtered_edges = [edge for edge in edges 
                     if edge['source'] in kept_nodes and edge['target'] in kept_nodes]
    
    return filtered_nodes, filtered_edges


def limit_nodes(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                max_nodes: int) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """가장 많이 연결된 노드를 유지하면서 노드 수를 제한합니다."""
    # 노드 수가 최대 노드 수보다 작거나 같으면 원본 노드와 엣지를 반환합니다.
    if len(nodes) <= max_nodes:
        return nodes, edges
    
    # 각 노드의 연결 수를 계산합니다.
    node_connections = {}
    for node in nodes:
        node_connections[node['id']] = 0
    
    for edge in edges:
        if edge['source'] in node_connections:
            node_connections[edge['source']] += 1
        if edge['target'] in node_connections:
            node_connections[edge['target']] += 1
    
    # 연결 수별로 노드를 정렬하고 상위 N개를 가져옵니다.
    sorted_nodes = sorted(nodes, key=lambda n: node_connections.get(n['id'], 0), reverse=True)
    kept_nodes_ids = {node['id'] for node in sorted_nodes[:max_nodes]}
    
    # 노드와 엣지를 필터링합니다.
    filtered_nodes = [node for node in nodes if node['id'] in kept_nodes_ids]
    filtered_edges = [edge for edge in edges 
                     if edge['source'] in kept_nodes_ids and edge['target'] in kept_nodes_ids]
    
    return filtered_nodes, filtered_edges