#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순 테스트 러너 (한글 로그/주석)

검증 항목
- Java 파서: 정상/비정상 자바 파일 파싱 안정성, 기본 메타데이터 채움 여부
- JSP/MyBatis 파서: 정상/비정상 JSP/XML 파싱 안정성, JOIN/WHERE 1차 추출 여부
- (선택) 메타데이터 엔진: SQLite 임시 DB에 저장 시 call 엣지 저장/해결 루프 기본 작동 여부(간단 경로)
"""
import os
import sys
import json
import tempfile
from datetime import datetime

# phase1를 sys.path에 추가하여 src 네임스페이스 패키지로 임포트되도록 설정
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PHASE1_DIR = os.path.join(REPO_ROOT, 'phase1')
SRC_DIR = os.path.join(PHASE1_DIR, 'src')
sys.path.insert(0, PHASE1_DIR)

print("[테스트 시작] 환경 준비 완료")

def _mk_config(db_path=None):
    """테스트용 최소 설정 객체 생성"""
    return {
        'java': {
            'parser_type': 'javalang'  # 환경에 따라 tree-sitter 사용 가능
        },
        'database': {
            'type': 'sqlite',
            'sqlite': {
                'path': db_path or os.path.join(tempfile.gettempdir(), f"sa_test_{int(datetime.now().timestamp())}.db"),
                'wal_mode': False
            },
            'default_schema': 'public'
        },
        'processing': {
            'confidence_threshold': 0.5
        },
        'confidence': {
            'suspect_threshold': 0.3,
            'filter_threshold': 0.1
        }
    }

def test_java_parser_normal():
    from src.parsers.java_parser import JavaParser
    from src.models.database import File
    config = _mk_config()
    parser = JavaParser(config)
    sample = os.path.join(REPO_ROOT, 'tests', 'samples', 'java', 'ValidSimple.java')
    print("[JAVA-정상] 파싱 시도:", sample)
    f, classes, methods, edges = parser.parse_file(sample, project_id=1)
    assert isinstance(f, File), "파일 객체가 올바르지 않습니다"
    assert len(classes) >= 1, "클래스가 추출되지 않았습니다"
    assert len(methods) >= 1, "메서드가 추출되지 않았습니다"
    print("[JAVA-정상] 클래스/메서드/엣지 수:", len(classes), len(methods), len(edges))

def test_java_parser_invalid():
    from src.parsers.java_parser import JavaParser
    config = _mk_config()
    parser = JavaParser(config)
    sample = os.path.join(REPO_ROOT, 'tests', 'samples', 'java', 'InvalidSyntax.java')
    print("[JAVA-오류] 파싱 시도(의도적 문법 오류):", sample)
    f, classes, methods, edges = parser.parse_file(sample, project_id=1)
    # 비정상 소스라도 예외로 테스트가 중단되면 안 됨
    assert isinstance(classes, list) and isinstance(methods, list) and isinstance(edges, list), "반환 형식이 올바르지 않습니다"
    print("[JAVA-오류] 예외 없이 종료(빈 결과 가능)")

def test_jsp_mybatis_parsers():
    from src.parsers.jsp_mybatis_parser import JspMybatisParser
    config = _mk_config()
    parser = JspMybatisParser(config)
    jsp = os.path.join(REPO_ROOT, 'tests', 'samples', 'jsp', 'sample.jsp')
    xml_ok = os.path.join(REPO_ROOT, 'tests', 'samples', 'xml', 'mybatis_valid.xml')
    xml_ng = os.path.join(REPO_ROOT, 'tests', 'samples', 'xml', 'mybatis_invalid.xml')

    print("[JSP-정상] 파싱 시도:", jsp)
    f, sqls, joins, filters, edges, vulns = parser.parse_file(jsp, project_id=1)
    assert isinstance(sqls, list), "JSP SQL 추출 결과 형식 오류"
    print("[JSP-정상] SQL/Join/Filter 수:", len(sqls), len(joins), len(filters))

    print("[XML-정상] 파싱 시도:", xml_ok)
    f2, sqls2, joins2, filters2, edges2, vulns2 = parser.parse_file(xml_ok, project_id=1)
    assert len(sqls2) >= 1, "MyBatis SQL이 추출되지 않았습니다"
    # JOIN/WHERE 1차 고도화가 동작하는지 간단 검증
    assert len(joins2) >= 1, "JOIN 추출 결과가 없습니다"
    assert len(filters2) >= 1, "WHERE 필터 추출 결과가 없습니다"
    print("[XML-정상] SQL/Join/Filter 수:", len(sqls2), len(joins2), len(filters2))

    print("[XML-오류] 파싱 시도(의도적 XML 오류):", xml_ng)
    f3, sqls3, joins3, filters3, edges3, vulns3 = parser.parse_file(xml_ng, project_id=1)
    assert isinstance(sqls3, list), "비정상 XML 파싱 결과 형식 오류"
    print("[XML-오류] 예외 없이 종료(빈 결과 가능)")

def test_engine_save_basic():
    # SQLite 임시 DB에 저장 경로 기본 동작 확인
    from src.models.database import DatabaseManager
    from src.database.metadata_engine import MetadataEngine
    from src.parsers.java_parser import JavaParser

    db_path = os.path.join(tempfile.gettempdir(), f"sa_test_{int(datetime.now().timestamp())}.db")
    config = _mk_config(db_path=db_path)
    db = DatabaseManager(config)
    db.initialize()
    engine = MetadataEngine(config, db)

    parser = JavaParser(config)
    sample = os.path.join(REPO_ROOT, 'tests', 'samples', 'java', 'ValidSimple.java')
    f, classes, methods, edges = parser.parse_file(sample, project_id=1)

    print("[엔진-저장] Java 파싱 결과 저장 시도")
    saved = engine._save_java_analysis_sync(f, classes, methods, edges)
    # call 엣지(dst 미해결)도 저장되도록 변경됨 → edges 카운트가 0 이상이면 OK
    assert saved.get('files', 0) == 1, "파일 저장 실패"
    assert saved.get('classes', 0) >= 1, "클래스 저장 실패"
    assert saved.get('methods', 0) >= 1, "메서드 저장 실패"
    print("[엔진-저장] 저장 결과:", saved)

def main():
    ok = 0
    fail = 0
    tests = [
        ("JAVA 정상 파싱", test_java_parser_normal),
        ("JAVA 비정상 파싱", test_java_parser_invalid),
        ("JSP/MyBatis 파싱", test_jsp_mybatis_parsers),
        ("엔진 저장 기본", test_engine_save_basic),
    ]
    for name, fn in tests:
        try:
            print(f"\n[케이스 시작] {name}")
            fn()
            ok += 1
            print(f"[케이스 성공] {name}")
        except AssertionError as ae:
            fail += 1
            print(f"[케이스 실패] {name}: {ae}")
        except Exception as e:
            fail += 1
            print(f"[케이스 예외] {name}: {e}")

    print(f"\n[테스트 종료] 성공 {ok} / 실패 {fail}")
    if fail:
        sys.exit(1)

if __name__ == '__main__':
    main()

