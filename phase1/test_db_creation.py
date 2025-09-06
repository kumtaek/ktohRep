#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 테이블 생성 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 모든 모델을 임포트
from phase1.models.database import (
    DatabaseManager, File, Project, Class, Method, SqlUnit, DbTable, DbColumn, DbPk,
    Edge, Join, RequiredFilter, Summary, EnrichmentLog, Chunk, Embedding,
    JavaImport, EdgeHint, Relatedness, VulnerabilityFix, CodeMetric, Duplicate,
    DuplicateInstance, ParseResultModel, Base
)

def test_db_creation():
    """데이터베이스 테이블 생성 테스트"""
    
    # 기존 데이터베이스 파일 삭제
    db_path = "../project/sampleSrc/metadata.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"기존 데이터베이스 파일 삭제: {db_path}")
    
    # 데이터베이스 설정
    db_config = {
        'type': 'sqlite',
        'sqlite': {
            'path': db_path
        }
    }
    
    # DatabaseManager 초기화
    db_manager = DatabaseManager(db_config)
    db_manager.initialize()
    
    # 명시적으로 테이블 생성
    Base.metadata.create_all(db_manager.engine)
    
    # 테이블 목록 확인
    from sqlalchemy import inspect
    inspector = inspect(db_manager.engine)
    tables = inspector.get_table_names()
    
    print(f"생성된 테이블 수: {len(tables)}")
    print("생성된 테이블 목록:")
    for table in tables:
        print(f"  - {table}")
    
    # 데이터베이스 파일 크기 확인
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"데이터베이스 파일 크기: {file_size} bytes")
    else:
        print("데이터베이스 파일이 생성되지 않았습니다.")
    
    db_manager.close()

if __name__ == "__main__":
    test_db_creation()
