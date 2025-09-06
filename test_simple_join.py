#!/usr/bin/env python3
"""간단한 조인 테스트"""

import sys
from pathlib import Path
import yaml

# Add phase1 to path
phase1_root = Path(__file__).parent / "phase1"
sys.path.insert(0, str(phase1_root))

from parsers.jsp_mybatis_parser import JspMybatisParser
from models.database import SqlUnit

def test_simple_join():
    """간단한 조인 추출 테스트"""
    
    # 설정 로드
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 파서 초기화
    parser = JspMybatisParser(config)
    
    # 가짜 SqlUnit 생성
    sql_unit = SqlUnit(
        sql_id=1,
        stmt_id="test_join",
        stmt_kind="select"
    )
    
    # 간단한 JOIN 구문 테스트
    test_sql = "JOIN CUSTOMERS c ON o.CUSTOMER_ID = c.CUSTOMER_ID"
    
    print(f"테스트 SQL: {test_sql}")
    print()
    
    # _parse_join_condition 직접 호출
    result = parser._parse_join_condition(test_sql, sql_unit)
    
    if result:
        print(f"성공! 조인 추출됨:")
        print(f"  l_table: {result.l_table}")
        print(f"  l_col: {result.l_col}")
        print(f"  op: {result.op}")
        print(f"  r_table: {result.r_table}")
        print(f"  r_col: {result.r_col}")
    else:
        print("실패! 조인이 추출되지 않음.")

if __name__ == "__main__":
    test_simple_join()