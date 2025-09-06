#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_edges():
    """엣지 정보 확인"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 엣지 테이블 정보 ===')
    cursor.execute('SELECT COUNT(*) FROM edges')
    edge_count = cursor.fetchone()[0]
    print(f'총 엣지 수: {edge_count}개')
    
    if edge_count > 0:
        print('\n=== 엣지 타입별 분포 ===')
        cursor.execute('SELECT edge_kind, COUNT(*) FROM edges GROUP BY edge_kind')
        edge_types = cursor.fetchall()
        for edge_type, count in edge_types:
            print(f'{edge_type}: {count}개')
        
        print('\n=== 엣지 샘플 데이터 ===')
        cursor.execute('SELECT * FROM edges LIMIT 10')
        edges = cursor.fetchall()
        for edge in edges:
            print(f'  {edge}')
    else:
        print('엣지가 생성되지 않았습니다.')
    
    # 조인 정보도 확인
    print('\n=== 조인 정보 ===')
    cursor.execute('SELECT COUNT(*) FROM joins')
    join_count = cursor.fetchone()[0]
    print(f'총 조인 수: {join_count}개')
    
    if join_count > 0:
        cursor.execute('SELECT * FROM joins LIMIT 5')
        joins = cursor.fetchall()
        for join in joins:
            print(f'  {join}')
    
    conn.close()
    return edge_count, join_count

if __name__ == '__main__':
    check_edges()
