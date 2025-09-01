#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 오프라인 환경 개선 스크립트
"""

import os
import re
from pathlib import Path

def create_fallback_libraries():
    """폴백 라이브러리 생성"""
    static_dir = Path("static/vendor")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # jsPDF 폴백
    jspdf_content = """
// jsPDF Fallback
window.jsPDF = function() {
    return {
        text: function() { return this; },
        save: function(filename) { 
            alert('PDF 내보내기는 온라인에서만 가능합니다.');
        }
    };
};
"""
    
    # Mermaid 폴백
    mermaid_content = """
// Mermaid Fallback
window.mermaid = {
    initialize: function(config) {
        console.log('Mermaid offline mode');
    },
    init: function() {
        document.querySelectorAll('.mermaid').forEach(function(el) {
            el.innerHTML = '<pre style="background:#f5f5f5;padding:20px;">시퀀스 다이어그램 (오프라인 모드)</pre>';
        });
    }
};
"""
    
    with open(static_dir / "jspdf.min.js", 'w', encoding='utf-8') as f:
        f.write(jspdf_content)
    
    with open(static_dir / "mermaid.min.js", 'w', encoding='utf-8') as f:
        f.write(mermaid_content)
    
    print("폴백 라이브러리 생성 완료")

def fix_cdn_urls():
    """HTML 파일의 CDN URL을 로컬 경로로 변경"""
    output_dir = Path("output")
    if not output_dir.exists():
        print("output 디렉토리가 없습니다")
        return
    
    count = 0
    for html_file in output_dir.rglob("*.html"):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CDN URL 교체
            modified = False
            if 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js' in content:
                content = content.replace(
                    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
                    './static/vendor/jspdf.min.js'
                )
                modified = True
            
            if 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js' in content:
                content = content.replace(
                    'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js',
                    './static/vendor/mermaid.min.js'
                )
                modified = True
            
            if modified:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                
        except Exception as e:
            print(f"파일 처리 실패: {html_file} - {e}")
    
    print(f"CDN URL 변경 완료: {count}개 파일")

def create_vulnerability_downloader():
    """취약점 문서 다운로더 생성"""
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""취약점 문서 다운로더"""
import os
import sqlite3
from pathlib import Path
from datetime import datetime

def download_docs(project_name):
    db_path = f"PROJECT/{project_name}/data/metadata.db"
    if not os.path.exists(db_path):
        print(f"DB 파일 없음: {db_path}")
        return
    
    output_dir = Path(f"output/{project_name}/vulnerability_docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 취약점 정보 조회 시도
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vulnerability_fixes'")
        if cursor.fetchone():
            cursor.execute("SELECT DISTINCT cwe_code, description FROM vulnerability_fixes WHERE cwe_code IS NOT NULL")
            vulnerabilities = cursor.fetchall()
            
            for cwe_code, desc in vulnerabilities:
                content = f"""# CWE-{cwe_code} 취약점 분석

## 설명
{desc or '상세 설명 없음'}

## 권장 수정사항
- 입력값 검증 강화
- 적절한 인코딩 적용
- 보안 라이브러리 사용

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                with open(output_dir / f"CWE-{cwe_code}.md", 'w', encoding='utf-8') as f:
                    f.write(content)
            
            print(f"취약점 문서 {len(vulnerabilities)}개 생성 완료: {output_dir}")
        else:
            print("vulnerability_fixes 테이블이 없습니다")
    except Exception as e:
        print(f"취약점 문서 생성 실패: {e}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        download_docs(sys.argv[1])
    else:
        print("사용법: python download_vulnerability_docs.py <project_name>")
'''
    
    with open("download_vulnerability_docs.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("취약점 다운로더 생성 완료")

def main():
    print("=== 오프라인 환경 개선 ===")
    
    # 1. 폴백 라이브러리 생성
    create_fallback_libraries()
    
    # 2. CDN URL 수정
    fix_cdn_urls()
    
    # 3. 취약점 다운로더 생성
    create_vulnerability_downloader()
    
    print("=== 개선 작업 완료 ===")
    print("다음 명령으로 취약점 문서 다운로드:")
    print("python download_vulnerability_docs.py sampleSrc")

if __name__ == "__main__":
    main()