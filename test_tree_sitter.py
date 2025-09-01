# E:\SourceAnalyzer.git\test_tree_sitter.py
from tree_sitter import Language, Parser
import tree_sitter_java
import os

print("Tree-sitter 및 tree-sitter-java 모듈 로드 성공!")

try:
    # 1. Java 언어 로드
    # tree_sitter_java.language()는 이미 Language 객체를 반환합니다.
    JAVA_LANGUAGE = tree_sitter_java.language()
    print(f"Java 언어 로드 성공! (타입: {type(JAVA_LANGUAGE)})")

    # 2. 파서 생성 및 언어 설정
    parser = Parser()
    print(f"Tree-sitter 파서 생성 성공! (타입: {type(parser)})")

    # set_language 메서드가 있는지 확인 후 호출
    if hasattr(parser, 'set_language'):
        parser.set_language(JAVA_LANGUAGE)
        print("Tree-sitter 파서 언어 설정 성공!")
    else:
        raise AttributeError("'tree_sitter.Parser' object has no attribute 'set_language'. Check tree-sitter version or usage.")


    # 3. 파싱할 Java 코드 (간단한 예시)
    java_code = """
    package com.example;

    public class HelloWorld {
        public static void main(String[] args) {
            System.out.println("Hello, Tree-sitter!");
        }
    }
    """
    print("\n--- 파싱할 Java 코드 ---")
    print(java_code)

    # 4. 코드 파싱
    tree = parser.parse(bytes(java_code, 'utf8'))
    root_node = tree.root_node
    print("\n--- 코드 파싱 성공! ---")
    print(f"AST Root Node Type: {root_node.type}")
    print(f"AST Root Node Text (partial): {root_node.text.decode('utf8')[:50]}...")

    # 5. 간단한 AST 탐색 (클래스 이름 찾기)
    def find_nodes_by_type(node, node_type):
        results = []
        if node.type == node_type:
            results.append(node)
        for child in node.children:
            results.extend(find_nodes_by_type(child, node_type))
        return results

    class_declarations = find_nodes_by_type(root_node, 'class_declaration')
    if class_declarations:
        class_node = class_declarations[0]
        class_name_node = class_node.child_by_field_name('name')
        if class_name_node:
            print(f"\n찾은 클래스 이름: {class_name_node.text.decode('utf8')}")
            print(f"클래스 시작 라인: {class_node.start_point[0] + 1}, 종료 라인: {class_node.end_point[0] + 1}")
    else:
        print("\n클래스 선언을 찾을 수 없습니다.")

    print("\nTree-sitter 테스트가 성공적으로 완료되었습니다.")

except Exception as e:
    print(f"\nTree-sitter 테스트 중 오류 발생: {e}")
    print("Tree-sitter 설치 또는 환경 설정에 문제가 있을 수 있습니다.")
    print("Visual Studio Build Tools (Windows) 또는 개발 도구 (Linux)가 설치되어 있는지 확인하세요.")
