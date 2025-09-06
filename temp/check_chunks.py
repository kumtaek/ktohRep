#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_chunks():
    """청크 정보 확인"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 청크 관련 정보 ===')
    cursor.execute('SELECT COUNT(*) FROM chunks')
    chunk_count = cursor.fetchone()[0]
    print(f'총 청크 수: {chunk_count}개')
    
    print('\n=== 청크 상세 정보 ===')
    cursor.execute('SELECT file_type, COUNT(*) FROM chunks GROUP BY file_type')
    chunk_by_type = cursor.fetchall()
    for file_type, count in chunk_by_type:
        print(f'{file_type}: {count}개 청크')
    
    print('\n=== 파일별 청크 수 (상위 10개) ===')
    cursor.execute('SELECT file_path, COUNT(*) as chunk_count FROM chunks GROUP BY file_path ORDER BY chunk_count DESC LIMIT 10')
    file_chunks = cursor.fetchall()
    for file_path, count in file_chunks:
        print(f'{file_path}: {count}개 청크')
    
    print('\n=== 청크 크기 분포 ===')
    cursor.execute('SELECT LENGTH(content) as chunk_size, COUNT(*) FROM chunks GROUP BY LENGTH(content) ORDER BY chunk_size')
    size_distribution = cursor.fetchall()
    for size, count in size_distribution:
        print(f'{size}자: {count}개 청크')
    
    conn.close()
    return chunk_count

if __name__ == '__main__':
    check_chunks()
