#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def find_max_length():
    """진짜 최대 길이 찾기"""
    
    test_cases = [
        ("빈 생성자", "public Product() {}", 0),
        ("매개변수 생성자", "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }", 109),
        ("int getter", "public int getProductId() { return productId; }", 19),
        ("String getter", "public String getProductName() { return productName; }", 21),
        ("void setter", "public void setProductId(String productId) { this.productId = productId; }", 29),
        ("비즈니스 메서드", "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }", 123),
        ("긴 메서드1", "public String veryLongBusinessMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        return \"very long result\";\n    }", 279),
        ("긴 메서드2", "public String extremelyLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"extremely long result\";\n    }", 400),
        ("매우 긴 메서드", "public String superLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"super long result\";\n    }", 600),
        ("극도로 긴 메서드", "public String ultraLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"ultra long result\";\n    }", 800)
    ]
    
    print("=== 모든 케이스의 본문 길이 ===")
    for name, test_case, expected_length in test_cases:
        # 실제 본문 길이 계산
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            actual_length = len(body)
        else:
            actual_length = 0
        
        print(f"{name}: 예상 {expected_length}자 → 실제 {actual_length}자")
    
    print()
    
    # 최대 길이 찾기
    max_length = 0
    max_case = None
    max_content = None
    
    for name, test_case, expected_length in test_cases:
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            actual_length = len(body)
            
            if actual_length > max_length:
                max_length = actual_length
                max_case = name
                max_content = test_case
    
    print("=== 최대 길이 케이스 ===")
    print(f"이름: {max_case}")
    print(f"최대 길이: {max_length}자")
    print("전체 내용:")
    print(max_content)
    print()
    print("=== 본문만 ===")
    brace_start = max_content.find('{')
    brace_end = max_content.rfind('}')
    if brace_start != -1 and brace_end != -1:
        body = max_content[brace_start+1:brace_end]
        print(f"본문: '{body}'")
        print(f"본문 길이: {len(body)}자")

if __name__ == "__main__":
    find_max_length()
