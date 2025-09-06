#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting simple test...")

try:
    from parsers.optimized_java_parser import OptimizedJavaParser
    print("1. Import OptimizedJavaParser: OK")
except Exception as e:
    print(f"1. Import OptimizedJavaParser: ERROR - {e}")

try:
    from core.optimized_metadata_engine import OptimizedMetadataEngine
    print("2. Import OptimizedMetadataEngine: OK")
except Exception as e:
    print(f"2. Import OptimizedMetadataEngine: ERROR - {e}")

try:
    engine = OptimizedMetadataEngine()
    print("3. Create OptimizedMetadataEngine: OK")
except Exception as e:
    print(f"3. Create OptimizedMetadataEngine: ERROR - {e}")

try:
    parser = OptimizedJavaParser(engine)
    print("4. Create OptimizedJavaParser: OK")
except Exception as e:
    print(f"4. Create OptimizedJavaParser: ERROR - {e}")

print("Simple test completed.")
