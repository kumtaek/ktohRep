#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_hybrid_pattern():
    """하이브리드 패턴 테스트"""
    
    test_cases = [
        # 어노테이션이 있는 메서드들
        "@Override\npublic String toString() { return \"Product\"; }",
        "@RequestMapping(\"/products\")\npublic String listProducts() { return \"list\"; }",
        "@Transactional\npublic void saveProduct(Product product) { /* save logic */ }",
        "@Autowired\npublic void setService(ProductService service) { this.service = service; }",
        
        # 어노테이션이 없는 메서드들
        "public String getProductId() { return productId; }",
        "public void setProductId(String productId) { this.productId = productId; }",
        "public Product() {}",
        "public Product(String id) { this.id = id; }",
        
        # 복합 케이스들
        "@Override\npublic static final String getComplexValue() { return \"complex\"; }",
        "@Transactional\npublic synchronized void complexMethod() { /* complex logic */ }",
        
        # 제네릭 메서드들
        "public <T> T genericMethod(T input) { return input; }",
        "@SuppressWarnings(\"unchecked\")\npublic List<String> getStringList() { return new ArrayList<>(); }"
    ]
    
    # 하이브리드 패턴들
    pattern_with_annotation = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    pattern_without_annotation = r'public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    # 생성자 패턴들
    constructor_with_annotation = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    constructor_without_annotation = r'public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    print("=== 하이브리드 패턴 테스트 ===")
    print(f"어노테이션 있음 패턴: {pattern_with_annotation}")
    print(f"어노테이션 없음 패턴: {pattern_without_annotation}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 케이스 {i} ---")
        print(f"내용: {test_case[:80]}{'...' if len(test_case) > 80 else ''}")
        
        # 어노테이션 있음 패턴 테스트
        match_with_annotation = re.search(pattern_with_annotation, test_case, re.IGNORECASE | re.DOTALL)
        
        # 어노테이션 없음 패턴 테스트
        match_without_annotation = re.search(pattern_without_annotation, test_case, re.IGNORECASE | re.DOTALL)
        
        # 생성자 패턴 테스트
        match_constructor_with = re.search(constructor_with_annotation, test_case, re.IGNORECASE | re.DOTALL)
        match_constructor_without = re.search(constructor_without_annotation, test_case, re.IGNORECASE | re.DOTALL)
        
        # 결과 분석
        method_match = match_with_annotation or match_without_annotation
        constructor_match = match_constructor_with or match_constructor_without
        
        if method_match or constructor_match:
            result = "매치됨 ✅"
        else:
            result = "매치안됨 ❌"
        
        print(f"어노테이션 있음: {'매치됨' if match_with_annotation else '매치안됨'}")
        print(f"어노테이션 없음: {'매치됨' if match_without_annotation else '매치안됨'}")
        print(f"생성자 (있음): {'매치됨' if match_constructor_with else '매치안됨'}")
        print(f"생성자 (없음): {'매치됨' if match_constructor_without else '매치안됨'}")
        print(f"최종 결과: {result}")
        
        # 중복 매치 확인
        if (match_with_annotation and match_without_annotation) or (match_constructor_with and match_constructor_without):
            print("⚠️  중복 매치 발생!")
        
        print()
    
    print("=== 하이브리드 패턴 장단점 분석 ===")
    print()
    print("✅ 장점:")
    print("1. 어노테이션이 있는 메서드도 매치됨")
    print("2. 어노테이션이 없는 메서드도 매치됨")
    print("3. 기존 기능 유지")
    print("4. 새로운 기능 추가")
    print()
    print("❌ 단점:")
    print("1. 패턴이 2개로 늘어남 (복잡도 증가)")
    print("2. 중복 매치 가능성")
    print("3. 성능 저하 (2번의 정규식 매치)")
    print("4. 코드 복잡도 증가")
    print()
    print("🔧 개선 방안:")
    print("1. 중복 매치 방지 로직 추가")
    print("2. 성능 최적화")
    print("3. 패턴 통합 시도")

if __name__ == "__main__":
    test_hybrid_pattern()
