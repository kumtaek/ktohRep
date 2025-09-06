import sqlite3

def check_metadb():
    conn = sqlite3.connect('../project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    # 테이블 목록 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # 각 테이블의 레코드 수 확인
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count}개")
        except Exception as e:
            print(f"{table_name}: 오류 - {e}")
    
    # files 테이블 샘플 확인 (테이블이 존재하는 경우에만)
    if any(table[0] == 'files' for table in tables):
        print("\n=== Files 테이블 샘플 ===")
        cursor.execute("SELECT path, loc FROM files LIMIT 5")
        files = cursor.fetchall()
        for file in files:
            print(f"파일: {file[0]}, 라인: {file[1]}")
    
    # classes 테이블 샘플 확인 (테이블이 존재하는 경우에만)
    if any(table[0] == 'classes' for table in tables):
        print("\n=== Classes 테이블 샘플 ===")
        cursor.execute("SELECT fqn, name FROM classes LIMIT 5")
        classes = cursor.fetchall()
        for cls in classes:
            print(f"클래스: {cls[0]}, 이름: {cls[1]}")
    
    # methods 테이블 샘플 확인 (테이블이 존재하는 경우에만)
    if any(table[0] == 'methods' for table in tables):
        print("\n=== Methods 테이블 샘플 ===")
        cursor.execute("SELECT name, signature FROM methods LIMIT 5")
        methods = cursor.fetchall()
        for method in methods:
            print(f"메소드: {method[0]}, 시그니처: {method[1]}")
    
    # edges 테이블 샘플 확인 (테이블이 존재하는 경우에만)
    if any(table[0] == 'edges' for table in tables):
        print("\n=== Edges 테이블 샘플 ===")
        cursor.execute("SELECT source_type, target_type, relationship_type FROM edges LIMIT 5")
        edges = cursor.fetchall()
        for edge in edges:
            print(f"소스: {edge[0]}, 타겟: {edge[1]}, 관계: {edge[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_metadb()