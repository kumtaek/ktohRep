#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 JSP 파일 파싱 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

async def test_real_jsp_parsing():
    """실제 JSP 파일 파싱 테스트"""
    try:
        from phase1.parsers.jsp_mybatis_parser import JspMybatisParser
        print("✅ JspMybatisParser import 성공")
        
        # 설정으로 파서 초기화
        config = {
            'database': {
                'project': {
                    'default_schema': 'SAMPLE'
                }
            },
            'logger': None
        }
        
        parser = JspMybatisParser(config)
        print("✅ JspMybatisParser 초기화 성공")
        
        # 실제 JSP 파일 경로
        jsp_file_path = "project/sampleSrc/src/main/webapp/WEB-INF/jsp/IntegratedView.jsp"
        
        if not os.path.exists(jsp_file_path):
            print(f"❌ JSP 파일을 찾을 수 없음: {jsp_file_path}")
            return False
        
        print(f"📁 JSP 파일 발견: {jsp_file_path}")
        
        # 파일 내용 읽기
        with open(jsp_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 파일 내용 읽기 완료: {len(content)} 문자")
        
        # 파싱 실행
        print("🔍 JSP 파일 파싱 시작...")
        result = await parser.parse(content, jsp_file_path)
        
        if result:
            file_obj, sql_units, joins, filters, edges, vulnerabilities = result
            print(f"✅ 파싱 완료!")
            print(f"   - SQL Units: {len(sql_units)}개")
            print(f"   - Joins: {len(joins)}개")
            print(f"   - Filters: {len(filters)}개")
            print(f"   - Edges: {len(edges)}개")
            
            # SQL Units 상세 정보
            for i, sql_unit in enumerate(sql_units):
                print(f"   SQL Unit {i+1}:")
                print(f"     - Origin: {sql_unit.origin}")
                print(f"     - Statement ID: {sql_unit.stmt_id}")
                print(f"     - Kind: {sql_unit.stmt_kind}")
                print(f"     - Lines: {sql_unit.start_line}-{sql_unit.end_line}")
            
            # Joins 상세 정보
            for i, join in enumerate(joins):
                print(f"   Join {i+1}:")
                print(f"     - Tables: {join.l_table} -> {join.r_table}")
                print(f"     - Columns: {join.l_col} -> {join.r_col}")
                print(f"     - Operator: {join.op}")
            
            return True
        else:
            print("❌ 파싱 결과가 없음")
            return False
        
    except Exception as e:
        print(f"❌ JSP 파싱 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("실제 JSP 파일 파싱 테스트 시작...")
    import asyncio
    success = asyncio.run(test_real_jsp_parsing())
    if success:
        print("🎉 파싱 테스트 성공!")
    else:
        print("💥 파싱 테스트 실패!")
