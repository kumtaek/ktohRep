import sqlite3
import os

def deduplicate_metadb(db_path):
    """metadata.db에서 중복된 항목을 제거합니다."""
    if not os.path.exists(db_path):
        print(f"오류: 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("데이터베이스 중복 제거 시작...")

    # 1. classes 테이블 중복 제거
    print("\nclasses 테이블 중복 제거 중...")
    cursor.execute("""
        SELECT file_id, fqn, COUNT(*) as count
        FROM classes
        GROUP BY file_id, fqn
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()

    for file_id, fqn, count in duplicates:
        print(f"  - 중복 발견: file_id={file_id}, fqn='{fqn}', count={count}")
        cursor.execute("""
            SELECT class_id FROM classes
            WHERE file_id = ? AND fqn = ?
            ORDER BY class_id
        """, (file_id, fqn))
        class_ids = [row[0] for row in cursor.fetchall()]
        
        id_to_keep = class_ids[0]
        ids_to_delete = class_ids[1:]
        print(f"    - 유지할 class_id: {id_to_keep}")
        print(f"    - 삭제할 class_id: {ids_to_delete}")

        # methods 테이블의 class_id를 업데이트
        if ids_to_delete:
            placeholders = ', '.join('?' * len(ids_to_delete))
            cursor.execute(f"""
                UPDATE methods
                SET class_id = ?
                WHERE class_id IN ({placeholders})
            """, (id_to_keep, *ids_to_delete))
            print(f"    - methods 테이블의 {cursor.rowcount}개 레코드 업데이트 완료.")

            # 중복된 class 항목 삭제
            cursor.execute(f"""
                DELETE FROM classes
                WHERE class_id IN ({placeholders})
            """, ids_to_delete)
            print(f"    - classes 테이블에서 {cursor.rowcount}개 중복 레코드 삭제 완료.")

    # 2. sql_units 테이블 중복 제거
    print("\nsql_units 테이블 중복 제거 중...")
    cursor.execute("""
        SELECT file_id, stmt_id, COUNT(*) as count
        FROM sql_units
        GROUP BY file_id, stmt_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()

    for file_id, stmt_id, count in duplicates:
        print(f"  - 중복 발견: file_id={file_id}, stmt_id='{stmt_id}', count={count}")
        cursor.execute("""
            SELECT sql_id FROM sql_units
            WHERE file_id = ? AND stmt_id = ?
            ORDER BY sql_id
        """, (file_id, stmt_id))
        sql_ids = [row[0] for row in cursor.fetchall()]

        id_to_keep = sql_ids[0]
        ids_to_delete = sql_ids[1:]
        print(f"    - 유지할 sql_id: {id_to_keep}")
        print(f"    - 삭제할 sql_id: {ids_to_delete}")

        # sql_units에서 중복 삭제 (다른 테이블과의 FK는 없다고 가정)
        if ids_to_delete:
            placeholders = ', '.join('?' * len(ids_to_delete))
            cursor.execute(f"""
                DELETE FROM sql_units
                WHERE sql_id IN ({placeholders})
            """, ids_to_delete)
            print(f"    - sql_units 테이블에서 {cursor.rowcount}개 중복 레코드 삭제 완료.")

    conn.commit()
    conn.close()
    print("\n데이터베이스 중복 제거 완료.")

if __name__ == '__main__':
    db_path = os.path.join('project', 'sampleSrc', 'metadata.db')
    deduplicate_metadb(db_path)
