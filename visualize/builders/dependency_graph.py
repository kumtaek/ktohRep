# visualize/builders/dependency_graph.py
from typing import List, Dict, Any, Optional
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph, filter_nodes_by_focus, limit_nodes
from ..clustering import AdvancedClusterer


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
    
    # If no edges found with specified kinds, try to find what kinds exist
    if len(edges) == 0:
        all_edges = db.fetch_all_edges(project_id)
        print(f"  전체 엣지 {len(all_edges)}개 발견")
        if all_edges:
            available_kinds = set(edge.edge_kind for edge in all_edges)
            print(f"  사용 가능한 엣지 종류: {sorted(available_kinds)}")
            # Use package_relation if available
            if 'package_relation' in available_kinds:
                edges = db.fetch_edges(project_id, ['package_relation'], min_conf)
                print(f"  package_relation 엣지 {len(edges)}개 사용")
    
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
        if src_id not in nodes_dict and src_details:
            from ..schema import guess_group
            src_label = _get_node_label(edge.src_type, src_details)
            src_group = guess_group(edge.src_type, src_details.get('path') or src_details.get('file'), src_details.get('fqn'))
            nodes_dict[src_id] = create_node(src_id, edge.src_type, src_label, src_group, src_details)
        
        # Add destination node
        if dst_id not in nodes_dict and dst_details:
            dst_label = _get_node_label(edge.dst_type, dst_details)
            dst_group = guess_group(edge.dst_type, dst_details.get('path') or dst_details.get('file'), dst_details.get('fqn'))
            nodes_dict[dst_id] = create_node(dst_id, edge.dst_type, dst_label, dst_group, dst_details)
        
        # Add edge
        json_edges.append(create_edge(
            f"edge_{edge.edge_id}",
            src_id,
            dst_id,
            edge.edge_kind,
            edge.confidence,
            edge.meta
        ))
    
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

    def _bin_hotspot(loc: int | None, cx: int | None) -> str:
        # LOC-based bins; promote if complexity high
        loc_val = int(loc) if isinstance(loc, (int, float)) else 0
        cx_val = int(cx) if isinstance(cx, (int, float)) else 0
        if loc_val <= 100:
            base = 'low'
        elif loc_val <= 300:
            base = 'med'
        elif loc_val <= 800:
            base = 'high'
        else:
            base = 'crit'
        if cx_val >= 20 and base in ('low', 'med'):
            return 'high'
        return base

    # Fetch vulnerabilities and map by node id string
    try:
        vulns = db.fetch_vulnerabilities(project_id)
    except Exception as _:
        vulns = []
    by_target: Dict[str, list] = {}
    for v in vulns or []:
        key = f"{getattr(v, 'target_type', None)}:{getattr(v, 'target_id', None)}"
        by_target.setdefault(key, []).append(v)

    # Apply meta to nodes
    for n in nodes_list:
        nid = n['id']
        details = n.get('meta') or {}
        loc = details.get('loc') or details.get('lines_of_code')
        cx = details.get('complexity_est')
        # If no complexity, derive from out-degree of call edges
        if cx is None:
            cx = out_degree.get(nid, 0)
        # Store meta
        if n.get('meta') is None:
            n['meta'] = {}
        n['meta']['loc'] = int(loc) if isinstance(loc, (int, float)) else (loc or 0)
        n['meta']['complexity_est'] = int(cx) if isinstance(cx, (int, float)) else 0
        n['meta']['hotspot_bin'] = _bin_hotspot(n['meta']['loc'], n['meta']['complexity_est'])

        # Vulnerabilities
        vlist = by_target.get(nid, [])
        if vlist:
            counts: Dict[str, int] = {}
            for v in vlist:
                sev = (getattr(v, 'severity', '') or 'none').lower()
                counts[sev] = counts.get(sev, 0) + 1
            # Determine max severity by order
            order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'none': 0}
            max_sev = max(counts, key=lambda s: order.get(s, 0)) if counts else 'none'
            n['meta']['vuln_counts'] = counts
            n['meta']['vuln_max_severity'] = max_sev

    graph = create_graph(nodes_list, json_edges)
    # Attach filter metadata and cluster definitions for documentation/export context
    graph.setdefault('metadata', {})
    graph['metadata']['filters'] = {
        'kinds': ','.join(kinds) if kinds else '',
        'min_confidence': min_conf,
        'focus': focus or '',
        'depth': depth,
        'max_nodes': max_nodes,
    }
    graph['metadata']['clusters'] = clusterer.get_all_cluster_defs()

    return graph


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
