#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def show_400_case():
    """400자 짜리 사례 상세 보기"""
    
    # 400자 짜리 사례
    case_400 = """public String extremelyLongMethod(@RequestParam Map<String,String> searchParams, Model model) {
        // 매우 복잡한 비즈니스 로직이 여기에 들어감
        // 데이터베이스 조회
        // 비즈니스 규칙 적용
        // 복잡한 계산
        // 추가적인 처리
        // 로그 기록
        // 알림 발송
        // 결과 검증
        // 최종 결과 반환
        // 더 많은 로직
        // 추가 검증
        // 최종 처리
        // 추가적인 비즈니스 로직
        // 복잡한 데이터 처리
        // 외부 API 호출
        // 결과 변환
        // 로그 기록
        // 알림 발송
        // 최종 검증
        return "extremely long result";
    }"""
    
    # 본문 길이 계산
    brace_start = case_400.find('{')
    brace_end = case_400.rfind('}')
    if brace_start != -1 and brace_end != -1:
        body = case_400[brace_start+1:brace_end]
        body_length = len(body)
    else:
        body_length = 0
    
    print("=== 400자 짜리 사례 상세 ===")
    print(f"이름: 긴 메서드2")
    print(f"본문 길이: {body_length}자")
    print("전체 내용:")
    print(case_400)
    print()
    print("=== 본문만 ===")
    print(f"본문: '{body}'")
    print(f"본문 길이: {len(body)}자")

if __name__ == "__main__":
    show_400_case()
