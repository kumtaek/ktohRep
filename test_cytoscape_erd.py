#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cytoscape.js ERD 테스트 스크립트
"""

import sys
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from visualize.renderers.cytoscape_erd_renderer import create_cytoscape_erd


def main():
    """테스트 메인 함수"""
    print("🎨 Cytoscape.js ERD 테스트 시작")
    
    # 테스트 데이터 생성
    test_data = {
        'nodes': [
            {
                'id': 'table:HR.EMPLOYEES',
                'label': 'EMPLOYEES',
                'type': 'table',
                'group': 'DB',
                'meta': {
                    'owner': 'HR',
                    'table_name': 'EMPLOYEES',
                    'status': 'VALID',
                    'comment': '직원 정보 테이블',
                    'pk_columns': ['EMPLOYEE_ID'],
                    'columns': [
                        {
                            'name': 'EMPLOYEE_ID',
                            'data_type': 'NUMBER',
                            'nullable': False,
                            'is_pk': True,
                            'comment': '직원 고유 ID'
                        },
                        {
                            'name': 'FIRST_NAME',
                            'data_type': 'VARCHAR2(50)',
                            'nullable': False,
                            'is_pk': False,
                            'comment': '이름'
                        },
                        {
                            'name': 'LAST_NAME',
                            'data_type': 'VARCHAR2(50)',
                            'nullable': False,
                            'is_pk': False,
                            'comment': '성'
                        },
                        {
                            'name': 'EMAIL',
                            'data_type': 'VARCHAR2(100)',
                            'nullable': False,
                            'is_pk': False,
                            'comment': '이메일'
                        },
                        {
                            'name': 'DEPARTMENT_ID',
                            'data_type': 'NUMBER',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '부서 ID'
                        },
                        {
                            'name': 'HIRE_DATE',
                            'data_type': 'DATE',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '입사일'
                        }
                    ]
                }
            },
            {
                'id': 'table:HR.DEPARTMENTS',
                'label': 'DEPARTMENTS',
                'type': 'table',
                'group': 'DB',
                'meta': {
                    'owner': 'HR',
                    'table_name': 'DEPARTMENTS',
                    'status': 'VALID',
                    'comment': '부서 정보 테이블',
                    'pk_columns': ['DEPARTMENT_ID'],
                    'columns': [
                        {
                            'name': 'DEPARTMENT_ID',
                            'data_type': 'NUMBER',
                            'nullable': False,
                            'is_pk': True,
                            'comment': '부서 고유 ID'
                        },
                        {
                            'name': 'DEPARTMENT_NAME',
                            'data_type': 'VARCHAR2(100)',
                            'nullable': False,
                            'is_pk': False,
                            'comment': '부서명'
                        },
                        {
                            'name': 'MANAGER_ID',
                            'data_type': 'NUMBER',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '매니저 ID'
                        },
                        {
                            'name': 'LOCATION_ID',
                            'data_type': 'NUMBER',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '위치 ID'
                        }
                    ]
                }
            },
            {
                'id': 'table:HR.LOCATIONS',
                'label': 'LOCATIONS',
                'type': 'table',
                'group': 'DB',
                'meta': {
                    'owner': 'HR',
                    'table_name': 'LOCATIONS',
                    'status': 'VALID',
                    'comment': '위치 정보 테이블',
                    'pk_columns': ['LOCATION_ID'],
                    'columns': [
                        {
                            'name': 'LOCATION_ID',
                            'data_type': 'NUMBER',
                            'nullable': False,
                            'is_pk': True,
                            'comment': '위치 고유 ID'
                        },
                        {
                            'name': 'STREET_ADDRESS',
                            'data_type': 'VARCHAR2(200)',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '도로명 주소'
                        },
                        {
                            'name': 'CITY',
                            'data_type': 'VARCHAR2(100)',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '도시'
                        },
                        {
                            'name': 'COUNTRY_ID',
                            'data_type': 'CHAR(2)',
                            'nullable': True,
                            'is_pk': False,
                            'comment': '국가 코드'
                        }
                    ]
                }
            }
        ],
        'edges': [
            {
                'id': 'fk_emp_dept',
                'source': 'table:HR.EMPLOYEES',
                'target': 'table:HR.DEPARTMENTS',
                'kind': 'foreign_key',
                'confidence': 0.95,
                'meta': {
                    'left_column': 'DEPARTMENT_ID',
                    'right_column': 'DEPARTMENT_ID',
                    'frequency': 10,
                    'arrow': True,
                    'source': 'joins_table',
                    'join_condition': 'EMPLOYEES.DEPARTMENT_ID = DEPARTMENTS.DEPARTMENT_ID'
                }
            },
            {
                'id': 'fk_dept_loc',
                'source': 'table:HR.DEPARTMENTS',
                'target': 'table:HR.LOCATIONS',
                'kind': 'foreign_key',
                'confidence': 0.9,
                'meta': {
                    'left_column': 'LOCATION_ID',
                    'right_column': 'LOCATION_ID',
                    'frequency': 5,
                    'arrow': True,
                    'source': 'joins_table',
                    'join_condition': 'DEPARTMENTS.LOCATION_ID = LOCATIONS.LOCATION_ID'
                }
            },
            {
                'id': 'fk_emp_mgr',
                'source': 'table:HR.EMPLOYEES',
                'target': 'table:HR.EMPLOYEES',
                'kind': 'self_reference',
                'confidence': 0.8,
                'meta': {
                    'left_column': 'MANAGER_ID',
                    'right_column': 'EMPLOYEE_ID',
                    'frequency': 3,
                    'arrow': True,
                    'source': 'joins_table',
                    'join_condition': 'EMPLOYEES.MANAGER_ID = EMPLOYEES.EMPLOYEE_ID'
                }
            }
        ]
    }
    
    try:
        # 출력 디렉토리 생성
        output_dir = Path("./test_output")
        output_dir.mkdir(exist_ok=True)
        
        print(f"📁 출력 디렉토리: {output_dir.absolute()}")
        
        # Cytoscape.js ERD 생성
        print("🎨 Cytoscape.js ERD 생성 중...")
        result_path = create_cytoscape_erd(test_data, "TEST_HR_PROJECT", output_dir)
        
        print(f"✅ Cytoscape.js ERD 생성 완료!")
        print(f"📄 파일 경로: {result_path}")
        print(f"📊 테이블 수: {len(test_data['nodes'])}")
        print(f"🔗 관계 수: {len(test_data['edges'])}")
        
        # 생성된 파일 내용 확인
        if result_path.exists():
            print(f"📏 파일 크기: {result_path.stat().st_size:,} bytes")
            
            # HTML 내용 일부 출력
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📝 HTML 내용 미리보기:")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 50)
        
        print("\n🎉 테스트 완료! 브라우저에서 생성된 HTML 파일을 열어보세요.")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
