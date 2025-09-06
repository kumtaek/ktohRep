#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
다이나믹 쿼리가 포함된 JSP, Java, MyBatis 샘플 생성 (수정된 버전)
- 재사용성을 위해 명확한 폴더명/파일명 사용
- Oracle + Spring + MyBatis + JSP + 다이나믹 쿼리 포함
"""

import os
import shutil
from datetime import datetime

def create_dynamic_sample():
    """다이나믹 쿼리 샘플 생성 (메인 함수)"""
    
    print("=== 다이나믹 쿼리 샘플 생성 (수정된 버전) ===")
    print("목적: 파서 검증용 대규모 샘플 (Oracle + Spring + MyBatis + JSP + 다이나믹 쿼리)")
    
    # 1. 기존 샘플 백업
    backup_existing_sample()
    
    # 2. 샘플 디렉토리 구조 생성
    create_sample_structure()
    
    # 3. Java 파일들 생성 (다이나믹 쿼리 포함)
    create_java_files()
    
    # 4. MyBatis XML 파일들 생성 (다이나믹 쿼리 포함)
    create_mybatis_files()
    
    # 5. JSP 파일들 생성 (다이나믹 쿼리 포함)
    create_jsp_files()
    
    # 6. Oracle DB Schema 생성
    create_oracle_schema()
    
    # 7. 파일/청크 건수 집계 및 리포트 생성
    generate_sample_report()

def backup_existing_sample():
    """기존 샘플 백업 (재사용 가능한 백업 함수)"""
    
    source_dir = '../project/sampleSrc'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f'../project/sampleSrc_backup_{timestamp}'
    
    if os.path.exists(source_dir):
        shutil.copytree(source_dir, backup_dir)
        print(f"✅ 기존 샘플 백업 완료: {backup_dir}")
    
    # 기존 샘플 제거
    if os.path.exists(source_dir):
        shutil.rmtree(source_dir)
        print("✅ 기존 샘플 제거 완료")

def create_sample_structure():
    """샘플 디렉토리 구조 생성 (표준 Maven 구조)"""
    
    directories = [
        '../project/sampleSrc/src/main/java/com/example',
        '../project/sampleSrc/src/main/java/com/example/controller',
        '../project/sampleSrc/src/main/java/com/example/service',
        '../project/sampleSrc/src/main/java/com/example/mapper',
        '../project/sampleSrc/src/main/java/com/example/model',
        '../project/sampleSrc/src/main/resources/mybatis/mapper',
        '../project/sampleSrc/src/main/webapp',
        '../project/sampleSrc/src/main/webapp/user',
        '../project/sampleSrc/db_schema'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 샘플 디렉토리 구조 생성 완료 (표준 Maven 구조)")

def create_java_files():
    """Java 파일들 생성 (다이나믹 쿼리 로직 포함)"""
    
    # UserController.java - 다이나믹 쿼리 파라미터 처리
    user_controller = '''package com.example.controller;

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
 * 파서 검증용: 복잡한 조건부 쿼리 로직 포함
 */
@Controller
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    /**
     * 조건부 사용자 목록 조회 (다이나믹 쿼리)
     * 파서 검증용: Map 파라미터로 동적 조건 구성
     */
    @GetMapping("/list")
    public String getUserList(@RequestParam(required = false) String name,
                             @RequestParam(required = false) String email,
                             @RequestParam(required = false) String status,
                             Model model) {
        
        // 다이나믹 쿼리 파라미터 구성
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
    
    /**
     * 고급 조건부 사용자 검색 (복잡한 다이나믹 쿼리)
     * 파서 검증용: 복합 조건 및 날짜 범위 검색
     */
    @PostMapping("/search")
    public String searchUsers(@RequestParam Map<String, String> searchParams, Model model) {
        
        // 복잡한 다이나믹 쿼리 조건 구성
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
        
        // 날짜 범위 검색
        if (searchParams.get("startDate") != null && !searchParams.get("startDate").isEmpty()) {
            params.put("startDate", searchParams.get("startDate"));
        }
        
        if (searchParams.get("endDate") != null && !searchParams.get("endDate").isEmpty()) {
            params.put("endDate", searchParams.get("endDate"));
        }
        
        List<User> users = userService.getUsersByAdvancedCondition(params);
        model.addAttribute("users", users);
        model.addAttribute("searchParams", searchParams);
        
        return "user/searchResult";
    }
    
    /**
     * 타입별 사용자 조회 (동적 타입 처리)
     * 파서 검증용: PathVariable을 이용한 동적 쿼리
     */
    @GetMapping("/dynamic/{type}")
    public String getUsersByType(@PathVariable String type, Model model) {
        
        // 타입별 다이나믹 쿼리
        List<User> users = userService.getUsersByType(type);
        model.addAttribute("users", users);
        model.addAttribute("userType", type);
        
        return "user/typeList";
    }
}'''

    # 파일 저장
    controller_path = '../project/sampleSrc/src/main/java/com/example/controller/UserController.java'
    with open(controller_path, 'w', encoding='utf-8') as f:
        f.write(user_controller)
    
    # UserService.java - 서비스 인터페이스
    user_service = '''package com.example.service;

import com.example.model.User;
import java.util.List;
import java.util.Map;

/**
 * 사용자 서비스 인터페이스 - 다이나믹 쿼리 메소드 정의
 * 파서 검증용: 다양한 조건부 쿼리 메소드 포함
 */
public interface UserService {
    
    /**
     * 기본 조건부 사용자 조회
     */
    List<User> getUsersByCondition(Map<String, Object> params);
    
    /**
     * 고급 조건부 사용자 조회 (복합 조건)
     */
    List<User> getUsersByAdvancedCondition(Map<String, Object> params);
    
    /**
     * 타입별 사용자 조회
     */
    List<User> getUsersByType(String type);
    
    /**
     * ID로 사용자 조회
     */
    User getUserById(Long id);
    
    /**
     * 동적 사용자 업데이트
     */
    int updateUserDynamic(User user);
    
    /**
     * 조건부 사용자 삭제
     */
    int deleteUsersByCondition(Map<String, Object> params);
}'''

    service_path = '../project/sampleSrc/src/main/java/com/example/service/UserService.java'
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(user_service)
    
    # User.java - 모델 클래스
    user_model = '''package com.example.model;

import java.util.Date;

/**
 * 사용자 모델 클래스 - 다이나믹 쿼리용 필드 포함
 * 파서 검증용: 다양한 데이터 타입 및 필드 포함
 */
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
    
    // Constructors
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

    model_path = '../project/sampleSrc/src/main/java/com/example/model/User.java'
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(user_model)
    
    print("✅ Java 파일들 생성 완료 (다이나믹 쿼리 로직 포함)")

def create_mybatis_files():
    """MyBatis XML 파일들 생성 (다이나믹 쿼리 태그 포함)"""
    
    # UserMapper.xml - 다이나믹 쿼리 태그들 포함
    user_mapper_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" 
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<!-- 
    MyBatis 매퍼 XML - 다이나믹 쿼리 태그 포함
    파서 검증용: <if>, <where>, <set>, <foreach> 태그 사용
-->
<mapper namespace="com.example.mapper.UserMapper">
    
    <!-- 기본 사용자 조회 -->
    <select id="selectUserById" parameterType="long" resultType="com.example.model.User">
        SELECT * FROM users WHERE id = #{id}
    </select>
    
    <!-- 조건부 사용자 조회 (다이나믹 쿼리) -->
    <select id="selectUsersByCondition" parameterType="map" resultType="com.example.model.User">
        SELECT * FROM users
        <where>
            <if test="name != null and name != ''">
                AND name LIKE #{name}
            </if>
            <if test="email != null and email != ''">
                AND email LIKE #{email}
            </if>
            <if test="status != null and status != ''">
                AND status = #{status}
            </if>
        </where>
        ORDER BY created_date DESC
    </select>
    
    <!-- 고급 조건부 사용자 조회 (복잡한 다이나믹 쿼리) -->
    <select id="selectUsersByAdvancedCondition" parameterType="map" resultType="com.example.model.User">
        SELECT u.*, ut.type_name
        FROM users u
        LEFT JOIN user_types ut ON u.user_type = ut.type_code
        <where>
            <if test="userType != null and userType != ''">
                AND u.user_type = #{userType}
            </if>
            <if test="minAge != null">
                AND u.age >= #{minAge}
            </if>
            <if test="maxAge != null">
                AND u.age &lt;= #{maxAge}
            </if>
            <if test="startDate != null and startDate != ''">
                AND u.created_date >= TO_DATE(#{startDate}, 'YYYY-MM-DD')
            </if>
            <if test="endDate != null and endDate != ''">
                AND u.created_date &lt;= TO_DATE(#{endDate}, 'YYYY-MM-DD')
            </if>
            <if test="statusList != null and statusList.size() > 0">
                AND u.status IN
                <foreach collection="statusList" item="status" open="(" separator="," close=")">
                    #{status}
                </foreach>
            </if>
        </where>
        ORDER BY u.created_date DESC
    </select>
    
    <!-- 타입별 사용자 조회 -->
    <select id="selectUsersByType" parameterType="string" resultType="com.example.model.User">
        SELECT * FROM users 
        WHERE user_type = #{type}
        ORDER BY name
    </select>
    
    <!-- 동적 사용자 업데이트 -->
    <update id="updateUserDynamic" parameterType="com.example.model.User">
        UPDATE users
        <set>
            <if test="username != null and username != ''">
                username = #{username},
            </if>
            <if test="email != null and email != ''">
                email = #{email},
            </if>
            <if test="name != null and name != ''">
                name = #{name},
            </if>
            <if test="age != null">
                age = #{age},
            </if>
            <if test="status != null and status != ''">
                status = #{status},
            </if>
            <if test="phone != null and phone != ''">
                phone = #{phone},
            </if>
            <if test="address != null and address != ''">
                address = #{address},
            </if>
            updated_date = SYSDATE
        </set>
        WHERE id = #{id}
    </update>
    
    <!-- 동적 사용자 삽입 -->
    <insert id="insertUserDynamic" parameterType="com.example.model.User" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (
            <trim suffixOverrides=",">
                <if test="username != null and username != ''">username,</if>
                <if test="email != null and email != ''">email,</if>
                <if test="password != null and password != ''">password,</if>
                <if test="name != null and name != ''">name,</if>
                <if test="age != null">age,</if>
                <if test="status != null and status != ''">status,</if>
                <if test="userType != null and userType != ''">user_type,</if>
                <if test="phone != null and phone != ''">phone,</if>
                <if test="address != null and address != ''">address,</if>
                created_date,
                updated_date
            </trim>
        ) VALUES (
            <trim suffixOverrides=",">
                <if test="username != null and username != ''">#{username},</if>
                <if test="email != null and email != ''">#{email},</if>
                <if test="password != null and password != ''">#{password},</if>
                <if test="name != null and name != ''">#{name},</if>
                <if test="age != null">#{age},</if>
                <if test="status != null and status != ''">#{status},</if>
                <if test="userType != null and userType != ''">#{userType},</if>
                <if test="phone != null and phone != ''">#{phone},</if>
                <if test="address != null and address != ''">#{address},</if>
                SYSDATE,
                SYSDATE
            </trim>
        )
    </insert>
    
    <!-- 조건부 사용자 삭제 -->
    <delete id="deleteUsersByCondition" parameterType="map">
        DELETE FROM users
        <where>
            <if test="status != null and status != ''">
                AND status = #{status}
            </if>
            <if test="userType != null and userType != ''">
                AND user_type = #{userType}
            </if>
            <if test="beforeDate != null and beforeDate != ''">
                AND created_date &lt; TO_DATE(#{beforeDate}, 'YYYY-MM-DD')
            </if>
        </where>
    </delete>
    
</mapper>'''

    mapper_path = '../project/sampleSrc/src/main/resources/mybatis/mapper/UserMapper.xml'
    with open(mapper_path, 'w', encoding='utf-8') as f:
        f.write(user_mapper_xml)
    
    print("✅ MyBatis XML 파일들 생성 완료 (다이나믹 쿼리 태그 포함)")

def create_jsp_files():
    """JSP 파일들 생성 (다이나믹 쿼리 UI 포함)"""
    
    # JSP 디렉토리 생성
    jsp_user_dir = '../project/sampleSrc/src/main/webapp/user'
    os.makedirs(jsp_user_dir, exist_ok=True)
    
    # user/list.jsp - 다이나믹 검색 폼 포함
    user_list_jsp = '''<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>사용자 목록 - 다이나믹 쿼리 검색</title>
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
    <h1>사용자 목록 (다이나믹 쿼리 검색)</h1>
    
    <!-- 다이나믹 검색 폼 -->
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

    # JSP 파일 저장
    list_jsp_path = os.path.join(jsp_user_dir, 'list.jsp')
    with open(list_jsp_path, 'w', encoding='utf-8') as f:
        f.write(user_list_jsp)
    
    print("✅ JSP 파일들 생성 완료 (다이나믹 쿼리 UI 포함)")

def create_oracle_schema():
    """Oracle DB Schema 생성 (다이나믹 쿼리용 테이블)"""
    
    # DDL - 다이나믹 쿼리용 테이블 구조
    ddl_content = '''-- Oracle DDL 스크립트 (다이나믹 쿼리용)
-- 파서 검증용: 다양한 조건부 쿼리를 위한 테이블 구조

-- 사용자 테이블
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

-- 사용자 타입 테이블
CREATE TABLE user_types (
    type_code VARCHAR2(20) PRIMARY KEY,
    type_name VARCHAR2(50) NOT NULL,
    description VARCHAR2(200)
);

-- 인덱스 생성 (다이나믹 쿼리 성능 최적화)
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_created_date ON users(created_date);

-- 시퀀스 생성
CREATE SEQUENCE user_seq START WITH 1 INCREMENT BY 1;'''

    ddl_path = '../project/sampleSrc/db_schema/oracle_ddl.sql'
    with open(ddl_path, 'w', encoding='utf-8') as f:
        f.write(ddl_content)
    
    # DML - 다이나믹 쿼리용 샘플 데이터
    dml_content = '''-- Oracle DML 스크립트 (다이나믹 쿼리용)
-- 파서 검증용: 다양한 조건부 쿼리를 위한 샘플 데이터

-- 사용자 타입 데이터
INSERT INTO user_types (type_code, type_name, description) VALUES ('ADMIN', '관리자', '시스템 관리자');
INSERT INTO user_types (type_code, type_name, description) VALUES ('USER', '일반사용자', '일반 사용자');
INSERT INTO user_types (type_code, type_name, description) VALUES ('VIP', 'VIP사용자', 'VIP 사용자');

-- 사용자 데이터 (다양한 조건 테스트용)
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

    dml_path = '../project/sampleSrc/db_schema/oracle_dml.sql'
    with open(dml_path, 'w', encoding='utf-8') as f:
        f.write(dml_content)
    
    print("✅ Oracle DB Schema 생성 완료 (다이나믹 쿼리용 테이블)")

def generate_sample_report():
    """샘플 리포트 생성 (파일/청크 건수 집계)"""
    
    print("\n=== 샘플 리포트 생성 ===")
    
    # 파일 및 청크 건수 집계
    stats = analyze_sample_files()
    
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
- **Java 파일**: {stats['java_files']}개
- **XML 파일**: {stats['xml_files']}개  
- **JSP 파일**: {stats['jsp_files']}개
- **SQL 파일**: {stats['sql_files']}개
- **총 파일**: {stats['total_files']}개

### 파일 상세 목록

#### Java 파일 ({stats['java_files']}개)
{format_file_list(stats['java_file_list'])}

#### XML 파일 ({stats['xml_files']}개)
{format_file_list(stats['xml_file_list'])}

#### JSP 파일 ({stats['jsp_files']}개)
{format_file_list(stats['jsp_file_list'])}

#### SQL 파일 ({stats['sql_files']}개)
{format_file_list(stats['sql_file_list'])}

## 청크 통계

### 구성요소별 건수
- **클래스**: {stats['classes']}개
- **메소드**: {stats['methods']}개
- **SQL 쿼리**: {stats['sql_queries']}개
- **다이나믹 쿼리**: {stats['dynamic_queries']}개
- **JSP 태그**: {stats['jsp_tags']}개

### 다이나믹 쿼리 상세
{format_dynamic_queries(stats['dynamic_query_details'])}

## 파서 검증 목표
- **재현율 우선**: 누락 방지
- **정확도 목표**: 파일별 10% 이내 오차
- **과소추출**: 절대 금지
- **과다추출**: 10% 이내 허용

## 검증 기준
1. **클래스**: {stats['classes']}개 (허용 범위: {stats['classes']}-{int(stats['classes']*1.1)}개)
2. **메소드**: {stats['methods']}개 (허용 범위: {stats['methods']}-{int(stats['methods']*1.1)}개)
3. **SQL 쿼리**: {stats['sql_queries']}개 (허용 범위: {stats['sql_queries']}-{int(stats['sql_queries']*1.1)}개)

## 다이나믹 쿼리 패턴
- **MyBatis <if> 태그**: 조건부 쿼리
- **MyBatis <where> 태그**: 동적 WHERE 절
- **MyBatis <set> 태그**: 동적 UPDATE 절
- **MyBatis <foreach> 태그**: 반복 쿼리
- **Java Map 파라미터**: 동적 조건 구성
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

def analyze_sample_files():
    """샘플 파일 분석 (재사용 가능한 분석 함수)"""
    
    sample_dir = '../project/sampleSrc'
    stats = {
        'java_files': 0,
        'xml_files': 0,
        'jsp_files': 0,
        'sql_files': 0,
        'total_files': 0,
        'java_file_list': [],
        'xml_file_list': [],
        'jsp_file_list': [],
        'sql_file_list': [],
        'classes': 0,
        'methods': 0,
        'sql_queries': 0,
        'dynamic_queries': 0,
        'jsp_tags': 0,
        'dynamic_query_details': []
    }
    
    # 파일 분석
    for root, dirs, files in os.walk(sample_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, sample_dir)
            
            if file.endswith('.java'):
                stats['java_files'] += 1
                stats['java_file_list'].append(relative_path)
                # 간단한 클래스/메소드 카운트
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['classes'] += content.count('class ')
                    stats['methods'] += content.count('public ') + content.count('private ') + content.count('protected ')
                    
            elif file.endswith('.xml'):
                stats['xml_files'] += 1
                stats['xml_file_list'].append(relative_path)
                # SQL 쿼리 카운트
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['sql_queries'] += content.count('<select') + content.count('<insert') + content.count('<update') + content.count('<delete')
                    stats['dynamic_queries'] += content.count('<if') + content.count('<where') + content.count('<set') + content.count('<foreach')
                    
            elif file.endswith('.jsp'):
                stats['jsp_files'] += 1
                stats['jsp_file_list'].append(relative_path)
                # JSP 태그 카운트
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['jsp_tags'] += content.count('<c:') + content.count('<fmt:')
                    
            elif file.endswith('.sql'):
                stats['sql_files'] += 1
                stats['sql_file_list'].append(relative_path)
    
    stats['total_files'] = stats['java_files'] + stats['xml_files'] + stats['jsp_files'] + stats['sql_files']
    
    # 다이나믹 쿼리 상세
    stats['dynamic_query_details'] = [
        "MyBatis <if> 태그: 조건부 쿼리 구성",
        "MyBatis <where> 태그: 동적 WHERE 절",
        "MyBatis <set> 태그: 동적 UPDATE 절", 
        "MyBatis <foreach> 태그: 반복 쿼리",
        "Java Map 파라미터: 동적 조건 구성",
        "JSP 조건부 렌더링: 동적 화면 구성"
    ]
    
    return stats

def format_file_list(file_list):
    """파일 목록 포맷팅 (재사용 가능한 유틸리티 함수)"""
    if not file_list:
        return "- 없음"
    
    formatted = []
    for file in file_list:
        formatted.append(f"- {file}")
    return "\n".join(formatted)

def format_dynamic_queries(details):
    """다이나믹 쿼리 상세 포맷팅 (재사용 가능한 유틸리티 함수)"""
    formatted = []
    for detail in details:
        formatted.append(f"- {detail}")
    return "\n".join(formatted)

if __name__ == "__main__":
    create_dynamic_sample()



