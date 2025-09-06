#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from parsers.mybatis.mybatis_parser import MyBatisParser

def check_sql_statements_structure():
    """MyBatis 파서의 sql_statements 구조 확인"""
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
        
        if 'sql_units' in result:
            sql_units = result['sql_units']
            print(f"SQL Units 개수: {len(sql_units)}")
            
            if sql_units:
                first_unit = sql_units[0]
                print(f"첫 번째 SQL Unit 구조:")
                print(f"  타입: {type(first_unit)}")
                if isinstance(first_unit, dict):
                    print(f"  키들: {list(first_unit.keys())}")
                    for key, value in first_unit.items():
                        if key in ['id', 'type', 'stmt_kind', 'tables', 'joins']:
                            print(f"  {key}: {value}")
                else:
                    print(f"  값: {first_unit}")
        else:
            print("sql_units 키가 없습니다.")
            print(f"사용 가능한 키들: {list(result.keys())}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sql_statements_structure()
