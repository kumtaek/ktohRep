#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import yaml
sys.path.append('.')

from parsers.java.java_parser import JavaParser

def simple_java_test():
    print("=== 간단한 Java 파싱 테스트 ===")
    
    # Config 로드
    config_path = "config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 인스턴스 생성
    parser = JavaParser(config)
    
    # 테스트할 Java 파일
    test_file = "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java"
    
    if not os.path.exists(test_file):
        print(f"파일이 없습니다: {test_file}")
        return
        
    # 파일 내용 읽기
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"파일 크기: {len(content)} 문자")
    
    # 파서로 분석
    try:
        result = parser.parse_content(content, test_file)
        print(f"파싱 성공!")
        
        # 주요 결과만 출력
        print(f"메소드 개수: {len(result.get('methods', []))}")
        print(f"클래스 개수: {len(result.get('classes', []))}")
        print(f"SQL 유닛 개수: {len(result.get('sql_units', []))}")
        print(f"어노테이션 개수: {len(result.get('annotations', []))}")
        print(f"SQL 문자열 개수: {len(result.get('sql_strings', []))}")
        
        # 메소드 몇 개 출력
        methods = result.get('methods', [])
        if methods:
            print(f"\n첫 번째 메소드: {methods[0]}")
        
        # SQL 문자열 몇 개 출력
        sql_strings = result.get('sql_strings', [])
        if sql_strings:
            print(f"\n첫 번째 SQL 문자열: {sql_strings[0]}")
                
    except Exception as e:
        print(f"파싱 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_java_test()

