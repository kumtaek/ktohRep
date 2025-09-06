#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def final_ground_truth_analysis():
    """최종 Ground Truth 분석"""
    
    print("=== 최종 Ground Truth 검증 및 비교 분석 ===\n")
    
    # 실제 소스코드 직접 분석 결과
    actual_source = {
        'total_files': 32,
        'total_methods': 74,
        'total_classes': 15,
        'total_sql_queries': 37,
        'total_sql_injection': 54
    }
    
    # 메타디비 분석 결과
    metadb_result = {
        'total_files': 31,
        'java_files': 20,
        'total_methods': 311,
        'total_classes': 120,
        'total_sql_units': 172
    }
    
    print("1. 실제 소스코드 직접 분석 결과:")
    print(f"   총 파일 수: {actual_source['total_files']}")
    print(f"   총 메소드 수: {actual_source['total_methods']}")
    print(f"   총 클래스 수: {actual_source['total_classes']}")
    print(f"   총 SQL 쿼리 수: {actual_source['total_sql_queries']}")
    print(f"   총 SQL Injection 패턴 수: {actual_source['total_sql_injection']}")
    
    print(f"\n2. 메타디비 분석 결과:")
    print(f"   총 파일 수: {metadb_result['total_files']}")
    print(f"   Java 파일 수: {metadb_result['java_files']}")
    print(f"   총 메소드 수: {metadb_result['total_methods']}")
    print(f"   총 클래스 수: {metadb_result['total_classes']}")
    print(f"   총 SQL 유닛 수: {metadb_result['total_sql_units']}")
    
    print(f"\n3. 비교 분석:")
    
    # 파일 수 비교
    file_diff = metadb_result['total_files'] - actual_source['total_files']
    file_accuracy = (actual_source['total_files'] / metadb_result['total_files'] * 100) if metadb_result['total_files'] > 0 else 0
    print(f"   파일 수: 실제 {actual_source['total_files']} vs 메타디비 {metadb_result['total_files']} (차이: {file_diff}, 정확도: {file_accuracy:.1f}%)")
    
    # 메소드 수 비교
    method_diff = metadb_result['total_methods'] - actual_source['total_methods']
    method_accuracy = (actual_source['total_methods'] / metadb_result['total_methods'] * 100) if metadb_result['total_methods'] > 0 else 0
    print(f"   메소드 수: 실제 {actual_source['total_methods']} vs 메타디비 {metadb_result['total_methods']} (차이: {method_diff}, 정확도: {method_accuracy:.1f}%)")
    
    # 클래스 수 비교
    class_diff = metadb_result['total_classes'] - actual_source['total_classes']
    class_accuracy = (actual_source['total_classes'] / metadb_result['total_classes'] * 100) if metadb_result['total_classes'] > 0 else 0
    print(f"   클래스 수: 실제 {actual_source['total_classes']} vs 메타디비 {metadb_result['total_classes']} (차이: {class_diff}, 정확도: {class_accuracy:.1f}%)")
    
    # SQL 쿼리 수 비교
    sql_diff = metadb_result['total_sql_units'] - actual_source['total_sql_queries']
    sql_accuracy = (actual_source['total_sql_queries'] / metadb_result['total_sql_units'] * 100) if metadb_result['total_sql_units'] > 0 else 0
    print(f"   SQL 쿼리 수: 실제 {actual_source['total_sql_queries']} vs 메타디비 {metadb_result['total_sql_units']} (차이: {sql_diff}, 정확도: {sql_accuracy:.1f}%)")
    
    print(f"\n4. 정확도 평가:")
    
    # 5% 이내 정확도 확인
    accuracies = [file_accuracy, method_accuracy, class_accuracy, sql_accuracy]
    avg_accuracy = sum(accuracies) / len(accuracies)
    
    print(f"   평균 정확도: {avg_accuracy:.1f}%")
    
    if avg_accuracy >= 95:
        print("   ✅ 정확도 우수 (95% 이상)")
    elif avg_accuracy >= 90:
        print("   ⚠️  정확도 양호 (90-95%)")
    elif avg_accuracy >= 80:
        print("   ⚠️  정확도 보통 (80-90%)")
    else:
        print("   ❌ 정확도 개선 필요 (80% 미만)")
    
    # 5% 이상 차이나는 항목 식별
    print(f"\n5. 5% 이상 차이나는 항목:")
    items = [
        ("파일 수", file_accuracy),
        ("메소드 수", method_accuracy),
        ("클래스 수", class_accuracy),
        ("SQL 쿼리 수", sql_accuracy)
    ]
    
    significant_diffs = [item for item in items if abs(100 - item[1]) > 5]
    
    if significant_diffs:
        for item_name, accuracy in significant_diffs:
            diff_percent = abs(100 - accuracy)
            print(f"   - {item_name}: {diff_percent:.1f}% 차이 (정확도: {accuracy:.1f}%)")
    else:
        print("   모든 항목이 5% 이내 차이")
    
    print(f"\n6. 주요 발견사항:")
    
    # 메소드 과추출 문제
    if method_accuracy < 50:
        print(f"   ❌ 심각한 메소드 과추출: 메타디비가 실제보다 {method_diff}개 더 많이 추출")
        print(f"      - 실제: {actual_source['total_methods']}개")
        print(f"      - 메타디비: {metadb_result['total_methods']}개")
        print(f"      - 과추출률: {((metadb_result['total_methods'] - actual_source['total_methods']) / actual_source['total_methods'] * 100):.1f}%")
    
    # 클래스 과추출 문제
    if class_accuracy < 50:
        print(f"   ❌ 심각한 클래스 과추출: 메타디비가 실제보다 {class_diff}개 더 많이 추출")
        print(f"      - 실제: {actual_source['total_classes']}개")
        print(f"      - 메타디비: {metadb_result['total_classes']}개")
        print(f"      - 과추출률: {((metadb_result['total_classes'] - actual_source['total_classes']) / actual_source['total_classes'] * 100):.1f}%")
    
    # SQL 쿼리 과추출 문제
    if sql_accuracy < 50:
        print(f"   ❌ 심각한 SQL 쿼리 과추출: 메타디비가 실제보다 {sql_diff}개 더 많이 추출")
        print(f"      - 실제: {actual_source['total_sql_queries']}개")
        print(f"      - 메타디비: {metadb_result['total_sql_units']}개")
        print(f"      - 과추출률: {((metadb_result['total_sql_units'] - actual_source['total_sql_queries']) / actual_source['total_sql_queries'] * 100):.1f}%")
    
    print(f"\n7. 결론:")
    if avg_accuracy >= 95 and not significant_diffs:
        print("   ✅ Ground Truth 검증 완료: 실제 소스코드와 메타디비 결과가 일치")
        print("   ✅ 파서 정확도 우수: 5% 이내 오차로 양호한 성능")
    else:
        print("   ⚠️  Ground Truth 검증 필요: 실제 소스코드와 메타디비 결과 차이 발견")
        print("   ⚠️  파서 개선 필요: 5% 이상 차이나는 항목 존재")
        
        if avg_accuracy < 50:
            print("   ❌ 심각한 정확도 문제: 파서 재설계 필요")
            print("   📋 권장사항:")
            print("      - Java 파서의 메소드/클래스 추출 로직 개선")
            print("      - SQL 파서의 쿼리 추출 로직 개선")
            print("      - Context7 기반 파서 패턴 재검토")
        elif avg_accuracy < 80:
            print("   ⚠️  중간 수준 정확도 문제: 파서 로직 개선 필요")
        else:
            print("   ⚠️  미세한 정확도 문제: 파서 패턴 조정 필요")
    
    return {
        'actual_source': actual_source,
        'metadb_result': metadb_result,
        'avg_accuracy': avg_accuracy,
        'significant_diffs': significant_diffs
    }

if __name__ == "__main__":
    final_ground_truth_analysis()
