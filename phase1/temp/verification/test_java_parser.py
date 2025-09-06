#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import yaml
sys.path.append('.')

from parsers.java.java_parser import JavaParser

def test_java_parser():
    print("=== Java 파서 테스트 ===")
    
    # Config 로드
    config_path = "config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 인스턴스 생성
    parser = JavaParser(config)
    print(f"Java 파서 생성 완료: {type(parser)}")
    
    # 테스트할 Java 파일 경로
    test_file = "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java"
    
    if not os.path.exists(test_file):
        print(f"테스트 파일이 없습니다: {test_file}")
        return
    
    # 파일 내용 읽기
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n파일 내용 길이: {len(content)} 문자")
    print(f"파일 내용 미리보기 (처음 500자):")
    print(content[:500])
    
    # 파서로 분석
    try:
        result = parser.parse_content(content, test_file)
        print(f"\n파싱 결과:")
        print(f"타입: {type(result)}")
        print(f"내용: {result}")
        
        if hasattr(result, 'methods'):
            print(f"메소드 개수: {len(result.methods)}")
            for i, method in enumerate(result.methods[:3]):  # 처음 3개만 출력
                print(f"  메소드 {i+1}: {method}")
        
        if hasattr(result, 'sql_units'):
            print(f"SQL 유닛 개수: {len(result.sql_units)}")
            for i, sql_unit in enumerate(result.sql_units[:3]):  # 처음 3개만 출력
                print(f"  SQL 유닛 {i+1}: {sql_unit}")
                
    except Exception as e:
        print(f"파싱 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_java_parser()
