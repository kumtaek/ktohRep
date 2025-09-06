#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Basic test starting...")

try:
    print("1. Testing basic imports...")
    from parsers.optimized_java_parser import OptimizedJavaParser
    from core.optimized_metadata_engine import OptimizedMetadataEngine
    print("   Imports successful")
    
    print("2. Testing engine creation...")
    engine = OptimizedMetadataEngine()
    print("   Engine created successfully")
    
    print("3. Testing parser creation...")
    parser = OptimizedJavaParser(engine)
    print("   Parser created successfully")
    
    print("4. Testing simple parse...")
    result = parser.parse_java_file(1, './project/sampleSrc/src/main/java/com/example/model/User.java')
    print(f"   Parse result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Basic test completed.")
