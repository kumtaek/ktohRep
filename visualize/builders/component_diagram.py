# visualize/builders/component_diagram.py
from typing import Dict, Any, List, Optional
import re
import yaml
import logging
from pathlib import Path
from collections import defaultdict
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


# Component classification rules
COMPONENT_RULES = {
    'Controller': [
        r'.*[Cc]ontroller.*',
        r'.*/controller/.*',
        r'.*Controller\.java$'
    ],
    'Service': [
        r'.*[Ss]ervice.*',
        r'.*/service/.*',
        r'.*Service\.java$',
        r'.*ServiceImpl.*'
    ],
    'Repository': [
        r'.*[Rr]epository.*',
        r'.*[Dd]ao.*',
        r'.*/dao/.*',
        r'.*/repository/.*',
        r'.*Dao\.java$',
        r'.*Repository\.java$'
    ],
    'Mapper': [
        r'.*[Mm]apper.*',
        r'.*/mapper/.*',
        r'.*Mapper\.java$',
        r'.*Mapper\.xml$'
    ],
    'Model': [
        r'.*[Mm]odel.*',
        r'.*[Ee]ntity.*',
        r'.*[Dd]to.*',
        r'.*[Vv]o.*',
        r'.*/model/.*',
        r'.*/entity/.*',
        r'.*/dto/.*',
        r'.*/vo/.*',
        r'ResponseEntity'
    ],
    'View': [
        r'.*\.jsp$',
        r'.*\.html$',
        r'.*\.ftl$',
        r'.*/jsp/.*',
        r'.*/view/.*',
        r'.*/template/.*'
    ],
    'Config': [
        r'.*[Cc]onfig.*',
        r'.*\.properties$',
        r'.*\.yml$',
        r'.*\.yaml$',
        r'.*/config/.*'
    ],
    'Util': [
        r'.*[Uu]til.*',
        r'.*[Hh]elper.*',
        r'.*/util/.*',
        r'.*/utils/.*',
        r'.*/helper/.*'
    ]
}

DEFAULT_COMPONENT = 'Other'
LOG_MISMATCHES = True


def build_component_graph_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], min_conf: float, max_nodes: int = 2000) -> Dict[str, Any]:
    """Build component diagram JSON for visualization"""
    print(f"Building component diagram for project {project_id}")
    print(f"  Min confidence: {min_conf}")
    print(f"  Max nodes: {max_nodes}")
    
    db = VizDB(config, project_name)
    
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
    
    # Add table entities (DB component) - include key database tables
    db_tables = ['ORDERS', 'PRODUCTS', 'USERS', 'CATEGORIES', 'INVENTORIES']
    for table_name in db_tables:
        entity_id = f"table:{table_name}"
        if entity_id not in entity_to_component:
            entity_to_component[entity_id] = 'DB'
            component_entities['DB'].append({
                'id': entity_id,
                'type': 'table',
                'label': table_name
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
    
    # Process actual edges to create cross-component relationships
    print(f"Processing {len(edges)} actual edges for component relationships...")
    for edge in edges:
        src_id = f"{edge.src_type}:{edge.src_id}"
        dst_id = f"{edge.dst_type}:{edge.dst_id}" if edge.dst_id else None
        
        src_component = entity_to_component.get(src_id)
        dst_component = entity_to_component.get(dst_id) if dst_id else None
        
        
        # 메서드 호출의 경우 meta 정보를 통해 컴포넌트 관계 추론
        if edge.src_type == 'method' and edge.edge_kind == 'call':
            try:
                # meta 정보에서 대상 클래스 추출
                import json
                meta = json.loads(edge.meta) if isinstance(edge.meta, str) else edge.meta
                callee_qualifier = meta.get('callee_qualifier_type', '')
                
                if callee_qualifier:
                    # 클래스명으로 컴포넌트 추론
                    dst_component_inferred = decide_component_group('', callee_qualifier)
                    if dst_component_inferred != 'Other':
                        dst_component = dst_component_inferred
                        
            except Exception as e:
                pass
        
        # dst_id가 있는 경우의 기존 로직도 유지
        elif edge.src_type == 'method' and edge.dst_type == 'method' and dst_id:
            # 대상 메서드의 컴포넌트를 클래스명으로 추론
            try:
                dst_method_id = edge.dst_id
                # 데이터베이스에서 대상 메서드의 클래스 정보 조회
                dst_method_details = db.get_node_details('method', dst_method_id)
                if dst_method_details and dst_method_details.get('file'):
                    dst_component_inferred = decide_component_group(dst_method_details['file'], dst_method_details.get('class'))
                    if dst_component_inferred != 'Other':
                        dst_component = dst_component_inferred
                        
                # 이미 매핑된 entity_to_component에 추가
                if dst_id not in entity_to_component:
                    entity_to_component[dst_id] = dst_component
                    
            except Exception as e:
                pass
        
        # SQL unit -> table 관계도 처리
        if edge.src_type == 'sql_unit' and edge.dst_type == 'table':
            if not dst_component:
                dst_component = 'DB'
                entity_to_component[dst_id] = dst_component
        
        if src_component and dst_component and src_component != dst_component:
            edge_key = (src_component, dst_component)
            component_edges[edge_key]['count'] += 1
            component_edges[edge_key]['confidence_sum'] += edge.confidence
            component_edges[edge_key]['kinds'].add(edge.edge_kind)
    
    # 참조되는 컴포넌트 중 실제 노드가 없는 경우 가상 노드 생성
    referenced_components = set()
    for edge_key in component_edges.keys():
        referenced_components.add(edge_key[0])  # source
        referenced_components.add(edge_key[1])  # target
    
    existing_components = set(component_entities.keys())
    missing_components = referenced_components - existing_components
    
    for missing_comp in missing_components:
        print(f"  가상 컴포넌트 노드 생성: {missing_comp}")
        component_nodes.append(create_node(
            f"component:{missing_comp}", 'component', f"{missing_comp} (Virtual)", missing_comp, 
            {'entity_count': 0, 'entities': [], 'total_entities': 0, 'virtual': True}
        ))

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