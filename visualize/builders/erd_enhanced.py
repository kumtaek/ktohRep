# visualize/builders/erd_enhanced.py
from typing import Dict, Any, List, Optional
from collections import Counter
from ..data_access import VizDB  
from ..schema import create_node, create_edge, create_graph

# Helper function to resolve abbreviated table names to node_ids
def resolve_abbreviation_to_node_id(abbreviated_name: str, nodes_dict: Dict[str, Any]) -> Optional[str]:
    owner_abbr, table_abbr = abbreviated_name.split('.') if '.' in abbreviated_name else ('', abbreviated_name)

    potential_matches = []
    exact_matches = []

    for node_id, node_data in nodes_dict.items():
        if node_data is None:
            continue
        if not isinstance(node_data, dict) or 'meta' not in node_data or not isinstance(node_data['meta'], dict):
            continue

        full_owner = node_data['meta'].get('owner', '').upper()
        full_table = node_data['meta'].get('table_name', '').upper()
        
        # Create common abbreviations for the table name
        table_abbrev_candidates = []
        if full_table:
            # Single letter abbreviation (first letter)
            table_abbrev_candidates.append(full_table[0])
            # Two letter abbreviation for compound words
            if '_' in full_table:
                parts = full_table.split('_')
                if len(parts) >= 2:
                    table_abbrev_candidates.append(parts[0][0] + parts[1][0])
            # Full abbreviations like ORDER_ITEMS -> OI
            if full_table == 'ORDER_ITEMS':
                table_abbrev_candidates.extend(['OI', 'ORDER_ITEMS'])
            elif full_table == 'ORDERS':
                table_abbrev_candidates.extend(['O', 'ORDER'])
            elif full_table == 'USERS':
                table_abbrev_candidates.extend(['U', 'USER'])  
            elif full_table == 'USER_ROLE':
                table_abbrev_candidates.extend(['UR', 'USER_ROLE'])
            elif full_table == 'CUSTOMERS':
                table_abbrev_candidates.extend(['C', 'CUSTOMER'])
            elif full_table == 'CATEGORIES':
                table_abbrev_candidates.extend(['CAT', 'CATEGORY'])
            
        match_found = False
        is_exact_match = False
        
        # Check if the abbreviation matches any of our candidates
        table_abbr_upper = table_abbr.upper()
        if table_abbr_upper in table_abbrev_candidates:
            # Check owner matching
            if owner_abbr.upper() == "PUBLIC":
                # PUBLIC is a wildcard, matches any owner
                match_found = True
                # Prefer exact length matches for disambiguation
                if table_abbr_upper == full_table or len(table_abbr_upper) > 1:
                    is_exact_match = True
            else:
                if full_owner == owner_abbr.upper():
                    match_found = True
                    is_exact_match = True
        
        if match_found:
            if is_exact_match:
                exact_matches.append(node_id)
            else:
                potential_matches.append(node_id)

    # Prefer exact matches over potential matches
    if len(exact_matches) == 1:
        return exact_matches[0]
    elif len(exact_matches) > 1:
        return exact_matches[0]  # Choose the first exact match
    elif len(potential_matches) == 1:
        return potential_matches[0]
    elif len(potential_matches) > 1:
        return potential_matches[0]  # Choose the first potential match
    else:
        return None


def get_column_comments(db: VizDB, table_id: int) -> Dict[str, str]:
    """테이블의 컬럼 코멘트 정보를 가져옴"""
    try:
        # 스키마 코멘트 CSV 데이터가 있다면 활용
        column_comments = {}
        
        # DB에서 직접 코멘트 정보 조회 (Oracle, MySQL 등에서 지원)
        query = """
        SELECT column_name, comments 
        FROM all_col_comments 
        WHERE table_name = (SELECT table_name FROM db_table WHERE table_id = ?)
        AND owner = (SELECT owner FROM db_table WHERE table_id = ?)
        """
        
        # 실제 구현에서는 DB 종류에 따라 다른 쿼리 사용
        # 여기서는 기본적인 구조만 제공
        return column_comments
        
    except Exception:
        return {}


