#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EdgeGenerator 수정사항 테스트 스크립트
"""

from phase1.models.database import DatabaseManager
import yaml

def test_edge_generator():
    try:
        # 설정 파일 로드
        with open('phase1/config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        db_config = config.get('database', {})
        db_manager = DatabaseManager(db_config)
        db_manager.initialize()

        with db_manager.get_auto_commit_session() as session:
            from phase1.utils.edge_generator import EdgeGenerator
            edge_generator = EdgeGenerator(session, 2, config)  # project_id = 2
            print('✅ EdgeGenerator 초기화 성공')
            print(f'프로젝트 ID: {edge_generator.project_id}')
            
            # 간단한 엣지 생성 테스트
            try:
                edge_generator._create_edge(
                    source_type='class',
                    source_id=1,
                    target_type='class', 
                    target_id=2,
                    edge_type='test',
                    description='테스트 엣지'
                )
                print('✅ 테스트 엣지 생성 성공')
            except Exception as e:
                print(f'❌ 테스트 엣지 생성 실패: {e}')
                
    except Exception as e:
        print(f'❌ 테스트 실패: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_edge_generator()
