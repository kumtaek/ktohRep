#!/usr/bin/env python3
"""
파일 스캔 패턴 테스트
"""

from pathlib import Path

def test_pattern():
    project_root = Path('./project/sampleSrc')
    print('=== 파일 스캔 패턴 테스트 ===')
    
    # 1. 현재 방식 (문제 있는 방식)
    print('\n1. 현재 방식 (문제):')
    include_pattern = '**/*.jsp'
    old_pattern = include_pattern.replace('**/', '')
    print(f'  패턴: {include_pattern} -> {old_pattern}')
    old_files = list(project_root.rglob(old_pattern))
    print(f'  발견된 파일 수: {len(old_files)}')
    for f in old_files:
        print(f'    {f}')
    
    # 2. 올바른 방식
    print('\n2. 올바른 방식:')
    new_files = list(project_root.rglob(include_pattern))
    print(f'  패턴: {include_pattern}')
    print(f'  발견된 파일 수: {len(new_files)}')
    for f in new_files:
        print(f'    {f}')
    
    # 3. 누락된 파일들
    print('\n3. 누락된 파일들:')
    all_jsp_files = [
        'src/main/webapp/user/error.jsp',
        'src/main/webapp/user/list.jsp', 
        'src/main/webapp/user/searchResult.jsp',
        'src/main/webapp/user/typeList.jsp',
        'src/main/webapp/product/list.jsp',
        'src/main/webapp/product/searchResult.jsp',
        'src/main/webapp/error/syntaxError.jsp',
        'src/main/webapp/mixed/partialError.jsp'
    ]
    
    for jsp_file in all_jsp_files:
        full_path = project_root / jsp_file
        if full_path.exists():
            print(f'  ✅ {jsp_file}: 존재')
        else:
            print(f'  ❌ {jsp_file}: 없음')

if __name__ == "__main__":
    test_pattern()
