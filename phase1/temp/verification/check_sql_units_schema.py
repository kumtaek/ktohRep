#!/usr/bin/env python3
"""
SQL Units 테이블 스키마 확인
"""

import sqlite3

def check_sql_units_schema():
    """SQL Units 테이블 스키마 확인"""
    
    conn = sqlite3.connect('project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(sql_units)')
    schema = cursor.fetchall()
    
    print('=== sql_units 테이블 스키마 ===')
    for row in schema:
        print(f'  {row[1]} ({row[2]})')
    
    conn.close()

if __name__ == "__main__":
    check_sql_units_schema()

