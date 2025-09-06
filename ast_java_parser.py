import os
import glob
from javalang import parse, tree

def count_java_classes(source_directory):
    """AST 파서를 사용하여 Java 파일의 클래스와 인터페이스 수를 계산합니다."""
    java_files = glob.glob(os.path.join(source_directory, '**', '*.java'), recursive=True)
    total_classes = 0
    total_interfaces = 0
    print(f"{len(java_files)}개의 Java 파일에서 클래스 및 인터페이스 수를 계산합니다...")

    for file_path in java_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            compilation_unit = parse.parse(content)
            classes_in_file = len(list(compilation_unit.filter(tree.ClassDeclaration)))
            interfaces_in_file = len(list(compilation_unit.filter(tree.InterfaceDeclaration)))
            
            total_classes += classes_in_file
            total_interfaces += interfaces_in_file
            
            if classes_in_file > 0 or interfaces_in_file > 0:
                print(f" - {os.path.basename(file_path)}: 클래스 {classes_in_file}개, 인터페이스 {interfaces_in_file}개")

        except Exception as e:
            print(f"파일 파싱 오류 {file_path}: {e}")

    print(f"\n총 클래스 수: {total_classes}")
    print(f"총 인터페이스 수: {total_interfaces}")
    print(f"총 합계 (클래스 + 인터페이스): {total_classes + total_interfaces}")
    return total_classes + total_interfaces

if __name__ == '__main__':
    source_dir = os.path.join('project', 'sampleSrc', 'src')
    count_java_classes(source_dir)
