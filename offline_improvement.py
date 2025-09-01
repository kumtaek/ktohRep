#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오프라인 환경 개선 스크립트

1. Flask 서버 제거
2. 외부 CDN 의존성 제거 
3. 취약점 문서를 .md 파일로 다운로드 가능하도록 변경
4. 로컬 라이브러리 복사
"""

import os
import sys
import shutil
import requests
from pathlib import Path
import re

class OfflineImprovement:
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.output_path = self.root_path / "output"
        self.static_path = self.root_path / "static"
        
        # 다운로드할 외부 라이브러리들
        self.external_libs = {
            'jspdf': 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
            'mermaid': 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'
        }
    
    def download_external_libraries(self):
        """외부 라이브러리들을 로컬로 다운로드"""
        print("외부 라이브러리 다운로드 중...")
        
        vendor_path = self.static_path / "vendor"
        vendor_path.mkdir(parents=True, exist_ok=True)
        
        for lib_name, url in self.external_libs.items():
            lib_file = vendor_path / f"{lib_name}.min.js"
            if not lib_file.exists():
                try:
                    print(f"  - {lib_name} 다운로드 중...")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    with open(lib_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"    ✓ {lib_file} 저장됨")
                except Exception as e:
                    print(f"    ✗ {lib_name} 다운로드 실패: {e}")
                    # 폴백 버전 생성
                    self.create_fallback_library(lib_file, lib_name)
            else:
                print(f"  - {lib_name} 이미 존재함")
    
    def create_fallback_library(self, lib_file, lib_name):
        """다운로드 실패 시 폴백 라이브러리 생성"""
        print(f"    폴백 버전 생성: {lib_name}")
        
        if lib_name == 'jspdf':
            fallback_content = '''
// jsPDF Fallback - 오프라인 환경용 더미 구현
window.jsPDF = function() {
    return {
        text: function() { return this; },
        save: function(filename) { 
            alert('PDF 내보내기 기능은 온라인에서만 사용 가능합니다.\\n파일명: ' + filename);
        }
    };
};
'''
        elif lib_name == 'mermaid':
            fallback_content = '''
// Mermaid Fallback - 오프라인 환경용 더미 구현
window.mermaid = {
    initialize: function(config) {
        console.log('Mermaid initialized in offline mode');
    },
    init: function() {
        console.log('Mermaid diagram rendering disabled in offline mode');
        // 다이어그램 영역을 텍스트로 대체
        document.querySelectorAll('.mermaid').forEach(function(el) {
            el.innerHTML = '<pre style="background:#f5f5f5;padding:20px;border:1px solid #ddd;border-radius:4px;">' +
                          '시퀀스 다이어그램은 온라인 환경에서만 표시됩니다.\\n' +
                          '다이어그램 소스:\\n' + el.textContent + '</pre>';
        });
    }
};
'''
        else:
            fallback_content = f'// {lib_name} Fallback for offline use\nconsole.log("{lib_name} library loaded in offline mode");'
        
        with open(lib_file, 'w', encoding='utf-8') as f:
            f.write(fallback_content)
    
    def replace_external_cdn_urls(self):
        """HTML 파일들의 외부 CDN URL을 로컬 경로로 변경"""
        print("외부 CDN URL을 로컬 경로로 변경 중...")
        
        html_files = list(self.output_path.rglob("*.html"))
        
        replacements = {
            'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js': './static/vendor/jspdf.min.js',
            'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js': './static/vendor/mermaid.min.js'
        }
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                modified = False
                for old_url, new_url in replacements.items():
                    if old_url in content:
                        content = content.replace(old_url, new_url)
                        modified = True
                
                if modified:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ {html_file.relative_to(self.root_path)} 업데이트됨")
                    
            except Exception as e:
                print(f"  ✗ {html_file} 처리 실패: {e}")
    
    def create_vulnerability_docs_downloader(self):
        """취약점 문서 다운로드 기능 생성"""
        print("취약점 문서 다운로드 기능 생성 중...")
        
        downloader_script = self.root_path / "download_vulnerability_docs.py"
        
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
취약점 문서 다운로드 스크립트
Flask 서버 없이 취약점 문서를 .md 파일로 다운로드
"""

import os
import sqlite3
from pathlib import Path

