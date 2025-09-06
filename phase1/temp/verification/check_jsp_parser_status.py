#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_jsp_parser_status():
    """JSP 파서 상태 확인"""
    print("=== JSP 파서 상태 확인 ===\n")
    
    db_path = "project/sampleSrc/metadata.db"
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. JSP 파일들 확인
            print("=== 1. JSP 파일들 ===")
            cursor.execute("SELECT file_id, path, loc FROM files WHERE language = 'jsp' ORDER BY file_id")
            jsp_files = cursor.fetchall()
            
            print(f"JSP 파일 수: {len(jsp_files)}")
            for file_id, path, loc in jsp_files:
                print(f"  ID: {file_id}, LOC: {loc}, 경로: {path}")
            
            # 2. JSP 파일별 SQL Units 확인
            print(f"\n=== 2. JSP 파일별 SQL Units ===")
            for file_id, path, loc in jsp_files:
                cursor.execute("SELECT COUNT(*) FROM sql_units WHERE file_id = ?", (file_id,))
                sql_count = cursor.fetchone()[0]
                print(f"  파일 ID: {file_id}, SQL Units: {sql_count}개")
            
            # 3. 전체 SQL Units 통계
            print(f"\n=== 3. 전체 SQL Units 통계 ===")
            cursor.execute("SELECT origin, COUNT(*) as count FROM sql_units GROUP BY origin ORDER BY count DESC")
            sql_stats = cursor.fetchall()
            
            for origin, count in sql_stats:
                print(f"  {origin}: {count}개")
            
            # 4. JSP 파일별 상세 분석
            print(f"\n=== 4. JSP 파일별 상세 분석 ===")
            for file_id, path, loc in jsp_files:
                print(f"\n파일 ID: {file_id}")
                print(f"  경로: {path}")
                print(f"  LOC: {loc}")
                
                # SQL Units 상세
                cursor.execute("SELECT stmt_id, stmt_kind, mapper_ns FROM sql_units WHERE file_id = ?", (file_id,))
                sql_units = cursor.fetchall()
                print(f"  SQL Units: {len(sql_units)}개")
                for stmt_id, stmt_kind, mapper_ns in sql_units:
                    print(f"    - {stmt_id} ({stmt_kind})")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 메타디비 조회 오류: {e}")
    else:
        print("❌ 메타디비 파일이 없습니다.")

if __name__ == "__main__":
    import os
    check_jsp_parser_status()

