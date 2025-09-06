#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_chunk_integration():
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    # 청크 통합 현황 조회
    cursor.execute('''
        SELECT target_type, target_id, COUNT(*) as chunk_count 
        FROM chunks 
        GROUP BY target_type, target_id 
        ORDER BY target_type, target_id
    ''')
    results = cursor.fetchall()
    
    print('=== 청크 통합 현황 (수작업과 동일한 방식) ===')
    
    current_type = None
    type_count = 0
    total_count = 0
    
    for row in results:
        if row[0] != current_type:
            if current_type:
                print(f'{current_type}: {type_count}개')
            type_count = 0
            current_type = row[0]
        type_count += 1
        total_count += 1
    
    if current_type:
        print(f'{current_type}: {type_count}개')
    
    print(f'총 청크: {total_count}개')
    
    # 수작업과 비교
    print('\n=== 수작업과 비교 ===')
    print('수작업 분석:')
    print('  File: 28개')
    print('  Class: 15개') 
    print('  SQL Unit: 35개')
    print('  총 청크: 78개')
    
    conn.close()

if __name__ == '__main__':
    check_chunk_integration()
