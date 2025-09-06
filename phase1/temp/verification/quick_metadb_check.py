#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb():
    metadb_path = '../project/sampleSrc/metadata.db'
    
    if not os.path.exists(metadb_path):
        print(f"메타DB 파일이 없습니다: {metadb_path}")
        return
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    print("=== 메타DB 상태 확인 ===")
    
    # Java 파일 개수
    cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
    java_files = cursor.fetchone()[0]
    print(f"Java 파일: {java_files}개")
    
    # Sql_units 개수
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    sql_units = cursor.fetchone()[0]
    print(f"Sql_units: {sql_units}개")
    
    # 파일별 sql_units 개수
    cursor.execute("""
        SELECT f.path, COUNT(s.sql_id) as count
        FROM files f
        LEFT JOIN sql_units s ON f.file_id = s.file_id
        WHERE f.language = 'java'
        GROUP BY f.file_id, f.path
        ORDER BY count DESC
    """)
    
    print("\n=== 파일별 Sql_units 개수 ===")
    for path, count in cursor.fetchall():
        print(f"{path}: {count}개")
    
    conn.close()

if __name__ == "__main__":
    check_metadb()
