#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
메타디비 데이터 디버깅
과다추출 원인 분석
"""

import sqlite3
import os

def debug_metadb_data():
    """메타디비 데이터 디버깅"""
    
    print("=== 메타디비 데이터 디버깅 ===")
    
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    # 클래스 데이터 상세 분석
    print("\n=== 클래스 데이터 상세 분석 ===")
    cursor.execute("SELECT name, file_path FROM classes LIMIT 20")
    classes = cursor.fetchall()
    
    print(f"클래스 수: {len(classes)}")
    for i, (name, file_path) in enumerate(classes, 1):
        print(f"  {i}. {name} ({file_path})")
    
    # 메소드 데이터 상세 분석
    print("\n=== 메소드 데이터 상세 분석 ===")
    cursor.execute("SELECT name, file_path FROM methods LIMIT 20")
    methods = cursor.fetchall()
    
    print(f"메소드 수: {len(methods)}")
    for i, (name, file_path) in enumerate(methods, 1):
        print(f"  {i}. {name} ({file_path})")
    
    # SQL Units 데이터 상세 분석
    print("\n=== SQL Units 데이터 상세 분석 ===")
    cursor.execute("SELECT type, file_path FROM sql_units LIMIT 20")
    sql_units = cursor.fetchall()
    
    print(f"SQL Units 수: {len(sql_units)}")
    for i, (sql_type, file_path) in enumerate(sql_units, 1):
        print(f"  {i}. {sql_type} ({file_path})")
    
    # 파일별 상세 분석
    print("\n=== 파일별 상세 분석 ===")
    cursor.execute("""
        SELECT f.file_path, f.language, 
               COUNT(DISTINCT c.id) as class_count,
               COUNT(DISTINCT m.id) as method_count,
               COUNT(DISTINCT s.id) as sql_count
        FROM files f
        LEFT JOIN classes c ON f.id = c.file_id
        LEFT JOIN methods m ON f.id = m.file_id
        LEFT JOIN sql_units s ON f.id = s.file_id
        GROUP BY f.id, f.file_path, f.language
        ORDER BY class_count DESC, method_count DESC
    """)
    
    file_stats = cursor.fetchall()
    
    for file_path, language, class_count, method_count, sql_count in file_stats:
        print(f"  {file_path} ({language}):")
        print(f"    클래스: {class_count}, 메소드: {method_count}, SQL: {sql_count}")
    
    conn.close()

if __name__ == "__main__":
    debug_metadb_data()



