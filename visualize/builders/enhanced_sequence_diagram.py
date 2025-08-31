# enhanced_sequence_diagram.py
"""
Enhanced sequence diagram builder with automatic start point detection
and improved edge registration handling.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict, deque
import json
from pathlib import Path
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph
from sqlalchemy import or_, and_


def build_automatic_sequence_diagrams(config: Dict[str, Any], project_id: int, project_name: Optional[str], 
                                     max_diagrams: int = 5, depth: int = 3, max_nodes: int = 50) -> List[Dict[str, Any]]:
    """
    Build multiple sequence diagrams automatically from discovered entry points
    
    Args:
        config: Database configuration
        project_id: Project identifier
        project_name: Project name
        max_diagrams: Maximum number of diagrams to generate
        depth: Maximum call depth to trace
        max_nodes: Maximum nodes per diagram
        
    Returns:
        List of sequence diagram data structures
    """
    print(f"Building automatic sequence diagrams for project {project_id}")
    
    # VizDB expects the full config structure
    if 'database' not in config:
        full_config = {'database': {'project': config}}
    else:
        full_config = config
    db = VizDB(full_config, project_name)
    
    # Step 1: Discover and repair edge metadata issues
    print("  Step 1: Analyzing and repairing edge metadata...")
    repaired_edges = _repair_edge_metadata(db, project_id)
    print(f"    Repaired {repaired_edges} edges")
    
    # Step 2: Find potential entry points automatically
    print("  Step 2: Discovering entry points...")
    entry_points = _discover_entry_points(db, project_id)
    print(f"    Found {len(entry_points)} potential entry points")
    
    # Step 3: Generate diagrams from best entry points
    print("  Step 3: Generating sequence diagrams...")
    diagrams = []
    
    for i, entry_point in enumerate(entry_points[:max_diagrams]):
        print(f"    Creating diagram {i+1} from {entry_point['type']}:{entry_point['name']}")
        
        diagram = _build_sequence_from_entry_point(
            config, db, project_id, entry_point, depth, max_nodes
        )
        
        if diagram and diagram.get('interactions'):
            diagram['title'] = f"Sequence from {entry_point['name']}"
            diagram['entry_point'] = entry_point
            diagrams.append(diagram)
        else:
            print(f"      No meaningful sequence found for {entry_point['name']}")
    
    print(f"  Generated {len(diagrams)} sequence diagrams")
    
    return diagrams


def _repair_edge_metadata(db: VizDB, project_id: int) -> int:
    """
    Repair missing src_id/dst_id in edges by analyzing available metadata
    """
    repaired_count = 0
    
    with db.dbm.get_session() as session:
        from models.database import Edge, Method, Class, File
        
        # Find edges with missing src_id or dst_id
        broken_edges = session.query(Edge).filter(
            and_(
                Edge.project_id == project_id,
                or_(Edge.src_id.is_(None), Edge.dst_id.is_(None)),
                Edge.edge_kind.in_(['call', 'call_unresolved', 'use_table', 'call_sql'])
            )
        ).all()
        
        for edge in broken_edges:
            original_src = edge.src_id
            original_dst = edge.dst_id
            
            # Try to repair src_id from metadata
            if edge.src_id is None and edge.src_type == 'method':
                src_id = _resolve_method_id_from_meta(session, edge, project_id, 'src')
                if src_id:
                    edge.src_id = src_id
                    repaired_count += 1
            
            # Try to repair dst_id from metadata  
            if edge.dst_id is None and edge.dst_type in ['method', 'table']:
                dst_id = _resolve_method_id_from_meta(session, edge, project_id, 'dst')
                if dst_id:
                    edge.dst_id = dst_id
                    repaired_count += 1
                else:
                    # If still unresolved, create placeholder with metadata
                    _create_placeholder_target(session, edge, project_id)
        
        session.commit()
    
    return repaired_count


def _resolve_method_id_from_meta(session, edge, project_id: int, id_type: str) -> Optional[int]:
    """
    Try to resolve missing method ID from edge metadata
    """
    from models.database import Method, Class, File
    
    if not hasattr(edge, 'meta') or not edge.meta:
        return None
        
    try:
        meta = json.loads(edge.meta)
    except:
        return None
    
    if id_type == 'src':
        src_method_fqn = meta.get('src_method_fqn')
        if src_method_fqn and '.' in src_method_fqn:
            class_fqn, method_name = src_method_fqn.rsplit('.', 1)
            
            method = session.query(Method).join(Class).join(File).filter(
                and_(
                    Class.fqn == class_fqn,
                    Method.name == method_name,
                    File.project_id == project_id
                )
            ).first()
            
            return method.method_id if method else None
    
    elif id_type == 'dst':
        called_name = meta.get('called_name')
        if called_name:
            # Try different resolution strategies
            qualifier_type = meta.get('callee_qualifier_type')
            
            # Strategy 1: Use qualifier type if available
            if qualifier_type:
                method = session.query(Method).join(Class).join(File).filter(
                    and_(
                        Class.fqn.like(f"%{qualifier_type}%"),
                        Method.name == called_name,
                        File.project_id == project_id
                    )
                ).first()
                
                if method:
                    return method.method_id
            
            # Strategy 2: Find by method name only
            method = session.query(Method).join(Class).join(File).filter(
                and_(
                    Method.name == called_name,
                    File.project_id == project_id
                )
            ).first()
            
            if method:
                return method.method_id
    
    return None


def _create_placeholder_target(session, edge, project_id: int):
    """
    Create placeholder target for unresolved calls to maintain sequence flow
    """
    from models.database import Method, Class, File
    
    if not hasattr(edge, 'meta') or not edge.meta:
        return
        
    try:
        meta = json.loads(edge.meta)
        called_name = meta.get('called_name', 'Unknown')
    except:
        called_name = 'Unknown'
    
    # For sequence diagrams, we'll handle this in the visualization layer
    # by creating virtual nodes for unresolved calls
    pass


def _discover_entry_points(db: VizDB, project_id: int) -> List[Dict[str, Any]]:
    """
    Automatically discover potential entry points for sequence diagrams
    """
    entry_points = []
    
    # Strategy 1: Find controller methods (common entry points)
    controller_methods = _find_controller_methods(db, project_id)
    entry_points.extend(controller_methods)
    
    # Strategy 2: Find service methods with multiple callers
    service_methods = _find_service_entry_methods(db, project_id)
    entry_points.extend(service_methods)
    
    # Strategy 3: Find main/test methods
    main_methods = _find_main_methods(db, project_id)
    entry_points.extend(main_methods)
    
    # Strategy 4: Find methods with high outgoing call count
    high_activity_methods = _find_high_activity_methods(db, project_id)
    entry_points.extend(high_activity_methods)
    
    # Sort by priority score and remove duplicates
    seen_ids = set()
    unique_points = []
    
    for point in sorted(entry_points, key=lambda x: x.get('priority', 0), reverse=True):
        key = f"{point['type']}:{point['id']}"
        if key not in seen_ids:
            seen_ids.add(key)
            unique_points.append(point)
    
    return unique_points


def _find_controller_methods(db: VizDB, project_id: int) -> List[Dict[str, Any]]:
    """Find methods in controller classes"""
    entry_points = []
    
    with db.dbm.get_session() as session:
        from models.database import Method, Class, File
        
        methods = session.query(Method).join(Class).join(File).filter(
            File.project_id == project_id,
            or_(
                Class.fqn.like('%Controller%'),
                Class.fqn.like('%controller%'),
                Class.name.like('%Controller%'),
                Class.name.like('%controller%')
            )
        ).all()
        
        for method in methods:
            entry_points.append({
                'id': method.method_id,
                'type': 'method',
                'name': f"{method.class_.name}.{method.name}",
                'full_name': f"{method.class_.fqn}.{method.name}",
                'priority': 10,  # High priority for controllers
                'category': 'controller'
            })
    
    return entry_points


def _find_service_entry_methods(db: VizDB, project_id: int) -> List[Dict[str, Any]]:
    """Find service methods that could be good entry points"""
    entry_points = []
    
    with db.dbm.get_session() as session:
        from models.database import Method, Class, File, Edge
        
        # Find methods in service classes that have outgoing calls
        methods = session.query(Method).join(Class).join(File).filter(
            File.project_id == project_id,
            or_(
                Class.fqn.like('%Service%'),
                Class.fqn.like('%service%'),
                Class.name.like('%Service%'),
                Class.name.like('%service%')
            )
        ).all()
        
        for method in methods:
            # Count outgoing calls
            call_count = session.query(Edge).filter(
                and_(
                    Edge.src_type == 'method',
                    Edge.src_id == method.method_id,
                    Edge.edge_kind.in_(['call', 'call_unresolved'])
                )
            ).count()
            
            if call_count > 0:
                entry_points.append({
                    'id': method.method_id,
                    'type': 'method', 
                    'name': f"{method.class_.name}.{method.name}",
                    'full_name': f"{method.class_.fqn}.{method.name}",
                    'priority': 8,
                    'category': 'service',
                    'call_count': call_count
                })
    
    return entry_points


def _find_main_methods(db: VizDB, project_id: int) -> List[Dict[str, Any]]:
    """Find main methods and test methods"""
    entry_points = []
    
    with db.dbm.get_session() as session:
        from models.database import Method, Class, File
        
        methods = session.query(Method).join(Class).join(File).filter(
            File.project_id == project_id,
            or_(Method.name == 'main', Method.name.like('test%'))
        ).all()
        
        for method in methods:
            priority = 15 if method.name == 'main' else 5
            entry_points.append({
                'id': method.method_id,
                'type': 'method',
                'name': f"{method.class_.name}.{method.name}",
                'full_name': f"{method.class_.fqn}.{method.name}",
                'priority': priority,
                'category': 'main' if method.name == 'main' else 'test'
            })
    
    return entry_points


def _find_high_activity_methods(db: VizDB, project_id: int) -> List[Dict[str, Any]]:
    """Find methods with high outgoing call activity"""
    entry_points = []
    
    with db.dbm.get_session() as session:
        from models.database import Method, Class, File, Edge
        from sqlalchemy import func
        
        # Find methods with most outgoing calls
        results = session.query(
            Method.method_id,
            Method.name,
            Class.name.label('class_name'),
            Class.fqn.label('class_fqn'),
            func.count(Edge.edge_id).label('call_count')
        ).join(Class).join(File).outerjoin(
            Edge, (Edge.src_type == 'method') & (Edge.src_id == Method.method_id)
        ).filter(
            and_(
                File.project_id == project_id,
                Edge.edge_kind.in_(['call', 'call_unresolved'])
            )
        ).group_by(
            Method.method_id
        ).having(
            func.count(Edge.edge_id) >= 2
        ).order_by(
            func.count(Edge.edge_id).desc()
        ).limit(10).all()
        
        for result in results:
            entry_points.append({
                'id': result.method_id,
                'type': 'method',
                'name': f"{result.class_name}.{result.name}",
                'full_name': f"{result.class_fqn}.{result.name}",
                'priority': min(7, result.call_count),
                'category': 'high_activity',
                'call_count': result.call_count
            })
    
    return entry_points


def _build_sequence_from_entry_point(config: Dict[str, Any], db: VizDB, project_id: int, 
                                    entry_point: Dict[str, Any], depth: int, max_nodes: int) -> Dict[str, Any]:
    """
    Build sequence diagram starting from a specific entry point
    """
    # Get edges for tracing
    target_edge_types = ['call', 'call_unresolved', 'use_table', 'call_sql']
    edges = db.fetch_edges(project_id, target_edge_types, 0.0)
    
    # Create start node
    start_node = {
        'id': f"method:{entry_point['id']}",
        'type': 'method',
        'label': entry_point['name'],
        'layer': 0,
        'details': db.get_node_details('method', entry_point['id']) or {}
    }
    
    # Build sequence using enhanced algorithm
    sequence_data = _build_enhanced_sequence_diagram(
        db, edges, [start_node], depth, max_nodes, project_id
    )
    
    return sequence_data


def _build_enhanced_sequence_diagram(db: VizDB, edges: List, start_nodes: List[Dict[str, Any]], 
                                   max_depth: int, max_nodes: int, project_id: int) -> Dict[str, Any]:
    """
    Build enhanced sequence diagram with better handling of missing metadata
    """
    # Build adjacency map with enhanced edge handling
    adjacency = defaultdict(list)
    unresolved_counter = 0
    
    for edge in edges:
        src_id = f"{edge.src_type}:{edge.src_id}" if edge.src_id else None
        
        # Handle destination
        if edge.dst_id:
            dst_id = f"{edge.dst_type}:{edge.dst_id}"
            target_details = None
        else:
            # Create virtual node for unresolved calls
            called_name = 'Unknown'
            if hasattr(edge, 'meta') and edge.meta:
                try:
                    meta = json.loads(edge.meta)
                    called_name = meta.get('called_name', 'Unknown')
                except:
                    pass
            
            dst_id = f"unresolved:{unresolved_counter}"
            target_details = {'name': called_name, 'virtual': True}
            unresolved_counter += 1
        
        if src_id and dst_id:
            adjacency[src_id].append({
                'target': dst_id,
                'kind': edge.edge_kind,
                'confidence': edge.confidence,
                'edge': edge,
                'target_details': target_details,
            })
    
    # Build sequence using BFS
    participants = {}
    interactions = []
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
        queue.append((participant_id, 0, None))
        visited.add(participant_id)
    
    while queue and len(participants) < max_nodes:
        current_id, current_depth, caller_id = queue.popleft()
        
        if current_depth >= max_depth:
            continue
        
        # Process outgoing calls
        current_edges = adjacency.get(current_id, [])
        
        for edge_info in current_edges:
            target_id = edge_info['target']
            target_details = edge_info.get('target_details')
            
            # Get or create target details
            if not target_details:
                node_type, raw_id = target_id.split(':', 1)
                if node_type == 'unresolved':
                    target_details = {'name': f'unresolved_{raw_id}', 'virtual': True}
                else:
                    try:
                        node_id = int(raw_id) if raw_id.isdigit() else raw_id
                        target_details = db.get_node_details(node_type, node_id)
                        if not target_details:
                            target_details = {'name': 'unknown', 'virtual': True}
                    except:
                        target_details = {'name': 'unknown', 'virtual': True}
            
            # Add participant if not exists
            if target_id not in participants:
                node_type = target_id.split(':', 1)[0]
                participants[target_id] = {
                    'id': target_id,
                    'type': node_type,
                    'label': _get_sequence_label(node_type, target_details),
                    'actor_type': _get_actor_type(node_type),
                    'order': len(participants),
                    'details': target_details,
                    'virtual': target_details.get('virtual', False)
                }
            
            # Add interaction
            interaction_type = _get_interaction_type(edge_info['kind'])
            is_unresolved = edge_info['kind'] == 'call_unresolved' or target_details.get('virtual', False)
            
            interactions.append({
                'id': f"interaction_{sequence_order}",
                'sequence_order': sequence_order,
                'type': interaction_type,
                'from_participant': current_id,
                'to_participant': target_id,
                'message': _get_interaction_message(edge_info['kind'], participants[current_id], participants[target_id]),
                'confidence': edge_info['confidence'],
                'unresolved': is_unresolved
            })
            sequence_order += 1
            
            # Continue traversal for non-virtual nodes
            if target_id not in visited and not target_details.get('virtual', False):
                visited.add(target_id)
                queue.append((target_id, current_depth + 1, current_id))
    
    # Sort participants by order
    participant_list = sorted(participants.values(), key=lambda x: x['order'])
    
    return {
        'type': 'sequence',
        'participants': participant_list,
        'interactions': sorted(interactions, key=lambda x: x['sequence_order']),
        'metadata': {
            'total_participants': len(participant_list),
            'total_interactions': len(interactions),
            'max_depth_reached': max(0 if not interactions else max_depth),
            'unresolved_calls': sum(1 for i in interactions if i.get('unresolved', False))
        }
    }


def _get_sequence_label(node_type: str, details: Dict[str, Any]) -> str:
    """Generate label for sequence diagram node"""
    if node_type in ('method', 'library_method'):
        class_name = details.get('class', '').split('.')[-1] if details.get('class') else ''
        method_name = details.get('name', 'unknown')
        return f"{class_name}.{method_name}()" if class_name else f"{method_name}()"
    elif node_type == 'unresolved':
        return f"{details.get('name', 'unknown')}()"
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
        'mapper': 'boundary',
        'library_method': 'control',
        'unresolved': 'control'
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