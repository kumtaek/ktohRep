#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from phase1.database.metadata_engine import MetadataEngine

def debug_metadata_engine():
    """메타디비 엔진의 XML 처리 과정 디버깅"""
    
    # 테스트용 데이터 (MyBatis 파서 결과 시뮬레이션)
    test_data = {
        'sql_units': [
            {
                'id': 'selectOrderById',
                'type': 'select',
                'tables': ['CUSTOMERS'],
                'joins': [],
                'filters': []
            },
            {
                'id': 'insertOrder',
                'type': 'insert',
                'tables': ['ORDERS'],
                'joins': [],
                'filters': []
            }
        ]
    }
    
    print("=== 메타디비 엔진 XML 처리 테스트 ===")
    print(f"테스트 데이터: {test_data}")
    
    try:
        # 메타디비 엔진 생성
        engine = MetadataEngine("project/sampleSrc/metadata.db")
        
        # _augment_sql_from_json 메소드 직접 테스트
        print("\n=== _augment_sql_from_json 메소드 테스트 ===")
        
        # 테스트용 file_id (실제 존재하는 XML 파일 ID 사용)
        test_file_id = 27  # OrderMapper.xml의 file_id
        test_file_path = "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml"
        
        print(f"테스트 파일 ID: {test_file_id}")
        print(f"테스트 파일 경로: {test_file_path}")
        
        # 메소드 호출
        result = engine._augment_sql_from_json(test_file_id, test_file_path, test_data)
        
        print(f"결과: {result}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_metadata_engine()

