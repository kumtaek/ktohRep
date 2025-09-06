#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from phase1.parsers.mybatis.mybatis_parser import MyBatisParser
from phase1.parsers.parser_factory import ParserFactory

def test_xml_parsing():
    """XML 파일 직접 파싱 테스트"""
    print("=== XML 파일 직접 파싱 테스트 ===\n")
    
    # 설정 로드
    config = {
        'processing': {'max_workers': 4},
        'confidence': {'default': 0.8}
    }
    
    # MyBatis 파서 생성
    mybatis_parser = MyBatisParser(config)
    
    # XML 파일들 테스트
    xml_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/ProductMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/IntegratedMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/TestJoinMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/mapper/UserMapper.xml"
    ]
    
    total_queries = 0
    
    for xml_file in xml_files:
        if not os.path.exists(xml_file):
            print(f"파일이 존재하지 않습니다: {xml_file}")
            continue
            
        print(f"=== {xml_file} ===")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 컨텍스트 정보
            context = {
                'file_path': xml_file,
                'default_schema': 'DEFAULT'
            }
            
            # MyBatis 파서로 파싱
            result = mybatis_parser.parse_content(content, context)
            
            # SQL 구문 추출
            sql_statements = result.get('sql_statements', [])
            print(f"파싱된 SQL 구문 수: {len(sql_statements)}")
            
            for i, stmt in enumerate(sql_statements, 1):
                print(f"  {i}. {stmt['type']}: {stmt['id']}")
                print(f"     - 테이블: {stmt.get('tables', [])}")
                print(f"     - 컬럼: {stmt.get('columns', [])}")
                print(f"     - 파라미터: {stmt.get('parameters', [])}")
            
            total_queries += len(sql_statements)
            print()
            
        except Exception as e:
            print(f"파싱 오류: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print(f"=== 전체 요약 ===")
    print(f"총 파싱된 SQL 구문 수: {total_queries}개")
    
    return total_queries

def test_parser_factory():
    """파서 팩토리를 통한 XML 파싱 테스트"""
    print("\n=== 파서 팩토리를 통한 XML 파싱 테스트 ===\n")
    
    # 설정 로드
    config = {
        'processing': {'max_workers': 4},
        'confidence': {'default': 0.8}
    }
    
    # 파서 팩토리 생성
    factory = ParserFactory(config)
    
    # XML 파일들 테스트
    xml_files = [
        "project/sampleSrc/src/main/resources/mybatis/OrderMapper.xml",
        "project/sampleSrc/src/main/resources/mybatis/UserMapper.xml"
    ]
    
    total_queries = 0
    
    for xml_file in xml_files:
        if not os.path.exists(xml_file):
            print(f"파일이 존재하지 않습니다: {xml_file}")
            continue
            
        print(f"=== {xml_file} ===")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 파서 자동 선택
            parser = factory.auto_detect_parser(content, 'xml')
            
            if parser:
                print(f"선택된 파서: {parser._get_parser_type()}")
                
                # 컨텍스트 정보
                context = {
                    'file_path': xml_file,
                    'default_schema': 'DEFAULT'
                }
                
                # 파싱 실행
                result = parser.parse_content(content, context)
                
                # SQL 구문 추출
                sql_statements = result.get('sql_statements', [])
                print(f"파싱된 SQL 구문 수: {len(sql_statements)}")
                
                for i, stmt in enumerate(sql_statements, 1):
                    print(f"  {i}. {stmt['type']}: {stmt['id']}")
                
                total_queries += len(sql_statements)
            else:
                print("적절한 파서를 찾을 수 없습니다.")
            
            print()
            
        except Exception as e:
            print(f"파싱 오류: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print(f"=== 전체 요약 ===")
    print(f"총 파싱된 SQL 구문 수: {total_queries}개")
    
    return total_queries

if __name__ == "__main__":
    # 직접 파싱 테스트
    direct_result = test_xml_parsing()
    
    # 파서 팩토리 테스트
    factory_result = test_parser_factory()
    
    print(f"\n=== 최종 결과 ===")
    print(f"직접 파싱: {direct_result}개")
    print(f"파서 팩토리: {factory_result}개")

