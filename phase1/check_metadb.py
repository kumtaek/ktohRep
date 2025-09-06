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
    
    # db_tables 테이블 샘플 확인
    print("\n=== DB Tables 테이블 샘플 ===")
    cursor.execute("SELECT table_name, owner FROM db_tables LIMIT 5")
    tables = cursor.fetchall()
    for table in tables:
        print(f"테이블: {table[0]}, 소유자: {table[1]}")
    
    # db_columns 테이블 구조 확인
    print("\n=== DB Columns 테이블 구조 ===")
    cursor.execute("PRAGMA table_info(db_columns)")
    columns_info = cursor.fetchall()
    for col in columns_info:
        print(f"컬럼: {col[1]}, 타입: {col[2]}")
    
    # db_columns 테이블 샘플 확인
    print("\n=== DB Columns 테이블 샘플 ===")
    cursor.execute("SELECT * FROM db_columns LIMIT 5")
    columns = cursor.fetchall()
    for column in columns:
        print(f"데이터: {column}")
    
    conn.close()

if __name__ == "__main__":
    check_metadb()
