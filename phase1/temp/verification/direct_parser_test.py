#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Java 파서 직접 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.java.java_parser import JavaParser
import yaml

def test_java_parser_directly():
    """Java 파서 직접 테스트"""
    
    print("=== Java 파서 직접 테스트 ===")
    
    # 설정 로드
    config_path = './config/config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 초기화
    java_parser = JavaParser(config)
    
    # 테스트용 Java 소스 코드
    test_java_code = '''
    @PostMapping("/create")
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        return ResponseEntity.ok(order);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        return ResponseEntity.ok(order);
    }
    
    private String buildOrderQuery(Long customerId) {
        StringBuilder query = new StringBuilder("SELECT * FROM orders WHERE customer_id = ?");
        return query.toString();
    }
    '''
    
    print(f"테스트 코드:\n{test_java_code}")
    
    # 간단한 패턴 직접 테스트
    import re
    simple_pattern = re.compile(r'(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    matches = simple_pattern.finditer(test_java_code)
    
    print(f"\n=== 간단한 패턴 직접 테스트 ===")
    count = 0
    for match in matches:
        count += 1
        print(f"  {count}. {match.group(1)}")
    print(f"총 {count}개 메소드 추출")
    
    # Java 파서의 간단한 패턴 테스트
    print(f"\n=== Java 파서의 간단한 패턴 테스트 ===")
    matches2 = java_parser.simple_method_pattern.finditer(test_java_code)
    count2 = 0
    for match in matches2:
        count2 += 1
        print(f"  {count2}. {match.group(1)}")
    print(f"총 {count2}개 메소드 추출")
    
    # Java 파서의 메소드 추출 테스트
    print(f"\n=== Java 파서의 메소드 추출 테스트 ===")
    methods = java_parser._extract_methods(test_java_code)
    print(f"추출된 메소드 수: {len(methods)}")
    for i, method in enumerate(methods, 1):
        print(f"  {i}. {method['name']}")

if __name__ == "__main__":
    test_java_parser_directly()
