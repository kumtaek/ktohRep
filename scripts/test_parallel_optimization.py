#!/usr/bin/env python3
"""
병렬 처리 최적화 검증 테스트 스크립트
Phase 1 Priority 2: 병렬 처리 성능 검증 및 최적화 테스트
"""

import sys
import os
import asyncio
import pytest
import logging
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.parallel_processor import ParallelProcessor, dummy_java_parser, dummy_jsp_parser, dummy_xml_parser


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_test_files(test_dir: str, file_counts: dict) -> list:
    """테스트용 파일 생성"""
    
    os.makedirs(test_dir, exist_ok=True)
    test_files = []
    
    # Java 파일 생성
    for i in range(file_counts.get('java', 0)):
        file_path = os.path.join(test_dir, f"TestClass{i}.java")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"""
public class TestClass{i} {{
    private String field{i};
    
    public void method{i}() {{
        System.out.println("Test method {i}");
    }}
    
    public String getField{i}() {{
        return field{i};
    }}
    
    public void setField{i}(String value) {{
        this.field{i} = value;
    }}
}}
""")
        test_files.append(file_path)
    
    # JSP 파일 생성
    for i in range(file_counts.get('jsp', 0)):
        file_path = os.path.join(test_dir, f"test{i}.jsp")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"""
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ include file="/WEB-INF/include/header.jsp" %>

<html>
<head>
    <title>Test Page {i}</title>
</head>
<body>
    <% 
        String testData{i} = request.getParameter("data{i}");
        if (testData{i} != null) {{
    %>
        <p>Data {i}: <%= testData{i} %></p>
    <% }} %>
    
    <form method="post" action="test{i}.jsp">
        <input type="text" name="data{i}" placeholder="Enter data {i}"/>
        <input type="submit" value="Submit"/>
    </form>
</body>
</html>
""")
        test_files.append(file_path)
    
    # MyBatis XML 파일 생성
    for i in range(file_counts.get('xml', 0)):
        file_path = os.path.join(test_dir, f"TestMapper{i}.xml")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.test.mapper.TestMapper{i}">
    
    <select id="selectTest{i}" parameterType="String" resultType="TestVO{i}">
        SELECT 
            test_id{i},
            test_name{i},
            test_value{i}
        FROM test_table{i}
        WHERE test_id{i} = #{{testId{i}}}
    </select>
    
    <insert id="insertTest{i}" parameterType="TestVO{i}">
        INSERT INTO test_table{i} (
            test_name{i},
            test_value{i}
        ) VALUES (
            #{{testName{i}}},
            #{{testValue{i}}}
        )
    </insert>
    
    <update id="updateTest{i}" parameterType="TestVO{i}">
        UPDATE test_table{i} SET
            test_name{i} = #{{testName{i}}},
            test_value{i} = #{{testValue{i}}}
        WHERE test_id{i} = #{{testId{i}}}
    </update>
    
    <delete id="deleteTest{i}" parameterType="String">
        DELETE FROM test_table{i}
        WHERE test_id{i} = #{{testId{i}}}
    </delete>
    
