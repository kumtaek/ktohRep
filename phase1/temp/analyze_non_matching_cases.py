#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def analyze_non_matching_cases():
    """매치되지 않는 사례들을 상세 분석"""
    
    # 실제 Java 파일에서 추출한 메서드 샘플들
    test_cases = [
        # Getter/Setter 메서드들 (매치되지 않아야 함)
        "public String getProductId() { return productId; }",
        "public void setProductId(String productId) { this.productId = productId; }",
        "public String getProductName() { return productName; }",
        "public void setProductName(String productName) { this.productName = productName; }",
        "public Double getPrice() { return price; }",
        "public void setPrice(Double price) { this.price = price; }",
        
        # 생성자들 (매치되지 않아야 함)
        "public Product() {}",
        "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }",
        
        # 비즈니스 메서드들 (매치되어야 함)
        "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }",
        "public void updateProductStock(@RequestParam String productId, @RequestParam int quantity, Model model) {\n        // 재고 업데이트 로직\n        // 데이터베이스 업데이트\n        // 로그 기록\n        // 알림 발송\n    }"
    ]
    
    # 현재 패턴
    pattern = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,100}\}'
    
    print("=== 매치되지 않는 사례 분석 ===")
    print("패턴: " + pattern)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 테스트 케이스 {i} ---")
        print(f"내용: {test_case}")
        
        # 패턴 매치 시도
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            print("결과: 매치됨 (예상과 다름)")
            print(f"매치된 부분: {match.group(0)}")
        else:
            print("결과: 매치되지 않음 (예상대로)")
            
            # 본문 길이 분석
            brace_start = test_case.find('{')
            brace_end = test_case.rfind('}')
            if brace_start != -1 and brace_end != -1:
                body = test_case[brace_start+1:brace_end]
                print(f"본문: '{body}'")
                print(f"본문 길이: {len(body)}자")
                
                if len(body) <= 100:
                    print("분석: 100자 이하이므로 매치되지 않음 (올바름)")
                else:
                    print("분석: 100자 초과인데 매치되지 않음 (문제)")
            else:
                print("분석: 중괄호를 찾을 수 없음")
        
        print()

if __name__ == "__main__":
    analyze_non_matching_cases()
