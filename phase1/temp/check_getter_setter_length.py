#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_getter_setter_length():
    """getter/setter 메서드의 본문 길이를 확인"""
    
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
    LIMIT 20
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("=== Getter/Setter 메서드 샘플 (처음 20개) ===")
    for i, (name, signature, start_line, end_line, path) in enumerate(results, 1):
        print(f"{i}. {name} - {signature}")
        print(f"   파일: {path}")
        print(f"   라인: {start_line}-{end_line}")
        print(f"   라인 수: {end_line - start_line + 1}")
        print()
    
    # 본문 길이별 분포 확인
    query2 = """
    SELECT 
        CASE 
            WHEN (m.end_line - m.start_line + 1) <= 5 THEN '1-5줄'
            WHEN (m.end_line - m.start_line + 1) <= 10 THEN '6-10줄'
            WHEN (m.end_line - m.start_line + 1) <= 20 THEN '11-20줄'
            ELSE '20줄 이상'
        END as line_range,
        COUNT(*) as count
    FROM methods m
    WHERE (m.name LIKE 'get%' OR m.name LIKE 'set%' OR m.name LIKE 'is%')
    GROUP BY line_range
    ORDER BY line_range
    """
    
    cursor.execute(query2)
    results2 = cursor.fetchall()
    
    print("=== Getter/Setter 라인 수 분포 ===")
    for line_range, count in results2:
        print(f"{line_range}: {count}개")
    
    conn.close()

if __name__ == "__main__":
    check_getter_setter_length()
