#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb_detailed():
    """메타디비 상세 상태 확인"""
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print(f"메타디비 파일이 존재하지 않습니다: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Files 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(files)")
        files_schema = cursor.fetchall()
        print("=== Files 테이블 스키마 ===")
        for col in files_schema:
            print(f"- {col[1]} ({col[2]})")
        
        # Methods 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(methods)")
        methods_schema = cursor.fetchall()
        print("\n=== Methods 테이블 스키마 ===")
        for col in methods_schema:
            print(f"- {col[1]} ({col[2]})")
        
        # SQL Units 테이블 스키마 확인
        cursor.execute("PRAGMA table_info(sql_units)")
        sql_schema = cursor.fetchall()
        print("\n=== SQL Units 테이블 스키마 ===")
        for col in sql_schema:
            print(f"- {col[1]} ({col[2]})")
        
        # 파일별 상세 정보 (올바른 컬럼명 사용)
        print("\n=== 파일별 메소드 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(m.id) as method_count
            FROM files f
            LEFT JOIN methods m ON f.id = m.file_id
            GROUP BY f.id, f.path
            ORDER BY f.path
        """)
        file_methods = cursor.fetchall()
        for file_path, method_count in file_methods:
            print(f"{file_path}: {method_count}개 메소드")
        
        # 파일별 SQL Units 개수
        print("\n=== 파일별 SQL Units 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.id = s.file_id
            GROUP BY f.id, f.path
            ORDER BY f.path
        """)
        file_sqls = cursor.fetchall()
        for file_path, sql_count in file_sqls:
            print(f"{file_path}: {sql_count}개 SQL")
        
        # Java 파일만 필터링
        print("\n=== Java 파일별 메소드 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(m.id) as method_count
            FROM files f
            LEFT JOIN methods m ON f.id = m.file_id
            WHERE f.path LIKE '%.java'
            GROUP BY f.id, f.path
            ORDER BY f.path
        """)
        java_methods = cursor.fetchall()
        for file_path, method_count in java_methods:
            print(f"{file_path}: {method_count}개 메소드")
        
        # XML 파일만 필터링
        print("\n=== XML 파일별 SQL Units 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.id = s.file_id
            WHERE f.path LIKE '%.xml'
            GROUP BY f.id, f.path
            ORDER BY f.path
        """)
        xml_sqls = cursor.fetchall()
        for file_path, sql_count in xml_sqls:
            print(f"{file_path}: {sql_count}개 SQL")
        
        conn.close()
        
    except Exception as e:
        print(f"메타디비 조회 중 오류 발생: {e}")

if __name__ == "__main__":
    check_metadb_detailed()
