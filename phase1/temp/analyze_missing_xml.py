#!/usr/bin/env python3
"""
누락된 XML 쿼리 분석
"""

import os
import glob
import re
from pathlib import Path

def count_xml_queries_detailed(file_path):
    """XML 파일에서 쿼리 개수를 상세히 분석"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        queries = []
        
        # MyBatis 쿼리 태그들
        query_tags = ['select', 'insert', 'update', 'delete']
        
        for tag in query_tags:
            # 기본 패턴
            pattern = rf'<{tag}[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>'
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                query_id = match.group(1)
                queries.append((tag, query_id, 'basic'))
        
        # 동적 쿼리 패턴 (foreach, choose, if 등)
        dynamic_patterns = [
            r'<foreach[^>]*collection\s*=\s*["\']([^"\']+)["\'][^>]*>',
            r'<choose[^>]*>',
            r'<if[^>]*test\s*=\s*["\']([^"\']+)["\'][^>]*>',
            r'<when[^>]*test\s*=\s*["\']([^"\']+)["\'][^>]*>',
            r'<otherwise[^>]*>',
            r'<trim[^>]*>',
            r'<where[^>]*>',
            r'<set[^>]*>'
        ]
        
        for pattern in dynamic_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if 'collection' in pattern:
                    collection = match.group(1)
                    queries.append(('foreach', collection, 'dynamic'))
                elif 'test' in pattern:
                    test_condition = match.group(1)
                    queries.append(('conditional', test_condition, 'dynamic'))
                else:
                    tag_name = pattern.split('<')[1].split('>')[0].split()[0]
                    queries.append((tag_name, 'dynamic', 'dynamic'))
        
        # include 태그
        include_pattern = r'<include[^>]*refid\s*=\s*["\']([^"\']+)["\'][^>]*>'
        include_matches = re.finditer(include_pattern, content, re.IGNORECASE)
        for match in include_matches:
            refid = match.group(1)
            queries.append(('include', refid, 'include'))
        
        return len(queries), queries
        
    except Exception as e:
        print(f"XML 파일 읽기 오류 {file_path}: {e}")
        return 0, []

def analyze_xml_files():
    """XML 파일들 분석"""
    project_path = "project/sampleSrc/src"
    
    print("=== XML 파일 상세 분석 ===\n")
    
    xml_files = glob.glob(f"{project_path}/**/*.xml", recursive=True)
    total_queries = 0
    file_details = []
    
    for xml_file in xml_files:
        relative_path = os.path.relpath(xml_file, project_path)
        query_count, query_details = count_xml_queries_detailed(xml_file)
        total_queries += query_count
        file_details.append((relative_path, query_count, query_details))
        
        print(f"파일: {relative_path}")
        print(f"  쿼리 개수: {query_count}개")
        
        if query_count > 0:
            # 쿼리 타입별 그룹화
            by_type = {}
            for tag, id_or_condition, category in query_details:
                if category not in by_type:
                    by_type[category] = []
                by_type[category].append((tag, id_or_condition))
            
            for category, items in by_type.items():
                print(f"  {category}: {len(items)}개")
                for tag, id_or_condition in items[:5]:  # 최대 5개만 표시
                    print(f"    - {tag}: {id_or_condition}")
                if len(items) > 5:
                    print(f"    ... 외 {len(items) - 5}개")
        print()
    
    print(f"=== 전체 통계 ===")
    print(f"XML 파일 수: {len(xml_files)}개")
    print(f"총 쿼리 수: {total_queries}개")
    
    # 파일별 쿼리 개수 정렬
    file_details.sort(key=lambda x: x[1], reverse=True)
    print(f"\n=== 쿼리 개수별 파일 순위 ===")
    for i, (file_path, count, _) in enumerate(file_details[:10], 1):
        print(f"{i:2d}. {file_path}: {count}개")

if __name__ == "__main__":
    analyze_xml_files()

