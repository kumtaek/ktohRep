#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 스키마 데이터 현황 점검 스크립트
db_tables, db_columns, db_pk, joins 테이블의 데이터 상태를 확인합니다.
"""

import sqlite3
import os
from pathlib import Path

def check_db_schema_data():
    """DB 스키마 관련 테이블들의 데이터 현황을 점검합니다."""
    metadata_path = "./project/sampleSrc/metadata.db"
    
    if not os.path.exists(metadata_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {metadata_path}")
        return False
    
    print(f"✅ 메타데이터베이스 발견: {metadata_path}")
    
    try:
        conn = sqlite3.connect(metadata_path)
        cursor = conn.cursor()
        
        # DB 스키마 관련 테이블들
        schema_tables = ['db_tables', 'db_columns', 'db_pk', 'joins']
        
        print(f"\n🔍 DB 스키마 테이블 데이터 현황:")
        print("=" * 60)
        
        for table_name in schema_tables:
            print(f"\n📋 {table_name} 테이블:")
            
            # 테이블 존재 여부 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                print(f"  ❌ 테이블이 존재하지 않음")
                continue
            
            # 레코드 수 확인
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📊 총 레코드 수: {count}개")
            
            if count == 0:
                print(f"  ⚠️ 데이터가 없음")
                continue
            
            # 테이블 구조 확인
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"  🏗️ 테이블 구조:")
            for col in columns:
                col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                pk_mark = " 🔑" if pk else ""
                print(f"    - {col_name}: {col_type}{pk_mark}")
            
            # 샘플 데이터 (최대 5개)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = cursor.fetchall()
            if sample_data:
                print(f"  📝 샘플 데이터:")
                for i, row in enumerate(sample_data):
                    print(f"    {i+1}. {row}")
            
            # 전체 데이터 요약 (테이블별로)
            if table_name == 'db_tables':
                cursor.execute("SELECT table_name, owner, status FROM db_tables LIMIT 10")
                tables = cursor.fetchall()
                if tables:
                    print(f"  🗃️ 테이블 목록 (최대 10개):")
                    for table in tables:
                        print(f"    - {table}")
            
            elif table_name == 'db_columns':
                cursor.execute("SELECT table_id, column_name, data_type, nullable FROM db_columns LIMIT 10")
                columns = cursor.fetchall()
                if columns:
                    print(f"  📊 컬럼 목록 (최대 10개):")
                    for col in columns:
                        print(f"    - {col}")
            
            elif table_name == 'db_pk':
                cursor.execute("SELECT table_id, column_name FROM db_pk LIMIT 10")
                pks = cursor.fetchall()
                if pks:
                    print(f"  🔑 기본키 목록 (최대 10개):")
                    for pk in pks:
                        print(f"    - {pk}")
            
            elif table_name == 'joins':
                cursor.execute("SELECT l_table, r_table, l_col, r_col, confidence FROM joins LIMIT 10")
                joins = cursor.fetchall()
                if joins:
                    print(f"  🔗 조인 관계 목록 (최대 10개):")
                    for join in joins:
                        print(f"    - {join}")
        
        # CSV 파일 존재 여부 확인
        print(f"\n📁 CSV 파일 현황:")
        print("=" * 60)
        
        db_schema_path = Path("./project/sampleSrc/DB_SCHEMA")
        if db_schema_path.exists():
            print(f"  ✅ DB_SCHEMA 폴더 존재: {db_schema_path}")
            
            csv_files = list(db_schema_path.glob("*.csv"))
            if csv_files:
                print(f"  📊 CSV 파일들 ({len(csv_files)}개):")
                for csv_file in csv_files:
                    file_size = csv_file.stat().st_size
                    print(f"    - {csv_file.name} ({file_size} bytes)")
                    
                    # CSV 파일 내용 미리보기 (첫 3줄)
                    try:
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[:3]
                            print(f"      📝 내용 미리보기:")
                            for i, line in enumerate(lines):
                                print(f"        {i+1}: {line.strip()}")
                    except Exception as e:
                        print(f"      ❌ 파일 읽기 오류: {e}")
            else:
                print(f"  ❌ CSV 파일 없음")
        else:
            print(f"  ❌ DB_SCHEMA 폴더 없음")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ DB 스키마 데이터 점검 중 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🔍 DB 스키마 데이터 현황 분석")
    print("=" * 60)
    
    # DB 스키마 데이터 점검
    success = check_db_schema_data()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ DB 스키마 데이터 점검 완료")
    else:
        print("❌ DB 스키마 데이터 점검 실패")
    print("=" * 60)

if __name__ == "__main__":
    main()
