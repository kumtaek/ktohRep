#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_sql_pattern():
    print("=== SQL 패턴 테스트 ===")
    
    # Java 파서의 수정된 SQL 패턴
    sql_pattern = re.compile(
        r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']',
        re.IGNORECASE
    )
    
    # 테스트할 Java 코드 샘플
    test_code = '''
    String sql1 = "SELECT * FROM users WHERE id = ?";
    String sql2 = "UPDATE users SET name = ? WHERE id = ?";
    String sql3 = "INSERT INTO users (name, email) VALUES (?, ?)";
    String sql4 = "DELETE FROM users WHERE id = ?";
    String sql5 = "CREATE TABLE users (id INT, name VARCHAR(50))";
    String sql6 = "ALTER TABLE users ADD COLUMN age INT";
    String sql7 = "DROP TABLE users";
    String sql8 = "TRUNCATE TABLE users";
    String sql9 = "MERGE INTO users USING temp_users ON users.id = temp_users.id";
    String sql10 = "SELECT u.name, p.title FROM users u JOIN products p ON u.id = p.user_id";
    String sql11 = "SELECT COUNT(*) FROM users WHERE status = 'active'";
    String sql12 = "UPDATE users SET last_login = NOW() WHERE id = ?";
    String sql13 = "INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)";
    String sql14 = "DELETE FROM orders WHERE created_at < ?";
    String sql15 = "CREATE INDEX idx_users_email ON users(email)";
    String sql16 = "ALTER TABLE users MODIFY COLUMN email VARCHAR(100)";
    String sql17 = "DROP INDEX idx_users_email";
    String sql18 = "TRUNCATE TABLE orders";
    String sql19 = "MERGE INTO products USING temp_products ON products.id = temp_products.id";
    String sql20 = "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id";
    '''
    
    print("테스트 코드:")
    print(test_code)
    print("\n=== SQL 패턴 매칭 결과 ===")
    
    matches = sql_pattern.finditer(test_code)
    count = 0
    for match in matches:
        count += 1
        sql_content = match.group(1)
        print(f"SQL {count}: {sql_content}")
    
    print(f"\n총 {count}개의 SQL 문자열을 찾았습니다.")
    
    # 실제 Java 파일에서 테스트
    print("\n=== 실제 Java 파일 테스트 ===")
    try:
        with open("../project/sampleSrc/src/main/java/com/example/controller/OrderController.java", 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = sql_pattern.finditer(content)
        count = 0
        for match in matches:
            count += 1
            sql_content = match.group(1)
            print(f"실제 SQL {count}: {sql_content[:100]}...")
        
        print(f"\n실제 파일에서 {count}개의 SQL 문자열을 찾았습니다.")
        
    except Exception as e:
        print(f"파일 읽기 오류: {e}")

if __name__ == "__main__":
    test_sql_pattern()
