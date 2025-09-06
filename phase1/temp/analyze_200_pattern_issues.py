#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def analyze_200_pattern_issues():
    """200자 이하 패턴 문제 분석"""
    
    # 실제 Java 파일에서 추출한 다양한 케이스들
    test_cases = [
        # 빈 생성자
        "public Product() {}",
        
        # 매개변수 생성자
        "public Product(String productId, String productName, Double price) {\n        this.productId = productId;\n        this.productName = productName;\n        this.price = price;\n    }",
        
        # Getter/Setter
        "public String getProductId() { return productId; }",
        "public void setProductId(String productId) { this.productId = productId; }",
        
        # 비즈니스 메서드들 (다양한 길이)
        "public String searchProducts(@RequestParam Map<String,String> searchParams, Model model) {\n        // 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 결과 반환\n        return \"success\";\n    }",
        
        # 매우 긴 메서드들
        "public String veryLongBusinessMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        return \"very long result\";\n    }",
        
        # 더 긴 메서드
        "public String extremelyLongMethod(@RequestParam Map<String,String> searchParams, Model model) {\n        // 매우 복잡한 비즈니스 로직이 여기에 들어감\n        // 데이터베이스 조회\n        // 비즈니스 규칙 적용\n        // 복잡한 계산\n        // 추가적인 처리\n        // 로그 기록\n        // 알림 발송\n        // 결과 검증\n        // 최종 결과 반환\n        // 더 많은 로직\n        // 추가 검증\n        // 최종 처리\n        // 추가적인 비즈니스 로직\n        // 복잡한 데이터 처리\n        // 외부 API 호출\n        // 결과 변환\n        // 로그 기록\n        // 알림 발송\n        // 최종 검증\n        return \"extremely long result\";\n    }"
    ]
    
    # 200자 이하 패턴
    pattern = r'public\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]{,200}\}'
    
    print("=== 200자 이하 패턴 문제 분석 ===")
    print("패턴:", pattern)
    print()
    
    non_matching_cases = []
    matching_cases = []
    over_200_cases = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- 케이스 {i} ---")
        print("내용:", test_case[:100] + "..." if len(test_case) > 100 else test_case)
        
        # 본문 길이 확인
        brace_start = test_case.find('{')
        brace_end = test_case.rfind('}')
        if brace_start != -1 and brace_end != -1:
            body = test_case[brace_start+1:brace_end]
            body_length = len(body)
            print("본문 길이:", body_length, "자")
            
            # 200자 초과 케이스 수집
            if body_length > 200:
                over_200_cases.append({
                    'case': i,
                    'body_length': body_length,
                    'content': test_case[:100] + "..."
                })
        else:
            body_length = 0
            print("본문 길이: 0자 (중괄호 없음)")
        
        # 패턴 매치 시도
        match = re.search(pattern, test_case, re.IGNORECASE | re.DOTALL)
        
        if match:
            print("결과: 매치됨")
            matching_cases.append({
                'case': i,
                'body_length': body_length,
                'content': test_case[:100] + "..." if len(test_case) > 100 else test_case
            })
        else:
            print("결과: 매치되지 않음 ⭐")
            non_matching_cases.append({
                'case': i,
                'body_length': body_length,
                'content': test_case[:100] + "..." if len(test_case) > 100 else test_case
            })
        print()
    
    print("=== 분석 결과 ===")
    print(f"매치된 케이스: {len(matching_cases)}개")
    print(f"매치 안된 케이스: {len(non_matching_cases)}개")
    print(f"200자 초과 케이스: {len(over_200_cases)}개")
    print()
    
    print("=== 매치 안된 케이스 상세 ===")
    for case in non_matching_cases:
        print(f"케이스 {case['case']}: {case['body_length']}자 - {case['content']}")
        if case['body_length'] <= 200:
            print("  → 200자 이하인데 매치 안됨 (문제)")
        else:
            print("  → 200자 초과이므로 매치 안됨 (올바름)")
    print()
    
    print("=== 200자 초과 케이스 상세 ===")
    if over_200_cases:
        max_length = max(case['body_length'] for case in over_200_cases)
        print(f"최대 길이: {max_length}자")
        print("200자 초과 케이스들:")
        for case in over_200_cases:
            print(f"  케이스 {case['case']}: {case['body_length']}자 - {case['content']}")
    else:
        print("200자 초과 케이스가 없습니다.")

if __name__ == "__main__":
    analyze_200_pattern_issues()
