#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_edges():
    """엣지 데이터를 확인합니다."""
    db_path = './project/sampleSrc/metadata.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 구조 확인
    print("=== 엣지 테이블 구조 ===")
    cursor.execute("PRAGMA table_info(edges)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
    
    # 총 엣지 수
    cursor.execute("SELECT COUNT(*) FROM edges")
    total = cursor.fetchone()[0]
    print(f"\n총 엣지 수: {total}")
    
    # 실제 데이터 샘플 (NULL 값 확인)
    print("\n=== 첫 10개 엣지 데이터 ===")
    cursor.execute("SELECT * FROM edges LIMIT 10")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. edge_id={row[0]}, src_type='{row[2]}', dst_type='{row[4]}', edge_kind='{row[6]}', meta='{row[8]}'")
    
    # edge_kind 분포 (NULL 값 포함)
    print("\n=== edge_kind 분포 ===")
    cursor.execute("SELECT edge_kind, COUNT(*) FROM edges GROUP BY edge_kind")
    for row in cursor.fetchall():
        kind = row[0] if row[0] else "NULL"
        print(f"{kind}: {row[1]}개")
    
    # src_type, dst_type 분포
    print("\n=== 소스/타겟 타입 분포 ===")
    cursor.execute("SELECT src_type, dst_type, COUNT(*) FROM edges GROUP BY src_type, dst_type ORDER BY COUNT(*) DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}: {row[2]}개")
    
    conn.close()

if __name__ == "__main__":
    check_edges()