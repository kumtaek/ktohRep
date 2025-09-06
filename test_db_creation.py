#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 생성 테스트 스크립트
최소한의 설정으로 데이터베이스 테이블 생성이 정상적으로 작동하는지 확인합니다.
"""

import yaml
import os
import sys
from pathlib import Path

# phase1 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from models.database import DatabaseManager, Base

def test_minimal_db_creation():
    """최소한의 설정으로 데이터베이스 생성 테스트"""
    
    print("1. 설정 로드 중...")
    
    # 설정 파일 경로
    config_path = 'config/config.yaml'
    
    if not os.path.exists(config_path):
        print(f"설정 파일을 찾을 수 없습니다: {config_path}")
        return False
    
    # 설정 로드
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']['project']
    print(f"DB 설정: {db_config['type']}")
    
    print("2. DatabaseManager 초기화...")
    db_manager = DatabaseManager(db_config)
    
    print("3. DB 초기화...")
    db_manager.initialize()
    
    print("4. 등록된 테이블 확인...")
    print(f"등록된 테이블: {list(Base.metadata.tables.keys())}")
    
    print("5. 실제 DB 테이블 확인...")
    from sqlalchemy import inspect
    inspector = inspect(db_manager.engine)
    existing_tables = inspector.get_table_names()
    print(f"생성된 테이블: {existing_tables}")
    
    print("6. 테이블 생성 검증...")
    if not existing_tables:
        print("❌ 테이블이 생성되지 않았습니다!")
        return False
    else:
        print(f"✅ {len(existing_tables)}개 테이블이 성공적으로 생성되었습니다!")
        
        # 핵심 테이블 확인
        core_tables = ['files', 'classes', 'methods', 'edges']
        missing_tables = [table for table in core_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"⚠️  누락된 핵심 테이블: {missing_tables}")
        else:
            print("✅ 모든 핵심 테이블이 생성되었습니다!")
    
    print("7. 테스트 완료")
    return True

if __name__ == "__main__":
    try:
        success = test_minimal_db_creation()
        if success:
            print("\n🎉 데이터베이스 생성 테스트 성공!")
        else:
            print("\n❌ 데이터베이스 생성 테스트 실패!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
