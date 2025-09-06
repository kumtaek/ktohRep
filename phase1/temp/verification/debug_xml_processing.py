#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from parsers.mybatis.mybatis_parser import MyBatisParser

def debug_xml_processing():
    """XML 파일 처리 과정 디버깅"""
    config = {
        'include_patterns': ['**/*.xml'],
        'exclude_patterns': [],
        'default_owner': 'DEFAULT'
    }
    parser = MyBatisParser(config)
    
    xml_file = "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml"
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"=== {xml_file} 처리 과정 ===")
        print(f"파일 크기: {len(content)} bytes")
        
        # 1. 파일 확장자 확인
        print(f"파일 확장자: {os.path.splitext(xml_file)[1]}")
        
        # 2. 파싱 실행
        context = {'default_schema': 'DEFAULT'}
        result = parser.parse_content(content, context)
        
        print(f"파싱 결과 키들: {list(result.keys())}")
        
        if 'sql_units' in result:
            sql_units = result['sql_units']
            print(f"SQL Units 개수: {len(sql_units)}")
            
            if sql_units:
                print("첫 번째 SQL Unit:")
                first_unit = sql_units[0]
                for key, value in first_unit.items():
                    if key in ['id', 'type', 'stmt_kind', 'tables']:
                        print(f"  {key}: {value}")
        
        # 3. 메타디비 엔진에서 사용할 수 있는 형태인지 확인
        print(f"\n메타디비 엔진 호환성:")
        print(f"  sql_units 키 존재: {'sql_units' in result}")
        print(f"  sql_units 타입: {type(result.get('sql_units'))}")
        print(f"  sql_units 리스트 여부: {isinstance(result.get('sql_units'), list)}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_xml_processing()
