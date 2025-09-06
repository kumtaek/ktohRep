#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb_counts():
    """메타DB 건수 조회"""
    
    # 메타DB 연결
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print('메타DB 파일이 존재하지 않습니다.')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블별 건수 조회
    tables = ['java_files', 'java_classes', 'java_methods', 'java_fields', 'java_annotations', 
              'xml_files', 'xml_queries', 'xml_dynamic_elements', 'xml_joins',
              'jsp_files', 'jsp_tags', 'jsp_errors']
    
    print('=== 메타DB 건수 조회 ===')
    metadb_counts = {}
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            metadb_counts[table] = count
            print(f'{table}: {count}건')
        except Exception as e:
            print(f'{table}: 테이블 없음 또는 오류 - {e}')
            metadb_counts[table] = 0
    
    # 추가 상세 조회
    print('\n=== 상세 조회 ===')
    
    # Java 클래스별 상세
    try:
        cursor.execute('SELECT package_name, class_name FROM java_classes')
        java_classes = cursor.fetchall()
        print(f'Java 클래스 상세 ({len(java_classes)}개):')
        for pkg, cls in java_classes:
            print(f'  {pkg}.{cls}')
    except Exception as e:
        print(f'Java 클래스 조회 오류: {e}')
    
    # XML 파일별 쿼리 수
    try:
        cursor.execute('SELECT file_name, COUNT(*) as query_count FROM xml_queries GROUP BY file_name')
        xml_queries = cursor.fetchall()
        print(f'\nXML 파일별 쿼리 수:')
        for file_name, count in xml_queries:
            print(f'  {file_name}: {count}개 쿼리')
    except Exception as e:
        print(f'XML 쿼리 조회 오류: {e}')
    
    # JSP 파일별 태그 수
    try:
        cursor.execute('SELECT file_name, COUNT(*) as tag_count FROM jsp_tags GROUP BY file_name')
        jsp_tags = cursor.fetchall()
        print(f'\nJSP 파일별 태그 수:')
        for file_name, count in jsp_tags:
            print(f'  {file_name}: {count}개 태그')
    except Exception as e:
        print(f'JSP 태그 조회 오류: {e}')
    
    conn.close()
    return metadb_counts

if __name__ == '__main__':
    check_metadb_counts()
