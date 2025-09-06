#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
청크 과대 생성 원인 분석 스크립트
"""

import os
import sqlite3
import re
from pathlib import Path

def analyze_chunks(project_name):
    """메타디비에서 청크 생성 현황 분석"""
    db_paths = [
        f"./project/{project_name}/metadata.db",
        f"./phase1/project/{project_name}/metadata.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if db_path is None:
        print(f"ERROR: 메타디비 파일을 찾을 수 없습니다. 시도한 경로: {db_paths}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"메타디비 경로: {db_path}")
        print("="*80)
        
        # 전체 청크 수
        cursor.execute("SELECT COUNT(*) FROM chunks;")
        total_chunks = cursor.fetchone()[0]
        print(f"전체 청크 수: {total_chunks:,}개")
        
        # 파일별 청크 수
        print("\n[파일별 청크 수]")
        cursor.execute("""
            SELECT f.path, COUNT(c.chunk_id) as chunk_count
            FROM files f
            LEFT JOIN chunks c ON f.file_id = c.target_id AND c.target_type = 'file'
            GROUP BY f.file_id, f.path
            ORDER BY chunk_count DESC
            LIMIT 20
        """)
        
        file_chunks = cursor.fetchall()
        for file_path, chunk_count in file_chunks:
            print(f"  {file_path}: {chunk_count:,}개")
        
        # 청크 타입별 분석
        print("\n[청크 타입별 분석]")
        cursor.execute("SELECT target_type, COUNT(*) FROM chunks GROUP BY target_type ORDER BY COUNT(*) DESC;")
        chunk_types = cursor.fetchall()
        for target_type, count in chunk_types:
            print(f"  {target_type}: {count:,}개")
        
        # 파일 타입별 청크 수
        print("\n[파일 타입별 청크 수]")
        cursor.execute("""
            SELECT f.language, COUNT(c.chunk_id) as chunk_count
            FROM files f
            LEFT JOIN chunks c ON f.file_id = c.target_id AND c.target_type = 'file'
            GROUP BY f.language
            ORDER BY chunk_count DESC
        """)
        
        lang_chunks = cursor.fetchall()
        for language, chunk_count in lang_chunks:
            print(f"  {language}: {chunk_count:,}개")
        
        # 가장 많은 청크를 가진 파일 상세 분석
        if file_chunks:
            top_file = file_chunks[0]
            print(f"\n[최대 청크 파일 상세 분석: {top_file[0]}]")
            
            cursor.execute("""
                SELECT c.target_type, LENGTH(c.content), c.content
                FROM chunks c
                JOIN files f ON c.target_id = f.file_id AND c.target_type = 'file'
                WHERE f.path = ?
                ORDER BY c.chunk_id
                LIMIT 10
            """, (top_file[0],))
            
            chunks_detail = cursor.fetchall()
            for i, (chunk_type, content_length, content) in enumerate(chunks_detail, 1):
                print(f"  청크 {i}: 타입={chunk_type}, 길이={content_length}")
                if content:
                    preview = content[:100].replace('\n', '\\n')
                    print(f"    내용 미리보기: {preview}...")
        
        # 청크 크기 분포
        print("\n[청크 크기 분포]")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN LENGTH(content) < 100 THEN '0-99'
                    WHEN LENGTH(content) < 500 THEN '100-499'
                    WHEN LENGTH(content) < 1000 THEN '500-999'
                    WHEN LENGTH(content) < 2000 THEN '1000-1999'
                    ELSE '2000+'
                END as size_range,
                COUNT(*) as count
            FROM chunks
            GROUP BY size_range
            ORDER BY 
                CASE 
                    WHEN LENGTH(content) < 100 THEN 1
                    WHEN LENGTH(content) < 500 THEN 2
                    WHEN LENGTH(content) < 1000 THEN 3
                    WHEN LENGTH(content) < 2000 THEN 4
                    ELSE 5
                END
        """)
        
        size_dist = cursor.fetchall()
        for size_range, count in size_dist:
            print(f"  {size_range}자: {count:,}개")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: 청크 분석 중 오류 발생: {e}")

def main():
    project_name = "sampleSrc"
    print("청크 과대 생성 원인 분석 시작...")
    analyze_chunks(project_name)

if __name__ == "__main__":
    main()
