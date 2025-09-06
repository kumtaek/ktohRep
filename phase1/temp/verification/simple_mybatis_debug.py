#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from phase1.parsers.mybatis.mybatis_parser import MyBatisParser

def simple_mybatis_debug():
    """간단한 MyBatis 파서 디버깅"""
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
        
        context = {'default_schema': 'DEFAULT'}
        result = parser.parse_content(content, context)
        
        print(f"=== {xml_file} 파싱 결과 ===")
        print(f"결과 타입: {type(result)}")
        
        if isinstance(result, dict):
            print(f"키들: {list(result.keys())}")
            
            if 'sql_units' in result:
                sql_units = result['sql_units']
                print(f"SQL Units 개수: {len(sql_units)}")
                
                if sql_units:
                    print(f"첫 번째 SQL Unit 키들: {list(sql_units[0].keys()) if isinstance(sql_units[0], dict) else 'Not a dict'}")
                    if isinstance(sql_units[0], dict) and 'id' in sql_units[0]:
                        print(f"첫 번째 SQL Unit ID: {sql_units[0]['id']}")
            
            if 'tables' in result:
                print(f"Tables 개수: {len(result['tables'])}")
                
            if 'joins' in result:
                print(f"Joins 개수: {len(result['joins'])}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_mybatis_debug()

