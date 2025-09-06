#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_200_pattern():
    """200자 이하 패턴 테스트 - 매칭 안되는 건들만 정리"""
    
    test_cases = [
        # Getter/Setter 메서드들 (매치되어야 함 - 200자 이하)
        "public String getProductId() { return productId; }",  # 19자
        "public void setProductId(String productId) { this.productId = productId; }",  # 45자
        "public String getProductName() { return productName; }",  # 21자
        "public void setProductName(String productName) { this.productName = productName; }",  # 47자
        
        # 생성자들 (매치되어야 함 - 200자 이하)
        "public Product() {}",  # 2자
        "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }",  # 약 100자
        
        # 비즈니스 메서드들 (매치되어야 함 - 200자 이하)
        "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }",  # 약 150자
        
        # 긴 비즈니스 메서드 (매치되지 않아야 함 - 200자 초과)
        "public String veryLongBusinessMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        return \"very long result\";\n    }"  # 약 300자
    ]
    
    # 200자 이하 패턴
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,200}\}'
    
    print("=== 200자 이하 패턴 테스트 - 매칭 안되는 건들 ===")
    print("패턴:", pattern)
    print()
    
    non_matching_cases = []
    
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
            print("결과: 매치되지 않음 ⭐")
            non_matching_cases.append({
                'case': i,
                'content': test_case[:100] + "..." if len(test_case) > 100 else test_case,
                'body_length': len(body) if brace_start != -1 and brace_end != -1 else 0
            })
        print()
    
    print("=== 매칭 안되는 건들 정리 ===")
    if non_matching_cases:
        for case in non_matching_cases:
            print(f"케이스 {case['case']}: {case['content']} (본문: {case['body_length']}자)")
    else:
        print("매칭 안되는 건이 없습니다.")

if __name__ == "__main__":
    test_200_pattern()
