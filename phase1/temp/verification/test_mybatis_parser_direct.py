#!/usr/bin/env python3
"""
MyBatis 파서 직접 테스트
"""

import sys
import os
sys.path.append('phase1')

from parsers.parser_factory import ParserFactory

def test_mybatis_parser():
    """MyBatis 파서 직접 테스트"""
    
    # 테스트할 XML 파일들
    test_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/ProductMapper.xml", 
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/IntegratedMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/TestJoinMapper.xml"
    ]
    
    # ParserFactory를 사용해서 MyBatis 파서 생성
    config = {'default_schema': 'DEFAULT'}
    factory = ParserFactory(config)
    parser = factory.get_parser('mybatis', 'mapper')
    
    print("=== MyBatis 파서 직접 테스트 ===\n")
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"파일 없음: {file_path}")
            continue
            
        print(f"파일: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 파서로 분석
            context = {'default_schema': 'DEFAULT'}
            result = parser.parse_content(content, context)
            
            print(f"  파싱 결과 타입: {type(result)}")
            
            if isinstance(result, dict):
                print(f"  결과 키들: {list(result.keys())}")
                
                if 'sql_units' in result:
                    sql_units = result['sql_units']
                    print(f"  SQL Units 개수: {len(sql_units)}")
                    
                    for i, unit in enumerate(sql_units[:5]):  # 최대 5개만 표시
                        print(f"    {i+1}. {unit}")
                    if len(sql_units) > 5:
                        print(f"    ... 외 {len(sql_units) - 5}개")
                else:
                    print("  SQL Units 키가 없음")
            else:
                print(f"  예상치 못한 결과 타입: {type(result)}")
                print(f"  결과: {result}")
                
        except Exception as e:
            print(f"  파싱 오류: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    test_mybatis_parser()
