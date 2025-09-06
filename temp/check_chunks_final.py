#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_chunks_final():
    """청크 정보 최종 확인"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 청크 기본 정보 ===')
    cursor.execute('SELECT COUNT(*) FROM chunks')
    chunk_count = cursor.fetchone()[0]
    print(f'총 청크 수: {chunk_count}개')
    
    print('\n=== 타입별 청크 수 ===')
    cursor.execute('SELECT target_type, COUNT(*) FROM chunks GROUP BY target_type')
    type_chunks = cursor.fetchall()
    for target_type, count in type_chunks:
        print(f'{target_type}: {count}개 청크')
    
    print('\n=== 파일별 청크 수 (상위 10개) ===')
    cursor.execute('''
        SELECT f.path, f.language, COUNT(c.chunk_id) as chunk_count 
        FROM files f 
        LEFT JOIN chunks c ON f.file_id = c.target_id AND c.target_type = 'file'
        GROUP BY f.file_id, f.path, f.language 
        ORDER BY chunk_count DESC
        LIMIT 10
    ''')
    file_chunks = cursor.fetchall()
    for path, language, count in file_chunks:
        print(f'{language}: {path} - {count}개 청크')
    
    print('\n=== 언어별 청크 수 ===')
    cursor.execute('''
        SELECT f.language, COUNT(c.chunk_id) as chunk_count 
        FROM files f 
        LEFT JOIN chunks c ON f.file_id = c.target_id AND c.target_type = 'file'
        GROUP BY f.language 
        ORDER BY chunk_count DESC
    ''')
    lang_chunks = cursor.fetchall()
    for language, count in lang_chunks:
        print(f'{language}: {count}개 청크')
    
    conn.close()
    return chunk_count

if __name__ == '__main__':
    check_chunks_final()
