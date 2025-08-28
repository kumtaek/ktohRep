# visualize/builders/erd.py
from typing import Dict, Any, List, Optional
from collections import Counter
from ..data_access import VizDB  
from ..schema import create_node, create_edge, create_graph


def build_erd_json(project_id: int, tables: str = None, owners: str = None, 
                   from_sql: str = None) -> Dict[str, Any]:
    """Build ERD JSON for visualization"""
    print(f"ERD 생성: 프로젝트 {project_id}")
    print(f"  테이블 필터: {tables}")
    print(f"  오너 필터: {owners}")
    print(f"  SQL 기준: {from_sql}")
    
    db = VizDB()
    
    # Get database schema information
    db_tables = db.fetch_tables()
    pk_info = db.fetch_pk()
    columns_info = db.fetch_columns()
    joins = db.fetch_joins_for_project(project_id)
    
    print(f"  테이블 {len(db_tables)}개, 조인 {len(joins)}개 발견")
    
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
        
        print(f"  고유 조인 패턴 {len(join_patterns)}개")
        
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
                
                # Get required filters for this SQL (SQLERD enhancement)
                required_filters = db.fetch_required_filters(project_id, target_sql.sql_id)
                
                # Add tables mentioned in this SQL (joins + filters)
                mentioned_tables = set()
                for join in sql_joins:
                    if join.l_table:
                        mentioned_tables.add(join.l_table.upper())
                    if join.r_table:
                        mentioned_tables.add(join.r_table.upper())
                
                for filter_item in required_filters:
                    if filter_item.table_name:
                        mentioned_tables.add(filter_item.table_name.upper())
                
                # Group required filters by table for highlighting
                filters_by_table = {}
                for filter_item in required_filters:
                    table_key = filter_item.table_name.upper() if filter_item.table_name else 'UNKNOWN'
                    if table_key not in filters_by_table:
                        filters_by_table[table_key] = []
                    
                    filters_by_table[table_key].append({
                        'column': filter_item.column_name.upper() if filter_item.column_name else '',
                        'op': filter_item.op or '',
                        'value': filter_item.value_repr or '',
                        'always': bool(filter_item.always_applied)
                    })
                
                # Filter nodes to only include mentioned tables
                filtered_nodes = {}
                for node_id, node in nodes_dict.items():
                    table_name = node['meta'].get('table_name', '').upper()
                    owner = node['meta'].get('owner', '').upper()
                    full_name = f"{owner}.{table_name}" if owner else table_name
                    
                    if table_name in mentioned_tables or full_name in mentioned_tables:
                        # Add required filters to table metadata
                        node['meta']['required_filters'] = filters_by_table.get(table_name, [])
                        node['meta']['sql_context'] = f"{target_sql.mapper_ns}:{target_sql.stmt_id}"
                        
                        # Mark filtered columns in existing column data
                        if 'columns' in node['meta']:
                            for col in node['meta']['columns']:
                                col['is_filtered'] = any(
                                    f['column'] == col['name'].upper() 
                                    for f in filters_by_table.get(table_name, [])
                                )
                        
                        filtered_nodes[node_id] = node
                
                nodes_dict = filtered_nodes
                print(f"  SQLERD: 테이블 {len(nodes_dict)}개, 필수 필터 {len(required_filters)}개 (SQL: {from_sql})")
        except ValueError:
            print(f"  경고: 잘못된 from_sql 형식: {from_sql}")
    
    nodes_list = list(nodes_dict.values())
    
    print(f"  생성된 테이블 노드 {len(nodes_list)}개, 관계 {len(edges_list)}개")
    
    return create_graph(nodes_list, edges_list)
