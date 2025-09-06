#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def get_correct_metadb_counts():
    """올바른 스키마로 메타DB 건수 조회"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 메타DB 상세 건수 ===')
    
    # Java 관련
    cursor.execute('SELECT COUNT(*) FROM classes')
    java_classes = cursor.fetchone()[0]
    print(f'Java 클래스: {java_classes}개')
    
    cursor.execute('SELECT COUNT(*) FROM methods')
    java_methods = cursor.fetchone()[0]
    print(f'Java 메서드: {java_methods}개')
    
    # 파일 타입별
    cursor.execute('SELECT language, COUNT(*) FROM files GROUP BY language')
    file_types = cursor.fetchall()
    print(f'\n파일 타입별:')
    for lang, count in file_types:
        print(f'  {lang}: {count}개')
    
    # XML 관련
    cursor.execute('SELECT COUNT(*) FROM files WHERE language = "xml"')
    xml_files = cursor.fetchone()[0]
    print(f'\nXML 파일: {xml_files}개')
    
    cursor.execute('SELECT COUNT(*) FROM sql_units')
    sql_units = cursor.fetchone()[0]
    print(f'SQL Units: {sql_units}개')
    
    # JSP 관련
    cursor.execute('SELECT COUNT(*) FROM files WHERE language = "jsp"')
    jsp_files = cursor.fetchone()[0]
    print(f'JSP 파일: {jsp_files}개')
    
    # DB 관련
    cursor.execute('SELECT COUNT(*) FROM db_tables')
    db_tables = cursor.fetchone()[0]
    print(f'DB 테이블: {db_tables}개')
    
    cursor.execute('SELECT COUNT(*) FROM db_columns')
    db_columns = cursor.fetchone()[0]
    print(f'DB 컬럼: {db_columns}개')
    
    # Java 클래스 상세
    print('\n=== Java 클래스 상세 ===')
    cursor.execute('SELECT fqn FROM classes')
    java_classes_detail = cursor.fetchall()
    for (fqn,) in java_classes_detail:
        print(f'  {fqn}')
    
    # SQL Units 상세
    print('\n=== SQL Units 상세 ===')
    cursor.execute('SELECT mapper_ns, stmt_id, stmt_kind FROM sql_units')
    sql_units_detail = cursor.fetchall()
    for mapper_ns, stmt_id, stmt_kind in sql_units_detail:
        print(f'  {mapper_ns}.{stmt_id} ({stmt_kind})')
    
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
    get_correct_metadb_counts()
