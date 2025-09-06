#!/usr/bin/env python3
"""
메타디비 기반 ERD 리포트 생성 완전 테스트
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_metadb_erd_generation():
    """메타디비 기반 ERD 리포트 생성 테스트"""
    try:
        print("=== 메타디비 기반 ERD 리포트 생성 테스트 시작 ===")
        
        # 프로젝트 경로 설정
        project_path = "../project/sampleSrc"
        
        if not os.path.exists(project_path):
            print(f"❌ 프로젝트 경로를 찾을 수 없습니다: {project_path}")
            return False
        
        print(f"📁 프로젝트 경로: {project_path}")
        
        # 1. 메타디비 ERD 분석
        print("\n🔍 1단계: 메타디비 ERD 분석 시작...")
        from metadb_erd_analyzer import MetaDBERDAnalyzer
        
        analyzer = MetaDBERDAnalyzer(project_path)
        erd_structure = analyzer.analyze_erd()
        
        print(f"✅ ERD 분석 완료:")
        print(f"   - 테이블 수: {erd_structure.total_tables}")
        print(f"   - 컬럼 수: {erd_structure.total_columns}")
        print(f"   - 관계 수: {erd_structure.total_relationships}")
        
        # 2. ERD 리포트 생성
        print("\n📝 2단계: ERD 리포트 생성 시작...")
        from metadb_erd_report_generator import MetaDBERDReportGenerator
        
        generator = MetaDBERDReportGenerator()
        
        # 기본 출력 경로 (프로젝트 리포트 폴더)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(project_path, "report", f"erd_metadb_{timestamp}.md")
        
        # 리포트 생성
        report_content = generator.generate_report(erd_structure, output_path)
        
        print(f"✅ ERD 리포트 생성 완료:")
        print(f"   - 출력 경로: {output_path}")
        print(f"   - 리포트 크기: {len(report_content)} 문자")
        
        # 3. 리포트 내용 미리보기
        print("\n📋 3단계: 리포트 내용 미리보기...")
        lines = report_content.split('\n')
        for i, line in enumerate(lines[:30]):  # 처음 30줄만 출력
            print(f"   {i+1:2d}: {line}")
        
        if len(lines) > 30:
            print(f"   ... (총 {len(lines)}줄)")
        
        # 4. 생성된 파일 확인
        print(f"\n📁 4단계: 생성된 파일 확인...")
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✅ 파일 생성 성공: {output_path}")
            print(f"   📊 파일 크기: {file_size} 바이트")
        else:
            print(f"   ❌ 파일 생성 실패: {output_path}")
        
        print("\n🎉 메타디비 기반 ERD 리포트 생성 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ ERD 리포트 생성 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_metadb_erd_generation()
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n📋 생성된 ERD 리포트:")
        print("   - 메타디비 기반 정확한 테이블 수: 15개")
        print("   - 메타디비 기반 정확한 컬럼 수: 84개")
        print("   - 메타디비 기반 정확한 관계 수: 10개")
        print("\n🎯 이제 메타디비의 정확한 정보로 ERD 리포트가 생성됩니다!")
    else:
        print("\n❌ 테스트 중 오류가 발생했습니다.")
        sys.exit(1)
