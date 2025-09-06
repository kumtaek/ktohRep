#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_chunk_schema():
    """청크 테이블 스키마 및 정보 확인"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== chunks 테이블 스키마 ===')
    cursor.execute('PRAGMA table_info(chunks)')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    print('\n=== 청크 기본 정보 ===')
    cursor.execute('SELECT COUNT(*) FROM chunks')
    chunk_count = cursor.fetchone()[0]
    print(f'총 청크 수: {chunk_count}개')
    
    print('\n=== 청크 샘플 데이터 ===')
    cursor.execute('SELECT * FROM chunks LIMIT 3')
    rows = cursor.fetchall()
    for row in rows:
        print(f'  {row}')
    
    # 파일별 청크 수 (file_id로 조인)
    print('\n=== 파일별 청크 수 ===')
    cursor.execute('''
        SELECT f.path, f.language, COUNT(c.chunk_id) as chunk_count 
        FROM files f 
        LEFT JOIN chunks c ON f.file_id = c.file_id 
        GROUP BY f.file_id, f.path, f.language 
        ORDER BY chunk_count DESC
    ''')
    file_chunks = cursor.fetchall()
    for path, language, count in file_chunks:
        print(f'{language}: {path} - {count}개 청크')
    
    conn.close()
    return chunk_count

if __name__ == '__main__':
    check_chunk_schema()
