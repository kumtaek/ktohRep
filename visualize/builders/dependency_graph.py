# visualize/builders/dependency_graph.py
from typing import List, Dict, Any
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph, guess_group, filter_nodes_by_focus, limit_nodes


def build_dependency_graph_json(project_id: int, kinds: List[str], min_conf: float, 
                               focus: str = None, depth: int = 2, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build dependency graph JSON for visualization"""
    print(f"의존성 그래프 생성: 프로젝트 {project_id}")
    print(f"  종류: {kinds}")
    print(f"  최소 신뢰도: {min_conf}")
    print(f"  포커스: {focus}")
    print(f"  최대 깊이: {depth}")
    print(f"  최대 노드 수: {max_nodes}")
    
    db = VizDB()
    
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
        
        # Add source node
        if src_id not in nodes_dict:
            src_label = _get_node_label(edge.src_type, src_details)
            src_group = guess_group(edge.src_type, 
                                  src_details.get('file') if src_details else None,
                                  src_details.get('fqn') if src_details else None)
            nodes_dict[src_id] = create_node(src_id, edge.src_type, src_label, src_group, src_details)
        
        # Add destination node
        if dst_id not in nodes_dict:
            if dst_details:
                dst_label = _get_node_label(edge.dst_type, dst_details)
                dst_group = guess_group(edge.dst_type,
                                      dst_details.get('file') if dst_details else None,
                                      dst_details.get('fqn') if dst_details else None)
            else:
                dst_label = f"Unknown {edge.edge_kind}"
                dst_group = "Unknown"
            nodes_dict[dst_id] = create_node(dst_id, edge.dst_type, dst_label, dst_group, dst_details)
        
        # Add edge
        edge_id = f"edge:{edge.edge_id}" if hasattr(edge, 'edge_id') else f"edge:{len(json_edges)}"
        json_edges.append(create_edge(edge_id, src_id, dst_id, edge.edge_kind, edge.confidence))
    
    nodes_list = list(nodes_dict.values())
    print(f"  노드 {len(nodes_list)}개 생성")
    
    # Apply focus filtering if specified
    if focus:
        nodes_list, json_edges = filter_nodes_by_focus(nodes_list, json_edges, focus, depth)
        print(f"  포커스 필터 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")
    
    # Apply node limit
    if len(nodes_list) > max_nodes:
        nodes_list, json_edges = limit_nodes(nodes_list, json_edges, max_nodes)
        print(f"  노드 제한 적용 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")
    
    return create_graph(nodes_list, json_edges)


def _get_node_label(node_type: str, details: Dict[str, Any] = None) -> str:
    """Generate a readable label for a node"""
    if not details:
        return f"Unknown {node_type}"
    
    if node_type == 'method':
        class_name = details.get('class', '').split('.')[-1] if details.get('class') else 'Unknown'
        method_name = details.get('name', 'unknown')
        return f"{class_name}.{method_name}()"
    elif node_type == 'class':
        return details.get('fqn', details.get('name', 'Unknown'))
    elif node_type == 'file':
        path = details.get('path', 'unknown')
        return path.split('/')[-1] if '/' in path else path.split('\\')[-1]
    elif node_type == 'sql_unit':
        stmt_id = details.get('stmt_id', 'unknown')
        mapper_ns = details.get('mapper_ns', 'unknown')
        return f"{mapper_ns}.{stmt_id}"
    elif node_type == 'table':
        return details.get('name', 'Unknown Table')
    else:
        return f"{node_type}:{details.get('name', 'unknown')}"
