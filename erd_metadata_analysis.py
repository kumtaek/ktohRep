#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERD 생성을 위한 메타데이터 분석 스크립트
메타데이터베이스에서 ERD 생성에 필요한 모든 정보를 조회하고 요약합니다.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

def analyze_erd_metadata():
    """ERD 생성을 위한 메타데이터를 분석합니다."""
    metadata_path = "./project/sampleSrc/metadata.db"
    
    if not os.path.exists(metadata_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {metadata_path}")
        return False
    
    print(f"✅ 메타데이터베이스 발견: {metadata_path}")
    
    try:
        conn = sqlite3.connect(metadata_path)
        cursor = conn.cursor()
        
        print(f"\n" + "=" * 80)
        print("🔍 ERD 생성을 위한 메타데이터 분석 보고서")
        print("=" * 80)
        print(f"📅 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 프로젝트: sampleSrc")
        
        # 1. 테이블 정보 분석
        print(f"\n📋 1. 테이블 정보 분석")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM db_tables")
        table_count = cursor.fetchone()[0]
        print(f"  📊 총 테이블 수: {table_count}개")
        
        if table_count > 0:
            # 테이블별 상세 정보
            cursor.execute("""
                SELECT owner, table_name, status, table_comment, llm_comment_confidence
                FROM db_tables 
                ORDER BY owner, table_name
            """)
            tables = cursor.fetchall()
            
            print(f"  🗃️ 테이블 상세 정보:")
            for table in tables:
                owner, table_name, status, comment, confidence = table
                comment_str = comment if comment else "코멘트 없음"
                confidence_str = f"{confidence:.1f}" if confidence else "0.0"
                print(f"    - {owner}.{table_name} ({status}) - {comment_str} [신뢰도: {confidence_str}]")
        
        # 2. 컬럼 정보 분석
        print(f"\n📊 2. 컬럼 정보 분석")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM db_columns")
        column_count = cursor.fetchone()[0]
        print(f"  📊 총 컬럼 수: {column_count}개")
        
        if column_count > 0:
            # 테이블별 컬럼 수
            cursor.execute("""
                SELECT t.owner, t.table_name, COUNT(c.column_name) as col_count
                FROM db_tables t
                LEFT JOIN db_columns c ON t.table_id = c.table_id
                GROUP BY t.table_id, t.owner, t.table_name
                ORDER BY t.owner, t.table_name
            """)
            table_columns = cursor.fetchall()
            
            print(f"  🗂️ 테이블별 컬럼 수:")
            for table_col in table_columns:
                owner, table_name, col_count = table_col
                print(f"    - {owner}.{table_name}: {col_count}개 컬럼")
            
            # 데이터 타입별 통계
            cursor.execute("""
                SELECT data_type, COUNT(*) as count
                FROM db_columns
                GROUP BY data_type
                ORDER BY count DESC
            """)
            data_types = cursor.fetchall()
            
            print(f"  🔤 데이터 타입별 통계:")
            for data_type, count in data_types:
                print(f"    - {data_type}: {count}개")
        
        # 3. 기본키 정보 분석
        print(f"\n🔑 3. 기본키 정보 분석")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM db_pk")
        pk_count = cursor.fetchone()[0]
        print(f"  📊 총 기본키 수: {pk_count}개")
        
        if pk_count > 0:
            # 테이블별 기본키 정보
            cursor.execute("""
                SELECT t.owner, t.table_name, p.column_name, p.pk_pos
                FROM db_pk p
                JOIN db_tables t ON p.table_id = t.table_id
                ORDER BY t.owner, t.table_name, p.pk_pos
            """)
            pks = cursor.fetchall()
            
            print(f"  🔑 테이블별 기본키:")
            for pk in pks:
                owner, table_name, column_name, position = pk
                print(f"    - {owner}.{table_name}.{column_name} (위치: {position})")
        
        # 4. 조인 관계 분석
        print(f"\n🔗 4. 조인 관계 분석")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM joins")
        join_count = cursor.fetchone()[0]
        print(f"  📊 총 조인 관계 수: {join_count}개")
        
        if join_count > 0:
            # 조인 관계 상세 정보
            cursor.execute("""
                SELECT l_table, r_table, l_col, r_col, confidence, inferred_pkfk
                FROM joins
                ORDER BY confidence DESC, l_table, r_table
            """)
            joins = cursor.fetchall()
            
            print(f"  🔗 조인 관계 상세:")
            for join in joins:
                l_table, r_table, l_col, r_col, confidence, inferred_pkfk = join
                pkfk_mark = "🔑" if inferred_pkfk else ""
                confidence_str = f"{confidence:.1f}"
                print(f"    - {l_table}.{l_col} = {r_table}.{r_col} [신뢰도: {confidence_str}] {pkfk_mark}")
        
        # 5. ERD 생성 가능성 분석
        print(f"\n🚀 5. ERD 생성 가능성 분석")
        print("-" * 60)
        
        # 테이블 간 관계 분석
        cursor.execute("""
            SELECT COUNT(DISTINCT l_table) as left_tables,
                   COUNT(DISTINCT r_table) as right_tables
            FROM joins
        """)
        join_stats = cursor.fetchone()
        left_tables, right_tables = join_stats
        
        print(f"  📊 조인 관계 통계:")
        print(f"    - 왼쪽 테이블 수: {left_tables}개")
        print(f"    - 오른쪽 테이블 수: {right_tables}개")
        
        # 외래키 추정 가능한 관계
        cursor.execute("SELECT COUNT(*) FROM joins WHERE inferred_pkfk = 1")
        fk_count = cursor.fetchone()[0]
        print(f"    - 외래키 추정 가능한 관계: {fk_count}개")
        
        # ERD 생성 가능성 평가
        if table_count >= 2 and join_count > 0:
            print(f"  ✅ ERD 생성 가능: 테이블과 관계 정보가 충분함")
            print(f"    - 테이블 수: {table_count}개 (충분)")
            print(f"    - 관계 수: {join_count}개 (충분)")
        elif table_count >= 2:
            print(f"⚠️ ERD 생성 부분 가능: 테이블은 있지만 관계 정보 부족")
            print(f"    - 테이블 수: {table_count}개 (충분)")
            print(f"    - 관계 수: {join_count}개 (부족)")
        else:
            print(f"❌ ERD 생성 불가: 테이블 정보 부족")
            print(f"    - 테이블 수: {table_count}개 (부족)")
        
        # 6. 샘플 ERD 구조 제안
        print(f"\n💡 6. 샘플 ERD 구조 제안")
        print("-" * 60)
        
        if table_count > 0:
            # 핵심 테이블 식별 (컬럼 수가 많은 테이블)
            cursor.execute("""
                SELECT t.owner, t.table_name, COUNT(c.column_name) as col_count
                FROM db_tables t
                LEFT JOIN db_columns c ON t.table_id = c.table_id
                GROUP BY t.table_id, t.owner, t.table_name
                ORDER BY col_count DESC
                LIMIT 5
            """)
            core_tables = cursor.fetchall()
            
            print(f"  🎯 핵심 테이블 (컬럼 수 기준):")
            for table in core_tables:
                owner, table_name, col_count = table
                print(f"    - {owner}.{table_name} ({col_count}개 컬럼)")
            
            # 관계 중심 테이블 식별
            if join_count > 0:
                cursor.execute("""
                    SELECT l_table, COUNT(*) as join_count
                    FROM joins
                    GROUP BY l_table
                    ORDER BY join_count DESC
                    LIMIT 3
                """)
                central_tables = cursor.fetchall()
                
                print(f"  🔗 관계 중심 테이블:")
                for table, join_count in central_tables:
                    print(f"    - {table} ({join_count}개 관계)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 메타데이터 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🔍 ERD 메타데이터 분석 시작")
    print("=" * 80)
    
    # ERD 메타데이터 분석
    success = analyze_erd_metadata()
    
    print(f"\n" + "=" * 80)
    if success:
        print("✅ ERD 메타데이터 분석 완료")
        print("📊 ERD 생성 가능성 및 구조 정보 확인 완료")
    else:
        print("❌ ERD 메타데이터 분석 실패")
    print("=" * 80)

if __name__ == "__main__":
    main()
