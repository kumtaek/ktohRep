#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def debug_xml_sql_units():
    """XML 파일의 SQL Units 저장 문제 디버깅"""
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print("메타디비 파일이 존재하지 않습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # XML 파일들 확인
        print("=== XML 파일들 ===")
        cursor.execute("""
            SELECT file_id, path 
            FROM files 
            WHERE path LIKE '%.xml'
            ORDER BY path
        """)
        xml_files = cursor.fetchall()
        
        for file_id, path in xml_files:
            print(f"ID: {file_id}, Path: {path}")
            
            # 해당 파일의 SQL Units 확인
            cursor.execute("""
                SELECT sql_id, stmt_id, stmt_kind, origin
                FROM sql_units 
                WHERE file_id = ?
            """, (file_id,))
            sql_units = cursor.fetchall()
            
            print(f"  SQL Units 개수: {len(sql_units)}")
            for sql_id, stmt_id, stmt_kind, origin in sql_units:
                print(f"    SQL ID: {sql_id}, Stmt ID: {stmt_id}, Kind: {stmt_kind}, Origin: {origin}")
        
        # 전체 SQL Units 통계
        print("\n=== 전체 SQL Units 통계 ===")
        cursor.execute("SELECT COUNT(*) FROM sql_units")
        total_sql_units = cursor.fetchone()[0]
        print(f"전체 SQL Units: {total_sql_units}개")
        
        cursor.execute("SELECT origin, COUNT(*) FROM sql_units GROUP BY origin")
        origin_stats = cursor.fetchall()
        for origin, count in origin_stats:
            print(f"  {origin}: {count}개")
        
        conn.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_xml_sql_units()

