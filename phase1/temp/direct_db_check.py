#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def direct_db_check():
    """직접 데이터베이스 체크"""
    
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print(f"메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    try:
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
        
        # 파일 수 조회
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        
        # 조인 수 조회
        cursor.execute("SELECT COUNT(*) FROM joins")
        join_count = cursor.fetchone()[0]
        
        print("=== 메타디비 집계 결과 ===")
        print(f"파일 수: {file_count}개")
        print(f"클래스 수: {class_count}개")
        print(f"메서드 수: {method_count}개")
        print(f"SQL 단위 수: {sql_unit_count}개")
        print(f"조인 수: {join_count}개")
        
        conn.close()
        
    except Exception as e:
        print(f"데이터베이스 조회 중 오류: {e}")

if __name__ == "__main__":
    direct_db_check()
