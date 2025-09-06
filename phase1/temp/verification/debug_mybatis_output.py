#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from phase1.parsers.mybatis.mybatis_parser import MyBatisParser

def debug_mybatis_output():
    """MyBatis 파서 출력 구조 디버깅"""
    # 간단한 config 생성
    config = {
        'include_patterns': ['**/*.xml'],
        'exclude_patterns': [],
        'default_owner': 'DEFAULT'
    }
    parser = MyBatisParser(config)
    
    # XML 파일 경로
    xml_file = "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml"
    
    print(f"=== {xml_file} 파싱 결과 구조 분석 ===")
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파싱 실행
        context = {'default_schema': 'DEFAULT'}
        result = parser.parse_content(content, context)
        
        print(f"파싱 결과 타입: {type(result)}")
        print(f"파싱 결과: {result}")
        
        if isinstance(result, dict):
            print(f"파싱 결과 키들: {result.keys()}")
            
            if 'sql_units' in result:
                sql_units = result['sql_units']
                print(f"SQL Units 개수: {len(sql_units)}")
                
                if sql_units:
                    print(f"첫 번째 SQL Unit 구조:")
                    first_unit = sql_units[0]
                    print(f"  타입: {type(first_unit)}")
                    if isinstance(first_unit, dict):
                        print(f"  키들: {first_unit.keys()}")
                        for key, value in first_unit.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"  값: {first_unit}")
            
            if 'tables' in result:
                tables = result['tables']
                print(f"Tables 개수: {len(tables)}")
                
            if 'joins' in result:
                joins = result['joins']
                print(f"Joins 개수: {len(joins)}")
        else:
            print(f"결과가 dict가 아님: {result}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mybatis_output()