</mapper>
""")
        test_files.append(file_path)
    
    return test_files


def cleanup_test_files(test_files: list):
    """테스트 파일 정리"""
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.warning(f"파일 삭제 실패 {file_path}: {e}")
    
    # 빈 디렉토리 제거
    try:
        test_dir = os.path.dirname(test_files[0]) if test_files else None
        if test_dir and os.path.exists(test_dir) and not os.listdir(test_dir):
            os.rmdir(test_dir)
    except Exception:
        pass


@pytest.mark.asyncio
async def test_run_parallel_processing():
    """병렬 처리 검증 테스트 실행"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("병렬 처리 최적화 검증 테스트 시작")
    
    # 테스트 설정
    config = {
        'processing': {
            'max_workers': 4,
            'chunk_size': 512
        }
    }
    
    # 테스트 파일 생성
    test_dir = "./temp_test_files"
    file_counts = {
        'java': 50,
        'jsp': 30,
        'xml': 40
    }
    
    logger.info(f"테스트 파일 생성: {sum(file_counts.values())}개")
    test_files = create_test_files(test_dir, file_counts)
    
    try:
        # 병렬 프로세서 초기화
        processor = ParallelProcessor(config)
        
        # 1. 파서 함수 매핑
        parser_mapping = {
            '.java': dummy_java_parser,
            '.jsp': dummy_jsp_parser, 
            '.xml': dummy_xml_parser
        }
        
        # 2. 병렬 처리 성능 검증
        logger.info("=== 병렬 처리 성능 검증 시작 ===")
        
        # Java 파일만으로 성능 테스트
        java_files = [f for f in test_files if f.endswith('.java')]
        verification_result = await processor.verify_parallel_processing(
            java_files,
            dummy_java_parser,
            max_workers_list=[1, 2, 4, 8]
        )
        
        # 결과 출력
        logger.info("=== 성능 검증 결과 ===")
        logger.info(f"시스템 정보: CPU {verification_result['system_info']['cpu_count']}코어, "
                   f"메모리 {verification_result['system_info']['memory_gb']:.1f}GB")
        logger.info(f"테스트 파일 수: {verification_result['system_info']['test_files_count']}")
        
        logger.info("성능 테스트 결과:")
        for test in verification_result['performance_tests']:
            logger.info(f"  {test['executor_type']} ({test['workers']} workers): "
                       f"{test['processing_time']:.3f}초, "
                       f"성공률: {test['success_count']}/{test['total_files']}, "
                       f"CPU: {test['cpu_usage_avg']:.1f}%, "
                       f"메모리: {test['memory_usage_peak']:.1f}MB")
        
        logger.info(f"최적 구성: {verification_result['optimal_executor']} "
                   f"with {verification_result['optimal_workers']} workers")
        
        logger.info("권장사항:")
        for rec in verification_result['recommendations']:
            logger.info(f"  - {rec}")
        
        # 3. 비동기 처리 최적화 테스트
        logger.info("=== 비동기 처리 최적화 테스트 시작 ===")
        
        optimization_result = processor.optimize_async_processing(
            test_files,
            parser_mapping,
            optimal_workers=verification_result['optimal_workers']
        )
        
        logger.info("=== 최적화 결과 ===")
        logger.info(f"총 파일 수: {optimization_result['total_files']}")
        logger.info(f"총 처리 시간: {optimization_result['total_processing_time']:.3f}초")
        
        logger.info("파일 그룹별 처리 결과:")
        for ext, result in optimization_result['processing_results'].items():
            logger.info(f"  {ext}: {result['files_processed']}개 파일, "
                       f"{result['processing_time']:.3f}초, "
                       f"워커: {result['workers_used']}, "
                       f"배치 크기: {result['batch_size']}")
        
        logger.info("적용된 최적화:")
        for opt in optimization_result['optimization_applied']:
            logger.info(f"  - {opt}")
        
        # 4. 성능 리포트 저장
        report_path = "./reports/parallel_processing_performance.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        combined_results = {
            'verification': verification_result,
            'optimization': optimization_result
        }
        
        processor.save_performance_report(combined_results, report_path)
        logger.info(f"성능 리포트 저장: {report_path}")
        
        # 5. 성능 개선 확인
        logger.info("=== 성능 개선 확인 ===")
        
        # 단일 스레드 vs 최적화된 병렬 처리 비교
        single_thread_time = None
        parallel_time = optimization_result['total_processing_time']
        
        for test in verification_result['performance_tests']:
            if test['workers'] == 1 and test['executor_type'] == 'ThreadPool':
                single_thread_time = test['processing_time']
                break
        
        if single_thread_time:
            speedup = single_thread_time / parallel_time
            logger.info(f"성능 개선: {speedup:.2f}배 향상 "
                       f"(단일: {single_thread_time:.3f}초 → 병렬: {parallel_time:.3f}초)")
        
        logger.info("병렬 처리 최적화 검증 완료!")
        
        return True
        
    except Exception as e:
        logger.error(f"테스트 실행 오류: {e}")
        return False
        
    finally:
        # 테스트 파일 정리
        cleanup_test_files(test_files)
        logger.info("테스트 파일 정리 완료")


if __name__ == "__main__":
    success = asyncio.run(run_parallel_processing_test())
    
    if success:
        print("\n✅ 병렬 처리 최적화 검증 테스트 성공!")
        sys.exit(0)
    else:
        print("\n❌ 병렬 처리 최적화 검증 테스트 실패!")
        sys.exit(1)