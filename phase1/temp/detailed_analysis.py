#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def detailed_analysis():
    """하이브리드 패턴 적용 후 상세 분석"""
    
    # 메타디비 경로
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print("❌ 메타데이터베이스가 존재하지 않습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 하이브리드 패턴 적용 후 상세 분석 ===\n")
        
        # 1. 테이블 구조 확인
        print("=== 테이블 구조 확인 ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  테이블: {table[0]}")
        
        # 2. 파일 상세 정보
        print(f"\n=== 파일 상세 정보 ===")
        cursor.execute("SELECT * FROM files")
        files = cursor.fetchall()
        for file in files:
            print(f"  파일: {file}")
        
        # 3. 클래스 상세 정보
        print(f"\n=== 클래스 상세 정보 ===")
        cursor.execute("SELECT * FROM classes")
        classes = cursor.fetchall()
        if classes:
            for cls in classes:
                print(f"  클래스: {cls}")
        else:
            print("  클래스가 없습니다.")
        
        # 4. 메서드 상세 정보
        print(f"\n=== 메서드 상세 정보 ===")
        cursor.execute("SELECT * FROM methods")
        methods = cursor.fetchall()
        for method in methods:
            print(f"  메서드: {method}")
        
        # 5. 메서드와 클래스 조인 확인
        print(f"\n=== 메서드-클래스 조인 확인 ===")
        cursor.execute("""
            SELECT m.id, m.name, m.class_id, c.name as class_name
            FROM methods m
            LEFT JOIN classes c ON m.class_id = c.id
        """)
        join_results = cursor.fetchall()
        for result in join_results:
            print(f"  메서드 ID: {result[0]}, 이름: {result[1]}, 클래스 ID: {result[2]}, 클래스명: {result[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    detailed_analysis()
