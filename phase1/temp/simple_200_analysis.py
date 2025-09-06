#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def simple_200_analysis():
    """200자 이하 패턴 문제 간단 분석"""
    
    test_cases = [
        ("빈 생성자", "public Product() {}", 0),
        ("매개변수 생성자", "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }", 109),
        ("Getter", "public String getProductId() { return productId; }", 19),
        ("Setter", "public void setProductId(String productId) { this.productId = productId; }", 29),
        ("비즈니스 메서드", "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }", 123),
        ("긴 메서드1", "public String veryLongBusinessMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        return \"very long result\";\n    }", 279),
        ("긴 메서드2", "public String extremelyLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"extremely long result\";\n    }", 400)
    ]
    
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,200}\}'
    
    print("=== 200자 이하 패턴 분석 결과 ===")
    print()
    
    non_matching_under_200 = []
    non_matching_over_200 = []
    
    for name, test_case, expected_length in test_cases:
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            result = "매치됨"
        else:
            result = "매치안됨"
            if expected_length <= 200:
                non_matching_under_200.append((name, expected_length))
            else:
                non_matching_over_200.append((name, expected_length))
        
        print(f"{name}: {expected_length}자 → {result}")
    
    print()
    print("=== 문제 케이스 (200자 이하인데 매치 안됨) ===")
    for name, length in non_matching_under_200:
        print(f"- {name}: {length}자")
    
    print()
    print("=== 200자 초과 케이스 (매치 안되는 것이 올바름) ===")
    for name, length in non_matching_over_200:
        print(f"- {name}: {length}자")
    
    if non_matching_over_200:
        max_length = max(length for _, length in non_matching_over_200)
        print(f"최대 길이: {max_length}자")

if __name__ == "__main__":
    simple_200_analysis()
