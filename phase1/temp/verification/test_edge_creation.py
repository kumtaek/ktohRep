import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.java.javaparser_enhanced import JavaParserEnhanced
import json

# ListServiceImpl1.java 내용
test_content = '''package com.example.service.impl;

import com.example.service.ListService;

public class ListServiceImpl1 implements ListService {
    @Override
    public void list() {
        helper();
    }

    private void helper() {
        // dummy
    }
}
'''

parser = JavaParserEnhanced({})
classes, methods, edges = parser._parse_with_regex(test_content, 'test.java', 1)

print('=== Edge 생성 테스트 ===')
print(f'Classes: {len(classes)}')
for cls in classes:
    print(f'  - {cls.fqn}')

print(f'Edges: {len(edges)}')
for i, edge in enumerate(edges):
    print(f'  Edge {i+1}:')
    print(f'    src_fqn: {getattr(edge, "src_fqn", "None")}')
    print(f'    dst_fqn: {getattr(edge, "dst_fqn", "None")}')
    print(f'    src_type: {edge.src_type}')
    print(f'    dst_type: {edge.dst_type}')
    print(f'    edge_kind: {edge.edge_kind}')
    print(f'    confidence: {edge.confidence}')
    print(f'    src_id: {edge.src_id}')
    print(f'    dst_id: {edge.dst_id}')
    print()
