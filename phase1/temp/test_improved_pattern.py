#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_improved_pattern():
    """개선된 패턴 테스트"""
    
    test_cases = [
        # getter/setter 메서드들
        "public String getProductId() { return productId; }",
        "public void setProductId(String productId) { this.productId = productId; }",
        "public int getStockQuantity() { return stockQuantity; }",
        "public Double getPrice() { return price; }",
        
        # 생성자들
        "public Product() {}",
        "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }",
        
        # 비즈니스 메서드들
        "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }",
        
        # 긴 메서드 (커멘트 포함)
        "public String veryLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        return \"very long result\";\n    }"
    ]
    
    # 개선된 패턴들
    constructor_pattern = r'public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    method_pattern = r'public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    print("=== 개선된 패턴 테스트 ===")
    print(f"생성자 패턴: {constructor_pattern}")
    print(f"메서드 패턴: {method_pattern}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 테스트 케이스 {i} ---")
        print(f"내용: {test_case[:100]}{'...' if len(test_case) > 100 else ''}")
        
        # 본문 길이 확인
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            # 커멘트 제거
            body_no_comments = re.sub(r'//.*$', '', body, flags=re.MULTILINE)
            body_no_comments = re.sub(r'/\*.*?\*/', '', body_no_comments, flags=re.DOTALL)
            body_no_comments = re.sub(r'\s+', ' ', body_no_comments).strip()
            print(f"본문 길이 (커멘트 제외): {len(body_no_comments)}자")
        
        # 생성자 패턴 테스트
        constructor_match = re.search(constructor_pattern, test_case, re.IGNORECASE | re.DOTALL)
        print(f"생성자 패턴: {'매치됨' if constructor_match else '매치안됨'}")
        
        # 메서드 패턴 테스트
        method_match = re.search(method_pattern, test_case, re.IGNORECASE | re.DOTALL)
        print(f"메서드 패턴: {'매치됨' if method_match else '매치안됨'}")
        
        # 전체 결과
        if constructor_match or method_match:
            print("결과: 매치됨 ✅")
        else:
            print("결과: 매치안됨 ❌")
        
        print()

if __name__ == "__main__":
    test_improved_pattern()
