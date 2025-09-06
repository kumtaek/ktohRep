#!/usr/bin/env python3
"""JOIN 정규식 패턴 테스트 스크립트"""

import re

def test_join_patterns():
    """JOIN 정규식 패턴을 실제 SQL로 테스트합니다."""
    
    # 실제 JSP에서 추출된 SQL들
    test_sqls = [
        "LEFT JOIN categories c ON p.category_id = c.id",
        "LEFT JOIN brands b ON p.brand_id = b.id",
        "JOIN customers c ON o.customer_id = c.id",
        "p.category_id = c.id",  # 암시적 JOIN
        "o.customer_id = c.id",  # 암시적 JOIN
    ]
    
    # 현재 사용 중인 JOIN 패턴들
    join_patterns = [
        # 명시적 JOIN 패턴 (JSP에서 실제 사용되는 패턴) - 우선순위 높음
        r'LEFT\s+JOIN\s+(\w+)\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # LEFT JOIN table alias ON a.col = b.col
        r'JOIN\s+(\w+)\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # JOIN table alias ON a.col = b.col
        r'RIGHT\s+JOIN\s+(\w+)\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # RIGHT JOIN table alias ON a.col = b.col
        r'INNER\s+JOIN\s+(\w+)\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # INNER JOIN table alias ON a.col = b.col
        r'JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # JOIN table ON a.col = b.col
        # 암시적 JOIN 패턴 (WHERE 절) - 우선순위 낮음
        r'WHERE\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # WHERE a.id = b.fk
        r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',  # a.id = b.fk (일반적인 패턴)
    ]
    
    print("🔍 JOIN 정규식 패턴 테스트 시작")
    print("=" * 60)
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n📝 테스트 SQL {i}: {sql}")
        print("-" * 40)
        
        matched = False
        for j, pattern in enumerate(join_patterns, 1):
            matches = list(re.finditer(pattern, sql, re.IGNORECASE))
            
            if matches:
                matched = True
                print(f"✅ 패턴 {j} 매치 성공!")
                for match in matches:
                    groups = match.groups()
                    print(f"   그룹 수: {len(groups)}")
                    print(f"   그룹 내용: {groups}")
                    
                    # 그룹 수별 처리 로직 테스트
                    if len(groups) == 6:  # 명시적 JOIN
                        table, alias, l_ref, l_col, r_ref, r_col = groups
                        print(f"   → 명시적 JOIN: {table}({alias}) ON {l_ref}.{l_col} = {r_ref}.{r_col}")
                    elif len(groups) == 4:  # 암시적 JOIN
                        l_ref, l_col, r_ref, r_col = groups
                        print(f"   → 암시적 JOIN: {l_ref}.{l_col} = {r_ref}.{r_col}")
                    else:
                        print(f"   → 지원되지 않는 그룹 수: {len(groups)}")
            else:
                print(f"❌ 패턴 {j} 매치 실패")
        
        if not matched:
            print("❌ 모든 패턴에서 매치 실패!")
    
    print("\n" + "=" * 60)
    print("🔍 JOIN 정규식 패턴 테스트 완료")

if __name__ == "__main__":
    test_join_patterns()
