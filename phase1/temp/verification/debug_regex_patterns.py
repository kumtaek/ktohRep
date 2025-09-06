#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def debug_regex_patterns():
    """정규식 패턴 디버깅"""
    print("=== 정규식 패턴 디버깅 ===\n")
    
    # VulnerabilityTestService.java 파일 내용
    file_path = "project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"파일: {file_path}")
        print(f"파일 크기: {len(content)} bytes")
        print()
        
        # Java 파서에서 사용하는 패턴들
        patterns = [
            # 1. 일반 메소드 패턴
            r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{',
            # 2. 인터페이스 메소드 패턴
            r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|default)?\s+(?!new\s)(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;',
        ]
        
        for i, pattern in enumerate(patterns, 1):
            print(f"=== 패턴 {i} ===")
            print(f"패턴: {pattern}")
            
            try:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                match_list = list(matches)
                print(f"매치 수: {len(match_list)}")
                
                for j, match in enumerate(match_list[:3]):  # 처음 3개만 출력
                    print(f"  {j+1}. 그룹 수: {len(match.groups())}")
                    print(f"     전체 매치: {match.group(0)[:100]}...")
                    for k, group in enumerate(match.groups()):
                        print(f"     그룹 {k+1}: {group}")
                    print()
                
                if len(match_list) > 3:
                    print(f"  ... 외 {len(match_list)-3}개")
                
            except Exception as e:
                print(f"패턴 오류: {e}")
            
            print()
        
        # 간단한 패턴으로 테스트
        print("=== 간단한 패턴 테스트 ===")
        simple_pattern = r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        print(f"간단한 패턴: {simple_pattern}")
        
        try:
            matches = re.finditer(simple_pattern, content, re.IGNORECASE | re.DOTALL)
            match_list = list(matches)
            print(f"매치 수: {len(match_list)}")
            
            for j, match in enumerate(match_list[:3]):
                print(f"  {j+1}. {match.group(1)} {match.group(2)}({match.group(3)})")
            
        except Exception as e:
            print(f"간단한 패턴 오류: {e}")
        
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_regex_patterns()