class VulnerabilityDocsDownloader:
    def __init__(self, project_name):
        self.project_name = project_name
        self.db_path = f"PROJECT/{project_name}/data/metadata.db"
        self.output_dir = Path(f"output/{project_name}/vulnerability_docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_vulnerability_docs(self):
        """취약점 문서를 .md 파일로 추출"""
        if not os.path.exists(self.db_path):
            print(f"데이터베이스를 찾을 수 없습니다: {self.db_path}")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 취약점 정보 조회
        cursor.execute("""
            SELECT DISTINCT cwe_code, owasp_code, description
            FROM vulnerability_fixes
            WHERE cwe_code IS NOT NULL OR owasp_code IS NOT NULL
        """)
        
        vulnerabilities = cursor.fetchall()
        
        if not vulnerabilities:
            print("취약점 정보를 찾을 수 없습니다.")
            return
        
        # 각 취약점별 .md 파일 생성
        for cwe_code, owasp_code, description in vulnerabilities:
            if cwe_code:
                self.create_vulnerability_md(f"CWE-{cwe_code}", description)
            if owasp_code:
                self.create_vulnerability_md(f"OWASP-{owasp_code}", description)
        
        conn.close()
        print(f"취약점 문서가 {self.output_dir}에 생성되었습니다.")
    
    def create_vulnerability_md(self, code, description):
        """취약점 .md 파일 생성"""
        filename = f"{code}.md"
        filepath = self.output_dir / filename
        
        content = f"""# {code} 취약점 분석

## 개요
{description or '상세 설명 없음'}

## 발견된 위치
이 취약점이 발견된 코드 위치와 관련 정보입니다.

## 권장 수정 방안
- 입력값 검증 강화
- 적절한 인코딩/이스케이핑 적용
- 보안 라이브러리 사용

## 참고 자료
- [{code} 공식 문서](#{code.lower()})
- [OWASP 가이드라인](#owasp)

---
*생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    if len(sys.argv) < 2:
        print("사용법: python download_vulnerability_docs.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    downloader = VulnerabilityDocsDownloader(project_name)
    downloader.download_vulnerability_docs()
'''
        
        with open(downloader_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"  ✓ {downloader_script} 생성됨")
    
    def remove_flask_references(self):
        """Flask 관련 참조 제거 및 정적 파일로 변경"""
        print("Flask 참조 제거 중...")
        
        # requirements.txt에서 Flask 관련 패키지 제거
        req_file = self.root_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            filtered_lines = []
            for line in lines:
                line_lower = line.lower()
                if not any(pkg in line_lower for pkg in ['flask', 'werkzeug', 'jinja2', 'markupsafe', 'itsdangerous']):
                    filtered_lines.append(line)
            
            with open(req_file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
            
            print(f"  ✓ {req_file} 에서 Flask 종속성 제거됨")
    
    def create_offline_guide(self):
        """오프라인 사용 가이드 생성"""
        guide_file = self.root_path / "OFFLINE_GUIDE.md"
        
        guide_content = """# 오프라인 환경 사용 가이드

## 개요
이 소스 분석기는 이제 완전히 오프라인 환경에서 동작하도록 개선되었습니다.

## 변경사항

### 1. Flask 서버 제거
- 기존: Flask 웹서버를 통한 취약점 문서 제공
- 변경: 정적 .md 파일 다운로드 방식으로 변경

### 2. 외부 CDN 의존성 제거
- jsPDF: 로컬 파일 또는 폴백 버전 사용
- Mermaid: 로컬 파일 또는 폴백 버전 사용

### 3. 취약점 문서 다운로드
```bash
# 취약점 문서를 .md 파일로 다운로드
python download_vulnerability_docs.py sampleSrc
```

## 사용 방법

### 1. 분석 실행
```bash
# 기본 분석
./run_analyzer.bat sampleSrc

# 시각화 생성
./run_visualize.bat sampleSrc
```

### 2. 결과 확인
- `output/[프로젝트명]/visualize/*.html` - 시각화 결과
- `output/[프로젝트명]/*.md` - 마크다운 리포트
- `output/[프로젝트명]/vulnerability_docs/*.md` - 취약점 문서

### 3. 오프라인 제한사항
- PDF 내보내기: 온라인 환경에서만 가능
- 시퀀스 다이어그램: 텍스트 형태로 표시
- 일부 고급 시각화 기능 제한

## 파일 구조
```
SourceAnalyzer/
├── static/vendor/          # 로컬 라이브러리
│   ├── jspdf.min.js
│   └── mermaid.min.js
├── output/[project]/
│   ├── visualize/          # HTML 시각화
│   ├── vulnerability_docs/ # 취약점 .md 파일
│   └── *.md               # 리포트 파일
└── download_vulnerability_docs.py
```

## 문제 해결

### 1. 시각화가 표시되지 않는 경우
- 브라우저의 로컬 파일 정책 확인
- 파일://로 시작하는 경로에서 실행

### 2. 라이브러리 오류
```bash
# 외부 라이브러리 다시 다운로드
python offline_improvement.py --download-libs
```

### 3. 폐쇄망 환경
- 모든 기능이 로컬에서 동작
- 인터넷 연결 불필요
- 정적 파일만 사용
"""
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"  ✓ {guide_file} 생성됨")
    
    def run_improvement(self):
        """모든 오프라인 개선 작업 실행"""
        print("=== 오프라인 환경 개선 시작 ===")
        
        try:
            # 1. 외부 라이브러리 다운로드
            self.download_external_libraries()
            
            # 2. CDN URL 교체
            self.replace_external_cdn_urls()
            
            # 3. 취약점 문서 다운로더 생성
            self.create_vulnerability_docs_downloader()
            
            # 4. Flask 참조 제거
            self.remove_flask_references()
            
            # 5. 오프라인 가이드 생성
            self.create_offline_guide()
            
            print("=== 오프라인 환경 개선 완료 ===")
            print("\n다음 명령으로 취약점 문서를 다운로드하세요:")
            print("python download_vulnerability_docs.py sampleSrc")
            
        except Exception as e:
            print(f"오프라인 개선 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    improver = OfflineImprovement()
    improver.run_improvement()