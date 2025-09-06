#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('phase1')

from phase1.parsers.jsp.jsp_parser import JSPParser

def test_jsp_parser_direct():
    """JSP 파서 직접 테스트"""
    print("=== JSP 파서 직접 테스트 ===\n")
    
    # JSP 파일들
    jsp_files = [
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/IntegratedView.jsp",
        "project/sampleSrc/src/main/webapp/WEB-INF/views/userList.jsp",
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/order/orderView.jsp",
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/product/productSearch.jsp",
        "project/sampleSrc/src/main/webapp/WEB-INF/jsp/user/userList.jsp"
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
            print(f"파일 존재: {os.path.exists(file_path)}")
            
            # 1. SQL Units 추출 테스트
            print("\n1. SQL Units 추출 테스트:")
            sql_units = parser._extract_sql_queries_aggressive(content)
            print(f"추출된 SQL Units 수: {len(sql_units)}")
            for i, unit in enumerate(sql_units[:5]):  # 처음 5개만 출력
                print(f"  {i+1}. {unit.get('id', 'Unknown')} ({unit.get('type', 'Unknown')})")
            if len(sql_units) > 5:
                print(f"  ... 외 {len(sql_units) - 5}개")
            
            # 2. 간단한 SQL 패턴 테스트
            print("\n2. 간단한 SQL 패턴 테스트:")
            import re
            sql_patterns = [
                r'SELECT\s+.*?FROM\s+\w+',
                r'INSERT\s+INTO\s+\w+',
                r'UPDATE\s+\w+\s+SET',
                r'DELETE\s+FROM\s+\w+'
            ]
            
            total_matches = 0
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                match_list = list(matches)
                if match_list:
                    print(f"  패턴 '{pattern}': {len(match_list)}개 매치")
                    total_matches += len(match_list)
            
            if total_matches == 0:
                print("  SQL 패턴 매치 없음")
            
            # 3. 파일 내용 샘플 확인
            print("\n3. 파일 내용 샘플:")
            lines = content.split('\n')
            for i, line in enumerate(lines[:10]):  # 처음 10줄만 출력
                if line.strip():
                    print(f"  {i+1}: {line.strip()[:100]}...")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_jsp_parser_direct()
