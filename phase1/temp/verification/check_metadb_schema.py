#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_metadb_schema():
    """메타디비 스키마 확인"""
    print("=== 메타디비 스키마 확인 ===\n")
    
    db_path = "project/sampleSrc/metadata.db"
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 테이블 목록 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("테이블 목록:")
            for table in tables:
                print(f"  - {table[0]}")
            
            print("\n=== files 테이블 스키마 ===")
            cursor.execute("PRAGMA table_info(files)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            print("\n=== classes 테이블 스키마 ===")
            cursor.execute("PRAGMA table_info(classes)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            print("\n=== methods 테이블 스키마 ===")
            cursor.execute("PRAGMA table_info(methods)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 메타디비 조회 오류: {e}")
    else:
        print("❌ 메타디비 파일이 없습니다.")

if __name__ == "__main__":
    import os
    check_metadb_schema()

