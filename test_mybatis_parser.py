#!/usr/bin/env python3
"""MyBatis XML 파서 테스트 스크립트"""

import sys
from pathlib import Path
import yaml

# Add phase1 to path
phase1_root = Path(__file__).parent / "phase1"
sys.path.insert(0, str(phase1_root))

from parsers.jsp_mybatis_parser import JspMybatisParser

def test_mybatis_parser():
    """IntegratedMapper.xml 파싱 테스트"""
    
    # 설정 로드
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 파서 초기화
    parser = JspMybatisParser(config)
    
    # IntegratedMapper.xml 파싱
    xml_file = Path(__file__).parent / "project" / "sampleSrc" / "src" / "main" / "resources" / "mybatis" / "IntegratedMapper.xml"
    
    print(f"파싱할 파일: {xml_file}")
    print(f"파일 존재 여부: {xml_file.exists()}")
    
    if xml_file.exists():
        try:
            result = parser.parse_file(str(xml_file), 1)  # project_id = 1
            file_obj, sql_units, joins, filters, edges, vulnerabilities = result
            
            print(f"\n파싱 결과:")
            print(f"- SQL Units: {len(sql_units)}개")
            print(f"- Joins: {len(joins)}개") 
            print(f"- Filters: {len(filters)}개")
            print(f"- Edges: {len(edges)}개")
            
            if sql_units:
                print(f"\nSQL Units 상세:")
                for i, sql_unit in enumerate(sql_units):
                    print(f"  {i+1}. {sql_unit.stmt_id} ({sql_unit.stmt_kind}) - Line {sql_unit.start_line}-{sql_unit.end_line}")
                    
            if joins:
                print(f"\nJoins 상세:")
                for i, join in enumerate(joins):
                    print(f"  {i+1}. {join.l_table}.{join.l_col} {join.op} {join.r_table}.{join.r_col}")
            else:
                print(f"\n조인이 추출되지 않음. SQL 내용 확인:")
                for i, sql_unit in enumerate(sql_units):
                    if 'join' in sql_unit.normalized_fingerprint.lower():
                        print(f"  SQL Unit {i+1} ({sql_unit.stmt_id})에 JOIN 키워드 포함됨")
                        print(f"  Fingerprint: {sql_unit.normalized_fingerprint[:200]}...")
                    
        except Exception as e:
            print(f"파싱 에러: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("파일이 존재하지 않습니다!")

if __name__ == "__main__":
    test_mybatis_parser()