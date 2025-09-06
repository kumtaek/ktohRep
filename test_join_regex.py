#!/usr/bin/env python3
"""조인 정규식 테스트"""

import re

def test_join_patterns():
    """조인 패턴 정규식 테스트"""
    
    test_cases = [
        "JOIN CUSTOMERS c ON o.CUSTOMER_ID = c.CUSTOMER_ID",
        "ON o.CUSTOMER_ID = c.CUSTOMER_ID",
        "o.CUSTOMER_ID = c.CUSTOMER_ID",
        "ON oi.PRODUCT_ID = p.PRODUCT_ID",
        "oi.PRODUCT_ID = p.PRODUCT_ID"
    ]
    
    # 현재 ON 절 패턴
    on_pattern = r"\bON\s+([\w\.]+)\s*\.\s*(\w+)\s*(=|!=|>=|<=|<>|<|>)\s*([\w\.]+)\s*\.\s*(\w+)"
    
    # 암시적 조인 패턴  
    implicit_pattern = r"([\w\.]+)\s*\.\s*(\w+)\s*(=|!=|>=|<=|<>|<|>)\s*([\w\.]+)\s*\.\s*(\w+)"
    
    print("조인 정규식 패턴 테스트:")
    print(f"ON 패턴: {on_pattern}")
    print(f"암시적 패턴: {implicit_pattern}")
    print()
    
    for i, text in enumerate(test_cases):
        print(f"테스트 케이스 {i+1}: '{text}'")
        
        on_match = re.search(on_pattern, text, re.I)
        print(f"  ON 패턴 매치: {on_match}")
        if on_match:
            print(f"  ON 매치 그룹: {on_match.groups()}")
        
        implicit_match = re.search(implicit_pattern, text, re.I)
        print(f"  암시적 패턴 매치: {implicit_match}")
        if implicit_match:
            print(f"  암시적 매치 그룹: {implicit_match.groups()}")
            
        print()

if __name__ == "__main__":
    test_join_patterns()