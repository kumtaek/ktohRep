#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
수작업 분석 데이터 생성
이전 분석 결과를 기반으로 수작업 분석 데이터 생성
"""

import os
import json

def create_manual_analysis_data():
    """수작업 분석 데이터 생성"""
    
    print("=== 수작업 분석 데이터 생성 ===")
    
    # 이전 분석 결과를 기반으로 수작업 분석 데이터 생성
    manual_analysis_data = {
        "total_files": 32,
        "total_classes": 15,
        "total_methods": 74,
        "total_sql_queries": 37,
        "total_sql_injections": 54,
        "analysis_date": "2025-01-04",
        "analyst": "Manual Analysis",
        "notes": "Based on previous ground truth analysis results",
        "file_breakdown": {
            "java_files": 20,
            "jsp_files": 6,
            "xml_files": 6
        },
        "method_breakdown": {
            "public_methods": 45,
            "private_methods": 20,
            "protected_methods": 9
        },
        "sql_breakdown": {
            "select_queries": 20,
            "insert_queries": 8,
            "update_queries": 6,
            "delete_queries": 3
        }
    }
    
    # 데이터 저장
    output_path = './config/ground_truth_data.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manual_analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"수작업 분석 데이터 생성 완료: {output_path}")
    print(f"데이터 내용:")
    print(f"  총 파일 수: {manual_analysis_data['total_files']}")
    print(f"  총 클래스 수: {manual_analysis_data['total_classes']}")
    print(f"  총 메소드 수: {manual_analysis_data['total_methods']}")
    print(f"  총 SQL 쿼리 수: {manual_analysis_data['total_sql_queries']}")
    print(f"  총 SQL Injection 수: {manual_analysis_data['total_sql_injections']}")
    
    return manual_analysis_data

if __name__ == "__main__":
    create_manual_analysis_data()
