#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('phase1/project/sampleSrc/metadata.db')
cursor = conn.cursor()

print("files 테이블 내용:")
cursor.execute("SELECT file_id, path, language FROM files ORDER BY file_id")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} ({row[2]})")

print(f"\n총 파일 수: {cursor.rowcount}")

conn.close()



