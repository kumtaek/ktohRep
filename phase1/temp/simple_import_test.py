#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('..')

print("=== Import 테스트 ===")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"Python 경로: {sys.path}")

try:
    from phase1.parsers.java.java_parser import JavaParser
    print("✅ JavaParser import 성공")
except ImportError as e:
    print(f"❌ JavaParser import 실패: {e}")

try:
    import phase1.parsers
    print("✅ phase1.parsers import 성공")
except ImportError as e:
    print(f"❌ phase1.parsers import 실패: {e}")

try:
    import phase1
    print("✅ phase1 import 성공")
except ImportError as e:
    print(f"❌ phase1 import 실패: {e}")

# 직접 경로로 테스트
try:
    sys.path.append('../phase1')
    from parsers.java.java_parser import JavaParser
    print("✅ 직접 경로로 JavaParser import 성공")
except ImportError as e:
    print(f"❌ 직접 경로로 JavaParser import 실패: {e}")
