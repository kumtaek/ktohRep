# visualize/builders/sequence_diagram.py
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict, deque
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


def build_sequence_graph_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], start_file: str = None, start_method: str = None, 
                             depth: int = 3, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build sequence diagram JSON for visualization"""
    print(f"Building sequence diagram for project {project_id}")
    print(f"  Start file: {start_file}")
    print(f"  Start method: {start_method}")
    print(f"  Max depth: {depth}")
    print(f"  Max nodes: {max_nodes}")
    
    db = VizDB(config, project_name)
    
    # Get all edges for call tracing (including unresolved calls)
    edges = db.fetch_edges(project_id, ['call', 'call_unresolved', 'use_table', 'call_sql'], 0.0)
    
    # Find starting point
    start_nodes = _find_start_nodes(config, db, project_id, start_file, start_method)
    if not start_nodes:
        print("  Warning: No start nodes found, using JSP->SQL->Table pattern")
        return _build_jsp_sql_sequence(config, db, project_id, max_nodes)
    
    print(f"  Found {len(start_nodes)} start nodes")
    
    # Build call chain using BFS
    sequence_nodes, sequence_edges = _trace_call_sequence(config, db, edges, start_nodes, depth, max_nodes)
    
    print(f"  Generated {len(sequence_nodes)} nodes, {len(sequence_edges)} edges in sequence")
    
    return create_graph(sequence_nodes, sequence_edges)


def _find_start_nodes(config: Dict[str, Any], db: VizDB, project_id: int, start_file: str = None, 
                     start_method: str = None) -> List[Dict[str, Any]]:
    """Find starting nodes for sequence tracing"""
    start_nodes = []
    
    if start_file:
        files = db.load_project_files(project_id)
        matching_files = [f for f in files if start_file in f.path]
        
        if start_method:
            # Find specific method in file
            methods = db.fetch_methods_by_project(project_id)
            for method in methods:
                method_details = db.get_node_details('method', method.method_id)
                if (method_details and 
                    method_details.get('file') and 
                    any(start_file in f.path for f in matching_files if f.path == method_details['file']) and
                    start_method in method.name):
                    
                    start_nodes.append({
                        'id': f"method:{method.method_id}",
                        'type': 'method',
                        'label': f"{method.name}()",
                        'layer': 0,
                        'details': method_details
                    })
        else:
            # Use all methods in the file
            methods = db.fetch_methods_by_project(project_id)
            for method in methods:
                method_details = db.get_node_details('method', method.method_id)
                if (method_details and 
                    method_details.get('file') and
                    any(start_file in f.path for f in matching_files if f.path == method_details['file'])):
                    
                    start_nodes.append({
                        'id': f"method:{method.method_id}",
                        'type': 'method',
                        'label': f"{method.name}()",
                        'layer': 0,
                        'details': method_details
                    })
    
    return start_nodes


def _trace_call_sequence(config: Dict[str, Any], db: VizDB, edges: List, start_nodes: List[Dict[str, Any]], 
                        max_depth: int, max_nodes: int) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Trace call sequence using BFS"""
    
    # Build adjacency map
    adjacency = defaultdict(list)
    for edge in edges:
        src_id = f"{edge.src_type}:{edge.src_id}"
        dst_id = f"{edge.dst_type}:{edge.dst_id}" if edge.dst_id else None
        if dst_id:
            adjacency[src_id].append({
                'target': dst_id,
                'kind': edge.edge_kind,
                'confidence': edge.confidence,
                'edge': edge
            })
    
    # BFS traversal
    visited = set()
    sequence_nodes = []
    sequence_edges = []
    queue = deque()
    
    # Initialize queue with start nodes
    for start_node in start_nodes:
        queue.append((start_node['id'], 0, []))  # (node_id, depth, path)
        sequence_nodes.append(start_node)
        visited.add(start_node['id'])
    
    while queue and len(sequence_nodes) < max_nodes:
        current_id, current_depth, path = queue.popleft()
        
        if current_depth >= max_depth:
            continue
        
        # Get outgoing edges from current node
        for edge_info in adjacency.get(current_id, []):
            target_id = edge_info['target']
            
            if target_id not in visited or current_depth == 0:  # Allow revisit at depth 0
                # Get target node details
                node_type, raw_id = target_id.split(':', 1)
                try:
                    node_id = int(raw_id) if node_type in ('file', 'class', 'method', 'sql_unit') and raw_id.isdigit() else raw_id
                except ValueError:
                    node_id = raw_id
                target_details = db.get_node_details(node_type, node_id)
                
                if target_details:
                    target_node = {
                        'id': target_id,
                        'type': node_type,
                        'label': _get_sequence_label(node_type, target_details),
                        'layer': current_depth + 1,
                        'details': target_details
                    }
                    
                    if target_id not in visited:
                        sequence_nodes.append(target_node)
                        visited.add(target_id)
                        queue.append((target_id, current_depth + 1, path + [current_id]))
                    
                    # Add edge with unresolved marking
                    edge_id = f"seq_edge:{len(sequence_edges)}"
                    is_unresolved = edge_info['kind'] == 'call_unresolved'
                    sequence_edges.append({
                        'id': edge_id,
                        'source': current_id,
                        'target': target_id,
                        'kind': edge_info['kind'],
                        'confidence': edge_info['confidence'],
                        'sequence_order': len(sequence_edges),
                        'depth': current_depth,
                        'meta': {
                            'unresolved': is_unresolved,
                            'style': 'dashed' if is_unresolved else 'solid'
                        }
                    })
    
    return sequence_nodes, sequence_edges


