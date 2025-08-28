# visualize/builders/component_diagram.py
from typing import Dict, Any, List
import re
import yaml
import logging
from pathlib import Path
from collections import defaultdict
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


def load_component_config() -> Dict[str, Any]:
    """Load component classification configuration"""
    config_path = Path(__file__).parent.parent / "config" / "visualization_config.yaml"
    
    # Default configuration (fallback)
    default_config = {
        'component_classification': {
            'rules': {
                'Controller': [r'.*\.controller\..*', r'.*Controller\.java$'],
                'Service': [r'.*\.service\..*', r'.*Service\.java$'],
                'Repository': [r'.*\.repository\..*', r'.*Repository\.java$'],
                'Mapper': [r'.*Mapper\.xml$', r'.*\.mapper\..*'],
                'JSP': [r'.*/WEB-INF/jsp/.*\.jsp$', r'.*\.jsp$'],
                'Entity': [r'.*\.entity\..*', r'.*\.model\..*', r'.*\.domain\..*'],
                'Util': [r'.*\.util\..*', r'.*Utils?\.java$'],
                'Config': [r'.*\.config\..*', r'.*Config\.java$'],
                'DB': [r'^TABLE:.*']
            },
            'default_component': 'Other',
            'log_mismatches': True
        }
    }
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        else:
            print(f"Config file not found: {config_path}, using defaults")
    except Exception as e:
        print(f"Error loading config: {e}, using defaults")
    
    return default_config


# Load configuration at module level
CONFIG = load_component_config()
COMPONENT_RULES = CONFIG['component_classification']['rules']
DEFAULT_COMPONENT = CONFIG['component_classification'].get('default_component', 'Other')
LOG_MISMATCHES = CONFIG['component_classification'].get('log_mismatches', True)


