#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def get_simple_metadb_counts():
    """메타DB 간단 건수 조회"""
    
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print('=== 메타DB 건수 ===')
    
    # 기본 건수들
    cursor.execute('SELECT COUNT(*) FROM classes')
    java_classes = cursor.fetchone()[0]
    print(f'Java 클래스: {java_classes}개')
    
    cursor.execute('SELECT COUNT(*) FROM methods')
    java_methods = cursor.fetchone()[0]
    print(f'Java 메서드: {java_methods}개')
    
    cursor.execute('SELECT COUNT(*) FROM files WHERE language = "java"')
    java_files = cursor.fetchone()[0]
    print(f'Java 파일: {java_files}개')
    
    cursor.execute('SELECT COUNT(*) FROM files WHERE language = "xml"')
    xml_files = cursor.fetchone()[0]
    print(f'XML 파일: {xml_files}개')
    
    cursor.execute('SELECT COUNT(*) FROM sql_units')
    sql_units = cursor.fetchone()[0]
    print(f'SQL Units: {sql_units}개')
    
    cursor.execute('SELECT COUNT(*) FROM files WHERE language = "jsp"')
    jsp_files = cursor.fetchone()[0]
    print(f'JSP 파일: {jsp_files}개')
    
    cursor.execute('SELECT COUNT(*) FROM db_tables')
    db_tables = cursor.fetchone()[0]
    print(f'DB 테이블: {db_tables}개')
    
    cursor.execute('SELECT COUNT(*) FROM db_columns')
    db_columns = cursor.fetchone()[0]
    print(f'DB 컬럼: {db_columns}개')
    
    conn.close()
    
    return {
        'java_classes': java_classes,
        'java_methods': java_methods,
        'java_files': java_files,
        'xml_files': xml_files,
        'sql_units': sql_units,
        'jsp_files': jsp_files,
        'db_tables': db_tables,
        'db_columns': db_columns
    }

if __name__ == '__main__':
    get_simple_metadb_counts()
