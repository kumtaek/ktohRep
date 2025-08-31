# visualize/builders/sequence_diagram.py
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict, deque
from ..data_access import VizDB
from pathlib import Path
from ..schema import create_node, create_edge, create_graph
from difflib import get_close_matches


def build_sequence_graph_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], start_file: str = None, start_method: str = None, 
                             depth: int = 3, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build UML sequence diagram JSON for visualization"""
    print(f"Building sequence diagram for project {project_id}")
    print(f"  Start file: {start_file}")
    print(f"  Start method: {start_method}")
    print(f"  Max depth: {depth}")
    print(f"  Max nodes: {max_nodes}")
    
    db = VizDB(config, project_name)
    
    # Get all edges first to see what's available
    all_edges = db.fetch_edges(project_id, [], 0.0)  # Get all edge types
    
    if all_edges:
        edge_types = {}
        for edge in all_edges:
            edge_types[edge.edge_kind] = edge_types.get(edge.edge_kind, 0) + 1
    
    # Get all edges for call tracing (including unresolved calls)
    target_edge_types = ['call', 'call_unresolved', 'use_table', 'call_sql']
    edges = db.fetch_edges(project_id, target_edge_types, 0.0)
    
    # If no specific edges found, try to use available edges that make sense for sequence
    if not edges:
        available_types = list(edge_types.keys()) if all_edges else []
        
        # Try to find any relationship edges that could show flow
        alternative_types = []
        for edge_type in available_types:
            if any(keyword in edge_type.lower() for keyword in ['call', 'use', 'invoke', 'include', 'depend', 'relation']):
                alternative_types.append(edge_type)
        
        if alternative_types:
            print(f"  Using alternative edge types: {alternative_types}")
            edges = db.fetch_edges(project_id, alternative_types, 0.0)
        else:
            edges = all_edges
    
    # Find starting point
    start_nodes = _find_start_nodes(config, db, project_id, start_file, start_method)
    if not start_nodes:
        print("  Warning: No start nodes found.")
        possible_files = db.get_files_with_methods(project_id, limit=20)
        if possible_files:
            print("  Available files with methods:")
            for path in possible_files:
                print(f"    - {path}")
            print("  Please choose one of the above files and optionally a method name for more accurate results.")
        else:
            print("  No files with methods were found in this project.")
        print("  Defaulting to JSP->SQL->Table pattern. Specify a file/method to avoid this fallback.")
        return _build_jsp_sql_sequence(config, db, project_id, max_nodes)
    
    print(f"  Found {len(start_nodes)} start nodes")
    
    # Build UML sequence diagram 
    sequence_data = _build_uml_sequence_diagram(config, db, edges, start_nodes, depth, max_nodes)
    
    print(f"  Generated UML sequence diagram with {len(sequence_data['participants'])} participants and {len(sequence_data['interactions'])} interactions")
    
    return sequence_data


def _find_start_nodes(config: Dict[str, Any], db: VizDB, project_id: int, start_file: str = None, 
                     start_method: str = None) -> List[Dict[str, Any]]:
    """Find starting nodes for sequence tracing"""
    start_nodes = []
    
    if start_file:
        files = db.load_project_files(project_id)
        normalized_start = Path(start_file).as_posix()
        file_tuples = [(f, Path(f.path).as_posix()) for f in files]
        matching_files = [f for f, path in file_tuples if normalized_start in path]
        if not matching_files:
            suggestions = get_close_matches(normalized_start, [path for _, path in file_tuples], n=3)
            print(f"  Warning: start file '{start_file}' not found.")
            if suggestions:
                print(f"  Did you mean: {', '.join(suggestions)}?")

        matching_paths = [Path(f.path).as_posix() for f in matching_files]
        
        if start_method:
            # Find specific method in file
            methods = db.fetch_methods_by_project(project_id)
            for method in methods:
                method_details = db.get_node_details('method', method.method_id)
                if (method_details and
                    method_details.get('file') and
                    Path(method_details['file']).as_posix() in matching_paths and
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
                    Path(method_details['file']).as_posix() in matching_paths):
                    
                    start_nodes.append({
                        'id': f"method:{method.method_id}",
                        'type': 'method',
                        'label': f"{method.name}()",
                        'layer': 0,
                        'details': method_details
                    })
    
    return start_nodes


def _build_uml_sequence_diagram(config: Dict[str, Any], db: VizDB, edges: List, start_nodes: List[Dict[str, Any]], 
                               max_depth: int, max_nodes: int) -> Dict[str, Any]:
    """Build proper UML sequence diagram data structure"""
    
    # Build adjacency map
    adjacency = defaultdict(list)
    unknown_counter = 0

    for edge in edges:
        src_id = f"{edge.src_type}:{edge.src_id}"
        if edge.dst_id:
            dst_id = f"{edge.dst_type}:{edge.dst_id}"
        elif edge.edge_kind == 'call_unresolved':
            dst_id = f"unknown:{unknown_counter}"
            unknown_counter += 1
        else:
            dst_id = None

        if dst_id:
            adjacency[src_id].append({
                'target': dst_id,
                'kind': edge.edge_kind,
                'confidence': edge.confidence,
                'edge': edge
            })
    
    # If we have class/file level edges but no method level edges, create simplified connections
    if adjacency and not any('method:' in src_id for src_id in adjacency.keys()):
        print("  Creating simplified method sequence from available methods...")
        method_adjacency = defaultdict(list)
        
        # Get all methods from start nodes 
        start_method_ids = [node['id'] for node in start_nodes if node['type'] == 'method']
        
        # Create some connections between start methods to show a sequence flow
        if len(start_method_ids) > 1:
            for i, current_method in enumerate(start_method_ids[:-1]):
                next_method = start_method_ids[i + 1]
                method_adjacency[current_method].append({
                    'target': next_method,
                    'kind': 'inferred_sequence',
                    'confidence': 0.5,
                    'edge': None
                })
        
        if method_adjacency:
            print(f"  Created {len(method_adjacency)} method connections")
            adjacency.update(method_adjacency)
    
    # Track participants and interactions for UML sequence
    participants = {}  # id -> participant info
    interactions = []  # chronological list of interactions
    lifelines = set()  # active lifelines
    
    # Process nodes in chronological order
    visited = set()
    queue = deque()
    sequence_order = 0
    
    # Initialize with start nodes
    for start_node in start_nodes:
        participant_id = start_node['id']
        participants[participant_id] = {
            'id': participant_id,
            'type': start_node['type'],
            'label': start_node['label'],
            'actor_type': _get_actor_type(start_node['type']),
            'order': len(participants),
            'details': start_node.get('details', {})
        }
        lifelines.add(participant_id)
        queue.append((participant_id, 0, None))  # (node_id, depth, caller_id)
        visited.add(participant_id)
    
    while queue and len(participants) < max_nodes:
        current_id, current_depth, caller_id = queue.popleft()
        
        if current_depth >= max_depth:
            continue
        
        # Process outgoing calls from current participant
        current_edges = adjacency.get(current_id, [])
        
        for edge_info in current_edges:
            target_id = edge_info['target']
            
            # Get target node details
            node_type, raw_id = target_id.split(':', 1)
            try:
                node_id = int(raw_id) if node_type in ('file', 'class', 'method', 'sql_unit') and raw_id.isdigit() else raw_id
            except ValueError:
                node_id = raw_id
            target_details = db.get_node_details(node_type, node_id)
            
            if target_details:
                # Add participant if not exists
                if target_id not in participants:
                    participants[target_id] = {
                        'id': target_id,
                        'type': node_type,
                        'label': _get_sequence_label(node_type, target_details),
                        'actor_type': _get_actor_type(node_type),
                        'order': len(participants),
                        'details': target_details
                    }
                    lifelines.add(target_id)
                
                # Add interaction
                interaction_type = _get_interaction_type(edge_info['kind'])
                is_unresolved = edge_info['kind'] == 'call_unresolved'
                
                interactions.append({
                    'id': f"interaction_{sequence_order}",
                    'sequence_order': sequence_order,
                    'type': interaction_type,
                    'from_participant': current_id,
                    'to_participant': target_id,
                    'message': _get_interaction_message(edge_info['kind'], participants[current_id], participants[target_id]),
                    'confidence': edge_info['confidence'],
                    'unresolved': is_unresolved,
                    'depth': current_depth,
                    'style': 'dashed' if is_unresolved else 'solid',
                    'meta': {
                        'edge_kind': edge_info['kind'],
                        'caller_details': participants[current_id]['details'],
                        'target_details': participants[target_id]['details']
                    }
                })
                sequence_order += 1
                
                # Continue traversal
                if target_id not in visited or current_depth == 0:
                    queue.append((target_id, current_depth + 1, current_id))
                    visited.add(target_id)

    # Fallback: If no interactions were found, create a simplified sequence.
    if not interactions and len(participants) > 1:
        print("  No method calls found. Creating a simplified sequence flow based on participant order.")
        sorted_participants = sorted(participants.values(), key=lambda p: p['order'])
        for i in range(len(sorted_participants) - 1):
            from_p = sorted_participants[i]
            to_p = sorted_participants[i+1]
            interactions.append({
                'id': f"interaction_inferred_{i}",
                'sequence_order': i,
                'type': 'synchronous',
                'from_participant': from_p['id'],
                'to_participant': to_p['id'],
                'message': f"inferred_sequence_to: {to_p['label']}",
                'confidence': 0.1,
                'unresolved': True,
                'depth': 0,
                'style': 'dashed',
                'meta': {
                    'edge_kind': 'inferred_sequence',
                    'caller_details': from_p.get('details', {}),
                    'target_details': to_p.get('details', {})
                }
            })
    
    # Generate mermaid sequence diagram syntax
    mermaid_syntax = _generate_mermaid_sequence(participants, interactions)
    
    # Convert participants and interactions to nodes and edges for create_graph
    nodes = []
    for p_id, p_data in participants.items():
        nodes.append(create_node(
            id=p_id,
            label=p_data['label'],
            type=p_data['type'],
            group=p_data['actor_type'],
            meta=p_data.get('details', {})
        ))

    sequence_edges = []
    for i, interaction in enumerate(interactions):
        sequence_edges.append(create_edge(
            id=f"seq_edge_{i}",
            source=interaction['from_participant'],
            target=interaction['to_participant'],
            kind=interaction['meta']['edge_kind'],
            confidence=interaction.get('confidence', 1.0),
            details={
                'sequence_order': interaction['sequence_order'],
                'message': interaction['message'],
                'unresolved': interaction.get('unresolved', False)
            }
        ))

    graph_data = create_graph(nodes, sequence_edges)
    graph_data['mermaid'] = mermaid_syntax
    graph_data['type'] = 'sequence_diagram'
    graph_data['participants'] = list(participants.values())
    graph_data['interactions'] = interactions
    
    return graph_data


def _build_jsp_sql_sequence(config: Dict[str, Any], db: VizDB, project_id: int, max_nodes: int) -> Dict[str, Any]:
    """Build basic JSP->SQL->Table sequence when no specific start point is given"""
    print("  Building basic JSP->SQL->Table sequence")
    
    # Get JSP files
    files = db.load_project_files(project_id)
    jsp_files = [f for f in files if f.path.lower().endswith('.jsp')]
    
    # Get SQL units
    sql_units = db.fetch_sql_units_by_project(project_id)

    if not jsp_files or not sql_units:
        missing = []
        if not jsp_files:
            missing.append("JSP files")
        if not sql_units:
            missing.append("SQL units")
        missing_desc = " and ".join(missing)
        raise ValueError(
            f"Cannot build JSP->SQL sequence: no {missing_desc} found for project {project_id}"
        )
    
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


def _get_actor_type(node_type: str) -> str:
    """Get UML actor type for participant"""
    actor_mapping = {
        'file': 'control',
        'class': 'control', 
        'method': 'control',
        'sql_unit': 'boundary',
        'table': 'entity',
        'controller': 'control',
        'service': 'control',
        'repository': 'boundary',
        'mapper': 'boundary'
    }
    return actor_mapping.get(node_type.lower(), 'control')


def _get_interaction_type(edge_kind: str) -> str:
    """Get UML interaction type from edge kind"""
    interaction_mapping = {
        'call': 'synchronous',
        'call_unresolved': 'asynchronous', 
        'use_table': 'synchronous',
        'call_sql': 'synchronous',
        'include': 'include',
        'extends': 'extend'
    }
    return interaction_mapping.get(edge_kind, 'synchronous')


def _get_interaction_message(edge_kind: str, from_participant: Dict, to_participant: Dict) -> str:
    """Generate interaction message for sequence diagram"""
    if edge_kind == 'call':
        return f"call {to_participant['label']}"
    elif edge_kind == 'call_unresolved':
        return f"call? {to_participant['label']}"
    elif edge_kind == 'use_table':
        return f"query {to_participant['label']}"
    elif edge_kind == 'call_sql':
        return f"execute {to_participant['label']}"
    else:
        return f"{edge_kind} {to_participant['label']}"


def _generate_mermaid_sequence(participants: Dict[str, Dict], interactions: List[Dict]) -> str:
    """Generate Mermaid sequence diagram syntax"""
    lines = ['sequenceDiagram']
    
    # Sort participants by order
    sorted_participants = sorted(participants.values(), key=lambda p: p['order'])
    
    # Add participant declarations
    for participant in sorted_participants:
        actor_symbol = 'actor' if participant['actor_type'] == 'entity' else 'participant'
        clean_id = participant['id'].replace(':', '_').replace('-', '_')
        lines.append(f"    {actor_symbol} {clean_id} as {participant['label']}")
    
    lines.append('')
    
    # Add interactions in sequence order
    sorted_interactions = sorted(interactions, key=lambda i: i['sequence_order'])
    
    for interaction in sorted_interactions:
        from_id = interaction['from_participant'].replace(':', '_').replace('-', '_')
        to_id = interaction['to_participant'].replace(':', '_').replace('-', '_')
        message = interaction['message']
        
        # Choose arrow type based on interaction type and style
        if interaction.get('unresolved', False):
            arrow = '-->>>'
        elif interaction['type'] == 'asynchronous':
            arrow = '->>'
        else:
            arrow = '->>'
        
        # Add confidence indicator for low confidence calls
        if interaction['confidence'] < 0.7:
            message += f" (conf: {interaction['confidence']:.2f})"
        
        lines.append(f"    {from_id}{arrow}{to_id}: {message}")
        
        # Add note for unresolved calls
        if interaction.get('unresolved', False):
            lines.append(f"    Note over {to_id}: Unresolved call")
    
    return '\n'.join(lines)