def _build_jsp_sql_sequence(config: Dict[str, Any], db: VizDB, project_id: int, max_nodes: int) -> Dict[str, Any]:
    """Build basic JSP->SQL->Table sequence when no specific start point is given"""
    print("  Building basic JSP->SQL->Table sequence")
    
    # Get JSP files
    files = db.load_project_files(project_id)
    jsp_files = [f for f in files if f.path.lower().endswith('.jsp')]
    
    # Get SQL units
    sql_units = db.fetch_sql_units_by_project(project_id)
    
    # Get table usage edges
    table_edges = db.fetch_edges(project_id, ['use_table'], 0.3)
    
    sequence_nodes = []
    sequence_edges = []
    layer_counter = 0
    
    # Layer 1: JSP files
    for jsp in jsp_files[:min(5, len(jsp_files))]:  # Limit JSP files
        node_id = f"file:{jsp.file_id}"
        sequence_nodes.append({
            'id': node_id,
            'type': 'file',
            'label': jsp.path.split('/')[-1] if '/' in jsp.path else jsp.path.split('\\')[-1],
            'layer': 0,
            'details': {'path': jsp.path, 'language': 'JSP'}
        })
    
    # Layer 2: SQL units
    for sql in sql_units[:min(10, len(sql_units))]:  # Limit SQL units
        node_id = f"sql_unit:{sql.sql_id}"
        sequence_nodes.append({
            'id': node_id,
            'type': 'sql_unit',
            'label': f"{sql.mapper_ns}.{sql.stmt_id}" if sql.stmt_id else sql.mapper_ns,
            'layer': 1,
            'details': {
                'mapper_ns': sql.mapper_ns,
                'stmt_id': sql.stmt_id,
                'stmt_kind': sql.stmt_kind
            }
        })
    
    # Layer 3: Tables (from table usage)
    used_tables = set()
    for edge in table_edges:
        if edge.dst_type == 'table' and edge.dst_id:
            table_name = f"table:{edge.dst_id}"
            if table_name not in used_tables:
                used_tables.add(table_name)
                sequence_nodes.append({
                    'id': table_name,
                    'type': 'table',
                    'label': f"Table {edge.dst_id}",
                    'layer': 2,
                    'details': {'name': edge.dst_id}
                })
    
    # Create flow edges (simplified)
    edge_id_counter = 0
    # JSP -> SQL connections (generic)
    jsp_nodes = [n for n in sequence_nodes if n['type'] == 'file']
    sql_nodes = [n for n in sequence_nodes if n['type'] == 'sql_unit']
    
    for i, jsp in enumerate(jsp_nodes):
        if i < len(sql_nodes):
            sequence_edges.append({
                'id': f"flow_edge:{edge_id_counter}",
                'source': jsp['id'],
                'target': sql_nodes[i]['id'],
                'kind': 'renders',
                'confidence': 0.7,
                'sequence_order': edge_id_counter,
                'depth': 0
            })
            edge_id_counter += 1
    
    # SQL -> Table connections (from actual edges)
    for edge in table_edges:
        src_id = f"sql_unit:{edge.src_id}"
        dst_id = f"table:{edge.dst_id}"
        
        if any(n['id'] == src_id for n in sequence_nodes) and any(n['id'] == dst_id for n in sequence_nodes):
            sequence_edges.append({
                'id': f"flow_edge:{edge_id_counter}",
                'source': src_id,
                'target': dst_id,
                'kind': edge.edge_kind,
                'confidence': edge.confidence,
                'sequence_order': edge_id_counter,
                'depth': 1
            })
            edge_id_counter += 1
    
    print(f"  Generated basic sequence: {len(sequence_nodes)} nodes, {len(sequence_edges)} edges")
    
    return create_graph(sequence_nodes, sequence_edges)


def _get_sequence_label(node_type: str, details: Dict[str, Any]) -> str:
    """Generate label for sequence diagram node"""
    if node_type == 'method':
        class_name = details.get('class', '').split('.')[-1] if details.get('class') else ''
        method_name = details.get('name', 'unknown')
        return f"{class_name}.{method_name}()" if class_name else f"{method_name}()"
    elif node_type == 'sql_unit':
        return f"{details.get('mapper_ns', '')}.{details.get('stmt_id', '')}"
    elif node_type == 'table':
        return f"Table: {details.get('name', 'Unknown')}"
    elif node_type == 'file':
        path = details.get('path', '')
        return path.split('/')[-1] if '/' in path else path.split('\\')[-1]
    else:
        return f"{node_type}: {details.get('name', 'Unknown')}"