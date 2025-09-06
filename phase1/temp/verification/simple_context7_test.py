#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Context7 PRegEx 패턴 간단 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pregex_patterns():
    """Context7 PRegEx 패턴 테스트"""
    
    print("=== Context7 PRegEx 패턴 테스트 ===")
    
    try:
        from pregex.core.pre import Pregex
        from pregex.core.classes import AnyLetter, AnyDigit, AnyWhitespace
        from pregex.core.quantifiers import Optional, OneOrMore
        from pregex.core.operators import Either
        from pregex.core.groups import Capture, Group
        
        print("✅ PRegEx 라이브러리 로드 성공")
        
        # 간단한 Java 식별자 패턴 테스트
        java_identifier = AnyLetter() + Optional(OneOrMore(AnyLetter() | AnyDigit() | '_' | '$'))
        
        # 간단한 메소드 패턴 테스트
        simple_method_pattern = Group(
            Optional(AnyWhitespace()) +
            Capture(java_identifier) +
            Optional(AnyWhitespace()) +
            '(' +
            Optional(Capture(OneOrMore(AnyLetter() | AnyDigit() | AnyWhitespace() | ',' | '<' | '>' | '?' | '&' | '.' | '[' | ']' | '@'))) +
            ')' +
            Optional(AnyWhitespace()) +
            '{'
        )
        
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
        '''
        
        print(f"테스트 코드:\n{test_code}")
        
        # 패턴 매칭 테스트
        matches = simple_method_pattern.get_captures(test_code)
        
        print(f"\n매칭 결과: {len(matches)}개")
        for i, match in enumerate(matches, 1):
            print(f"  {i}. 메소드명: {match[0] if len(match) > 0 else 'N/A'}")
            print(f"     파라미터: {match[1] if len(match) > 1 else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ PRegEx 패턴 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_pregex_patterns()
