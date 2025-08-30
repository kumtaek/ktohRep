# visualize/builders/erd.py
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


def build_erd_json(project_id: int, tables: str = None, owners: str = None, 
                   from_sql: str = None) -> Dict[str, Any]:
    """Build ERD JSON for visualization"""
    
    db = VizDB()
    
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
    
    # Build table nodes
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
        
        # Get column details for this table
        table_columns = []
        for col in columns_info:
            if col.table_id == table.table_id:
                table_columns.append({
                    'name': col.column_name,
                    'data_type': col.data_type,
                    'nullable': col.nullable,
                    'is_pk': col.column_name in pk_columns,
                    'comment': getattr(col, 'column_comment', None)
                })
        
        # Get sample joins for this table
        sample_joins = db.fetch_sample_joins_for_table(table.table_id, limit=5)
        
        table_meta = {
            'owner': table.owner,
            'table_name': table.table_name,
            'status': getattr(table, 'status', 'VALID'),
            'pk_columns': pk_columns,
            'comment': getattr(table, 'table_comment', None),
            'columns': table_columns,
            'sample_joins': sample_joins
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

    # Build FK relationships from join patterns
    edges_list = []
    
    if joins:
        # Count join frequency to infer FK relationships
        join_patterns = Counter()
        for join in joins:
            if join.l_table and join.r_table and join.l_col and join.r_col:
                pattern = (join.l_table.upper(), join.l_col.upper(), 
                          join.r_table.upper(), join.r_col.upper())
                join_patterns[pattern] += 1
        
        # Create FK edges for frequently used joins
        for (l_table, l_col, r_table, r_col), frequency in join_patterns.items():
            if frequency >= 2:  # Threshold for FK inference
                # Use the helper function to resolve abbreviated table names to node_ids
                l_node_id = resolve_abbreviation_to_node_id(l_table, nodes_dict)
                r_node_id = resolve_abbreviation_to_node_id(r_table, nodes_dict)

                if not l_node_id:
                    continue
                if not r_node_id:
                    continue
                
                # Check if both tables are in our node set
                if l_node_id in nodes_dict and r_node_id in nodes_dict:
                    # Determine FK direction based on PK information
                    l_table_meta = nodes_dict[l_node_id]['meta']
                    r_table_meta = nodes_dict[r_node_id]['meta']
                    
                    l_is_pk = l_col in l_table_meta.get('pk_columns', [])
                    r_is_pk = r_col in r_table_meta.get('pk_columns', [])
                    
                    # Infer relationship direction
                    if l_is_pk and not r_is_pk:
                        # L is PK, R is FK - L is referenced by R
                        source, target = r_node_id, l_node_id
                        relation_type = "fk_inferred"
                        confidence = min(0.9, 0.6 + (frequency * 0.1))
                    elif r_is_pk and not l_is_pk:
                        # R is PK, L is FK - R is referenced by L
                        source, target = l_node_id, r_node_id
                        relation_type = "fk_inferred"
                        confidence = min(0.9, 0.6 + (frequency * 0.1))
                    else:
                        # Both or neither are PK - generic join relationship
                        source, target = l_node_id, r_node_id
                        relation_type = "join_inferred"
                        confidence = min(0.7, 0.4 + (frequency * 0.1))
                    
                    edge_id = f"fk:{l_table}.{l_col}-{r_table}.{r_col}"
                    edge_meta = {
                        'left_table': l_table,
                        'left_column': l_col,
                        'right_table': r_table,
                        'right_column': r_col,
                        'frequency': frequency
                    }
                    
                    edges_list.append(create_edge(edge_id, source, target, relation_type, 
                                                confidence, edge_meta))
    
    # Convert nodes_dict values to list
    nodes_list = list(nodes_dict.values())
    
    # Create graph using schema
    return create_graph(nodes_list, edges_list)
