#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERD 생성 기능 직접 테스트 스크립트
visualize 폴더에서 직접 실행하여 ERD가 제대로 생성되는지 테스트합니다.
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_erd_generation():
    """ERD 생성 기능을 테스트합니다."""
    try:
        print("🔍 ERD 생성 기능 테스트 시작")
        print("=" * 60)
        
        # 설정 파일 로드 (visualize 전용 config 사용)
        config_path = Path("config/config.yaml")
        if not config_path.exists():
            print(f"❌ visualize 설정 파일을 찾을 수 없습니다: {config_path}")
            return False
        
        print(f"✅ visualize 설정 파일 발견: {config_path}")
        
        # ERD 빌더 임포트
        try:
            from builders.erd import build_erd_json
            print("✅ ERD 빌더 모듈 임포트 성공")
        except ImportError as e:
            print(f"❌ ERD 빌더 모듈 임포트 실패: {e}")
            return False
        
        # 데이터 접근 모듈 임포트
        try:
            from data_access import VizDB
            print("✅ 데이터 접근 모듈 임포트 성공")
        except ImportError as e:
            print(f"❌ 데이터 접근 모듈 임포트 실패: {e}")
            return False
        
        # 설정 로드
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ 설정 로드 성공")
        
        # 프로젝트 정보
        project_name = "sampleSrc"
        project_id = 1  # sampleSrc 프로젝트 ID
        
        print(f"📋 프로젝트 정보:")
        print(f"  - 이름: {project_name}")
        print(f"  - ID: {project_id}")
        
        # VizDB 인스턴스 생성
        try:
            print(f"  🔧 설정 내용: {config}")
            viz_db = VizDB(config, project_name)
            print("✅ VizDB 인스턴스 생성 성공")
        except Exception as e:
            print(f"❌ VizDB 인스턴스 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 데이터 조회 테스트
        print(f"\n🔍 데이터 조회 테스트:")
        
        try:
            # 테이블 정보 조회
            tables = viz_db.fetch_tables()
            print(f"  ✅ 테이블 조회: {len(tables)}개")
            
            # 컬럼 정보 조회
            columns = viz_db.fetch_columns()
            print(f"  ✅ 컬럼 조회: {len(columns)}개")
            
            # 기본키 정보 조회
            pks = viz_db.fetch_pk()
            print(f"  ✅ 기본키 조회: {len(pks)}개")
            
            # 조인 정보 조회
            joins = viz_db.fetch_joins_for_project(project_id)
            print(f"  ✅ 조인 조회: {len(joins)}개")
            
        except Exception as e:
            print(f"  ❌ 데이터 조회 실패: {e}")
            return False
        
        # ERD JSON 생성 테스트
        print(f"\n🚀 ERD JSON 생성 테스트:")
        
        try:
            erd_json = build_erd_json(
                config=config,
                project_id=project_id,
                project_name=project_name
            )
            
            if erd_json:
                print("  ✅ ERD JSON 생성 성공!")
                
                # 생성된 데이터 구조 확인
                if 'nodes' in erd_json:
                    print(f"    📊 노드 수: {len(erd_json['nodes'])}개")
                if 'edges' in erd_json:
                    print(f"    🔗 엣지 수: {len(erd_json['edges'])}개")
                
                # 샘플 노드 데이터 확인
                if 'nodes' in erd_json and erd_json['nodes']:
                    sample_node = list(erd_json['nodes'].values())[0]
                    print(f"    📝 샘플 노드 구조:")
                    for key, value in sample_node.items():
                        if isinstance(value, dict) and len(str(value)) > 100:
                            print(f"      - {key}: {type(value).__name__} (내용 생략)")
                        else:
                            print(f"      - {key}: {value}")
                
                return True
            else:
                print("  ❌ ERD JSON 생성 실패: 빈 결과")
                return False
                
        except Exception as e:
            print(f"  ❌ ERD JSON 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ ERD 생성 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 ERD 생성 기능 테스트 (직접 실행)")
    print("=" * 60)
    
    # ERD 생성 테스트
    success = test_erd_generation()
    
    print(f"\n" + "=" * 60)
    if success:
        print("✅ ERD 생성 기능 테스트 성공!")
        print("🎉 ERD가 제대로 생성됩니다!")
    else:
        print("❌ ERD 생성 기능 테스트 실패")
        print("🔧 문제를 해결해야 합니다.")
    print("=" * 60)

if __name__ == "__main__":
    main()
