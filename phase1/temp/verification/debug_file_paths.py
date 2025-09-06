#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def debug_file_paths():
    """메타디비의 파일 경로와 실제 파일 경로 비교"""
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print("메타디비 파일이 존재하지 않습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 메타디비의 파일 경로들 확인
        print("=== 메타디비의 파일 경로들 ===")
        cursor.execute("SELECT file_id, path FROM files ORDER BY path")
        db_files = cursor.fetchall()
        
        for file_id, path in db_files:
            print(f"ID: {file_id}, Path: {path}")
        
        print(f"\n총 파일 수: {len(db_files)}개")
        
        # 메소드가 있는 파일들 확인
        print("\n=== 메소드가 있는 파일들 ===")
        cursor.execute("""
            SELECT f.path, COUNT(m.method_id) as method_count
            FROM files f
            LEFT JOIN classes c ON f.file_id = c.file_id
            LEFT JOIN methods m ON c.class_id = m.class_id
            GROUP BY f.file_id, f.path
            ORDER BY method_count DESC
        """)
        method_files = cursor.fetchall()
        
        for path, count in method_files:
            if count > 0:
                print(f"{path}: {count}개 메소드")
        
        # SQL Units가 있는 파일들 확인
        print("\n=== SQL Units가 있는 파일들 ===")
        cursor.execute("""
            SELECT f.path, COUNT(s.sql_id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.file_id = s.file_id
            GROUP BY f.file_id, f.path
            ORDER BY sql_count DESC
        """)
        sql_files = cursor.fetchall()
        
        for path, count in sql_files:
            if count > 0:
                print(f"{path}: {count}개 SQL Units")
        
        conn.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    debug_file_paths()

