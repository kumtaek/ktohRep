#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERD 데이터 생성 과정을 디버깅하고 검증하는 스크립트
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def debug_erd_data_generation():
    """ERD 데이터 생성 과정을 디버깅합니다."""
    metadata_path = "./project/sampleSrc/metadata.db"
    
    if not os.path.exists(metadata_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {metadata_path}")
        return None
    
    print(f"✅ 메타데이터베이스 발견: {metadata_path}")
    
    try:
        conn = sqlite3.connect(metadata_path)
        cursor = conn.cursor()
        
        print("🔍 ERD 데이터 생성 디버깅 시작...")
        
        # 1. 테이블 정보 조회
        cursor.execute("""
            SELECT table_id, owner, table_name, status, table_comment, llm_comment, llm_comment_confidence
            FROM db_tables
            ORDER BY owner, table_name
        """)
        tables = cursor.fetchall()
        
        print(f"  📊 테이블 정보 조회: {len(tables)}개")
        for table in tables[:5]:  # 처음 5개만 출력
            print(f"    - {table[1]}.{table[2]} ({table[3]})")
        
        # 2. 컬럼 정보 조회
        cursor.execute("""
            SELECT table_id, column_name, data_type, nullable, column_comment
            FROM db_columns
            ORDER BY table_id, column_name
        """)
        columns = cursor.fetchall()
        
        print(f"  📊 컬럼 정보 조회: {len(columns)}개")
        
        # 3. 기본키 정보 조회
        cursor.execute("""
            SELECT table_id, column_name, pk_pos
            FROM db_pk
            ORDER BY table_id, pk_pos
        """)
        pks = cursor.fetchall()
        
        print(f"  📊 기본키 정보 조회: {len(pks)}개")
        
        # 4. 조인 관계 정보 조회
        cursor.execute("""
            SELECT l_table, r_table, l_col, r_col, confidence, inferred_pkfk
            FROM joins
            ORDER BY confidence DESC
        """)
        joins = cursor.fetchall()
        
        print(f"  📊 조인 관계 조회: {len(joins)}개")
        for join in joins[:5]:  # 처음 5개만 출력
            print(f"    - {join[0]}.{join[2]} = {join[2]}.{join[3]} [신뢰도: {join[4]:.1f}]")
        
        # 5. ERD 데이터 구조 생성
        erd_data = {
            "nodes": {},
            "edges": []
        }
        
        # 테이블별 컬럼 정보 정리
        table_columns = {}
        for col in columns:
            table_id, col_name, data_type, nullable, comment = col
            if table_id not in table_columns:
                table_columns[table_id] = []
            table_columns[table_id].append({
                'name': col_name,
                'data_type': data_type,
                'nullable': nullable == 'Y',
                'comment': comment
            })
        
        # 테이블별 기본키 정보 정리
        table_pks = {}
        for pk in pks:
            table_id, col_name, pk_pos = pk
            if table_id not in table_pks:
                table_pks[table_id] = []
            table_pks[table_id].append(col_name)
        
        print(f"\n🔍 노드 생성 과정...")
        
        # 노드 생성
        for table in tables:
            table_id, owner, table_name, status, table_comment, llm_comment, confidence = table
            
            # 테이블별 컬럼 정보
            table_cols = table_columns.get(table_id, [])
            pk_cols = table_pks.get(table_id, [])
            
            # 컬럼 정보에 기본키 표시 추가
            for col in table_cols:
                col['is_pk'] = col['name'] in pk_cols
            
            # 노드 메타데이터
            table_meta = {
                'owner': owner,
                'table_name': table_name,
                'status': status,
                'table_comment': table_comment,
                'llm_comment': llm_comment,
                'llm_comment_confidence': confidence,
                'columns': table_cols,
                'pk_columns': pk_cols
            }
            
            # 노드 ID 생성
            node_id = f"table:{owner}.{table_name}"
            
            # 노드 데이터 생성
            erd_data["nodes"][node_id] = {
                "id": node_id,
                "type": "table",
                "label": f"{owner}.{table_name}",
                "category": "DB",
                "meta": table_meta
            }
            
            print(f"  ✅ 노드 생성: {node_id} (컬럼 {len(table_cols)}개)")
        
        print(f"\n🔍 엣지 생성 과정...")
        
        # 엣지 생성
        for join in joins:
            l_table, r_table, l_col, r_col, confidence, inferred_pkfk = join
            
            # 테이블별칭을 실제 테이블명으로 변환
            def resolve_table_name(alias):
                if alias.startswith('public.'):
                    return alias
                elif alias.startswith('*'):
                    return alias  # 특수 케이스는 그대로 유지
                else:
                    # 별칭을 실제 테이블명으로 매핑 (간단한 규칙)
                    alias_map = {
                        'o': 'ORDERS',
                        'oi': 'ORDER_ITEMS',
                        'p': 'PRODUCTS',
                        'c': 'CUSTOMERS',
                        'u': 'USERS',
                        'b': 'BRANDS'
                    }
                    return alias_map.get(alias, alias)
            
            left_table = resolve_table_name(l_table)
            right_table = resolve_table_name(r_table)
            
            # 엣지 데이터 생성
            edge = {
                "id": f"edge_{len(erd_data['edges'])}",
                "source": f"table:{left_table}",
                "target": f"table:{right_table}",
                "label": f"{l_col} = {r_col}",
                "meta": {
                    "left_column": l_col,
                    "right_column": r_col,
                    "confidence": confidence,
                    "inferred_pkfk": bool(inferred_pkfk)
                }
            }
            
            erd_data["edges"].append(edge)
            print(f"  ✅ 엣지 생성: {left_table} -> {right_table}")
        
        conn.close()
        
        print(f"\n🎯 ERD 데이터 생성 완료!")
        print(f"  📊 노드 수: {len(erd_data['nodes'])}개")
        print(f"  🔗 엣지 수: {len(erd_data['edges'])}개")
        
        # 노드 목록 출력
        print(f"\n📋 생성된 노드 목록:")
        for node_id in erd_data['nodes'].keys():
            print(f"  - {node_id}")
        
        return erd_data
        
    except Exception as e:
        print(f"❌ ERD 데이터 생성 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🔍 ERD 데이터 생성 디버깅")
    print("=" * 80)
    
    # ERD 데이터 생성 및 디버깅
    erd_data = debug_erd_data_generation()
    
    if erd_data:
        print(f"\n✅ 디버깅 완료!")
        print(f"📊 최종 결과:")
        print(f"  - 노드 수: {len(erd_data['nodes'])}개")
        print(f"  - 엣지 수: {len(erd_data['edges'])}개")
        
        # 데이터 검증
        if len(erd_data['nodes']) < 10:
            print(f"⚠️ 경고: 노드 수가 적습니다 ({len(erd_data['nodes'])}개)")
        else:
            print(f"✅ 노드 수가 충분합니다")
            
    else:
        print("❌ 디버깅 실패")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
