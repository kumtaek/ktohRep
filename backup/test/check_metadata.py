#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메타데이터베이스 상태 점검 스크립트
ERD 관련 메타데이터 생성 현황을 분석합니다.
"""

import sqlite3
import os
from pathlib import Path

def check_metadata_database():
    """메타데이터베이스의 상태를 점검합니다."""
    # 설정 파일에서 프로젝트명을 동적으로 읽기
    import yaml
    import os
    
    # 설정 파일 경로 (새로운 폴더 구조)
    config_path = "./phase1/config/config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 필수 설정값 확인
    if not config:
        raise ValueError("설정 파일이 비어있거나 잘못되었습니다")
    
    database_config = config.get('database')
    if not database_config:
        raise ValueError("설정 파일에 database 섹션이 없습니다")
    
    default_schema = database_config.get('default_schema')
    if not default_schema:
        raise ValueError("설정 파일에 default_schema가 설정되지 않았습니다")
    
    project_name = 'sampleSrc'  # Phase1은 sampleSrc 프로젝트 전용
    
    metadata_path = f"./project/{project_name}/metadata.db"
    
    if not os.path.exists(metadata_path):
        print(f"❌ 메타데이터베이스가 존재하지 않습니다: {metadata_path}")
        return False
    
    print(f"✅ 메타데이터베이스 발견: {metadata_path}")
    
    try:
        conn = sqlite3.connect(metadata_path)
        cursor = conn.cursor()
        
        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # ERD 관련 테이블들 확인
        erd_tables = ['Table', 'Column', 'ForeignKey', 'Index']
        print(f"\n🔍 ERD 관련 테이블 상태:")
        
        for table_name in erd_tables:
            if table_name in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table_name}: {count}개 레코드")
            else:
                print(f"  ❌ {table_name}: 테이블 없음")
        
        # 테이블 구조 상세 분석
        print(f"\n📊 주요 테이블 상세 분석:")
        
        for table_name in ['Table', 'Column', 'ForeignKey']:
            if table_name in [t[0] for t in tables]:
                print(f"\n  📋 {table_name} 테이블:")
                
                # 컬럼 정보
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                for col in columns:
                    col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                    pk_mark = " 🔑" if pk else ""
                    print(f"    - {col_name}: {col_type}{pk_mark}")
                
                # 샘플 데이터
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                if sample_data:
                    print(f"    📝 샘플 데이터 ({len(sample_data)}개):")
                    for i, row in enumerate(sample_data):
                        print(f"      {i+1}. {row}")
        
        # 프로젝트 정보 확인
        if 'Project' in [t[0] for t in tables]:
            print(f"\n🏗️ 프로젝트 정보:")
            cursor.execute("SELECT * FROM Project")
            projects = cursor.fetchall()
            for project in projects:
                print(f"  - {project}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 메타데이터베이스 점검 중 오류 발생: {e}")
        return False

def check_erd_generation_files():
    """ERD 생성 관련 파일들을 확인합니다."""
    print(f"\n🔍 ERD 생성 관련 파일 확인:")
    
    # visualize 폴더 확인
    visualize_path = Path("./visualize")
    if visualize_path.exists():
        print(f"  ✅ visualize 폴더 존재")
        
        # ERD 관련 Python 파일들
        erd_files = list(visualize_path.glob("**/*erd*.py"))
        if erd_files:
            print(f"  📝 ERD 관련 Python 파일들:")
            for file in erd_files:
                print(f"    - {file}")
        else:
            print(f"  ❌ ERD 관련 Python 파일 없음")
        
        # 설정 파일
        config_files = list(visualize_path.glob("**/config*.yaml"))
        if config_files:
            print(f"  ⚙️ 설정 파일들:")
            for file in config_files:
                print(f"      {file}")
    else:
        print(f"  ❌ visualize 폴더 없음")
    
    # 출력 폴더 확인 (sampleSrc 프로젝트)
    project_name = "sampleSrc"
    output_path = Path(f"./project/{project_name}/report")
    if output_path.exists():
        print(f"  ✅ 출력 폴더 존재: {output_path}")
        
        # 생성된 ERD 파일들
        erd_output_files = list(output_path.glob("**/*erd*.html"))
        if erd_output_files:
            print(f"  📊 생성된 ERD 파일들:")
            for file in erd_output_files:
                print(f"      {file}")
        else:
            print(f"  ❌ 생성된 ERD 파일 없음")
    else:
        print(f"  ❌ 출력 폴더 없음")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🔍 ERD 메타데이터 현황 분석")
    print("=" * 60)
    
    # 메타데이터베이스 점검
    db_ok = check_metadata_database()
    
    # ERD 생성 파일들 점검
    check_erd_generation_files()
    
    print(f"\n" + "=" * 60)
    if db_ok:
        print("✅ 메타데이터베이스 점검 완료")
    else:
        print("❌ 메타데이터베이스 점검 실패")
    print("=" * 60)

if __name__ == "__main__":
    main()
