#!/usr/bin/env python3
"""
중복 제거 파서 - 정확한 메타디비 생성
"""

import os
import sqlite3
import csv
from pathlib import Path
from datetime import datetime

def create_metadata_db(project_path: str):
    """메타디비 생성"""
    db_path = os.path.join(project_path, "metadata.db")
    
    # 기존 DB 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"기존 메타디비 삭제: {db_path}")
    
    # SQLite 데이터베이스 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS db_tables (
            table_id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner VARCHAR(128),
            table_name VARCHAR(128) NOT NULL,
            status VARCHAR(50),
            table_comment TEXT,
            llm_comment TEXT,
            llm_comment_confidence FLOAT,
            created_at DATETIME,
            updated_at DATETIME,
            UNIQUE(owner, table_name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS db_columns (
            column_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            column_name VARCHAR(128) NOT NULL,
            data_type VARCHAR(128),
            nullable VARCHAR(1),
            column_comment TEXT,
            llm_comment TEXT,
            llm_comment_confidence FLOAT,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(table_id) REFERENCES db_tables (table_id),
            UNIQUE(table_id, column_name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS db_pk (
            table_id INTEGER NOT NULL,
            column_name VARCHAR(128) NOT NULL,
            pk_pos INTEGER,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (table_id, column_name),
            FOREIGN KEY(table_id) REFERENCES db_tables (table_id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

def parse_csv_files(project_path: str, conn, cursor):
    """CSV 파일 파싱"""
    db_schema_path = os.path.join(project_path, "db_schema")
    
    if not os.path.exists(db_schema_path):
        print(f"DB_SCHEMA 폴더가 없습니다: {db_schema_path}")
        return
    
    # 테이블 정보 파싱
    tables_csv = os.path.join(db_schema_path, "ALL_TABLES.csv")
    if os.path.exists(tables_csv):
        print(f"테이블 정보 파싱 중: {tables_csv}")
        parse_tables_csv(tables_csv, conn, cursor)
    
    # 컬럼 정보 파싱
    columns_csv = os.path.join(db_schema_path, "ALL_TAB_COLUMNS.csv")
    if os.path.exists(columns_csv):
        print(f"컬럼 정보 파싱 중: {columns_csv}")
        parse_columns_csv(columns_csv, conn, cursor)
    
    # PK 정보 파싱
    pk_csv = os.path.join(db_schema_path, "PK_INFO.csv")
    if os.path.exists(pk_csv):
        print(f"PK 정보 파싱 중: {pk_csv}")
        parse_pk_csv(pk_csv, conn, cursor)

def parse_tables_csv(csv_path: str, conn, cursor):
    """테이블 CSV 파싱 - 중복 제거"""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # 중복 제거를 위한 집합
        unique_tables = set()
        inserted_count = 0
        
        for row in reader:
            owner = row.get('OWNER', '').strip()
            table_name = row.get('TABLE_NAME', '').strip()
            comments = (row.get('COMMENTS') or '').strip()
            status = (row.get('STATUS') or 'VALID').strip()
            
            table_key = f"{owner}.{table_name}"
            
            if table_key not in unique_tables:
                try:
                    cursor.execute('''
                        INSERT INTO db_tables (owner, table_name, status, table_comment, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (owner, table_name, status, comments, datetime.now(), datetime.now()))
                    
                    unique_tables.add(table_key)
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    print(f"테이블 중복 무시: {table_key}")
        
        print(f"고유 테이블 수: {len(unique_tables)}")
        print(f"삽입된 테이블 수: {inserted_count}")
    
    conn.commit()
    print(f"테이블 정보 저장 완료")

def parse_columns_csv(csv_path: str, conn, cursor):
    """컬럼 CSV 파싱 - 중복 제거"""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        print(f"CSV에서 읽은 총 행 수: {len(rows)}")
        
        # 중복 제거를 위한 집합
        unique_columns = set()
        processed_count = 0
        skipped_count = 0
        
        for i, row in enumerate(rows):
            owner = row.get('OWNER', '').strip()
            table_name = row.get('TABLE_NAME', '').strip()
            column_name = row.get('COLUMN_NAME', '').strip()
            data_type = row.get('DATA_TYPE', '').strip()
            nullable = row.get('NULLABLE', 'Y').strip()
            comments = (row.get('COLUMN_COMMENTS') or '').strip()
            
            # 디버깅: 처음 몇 개 행 출력
            if i < 5:
                print(f"행 {i+1}: {owner}.{table_name}.{column_name} ({data_type})")
            
            # 테이블 ID 조회
            cursor.execute('''
                SELECT table_id FROM db_tables 
                WHERE owner = ? AND table_name = ?
            ''', (owner, table_name))
            
            table_result = cursor.fetchone()
            if table_result:
                table_id = table_result[0]
                column_key = f"{table_id}.{column_name}"
                
                if column_key not in unique_columns:
                    try:
                        cursor.execute('''
                            INSERT INTO db_columns (table_id, column_name, data_type, nullable, column_comment, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (table_id, column_name, data_type, nullable, comments, datetime.now(), datetime.now()))
                        
                        unique_columns.add(column_key)
                        processed_count += 1
                    except sqlite3.IntegrityError:
                        print(f"컬럼 중복 무시: {owner}.{table_name}.{column_name}")
                        skipped_count += 1
                else:
                    print(f"중복 컬럼 건너뜀: {owner}.{table_name}.{column_name}")
                    skipped_count += 1
            else:
                print(f"경고: 테이블을 찾을 수 없음 - {owner}.{table_name}")
                skipped_count += 1
        
        print(f"고유 컬럼 수: {len(unique_columns)}")
        print(f"처리된 컬럼 수: {processed_count}")
        print(f"건너뛴 컬럼 수: {skipped_count}")
    
    conn.commit()
    print(f"컬럼 정보 저장 완료")

def parse_pk_csv(csv_path: str, conn, cursor):
    """PK CSV 파싱"""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            owner = row.get('OWNER', '').strip()
            table_name = row.get('TABLE_NAME', '').strip()
            column_name = row.get('COLUMN_NAME', '').strip()
            pk_pos = row.get('POSITION', '1').strip()
            
            # 테이블 ID 조회
            cursor.execute('''
                SELECT table_id FROM db_tables 
                WHERE owner = ? AND table_name = ?
            ''', (owner, table_name))
            
            table_result = cursor.fetchone()
            if table_result:
                table_id = table_result[0]
                
                cursor.execute('''
                    INSERT INTO db_pk (table_id, column_name, pk_pos, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (table_id, column_name, pk_pos, datetime.now(), datetime.now()))
    
    conn.commit()
    print(f"PK 정보 저장 완료")

def main():
    """메인 함수"""
    project_path = "../project/sampleSrc"
    
    print(f"프로젝트 경로: {project_path}")
    print("중복 제거 메타디비 생성 시작...")
    
    # 메타디비 생성
    conn, cursor = create_metadata_db(project_path)
    
    # CSV 파일 파싱
    parse_csv_files(project_path, conn, cursor)
    
    # 결과 확인
    cursor.execute("SELECT COUNT(*) FROM db_tables")
    table_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM db_columns")
    column_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM db_pk")
    pk_count = cursor.fetchone()[0]
    
    print(f"\n=== 파싱 결과 ===")
    print(f"테이블 수: {table_count}")
    print(f"컬럼 수: {column_count}")
    print(f"PK 수: {pk_count}")
    
    # 상세 정보 출력
    print(f"\n=== 테이블 상세 정보 ===")
    cursor.execute('''
        SELECT owner, table_name, status FROM db_tables 
        ORDER BY owner, table_name
    ''')
    
    for row in cursor.fetchall():
        print(f"{row[0]}.{row[1]} ({row[2]})")
    
    conn.close()
    print(f"\n중복 제거 메타디비 생성 완료: {os.path.join(project_path, 'metadata.db')}")

if __name__ == "__main__":
    main()
