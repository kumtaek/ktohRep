#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 SQL 쿼리로 ERD 데이터를 생성하는 스크립트 (수정된 버전)
테이블별칭 해석 로직을 개선하여 실제 스키마(SAMPLE)와 일치하도록 수정합니다.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

def generate_erd_data():
    """직접 SQL 쿼리로 ERD 데이터를 생성합니다."""
    # 설정 파일에서 프로젝트명과 스키마를 동적으로 읽기
    import yaml
    import os
    
    # 설정 파일 경로 (새로운 폴더 구조)
    config_path = "./visualize/config/config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 필수 설정값 확인
    if not config:
        raise ValueError("설정 파일이 비어있거나 잘못되었습니다")
    
    database_config = config.get('database')
    if not database_config:
        raise ValueError("설정 파일에 database 섹션이 없습니다")
    
    default_schema = database_config.get('default_schema')
    if not default_schema:
        raise ValueError("설정 파일에 default_schema가 설정되지 않았습니다")
    
    project_name = 'sampleSrc'  # 시각화는 sampleSrc 프로젝트 전용
    
    metadata_path = f"./project/{project_name}/metadata.db"
    
    if not os.path.exists(metadata_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {metadata_path}")
        return None
    
    print(f"✅ 메타데이터베이스 발견: {metadata_path}")
    
    try:
        conn = sqlite3.connect(metadata_path)
        cursor = conn.cursor()
        
        print("🔍 ERD 데이터 생성 시작...")
        
        # 1. 테이블 정보 조회
        cursor.execute("""
            SELECT table_id, owner, table_name, status, table_comment, llm_comment, llm_comment_confidence
            FROM db_tables
            ORDER BY owner, table_name
        """)
        tables = cursor.fetchall()
        
        print(f"  📊 테이블 정보 조회: {len(tables)}개")
        
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
        
        # 엣지 생성 (테이블별칭 해석 로직 개선)
        print("🔍 엣지 생성 중...")
        
        for join in joins:
            l_table, r_table, l_col, r_col, confidence, inferred_pkfk = join
            
            # 테이블별칭을 실제 테이블명으로 변환 (개선된 로직)
            def resolve_table_name(alias, cursor):
                """메타데이터베이스를 활용한 동적 테이블 별칭 해결"""
                try:
                    # public. 접두사 제거
                    if alias.startswith('public.'):
                        alias = alias[7:]  # 'public.' 제거
                    
                    # 특수 케이스는 그대로 유지
                    if alias.startswith('*'):
                        return alias
                    
                    # 메타데이터베이스에서 테이블명으로 검색하여 owner 찾기
                    cursor.execute("""
                        SELECT owner, table_name 
                        FROM db_tables 
                        WHERE table_name LIKE ? 
                        ORDER BY status DESC, table_id ASC
                    """, (f'%{alias.upper()}%',))
                    
                    result = cursor.fetchone()
                    if result:
                        owner, table_name = result
                        return f"{owner}.{table_name}"
                    
                    # 찾지 못한 경우 원본 반환
                    return alias
                    
                except Exception as e:
                    print(f"⚠️ 별칭 해결 중 오류: {alias} - {e}")
                    return alias
            
            left_table = resolve_table_name(l_table, cursor)
            right_table = resolve_table_name(r_table, cursor)
            
            # 실제 노드 ID 생성
            left_node_id = f"table:{left_table}"
            right_node_id = f"table:{right_table}"
            
            # 노드가 실제로 존재하는지 확인
            if left_node_id not in erd_data["nodes"]:
                print(f"⚠️ 왼쪽 노드가 존재하지 않음: {left_node_id} (원본: {l_table})")
                continue
                
            if right_node_id not in erd_data["nodes"]:
                print(f"⚠️ 오른쪽 노드가 존재하지 않음: {right_node_id} (원본: {r_table})")
                continue
            
            # 엣지 데이터 생성
            edge = {
                "id": f"edge_{len(erd_data['edges'])}",
                "source": left_node_id,
                "target": right_node_id,
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
        
        print(f"✅ ERD 데이터 생성 완료!")
        print(f"  📊 노드 수: {len(erd_data['nodes'])}개")
        print(f"  🔗 엣지 수: {len(erd_data['edges'])}개")
        
        return erd_data
        
    except Exception as e:
        print(f"❌ ERD 데이터 생성 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_erd_data(erd_data, output_path):
    """ERD 데이터를 JSON 파일로 저장합니다."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(erd_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ ERD 데이터 저장 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ ERD 데이터 저장 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚀 직접 SQL 쿼리로 ERD 데이터 생성 (수정된 버전)")
    print("=" * 80)
    
    # ERD 데이터 생성
    erd_data = generate_erd_data()
    
    if erd_data:
        # 새로운 폴더 구조에 맞춰 출력 디렉토리 생성
        output_dir = Path(f"./project/{project_name}/report")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ERD 데이터를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"erd_data_fixed_{timestamp}.json"
        
        if save_erd_data(erd_data, json_path):
            print(f"\n🎉 ERD 데이터 생성 및 저장 완료!")
            print(f"📁 저장 위치: {json_path}")
            print(f"📊 데이터 요약:")
            print(f"  - 테이블 수: {len(erd_data['nodes'])}개")
            print(f"  - 관계 수: {len(erd_data['edges'])}개")
            
            # 노드 목록 출력
            print(f"\n📋 생성된 노드 목록:")
            for node_id in erd_data['nodes'].keys():
                print(f"  - {node_id}")
            
            # 엣지 목록 출력
            print(f"\n🔗 생성된 엣지 목록:")
            for edge in erd_data['edges']:
                print(f"  - {edge['source']} -> {edge['target']}")
        else:
            print("❌ ERD 데이터 저장 실패")
    else:
        print("❌ ERD 데이터 생성 실패")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
