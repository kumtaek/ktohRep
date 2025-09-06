#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb_schema():
    """메타DB 스키마 및 건수 조회"""
    
    # 메타DB 연결
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print('메타DB 파일이 존재하지 않습니다.')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print('=== 메타DB 테이블 목록 ===')
    for table in tables:
        print(f'  {table[0]}')
    
    print('\n=== 테이블별 건수 조회 ===')
    metadb_counts = {}
    
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            metadb_counts[table_name] = count
            print(f'{table_name}: {count}건')
        except Exception as e:
            print(f'{table_name}: 오류 - {e}')
            metadb_counts[table_name] = 0
    
    # 주요 테이블 상세 조회
    print('\n=== 주요 테이블 상세 조회 ===')
    
    # files 테이블
    try:
        cursor.execute('SELECT file_path, file_type FROM files')
        files = cursor.fetchall()
        print(f'Files 테이블 ({len(files)}개):')
        for file_path, file_type in files:
            print(f'  {file_type}: {file_path}')
    except Exception as e:
        print(f'Files 테이블 조회 오류: {e}')
    
    # classes 테이블
    try:
        cursor.execute('SELECT package_name, class_name FROM classes')
        classes = cursor.fetchall()
        print(f'\nClasses 테이블 ({len(classes)}개):')
        for pkg, cls in classes:
            print(f'  {pkg}.{cls}')
    except Exception as e:
        print(f'Classes 테이블 조회 오류: {e}')
    
    # methods 테이블
    try:
        cursor.execute('SELECT class_name, method_name FROM methods')
        methods = cursor.fetchall()
        print(f'\nMethods 테이블 ({len(methods)}개):')
        for cls, method in methods[:10]:  # 처음 10개만 출력
            print(f'  {cls}.{method}')
        if len(methods) > 10:
            print(f'  ... 외 {len(methods) - 10}개')
    except Exception as e:
        print(f'Methods 테이블 조회 오류: {e}')
    
    # sql_units 테이블
    try:
        cursor.execute('SELECT file_name, query_type FROM sql_units')
        sql_units = cursor.fetchall()
        print(f'\nSQL Units 테이블 ({len(sql_units)}개):')
        for file_name, query_type in sql_units:
            print(f'  {query_type}: {file_name}')
    except Exception as e:
        print(f'SQL Units 테이블 조회 오류: {e}')
    
    # db_tables 테이블
    try:
        cursor.execute('SELECT table_name, owner FROM db_tables')
        db_tables = cursor.fetchall()
        print(f'\nDB Tables 테이블 ({len(db_tables)}개):')
        for table_name, owner in db_tables:
            print(f'  {owner}.{table_name}')
    except Exception as e:
        print(f'DB Tables 테이블 조회 오류: {e}')
    
    conn.close()
    return metadb_counts

if __name__ == '__main__':
    check_metadb_schema()