def build_enhanced_erd_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], 
                           tables: str = None, owners: str = None, from_sql: str = None) -> Dict[str, Any]:
    """Build Enhanced ERD JSON with detailed column information and tooltips"""
    
    db = VizDB(config, project_name)
    
    # Get database schema information
    db_tables = db.fetch_tables()
    pk_info = db.fetch_pk()
    columns_info = db.fetch_columns()
    joins = db.fetch_joins_for_project(project_id)
    
    # Special handling for --from-sql (SQLERD mode)
    sqlerd_mode = bool(from_sql)
    
    # Parse filters
    wanted_tables = set()
    if tables:
        wanted_tables = {t.strip().upper() for t in tables.split(',')}
    
    wanted_owners = set()
    if owners:
        wanted_owners = {o.strip().upper() for o in owners.split(',')}
    
    # Build table nodes with enhanced information
    nodes_dict = {}
    
    # Add database tables
    for table in db_tables:
        table_key = f"{table.owner}.{table.table_name}" if table.owner else table.table_name
        table_key_upper = table_key.upper()
        
        # Apply filters
        if wanted_tables and table.table_name.upper() not in wanted_tables:
            continue
        if wanted_owners and (table.owner or '').upper() not in wanted_owners:
            continue
        
        # Get primary key info for this table
        pk_columns = []
        for pk in pk_info:
            if pk.table_id == table.table_id:
                pk_columns.append(pk.column_name)
        
        # Get enhanced column details for this table
        table_columns = []
        column_comments = get_column_comments(db, table.table_id)
        
        for col in columns_info:
            if col.table_id == table.table_id:
                # 외래키 여부 판단 로직 개선
                is_fk = False
                fk_references = None
                
                # 조인 정보에서 외래키 추론
                for join in joins:
                    if (join.l_table and join.l_table.upper() == table.table_name.upper() and
                        join.l_col and join.l_col.upper() == col.column_name.upper()):
                        is_fk = True
                        fk_references = f"{join.r_table}.{join.r_col}"
                        break
                    elif (join.r_table and join.r_table.upper() == table.table_name.upper() and
                          join.r_col and join.r_col.upper() == col.column_name.upper()):
                        is_fk = True
                        fk_references = f"{join.l_table}.{join.l_col}"
                        break
                
                column_detail = {
                    'name': col.column_name,
                    'data_type': col.data_type,
                    'nullable': col.nullable,
                    'is_pk': col.column_name in pk_columns,
                    'is_foreign_key': is_fk,
                    'fk_references': fk_references,
                    'comment': column_comments.get(col.column_name, getattr(col, 'column_comment', None)),
                    'max_length': getattr(col, 'char_length', None),
                    'precision': getattr(col, 'data_precision', None),
                    'scale': getattr(col, 'data_scale', None)
                }
                
                table_columns.append(column_detail)
        
        # Get sample joins for this table (확장된 정보)
        sample_joins = []
        try:
            join_query_results = db.fetch_sample_joins_for_table(table.table_id, limit=10)
            for join_result in join_query_results:
                sample_joins.append({
                    'l_table': join_result.get('l_table', ''),
                    'l_col': join_result.get('l_col', ''),
                    'r_table': join_result.get('r_table', ''),
                    'r_col': join_result.get('r_col', ''),
                    'frequency': join_result.get('frequency', 1),
                    'confidence': join_result.get('confidence', 0.8)
                })
        except Exception:
            # fetch_sample_joins_for_table 메서드가 없는 경우 대체 로직
            for join in joins:
                if ((join.l_table and join.l_table.upper() == table.table_name.upper()) or
                    (join.r_table and join.r_table.upper() == table.table_name.upper())):
                    sample_joins.append({
                        'l_table': join.l_table or '',
                        'l_col': join.l_col or '',
                        'r_table': join.r_table or '',
                        'r_col': join.r_col or '',
                        'frequency': 1,
                        'confidence': 0.8
                    })
                    if len(sample_joins) >= 10:
                        break
        
        # 테이블 메타 정보 확장
        table_meta = {
            'owner': table.owner,
            'table_name': table.table_name,
            'status': getattr(table, 'status', 'VALID'),
            'pk_columns': pk_columns,
            'comment': getattr(table, 'table_comment', None),
            'columns': table_columns,
            'sample_joins': sample_joins,
            'column_count': len(table_columns),
            'pk_count': len(pk_columns),
            'fk_count': len([col for col in table_columns if col['is_foreign_key']]),
            'has_comments': any(col['comment'] for col in table_columns),
            # 테이블 크기 정보 (가능한 경우)
            'estimated_size': 'unknown'
        }
        
        node_id = f"table:{table_key}"
        nodes_dict[node_id] = create_node(node_id, 'table', table_key, 'DB', table_meta)
    
    # Create a mapping from full table name (OWNER.TABLE_NAME) to node_id
    full_name_to_node_id_map = {}
    for node_id, node_data in nodes_dict.items():
        owner = node_data['meta'].get('owner', '').upper()
        table_name = node_data['meta'].get('table_name', '').upper()
        full_table_name = f"{owner}.{table_name}" if owner else table_name
        full_name_to_node_id_map[full_table_name] = node_id

    # Build FK relationships from join patterns or infer from column names
    edges_list = []
    
    if joins:
        # Count join frequency to infer FK relationships
        join_patterns = Counter()
        for join in joins:
            if join.l_table and join.r_table and join.l_col and join.r_col:
                pattern = (join.l_table.upper(), join.l_col.upper(), 
                          join.r_table.upper(), join.r_col.upper())
                join_patterns[pattern] += 1
        
        # Create FK edges for frequently used joins with enhanced metadata
        for (l_table, l_col, r_table, r_col), frequency in join_patterns.items():
            if frequency >= 2:  # Threshold for FK inference
                # Use the helper function to resolve abbreviated table names to node_ids
                l_node_id = resolve_abbreviation_to_node_id(l_table, nodes_dict)
                r_node_id = resolve_abbreviation_to_node_id(r_table, nodes_dict)

                if not l_node_id or not r_node_id:
                    continue
                
                # Check if both tables are in our node set
                if l_node_id in nodes_dict and r_node_id in nodes_dict:
                    # 신뢰도 계산 개선
                    confidence = min(0.9, 0.6 + (frequency * 0.1))
                    
                    # 조인 조건 상세 정보 생성
                    join_condition = f"{l_table}.{l_col} = {r_table}.{r_col}"
                    
                    edge_meta = {
                        "left_column": l_col, 
                        "right_column": r_col, 
                        "frequency": frequency,
                        "relationship_type": "inferred_fk",
                        "cardinality": "many_to_one",  # 대부분의 FK는 N:1
                        "constraint_name": f"FK_{l_table}_{l_col}",
                        "join_condition": join_condition,
                        "source_table": l_table,
                        "target_table": r_table,
                        "join_type": "INNER JOIN",
                        "description": f"{l_table} 테이블의 {l_col} 컬럼이 {r_table} 테이블의 {r_col} 컬럼을 참조"
                    }
                    
                    edges_list.append(create_edge(
                        f"fk_{len(edges_list)+1}",
                        l_node_id,
                        r_node_id,
                        "foreign_key",
                        confidence,
                        edge_meta
                    ))
    else:
        # No joins data - infer FK relationships from column name patterns
        edge_id = 1
        for node1_id, node1 in nodes_dict.items():
            table1_name = node1['meta']['table_name']
            table1_columns = [col['name'] for col in node1['meta']['columns']]
            
            for node2_id, node2 in nodes_dict.items():
                if node1_id == node2_id:
                    continue
                    
                table2_name = node2['meta']['table_name'] 
                table2_pk = node2['meta']['pk_columns']
                
                # Look for FK patterns: table2_name + _ID in table1 columns
                for col_name in table1_columns:
                    col_upper = col_name.upper()
                    table2_upper = table2_name.upper()
                    
                    # Pattern 1: TABLE_ID (e.g., USER_ID, ORDER_ID)
                    if col_upper == f"{table2_upper}_ID" and f"{table2_upper}_ID" in [pk.upper() for pk in table2_pk]:
                        # 조인 조건 상세 정보 생성
                        join_condition = f"{table1_name}.{col_name} = {table2_name}.{table2_upper}_ID"
                        
                        edges_list.append(create_edge(
                            f"fk_{edge_id}",
                            node1_id,
                            node2_id,
                            "foreign_key",
                            0.7,
                            {
                                "left_column": col_name, 
                                "right_column": f"{table2_upper}_ID",
                                "column": col_name, 
                                "references": f"{table2_name}.{table2_upper}_ID", 
                                "inferred": True,
                                "pattern": "table_id_convention",
                                "join_condition": join_condition,
                                "source_table": table1_name,
                                "target_table": table2_name,
                                "join_type": "INNER JOIN",
                                "relationship_type": "one_to_many",
                                "cardinality": "1:N",
                                "description": f"{table1_name} 테이블의 {col_name} 컬럼이 {table2_name} 테이블의 기본키를 참조"
                            }
                        ))
                        edge_id += 1
                    
                    # Pattern 2: Exact PK match (e.g., ID -> ID)
                    elif col_upper in [pk.upper() for pk in table2_pk] and table1_name != table2_name:
                        # 조인 조건 상세 정보 생성
                        join_condition = f"{table1_name}.{col_name} = {table2_name}.{col_name}"
                        
                        edges_list.append(create_edge(
                            f"fk_{edge_id}",
                            node1_id,
                            node2_id,
                            "foreign_key",
                            0.6,
                            {
                                "left_column": col_name, 
                                "right_column": col_name,
                                "column": col_name, 
                                "references": f"{table2_name}.{col_name}", 
                                "inferred": True,
                                "pattern": "pk_match",
                                "join_condition": join_condition,
                                "source_table": table1_name,
                                "target_table": table2_name,
                                "join_type": "INNER JOIN",
                                "relationship_type": "many_to_one",
                                "cardinality": "N:1",
                                "description": f"{table1_name} 테이블이 {table2_name} 테이블의 {col_name} 컬럼을 참조"
                            }
                        ))
                        edge_id += 1
    
    # Convert nodes_dict values to list
    nodes_list = list(nodes_dict.values())
    
    # Add enhanced metadata to the graph
    graph_metadata = {
        'total_tables': len(nodes_list),
        'total_relationships': len(edges_list),
        'tables_with_comments': len([n for n in nodes_list if n['meta'].get('has_comments', False)]),
        'total_columns': sum(n['meta'].get('column_count', 0) for n in nodes_list),
        'filters_applied': {
            'tables': tables,
            'owners': owners,
            'from_sql': from_sql
        },
        'generation_time': str(pd.Timestamp.now()) if 'pd' in locals() else 'unknown'
    }
    
    # Create graph using schema
    graph = create_graph(nodes_list, edges_list)
    graph['metadata'] = graph_metadata
    
    return graph