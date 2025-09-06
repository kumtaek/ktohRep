"""
Q 파일 내용을 분석하여 자동으로 A 파일 생성하는 고급 분석기
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

class ProjectCodeAnalyzer:
    """프로젝트 코드 자동 분석 클래스"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # 분석 대상 파일 패턴들
        self.analysis_patterns = {
            'parsers': 'phase1/parsers/*.py',
            'models': 'phase1/models/*.py',
            'database': 'phase1/database/*.py',
            'utils': 'phase1/utils/*.py',
            'main': 'phase1/main.py',
            'config': 'config/**/*.yaml',
            'logs': 'logs/*.log'
        }
    
    def analyze_question_context(self, q_content: str) -> Dict[str, Any]:
        """Q 파일 내용을 분석하여 컨텍스트 파악"""
        context = {
            'question_type': 'general',
            'mentioned_files': [],
            'mentioned_methods': [],
            'mentioned_errors': [],
            'keywords': [],
            'priority': 'medium'
        }
        
        try:
            # 언급된 파일들 추출
            file_patterns = [
                r'`([^`]+\.py)`',
                r'`([^`]+\.java)`',
                r'([a-zA-Z_][a-zA-Z0-9_]*\.py)',
                r'([a-zA-Z_][a-zA-Z0-9_]*_parser\.py)'
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, q_content)
                context['mentioned_files'].extend(matches)
            
            # 언급된 메소드들 추출
            method_patterns = [
                r'`([a-zA-Z_][a-zA-Z0-9_]*)\(`',
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*메소드',
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*함수'
            ]
            
            for pattern in method_patterns:
                matches = re.findall(pattern, q_content)
                context['mentioned_methods'].extend(matches)
            
            # 에러 메시지 추출
            error_patterns = [
                r"'([^']*object has no attribute[^']*)'",
                r'`([^`]*Error[^`]*)`',
                r'오류[:\s]*([^\n]+)',
                r'에러[:\s]*([^\n]+)'
            ]
            
            for pattern in error_patterns:
                matches = re.findall(pattern, q_content)
                context['mentioned_errors'].extend(matches)
            
            # 키워드 추출
            keywords = ['Join', 'SQL', '파싱', '객체', '반환', '구조', '튜플', '리스트']
            context['keywords'] = [kw for kw in keywords if kw.lower() in q_content.lower()]
            
            # 우선순위 결정
            if any('critical' in err.lower() or 'error' in err.lower() for err in context['mentioned_errors']):
                context['priority'] = 'high'
            elif context['mentioned_methods'] or context['mentioned_files']:
                context['priority'] = 'medium'
            
        except Exception as e:
            self.logger.warning(f"질문 컨텍스트 분석 중 오류: {e}")
        
        return context
    
    def analyze_mentioned_files(self, mentioned_files: List[str]) -> Dict[str, Any]:
        """언급된 파일들 실제 분석"""
        file_analysis = {}
        
        for file_name in mentioned_files:
            try:
                # 파일 경로 해결
                file_paths = list(self.project_root.rglob(file_name))
                if not file_paths:
                    # 파일명만으로 검색
                    file_paths = list(self.project_root.rglob(f"*{file_name}*"))
                
                for file_path in file_paths[:1]:  # 첫 번째 매치만 분석
                    analysis = self._analyze_single_file(file_path)
                    file_analysis[str(file_path)] = analysis
                    
            except Exception as e:
                self.logger.warning(f"파일 분석 중 오류 {file_name}: {e}")
        
        return file_analysis
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """단일 파일 분석"""
        analysis = {
            'exists': False,
            'size': 0,
            'last_modified': '',
            'methods': [],
            'classes': [],
            'imports': [],
            'key_patterns': []
        }
        
        try:
            if not file_path.exists():
                return analysis
            
            analysis['exists'] = True
            analysis['size'] = file_path.stat().st_size
            analysis['last_modified'] = datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            # 파일 내용 분석 (Python 파일만)
            if file_path.suffix == '.py':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 메소드 추출
                method_matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
                analysis['methods'] = list(set(method_matches))
                
                # 클래스 추출
                class_matches = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                analysis['classes'] = list(set(class_matches))
                
                # 임포트 추출
                import_matches = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
                analysis['imports'] = list(set(import_matches))
                
                # 핵심 패턴 검색
                key_patterns = ['Join', 'SqlUnit', 'return', 'Tuple', 'List']
                analysis['key_patterns'] = [
                    pattern for pattern in key_patterns 
                    if pattern in content
                ]
        
        except Exception as e:
            self.logger.warning(f"파일 분석 중 오류 {file_path}: {e}")
        
        return analysis
    
    def find_related_issues(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """관련 이슈들 검색"""
        issues = []
        
        # 로그 파일에서 관련 오류 검색
        try:
            log_files = list(self.project_root.rglob('*.log'))
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    # 언급된 에러와 매칭되는 로그 엔트리 찾기
                    for error in context.get('mentioned_errors', []):
                        if error.lower() in log_content.lower():
                            issues.append({
                                'type': 'log_match',
                                'file': str(log_file),
                                'error': error,
                                'context': '로그에서 동일 에러 패턴 발견'
                            })
                            
                except Exception as e:
                    self.logger.debug(f"로그 파일 분석 중 오류 {log_file}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"관련 이슈 검색 중 오류: {e}")
        
        return issues
    
    def generate_detailed_answer(self, q_content: str, timestamp: str) -> str:
        """상세한 답변 생성"""
        
        # 1. 질문 컨텍스트 분석
        context = self.analyze_question_context(q_content)
        
        # 2. 언급된 파일들 분석
        file_analysis = self.analyze_mentioned_files(context['mentioned_files'])
        
        # 3. 관련 이슈 검색
        related_issues = self.find_related_issues(context)
        
        # 4. 종합 답변 생성
        answer = self._build_comprehensive_answer(q_content, context, file_analysis, related_issues, timestamp)
        
        return answer
    
    def _build_comprehensive_answer(self, q_content: str, context: Dict[str, Any], 
                                  file_analysis: Dict[str, Any], related_issues: List[Dict[str, str]], 
                                  timestamp: str) -> str:
        """종합 답변 작성"""
        
        answer_parts = []
        
        # 헤더
        answer_parts.append(f"""# 개발 질문 자동 분석 답변

## 📅 분석 정보
- **분석 시간**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
- **질문 파일**: Q_{timestamp}.md
- **우선순위**: {context['priority'].upper()}

## 🔍 질문 분석 결과

### 언급된 구성요소
""")
        
        # 언급된 파일들
        if context['mentioned_files']:
            answer_parts.append("**파일들:**")
            for file_name in set(context['mentioned_files']):
                answer_parts.append(f"- `{file_name}`")
            answer_parts.append("")
        
        # 언급된 메소드들
        if context['mentioned_methods']:
            answer_parts.append("**메소드들:**")
            for method in set(context['mentioned_methods']):
                answer_parts.append(f"- `{method}()`")
            answer_parts.append("")
        
        # 발견된 에러들
        if context['mentioned_errors']:
            answer_parts.append("**에러 메시지들:**")
            for error in set(context['mentioned_errors']):
                answer_parts.append(f"- `{error}`")
            answer_parts.append("")
        
        # 파일 분석 결과
        if file_analysis:
            answer_parts.append("## 📋 파일 분석 결과")
            for file_path, analysis in file_analysis.items():
                if analysis['exists']:
                    answer_parts.append(f"""
### `{Path(file_path).name}`
- **크기**: {analysis['size']:,} 바이트
- **수정일**: {analysis['last_modified']}
- **메소드 수**: {len(analysis['methods'])}개
- **클래스 수**: {len(analysis['classes'])}개
""")
                    
                    if analysis['methods']:
                        key_methods = [m for m in analysis['methods'] if any(kw in m.lower() for kw in ['extract', 'parse', 'join'])]
                        if key_methods:
                            answer_parts.append("**핵심 메소드들:**")
                            for method in key_methods[:5]:
                                answer_parts.append(f"- `{method}()`")
                            answer_parts.append("")
        
        # 관련 이슈들
        if related_issues:
            answer_parts.append("## 🚨 발견된 관련 이슈")
            for issue in related_issues[:3]:  # 최대 3개만
                answer_parts.append(f"- **{issue['type']}**: {issue['context']}")
            answer_parts.append("")
        
        # 권장사항
        answer_parts.append("""## 💡 분석 기반 권장사항

### 🎯 즉시 조치사항
- 언급된 메소드의 반환값 타입 검증
- 관련 파일들의 최근 변경사항 검토
- 로그 파일에서 상세 오류 컨텍스트 확인

### 🔧 구체적 해결 접근법
1. **객체 타입 검증**: `isinstance()` 또는 `type()` 사용한 디버깅
2. **반환값 구조 확인**: 메소드 시그니처와 실제 반환값 비교
3. **단위 테스트**: 문제가 되는 메소드에 대한 테스트 케이스 작성

### ⚠️ 주의사항
- 코드 수정 전 현재 상태 백업
- 변경 후 전체 테스트 파이프라인 실행
- 로그 레벨을 DEBUG로 설정하여 상세 추적

## 📊 분석 요약
- **분석된 키워드**: {len(context['keywords'])}개
- **검토 대상 파일**: {len(file_analysis)}개
- **발견된 관련 이슈**: {len(related_issues)}개

---
*SourceAnalyzer 자동 분석 시스템에 의해 생성됨*
""")
        
        return "\n".join(answer_parts)

class AutoAnswerGenerator:
    """자동 답변 생성 통합 클래스"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analyzer = ProjectCodeAnalyzer(project_root)
        self.logger = logging.getLogger(__name__)
    
    def process_q_file(self, q_file_path: Path) -> Optional[str]:
        """Q 파일 처리하여 A 파일 생성"""
        try:
            # Q 파일 읽기
            with open(q_file_path, 'r', encoding='utf-8') as f:
                q_content = f.read()
            
            self.logger.info(f"Q 파일 처리 시작: {q_file_path.name}")
            
            # 타임스탬프 추출
            match = re.match(r'Q_(\d{8}_\d{4})\.md', q_file_path.name)
            if not match:
                self.logger.error(f"잘못된 Q 파일 형식: {q_file_path.name}")
                return None
            
            timestamp = match.group(1)
            
            # 상세 분석 및 답변 생성
            answer_content = self.analyzer.generate_detailed_answer(q_content, timestamp)
            
            # A 파일 경로 결정
            a_file_path = q_file_path.parent / f"A_{timestamp}.md"
            
            # A 파일 생성
            with open(a_file_path, 'w', encoding='utf-8') as f:
                f.write(answer_content)
            
            self.logger.info(f"A 파일 생성 완료: {a_file_path.name}")
            return str(a_file_path)
            
        except Exception as e:
            self.logger.error(f"Q 파일 처리 중 오류: {e}")
            return None

def create_answer_for_question(q_file_path: str) -> bool:
    """외부에서 호출 가능한 답변 생성 함수"""
    try:
        generator = AutoAnswerGenerator()
        result = generator.process_q_file(Path(q_file_path))
        return result is not None
    except Exception as e:
        print(f"답변 생성 중 오류: {e}")
        return False

if __name__ == "__main__":
    # 테스트용 실행
    import sys
    
    if len(sys.argv) > 1:
        q_file_path = sys.argv[1]
        success = create_answer_for_question(q_file_path)
        if success:
            print(f"✅ 답변 생성 완료: {q_file_path}")
        else:
            print(f"❌ 답변 생성 실패: {q_file_path}")
    else:
        print("사용법: python qa_auto_analyzer.py Q_YYYYMMDD_HMS.md")