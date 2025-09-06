#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRegEx 사용법 테스트
"""

try:
    from pregex.core.classes import AnyLetter, AnyDigit, AnyWhitespace, AnyFrom
    from pregex.core.quantifiers import Optional, OneOrMore, AtLeastAtMost
    from pregex.core.groups import Capture, Group
    from pregex.core.operators import Either
    print("PRegEx 라이브러리 로드 성공")
    
    # AnyFrom 사용법 테스트
    print("\n=== AnyFrom 사용법 테스트 ===")
    
    # 방법 1: 개별 문자열
    try:
        pattern1 = AnyFrom('public', 'private', 'protected')
        print("방법 1 성공: AnyFrom('public', 'private', 'protected')")
    except Exception as e:
        print(f"방법 1 실패: {e}")
    
    # 방법 2: 리스트
    try:
        pattern2 = AnyFrom(['public', 'private', 'protected'])
        print("방법 2 성공: AnyFrom(['public', 'private', 'protected'])")
    except Exception as e:
        print(f"방법 2 실패: {e}")
    
    # 방법 3: Either 사용
    try:
        pattern3 = Either('public', 'private', 'protected')
        print("방법 3 성공: Either('public', 'private', 'protected')")
    except Exception as e:
        print(f"방법 3 실패: {e}")
    
    # 방법 4: 단순 문자열
    try:
        pattern4 = 'public' | 'private' | 'protected'
        print("방법 4 성공: 'public' | 'private' | 'protected'")
    except Exception as e:
        print(f"방법 4 실패: {e}")
    
    print("\n=== 패턴 컴파일 테스트 ===")
    
    # 성공한 방법으로 패턴 컴파일 테스트
    try:
        test_pattern = AnyFrom('public', 'private', 'protected')
        compiled = test_pattern.compile()
        print("패턴 컴파일 성공")
        
        # 테스트 매칭
        test_text = "public class Test"
        matches = list(compiled.finditer(test_text))
        print(f"매칭 결과: {len(matches)}개")
        for match in matches:
            print(f"  매칭: '{match.group()}'")
            
    except Exception as e:
        print(f"패턴 컴파일 실패: {e}")

except ImportError as e:
    print(f"PRegEx 라이브러리 로드 실패: {e}")
except Exception as e:
    print(f"예상치 못한 오류: {e}")


