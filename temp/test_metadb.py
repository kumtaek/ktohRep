#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def test_metadb():
    conn = sqlite3.connect('../project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    print("=== Files table ===")
    cursor.execute("SELECT * FROM files LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n=== Sql_units table ===")
    cursor.execute("SELECT * FROM sql_units LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n=== Java files count ===")
    cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
    print(f"Java files: {cursor.fetchone()[0]}")
    
    print("\n=== Sql_units count ===")
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    print(f"Sql_units: {cursor.fetchone()[0]}")
    
    print("\n=== Java files with sql_units ===")
    cursor.execute("""
        SELECT f.path, COUNT(s.sql_id) as method_count
        FROM files f
        LEFT JOIN sql_units s ON f.file_id = s.file_id
        WHERE f.language = 'java'
        GROUP BY f.file_id, f.path
    """)
    for row in cursor.fetchall():
        print(row)
    
    conn.close()

if __name__ == "__main__":
    test_metadb()





