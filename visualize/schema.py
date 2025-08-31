# visualize/schema.py
from typing import Dict, List, Any, Optional


def create_node(id: str, type: str, label: str, group: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized node dictionary"""
    return {
        'id': id,
        'type': type,
        'label': label,
        'group': group,
        'meta': meta or {}
    }


def create_edge(id: str, source: str, target: str, kind: str, confidence: float = 1.0, 
                meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized edge dictionary"""
    return {
        'id': id,
        'source': source,
        'target': target,
        'kind': kind,
        'confidence': confidence,
        'meta': meta or {}
    }


def create_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a complete graph structure"""
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
    """Guess the group/component category for a node"""
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
    """Filter nodes and edges by focus node and depth using BFS"""
    if not focus:
        return nodes, edges
    
    # Build adjacency map
    adj = {}
    for edge in edges:
        src, dst = edge['source'], edge['target']
        if src not in adj:
            adj[src] = set()
        if dst not in adj:
            adj[dst] = set()
        adj[src].add(dst)
        adj[dst].add(src)  # Undirected for exploration
    
    # Find focus node
    node_map = {node['id']: node for node in nodes}
    focus_node = None
    
    # Try exact ID match first
    if focus in node_map:
        focus_node = focus
    else:
        # Try label match
        for node in nodes:
            if node['label'] == focus or focus in node['label']:
                focus_node = node['id']
                break
    
    if not focus_node:
        print(f"Warning: Focus node '{focus}' not found")
        return nodes, edges
    
    # BFS to find nodes within depth
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
    
    # Filter nodes and edges
    filtered_nodes = [node for node in nodes if node['id'] in kept_nodes]
    filtered_edges = [edge for edge in edges 
                     if edge['source'] in kept_nodes and edge['target'] in kept_nodes]
    
    return filtered_nodes, filtered_edges


def limit_nodes(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                max_nodes: int) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Limit the number of nodes, keeping the most connected ones"""
    if len(nodes) <= max_nodes:
        return nodes, edges
    
    # Count connections for each node
    node_connections = {}
    for node in nodes:
        node_connections[node['id']] = 0
    
    for edge in edges:
        if edge['source'] in node_connections:
            node_connections[edge['source']] += 1
        if edge['target'] in node_connections:
            node_connections[edge['target']] += 1
    
    # Sort nodes by connection count and take top N
    sorted_nodes = sorted(nodes, key=lambda n: node_connections.get(n['id'], 0), reverse=True)
    kept_nodes_ids = {node['id'] for node in sorted_nodes[:max_nodes]}
    
    # Filter nodes and edges
    filtered_nodes = [node for node in nodes if node['id'] in kept_nodes_ids]
    filtered_edges = [edge for edge in edges 
                     if edge['source'] in kept_nodes_ids and edge['target'] in kept_nodes_ids]
    
    return filtered_nodes, filtered_edges