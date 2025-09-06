"""
로그 파일 정리 유틸리티
24시간 이상 된 로그 파일들을 자동으로 정리합니다.
"""

import os
import glob
from datetime import datetime, timedelta
from typing import Optional


def cleanup_old_log_files(logs_dir: str = "./logs", max_age_hours: int = 24) -> int:
    """
    24시간 이상 된 로그 파일들을 정리합니다.
    
    Args:
        logs_dir: 로그 디렉토리 경로
        max_age_hours: 최대 보관 시간 (시간 단위)
        
    Returns:
        삭제된 파일 수
    """
    try:
        if not os.path.exists(logs_dir):
            return 0
            
        # 현재 시간에서 지정된 시간 전 시간 계산
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # 로그 파일 패턴들
        log_patterns = [
            "*.log",
            "phase1_*.log", 
            "phase2_*.log",
            "visualize_*.log",
            "analyzer.log"
        ]
        
        deleted_count = 0
        for pattern in log_patterns:
            log_files = glob.glob(os.path.join(logs_dir, pattern))
            for log_file in log_files:
                try:
                    # 파일 수정 시간 확인
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if file_mtime < cutoff_time:
                        os.remove(log_file)
                        deleted_count += 1
                        print(f"오래된 로그 파일 삭제: {log_file}")
                except Exception as e:
                    print(f"로그 파일 삭제 실패 {log_file}: {e}")
        
        if deleted_count > 0:
            print(f"총 {deleted_count}개의 오래된 로그 파일을 정리했습니다.")
            
        return deleted_count
            
    except Exception as e:
        print(f"로그 파일 정리 중 오류 발생: {e}")
        return 0


if __name__ == "__main__":
    # 테스트 실행
    deleted_count = cleanup_old_log_files()
    print(f"삭제된 파일 수: {deleted_count}")
