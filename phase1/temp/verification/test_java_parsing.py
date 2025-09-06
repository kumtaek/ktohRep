#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import yaml
sys.path.append('.')

from parsers.java.java_parser import JavaParser

def test_java_parsing():
    print("=== Java 파싱 테스트 ===")
    
    # Config 로드
    config_path = "config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 인스턴스 생성
    parser = JavaParser(config)
    print(f"Java 파서 생성 완료: {type(parser)}")
    
    # 테스트할 Java 파일들
    test_files = [
        "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java",
        "../project/sampleSrc/src/main/java/com/example/mapper/UserMapper.java",
        "../project/sampleSrc/src/main/java/com/example/service/UserService.java"
    ]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"파일이 없습니다: {test_file}")
            continue
            
        print(f"\n=== {test_file} ===")
        
        # 파일 내용 읽기
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"파일 크기: {len(content)} 문자")
        
        # 파서로 분석
        try:
            result = parser.parse_content(content, test_file)
            print(f"파싱 결과 타입: {type(result)}")
            
            # result는 딕셔너리이므로 키로 접근
            if 'methods' in result:
                print(f"메소드 개수: {len(result['methods'])}")
                for i, method in enumerate(result['methods'][:3]):  # 처음 3개만 출력
                    print(f"  메소드 {i+1}: {method}")
            
            if 'sql_units' in result:
                print(f"SQL 유닛 개수: {len(result['sql_units'])}")
                for i, sql_unit in enumerate(result['sql_units'][:3]):  # 처음 3개만 출력
                    print(f"  SQL 유닛 {i+1}: {sql_unit}")
            
            if 'classes' in result:
                print(f"클래스 개수: {len(result['classes'])}")
                for i, class_info in enumerate(result['classes'][:3]):  # 처음 3개만 출력
                    print(f"  클래스 {i+1}: {class_info}")
            
            # 전체 결과 키 확인
            print(f"결과 키들: {list(result.keys())}")
                    
        except Exception as e:
            print(f"파싱 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_java_parsing()
