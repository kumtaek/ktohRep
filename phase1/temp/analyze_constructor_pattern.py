#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def analyze_constructor_pattern():
    """생성자 패턴 인식 문제 상세 분석"""
    
    # 현재 패턴
    current_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'
    
    # 생성자 케이스들
    constructor_cases = [
        ("빈 생성자", "public Product() {}"),
        ("매개변수 생성자", "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }"),
        ("단일 매개변수 생성자", "public Product(String productId) {\n        this.productId = productId;\n    }"),
        ("복잡한 매개변수 생성자", "public Product(String productId, String productName, Double price, Integer stockQuantity, String status) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n        this.stockQuantity = stockQuantity;\n        this.status = status;\n    }")
    ]
    
    print("=== 생성자 패턴 인식 문제 상세 분석 ===")
    print(f"현재 패턴: {current_pattern}")
    print()
    
    for name, test_case in constructor_cases:
        print(f"--- {name} ---")
        print(f"내용: {test_case}")
        
        # 본문 길이 확인
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            print(f"본문: '{body}'")
            print(f"본문 길이: {len(body)}자")
        
        # 현재 패턴으로 매치 시도
        match = re.search(current_pattern, test_case, re.IGNORECASE | re.DOTALL)
        print(f"현재 패턴 매치: {'성공' if match else '실패'}")
        
        # 패턴 분석
        print("패턴 분석:")
        print("  - public\\s+: 'public ' 매치")
        print("  - \\w+: 클래스명 매치")
        print("  - \\s+: 공백 매치")
        print("  - \\w+: 메서드명 매치 (생성자는 클래스명과 같음)")
        print("  - \\s*: 공백 매치")
        print("  - \\([^)]*\\): 매개변수 매치")
        print("  - \\s*: 공백 매치")
        print("  - \\{[^}]{,400}\\}: 본문 매치 (400자 이하)")
        
        # 문제점 분석
        print("문제점 분석:")
        
        # 1. 빈 생성자 분석
        if name == "빈 생성자":
            print("  - 빈 생성자 'public Product() {}' 분석:")
            print("    * 'public Product' → public\\s+\\w+ 매치됨")
            print("    * '()' → \\s*\\w+\\s*\\([^)]*\\) 매치됨")
            print("    * '{}' → \\{[^}]{,400}\\} 매치되어야 함")
            print("    * 문제: '{}'에서 본문이 0자이므로 {,400} 패턴이 매치되어야 함")
            print("    * 가능한 원인: 정규식 엔진의 {,400} 해석 문제")
        
        # 2. 매개변수 생성자 분석
        elif name == "매개변수 생성자":
            print("  - 매개변수 생성자 분석:")
            print("    * 'public Product(String productId, String productName, Double price)' → 매치됨")
            print("    * '{\\n        this.productId = productId;\\n        ...}' → 본문 109자")
            print("    * 문제: 109자는 400자 이하이므로 매치되어야 함")
            print("    * 가능한 원인: 줄바꿈 문자(\\n) 처리 문제")
            print("    * 가능한 원인: 공백 문자 처리 문제")
        
        print()
    
    # 패턴별 테스트
    print("=== 패턴별 테스트 ===")
    test_patterns = [
        ("기본 패턴", r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'),
        ("줄바꿈 고려 패턴", r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'),
        ("공백 고려 패턴", r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'),
        ("단순 패턴", r'public\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}')
    ]
    
    test_case = "public Product() {}"
    print(f"테스트 케이스: {test_case}")
    print()
    
    for pattern_name, pattern in test_patterns:
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        print(f"{pattern_name}: {'매치됨' if match else '매치안됨'}")
        print(f"  패턴: {pattern}")
        print()

if __name__ == "__main__":
    analyze_constructor_pattern()
