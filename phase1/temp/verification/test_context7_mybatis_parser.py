#!/usr/bin/env python3
"""
Context7 기반 개선된 MyBatis 파서 테스트
"""

import os
import sys
sys.path.append('phase1')

from parsers.parser_factory import ParserFactory

def test_context7_mybatis_parser():
    """Context7 기반 개선된 MyBatis 파서 테스트"""
    
    # 테스트할 XML 파일들
    test_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/ProductMapper.xml", 
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml"
    ]
    
    config = {'default_schema': 'DEFAULT'}
    factory = ParserFactory(config)
    parser = factory.get_parser('mybatis', 'mapper')
    
    print("=== Context7 기반 개선된 MyBatis 파서 테스트 ===\n")
    
    total_expected = 0
    total_parsed = 0
    total_unique = 0
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"파일: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 수동으로 SQL 개수 세기
            import re
            select_count = len(re.findall(r'<select[^>]*>', content, re.IGNORECASE))
            insert_count = len(re.findall(r'<insert[^>]*>', content, re.IGNORECASE))
            update_count = len(re.findall(r'<update[^>]*>', content, re.IGNORECASE))
            delete_count = len(re.findall(r'<delete[^>]*>', content, re.IGNORECASE))
            expected_count = select_count + insert_count + update_count + delete_count
            
            print(f"  수동 카운트: SELECT={select_count}, INSERT={insert_count}, UPDATE={update_count}, DELETE={delete_count}, 총={expected_count}")
            
            # Context7 기반 개선된 파서로 분석
            context = {'default_schema': 'DEFAULT'}
            result = parser.parse_content(content, context)
            
            if isinstance(result, dict) and 'sql_units' in result:
                parsed_count = len(result['sql_units'])
                print(f"  Context7 파서 결과: {parsed_count}개")
                
                # 중복 체크
                sql_ids = [unit.get('id', '') for unit in result['sql_units']]
                unique_ids = set(sql_ids)
                unique_count = len(unique_ids)
                
                if len(sql_ids) != unique_count:
                    print(f"  ⚠️ 중복 발견: {len(sql_ids)}개 중 {unique_count}개 고유")
                    duplicates = [id for id in sql_ids if sql_ids.count(id) > 1]
                    print(f"  중복된 ID: {set(duplicates)}")
                else:
                    print(f"  ✅ 중복 없음: {unique_count}개 모두 고유")
                
                # 각 SQL Unit 상세 분석
                for i, unit in enumerate(result['sql_units']):
                    print(f"    [{i+1}] {unit.get('type', 'unknown')} - {unit.get('id', 'no-id')}")
                    if unit.get('unique_id'):
                        print(f"        고유ID: {unit['unique_id']}")
                    if unit.get('has_dynamic_content'):
                        print(f"        동적쿼리: {unit['has_dynamic_content']}")
                    if unit.get('has_include_tags'):
                        print(f"        Include태그: {unit['has_include_tags']}")
                    if unit.get('line_number'):
                        print(f"        라인번호: {unit['line_number']}")
                    if unit.get('sql_content'):
                        sql_preview = unit['sql_content'][:50] + "..." if len(unit['sql_content']) > 50 else unit['sql_content']
                        print(f"        SQL: {sql_preview}")
                
                total_expected += expected_count
                total_parsed += parsed_count
                total_unique += unique_count
            else:
                print(f"  ❌ 파싱 실패: {type(result)}")
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print(f"=== Context7 기반 파서 전체 결과 ===")
    print(f"예상 총 개수: {total_expected}")
    print(f"파싱된 총 개수: {total_parsed}")
    print(f"고유 SQL Units: {total_unique}")
    if total_expected > 0:
        accuracy = (total_parsed / total_expected) * 100
        print(f"정확도: {accuracy:.1f}%")
    
    # 중복 방지 효과
    if total_parsed > 0:
        duplication_rate = ((total_parsed - total_unique) / total_parsed) * 100
        print(f"중복률: {duplication_rate:.1f}%")
    
    return total_expected, total_parsed, total_unique

if __name__ == "__main__":
    test_context7_mybatis_parser()

