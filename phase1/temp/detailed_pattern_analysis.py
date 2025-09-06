#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def detailed_pattern_analysis():
    """패턴 문제 상세 분석"""
    
    test_case = "public Product() {}"
    
    print("=== 패턴 문제 상세 분석 ===")
    print(f"테스트 케이스: {test_case}")
    print()
    
    # 문제가 있는 패턴
    problematic_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'
    
    # 단계별 분석
    print("=== 단계별 패턴 분석 ===")
    
    # 1단계: public\s+\w+
    step1_pattern = r'public\s+\w+'
    match1 = re.search(step1_pattern, test_case)
    print(f"1단계 'public\\s+\\w+': {'매치됨' if match1 else '매치안됨'}")
    if match1:
        print(f"  매치된 부분: '{match1.group(0)}'")
    
    # 2단계: public\s+\w+\s+\w+
    step2_pattern = r'public\s+\w+\s+\w+'
    match2 = re.search(step2_pattern, test_case)
    print(f"2단계 'public\\s+\\w+\\s+\\w+': {'매치됨' if match2 else '매치안됨'}")
    if match2:
        print(f"  매치된 부분: '{match2.group(0)}'")
    
    # 3단계: public\s+\w+\s+\w+\s*\([^)]*\)
    step3_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)'
    match3 = re.search(step3_pattern, test_case)
    print(f"3단계 'public\\s+\\w+\\s+\\w+\\s*\\([^)]*\\)': {'매치됨' if match3 else '매치안됨'}")
    if match3:
        print(f"  매치된 부분: '{match3.group(0)}'")
    
    # 4단계: public\s+\w+\s+\w+\s*\([^)]*\)\s*\{
    step4_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{'
    match4 = re.search(step4_pattern, test_case)
    print("4단계 'public\\s+\\w+\\s+\\w+\\s*\\([^)]*\\)\\s*\\{': " + ('매치됨' if match4 else '매치안됨'))
    if match4:
        print(f"  매치된 부분: '{match4.group(0)}'")
    
    # 5단계: 전체 패턴
    match5 = re.search(problematic_pattern, test_case)
    print(f"5단계 전체 패턴: {'매치됨' if match5 else '매치안됨'}")
    if match5:
        print(f"  매치된 부분: '{match5.group(0)}'")
    
    print()
    print("=== 문제점 발견 ===")
    print("2단계에서 매치가 실패하는 것을 확인했습니다.")
    print("원인: 'public Product() {}'에서 'Product' 다음에 '()'가 오는데,")
    print("패턴은 'public\\s+\\w+\\s+\\w+'를 기대하고 있습니다.")
    print("즉, 'Product' 다음에 또 다른 단어(\\w+)를 기대하지만 '()'가 와서 매치 실패")
    
    print()
    print("=== 해결책 테스트 ===")
    
    # 해결책 1: 생성자용 별도 패턴
    constructor_pattern = r'public\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'
    match_constructor = re.search(constructor_pattern, test_case)
    print("생성자용 패턴 'public\\s+\\w+\\s*\\([^)]*\\)\\s*\\{[^}]{{,400}}\\}': " + ('매치됨' if match_constructor else '매치안됨'))
    
    # 해결책 2: 메서드용 패턴
    method_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,400}\}'
    method_test = "public String getProductId() { return productId; }"
    match_method = re.search(method_pattern, method_test)
    print("메서드용 패턴 (getProductId 테스트): " + ('매치됨' if match_method else '매치안됨'))
    
    print()
    print("=== 결론 ===")
    print("문제의 근본 원인:")
    print("1. 생성자: 'public Product() {}' - 클래스명 다음에 바로 '()'가 옴")
    print("2. 메서드: 'public String getProductId() {}' - 반환타입 다음에 메서드명이 옴")
    print("3. 현재 패턴은 메서드 형태만 고려하고 생성자 형태를 고려하지 않음")

if __name__ == "__main__":
    detailed_pattern_analysis()
