#!/usr/bin/env python3
"""
Cursor API를 활용한 자동 메시지 전송 시스템
A 파일 감지 시 채팅창에 자동으로 메시지 전송
"""

import json
import time
import os
import requests
import asyncio
from pathlib import Path
from typing import List, Optional
import pyautogui
import pyperclip

class CursorAutoMessenger:
    def __init__(self, config_path: str = "cursor_api_config.json"):
        self.config_path = config_path
        self.watch_dir = "./Dev.Report"
        self.watch_patterns = ["A_*.md"]
        self.poll_interval = 30  # 30초마다 체크
        self.known_files = set()
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  설정 파일을 찾을 수 없음: {self.config_path}")
            return {}
    
    def scan_for_new_files(self) -> List[str]:
        """새로운 A 파일 스캔"""
        new_files = []
        
        if os.path.exists(self.watch_dir):
            for pattern in self.watch_patterns:
                for file_path in Path(self.watch_dir).glob(pattern):
                    if file_path.is_file():
                        file_str = str(file_path)
                        
                        if file_str not in self.known_files:
                            new_files.append(file_str)
                            self.known_files.add(file_str)
                            print(f"🎯 새로운 A 파일 감지됨: {file_path.name}")
        
        return new_files
    
    def send_cursor_api_message(self, filename: str) -> bool:
        """Cursor API를 통해 메시지 전송 (API 방식)"""
        try:
            if not self.config.get('cursor_api'):
                print("⚠️  Cursor API 설정이 없습니다.")
                return False
            
            api_config = self.config['cursor_api']
            message_template = self.config['auto_message']['template']
            message = message_template.format(filename=filename)
            
            payload = {
                "message": message,
                "type": "auto_notification",
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            response = requests.post(
                f"{api_config['base_url']}{api_config['endpoints']['message']}",
                headers=api_config['headers'],
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Cursor API 메시지 전송 성공: {filename}")
                return True
            else:
                print(f"❌ Cursor API 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Cursor API 메시지 전송 오류: {e}")
            return False
    
    def send_clipboard_message(self, filename: str) -> bool:
        """클립보드를 통한 메시지 전송 (폴백 방식)"""
        try:
            message_template = self.config.get('auto_message', {}).get('template', 
                "🚨 A 파일 자동 감지: {filename}이 도착했습니다! 즉시 확인하여 작업을 진행하세요.")
            message = message_template.format(filename=filename)
            
            # 클립보드에 메시지 복사
            pyperclip.copy(message)
            print(f"📋 클립보드에 메시지 복사됨: {message}")
            
            # 사용자에게 알림
            print("💡 클립보드에 메시지가 복사되었습니다!")
            print("💡 Cursor 채팅창에서 Ctrl+V로 붙여넣기하세요!")
            
            return True
            
        except Exception as e:
            print(f"❌ 클립보드 메시지 전송 오류: {e}")
            return False
    
    def send_auto_message(self, filename: str) -> bool:
        """자동 메시지 전송 (API 우선, 클립보드 폴백)"""
        print(f"🚨 A 파일 자동 감지: {filename}")
        
        # 1. Cursor API 시도
        if self.send_cursor_api_message(filename):
            return True
        
        # 2. 클립보드 폴백
        print("🔄 Cursor API 실패, 클립보드 방식으로 전환...")
        return self.send_clipboard_message(filename)
    
    async def start_monitoring(self):
        """파일 모니터링 및 자동 메시지 전송 시작"""
        print("🚀 Cursor 자동 메시지 시스템 시작...")
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
                filename = os.path.basename(file_path)
                self.send_auto_message(filename)
        
        try:
            while True:
                # 새로운 파일 스캔
                new_files = self.scan_for_new_files()
                
                # 새 파일이 있으면 자동 메시지 전송
                for file_path in new_files:
                    filename = os.path.basename(file_path)
                    self.send_auto_message(filename)
                
                # 대기
                await asyncio.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  모니터링 중지됨")
        except Exception as e:
            print(f"❌ 모니터링 오류: {e}")

def main():
    """메인 함수"""
    messenger = CursorAutoMessenger()
    
    try:
        asyncio.run(messenger.start_monitoring())
    except Exception as e:
        print(f"❌ 프로그램 실행 오류: {e}")

if __name__ == "__main__":
    main()
