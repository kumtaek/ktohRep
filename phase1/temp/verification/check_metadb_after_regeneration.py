#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb_after_regeneration():
    """재생성된 메타디비 상태 확인"""
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print(f"메타디비 파일이 존재하지 않습니다: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 재생성된 메타디비 데이터 현황 ===")
        
        # Files 테이블
        cursor.execute("SELECT COUNT(*) FROM files")
        files_count = cursor.fetchone()[0]
        print(f"Files: {files_count}개")
        
        # Methods 테이블
        cursor.execute("SELECT COUNT(*) FROM methods")
        methods_count = cursor.fetchone()[0]
        print(f"Methods: {methods_count}개")
        
        # SQL Units 테이블
        cursor.execute("SELECT COUNT(*) FROM sql_units")
        sql_count = cursor.fetchone()[0]
        print(f"SQL Units: {sql_count}개")
        
        # Chunks 테이블
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunks_count = cursor.fetchone()[0]
        print(f"Chunks: {chunks_count}개")
        
        # 파일별 상세 정보
        print("\n=== 파일별 메소드 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(m.method_id) as method_count
            FROM files f
            LEFT JOIN methods m ON f.file_id = m.class_id
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        file_methods = cursor.fetchall()
        for file_path, method_count in file_methods:
            print(f"{file_path}: {method_count}개 메소드")
        
        # 파일별 SQL Units 개수
        print("\n=== 파일별 SQL Units 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.sql_id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.file_id = s.file_id
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        file_sqls = cursor.fetchall()
        for file_path, sql_count in file_sqls:
            print(f"{file_path}: {sql_count}개 SQL")
        
        # Java 파일만 필터링
        print("\n=== Java 파일별 메소드 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(m.method_id) as method_count
            FROM files f
            LEFT JOIN methods m ON f.file_id = m.class_id
            WHERE f.path LIKE '%.java'
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        java_methods = cursor.fetchall()
        for file_path, method_count in java_methods:
            print(f"{file_path}: {method_count}개 메소드")
        
        # XML 파일만 필터링
        print("\n=== XML 파일별 SQL Units 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.sql_id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.file_id = s.file_id
            WHERE f.path LIKE '%.xml'
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        xml_sqls = cursor.fetchall()
        for file_path, sql_count in xml_sqls:
            print(f"{file_path}: {sql_count}개 SQL")
        
        # JSP 파일만 필터링
        print("\n=== JSP 파일별 SQL Units 개수 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.sql_id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.file_id = s.file_id
            WHERE f.path LIKE '%.jsp'
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        jsp_sqls = cursor.fetchall()
        for file_path, sql_count in jsp_sqls:
            print(f"{file_path}: {sql_count}개 SQL")
        
        # 전체 요약
        print("\n=== 전체 요약 ===")
        print(f"총 파일 수: {files_count}개")
        print(f"총 메소드 수: {methods_count}개")
        print(f"총 SQL Units 수: {sql_count}개")
        print(f"총 Chunks 수: {chunks_count}개")
        
        conn.close()
        
        return {
            'files': files_count,
            'methods': methods_count,
            'sql_units': sql_count,
            'chunks': chunks_count,
            'file_methods': file_methods,
            'file_sqls': file_sqls,
            'java_methods': java_methods,
            'xml_sqls': xml_sqls,
            'jsp_sqls': jsp_sqls
        }
        
    except Exception as e:
        print(f"메타디비 조회 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    result = check_metadb_after_regeneration()

