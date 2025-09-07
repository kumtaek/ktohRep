"""
시각적 리포터만 단독 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from core.optimized_metadata_engine import OptimizedMetadataEngine
    from parsers.visual_architecture_reporter import VisualArchitectureReporter
    
    # 기존 메타데이터 엔진 사용
    metadata_engine = OptimizedMetadataEngine(project_path="./project")
    
    # 프로젝트 ID 1번 사용 (이미 존재한다고 가정)
    project_id = 1
    
    # 시각적 리포터 생성
    visual_reporter = VisualArchitectureReporter(metadata_engine)
    
    # 리포트 생성
    visual_report = visual_reporter.generate_visual_report(project_id)
    
    print("시각적 아키텍처 리포트 생성 결과:")
    print("=" * 60)
    print(visual_report[:2000])  # 처음 2000자만 출력
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()