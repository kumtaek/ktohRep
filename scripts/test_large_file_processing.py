#!/usr/bin/env python3
"""
대용량 파일 처리 최적화 테스트 스크립트
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.large_file_processor import LargeFileProcessor, sample_processor


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_large_test_file(file_path: str, size_mb: int) -> str:
    """대용량 테스트 파일 생성"""
    
    # JSP/MyBatis 스타일의 테스트 내용 생성
    jsp_content = '''<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<html>
<head>
    <title>Large Test File</title>
</head>
<body>
    <h1>Test Content</h1>
    
    <%
        String testData = "This is a large test file for performance testing";
        for (int i = 0; i < 1000; i++) {
            out.println("<p>Line " + i + ": " + testData + "</p>");
        }
    %>
    
    <script type="text/javascript">
        function testFunction() {
            console.log("Testing large file processing optimization");
        }
    </script>
    
    <c:forEach var="item" items="${testList}">
        <div class="test-item">
            <p>${item.name}</p>
            <p>${item.value}</p>
        </div>
    </c:forEach>
    
</body>
</html>

'''
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.test.mapper.LargeTestMapper">
    
    <select id="selectLargeData" parameterType="String" resultType="TestVO">
        SELECT 
            test_id,
            test_name,
            test_value,
            test_description,
            created_date,
            updated_date
        FROM large_test_table
        WHERE test_status = #{status}
        AND test_category IN 
        <foreach item="category" collection="categories" open="(" separator="," close=")">
            #{category}
        </foreach>
        ORDER BY created_date DESC
    </select>
    
    <insert id="insertLargeData" parameterType="TestVO">
        INSERT INTO large_test_table (
            test_name,
            test_value,
            test_description,
            test_status,
            test_category,
            created_date
        ) VALUES (
            #{testName},
            #{testValue},
            #{testDescription},
            #{testStatus},
            #{testCategory},
            SYSDATE
        )
    </insert>
    
</mapper>

'''
    
    java_content = '''package com.test.large;

import java.util.*;
import java.io.*;
import java.sql.*;
import org.springframework.stereotype.Service;

@Service
public class LargeTestService {
    
    private static final String TEST_QUERY = "SELECT * FROM test_table WHERE id = ?";
    
    public List<TestVO> processLargeData(String category) {
        List<TestVO> results = new ArrayList<>();
        
        // Large data processing simulation
        for (int i = 0; i < 10000; i++) {
            TestVO vo = new TestVO();
            vo.setId(String.valueOf(i));
            vo.setName("Test Name " + i);
            vo.setValue("Test Value " + i);
            vo.setCategory(category);
            results.add(vo);
        }
        
        return results;
    }
    
    public void performDatabaseOperation() throws SQLException {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        
        try {
            conn = getConnection();
            stmt = conn.prepareStatement(TEST_QUERY);
            stmt.setString(1, "test");
            rs = stmt.executeQuery();
            
            while (rs.next()) {
                // Process result set
                String id = rs.getString("id");
                String name = rs.getString("name");
                String value = rs.getString("value");
            }
        } finally {
            if (rs != null) rs.close();
            if (stmt != null) stmt.close();
            if (conn != null) conn.close();
        }
    }
    
    private Connection getConnection() throws SQLException {
        // Database connection logic
        return null;
    }
}

'''
    
    # 파일 타입에 따른 내용 선택
    if file_path.endswith('.jsp'):
        base_content = jsp_content
    elif file_path.endswith('.xml'):
        base_content = xml_content
    else:
        base_content = java_content
    
    # 목표 크기만큼 내용 반복
    content_size = len(base_content.encode('utf-8'))
    target_size = size_mb * 1024 * 1024
    repeat_count = max(1, target_size // content_size)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for i in range(repeat_count):
            # 약간의 변화를 주어 실제 파일과 유사하게
            modified_content = base_content.replace('test', f'test_{i}')
            f.write(modified_content)
            f.write('\n' + '=' * 80 + f' SECTION {i} ' + '=' * 80 + '\n\n')
            
    actual_size = os.path.getsize(file_path)
    logging.info(f"테스트 파일 생성: {file_path} ({actual_size // 1024 // 1024}MB)")
    
    return file_path


def test_large_file_processing():
    """대용량 파일 처리 테스트"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("대용량 파일 처리 최적화 테스트 시작")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp(prefix="large_file_test_")
    test_files = []
    
    try:
        # 다양한 크기의 테스트 파일 생성
        test_file_configs = [
            ('small_test.java', 5),      # 5MB
            ('medium_test.jsp', 25),     # 25MB  
            ('large_test.xml', 60),      # 60MB
            ('huge_test.java', 120)      # 120MB
        ]
        
        logger.info("테스트 파일 생성 중...")
        for filename, size_mb in test_file_configs:
            file_path = os.path.join(temp_dir, filename)
            create_large_test_file(file_path, size_mb)
            test_files.append(file_path)
            
        # 대용량 파일 프로세서 초기화
        processor = LargeFileProcessor()
        
        # 1. 단일 대용량 파일 스트리밍 처리 테스트
        logger.info("=== 단일 대용량 파일 스트리밍 처리 테스트 ===")
        
        large_file = test_files[2]  # 60MB 파일
        logger.info(f"테스트 파일: {large_file} (카테고리: {processor.get_file_category(large_file)})")
        
        # 크기 기반 청크 처리
        result_size = processor.process_large_file_streaming(
            large_file, 
            sample_processor, 
            chunk_method="size"
        )
        
        logger.info(f"크기 기반 청크 처리 결과:")
        logger.info(f"  - 청크 수: {result_size['chunks_processed']}")
        logger.info(f"  - 처리 시간: {result_size['processing_time']:.3f}초")
        logger.info(f"  - 피크 메모리: {result_size['peak_memory_mb']:.1f}MB")
        
        # 라인 기반 청크 처리
        result_lines = processor.process_large_file_streaming(
            large_file,
            sample_processor,
            chunk_method="lines"
        )
        
        logger.info(f"라인 기반 청크 처리 결과:")
        logger.info(f"  - 청크 수: {result_lines['chunks_processed']}")
        logger.info(f"  - 처리 시간: {result_lines['processing_time']:.3f}초")
        logger.info(f"  - 피크 메모리: {result_lines['peak_memory_mb']:.1f}MB")
        
        # 2. 다중 파일 병렬 처리 테스트
        logger.info("=== 다중 대용량 파일 병렬 처리 테스트 ===")
        
        multi_result = processor.process_multiple_large_files(
            test_files,
            sample_processor,
            max_workers=2
        )
        
        stats = multi_result['processing_stats']
        logger.info(f"다중 파일 처리 결과:")
        logger.info(f"  - 총 파일 수: {stats.total_files}")
        logger.info(f"  - 대용량 파일 수: {stats.large_files}")
        logger.info(f"  - 총 크기: {stats.total_size_mb:.1f}MB")
        logger.info(f"  - 처리 시간: {stats.processing_time:.3f}초")
        logger.info(f"  - 처리된 청크 수: {stats.chunks_processed}")
        logger.info(f"  - 피크 메모리: {stats.memory_peak_mb:.1f}MB")
        
        logger.info("파일 분류:")
        for category, count in multi_result['file_categories'].items():
            logger.info(f"  - {category}: {count}개")
            
        logger.info("적용된 최적화:")
        for opt in stats.optimization_applied:
            logger.info(f"  - {opt}")
            
        # 3. 최적화 요약 확인
        logger.info("=== 최적화 요약 ===")
        
        opt_summary = multi_result['optimization_summary']
        
        memory_eff = opt_summary['memory_efficiency']
        logger.info(f"메모리 효율성:")
        logger.info(f"  - 피크 메모리: {memory_eff['peak_memory_mb']:.1f}MB")
        logger.info(f"  - 파일당 메모리: {memory_eff['memory_per_file_mb']:.1f}MB")
        logger.info(f"  - 효율성 등급: {memory_eff['efficiency_rating']}")
        
        proc_eff = opt_summary['processing_efficiency']
        logger.info(f"처리 효율성:")
        logger.info(f"  - 총 처리 시간: {proc_eff['total_time_seconds']:.3f}초")
        logger.info(f"  - MB당 처리 시간: {proc_eff['time_per_mb']:.3f}초/MB")
        logger.info(f"  - 처리된 청크 수: {proc_eff['chunks_processed']}")
        
        if opt_summary['recommendations']:
            logger.info("권장사항:")
            for rec in opt_summary['recommendations']:
                logger.info(f"  - {rec}")
        else:
            logger.info("권장사항: 최적화가 잘 적용되었습니다.")
            
        # 4. 청크 파일 분할 테스트
        logger.info("=== 임시 청크 파일 분할 테스트 ===")
        
        huge_file = test_files[3]  # 120MB 파일
        logger.info(f"청크 분할 대상: {huge_file}")
        
        chunk_files = processor.create_temp_file_chunks(huge_file, chunk_size=10*1024*1024)  # 10MB 청크
        logger.info(f"생성된 청크 파일 수: {len(chunk_files)}")
        
        # 청크 파일 크기 확인
        total_chunk_size = 0
        for chunk_file in chunk_files:
            chunk_size = os.path.getsize(chunk_file)
            total_chunk_size += chunk_size
            logger.info(f"  - {os.path.basename(chunk_file)}: {chunk_size // 1024 // 1024}MB")
            
        original_size = os.path.getsize(huge_file)
        logger.info(f"원본 파일 크기: {original_size // 1024 // 1024}MB")
        logger.info(f"청크 파일 총 크기: {total_chunk_size // 1024 // 1024}MB")
        
        # 청크 파일 정리
        processor.cleanup_temp_files(chunk_files)
        logger.info("임시 청크 파일 정리 완료")
        
        logger.info("대용량 파일 처리 최적화 테스트 성공!")
        return True
        
    except Exception as e:
        logger.error(f"테스트 실행 오류: {e}")
        return False
        
    finally:
        # 테스트 파일 정리
        for file_path in test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"테스트 파일 삭제 실패 {file_path}: {e}")
                
        # 임시 디렉토리 정리
        try:
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"임시 디렉토리 삭제 실패 {temp_dir}: {e}")
            
        logger.info("테스트 파일 정리 완료")


if __name__ == "__main__":
    success = test_large_file_processing()
    
    if success:
        print("\n✓ 대용량 파일 처리 최적화 테스트 성공!")
        sys.exit(0)
    else:
        print("\n✗ 대용량 파일 처리 최적화 테스트 실패!")
        sys.exit(1)