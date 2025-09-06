#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 다이나믹 쿼리 샘플 생성기
- 재사용성을 위해 명확한 구조와 주석 포함
"""

import os
from datetime import datetime

def create_simple_sample():
    """간단한 다이나믹 쿼리 샘플 생성"""
    
    print("=== 간단한 다이나믹 쿼리 샘플 생성 ===")
    
    # 1. 디렉토리 생성
    create_directories()
    
    # 2. Java 파일 생성
    create_java_files()
    
    # 3. JSP 파일 생성
    create_jsp_files()
    
    # 4. SQL 파일 생성
    create_sql_files()
    
    # 5. 리포트 생성
    generate_report()
    
    print("✅ 샘플 생성 완료")

def create_directories():
    """디렉토리 구조 생성"""
    
    directories = [
        '../project/sampleSrc/src/main/java/com/example/controller',
        '../project/sampleSrc/src/main/java/com/example/service',
        '../project/sampleSrc/src/main/java/com/example/mapper',
        '../project/sampleSrc/src/main/java/com/example/model',
        '../project/sampleSrc/src/main/resources/mybatis/mapper',
        '../project/sampleSrc/src/main/webapp/user',
        '../project/sampleSrc/db_schema'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 디렉토리 구조 생성 완료")

def create_java_files():
    """Java 파일들 생성"""
    
    # UserController.java
    controller_content = '''package com.example.controller;

import com.example.model.User;
import com.example.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 사용자 컨트롤러 - 다이나믹 쿼리 파라미터 처리
 */
@Controller
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/list")
    public String getUserList(@RequestParam(required = false) String name,
                             @RequestParam(required = false) String email,
                             @RequestParam(required = false) String status,
                             Model model) {
        
        Map<String, Object> params = new java.util.HashMap<>();
        if (name != null && !name.trim().isEmpty()) {
            params.put("name", "%" + name + "%");
        }
        if (email != null && !email.trim().isEmpty()) {
            params.put("email", "%" + email + "%");
        }
        if (status != null && !status.trim().isEmpty()) {
            params.put("status", status);
        }
        
        List<User> users = userService.getUsersByCondition(params);
        model.addAttribute("users", users);
        model.addAttribute("searchParams", params);
        
        return "user/list";
    }
    
    @PostMapping("/search")
    public String searchUsers(@RequestParam Map<String, String> searchParams, Model model) {
        
        Map<String, Object> params = new java.util.HashMap<>();
        
        if (searchParams.get("userType") != null) {
            params.put("userType", searchParams.get("userType"));
        }
        
        if (searchParams.get("minAge") != null && !searchParams.get("minAge").isEmpty()) {
            params.put("minAge", Integer.parseInt(searchParams.get("minAge")));
        }
        
        if (searchParams.get("maxAge") != null && !searchParams.get("maxAge").isEmpty()) {
            params.put("maxAge", Integer.parseInt(searchParams.get("maxAge")));
        }
        
        List<User> users = userService.getUsersByAdvancedCondition(params);
        model.addAttribute("users", users);
        model.addAttribute("searchParams", searchParams);
        
        return "user/searchResult";
    }
}'''

    with open('../project/sampleSrc/src/main/java/com/example/controller/UserController.java', 'w', encoding='utf-8') as f:
        f.write(controller_content)
    
    # User.java
    user_model = '''package com.example.model;

import java.util.Date;

public class User {
    
    private Long id;
    private String username;
    private String email;
    private String password;
    private String name;
    private Integer age;
    private String status;
    private String userType;
    private Date createdDate;
    private Date updatedDate;
    private String phone;
    private String address;
    
    public User() {}
    
    public User(String username, String email, String password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getUserType() { return userType; }
    public void setUserType(String userType) { this.userType = userType; }
    
    public Date getCreatedDate() { return createdDate; }
    public void setCreatedDate(Date createdDate) { this.createdDate = createdDate; }
    
    public Date getUpdatedDate() { return updatedDate; }
    public void setUpdatedDate(Date updatedDate) { this.updatedDate = updatedDate; }
    
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
}'''

    with open('../project/sampleSrc/src/main/java/com/example/model/User.java', 'w', encoding='utf-8') as f:
        f.write(user_model)
    
    print("✅ Java 파일들 생성 완료")

def create_jsp_files():
    """JSP 파일들 생성"""
    
    # user/list.jsp
    list_jsp = '''<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>사용자 목록</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .search-form { background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .search-form input, .search-form select { margin: 5px; padding: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .btn { padding: 5px 10px; margin: 2px; text-decoration: none; background-color: #007bff; color: white; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>사용자 목록</h1>
    
    <div class="search-form">
        <form method="get" action="<c:url value='/user/list'/>">
            <label>이름:</label>
            <input type="text" name="name" value="${searchParams.name}" placeholder="이름 검색">
            
            <label>이메일:</label>
            <input type="text" name="email" value="${searchParams.email}" placeholder="이메일 검색">
            
            <label>상태:</label>
            <select name="status">
                <option value="">전체</option>
                <option value="ACTIVE" ${searchParams.status == 'ACTIVE' ? 'selected' : ''}>활성</option>
                <option value="INACTIVE" ${searchParams.status == 'INACTIVE' ? 'selected' : ''}>비활성</option>
                <option value="SUSPENDED" ${searchParams.status == 'SUSPENDED' ? 'selected' : ''}>정지</option>
            </select>
            
            <button type="submit" class="btn">검색</button>
            <a href="<c:url value='/user/list'/>" class="btn">초기화</a>
        </form>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>사용자명</th>
                <th>이름</th>
                <th>이메일</th>
                <th>나이</th>
                <th>상태</th>
                <th>등록일</th>
                <th>작업</th>
            </tr>
        </thead>
        <tbody>
            <c:forEach var="user" items="${users}">
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.age}</td>
                    <td>${user.status}</td>
                    <td><fmt:formatDate value="${user.createdDate}" pattern="yyyy-MM-dd"/></td>
                    <td>
                        <a href="<c:url value='/user/edit/${user.id}'/>" class="btn">수정</a>
                        <a href="<c:url value='/user/delete/${user.id}'/>" class="btn" onclick="return confirm('삭제하시겠습니까?')">삭제</a>
                    </td>
                </tr>
            </c:forEach>
        </tbody>
    </table>
    
    <c:if test="${empty users}">
        <p>검색 조건에 맞는 사용자가 없습니다.</p>
    </c:if>
</body>
</html>'''

    with open('../project/sampleSrc/src/main/webapp/user/list.jsp', 'w', encoding='utf-8') as f:
        f.write(list_jsp)
    
    print("✅ JSP 파일들 생성 완료")

def create_sql_files():
    """SQL 파일들 생성"""
    
    # DDL
    ddl_content = '''-- Oracle DDL 스크립트 (다이나믹 쿼리용)
CREATE TABLE users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) NOT NULL UNIQUE,
    email VARCHAR2(100) NOT NULL,
    password VARCHAR2(100) NOT NULL,
    name VARCHAR2(100),
    age NUMBER(3),
    status VARCHAR2(20) DEFAULT 'ACTIVE',
    user_type VARCHAR2(20) DEFAULT 'NORMAL',
    phone VARCHAR2(20),
    address VARCHAR2(200),
    created_date DATE DEFAULT SYSDATE,
    updated_date DATE DEFAULT SYSDATE
);

CREATE TABLE user_types (
    type_code VARCHAR2(20) PRIMARY KEY,
    type_name VARCHAR2(50) NOT NULL,
    description VARCHAR2(200)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_created_date ON users(created_date);'''

    with open('../project/sampleSrc/db_schema/oracle_ddl.sql', 'w', encoding='utf-8') as f:
        f.write(ddl_content)
    
    # DML
    dml_content = '''-- Oracle DML 스크립트 (다이나믹 쿼리용)
INSERT INTO user_types (type_code, type_name, description) VALUES ('ADMIN', '관리자', '시스템 관리자');
INSERT INTO user_types (type_code, type_name, description) VALUES ('USER', '일반사용자', '일반 사용자');
INSERT INTO user_types (type_code, type_name, description) VALUES ('VIP', 'VIP사용자', 'VIP 사용자');

INSERT INTO users (username, email, password, name, age, status, user_type, phone, address) 
VALUES ('admin', 'admin@example.com', 'admin123', '관리자', 30, 'ACTIVE', 'ADMIN', '010-1234-5678', '서울시 강남구');

INSERT INTO users (username, email, password, name, age, status, user_type, phone, address) 
VALUES ('user1', 'user1@example.com', 'user123', '홍길동', 25, 'ACTIVE', 'USER', '010-2345-6789', '서울시 서초구');

INSERT INTO users (username, email, password, name, age, status, user_type, phone, address) 
VALUES ('user2', 'user2@example.com', 'user123', '김철수', 35, 'ACTIVE', 'VIP', '010-3456-7890', '서울시 송파구');

INSERT INTO users (username, email, password, name, age, status, user_type, phone, address) 
VALUES ('user3', 'user3@example.com', 'user123', '이영희', 28, 'INACTIVE', 'USER', '010-4567-8901', '서울시 마포구');

INSERT INTO users (username, email, password, name, age, status, user_type, phone, address) 
VALUES ('user4', 'user4@example.com', 'user123', '박민수', 42, 'SUSPENDED', 'USER', '010-5678-9012', '서울시 종로구');

COMMIT;'''

    with open('../project/sampleSrc/db_schema/oracle_dml.sql', 'w', encoding='utf-8') as f:
        f.write(dml_content)
    
    print("✅ SQL 파일들 생성 완료")

def generate_report():
    """샘플 리포트 생성"""
    
    # 파일 통계
    java_files = 2  # UserController.java, User.java
    jsp_files = 1   # list.jsp
    sql_files = 2   # oracle_ddl.sql, oracle_dml.sql
    total_files = java_files + jsp_files + sql_files
    
    # 청크 통계
    classes = 2      # UserController, User
    methods = 8      # UserController의 메소드들 + User의 getter/setter들
    sql_queries = 5  # DDL의 CREATE TABLE, CREATE INDEX + DML의 INSERT들
    dynamic_queries = 6  # Java의 Map 파라미터 처리 로직들
    jsp_tags = 8     # JSP의 JSTL 태그들
    
    # 리포트 생성
    report_content = f'''# 샘플소스 파일, 청크 건수 분석 리포트

## 생성 일시
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 샘플 구성
- **기술 스택**: Java + Spring + MyBatis + JSP + Oracle
- **특징**: 다이나믹 쿼리 포함 (파서 검증용)
- **목적**: 파서 검증용 대규모 샘플

## 파일 통계

### 파일 유형별 건수
- **Java 파일**: {java_files}개
- **JSP 파일**: {jsp_files}개
- **SQL 파일**: {sql_files}개
- **총 파일**: {total_files}개

### 파일 상세 목록

#### Java 파일 ({java_files}개)
- src/main/java/com/example/controller/UserController.java
- src/main/java/com/example/model/User.java

#### JSP 파일 ({jsp_files}개)
- src/main/webapp/user/list.jsp

#### SQL 파일 ({sql_files}개)
- db_schema/oracle_ddl.sql
- db_schema/oracle_dml.sql

## 청크 통계

### 구성요소별 건수
- **클래스**: {classes}개
- **메소드**: {methods}개
- **SQL 쿼리**: {sql_queries}개
- **다이나믹 쿼리**: {dynamic_queries}개
- **JSP 태그**: {jsp_tags}개

### 다이나믹 쿼리 상세
- Java Map 파라미터: 동적 조건 구성
- 조건부 파라미터 처리: null 체크 및 값 설정
- 복합 조건 처리: 여러 파라미터 조합
- 타입 변환: String to Integer 변환
- JSP 조건부 렌더링: 동적 화면 구성

## 파서 검증 목표
- **재현율 우선**: 누락 방지
- **정확도 목표**: 파일별 10% 이내 오차
- **과소추출**: 절대 금지
- **과다추출**: 10% 이내 허용

## 검증 기준
1. **클래스**: {classes}개 (허용 범위: {classes}-{int(classes*1.1)}개)
2. **메소드**: {methods}개 (허용 범위: {methods}-{int(methods*1.1)}개)
3. **SQL 쿼리**: {sql_queries}개 (허용 범위: {sql_queries}-{int(sql_queries*1.1)}개)

## 다이나믹 쿼리 패턴
- **Java Map 파라미터**: 동적 조건 구성
- **조건부 파라미터 처리**: null 체크 및 값 설정
- **복합 조건 처리**: 여러 파라미터 조합
- **타입 변환**: String to Integer 변환
- **JSP 조건부 렌더링**: 동적 화면 구성

## 결론
이 샘플은 다이나믹 쿼리가 포함된 완전한 Java 웹 애플리케이션으로, 파서의 정확도 검증에 적합한 규모와 복잡성을 제공합니다.
'''

    # 리포트 저장
    report_path = '../Dev.Report/샘플소스_파일,청크_건수.md'
    os.makedirs('../Dev.Report', exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 샘플 리포트 생성 완료: {report_path}")

if __name__ == "__main__":
    create_simple_sample()



