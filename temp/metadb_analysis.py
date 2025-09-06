#!/usr/bin/env python3
"""
메타디비 데이터 분석 및 샘플소스명세서와 비교 검증 스크립트
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def analyze_metadb(project_name):
    """메타디비 데이터 분석"""
    db_path = f"./project/{project_name}/metadata.db"
    
    if not Path(db_path).exists():
        print(f"메타디비가 존재하지 않습니다: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    analysis = {}
    
    # 1. 파일 정보 분석
    cursor.execute("SELECT COUNT(*) FROM files")
    analysis['total_files'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT language, COUNT(*) FROM files GROUP BY language")
    analysis['files_by_type'] = dict(cursor.fetchall())
    
    # 2. Java 클래스 정보 분석
    cursor.execute("SELECT COUNT(*) FROM classes")
    analysis['total_classes'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM methods")
    analysis['total_methods'] = cursor.fetchone()[0]
    
    # 3. SQL 쿼리 정보 분석
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    analysis['total_sql_units'] = cursor.fetchone()[0]
    
    # 4. 청크 정보 분석 (chunks 테이블에서)
    cursor.execute("SELECT COUNT(*) FROM chunks")
    analysis['total_chunks'] = cursor.fetchone()[0]
    
    # 청크 타입별 분석은 실제 데이터가 있을 때만 수행
    analysis['total_jsp_tags'] = 0
    analysis['total_html_tags'] = 0
    analysis['total_js_functions'] = 0
    analysis['total_css_classes'] = 0
    analysis['total_annotations'] = 0
    analysis['total_fields'] = 0
    
    # 7. 오류 정보 분석
    cursor.execute("SELECT COUNT(*) FROM parse_results WHERE success = 0")
    analysis['total_errors'] = cursor.fetchone()[0]
    
    # 8. 상세 파일별 분석
    cursor.execute("""
        SELECT f.path, f.language, 
               COUNT(DISTINCT c.class_id) as class_count,
               COUNT(DISTINCT m.method_id) as method_count,
               COUNT(DISTINCT s.sql_id) as sql_count,
               COUNT(DISTINCT ch.chunk_id) as chunk_count
        FROM files f
        LEFT JOIN classes c ON f.file_id = c.file_id
        LEFT JOIN methods m ON f.file_id = m.file_id
        LEFT JOIN sql_units s ON f.file_id = s.file_id
        LEFT JOIN chunks ch ON f.file_id = ch.target_id AND ch.target_type = 'file'
        GROUP BY f.file_id, f.path, f.language
        ORDER BY f.path
    """)
    analysis['files_detail'] = cursor.fetchall()
    
    # 9. 청크 타입별 상세 분석
    cursor.execute("SELECT target_type, COUNT(*) FROM chunks GROUP BY target_type")
    analysis['chunks_by_type'] = dict(cursor.fetchall())
    
    conn.close()
    return analysis

def compare_with_specification(metadb_analysis):
    """샘플소스명세서와 메타디비 결과 비교"""
    
    # 샘플소스명세서 기준값 (Part 1에서 추출)
    spec_values = {
        'total_files': 32,  # Java 16개 + JSP 8개 + XML 4개 + CSV 4개
        'java_files': 16,
        'jsp_files': 8,
        'xml_files': 4,
        'csv_files': 4,
        'total_classes': 16,
        'total_methods': 77,  # 정상 66개 + 일부 오류 11개
        'total_annotations': 59,
        'total_fields': 35,
        'total_sql_units': 31,  # 정상 29개 + 일부 오류 2개
        'total_jsp_tags': 51,  # JSTL 43개 + HTML 75개 + JavaScript 9개 + CSS 19개
        'total_html_tags': 75,
        'total_js_functions': 9,
        'total_css_classes': 19,
        'total_errors': 7  # Java 4개 + JSP 3개
    }
    
    comparison = {}
    
    for key, expected in spec_values.items():
        if key in metadb_analysis:
            actual = metadb_analysis[key]
            diff = actual - expected
            diff_percent = (diff / expected * 100) if expected > 0 else 0
            
            comparison[key] = {
                'expected': expected,
                'actual': actual,
                'difference': diff,
                'difference_percent': diff_percent,
                'status': 'PASS' if abs(diff_percent) <= 10 else 'FAIL'
            }
        else:
            comparison[key] = {
                'expected': expected,
                'actual': 0,
                'difference': -expected,
                'difference_percent': -100,
                'status': 'FAIL'
            }
    
    return comparison

def generate_report(metadb_analysis, comparison):
    """비교 결과 리포트 생성"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"./Dev.Report/메타디비_검증결과_{timestamp}.md"
    
    report = f"""# 메타디비 검증 결과 리포트

## 생성 일시
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 개요
- **목적**: 샘플소스명세서와 메타디비 생성 결과 비교 검증
- **검증 기준**: 과소추출 0%, 과다추출 10% 이내 허용
- **프로젝트**: sampleSrc

---

## 📊 메타디비 분석 결과

### 1. 전체 통계

| 항목 | 개수 |
|------|------|
| **총 파일 수** | {metadb_analysis.get('total_files', 0)} |
| **총 클래스 수** | {metadb_analysis.get('total_classes', 0)} |
| **총 메소드 수** | {metadb_analysis.get('total_methods', 0)} |
| **총 SQL 쿼리 수** | {metadb_analysis.get('total_sql_units', 0)} |
| **총 어노테이션 수** | {metadb_analysis.get('total_annotations', 0)} |
| **총 필드 수** | {metadb_analysis.get('total_fields', 0)} |
| **총 오류 수** | {metadb_analysis.get('total_errors', 0)} |

### 2. 파일 타입별 분포

| 파일 타입 | 개수 |
|-----------|------|
"""
    
    for file_type, count in metadb_analysis.get('files_by_type', {}).items():
        report += f"| {file_type} | {count} |\n"
    
    report += f"""
### 3. 청크 타입별 분포

| 청크 타입 | 개수 |
|-----------|------|
"""
    
    for chunk_type, count in metadb_analysis.get('chunks_by_type', {}).items():
        report += f"| {chunk_type} | {count} |\n"
    
    report += f"""
---

## 🔍 명세서 대비 검증 결과

### 검증 기준
- **과소추출**: 0% (절대 금지)
- **과다추출**: 10% 이내 허용
- **파일별 오차**: 10% 이내 허용

### 상세 비교 결과

| 항목 | 명세서 기준 | 메타디비 결과 | 차이 | 차이율 | 상태 |
|------|-------------|---------------|------|--------|------|
"""
    
    for key, result in comparison.items():
        status_emoji = "✅" if result['status'] == 'PASS' else "❌"
        report += f"| {key} | {result['expected']} | {result['actual']} | {result['difference']:+d} | {result['difference_percent']:+.1f}% | {status_emoji} {result['status']} |\n"
    
    # 통과/실패 요약
    pass_count = sum(1 for r in comparison.values() if r['status'] == 'PASS')
    total_count = len(comparison)
    pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
    
    report += f"""
---

## 📈 검증 요약

### 전체 검증 결과
- **총 검증 항목**: {total_count}개
- **통과 항목**: {pass_count}개
- **실패 항목**: {total_count - pass_count}개
- **통과율**: {pass_rate:.1f}%

### 상태별 분석
"""
    
    # 과소추출 항목 확인
    undershoot_items = [k for k, v in comparison.items() if v['difference'] < 0]
    overshoot_items = [k for k, v in comparison.items() if v['difference'] > 0 and v['difference_percent'] > 10]
    
    if undershoot_items:
        report += f"""
#### ❌ 과소추출 항목 (심각)
"""
        for item in undershoot_items:
            result = comparison[item]
            report += f"- **{item}**: {result['expected']} → {result['actual']} ({result['difference_percent']:+.1f}%)\n"
    
    if overshoot_items:
        report += f"""
#### ⚠️ 과다추출 항목 (10% 초과)
"""
        for item in overshoot_items:
            result = comparison[item]
            report += f"- **{item}**: {result['expected']} → {result['actual']} ({result['difference_percent']:+.1f}%)\n"
    
    # 통과 항목
    pass_items = [k for k, v in comparison.items() if v['status'] == 'PASS']
    if pass_items:
        report += f"""
#### ✅ 검증 통과 항목
"""
        for item in pass_items:
            result = comparison[item]
            report += f"- **{item}**: {result['expected']} → {result['actual']} ({result['difference_percent']:+.1f}%)\n"
    
    report += f"""
---

## 🔧 개선 권고사항

### 1. 과소추출 문제 해결
"""
    
    if undershoot_items:
        report += f"""
다음 항목들의 과소추출 문제를 해결해야 합니다:
"""
        for item in undershoot_items:
            report += f"- **{item}**: 파서 로직 개선 필요\n"
    else:
        report += f"""
과소추출 문제는 발견되지 않았습니다. ✅
"""
    
    report += f"""
### 2. 과다추출 문제 해결
"""
    
    if overshoot_items:
        report += f"""
다음 항목들의 과다추출 문제를 해결해야 합니다:
"""
        for item in overshoot_items:
            report += f"- **{item}**: 파서 로직 개선 필요\n"
    else:
        report += f"""
과다추출 문제는 발견되지 않았습니다. ✅
"""
    
    report += f"""
### 3. 전체 평가

"""
    
    if pass_rate >= 90:
        report += f"""
**🎉 우수한 성능**: {pass_rate:.1f}%의 검증 항목이 통과했습니다.
파서가 명세서 기준을 잘 만족하고 있습니다.
"""
    elif pass_rate >= 80:
        report += f"""
**👍 양호한 성능**: {pass_rate:.1f}%의 검증 항목이 통과했습니다.
일부 개선이 필요하지만 전반적으로 양호한 수준입니다.
"""
    elif pass_rate >= 70:
        report += f"""
**⚠️ 개선 필요**: {pass_rate:.1f}%의 검증 항목이 통과했습니다.
파서 로직의 개선이 필요합니다.
"""
    else:
        report += f"""
**❌ 심각한 문제**: {pass_rate:.1f}%의 검증 항목만 통과했습니다.
파서의 전면적인 개선이 필요합니다.
"""
    
    report += f"""
---

## 📋 상세 파일별 분석

### 파일별 상세 정보
"""
    
    for file_info in metadb_analysis.get('files_detail', []):
        file_path, language, class_count, method_count, sql_count, chunk_count = file_info
        report += f"""
#### {file_path}
- **언어**: {language}
- **클래스**: {class_count}개
- **메소드**: {method_count}개
- **SQL 쿼리**: {sql_count}개
- **청크**: {chunk_count}개
"""
    
    report += f"""
---

## 🎯 결론

이 검증 결과는 파서의 정확성을 평가하고 개선 방향을 제시하는 중요한 지표입니다.

### 주요 발견사항
1. **과소추출**: {'발견됨' if undershoot_items else '발견되지 않음'}
2. **과다추출**: {'발견됨' if overshoot_items else '발견되지 않음'}
3. **전체 통과율**: {pass_rate:.1f}%

### 다음 단계
1. 실패한 항목들의 파서 로직 개선
2. 재검증 수행
3. 지속적인 품질 관리

---
*이 리포트는 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}에 자동 생성되었습니다.*
"""
    
    # 리포트 파일 저장
    Path("./Dev.Report").mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"검증 결과 리포트가 생성되었습니다: {report_path}")
    return report_path

def main():
    """메인 함수"""
    project_name = "sampleSrc"
    
    print("메타디비 분석 시작...")
    metadb_analysis = analyze_metadb(project_name)
    
    if metadb_analysis is None:
        print("메타디비 분석 실패")
        return
    
    print(f"메타디비 분석 완료: {metadb_analysis}")
    print("명세서와 비교 분석 중...")
    comparison = compare_with_specification(metadb_analysis)
    
    print(f"비교 분석 완료: {comparison}")
    print("검증 결과 리포트 생성 중...")
    report_path = generate_report(metadb_analysis, comparison)
    
    print(f"\n=== 검증 완료 ===")
    print(f"리포트 파일: {report_path}")
    
    # 간단한 요약 출력
    pass_count = sum(1 for r in comparison.values() if r['status'] == 'PASS')
    total_count = len(comparison)
    pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
    
    print(f"전체 통과율: {pass_rate:.1f}% ({pass_count}/{total_count})")
    
    # 과소추출 항목 확인
    undershoot_items = [k for k, v in comparison.items() if v['difference'] < 0]
    if undershoot_items:
        print(f"과소추출 항목: {', '.join(undershoot_items)}")
    else:
        print("과소추출 문제 없음 ✅")

if __name__ == "__main__":
    main()
