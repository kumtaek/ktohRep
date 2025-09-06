#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def analyze_500_pattern():
    """500자 이하 패턴 분석"""
    
    test_cases = [
        ("빈 생성자", "public Product() {}", 0),
        ("매개변수 생성자", "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }", 109),
        ("int getter", "public int getProductId() { return productId; }", 19),
        ("String getter", "public String getProductName() { return productName; }", 21),
        ("void setter", "public void setProductId(String productId) { this.productId = productId; }", 29),
        ("비즈니스 메서드", "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }", 123),
        ("긴 메서드1", "public String veryLongBusinessMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        return \"very long result\";\n    }", 279),
        ("긴 메서드2", "public String extremelyLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"extremely long result\";\n    }", 400),
        ("매우 긴 메서드", "public String superLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"super long result\";\n    }", 600)
    ]
    
    # 500자 이하 패턴
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,500}\}'
    
    print("=== 500자 이하 패턴 분석 결과 ===")
    print()
    
    non_matching_under_500 = []
    non_matching_over_500 = []
    
    for name, test_case, expected_length in test_cases:
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            result = "매치됨"
        else:
            result = "매치안됨"
            if expected_length <= 500:
                non_matching_under_500.append((name, expected_length, test_case))
            else:
                non_matching_over_500.append((name, expected_length, test_case))
        
        print(f"{name}: {expected_length}자 → {result}")
    
    print()
    print("=== 문제 케이스 (500자 이하인데 매치 안됨) ===")
    for name, length, content in non_matching_under_500:
        print(f"- {name}: {length}자")
        print(f"  내용: {content[:100]}{'...' if len(content) > 100 else ''}")
    
    print()
    print("=== 500자 초과 케이스 (매치 안되는 것이 올바름) ===")
    for name, length, content in non_matching_over_500:
        print(f"- {name}: {length}자")
        print(f"  내용: {content[:100]}{'...' if len(content) > 100 else ''}")
    
    if non_matching_over_500:
        max_length = max(length for _, length, _ in non_matching_over_500)
        print(f"최대 길이: {max_length}자")
    
    # 400자 짜리 사례 상세 보기
    print()
    print("=== 400자 짜리 사례 상세 ===")
    for name, length, content in test_cases:
        if length == 400:
            print(f"이름: {name}")
            print(f"길이: {length}자")
            print("전체 내용:")
            print(content)
            print()
            break

if __name__ == "__main__":
    analyze_500_pattern()
