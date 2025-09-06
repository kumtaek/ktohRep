#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_actual_getter_setter():
    """실제 getter/setter 메서드 내용 확인"""
    
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print(f"메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # getter/setter 메서드 조회
    query = """
    SELECT m.name, m.signature, m.start_line, m.end_line, f.path
    FROM methods m
    JOIN classes c ON m.class_id = c.class_id
    JOIN files f ON c.file_id = f.file_id
    WHERE (m.name LIKE 'get%' OR m.name LIKE 'set%' OR m.name LIKE 'is%')
    ORDER BY m.name
    LIMIT 10
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("=== Getter/Setter 메서드 샘플 (처음 10개) ===")
    for i, (name, signature, start_line, end_line, path) in enumerate(results, 1):
        print(f"{i}. {name} - {signature}")
        print(f"   파일: {path}")
        print(f"   라인: {start_line}-{end_line}")
        print(f"   라인 수: {end_line - start_line + 1}")
        print()
    
    # 전체 메서드 수 확인
    query2 = """
    SELECT COUNT(*) as total_methods
    FROM methods
    """
    cursor.execute(query2)
    total_methods = cursor.fetchone()[0]
    
    # getter/setter 메서드 수 확인
    query3 = """
    SELECT COUNT(*) as getter_setter_methods
    FROM methods
    WHERE (name LIKE 'get%' OR name LIKE 'set%' OR name LIKE 'is%')
    """
    cursor.execute(query3)
    getter_setter_methods = cursor.fetchone()[0]
    
    print(f"=== 메서드 수 요약 ===")
    print(f"전체 메서드: {total_methods}개")
    print(f"Getter/Setter 메서드: {getter_setter_methods}개")
    print(f"비즈니스 메서드: {total_methods - getter_setter_methods}개")
    
    conn.close()

if __name__ == "__main__":
    check_actual_getter_setter()
