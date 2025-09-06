#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_metadb():
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()

    print('=== 개선된 메타디비 집계 결과 ===')

    # 파일 수 확인
    cursor.execute('SELECT COUNT(*) FROM files')
    file_count = cursor.fetchone()[0]
    print(f'파일 수: {file_count}')

    # 청크 수 확인
    cursor.execute('SELECT COUNT(*) FROM chunks')
    chunk_count = cursor.fetchone()[0]
    print(f'청크 수: {chunk_count}')

    # 에지 수 확인
    cursor.execute('SELECT COUNT(*) FROM edges')
    edge_count = cursor.fetchone()[0]
    print(f'에지 수: {edge_count}')

    # 클래스 수 확인
    cursor.execute('SELECT COUNT(*) FROM classes')
    class_count = cursor.fetchone()[0]
    print(f'클래스 수: {class_count}')

    # 메서드 수 확인
    cursor.execute('SELECT COUNT(*) FROM methods')
    method_count = cursor.fetchone()[0]
    print(f'메서드 수: {method_count}')

    # SQL 단위 수 확인
    cursor.execute('SELECT COUNT(*) FROM sql_units')
    sql_count = cursor.fetchone()[0]
    print(f'SQL 단위 수: {sql_count}')

    # DB 테이블 수 확인
    cursor.execute('SELECT COUNT(*) FROM db_tables')
    table_count = cursor.fetchone()[0]
    print(f'DB 테이블 수: {table_count}')

    # DB 컬럼 수 확인
    cursor.execute('SELECT COUNT(*) FROM db_columns')
    column_count = cursor.fetchone()[0]
    print(f'DB 컬럼 수: {column_count}')

    # 조인 수 확인
    cursor.execute('SELECT COUNT(*) FROM joins')
    join_count = cursor.fetchone()[0]
    print(f'조인 수: {join_count}')

    conn.close()

if __name__ == "__main__":
    check_metadb()





