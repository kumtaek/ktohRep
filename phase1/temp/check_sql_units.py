#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_sql_units():
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()

    print('=== SQL 단위 상세 정보 ===')
    cursor.execute('SELECT stmt_id, stmt_kind, mapper_ns, origin FROM sql_units ORDER BY origin, stmt_id')
    sql_units = cursor.fetchall()
    
    for stmt_id, stmt_kind, mapper_ns, origin in sql_units:
        print(f'{origin}: {stmt_kind} - {stmt_id} ({mapper_ns})')

    print(f'\n총 SQL 단위 수: {len(sql_units)}')
    
    # origin별 SQL 단위 수
    print('\n=== Origin별 SQL 단위 수 ===')
    cursor.execute('SELECT origin, COUNT(*) as count FROM sql_units GROUP BY origin')
    origin_counts = cursor.fetchall()
    
    for origin, count in origin_counts:
        print(f'{origin}: {count}개')
    
    conn.close()

if __name__ == "__main__":
    check_sql_units()




