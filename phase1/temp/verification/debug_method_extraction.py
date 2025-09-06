#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
메소드 추출 디버깅 테스트
"""

import re

def test_method_patterns():
    """메소드 패턴 테스트"""
    
    print("=== 메소드 추출 패턴 디버깅 ===")
    
    # 테스트 Java 코드
    test_code = '''
    @PostMapping("/create")
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        return ResponseEntity.ok(order);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        return ResponseEntity.ok(order);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<Order> updateOrder(@PathVariable Long id, @RequestBody OrderRequest request) {
        return ResponseEntity.ok(order);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrder(@PathVariable Long id) {
        return ResponseEntity.ok().build();
    }
    
    private String buildOrderQuery(Long customerId) {
        StringBuilder query = new StringBuilder("SELECT * FROM orders WHERE customer_id = ?");
        return query.toString();
    }
    '''
    
    print(f"테스트 코드:\n{test_code}")
    
    # 패턴 1: 복잡한 패턴
    pattern1 = re.compile(
        r'(?:@\w+(?:\([^)]*\))?\s*)*\s*'  # 어노테이션 (선택적)
        r'(?:public|private|protected)?\s*'  # 접근 제어자 (선택적)
        r'(?:static|final|abstract|synchronized\s+)*'  # 기타 수식자
        r'(?:[\w<>\[\],\s?&\.]+\s+)?'  # 반환 타입
        r'(\w+)\s*'  # 메소드명
        r'\([^)]*\)\s*'  # 파라미터
        r'(?:throws\s+[\w\s,\.]+)?\s*'  # 예외 선언
        r'[;{]',  # 메소드 본문 시작
        re.MULTILINE | re.DOTALL
    )
    
    # 패턴 2: 간단한 패턴
    pattern2 = re.compile(
        r'(\w+)\s*\([^)]*\)\s*\{',  # 메소드명(파라미터) {
        re.MULTILINE
    )
    
    # 패턴 3: 더 간단한 패턴
    pattern3 = re.compile(
        r'(\w+)\s*\(',  # 메소드명(
        re.MULTILINE
    )
    
    print(f"\n=== 패턴 1 (복잡한 패턴) ===")
    matches1 = pattern1.finditer(test_code)
    count1 = 0
    for match in matches1:
        count1 += 1
        print(f"  {count1}. {match.group(1)}")
    print(f"총 {count1}개 메소드 추출")
    
    print(f"\n=== 패턴 2 (간단한 패턴) ===")
    matches2 = pattern2.finditer(test_code)
    count2 = 0
    for match in matches2:
        count2 += 1
        print(f"  {count2}. {match.group(1)}")
    print(f"총 {count2}개 메소드 추출")
    
    print(f"\n=== 패턴 3 (더 간단한 패턴) ===")
    matches3 = pattern3.finditer(test_code)
    count3 = 0
    for match in matches3:
        count3 += 1
        print(f"  {count3}. {match.group(1)}")
    print(f"총 {count3}개 메소드 추출")
    
    # 키워드 필터링 테스트
    java_keywords = {
        'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
        'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
        'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
        'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
        'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
        'volatile', 'while', 'true', 'false', 'null'
    }
    
    print(f"\n=== 패턴 3 + 키워드 필터링 ===")
    matches3_filtered = pattern3.finditer(test_code)
    count3_filtered = 0
    for match in matches3_filtered:
        method_name = match.group(1)
        if method_name not in java_keywords:
            count3_filtered += 1
            print(f"  {count3_filtered}. {method_name}")
    print(f"총 {count3_filtered}개 메소드 추출 (키워드 제외)")

if __name__ == "__main__":
    test_method_patterns()
