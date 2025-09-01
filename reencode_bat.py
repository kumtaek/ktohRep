#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배치 파일 재인코딩 스크립트
BOM이 포함된 UTF-8 파일을 BOM 없는 UTF-8로 변환하는 유틸리티
"""

# 재인코딩할 배치 파일의 경로
file_path = "E:\\SourceAnalyzer.git\\exec_all.bat"

try:
    # BOM이 있는 UTF-8 파일을 읽습니다.
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # BOM 없이 UTF-8로 다시 저장합니다.
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"'{file_path}' 파일이 BOM 없는 UTF-8로 성공적으로 재인코딩되었습니다.")
except Exception as e:
    print(f"파일 재인코딩 중 오류 발생: {e}")