#!/usr/bin/env python3
"""메타데이터베이스 상태 확인 스크립트"""

import sqlite3
import os

def check_metadata_status():
    """메타데이터베이스의 현재 상태를 확인합니다."""
    
    db_path = "../project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📋 메타데이터베이스 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print()
        
        # 주요 테이블 데이터 수 확인
        key_tables = ['sql_units', 'joins', 'edges', 'db_tables', 'db_columns']
        
        for table in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table}: {count}개")
            except sqlite3.OperationalError:
                print(f"❌ {table}: 테이블이 존재하지 않음")
        
        print()
        
        # SQL Units 상세 정보
        cursor.execute("SELECT origin, stmt_id, stmt_kind FROM sql_units LIMIT 5")
        sql_units = cursor.fetchall()
        
        if sql_units:
            print("🔍 SQL Units 상세 정보 (최대 5개):")
            for unit in sql_units:
                print(f"  - {unit[0]}: {unit[1]} ({unit[2]})")
        else:
            print("🔍 SQL Units: 데이터 없음")
        
        print()
        
        # Joins 상세 정보
        cursor.execute("SELECT l_table, r_table, op FROM joins LIMIT 5")
        joins = cursor.fetchall()
        
        if joins:
            print("🔗 Joins 상세 정보 (최대 5개):")
            for join in joins:
                print(f"  - {join[0]} {join[2]} {join[1]}")
        else:
            print("🔗 Joins: 데이터 없음")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_metadata_status()
