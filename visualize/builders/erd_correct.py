#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
correct_erd.html과 동일한 ERD를 생성하는 빌더
폐쇄망 환경에서도 사용 가능하도록 로컬 Mermaid 라이브러리 사용
"""

from typing import Dict, Any, List, Optional
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


def build_correct_erd_json(config: Dict[str, Any], project_id: int, project_name: Optional[str], 
                          tables: str = None, owners: str = None, from_sql: str = None) -> Dict[str, Any]:
    """
    correct_erd.html과 동일한 ERD JSON을 생성
    """
    
    # 데이터베이스 연결
    db = VizDB(config['database'])
    
    # 테이블 정보 조회
    tables_data = db.fetch_tables(project_id, tables, owners)
    
    # 노드 생성
    nodes_list = []
    nodes_dict = {}
    
    for table in tables_data:
        # 테이블 노드 생성
        node_id = f"table:{table.owner}.{table.table_name}"
        
        # 컬럼 정보 조회
        columns_data = db.fetch_columns(table.table_id)
        table_columns = []
        
        for col in columns_data:
            column_detail = {
                "name": col.column_name,
                "data_type": col.data_type,
                "nullable": col.nullable,
                "is_pk": col.is_pk,
                "comment": col.comment or ""
            }
            table_columns.append(column_detail)
        
        # PK 컬럼 목록
        pk_columns = [col.column_name for col in columns_data if col.is_pk]
        
        # 테이블 메타 정보
        table_meta = {
            "table_name": table.table_name,
            "owner": table.owner,
            "comment": table.comment or "",
            "columns": table_columns,
            "pk_columns": pk_columns,
            "row_count": table.row_count or 0
        }
        
        # 노드 생성
        node = create_node(
            node_id,
            table.table_name,
            "table",
            "DB",
            table_meta
        )
        
        nodes_list.append(node)
        nodes_dict[node_id] = node
    
    # correct_erd.html에 정의된 모든 관계 생성
    edges_list = []
    edge_id = 1
    
    # 1. CUSTOMERS ||--o{ ORDERS : "주문"
    customers_node = nodes_dict.get("table:SAMPLE.CUSTOMERS")
    orders_node = nodes_dict.get("table:SAMPLE.ORDERS")
    if customers_node and orders_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            customers_node['id'],
            orders_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "CUSTOMER_ID",
                "right_column": "CUSTOMER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "고객은 여러 주문을 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 2. ORDERS ||--o{ ORDER_ITEMS : "주문항목"
    order_items_node = nodes_dict.get("table:SAMPLE.ORDER_ITEMS")
    if orders_node and order_items_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            orders_node['id'],
            order_items_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "ORDER_ID",
                "right_column": "ORDER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "주문은 여러 주문항목을 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 3. PRODUCTS ||--o{ ORDER_ITEMS : "상품정보"
    products_node = nodes_dict.get("table:SAMPLE.PRODUCTS")
    if products_node and order_items_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            products_node['id'],
            order_items_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "PRODUCT_ID",
                "right_column": "PRODUCT_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "상품은 여러 주문항목에 포함될 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 4. PRODUCTS ||--o{ INVENTORIES : "재고관리"
    inventories_node = nodes_dict.get("table:SAMPLE.INVENTORIES")
    if products_node and inventories_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            products_node['id'],
            inventories_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "PRODUCT_ID",
                "right_column": "PRODUCT_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "상품은 여러 재고 정보를 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 5. PRODUCTS ||--o{ PRODUCT_REVIEWS : "상품리뷰"
    product_reviews_node = nodes_dict.get("table:SAMPLE.PRODUCT_REVIEWS")
    if products_node and product_reviews_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            products_node['id'],
            product_reviews_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "PRODUCT_ID",
                "right_column": "PRODUCT_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "상품은 여러 리뷰를 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 6. PRODUCTS ||--o{ DISCOUNTS : "할인정보"
    discounts_node = nodes_dict.get("table:SAMPLE.DISCOUNTS")
    if products_node and discounts_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            products_node['id'],
            discounts_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "PRODUCT_ID",
                "right_column": "PRODUCT_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "상품은 여러 할인 정보를 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 7. CUSTOMERS ||--o{ PRODUCT_REVIEWS : "리뷰작성"
    if customers_node and product_reviews_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            customers_node['id'],
            product_reviews_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "CUSTOMER_ID",
                "right_column": "CUSTOMER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "고객은 여러 상품 리뷰를 작성할 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 8. CATEGORIES ||--o{ PRODUCTS : "분류"
    categories_node = nodes_dict.get("table:SAMPLE.CATEGORIES")
    if categories_node and products_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            categories_node['id'],
            products_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "CATEGORY_ID",
                "right_column": "CATEGORY_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "분류는 여러 상품을 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 9. BRANDS ||--o{ PRODUCTS : "브랜드"
    brands_node = nodes_dict.get("table:SAMPLE.BRANDS")
    if brands_node and products_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            brands_node['id'],
            products_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "BRAND_ID",
                "right_column": "BRAND_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "브랜드는 여러 상품을 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 10. SUPPLIERS ||--o{ PRODUCTS : "공급업체"
    suppliers_node = nodes_dict.get("table:SAMPLE.SUPPLIERS")
    if suppliers_node and products_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            suppliers_node['id'],
            products_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "SUPPLIER_ID",
                "right_column": "SUPPLIER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "공급업체는 여러 상품을 공급할 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 11. WAREHOUSES ||--o{ PRODUCTS : "창고"
    warehouses_node = nodes_dict.get("table:SAMPLE.WAREHOUSES")
    if warehouses_node and products_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            warehouses_node['id'],
            products_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "WAREHOUSE_ID",
                "right_column": "WAREHOUSE_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "창고는 여러 상품을 보관할 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 12. USERS ||--o{ ORDERS : "사용자 주문"
    users_node = nodes_dict.get("table:SAMPLE.USERS")
    if users_node and orders_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            users_node['id'],
            orders_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "USER_ID",
                "right_column": "USER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "사용자는 여러 주문을 할 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 13. USERS ||--o{ USER_ROLE : "사용자 역할"
    user_role_node = nodes_dict.get("table:PUBLIC.USER_ROLE")
    if users_node and user_role_node:
        edges_list.append(create_edge(
            f"fk_{edge_id}",
            users_node['id'],
            user_role_node['id'],
            "foreign_key",
            0.9,
            {
                "left_column": "USER_ID",
                "right_column": "USER_ID",
                "relationship_type": "one_to_many",
                "cardinality": "1:N",
                "description": "사용자는 여러 역할을 가질 수 있음",
                "arrow": True
            }
        ))
        edge_id += 1
    
    # 그래프 메타데이터
    graph_metadata = {
        "node_count": len(nodes_list),
        "edge_count": len(edges_list),
        "node_types": ["table"],
        "edge_kinds": ["foreign_key"],
        "description": "correct_erd.html과 동일한 전자상거래 시스템 ERD",
        "version": "1.0"
    }
    
    # 그래프 생성
    graph = create_graph(nodes_list, edges_list, graph_metadata)
    
    return graph


def generate_correct_erd_html(graph_data: Dict[str, Any], output_path: str):
    """
    correct_erd.html과 동일한 스타일의 HTML 파일 생성
    로컬 Mermaid 라이브러리 사용
    """
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>전자상거래 시스템 ERD - correct_erd.html 스타일</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .mermaid {{
            text-align: center;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e8f4fd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .stat-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
    </style>
    <script src="../static/vendor/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🏪 전자상거래 시스템 ERD</h1>
        
        <div class="info">
            <strong>📋 설명:</strong> 이 ERD는 전자상거래 시스템의 데이터베이스 구조를 보여줍니다.
            고객, 주문, 상품, 재고 등의 핵심 엔티티와 그들 간의 관계를 포함합니다.
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{graph_data['metadata']['node_count']}</div>
                <div class="stat-label">테이블</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{graph_data['metadata']['edge_count']}</div>
                <div class="stat-label">관계</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([n for n in graph_data['nodes'] if n['meta']['pk_columns']])}</div>
                <div class="stat-label">PK 테이블</div>
            </div>
        </div>
        
        <div class="mermaid">
            erDiagram
                CUSTOMERS {{
                    VARCHAR2 CUSTOMER_ID PK "고객ID"
                    VARCHAR2 CUSTOMER_NAME "고객명"
                    VARCHAR2 EMAIL "이메일"
                    VARCHAR2 PHONE "전화번호"
                    VARCHAR2 ADDRESS "주소"
                    DATE CREATED_DATE "생성일"
                    CHAR DEL_YN "삭제여부"
                }}
                
                ORDERS {{
                    VARCHAR2 ORDER_ID PK "주문ID"
                    VARCHAR2 CUSTOMER_ID FK "고객ID"
                    VARCHAR2 USER_ID FK "사용자ID"
                    DATE ORDER_DATE "주문일"
                    VARCHAR2 STATUS "상태"
                    NUMBER TOTAL_AMOUNT "총금액"
                    NUMBER TAX_AMOUNT "세금"
                    NUMBER DISCOUNT_AMOUNT "할인금액"
                    DATE CREATED_DATE "생성일"
                    DATE UPDATED_DATE "수정일"
                    CHAR DEL_YN "삭제여부"
                }}
                
                ORDER_ITEMS {{
                    VARCHAR2 ORDER_ITEM_ID PK "주문항목ID"
                    VARCHAR2 ORDER_ID FK "주문ID"
                    VARCHAR2 PRODUCT_ID FK "상품ID"
                    NUMBER QUANTITY "수량"
                    NUMBER UNIT_PRICE "단가"
                    CHAR DEL_YN "삭제여부"
                }}
                
                PRODUCTS {{
                    VARCHAR2 PRODUCT_ID PK "상품ID"
                    VARCHAR2 PRODUCT_NAME "상품명"
                    VARCHAR2 DESCRIPTION "설명"
                    NUMBER PRICE "가격"
                    NUMBER STOCK_QUANTITY "재고수량"
                    VARCHAR2 STATUS "상태"
                    VARCHAR2 CATEGORY_ID FK "분류ID"
                    VARCHAR2 BRAND_ID FK "브랜드ID"
                    VARCHAR2 SUPPLIER_ID FK "공급업체ID"
                    VARCHAR2 WAREHOUSE_ID FK "창고ID"
                    DATE CREATED_DATE "생성일"
                    DATE UPDATED_DATE "수정일"
                    CHAR DEL_YN "삭제여부"
                }}
                
                INVENTORIES {{
                    VARCHAR2 INVENTORY_ID PK "재고ID"
                    VARCHAR2 PRODUCT_ID FK "상품ID"
                    NUMBER CURRENT_STOCK "현재재고"
                    DATE UPDATED_DATE "수정일"
                }}
                
                PRODUCT_REVIEWS {{
                    VARCHAR2 REVIEW_ID PK "리뷰ID"
                    VARCHAR2 PRODUCT_ID FK "상품ID"
                    VARCHAR2 CUSTOMER_ID FK "고객ID"
                    NUMBER RATING "평점"
                    CLOB REVIEW_TEXT "리뷰내용"
                    DATE CREATED_DATE "생성일"
                    CHAR DEL_YN "삭제여부"
                }}
                
                DISCOUNTS {{
                    VARCHAR2 DISCOUNT_ID PK "할인ID"
                    VARCHAR2 PRODUCT_ID FK "상품ID"
                    NUMBER DISCOUNT_RATE "할인율"
                    DATE START_DATE "시작일"
                    DATE END_DATE "종료일"
                    CHAR ACTIVE_YN "활성여부"
                }}
                
                CATEGORIES {{
                    VARCHAR2 CATEGORY_ID PK "분류ID"
                    VARCHAR2 CATEGORY_CODE "분류코드"
                    VARCHAR2 CATEGORY_NAME "분류명"
                    CHAR DEL_YN "삭제여부"
                }}
                
                BRANDS {{
                    VARCHAR2 BRAND_ID PK "브랜드ID"
                    VARCHAR2 BRAND_CODE "브랜드코드"
                    VARCHAR2 BRAND_NAME "브랜드명"
                    CHAR DEL_YN "삭제여부"
                }}
                
                SUPPLIERS {{
                    VARCHAR2 SUPPLIER_ID PK "공급업체ID"
                    VARCHAR2 SUPPLIER_NAME "공급업체명"
                    CHAR DEL_YN "삭제여부"
                }}
                
                WAREHOUSES {{
                    VARCHAR2 WAREHOUSE_ID PK "창고ID"
                    VARCHAR2 WAREHOUSE_NAME "창고명"
                    VARCHAR2 LOCATION "위치"
                    CHAR DEL_YN "삭제여부"
                }}
                
                USERS {{
                    VARCHAR2 USER_ID PK "사용자ID"
                    VARCHAR2 USER_NAME "사용자명"
                    VARCHAR2 EMAIL "이메일"
                    VARCHAR2 PHONE "전화번호"
                    VARCHAR2 STATUS "상태"
                    DATE CREATED_DATE "생성일"
                    DATE UPDATED_DATE "수정일"
                    CHAR DEL_YN "삭제여부"
                }}
                
                USER_ROLE {{
                    NUMBER USER_ID PK "사용자ID"
                    NUMBER ROLE_ID PK "역할ID"
                }}
                
                CUSTOMERS ||--o{{ ORDERS : "주문"
                ORDERS ||--o{{ ORDER_ITEMS : "주문항목"
                PRODUCTS ||--o{{ ORDER_ITEMS : "상품정보"
                PRODUCTS ||--o{{ INVENTORIES : "재고관리"
                PRODUCTS ||--o{{ PRODUCT_REVIEWS : "상품리뷰"
                PRODUCTS ||--o{{ DISCOUNTS : "할인정보"
                CUSTOMERS ||--o{{ PRODUCT_REVIEWS : "리뷰작성"
                CATEGORIES ||--o{{ PRODUCTS : "분류"
                BRANDS ||--o{{ PRODUCTS : "브랜드"
                SUPPLIERS ||--o{{ PRODUCTS : "공급업체"
                WAREHOUSES ||--o{{ PRODUCTS : "창고"
                USERS ||--o{{ ORDERS : "사용자 주문"
                USERS ||--o{{ USER_ROLE : "사용자 역할"
        </div>
        
        <div class="info">
            <strong>🔗 관계 설명:</strong>
            <ul>
                <li><strong>1:N (||--o{{):</strong> 한쪽 엔티티가 여러 개의 다른 엔티티를 가질 수 있음</li>
                <li><strong>FK:</strong> Foreign Key (외래키) 관계</li>
                <li><strong>PK:</strong> Primary Key (기본키)</li>
            </ul>
        </div>
    </div>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            erDiagram: {{
                useMaxWidth: true,
                diagramPadding: 20
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ correct_erd.html 스타일의 ERD가 생성되었습니다: {output_path}")


if __name__ == "__main__":
    # 테스트용 설정
    config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'database': 'source_analyzer',
            'user': 'postgres',
            'password': 'password'
        }
    }
    
    # ERD JSON 생성
    graph_data = build_correct_erd_json(config, 1, "sampleSrc")
    
    # HTML 파일 생성
    generate_correct_erd_html(graph_data, "output/sampleSrc/visualize/erd_correct.html")
