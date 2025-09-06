#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def metadb_simple_check():
    """메타디비 간단 확인"""
    
    try:
        conn = sqlite3.connect('../project/sampleSrc/metadata.db')
        cursor = conn.cursor()
        
        # 파일 개수
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        print(f"총 파일 수: {total_files}")
        
        # Java 파일 개수
        cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
        java_files = cursor.fetchone()[0]
        print(f"Java 파일 수: {java_files}")
        
        # 메소드 개수
        cursor.execute("SELECT COUNT(*) FROM methods")
        total_methods = cursor.fetchone()[0]
        print(f"메소드 수: {total_methods}")
        
        # 클래스 개수
        cursor.execute("SELECT COUNT(*) FROM classes")
        total_classes = cursor.fetchone()[0]
        print(f"클래스 수: {total_classes}")
        
        # SQL 유닛 개수
        cursor.execute("SELECT COUNT(*) FROM sql_units")
        total_sql_units = cursor.fetchone()[0]
        print(f"SQL 유닛 수: {total_sql_units}")
        
        conn.close()
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    metadb_simple_check()
