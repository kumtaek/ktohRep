#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('phase1')

from parsers.jsp.jsp_parser import JSPParser

def test_jsp_parser_parse_content():
    """JSP 파서 parse_content 메서드 테스트"""
    print("=== JSP 파서 parse_content 메서드 테스트 ===\n")
    
    # JSP 파일들
    jsp_files = [
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/IntegratedView.jsp",
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/product/productSearch.jsp"
    ]
    
    # JSP 파서 초기화
    config = {}
    parser = JSPParser(config)
    
    for file_path in jsp_files:
        print(f"=== {file_path} ===")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"파일 크기: {len(content)} bytes")
            
            # parse_content 메서드 테스트
            print("\n1. parse_content 메서드 테스트:")
            context = {'default_schema': 'DEFAULT'}
            result = parser.parse_content(content, context)
            
            print(f"결과 타입: {type(result)}")
            print(f"결과 내용: {result}")
            
            if isinstance(result, dict):
                print("\n결과 딕셔너리 키들:")
                for key, value in result.items():
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)}개 항목")
                        if len(value) > 0:
                            print(f"    첫 번째 항목: {value[0]}")
                    else:
                        print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_jsp_parser_parse_content()

