#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_side_effects():
    """수정으로 인한 부작용 테스트"""
    
    # 다양한 케이스들
    test_cases = [
        # 어노테이션이 있는 메서드들
        "@Override\npublic String toString() { return \"Product\"; }",
        "@RequestMapping(\"/products\")\npublic String listProducts() { return \"list\"; }",
        "@Transactional\npublic void saveProduct(Product product) { /* save logic */ }",
        
        # static 메서드들
        "public static String getInstance() { return \"instance\"; }",
        "public static final String CONSTANT = \"value\";",
        
        # final 메서드들
        "public final String getFinalValue() { return \"final\"; }",
        "public final static String STATIC_FINAL = \"static_final\";",
        
        # synchronized 메서드들
        "public synchronized void syncMethod() { /* sync logic */ }",
        "public static synchronized String getSyncValue() { return \"sync\"; }",
        
        # 복합 케이스들
        "@Override\npublic static final String getComplexValue() { return \"complex\"; }",
        "@Transactional\npublic synchronized void complexMethod() { /* complex logic */ }",
        
        # 제네릭 메서드들
        "public <T> T genericMethod(T input) { return input; }",
        "public List<String> getStringList() { return new ArrayList<>(); }",
        
        # 기존에 잘 작동하던 케이스들
        "public String getProductId() { return productId; }",
        "public void setProductId(String productId) { this.productId = productId; }",
        "public Product() {}",
        "public Product(String id) { this.id = id; }"
    ]
    
    # 기존 복잡한 패턴
    old_constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    old_method_pattern = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    # 새로운 단순한 패턴
    new_constructor_pattern = r'public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    new_method_pattern = r'public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    print("=== 수정으로 인한 부작용 테스트 ===")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 케이스 {i} ---")
        print(f"내용: {test_case[:80]}{'...' if len(test_case) > 80 else ''}")
        
        # 기존 패턴 테스트
        old_constructor_match = re.search(old_constructor_pattern, test_case, re.IGNORECASE | re.DOTALL)
        old_method_match = re.search(old_method_pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        # 새로운 패턴 테스트
        new_constructor_match = re.search(new_constructor_pattern, test_case, re.IGNORECASE | re.DOTALL)
        new_method_match = re.search(new_method_pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        # 결과 비교
        old_result = "매치됨" if (old_constructor_match or old_method_match) else "매치안됨"
        new_result = "매치됨" if (new_constructor_match or new_method_match) else "매치안됨"
        
        print(f"기존 패턴: {old_result}")
        print(f"새로운 패턴: {new_result}")
        
        # 부작용 분석
        if old_result == "매치됨" and new_result == "매치안됨":
            print("⚠️  부작용: 기존에 매치되던 것이 매치안됨")
        elif old_result == "매치안됨" and new_result == "매치됨":
            print("✅ 개선: 기존에 매치안되던 것이 매치됨")
        elif old_result == new_result:
            print("✅ 동일: 결과가 동일함")
        else:
            print("❓ 예상외: 다른 결과")
        
        print()

if __name__ == "__main__":
    test_side_effects()
