#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyBatis 파서 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# phase1 경로를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.mybatis.mybatis_parser import MyBatisParser

def test_mybatis_parser():
    """MyBatis 파서 테스트"""
    
    # 설정 딕셔너리
    config = {
        'parsers': {
            'mybatis': {
                'enabled': True,
                'confidence_threshold': 0.8
            }
        }
    }
    
    # MyBatis 파서 인스턴스 생성
    parser = MyBatisParser(config)
    
    # 테스트할 MyBatis XML 파일 경로
    xml_file_path = Path(__file__).parent.parent.parent / "project" / "sampleSrc" / "src" / "main" / "resources" / "mybatis" / "mapper" / "UserMapper.xml"
    
    if not xml_file_path.exists():
        print(f"파일이 존재하지 않습니다: {xml_file_path}")
        return
    
    # 파일 내용 읽기
    with open(xml_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"=== MyBatis XML 파일 분석: {xml_file_path.name} ===")
    print(f"파일 크기: {len(content)} bytes")
    print(f"라인 수: {len(content.split(chr(10)))}")
    
    # 파싱 실행
    try:
        context = {'file_path': str(xml_file_path)}
        result = parser.parse_sql(content, context)
        
        if result:
            print(f"\n=== 파싱 결과 ===")
            print(f"결과 타입: {type(result)}")
            print(f"결과 키들: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"SQL 단위 수: {len(result.get('sql_units', []))}")
            print(f"테이블 수: {len(result.get('tables', []))}")
            print(f"컬럼 수: {len(result.get('columns', []))}")
            print(f"조인 수: {len(result.get('joins', []))}")
            
            # SQL 단위 상세 정보
            if result.get('sql_units'):
                print(f"\n=== SQL 단위 상세 ===")
                for i, sql_unit in enumerate(result['sql_units'], 1):
                    print(f"{i}. {sql_unit.get('type', 'UNKNOWN')} - {sql_unit.get('id', 'N/A')}")
                    print(f"   SQL: {sql_unit.get('sql', '')[:100]}...")
                    print(f"   테이블: {sql_unit.get('tables', [])}")
                    print()
            else:
                print("SQL 단위가 추출되지 않았습니다.")
                print(f"동적 쿼리 수: {len(result.get('dynamic_queries', []))}")
                print(f"결과 맵 수: {len(result.get('result_maps', []))}")
        else:
            print("파싱 결과가 None입니다.")
            
    except Exception as e:
        print(f"파싱 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mybatis_parser()
