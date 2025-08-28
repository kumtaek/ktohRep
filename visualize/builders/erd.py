# visualize/builders/erd.py
from typing import Dict, Any, List, Optional
from collections import Counter
from ..data_access import VizDB  
from ..schema import create_node, create_edge, create_graph


def build_erd_json(project_id: int, tables: str = None, owners: str = None, 
                   from_sql: str = None) -> Dict[str, Any]:
    """Build ERD JSON for visualization"""
    print(f"Building ERD for project {project_id}")
    print(f"  Tables filter: {tables}")
    print(f"  Owners filter: {owners}")
    print(f"  From SQL: {from_sql}")
    
    db = VizDB()
    
    # Get database schema information
    db_tables = db.fetch_tables()
    pk_info = db.fetch_pk()
    joins = db.fetch_joins_for_project(project_id)
    
    print(f"  Found {len(db_tables)} tables, {len(joins)} joins")
    
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
        
        table_meta = {
            'owner': table.owner,
            'table_name': table.table_name,
            'status': getattr(table, 'status', 'VALID'),
            'pk_columns': pk_columns
        }
        
        node_id = f"table:{table_key}"
        nodes_dict[node_id] = create_node(node_id, 'table', table_key, 'DB', table_meta)
    
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
        
        print(f"  Found {len(join_patterns)} unique join patterns")
        
        # Create FK edges for frequently used joins
        for (l_table, l_col, r_table, r_col), frequency in join_patterns.items():
            if frequency >= 2:  # Threshold for FK inference
                l_node_id = f"table:{l_table}"
                r_node_id = f"table:{r_table}"
                
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
    
    # Handle from_sql parameter
    if from_sql:
        # Parse format: mapper_ns:stmt_id
        try:
            mapper_ns, stmt_id = from_sql.split(':')
            sql_units = db.fetch_sql_units_by_project(project_id)
            
            # Find the specific SQL unit
            target_sql = None
            for sql in sql_units:
                if sql.mapper_ns == mapper_ns and sql.stmt_id == stmt_id:
                    target_sql = sql
                    break
            
            if target_sql:
                # Get joins specific to this SQL
                sql_joins = [j for j in joins if j.sql_id == target_sql.sql_id]
                
                # Add tables mentioned in this SQL
                mentioned_tables = set()
                for join in sql_joins:
                    mentioned_tables.add(join.l_table.upper())
                    mentioned_tables.add(join.r_table.upper())
                
                # Filter nodes to only include mentioned tables
                filtered_nodes = {}
                for node_id, node in nodes_dict.items():
                    table_name = node['meta'].get('table_name', '').upper()
                    owner = node['meta'].get('owner', '').upper()
                    full_name = f"{owner}.{table_name}" if owner else table_name
                    
                    if table_name in mentioned_tables or full_name in mentioned_tables:
                        filtered_nodes[node_id] = node
                
                nodes_dict = filtered_nodes
                print(f"  Filtered to {len(nodes_dict)} tables from SQL: {from_sql}")
        except ValueError:
            print(f"  Warning: Invalid from_sql format: {from_sql}")
    
    nodes_list = list(nodes_dict.values())
    
    print(f"  Generated {len(nodes_list)} table nodes, {len(edges_list)} relationships")
    
    return create_graph(nodes_list, edges_list)