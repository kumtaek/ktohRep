#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def quick_check():
    """빠른 메타디비 체크"""
    
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print(f"메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 메서드 수 조회
    cursor.execute("SELECT COUNT(*) FROM methods")
    method_count = cursor.fetchone()[0]
    
    # 클래스 수 조회
    cursor.execute("SELECT COUNT(*) FROM classes")
    class_count = cursor.fetchone()[0]
    
    # SQL 단위 수 조회
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    sql_unit_count = cursor.fetchone()[0]
    
    print(f"메서드 수: {method_count}개")
    print(f"클래스 수: {class_count}개")
    print(f"SQL 단위 수: {sql_unit_count}개")
    
    conn.close()

if __name__ == "__main__":
    quick_check()
