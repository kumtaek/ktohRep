#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def debug_getter_pattern():
    """getter 패턴 디버깅"""
    
    test_case = "public String getProductId() { return productId; }"
    
    print("=== getter 패턴 디버깅 ===")
    print(f"테스트 케이스: {test_case}")
    print()
    
    # 현재 패턴
    current_pattern = r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{,500}\}'
    
    print(f"현재 패턴: {current_pattern}")
    print()
    
    # 단계별 분석
    print("=== 단계별 패턴 분석 ===")
    
    # 1단계: public\s+
    step1_pattern = r'public\s+'
    match1 = re.search(step1_pattern, test_case)
    print(f"1단계 'public\\s+': {'매치됨' if match1 else '매치안됨'}")
    if match1:
        print(f"  매치된 부분: '{match1.group(0)}'")
    
    # 2단계: public\s+\w+
    step2_pattern = r'public\s+\w+'
    match2 = re.search(step2_pattern, test_case)
    print(f"2단계 'public\\s+\\w+': {'매치됨' if match2 else '매치안됨'}")
    if match2:
        print(f"  매치된 부분: '{match2.group(0)}'")
    
    # 3단계: public\s+\w+\s+\w+
    step3_pattern = r'public\s+\w+\s+\w+'
    match3 = re.search(step3_pattern, test_case)
    print(f"3단계 'public\\s+\\w+\\s+\\w+': {'매치됨' if match3 else '매치안됨'}")
    if match3:
        print(f"  매치된 부분: '{match3.group(0)}'")
    
    # 4단계: public\s+\w+\s+\w+\s*\([^)]*\)
    step4_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)'
    match4 = re.search(step4_pattern, test_case)
    print(f"4단계 'public\\s+\\w+\\s+\\w+\\s*\\([^)]*\\)': {'매치됨' if match4 else '매치안됨'}")
    if match4:
        print(f"  매치된 부분: '{match4.group(0)}'")
    
    # 5단계: public\s+\w+\s+\w+\s*\([^)]*\)\s*\{
    step5_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{'
    match5 = re.search(step5_pattern, test_case)
    print(f"5단계 'public\\s+\\w+\\s+\\w+\\s*\\([^)]*\\)\\s*\\{': {'매치됨' if match5 else '매치안됨'}")
    if match5:
        print(f"  매치된 부분: '{match5.group(0)}'")
    
    # 6단계: 전체 패턴
    match6 = re.search(current_pattern, test_case, re.IGNORECASE | re.DOTALL)
    print(f"6단계 전체 패턴: {'매치됨' if match6 else '매치안됨'}")
    if match6:
        print(f"  매치된 부분: '{match6.group(0)}'")
    
    print()
    print("=== 문제점 분석 ===")
    
    # 각 단계별 매치 결과 분석
    if match1 and match2 and match3 and match4 and match5:
        print("1-5단계 모두 매치됨")
        print("문제는 6단계 전체 패턴에 있을 가능성")
        
        # 본문 길이 확인
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            print(f"본문: '{body}'")
            print(f"본문 길이: {len(body)}자")
            
            if len(body) <= 500:
                print("본문이 500자 이하이므로 매치되어야 함")
                print("문제: {,500} 패턴이 작동하지 않음")
            else:
                print("본문이 500자 초과이므로 매치되지 않아야 함")
    else:
        print("1-5단계 중 매치 실패 단계가 있음")
        if not match1:
            print("1단계 실패: 'public ' 매치 실패")
        if not match2:
            print("2단계 실패: 'public String' 매치 실패")
        if not match3:
            print("3단계 실패: 'public String getProductId' 매치 실패")
        if not match4:
            print("4단계 실패: 'public String getProductId()' 매치 실패")
        if not match5:
            print("5단계 실패: 'public String getProductId() {' 매치 실패")
    
    print()
    print("=== 해결책 테스트 ===")
    
    # 간단한 패턴으로 테스트
    simple_pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,500}\}'
    match_simple = re.search(simple_pattern, test_case, re.IGNORECASE | re.DOTALL)
    print(f"간단한 패턴: {'매치됨' if match_simple else '매치안됨'}")
    if match_simple:
        print(f"  매치된 부분: '{match_simple.group(0)}'")

if __name__ == "__main__":
    debug_getter_pattern()
