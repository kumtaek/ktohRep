#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_table_schema():
    """테이블 스키마 확인"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    # 주요 테이블의 스키마 확인
    tables = ['classes', 'methods', 'files', 'sql_units', 'db_tables', 'db_columns']
    
    for table in tables:
        print(f'\n=== {table} 테이블 스키마 ===')
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
        except Exception as e:
            print(f'  오류: {e}')
    
    # 실제 데이터 샘플 확인
    print('\n=== 데이터 샘플 ===')
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            print(f'\n{table} 테이블 샘플:')
            for row in rows:
                print(f'  {row}')
        except Exception as e:
            print(f'{table} 샘플 조회 오류: {e}')
    
    conn.close()

if __name__ == '__main__':
    check_table_schema()
