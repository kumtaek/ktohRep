#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 ERD 생성 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    if len(sys.argv) < 2:
        print("사용법: python generate_enhanced_erd.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    try:
        from visualize.builders.erd_enhanced import build_enhanced_erd_json
        from visualize.renderers.enhanced_renderer_factory import EnhancedVisualizationFactory
        import yaml
        import json
        import shutil

        print('모듈 로딩 완료')

        # 설정 로드
        config_path = Path('config/config.yaml')
        config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = f.read().replace('{project_name}', project_name)
                config = yaml.safe_load(raw) or {}
            print('설정 파일 로드 완료')
        else:
            print('기본 설정 사용')

        # ERD 데이터 생성
        print('ERD 데이터 생성 중...')
        data = build_enhanced_erd_json(config, 1, project_name)
        print(f'노드 {len(data.get("nodes", []))}개, 엣지 {len(data.get("edges", []))}개 생성')

        # 향상된 렌더러로 HTML 생성
        print('향상된 HTML 렌더링 중...')
        factory = EnhancedVisualizationFactory()
        html = factory.create_enhanced_erd(data)
        print('HTML 생성 완료')

        # 출력 디렉토리 준비
        output_dir = Path(f'output/{project_name}/visualize')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Static 파일 복사
        visualize_static = Path('visualize/static')
        if visualize_static.exists():
            target_static = output_dir / 'static'
            if target_static.exists():
                shutil.rmtree(target_static)
            shutil.copytree(visualize_static, target_static)
            print('Static 파일 복사 완료')

        # HTML 파일 저장
        enhanced_path = output_dir / 'erd_enhanced.html'
        with open(enhanced_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f'✅ 향상된 ERD 저장: {enhanced_path}')
        return 0

    except ImportError as e:
        print(f'모듈 임포트 오류: {e}')
        print('기본 ERD를 사용합니다.')
        return 1
    except Exception as e:
        print(f'향상된 ERD 생성 오류: {e}')
        print('기본 ERD를 사용합니다.')
        return 1

if __name__ == '__main__':
    sys.exit(main())