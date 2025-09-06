#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def test_xml_parsing_simple():
    """간단한 XML 파싱 테스트"""
    print("=== 간단한 XML 파싱 테스트 ===\n")
    
    # XML 파일들 테스트
    xml_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/ProductMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/IntegratedMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/TestJoinMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/mapper/UserMapper.xml"
    ]
    
    total_queries = 0
    
    for xml_file in xml_files:
        if not os.path.exists(xml_file):
            print(f"파일이 존재하지 않습니다: {xml_file}")
            continue
            
        print(f"=== {xml_file} ===")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 간단한 정규식으로 SQL 태그 찾기
            sql_tags = ['select', 'insert', 'update', 'delete']
            file_queries = 0
            
            for tag in sql_tags:
                # <select id="..."> 형태
                pattern = rf'<{tag}\s+[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>'
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    print(f"  {tag.upper()} 쿼리: {len(matches)}개")
                    for match in matches:
                        print(f"    - {match}")
                    file_queries += len(matches)
            
            print(f"  총 쿼리 수: {file_queries}개")
            total_queries += file_queries
            print()
            
        except Exception as e:
            print(f"파일 읽기 오류: {e}")
            print()
    
    print(f"=== 전체 요약 ===")
    print(f"총 파싱된 SQL 쿼리 수: {total_queries}개")
    
    return total_queries

if __name__ == "__main__":
    result = test_xml_parsing_simple()

