#!/usr/bin/env python3
"""
CSV 파일 처리 디버깅 스크립트
"""

import sys
import os
sys.path.append('.')

from pathlib import Path
from phase1.main import SourceAnalyzer

async def debug_csv_processing():
    """CSV 파일 처리 디버깅"""
    
    # SourceAnalyzer 인스턴스 생성
    analyzer = SourceAnalyzer()
    
    # CSV 파일 경로
    csv_file = "project/sampleSrc/db_schema/ALL_TABLES.csv"
    
    print(f"CSV 파일 존재 확인: {os.path.exists(csv_file)}")
    
    # 파일 확장자 확인
    file_ext = Path(csv_file).suffix.lower()
    print(f"파일 확장자: {file_ext}")
    
    # 파서 선택 테스트
    parser = analyzer._select_parser_for_file(csv_file, 'csv')
    print(f"선택된 파서: {parser}")
    
    # CSV 파일 그룹핑 테스트
    file_groups = analyzer._group_files_by_type([csv_file])
    print(f"파일 그룹핑 결과: {file_groups}")
    
    # CSV 메타데이터 저장 테스트
    try:
        # 프로젝트 생성
        project_id = await analyzer.metadata_engine.create_project("project/sampleSrc", "sampleSrc")
        print(f"프로젝트 ID: {project_id}")
        
        # 파일 정보 저장
        file_id = await analyzer._save_file_info(csv_file, project_id)
        print(f"파일 ID: {file_id}")
        
        # CSV 메타데이터 저장
        await analyzer._save_csv_metadata(file_id, csv_file, project_id)
        print("CSV 메타데이터 저장 완료")
        
    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_csv_processing())


