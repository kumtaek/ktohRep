import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / 'phase1'))

from phase1.parsers.jar_parser import JarParser


def test_jar_parser_extracts_methods(tmp_path):
    java_src = tmp_path / "Hello.java"
    java_src.write_text(
        "public class Hello {\n"\
        "  public void sayHi() {}\"n"\
        "  private int add(int a, int b) { return a + b; }\n"\
        "}\n"
    )
    # Compile and package into jar
    os.system(f"javac {java_src}")
    os.system(f"jar cf {tmp_path}/'hello.jar' -C {tmp_path} Hello.class")

    parser = JarParser({})
    file_obj, classes, methods, _ = parser.parse_file(str(tmp_path/'hello.jar'), project_id=1)

    assert file_obj.path.endswith('hello.jar')
    class_names = [c.name for c in classes]
    assert 'Hello' in class_names
    method_names = [m.name for m in methods]
    assert 'sayHi' in method_names
    assert 'add' in method_names
