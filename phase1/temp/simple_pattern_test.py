#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def simple_pattern_test():
    """간단한 패턴 테스트"""
    
    # 테스트 케이스
    test_case = "public String getProductId() { return productId; }"
    
    # 현재 패턴
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,100}\}'
    
    print("테스트 케이스:", test_case)
    print("패턴:", pattern)
    
    # 패턴 매치 시도
    match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
    
    if match:
        print("결과: 매치됨")
        print("매치된 부분:", match.group(0))
    else:
        print("결과: 매치되지 않음")
        
        # 본문 길이 분석
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            print("본문:", repr(body))
            print("본문 길이:", len(body), "자")
            
            if len(body) <= 100:
                print("분석: 100자 이하이므로 매치되지 않음 (올바름)")
            else:
                print("분석: 100자 초과인데 매치되지 않음 (문제)")

if __name__ == "__main__":
    simple_pattern_test()
