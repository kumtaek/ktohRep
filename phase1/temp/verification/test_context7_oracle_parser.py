#!/usr/bin/env python3
"""
Context7 기반 개선된 Oracle 파서 테스트
"""

import os
import sys
sys.path.append('phase1')

from parsers.parser_factory import ParserFactory

def test_context7_oracle_parser():
    """Context7 기반 개선된 Oracle 파서 테스트"""
    
    # 테스트할 SQL 쿼리들
    test_queries = [
        {
            'type': 'select',
            'sql': '''
                SELECT 
                    e.employee_id,
                    e.first_name || ' ' || e.last_name AS full_name,
                    d.department_name,
                    ROW_NUMBER() OVER (PARTITION BY d.department_id ORDER BY e.salary DESC) as rn
                FROM employees e
                INNER JOIN departments d ON e.department_id = d.department_id
                WHERE e.salary > 5000
                AND e.hire_date >= TO_DATE('2020-01-01', 'YYYY-MM-DD')
                CONNECT BY PRIOR e.employee_id = e.manager_id
                START WITH e.manager_id IS NULL
                ORDER BY e.salary DESC
            '''
        },
        {
            'type': 'insert',
            'sql': '''
                INSERT INTO employees (
                    employee_id, first_name, last_name, email, 
                    hire_date, job_id, salary, department_id
                ) VALUES (
                    1001, 'John', 'Doe', 'john.doe@company.com',
                    SYSDATE, 'IT_PROG', 7500, 60
                )
            '''
        },
        {
            'type': 'update',
            'sql': '''
                UPDATE employees 
                SET salary = salary * 1.1,
                    last_update = SYSTIMESTAMP
                WHERE department_id = 60
                AND hire_date < ADD_MONTHS(SYSDATE, -12)
            '''
        },
        {
            'type': 'delete',
            'sql': '''
                DELETE FROM employees 
                WHERE employee_id IN (
                    SELECT employee_id 
                    FROM employees 
                    WHERE hire_date < TO_DATE('2010-01-01', 'YYYY-MM-DD')
                )
            '''
        },
        {
            'type': 'truncate',
            'sql': '''
                TRUNCATE TABLE temp_employees
            '''
        },
        {
            'type': 'merge',
            'sql': '''
                MERGE INTO employees e
                USING new_employees n ON (e.employee_id = n.employee_id)
                WHEN MATCHED THEN
                    UPDATE SET 
                        e.first_name = n.first_name,
                        e.last_name = n.last_name,
                        e.salary = n.salary
                WHEN NOT MATCHED THEN
                    INSERT (employee_id, first_name, last_name, salary)
                    VALUES (n.employee_id, n.first_name, n.last_name, n.salary)
            '''
        }
    ]
    
    config = {'default_schema': 'DEFAULT'}
    factory = ParserFactory(config)
    
    print("=== Context7 기반 개선된 Oracle 파서 테스트 ===\n")
    
    total_expected = len(test_queries)
    total_parsed = 0
    total_unique = 0
    
    for i, query_info in enumerate(test_queries):
        query_type = query_info['type']
        sql_content = query_info['sql']
        
        print(f"테스트 {i+1}: {query_type.upper()} 쿼리")
        print(f"SQL: {sql_content.strip()[:100]}...")
        
        try:
            # 파서 가져오기
            parser = factory.get_parser('oracle', query_type)
            
            if parser:
                # Context7 기반 개선된 파서로 분석
                context = {'default_schema': 'DEFAULT'}
                result = parser.parse_content(sql_content, context)
                
                if isinstance(result, dict) and 'sql_units' in result:
                    parsed_count = len(result['sql_units'])
                    print(f"  Context7 파서 결과: {parsed_count}개 SQL Units")
                    
                    # 중복 체크
                    sql_ids = [unit.get('unique_id', '') for unit in result['sql_units']]
                    unique_ids = set(sql_ids)
                    unique_count = len(unique_ids)
                    
                    if len(sql_ids) != unique_count:
                        print(f"  ⚠️ 중복 발견: {len(sql_ids)}개 중 {unique_count}개 고유")
                    else:
                        print(f"  ✅ 중복 없음: {unique_count}개 모두 고유")
                    
                    # 각 SQL Unit 상세 분석
                    for j, unit in enumerate(result['sql_units']):
                        print(f"    [{j+1}] {unit.get('type', 'unknown')} - {unit.get('unique_id', 'no-id')}")
                        if unit.get('tables'):
                            print(f"        테이블: {unit['tables']}")
                        if unit.get('columns'):
                            print(f"        컬럼: {unit['columns'][:3]}...")  # 처음 3개만 표시
                        if unit.get('oracle_features'):
                            features = unit['oracle_features']
                            feature_count = sum(len(v) for v in features.values() if isinstance(v, list))
                            print(f"        Oracle 기능: {feature_count}개")
                    
                    # Oracle 특화 기능 확인
                    if 'oracle_features' in result:
                        features = result['oracle_features']
                        print(f"  Oracle 특화 기능:")
                        for feature_type, feature_list in features.items():
                            if feature_list:
                                print(f"    {feature_type}: {len(feature_list)}개")
                    
                    total_parsed += parsed_count
                    total_unique += unique_count
                else:
                    print(f"  ❌ 파싱 실패: {type(result)}")
            else:
                print(f"  ❌ 파서를 찾을 수 없음: oracle/{query_type}")
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print(f"=== Context7 기반 Oracle 파서 전체 결과 ===")
    print(f"테스트 쿼리 수: {total_expected}")
    print(f"파싱된 총 SQL Units: {total_parsed}")
    print(f"고유 SQL Units: {total_unique}")
    if total_expected > 0:
        success_rate = (total_parsed / total_expected) * 100
        print(f"성공률: {success_rate:.1f}%")
    
    # 중복 방지 효과
    if total_parsed > 0:
        duplication_rate = ((total_parsed - total_unique) / total_parsed) * 100
        print(f"중복률: {duplication_rate:.1f}%")
    
    return total_expected, total_parsed, total_unique

if __name__ == "__main__":
    test_context7_oracle_parser()


