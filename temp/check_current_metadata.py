#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime

def check_metadata_counts():
    """메타DB에서 청크와 엣지 건수를 확인합니다."""
    
    db_path = "./project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print(f"메타DB 파일이 존재하지 않습니다: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("메타DB 청크 및 엣지 현황 조회")
        print("=" * 60)
        print(f"조회일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"DB 경로: {db_path}")
        print()
        
        # 1. 청크 현황
        print("청크 현황")
        print("-" * 30)
        
        # 전체 청크 수
        cursor.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cursor.fetchone()[0]
        print(f"총 청크 수: {total_chunks:,}개")
        
        # 청크 유형별 분포
        cursor.execute("""
            SELECT target_type, COUNT(*) as count
            FROM chunks 
            GROUP BY target_type 
            ORDER BY count DESC
        """)
        chunk_types = cursor.fetchall()
        
        print("\n청크 유형별 분포:")
        for chunk_type, count in chunk_types:
            print(f"  - {chunk_type}: {count:,}개")
        
        # 2. 엣지 현황
        print("\n엣지 현황")
        print("-" * 30)
        
        # 전체 엣지 수
        cursor.execute("SELECT COUNT(*) FROM edges")
        total_edges = cursor.fetchone()[0]
        print(f"총 엣지 수: {total_edges:,}개")
        
        # 엣지 유형별 분포
        cursor.execute("""
            SELECT edge_kind, COUNT(*) as count
            FROM edges 
            GROUP BY edge_kind 
            ORDER BY count DESC
        """)
        edge_types = cursor.fetchall()
        
        print("\n엣지 유형별 분포:")
        for edge_type, count in edge_types:
            print(f"  - {edge_type}: {count:,}개")
        
        # 3. 기타 메타데이터 현황
        print("\n기타 메타데이터 현황")
        print("-" * 30)
        
        # 파일 수
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        print(f"총 파일 수: {total_files:,}개")
        
        # 클래스 수
        cursor.execute("SELECT COUNT(*) FROM classes")
        total_classes = cursor.fetchone()[0]
        print(f"총 클래스 수: {total_classes:,}개")
        
        # 메서드 수
        cursor.execute("SELECT COUNT(*) FROM methods")
        total_methods = cursor.fetchone()[0]
        print(f"총 메서드 수: {total_methods:,}개")
        
        # SQL Unit 수
        cursor.execute("SELECT COUNT(*) FROM sql_units")
        total_sql_units = cursor.fetchone()[0]
        print(f"총 SQL Unit 수: {total_sql_units:,}개")
        
        # DB 테이블 수
        cursor.execute("SELECT COUNT(*) FROM db_tables")
        total_db_tables = cursor.fetchone()[0]
        print(f"총 DB 테이블 수: {total_db_tables:,}개")
        
        # 4. 파일 유형별 분포
        print("\n파일 유형별 분포")
        print("-" * 30)
        
        cursor.execute("""
            SELECT language, COUNT(*) as count
            FROM files 
            GROUP BY language 
            ORDER BY count DESC
        """)
        file_types = cursor.fetchall()
        
        for file_type, count in file_types:
            print(f"  - {file_type}: {count:,}개")
        
        # 5. 엣지 샘플 데이터
        print("\n엣지 샘플 데이터 (최대 5개)")
        print("-" * 30)
        
        cursor.execute("""
            SELECT src_type, src_id, dst_type, dst_id, edge_kind, meta
            FROM edges 
            LIMIT 5
        """)
        edge_samples = cursor.fetchall()
        
        for i, (src_type, src_id, dst_type, dst_id, edge_kind, meta) in enumerate(edge_samples, 1):
            print(f"{i}. {src_type}({src_id}) → {dst_type}({dst_id}) [{edge_kind}]")
            if meta:
                print(f"   메타: {meta[:100]}...")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("메타DB 조회 완료")
        print("=" * 60)
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_metadata_counts()
