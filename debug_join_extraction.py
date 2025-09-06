"""
JOIN 추출 로직 디버깅
"""
import re
import xml.etree.ElementTree as ET

def debug_join_extraction():
    print("JOIN 추출 로직 디버깅")
    print("-" * 50)
    
    xml_file = "./project/sampleSrc/src/main/resources/mybatis/mapper/MixedErrorMapper.xml"
    
    try:
        # XML 파일 파싱
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print("XML 파싱 성공")
        
        # 모든 SQL 쿼리 태그를 분석
        for sql_element in root.findall('.//select') + root.findall('.//update') + root.findall('.//insert') + root.findall('.//delete'):
            query_id = sql_element.get('id', 'unknown')
            print(f"\n쿼리 ID: {query_id}")
            
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
            print(sql_text[:200] + "..." if len(sql_text) > 200 else sql_text)
            
            # JOIN 패턴 검사
            join_patterns = [
                r'(?:INNER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
                r'LEFT\s+(?:OUTER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
                r'RIGHT\s+(?:OUTER\s+)?JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?',
                r'FULL\s+OUTER\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?(?:\s+ON\s+(.+?)(?=\s+(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN|\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|$))?'
            ]
            
            # FROM 절에서 메인 테이블 추출
            from_match = re.search(r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?', 
                                   sql_text, re.IGNORECASE)
            
            main_table = None
            if from_match:
                main_table = from_match.group(1)
                print(f"메인 테이블: {main_table}")
            else:
                print("메인 테이블을 찾을 수 없음")
            
            # JOIN 패턴 매칭
            joins_found = []
            for i, pattern in enumerate(join_patterns):
                matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
                
                for match in matches:
                    target_table = match.group(1)
                    alias = match.group(2) if match.group(2) else target_table
                    join_condition = match.group(3).strip() if match.group(3) else ''
                    
                    print(f"패턴 {i+1} 매치: 테이블={target_table}, 별칭={alias}, 조건={join_condition[:50]}...")
                    
                    if main_table and main_table != target_table:
                        joins_found.append({
                            'source_table': main_table,
                            'target_table': target_table,
                            'join_type': 'LEFT' if 'LEFT' in pattern else 'INNER',
                            'join_condition': join_condition,
                            'target_alias': alias
                        })
            
            print(f"이 쿼리에서 발견된 JOIN: {len(joins_found)}개")
            for join in joins_found:
                print(f"  - {join['source_table']} --[{join['join_type']}]--> {join['target_table']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_join_extraction()