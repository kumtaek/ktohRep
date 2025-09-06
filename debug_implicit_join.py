"""
Implicit JOIN 추출 로직 디버깅
"""
import re
import xml.etree.ElementTree as ET

def debug_implicit_join():
    print("Implicit JOIN 추출 로직 디버깅")
    print("-" * 50)
    
    xml_file = "./project/sampleSrc/src/main/resources/mybatis/mapper/ImplicitJoinMapper.xml"
    
    try:
        # XML 파일 파싱
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print("XML 파싱 성공")
        
        # 모든 SQL 쿼리 태그를 분석
        for sql_element in root.findall('.//select'):
            query_id = sql_element.get('id', 'unknown')
            print(f"\n=== 쿼리 ID: {query_id} ===")
            
            # SQL 텍스트 추출
            def get_all_text(elem):
                text = elem.text or ''
                for child in elem:
                    text += get_all_text(child)
                    if child.tail:
                        text += child.tail
                return text
            
            sql_text = get_all_text(sql_element)
            sql_text = sql_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            sql_text = sql_text.strip()
            
            print(f"SQL 텍스트:")
            print(sql_text)
            print()
            
            # FROM 절 추출 테스트
            from_match = re.search(r'FROM\s+(.+?)(?:\s+WHERE|\s+LEFT\s+JOIN|\s+RIGHT\s+JOIN|\s+INNER\s+JOIN|\s+JOIN|\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', sql_text, re.IGNORECASE | re.DOTALL)
            
            if from_match:
                from_clause = from_match.group(1).strip()
                print(f"FROM 절: '{from_clause}'")
                
                # Implicit JOIN 검사
                if ',' in from_clause and 'JOIN' not in from_clause.upper():
                    print("Implicit JOIN 패턴 발견!")
                    
                    table_parts = [part.strip() for part in from_clause.split(',')]
                    print(f"테이블 부분들: {table_parts}")
                    
                    all_tables = []
                    for part in table_parts:
                        table_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?', part.strip())
                        if table_match:
                            table_name = table_match.group(1)
                            alias = table_match.group(2) if table_match.group(2) else table_name
                            all_tables.append({'name': table_name, 'alias': alias})
                            print(f"  테이블: {table_name}, 별칭: {alias}")
                    
                    if all_tables:
                        main_table = all_tables[0]['name']
                        print(f"메인 테이블: {main_table}")
                        
                        # WHERE 절 추출
                        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', 
                                               sql_text, re.IGNORECASE | re.DOTALL)
                        if where_match:
                            where_conditions = where_match.group(1).strip()
                            print(f"WHERE 조건: '{where_conditions}'")
                            
                            # 조인 조건 찾기
                            for table_info in all_tables[1:]:
                                target_table = table_info['name']
                                print(f"\n{main_table} -> {target_table} 조인 조건 찾기:")
                                
                                # 테이블명과 별칭 매핑
                                table_aliases = {}
                                for ti in all_tables:
                                    table_aliases[ti['name']] = ti['alias']
                                    table_aliases[ti['alias']] = ti['name']
                                
                                main_alias = table_aliases.get(main_table, main_table)
                                target_alias = table_aliases.get(target_table, target_table)
                                
                                print(f"  메인 별칭: {main_alias}, 타겟 별칭: {target_alias}")
                                
                                # 조인 조건 패턴들
                                join_patterns = [
                                    rf'{main_alias}\.(\w+)\s*=\s*{target_alias}\.(\w+)',
                                    rf'{target_alias}\.(\w+)\s*=\s*{main_alias}\.(\w+)',
                                    rf'{main_table}\.(\w+)\s*=\s*{target_table}\.(\w+)',
                                    rf'{target_table}\.(\w+)\s*=\s*{main_table}\.(\w+)'
                                ]
                                
                                found_conditions = []
                                for i, pattern in enumerate(join_patterns):
                                    print(f"  패턴 {i+1}: {pattern}")
                                    matches = re.finditer(pattern, where_conditions, re.IGNORECASE)
                                    for match in matches:
                                        found_conditions.append(match.group(0))
                                        print(f"    매치: {match.group(0)}")
                                
                                if found_conditions:
                                    join_condition = ' AND '.join(found_conditions)
                                    print(f"  최종 조인 조건: {join_condition}")
                                else:
                                    print(f"  조인 조건을 찾지 못함")
                        
                        print(f"\nImplicit JOIN 관계:")
                        for table_info in all_tables[1:]:
                            print(f"  {main_table} --[INNER]--> {table_info['name']}")
                else:
                    print("Implicit JOIN 패턴이 아님")
            else:
                print("FROM 절을 찾을 수 없음")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_implicit_join()