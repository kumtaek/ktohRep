"""
Q&A 자동 모니터링 시스템
5분 주기로 Q 파일을 감지하여 자동으로 A 파일 생성

사용법:
python qa_monitor.py [--interval 300] [--dev-report-dir ./Dev.Report]
"""

import os
import time
import glob
import re
from datetime import datetime
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Any
import subprocess
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qa_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QAMonitor:
    """Q&A 파일 모니터링 및 자동 답변 생성 클래스"""
    
    def __init__(self, dev_report_dir: str = "./Dev.Report", check_interval: int = 300):
        self.dev_report_dir = Path(dev_report_dir)
        self.check_interval = check_interval  # 초 단위 (300초 = 5분)
        self.processed_files = set()  # 이미 처리된 Q 파일들
        
        # Dev.Report 디렉토리 확인/생성
        self.dev_report_dir.mkdir(exist_ok=True)
        
        logger.info(f"QA 모니터 초기화 완료: {self.dev_report_dir}, 체크 간격: {self.check_interval}초")
    
    def find_q_files_without_answers(self) -> List[Path]:
        """답변이 없는 Q 파일들 찾기"""
        q_files = list(self.dev_report_dir.glob("Q_*.md"))
        unanswered_files = []
        
        for q_file in q_files:
            # Q_YYYYMMDD_HMS.md에서 타임스탬프 추출
            match = re.match(r'Q_(\d{8}_\d{4})\.md', q_file.name)
            if match:
                timestamp = match.group(1)
                corresponding_a_file = self.dev_report_dir / f"A_{timestamp}.md"
                
                # 대응하는 A 파일이 없고 아직 처리하지 않은 경우
                if not corresponding_a_file.exists() and str(q_file) not in self.processed_files:
                    unanswered_files.append(q_file)
                    logger.info(f"답변 대기 중인 Q 파일 발견: {q_file.name}")
        
        return unanswered_files
    
    def generate_answer_for_q_file(self, q_file_path: Path) -> bool:
        """Q 파일에 대한 자동 답변 생성"""
        try:
            logger.info(f"Q 파일 답변 생성 시작: {q_file_path.name}")
            
            # 타임스탬프 추출
            match = re.match(r'Q_(\d{8}_\d{4})\.md', q_file_path.name)
            if not match:
                logger.error(f"잘못된 Q 파일 형식: {q_file_path.name}")
                return False
            
            timestamp = match.group(1)
            
            # Q 파일 내용 읽기
            with open(q_file_path, 'r', encoding='utf-8') as f:
                q_content = f.read()
            
            logger.info(f"Q 파일 읽기 완료: {len(q_content)} 문자")
            
            # 프로젝트 구조 분석
            analysis_result = self.analyze_project_structure()
            
            # 답변 생성
            answer_content = self.create_comprehensive_answer(q_content, analysis_result, timestamp)
            
            # A 파일 생성
            a_file_path = self.dev_report_dir / f"A_{timestamp}.md"
            with open(a_file_path, 'w', encoding='utf-8') as f:
                f.write(answer_content)
            
            # 처리 완료 표시
            self.processed_files.add(str(q_file_path))
            
            logger.info(f"답변 생성 완료: {a_file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {e}")
            return False
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """프로젝트 구조 분석"""
        analysis = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files_analyzed': [],
            'key_components': [],
            'recent_changes': []
        }
        
        try:
            # Python 파일들 분석
            python_files = list(Path('.').rglob('*.py'))
            analysis['files_analyzed'] = [str(f) for f in python_files[:20]]  # 최대 20개만
            
            # 핵심 컴포넌트 식별
            key_patterns = ['parser', 'database', 'main', 'analyzer']
            for pattern in key_patterns:
                matching_files = [f for f in python_files if pattern in f.name.lower()]
                if matching_files:
                    analysis['key_components'].extend([str(f) for f in matching_files[:5]])
            
            # 최근 수정 파일들
            recent_files = []
            for py_file in python_files:
                try:
                    mtime = py_file.stat().st_mtime
                    recent_files.append((py_file, mtime))
                except:
                    continue
            
            # 최근 수정 순으로 정렬
            recent_files.sort(key=lambda x: x[1], reverse=True)
            analysis['recent_changes'] = [str(f[0]) for f in recent_files[:10]]
            
        except Exception as e:
            logger.warning(f"프로젝트 구조 분석 중 오류: {e}")
        
        return analysis
    
    def create_comprehensive_answer(self, q_content: str, analysis: Dict[str, Any], timestamp: str) -> str:
        """종합적인 답변 생성"""
        
        # Q 파일에서 핵심 질문 추출
        question_summary = self.extract_question_summary(q_content)
        
        # 답변 템플릿
        answer_template = f"""# {question_summary.get('title', '개발 질문')} 분석 답변

## 📅 분석 일시
- **분석 시간**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
- **분석 대상**: Q_{timestamp}.md

## 🔍 질문 요약
{question_summary.get('summary', 'Q 파일 내용을 바탕으로 분석')}

## 📋 프로젝트 현황 분석

### 핵심 컴포넌트
"""
        
        # 핵심 컴포넌트 분석 추가
        for component in analysis['key_components']:
            answer_template += f"- `{component}`\n"
        
        answer_template += f"""

### 최근 변경 파일들
"""
        
        # 최근 변경 파일 추가
        for recent_file in analysis['recent_changes'][:5]:
            answer_template += f"- `{recent_file}`\n"
        
        answer_template += f"""

## 💡 분석 결과 및 권장사항

### 🎯 핵심 이슈
{self.analyze_common_issues(analysis)}

### 🛠️ 해결 방안
{self.suggest_solutions(question_summary, analysis)}

### ⚠️ 주의사항
- 코드 수정 전 백업 권장
- 테스트 실행으로 변경사항 검증 필요
- 로그 파일 확인으로 오류 상황 모니터링

## 📊 분석 통계
- **분석된 파일 수**: {len(analysis['files_analyzed'])}
- **핵심 컴포넌트**: {len(analysis['key_components'])}개
- **최근 변경**: {len(analysis['recent_changes'])}개 파일

---
*자동 생성된 답변 - QA 모니터링 시스템*
"""
        
        return answer_template
    
    def extract_question_summary(self, q_content: str) -> Dict[str, str]:
        """Q 파일에서 질문 요약 추출"""
        summary = {
            'title': '개발 관련 질문',
            'summary': '프로젝트 분석이 필요한 질문입니다.'
        }
        
        try:
            # 제목 추출
            title_match = re.search(r'^#\s*(.+)$', q_content, re.MULTILINE)
            if title_match:
                summary['title'] = title_match.group(1).strip()
            
            # 질문 내용 섹션 추출
            question_match = re.search(r'##\s*❓.*?질문.*?\n(.*?)(?=##|\Z)', q_content, re.DOTALL | re.IGNORECASE)
            if question_match:
                summary['summary'] = question_match.group(1).strip()[:200] + "..."
            
        except Exception as e:
            logger.warning(f"질문 요약 추출 중 오류: {e}")
        
        return summary
    
    def analyze_common_issues(self, analysis: Dict[str, Any]) -> str:
        """일반적인 이슈 분석"""
        issues = [
            "파서 모듈의 객체 반환 구조 불일치 가능성",
            "데이터베이스 모델 관계 설정 확인 필요",
            "예외 처리 및 로깅 개선 검토"
        ]
        return "\n".join(f"- {issue}" for issue in issues)
    
    def suggest_solutions(self, question_summary: Dict[str, str], analysis: Dict[str, Any]) -> str:
        """해결방안 제안"""
        solutions = [
            "메소드 반환값 타입 및 구조 검증",
            "단위 테스트 작성으로 객체 생성 확인",
            "로그 분석을 통한 구체적 오류 원인 파악",
            "코드 리뷰를 통한 일관성 확보"
        ]
        return "\n".join(f"- {solution}" for solution in solutions)
    
    def monitor_and_process(self):
        """메인 모니터링 루프"""
        logger.info("Q&A 모니터링 시작 (5분 간격)")
        
        while True:
            try:
                # 답변이 없는 Q 파일들 찾기
                unanswered_files = self.find_q_files_without_answers()
                
                if unanswered_files:
                    logger.info(f"{len(unanswered_files)}개의 미답변 Q 파일 발견")
                    
                    # 각 Q 파일에 대해 답변 생성
                    for q_file in unanswered_files:
                        success = self.generate_answer_for_q_file(q_file)
                        if success:
                            logger.info(f"✅ 답변 생성 완료: {q_file.name}")
                        else:
                            logger.error(f"❌ 답변 생성 실패: {q_file.name}")
                        
                        # 연속 처리 시 간격 두기 (API 제한 고려)
                        time.sleep(2)
                else:
                    logger.info("새로운 Q 파일 없음")
                
                # 다음 체크까지 대기
                logger.info(f"다음 체크까지 {self.check_interval}초 대기...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("사용자에 의해 모니터링 중단됨")
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류 발생: {e}")
                time.sleep(60)  # 오류 시 1분 후 재시도

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Q&A 자동 모니터링 시스템')
    parser.add_argument('--interval', type=int, default=300, help='체크 간격(초), 기본값: 300 (5분)')
    parser.add_argument('--dev-report-dir', type=str, default='./Dev.Report', help='Dev.Report 디렉토리 경로')
    
    args = parser.parse_args()
    
    # QA 모니터 시작
    monitor = QAMonitor(dev_report_dir=args.dev_report_dir, check_interval=args.interval)
    monitor.monitor_and_process()

if __name__ == "__main__":
    main()