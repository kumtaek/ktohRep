#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def debug_pattern():
    """패턴 디버깅"""
    
    test_case = "public String getProductId() { return productId; }"
    
    print("테스트 케이스:", test_case)
    print()
    
    # 다양한 패턴 테스트
    patterns = [
        r'\{[^}]{,100}\}',  # 현재 패턴
        r'\{[^}]{0,100}\}',  # 명시적 0-100
        r'\{[^}]{1,100}\}',  # 1-100
        r'\{[^}]{,50}\}',   # 0-50
        r'\{[^}]{,20}\}',   # 0-20
        r'\{[^}]{,10}\}',   # 0-10
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"패턴 {i}: {pattern}")
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            print("  결과: 매치됨")
            print("  매치된 부분:", repr(match.group(0)))
        else:
            print("  결과: 매치되지 않음")
        print()
    
    # 본문 길이 확인
    brace_start = test_case.find('{')
    brace_end = test_case.rfind('}')
    if brace_start != -1 and brace_end != -1:
        body = test_case[brace_start+1:brace_end]
        print("본문:", repr(body))
        print("본문 길이:", len(body), "자")

if __name__ == "__main__":
    debug_pattern()
