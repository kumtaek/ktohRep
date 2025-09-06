#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('phase1')

from phase1.parsers.java.java_parser import JavaParser

def test_java_parser_direct():
    """Java 파서 직접 테스트"""
    print("=== Java 파서 직접 테스트 ===\n")
    
    # Java 파서 초기화
    config = {}
    parser = JavaParser(config)
    
    # VulnerabilityTestService.java 파일 테스트
    file_path = "project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"파일: {file_path}")
        print(f"파일 크기: {len(content)} bytes")
        print(f"첫 200자: {content[:200]}...")
        print()
        
        # 파서 실행
        context = {'file_path': file_path}
        result = parser.parse_content(content, context)
        
        print("=== 파서 결과 ===")
        print(f"클래스: {len(result.get('classes', []))}개")
        print(f"메소드: {len(result.get('methods', []))}개")
        print(f"변수: {len(result.get('variables', []))}개")
        print(f"어노테이션: {len(result.get('annotations', []))}개")
        print(f"SQL 문자열: {len(result.get('sql_strings', []))}개")
        print()
        
        # 메소드 상세 정보
        methods = result.get('methods', [])
        print(f"=== 추출된 메소드들 ({len(methods)}개) ===")
        for i, method in enumerate(methods):
            print(f"{i+1}. {method.get('name', 'Unknown')} - {method.get('return_type', 'Unknown')}")
            print(f"   매개변수: {method.get('parameters', [])}")
            print(f"   수정자: {method.get('modifiers', [])}")
            print()
        
        # 클래스 상세 정보
        classes = result.get('classes', [])
        print(f"=== 추출된 클래스들 ({len(classes)}개) ===")
        for i, cls in enumerate(classes):
            print(f"{i+1}. {cls.get('name', 'Unknown')}")
            print(f"   상속: {cls.get('extends', 'None')}")
            print(f"   구현: {cls.get('implements', [])}")
            print()
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_java_parser_direct()

