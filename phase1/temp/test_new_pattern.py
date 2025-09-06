#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_new_pattern():
    """새로운 패턴 테스트"""
    
    test_cases = [
        "public String getProductId() { return productId; }",  # 19자 - 매치되지 않아야 함
        "public void setProductId(String productId) { this.productId = productId; }",  # 45자 - 매치되지 않아야 함
        "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }"  # 101자 이상 - 매치되어야 함
    ]
    
    # 새로운 패턴 (101자 이상)
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{101,}\}'
    
    print("=== 새로운 패턴 테스트 (101자 이상) ===")
    print("패턴:", pattern)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 테스트 케이스 {i} ---")
        print("내용:", test_case[:100] + "..." if len(test_case) > 100 else test_case)
        
        # 본문 길이 확인
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            print("본문 길이:", len(body), "자")
        
        # 패턴 매치 시도
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            print("결과: 매치됨")
        else:
            print("결과: 매치되지 않음")
        print()

if __name__ == "__main__":
    test_new_pattern()
