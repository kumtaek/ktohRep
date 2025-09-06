#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메타데이터베이스 스키마 업그레이드 스크립트 (SQLite 호환)
DbTable과 DbColumn 테이블에 created_at, updated_at 컬럼을 추가합니다.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def upgrade_db_schema():
    """메타데이터베이스 스키마를 업그레이드합니다."""
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
        
        print("🔍 현재 스키마 확인 중...")
        
        # 현재 db_tables 스키마 확인
        cursor.execute("PRAGMA table_info(db_tables)")
        table_columns = cursor.fetchall()
        column_names = [col[1] for col in table_columns]
        
        print(f"  📊 현재 db_tables 컬럼: {', '.join(column_names)}")
        
        # created_at 컬럼 추가
        if 'created_at' not in column_names:
            print("🔧 created_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_tables 
                ADD COLUMN created_at DATETIME
            """)
            print("  ✅ created_at 컬럼 추가 완료")
        else:
            print("  ℹ️ created_at 컬럼이 이미 존재합니다")
        
        # updated_at 컬럼 추가
        if 'updated_at' not in column_names:
            print("🔧 updated_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_tables 
                ADD COLUMN updated_at DATETIME
            """)
            print("  ✅ updated_at 컬럼 추가 완료")
        else:
            print("  ℹ️ updated_at 컬럼이 이미 존재합니다")
        
        # 현재 db_columns 스키마 확인
        cursor.execute("PRAGMA table_info(db_columns)")
        column_table_columns = cursor.fetchall()
        column_table_names = [col[1] for col in column_table_columns]
        
        print(f"  📊 현재 db_columns 컬럼: {', '.join(column_table_names)}")
        
        # db_columns에도 created_at, updated_at 컬럼 추가
        if 'created_at' not in column_table_names:
            print("🔧 db_columns에 created_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_columns 
                ADD COLUMN created_at DATETIME
            """)
            print("  ✅ db_columns created_at 컬럼 추가 완료")
        
        if 'updated_at' not in column_table_names:
            print("🔧 db_columns에 updated_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_columns 
                ADD COLUMN updated_at DATETIME
            """)
            print("  ✅ db_columns updated_at 컬럼 추가 완료")
        
        # db_pk 테이블 스키마 확인 및 업그레이드
        cursor.execute("PRAGMA table_info(db_pk)")
        pk_table_columns = cursor.fetchall()
        pk_table_names = [col[1] for col in pk_table_columns]
        
        print(f"  📊 현재 db_pk 컬럼: {', '.join(pk_table_names)}")
        
        # db_pk에도 created_at, updated_at 컬럼 추가
        if 'created_at' not in pk_table_names:
            print("🔧 db_pk에 created_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_pk 
                ADD COLUMN created_at DATETIME
            """)
            print("  ✅ db_pk created_at 컬럼 추가 완료")
        
        if 'updated_at' not in pk_table_names:
            print("🔧 db_pk에 updated_at 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE db_pk 
                ADD COLUMN updated_at DATETIME
            """)
            print("  ✅ db_pk updated_at 컬럼 추가 완료")
        
        # 기존 데이터에 기본값 설정
        print("🔧 기존 데이터 마이그레이션 중...")
        current_time = datetime.now().isoformat()
        
        # db_tables의 기존 레코드에 시간 설정
        cursor.execute("""
            UPDATE db_tables 
            SET created_at = ?, updated_at = ? 
            WHERE created_at IS NULL OR updated_at IS NULL
        """, (current_time, current_time))
        
        updated_tables = cursor.rowcount
        print(f"  ✅ db_tables {updated_tables}개 레코드 업데이트 완료")
        
        # db_columns의 기존 레코드에 시간 설정
        cursor.execute("""
            UPDATE db_columns 
            SET created_at = ?, updated_at = ? 
            WHERE created_at IS NULL OR updated_at IS NULL
        """, (current_time, current_time))
        
        updated_columns = cursor.rowcount
        print(f"  ✅ db_columns {updated_columns}개 레코드 업데이트 완료")
        
        # db_pk의 기존 레코드에 시간 설정
        cursor.execute("""
            UPDATE db_pk 
            SET created_at = ?, updated_at = ? 
            WHERE created_at IS NULL OR updated_at IS NULL
        """, (current_time, current_time))
        
        updated_pk = cursor.rowcount
        print(f"  ✅ db_pk {updated_pk}개 레코드 업데이트 완료")
        
        # 변경사항 커밋
        conn.commit()
        
        # 업그레이드된 스키마 확인
        print("\n🔍 업그레이드된 스키마 확인...")
        
        cursor.execute("PRAGMA table_info(db_tables)")
        new_table_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_table_columns]
        
        print(f"  📊 업그레이드된 db_tables 컬럼: {', '.join(new_column_names)}")
        
        # 샘플 데이터 확인
        cursor.execute("""
            SELECT table_name, created_at, updated_at 
            FROM db_tables 
            LIMIT 3
        """)
        sample_data = cursor.fetchall()
        
        print(f"\n📝 샘플 데이터 확인:")
        for table_name, created_at, updated_at in sample_data:
            print(f"  - {table_name}: 생성={created_at}, 수정={updated_at}")
        
        conn.close()
        
        print(f"\n🎉 데이터베이스 스키마 업그레이드 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 스키마 업그레이드 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚀 메타데이터베이스 스키마 업그레이드 (SQLite 호환)")
    print("=" * 80)
    
    # 스키마 업그레이드 실행
    success = upgrade_db_schema()
    
    print(f"\n" + "=" * 80)
    if success:
        print("✅ 스키마 업그레이드 완료")
        print("📊 DbTable과 DbColumn에 created_at, updated_at 컬럼이 추가되었습니다")
        print("🔧 이제 SQLAlchemy 모델이 정상적으로 작동할 것입니다")
    else:
        print("❌ 스키마 업그레이드 실패")
    print("=" * 80)

if __name__ == "__main__":
    main()
