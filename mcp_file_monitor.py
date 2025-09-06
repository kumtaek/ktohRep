#!/usr/bin/env python3
"""
MCP 기반 A 파일 자동 감지 시스템
"""

import json
import time
import os
from pathlib import Path
import asyncio
from typing import List, Optional

class MCPFileMonitor:
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.watch_dir = "./Dev.Report"
        self.watch_patterns = ["A_*.md"]
        self.poll_interval = 30  # 30초마다 체크
        self.last_check_time = 0
        self.known_files = set()
        
    def load_config(self) -> dict:
        """MCP 설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  설정 파일을 찾을 수 없음: {self.config_path}")
            return {}
    
    def scan_for_new_files(self) -> List[str]:
        """새로운 A 파일 스캔"""
        new_files = []
        current_time = time.time()
        
        # Dev.Report 폴더 스캔
        if os.path.exists(self.watch_dir):
            for pattern in self.watch_patterns:
                pattern_path = Path(self.watch_dir) / pattern
                for file_path in Path(self.watch_dir).glob(pattern):
                    if file_path.is_file():
                        file_str = str(file_path)
                        
                        # 새 파일인지 확인
                        if file_str not in self.known_files:
                            new_files.append(file_str)
                            self.known_files.add(file_str)
                            print(f"🎯 새로운 A 파일 감지됨: {file_path.name}")
        
        return new_files
    
    def notify_assistant(self, file_path: str):
        """어시스턴트에게 A 파일 도착 알림"""
        file_name = os.path.basename(file_path)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        
        print("=" * 60)
        print(f"🚨 A 파일 자동 감지 알림!")
        print(f"📁 파일명: {file_name}")
        print(f"📂 경로: {file_path}")
        print(f"⏰ 감지 시간: {current_time}")
        print(f"🔍 패턴: {', '.join(self.watch_patterns)}")
        print("=" * 60)
        
        # 어시스턴트가 즉시 확인할 수 있도록 강조
        print(f"💡 어시스턴트: {file_name} 파일이 도착했습니다!")
        print(f"💡 즉시 확인하여 작업을 진행하세요!")
        print("=" * 60)
    
    async def start_monitoring(self):
        """파일 모니터링 시작"""
        config = self.load_config()
        if config.get('monitoring', {}).get('pollInterval'):
            self.poll_interval = config['monitoring']['pollInterval'] // 1000
        
        print("🚀 MCP 기반 A 파일 모니터링 시작...")
        print(f"📁 감시 폴더: {self.watch_dir}")
        print(f"🔍 감시 패턴: {', '.join(self.watch_patterns)}")
        print(f"⏱️  체크 간격: {self.poll_interval}초")
        print("⏹️  중지하려면 Ctrl+C")
        print("-" * 50)
        
        # 초기 파일 목록 스캔
        self.known_files = set()
        initial_files = self.scan_for_new_files()
        if initial_files:
            print(f"📋 초기 A 파일 {len(initial_files)}개 발견")
            for file_path in initial_files:
                self.notify_assistant(file_path)
        
        try:
            while True:
                # 새로운 파일 스캔
                new_files = self.scan_for_new_files()
                
                # 새 파일이 있으면 어시스턴트에게 알림
                for file_path in new_files:
                    self.notify_assistant(file_path)
                
                # 대기
                await asyncio.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  모니터링 중지됨")
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")

def main():
    """메인 함수"""
    monitor = MCPFileMonitor()
    
    try:
        asyncio.run(monitor.start_monitoring())
    except Exception as e:
        print(f"❌ 프로그램 실행 오류: {e}")

if __name__ == "__main__":
    main()
