#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def test_file_paths():
    print("=== 파일 경로 테스트 ===")
    
    # 현재 디렉토리 확인
    print(f"현재 디렉토리: {os.getcwd()}")
    
    # 상대 경로 테스트
    test_paths = [
        "../project/sampleSrc/src/main/java",
        "./project/sampleSrc/src/main/java",
        "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java"
    ]
    
    for path in test_paths:
        exists = os.path.exists(path)
        print(f"경로: {path}")
        print(f"존재: {exists}")
        if exists:
            if os.path.isfile(path):
                print(f"파일 크기: {os.path.getsize(path)} bytes")
            elif os.path.isdir(path):
                files = os.listdir(path)
                print(f"디렉토리 내 파일 수: {len(files)}")
                if files:
                    print(f"첫 번째 파일: {files[0]}")
        print()

if __name__ == "__main__":
    test_file_paths()
