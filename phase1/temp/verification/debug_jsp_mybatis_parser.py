#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('phase1')

from parsers.jsp_mybatis_parser import JspMybatisParser

def debug_jsp_mybatis_parser():
    """JSP MyBatis 파서의 XML 처리 디버깅"""
    
    # 간단한 config 생성
    config = {
        'include_patterns': ['**/*.xml', '**/*.jsp'],
        'exclude_patterns': [],
        'default_owner': 'DEFAULT'
    }
    
    parser = JspMybatisParser(config)
    
    xml_file = "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml"
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"=== {xml_file} JSP MyBatis 파서 처리 ===")
        print(f"파일 크기: {len(content)} bytes")
        
        # 파싱 실행
        result = parser.parse_file(xml_file, 1)  # project_id = 1
        
        print(f"파싱 결과 타입: {type(result)}")
        
        if isinstance(result, tuple) and len(result) >= 2:
            file_obj, sql_units = result[0], result[1]
            print(f"File 객체: {file_obj}")
            print(f"SQL Units 개수: {len(sql_units)}")
            
            if sql_units:
                print("첫 번째 SQL Unit:")
                first_unit = sql_units[0]
                print(f"  타입: {type(first_unit)}")
                if hasattr(first_unit, '__dict__'):
                    print(f"  속성들: {list(first_unit.__dict__.keys())}")
                    for key, value in first_unit.__dict__.items():
                        if key in ['stmt_id', 'stmt_kind', 'origin']:
                            print(f"    {key}: {value}")
        else:
            print(f"예상과 다른 결과 형태: {result}")
            print(f"결과 타입: {type(result)}")
            if hasattr(result, '__dict__'):
                print(f"결과 속성들: {list(result.__dict__.keys())}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_jsp_mybatis_parser()
