#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def get_metadb_detailed_counts():
    """메타DB 상세 건수 조회"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 메타DB 상세 건수 ===')
    
    # Java 관련
    cursor.execute('SELECT COUNT(*) FROM classes WHERE file_type = "java"')
    java_classes = cursor.fetchone()[0]
    print(f'Java 클래스: {java_classes}개')
    
    cursor.execute('SELECT COUNT(*) FROM methods WHERE file_type = "java"')
    java_methods = cursor.fetchone()[0]
    print(f'Java 메서드: {java_methods}개')
    
    # XML 관련
    cursor.execute('SELECT COUNT(*) FROM files WHERE file_type = "xml"')
    xml_files = cursor.fetchone()[0]
    print(f'XML 파일: {xml_files}개')
    
    cursor.execute('SELECT COUNT(*) FROM sql_units')
    sql_units = cursor.fetchone()[0]
    print(f'SQL Units: {sql_units}개')
    
    # JSP 관련
    cursor.execute('SELECT COUNT(*) FROM files WHERE file_type = "jsp"')
    jsp_files = cursor.fetchone()[0]
    print(f'JSP 파일: {jsp_files}개')
    
    # DB 관련
    cursor.execute('SELECT COUNT(*) FROM db_tables')
    db_tables = cursor.fetchone()[0]
    print(f'DB 테이블: {db_tables}개')
    
    cursor.execute('SELECT COUNT(*) FROM db_columns')
    db_columns = cursor.fetchone()[0]
    print(f'DB 컬럼: {db_columns}개')
    
    # 파일 타입별 상세
    print('\n=== 파일 타입별 상세 ===')
    cursor.execute('SELECT file_type, COUNT(*) FROM files GROUP BY file_type')
    file_types = cursor.fetchall()
    for file_type, count in file_types:
        print(f'{file_type}: {count}개')
    
    # Java 클래스 상세
    print('\n=== Java 클래스 상세 ===')
    cursor.execute('SELECT package_name, class_name FROM classes WHERE file_type = "java"')
    java_classes_detail = cursor.fetchall()
    for pkg, cls in java_classes_detail:
        print(f'  {pkg}.{cls}')
    
    # SQL Units 상세
    print('\n=== SQL Units 상세 ===')
    cursor.execute('SELECT file_name, query_type, COUNT(*) FROM sql_units GROUP BY file_name, query_type')
    sql_units_detail = cursor.fetchall()
    for file_name, query_type, count in sql_units_detail:
        print(f'  {file_name} ({query_type}): {count}개')
    
    conn.close()
    
    return {
        'java_classes': java_classes,
        'java_methods': java_methods,
        'xml_files': xml_files,
        'sql_units': sql_units,
        'jsp_files': jsp_files,
        'db_tables': db_tables,
        'db_columns': db_columns
    }

if __name__ == '__main__':
    get_metadb_detailed_counts()
