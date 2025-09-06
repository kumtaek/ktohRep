#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_db_schema():
    """데이터베이스 스키마 확인"""
    
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print(f"메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("=== 테이블 목록 ===")
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n=== methods 테이블 스키마 ===")
    cursor.execute("PRAGMA table_info(methods);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    print("\n=== classes 테이블 스키마 ===")
    cursor.execute("PRAGMA table_info(classes);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_db_schema()
