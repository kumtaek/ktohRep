#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Context7 기반 개선된 Java 파서 테스트
과다추출 문제 해결 여부 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.java.java_parser import JavaParser
import yaml

def test_context7_java_parser():
    """Context7 기반 개선된 Java 파서 테스트"""
    
    print("=== Context7 기반 개선된 Java 파서 테스트 ===")
    
    # 설정 로드
    config_path = './config/config.yaml'
    if not os.path.exists(config_path):
        print(f"설정 파일이 없습니다: {config_path}")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 초기화
    java_parser = JavaParser(config)
    
    # 테스트용 Java 소스 코드 (과다추출 문제가 있던 샘플)
    test_java_code = '''
package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @PostMapping("/create")
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        try {
            Order order = orderService.createOrder(request);
            return ResponseEntity.ok(order);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        Order order = orderService.findById(id);
        if (order != null) {
            return ResponseEntity.ok(order);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<Order> updateOrder(@PathVariable Long id, @RequestBody OrderRequest request) {
        try {
            Order order = orderService.updateOrder(id, request);
            return ResponseEntity.ok(order);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrder(@PathVariable Long id) {
        try {
            orderService.deleteOrder(id);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    // SQL 쿼리 예제
    private String buildOrderQuery(Long customerId) {
        StringBuilder query = new StringBuilder("SELECT * FROM orders WHERE customer_id = ?");
        if (customerId != null) {
            query.append(" AND customer_id = ").append(customerId);
        }
        return query.toString();
    }
}
'''
    
    # 파싱 실행
    context = {
        'file_path': 'test/OrderController.java',
        'content': test_java_code
    }
    
    result = java_parser.parse_content(test_java_code, context)
    
    # 결과 분석
    print(f"\n=== 파싱 결과 분석 ===")
    print(f"클래스 수: {len(result['classes'])}")
    for i, cls in enumerate(result['classes'], 1):
        print(f"  {i}. {cls['name']}")
    
    print(f"\n메소드 수: {len(result['methods'])}")
    for i, method in enumerate(result['methods'], 1):
        print(f"  {i}. {method['name']}")
        if 'context7_confidence' in method:
            print(f"     신뢰도: {method['context7_confidence']}")
    
    print(f"\nSQL Units 수: {len(result.get('sql_units', []))}")
    for i, sql in enumerate(result.get('sql_units', []), 1):
        print(f"  {i}. {sql['type']}: {sql['sql_content'][:50]}...")
        if 'context7_confidence' in sql:
            print(f"     신뢰도: {sql['context7_confidence']}")
    
    print(f"\n다이나믹 쿼리 수: {len(result.get('dynamic_queries', []))}")
    for i, dq in enumerate(result.get('dynamic_queries', []), 1):
        print(f"  {i}. {dq['type']}: {dq.get('variable', 'N/A')}")
        if 'context7_confidence' in dq:
            print(f"     신뢰도: {dq['context7_confidence']}")
    
    print(f"\n어노테이션 수: {len(result.get('annotations', []))}")
    for i, ann in enumerate(result.get('annotations', []), 1):
        print(f"  {i}. @{ann['name']}")
    
    print(f"\nImport 수: {len(result.get('imports', []))}")
    for i, imp in enumerate(result.get('imports', []), 1):
        print(f"  {i}. {imp}")
    
    # 과다추출 문제 해결 여부 평가
    print(f"\n=== 과다추출 문제 해결 여부 평가 ===")
    
    # 예상 결과 (실제 소스코드 기반)
    expected_classes = 1  # OrderController
    expected_methods = 6  # createOrder, getOrder, updateOrder, deleteOrder, buildOrderQuery + 생성자
    expected_sql_units = 1  # buildOrderQuery 내의 SQL
    expected_dynamic_queries = 3  # StringBuilder init, append, toString
    
    actual_classes = len(result.get('classes', []))
    actual_methods = len(result.get('methods', []))
    actual_sql_units = len(result.get('sql_units', []))
    actual_dynamic_queries = len(result.get('dynamic_queries', []))
    
    print(f"클래스 정확도: {actual_classes}/{expected_classes} ({actual_classes/expected_classes*100:.1f}%)")
    print(f"메소드 정확도: {actual_methods}/{expected_methods} ({actual_methods/expected_methods*100:.1f}%)")
    print(f"SQL Units 정확도: {actual_sql_units}/{expected_sql_units} ({actual_sql_units/expected_sql_units*100:.1f}%)")
    print(f"다이나믹 쿼리 정확도: {actual_dynamic_queries}/{expected_dynamic_queries} ({actual_dynamic_queries/expected_dynamic_queries*100:.1f}%)")
    
    # 과다추출 여부 판단
    class_overextraction = (actual_classes - expected_classes) / expected_classes * 100 if expected_classes > 0 else 0
    method_overextraction = (actual_methods - expected_methods) / expected_methods * 100 if expected_methods > 0 else 0
    sql_overextraction = (actual_sql_units - expected_sql_units) / expected_sql_units * 100 if expected_sql_units > 0 else 0
    
    print(f"\n=== 과다추출 분석 ===")
    print(f"클래스 과다추출: {class_overextraction:.1f}%")
    print(f"메소드 과다추출: {method_overextraction:.1f}%")
    print(f"SQL Units 과다추출: {sql_overextraction:.1f}%")
    
    # 개선 여부 판단
    if class_overextraction <= 5 and method_overextraction <= 5 and sql_overextraction <= 5:
        print(f"\n✅ 과다추출 문제 해결됨! (5% 이내 오차)")
    else:
        print(f"\n❌ 과다추출 문제 여전히 존재 (5% 초과 오차)")
    
    # Context7 기능 활용 여부
    all_items = result.get('methods', []) + result.get('sql_units', []) + result.get('dynamic_queries', [])
    context7_used = any('context7_confidence' in item for item in all_items)
    print(f"\nContext7 기능 활용: {'✅ 사용됨' if context7_used else '❌ 사용 안됨'}")
    
    return result

if __name__ == "__main__":
    test_context7_java_parser()
