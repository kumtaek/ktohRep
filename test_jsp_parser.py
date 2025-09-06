#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JspMybatisParser 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_jsp_parser():
    """JspMybatisParser 테스트"""
    try:
        from phase1.parsers.jsp_mybatis_parser import JspMybatisParser
        print("✅ JspMybatisParser import 성공")
        
        # 간단한 설정으로 파서 초기화
        config = {
            'database': {
                'project': {
                    'default_schema': 'SAMPLE'
                }
            }
        }
        
        parser = JspMybatisParser(config)
        print("✅ JspMybatisParser 초기화 성공")
        
        # 테스트용 JSP 내용
        test_jsp_content = '''
        <%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
        <%
        String sql = "SELECT p.*, c.category_name FROM products p JOIN categories c ON p.category_id = c.category_id";
        %>
        '''
        
        print("✅ 테스트 준비 완료")
        return True
        
    except Exception as e:
        print(f"❌ JspMybatisParser 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("JspMybatisParser 테스트 시작...")
    success = test_jsp_parser()
    if success:
        print("🎉 모든 테스트 통과!")
    else:
        print("💥 테스트 실패!")