def build_component_graph_json(project_id: int, min_conf: float, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build component diagram JSON for visualization"""
    print(f"Building component diagram for project {project_id}")
    print(f"  Min confidence: {min_conf}")
    print(f"  Max nodes: {max_nodes}")
    
    db = VizDB()
    
    # Get all edges for the project
    edges = db.fetch_edges(project_id, None, min_conf)
    
    # Get all files, methods, classes for component classification
    files = db.load_project_files(project_id)
    methods = db.fetch_methods_by_project(project_id)
    sql_units = db.fetch_sql_units_by_project(project_id)
    
    print(f"  Found {len(edges)} edges, {len(files)} files")
    
    # Build component mapping
    entity_to_component = {}
    component_entities = defaultdict(list)
    
    # Classify files
    for file in files:
        component = decide_component_group(file.path, None)
        entity_id = f"file:{file.file_id}"
        entity_to_component[entity_id] = component
        component_entities[component].append({
            'id': entity_id,
            'type': 'file',
            'label': file.path.split('/')[-1] if '/' in file.path else file.path.split('\\')[-1],
            'path': file.path
        })
    
    # Classify methods (through their classes/files)
    for method in methods:
        # Get method's class and file info
        method_details = db.get_node_details('method', method.method_id)
        if method_details and method_details.get('file'):
            component = decide_component_group(method_details['file'], method_details.get('class'))
        else:
            component = 'Code'
        
        entity_id = f"method:{method.method_id}"
        entity_to_component[entity_id] = component
        component_entities[component].append({
            'id': entity_id,
            'type': 'method',
            'label': f"{method.name}()",
            'class': method_details.get('class') if method_details else None
        })
    
    # Classify SQL units
    for sql_unit in sql_units:
        sql_details = db.get_node_details('sql_unit', sql_unit.sql_id)
        if sql_details and sql_details.get('file'):
            component = decide_component_group(sql_details['file'], None)
        else:
            component = 'Mapper'
        
        entity_id = f"sql_unit:{sql_unit.sql_id}"
        entity_to_component[entity_id] = component
        component_entities[component].append({
            'id': entity_id,
            'type': 'sql_unit',
            'label': f"{sql_unit.mapper_ns}.{sql_unit.stmt_id}" if sql_unit.stmt_id else sql_unit.mapper_ns
        })
    
    # Add table entities (DB component)
    for edge in edges:
        if edge.dst_type == 'table':
            entity_id = f"table:{edge.dst_id}"
            if entity_id not in entity_to_component:
                entity_to_component[entity_id] = 'DB'
                component_entities['DB'].append({
                    'id': entity_id,
                    'type': 'table',
                    'label': f"Table {edge.dst_id}"
                })
    
    # Create component nodes
    component_nodes = []
    for component, entities in component_entities.items():
        if entities:  # Only create nodes for components that have entities
            node_id = f"component:{component}"
            entity_count = len(entities)
            
            # Create metadata with entity details
            meta = {
                'entity_count': entity_count,
                'entities': entities[:10],  # Limit to first 10 for display
                'total_entities': entity_count
            }
            
            component_nodes.append(create_node(
                node_id, 'component', f"{component} ({entity_count})", component, meta
            ))
    
    # Aggregate edges between components
    component_edges = defaultdict(lambda: {'count': 0, 'confidence_sum': 0.0, 'kinds': set()})
    
    for edge in edges:
        src_id = f"{edge.src_type}:{edge.src_id}"
        dst_id = f"{edge.dst_type}:{edge.dst_id}" if edge.dst_id else f"unknown:{edge.edge_kind}"
        
        src_component = entity_to_component.get(src_id)
        dst_component = entity_to_component.get(dst_id)
        
        if src_component and dst_component and src_component != dst_component:
            edge_key = (src_component, dst_component)
            component_edges[edge_key]['count'] += 1
            component_edges[edge_key]['confidence_sum'] += edge.confidence
            component_edges[edge_key]['kinds'].add(edge.edge_kind)
    
    # Create component edges
    edges_list = []
    for (src_comp, dst_comp), edge_data in component_edges.items():
        src_node_id = f"component:{src_comp}"
        dst_node_id = f"component:{dst_comp}"
        
        avg_confidence = edge_data['confidence_sum'] / edge_data['count']
        edge_kinds = list(edge_data['kinds'])
        
        edge_id = f"comp_edge:{src_comp}-{dst_comp}"
        edge_meta = {
            'count': edge_data['count'],
            'kinds': edge_kinds,
            'avg_confidence': avg_confidence
        }
        
        # Determine primary edge kind for display
        primary_kind = edge_kinds[0] if len(edge_kinds) == 1 else 'mixed'
        
        edges_list.append(create_edge(
            edge_id, src_node_id, dst_node_id, primary_kind, avg_confidence, edge_meta
        ))
    
    print(f"  Generated {len(component_nodes)} components, {len(edges_list)} relationships")
    
    return create_graph(component_nodes, edges_list)


def decide_component_group(file_path: str, fqn: str = None) -> str:
    """Decide which component group an entity belongs to"""
    matched_component = None
    matched_pattern = None
    
    # Check FQN first if available
    if fqn:
        for component, patterns in COMPONENT_RULES.items():
            for pattern in patterns:
                if re.search(pattern, fqn, re.IGNORECASE):
                    matched_component = component
                    matched_pattern = f"FQN:{pattern}"
                    break
            if matched_component:
                break
    
    # Check file path if no FQN match
    if not matched_component and file_path:
        for component, patterns in COMPONENT_RULES.items():
            for pattern in patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    matched_component = component
                    matched_pattern = f"PATH:{pattern}"
                    break
            if matched_component:
                break
    
    # Use default if no match
    if not matched_component:
        matched_component = DEFAULT_COMPONENT
        if LOG_MISMATCHES:
            print(f"COMPONENT_MISMATCH: No match for file='{file_path}', fqn='{fqn}' -> using '{DEFAULT_COMPONENT}'")
    elif LOG_MISMATCHES:
        print(f"COMPONENT_MATCH: file='{file_path}', fqn='{fqn}' -> '{matched_component}' (via {matched_pattern})")
    
    return matched_component