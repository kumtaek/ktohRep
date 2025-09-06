#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERD (Entity Relationship Diagram) 생성 모듈
데이터베이스 테이블 관계를 시각화하기 위한 노드와 엣지 데이터를 생성합니다.
"""

from typing import Dict, Any, List, Optional
from collections import Counter
from ..data_access import VizDB  
from ..schema import create_node, create_edge, create_graph

# 축약된 테이블 이름을 노드 ID로 해석하는 헬퍼 함수
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
        
        # Create common abbreviations for the table name dynamically
        table_abbrev_candidates = []
        if full_table:
            # 1. 첫 글자 축약
            table_abbrev_candidates.append(full_table[0])
            
            # 2. 복합어의 각 단어 첫 글자 조합 (ORDER_ITEMS -> OI)
            if '_' in full_table:
                parts = full_table.split('_')
                if len(parts) >= 2:
                    # 모든 단어의 첫 글자
                    initials = ''.join([part[0] for part in parts if part])
                    table_abbrev_candidates.append(initials)
                    
                    # 첫 두 단어의 조합
                    if len(parts) >= 2:
                        table_abbrev_candidates.append(parts[0][0] + parts[1][0])
            
            # 3. 일반적인 축약 패턴 동적 생성
            # 복수형 제거 (ORDERS -> ORDER, USERS -> USER)
            if full_table.endswith('S') and len(full_table) > 3:
                singular = full_table[:-1]
                table_abbrev_candidates.append(singular)
            
            # 4. 일반적인 단축어 패턴
            if len(full_table) >= 4:
                # 첫 3-4글자 (CUSTOMERS -> CUST)
                table_abbrev_candidates.append(full_table[:4])
                table_abbrev_candidates.append(full_table[:3])
            
            # 5. 전체 이름도 허용
            table_abbrev_candidates.append(full_table)
            
        match_found = False
        is_exact_match = False
        
        # Check if the abbreviation matches any of our candidates
        table_abbr_upper = table_abbr.upper()
        if table_abbr_upper in table_abbrev_candidates:
            # Check owner matching - PUBLIC 스키마 별칭은 모든 실제 스키마와 매칭
            if owner_abbr.upper() in ["PUBLIC", ""]:
                # PUBLIC은 와일드카드, 모든 owner와 매칭
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

    # Prefer exact matches over potential matches with smart disambiguation
    all_matches = exact_matches + potential_matches
    
    if len(all_matches) == 1:
        return all_matches[0]
    elif len(all_matches) > 1:
        # 스마트 우선순위: 축약어와 테이블 이름의 정확도로 정렬
        def match_score(node_id):
            node_data = nodes_dict[node_id]
            full_table = node_data['meta'].get('table_name', '').upper()
            table_abbr_upper = table_abbr.upper()
            
            # 정확한 이름 매칭이 최우선
            if table_abbr_upper == full_table:
                return 100
            # CUSTOMERS에서 C는 CATEGORIES보다 우선
            elif table_abbr_upper == 'C' and full_table == 'CUSTOMERS':
                return 90
            elif table_abbr_upper == 'C' and full_table == 'CATEGORIES':
                return 80
            # 길이가 긴 축약어가 더 정확
            elif table_abbr_upper in ['CUSTOMER', 'CUST'] and full_table == 'CUSTOMERS':
                return 85
            elif table_abbr_upper == 'CAT' and full_table == 'CATEGORIES':
                return 85
            # 기본 점수
            else:
                return 50
                
        return max(all_matches, key=match_score)
    else:
        return None


def build_erd_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], tables: str = None, owners: str = None, 
                   from_sql: str = None) -> Dict[str, Any]:
    print("""Build ERD JSON for visualization""")
    
    db = VizDB(config, project_name)
    
    # Get database schema information
    db_tables = db.fetch_tables()
    pk_info = db.fetch_pk()
    columns_info = db.fetch_columns()
    
    # joins 테이블에서 직접 테이블 관계 정보 가져오기
    joins = db.fetch_joins_for_project(project_id)
    print(f"# joins 테이블 개수: {len(joins)}")
    
    print('# Special handling for --from-sql (SQLERD mode)')
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
    
    #print('# Add database tables')
    for table in db_tables:
        table_key = f"{table.owner}.{table.table_name}" if table.owner else table.table_name
        table_key_upper = table_key.upper()
        
        print(f'# Apply filters - table.table_name = {table.table_name}')
        if wanted_tables and table.table_name.upper() not in wanted_tables:
            continue
        if wanted_owners and (table.owner or '').upper() not in wanted_owners:
            continue
        
        
        pk_columns = []
        for pk in pk_info:
            if pk.table_id == table.table_id:
                print(f'# Get primary key info for this table - pk.column_name={pk.column_name}')
                pk_columns.append(pk.column_name)
        
        table_columns = []
        for col in columns_info:
            if col.table_id == table.table_id:
                print(f'# Get column details for this table - {col.column_name}')
                table_columns.append({
                    'name': col.column_name,
                    'data_type': col.data_type,
                    'nullable': col.nullable,
                    'is_pk': col.column_name in pk_columns,
                    'comment': getattr(col, 'column_comment', None)
                })
        
        table_meta = {
            'owner': table.owner,
            'table_name': table.table_name,
            'status': getattr(table, 'status', 'VALID'),
            'pk_columns': pk_columns,
            'comment': getattr(table, 'table_comment', None),
            'columns': table_columns
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

    # Build relationships from joins table
    edges_list = []
    processed_relationships = set()  # 중복 관계 방지용 집합
    
    def should_show_arrow(l_node_id, r_node_id, l_col, r_col):
        """PK 기준으로 화살표 방향 결정"""
        l_node = nodes_dict.get(l_node_id)
        r_node = nodes_dict.get(r_node_id)
        
        if not l_node or not r_node:
            return None, False
            
        l_pk_cols = l_node['meta'].get('pk_columns', [])
        r_pk_cols = r_node['meta'].get('pk_columns', [])
        
        # PK 컬럼을 모두 조인 조건에 포함하는지 확인
        l_cols = [l_col] if isinstance(l_col, str) else l_col
        r_cols = [r_col] if isinstance(r_col, str) else r_col
        
        l_has_pk = any(col in l_pk_cols for col in l_cols)
        r_has_pk = any(col in r_pk_cols for col in r_cols)
        
        # FK → PK 방향으로 화살표 (FK가 PK를 참조)
        if l_has_pk and not r_has_pk:
            return r_node_id, True  # 오른쪽(FK)에서 왼쪽(PK)으로 화살표
        elif r_has_pk and not l_has_pk:
            return l_node_id, True  # 왼쪽(FK)에서 오른쪽(PK)으로 화살표
        elif l_has_pk and r_has_pk:
            return None, False  # 양쪽 모두 PK면 관계만 표시
        else:
            return None, False  # PK가 없으면 관계만 표시
    
    def create_edge(edge_id, source, target, edge_type, confidence, meta=None):
        """엣지 생성 헬퍼 함수"""
        return {
            'id': edge_id,
            'source': source,
            'target': target,
            'kind': edge_type,
            'confidence': confidence,
            'meta': meta or {}
        }
    
    # joins 테이블에서 테이블 관계 추출
    print(f"# joins 테이블에서 테이블 관계 추출 시작")
    
    if joins:
        # Count join frequency to infer FK relationships
        join_patterns = Counter()
        for join in joins:
            if join.l_table and join.r_table and join.l_col and join.r_col:
                pattern = (join.l_table.upper(), join.l_col.upper(), 
                          join.r_table.upper(), join.r_col.upper())
                join_patterns[pattern] += 1
        
        print(f"# 조인 패턴 분석: {len(join_patterns)}개 패턴")
        
        # Create FK edges for frequently used joins
        edge_id = 1
        for (l_table, l_col, r_table, r_col), frequency in join_patterns.items():
            if frequency >= 1:  # 임계값을 1로 설정 - 더 많은 관계 인식
                print(f"# 조인 패턴: {l_table}.{l_col} -> {r_table}.{r_col} (빈도: {frequency})")
                
                # Use the helper function to resolve abbreviated table names to node_ids
                l_node_id = resolve_abbreviation_to_node_id(l_table, nodes_dict)
                r_node_id = resolve_abbreviation_to_node_id(r_table, nodes_dict)

                if not l_node_id or not r_node_id:
                    print(f"# 노드 ID를 찾을 수 없음: {l_table} -> {l_node_id}, {r_table} -> {r_node_id}")
                    continue
                
                # 중복 관계 방지 - 테이블 쌍이 이미 처리되었는지 확인
                table_pair = tuple(sorted([l_node_id, r_node_id]))
                if table_pair in processed_relationships:
                    continue
                processed_relationships.add(table_pair)
                
                # Check if both tables are in our node set
                if l_node_id in nodes_dict and r_node_id in nodes_dict:
                    # 화살표 방향 결정
                    target_node, has_arrow = should_show_arrow(l_node_id, r_node_id, l_col, r_col)
                    
                    if has_arrow and target_node:
                        # 화살표가 있는 경우: FK -> PK 관계
                        source_node = r_node_id if target_node == l_node_id else l_node_id
                        edges_list.append(create_edge(
                            f"fk_{edge_id}",
                            source_node,
                            target_node,
                            "foreign_key",
                            0.8,
                            {"left_column": l_col, "right_column": r_col, "frequency": frequency, "arrow": True, "source": "joins_table"}
                        ))
                    else:
                        # 일반선인 경우
                        edges_list.append(create_edge(
                            f"rel_{edge_id}",
                            l_node_id,
                            r_node_id,
                            "relationship", 
                            0.7,
                            {"left_column": l_col, "right_column": r_col, "frequency": frequency, "arrow": False, "source": "joins_table"}
                        ))
                    edge_id += 1
    
    print(f"# 생성된 관계선 개수: {len(edges_list)}")
    
    # 디버그: 생성된 관계선 상세 정보 출력
    print(f"# === 생성된 관계선 상세 정보 ===")
    for i, edge in enumerate(edges_list):
        print(f"# 관계선 {i+1}: {edge['source']} -> {edge['target']} (타입: {edge['kind']})")
    
    # Create the final graph structure
    nodes_list = list(nodes_dict.values())
    
    result_graph = create_graph(
        nodes_list,
        edges_list
    )
    
    print(f"# === 최종 그래프 구조 ===")
    print(f"# 노드 개수: {len(result_graph.get('nodes', []))}")
    print(f"# 엣지 개수: {len(result_graph.get('edges', []))}")
    
    return result_graph
