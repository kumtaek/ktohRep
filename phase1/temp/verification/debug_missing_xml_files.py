#!/usr/bin/env python3
"""
누락된 XML 파일들 디버깅
"""

import os
import sys
sys.path.append('phase1')

from parsers.parser_factory import ParserFactory

def debug_missing_xml_files():
    """누락된 XML 파일들 디버깅"""
    
    # 파싱되지 않은 XML 파일들
    missing_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/ProductMapper.xml", 
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml"
    ]
    
    # ParserFactory를 사용해서 MyBatis 파서 생성
    config = {'default_schema': 'DEFAULT'}
    factory = ParserFactory(config)
    parser = factory.get_parser('mybatis', 'mapper')
    
    print("=== 누락된 XML 파일들 디버깅 ===\n")
    
    for file_path in missing_files:
        if not os.path.exists(file_path):
            print(f"파일 없음: {file_path}")
            continue
            
        print(f"파일: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            print(f"  파일 크기: {len(content)} 문자")
            print(f"  첫 200자: {content[:200]}...")
            
            # 파서로 분석
            context = {'default_schema': 'DEFAULT'}
            result = parser.parse_content(content, context)
            
            if isinstance(result, dict) and 'sql_units' in result:
                sql_units = result['sql_units']
                print(f"  파싱된 SQL Units: {len(sql_units)}개")
                
                if len(sql_units) > 0:
                    print("  첫 번째 SQL Unit:")
                    first_unit = sql_units[0]
                    for key, value in first_unit.items():
                        if key == 'sql_content' and len(str(value)) > 100:
                            print(f"    {key}: {str(value)[:100]}...")
                        else:
                            print(f"    {key}: {value}")
                else:
                    print("  ⚠️ SQL Units가 추출되지 않음")
                    
                    # 파일 내용에서 MyBatis 태그 확인
                    import re
                    select_pattern = re.compile(r'<select[^>]*>', re.IGNORECASE)
                    insert_pattern = re.compile(r'<insert[^>]*>', re.IGNORECASE)
                    update_pattern = re.compile(r'<update[^>]*>', re.IGNORECASE)
                    delete_pattern = re.compile(r'<delete[^>]*>', re.IGNORECASE)
                    
                    select_matches = select_pattern.findall(content)
                    insert_matches = insert_pattern.findall(content)
                    update_matches = update_pattern.findall(content)
                    delete_matches = delete_pattern.findall(content)
                    
                    print(f"  파일에서 발견된 태그들:")
                    print(f"    <select>: {len(select_matches)}개")
                    print(f"    <insert>: {len(insert_matches)}개")
                    print(f"    <update>: {len(update_matches)}개")
                    print(f"    <delete>: {len(delete_matches)}개")
                    
                    if len(select_matches) > 0:
                        print(f"    첫 번째 <select> 태그: {select_matches[0]}")
            else:
                print(f"  ⚠️ 예상치 못한 결과: {type(result)}")
                
        except Exception as e:
            print(f"  ❌ 파싱 오류: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    debug_missing_xml_files()

