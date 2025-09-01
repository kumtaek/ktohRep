#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쿼리 및 JSP 리스트를 생성하는 스크립트

메타데이터에서 쿼리ID, JSP 파일 정보를 추출하고
LLM을 사용하여 요약을 생성한 후 .md 파일로 출력합니다.
"""
import sqlite3
import os
import sys
import json
from pathlib import Path
import argparse
from datetime import datetime

# LLM API 설정 (OpenAI 또는 기타 LLM 서비스 사용)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI 라이브러리를 사용할 수 없습니다. LLM 요약 기능이 제한됩니다.")

class ListGenerator:
    def __init__(self, project_name):
        self.project_name = project_name
        self.db_path = f"PROJECT/{project_name}/data/metadata.db"
        self.project_root = f"PROJECT/{project_name}"
        self.output_dir = f"output/{project_name}"
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
    
    def connect_db(self):
        """데이터베이스 연결"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"데이터베이스 파일을 찾을 수 없습니다: {self.db_path}")
        return sqlite3.connect(self.db_path)
    
    def read_file_content(self, file_path, max_size=4096):
        """파일 내용을 읽어옵니다. 크기가 큰 경우 4KB까지만 읽습니다."""
        try:
            full_path = os.path.join(self.project_root, file_path.replace('PROJECT\\', '').replace(f'{self.project_name}\\', ''))
            if not os.path.exists(full_path):
                # 경로 구분자 변경 시도
                full_path = full_path.replace('\\', '/')
                if not os.path.exists(full_path):
                    return None
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_size)
                return content
        except Exception as e:
            print(f"파일 읽기 오류: {file_path} - {e}")
            return None
    
    def generate_summary_with_llm(self, content, file_type="code"):
        """LLM을 사용하여 파일 내용 요약 생성"""
        if not OPENAI_AVAILABLE or not content:
            return "요약 정보 없음"
        
        try:
            # 여기에 실제 LLM API 호출 코드를 구현
            # 현재는 간단한 더미 요약을 반환
            if file_type == "jsp":
                return f"JSP 파일: {len(content.split())}개 단어, 화면 렌더링 관련 코드"
            elif file_type == "mapper":
                return f"Mapper 파일: {content.count('select')}개 SELECT 쿼리, {content.count('insert')}개 INSERT 쿼리 포함"
            else:
                return f"코드 파일: {len(content.splitlines())}줄, {len(content.split())}개 단어"
        except Exception as e:
            print(f"LLM 요약 생성 오류: {e}")
            return "요약 생성 실패"
    
    def generate_query_list(self):
        """쿼리 리스트 생성"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # SQL 쿼리 정보 조회
        cursor.execute("""
            SELECT su.sql_id, su.stmt_id, su.llm_summary, f.path, su.stmt_kind
            FROM sql_units su
            JOIN files f ON su.file_id = f.file_id
            ORDER BY su.sql_id
        """)
        
        queries = cursor.fetchall()
        
        # 쿼리가 없으면 Mapper 파일에서 직접 추출
        if not queries:
            cursor.execute("""
                SELECT file_id, path, llm_summary
                FROM files
                WHERE path LIKE '%Mapper.java' OR path LIKE '%mapper%.xml'
            """)
            mapper_files = cursor.fetchall()
            queries = []
            
            for file_id, file_path, existing_summary in mapper_files:
                content = self.read_file_content(file_path)
                if content:
                    # 기존 요약이 없으면 새로 생성
                    if not existing_summary:
                        summary = self.generate_summary_with_llm(content, "mapper")
                        # DB에 요약 업데이트
                        cursor.execute("UPDATE files SET llm_summary = ? WHERE file_id = ?", 
                                     (summary, file_id))
                    else:
                        summary = existing_summary
                    
                    queries.append((file_id, file_path.split('/')[-1], summary, file_path, "mapper"))
        
        conn.commit()
        conn.close()
        
        # Markdown 파일 생성
        md_content = self._generate_query_markdown(queries)
        
        output_file = os.path.join(self.output_dir, "쿼리리스트.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"쿼리 리스트가 생성되었습니다: {output_file}")
        return output_file
    
    def generate_jsp_list(self):
        """JSP 리스트 생성"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # JSP 파일 정보 조회
        cursor.execute("""
            SELECT file_id, path, llm_summary
            FROM files
            WHERE path LIKE '%.jsp'
            ORDER BY path
        """)
        
        jsp_files = cursor.fetchall()
        
        # JSP 파일이 없으면 실제 파일시스템에서 찾기
        if not jsp_files:
            jsp_files = self._find_jsp_files_in_filesystem()
        
        # 요약이 없는 파일에 대해 LLM 요약 생성
        updated_jsp_files = []
        for file_id, file_path, existing_summary in jsp_files:
            content = self.read_file_content(file_path)
            if content:
                if not existing_summary:
                    summary = self.generate_summary_with_llm(content, "jsp")
                    if file_id:  # DB에 파일이 있는 경우만 업데이트
                        cursor.execute("UPDATE files SET llm_summary = ? WHERE file_id = ?", 
                                     (summary, file_id))
                else:
                    summary = existing_summary
                
                updated_jsp_files.append((file_id, file_path, summary))
        
        conn.commit()
        conn.close()
        
        # Markdown 파일 생성
        md_content = self._generate_jsp_markdown(updated_jsp_files)
        
        output_file = os.path.join(self.output_dir, "JSP리스트.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"JSP 리스트가 생성되었습니다: {output_file}")
        return output_file
    
    def _find_jsp_files_in_filesystem(self):
        """파일시스템에서 JSP 파일 찾기"""
        jsp_files = []
        project_path = Path(self.project_root)
        
        for jsp_file in project_path.rglob("*.jsp"):
            relative_path = str(jsp_file.relative_to(project_path.parent))
            jsp_files.append((None, relative_path, None))
        
        return jsp_files
    
    def _generate_query_markdown(self, queries):
        """쿼리 리스트 Markdown 생성"""
        content = f"""# 쿼리 리스트

**프로젝트:** {self.project_name}  
**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**총 쿼리 수:** {len(queries)}개

---

## 쿼리 목록

| 번호 | 쿼리ID/파일명 | 타입 | 요약 | 파일 경로 |
|------|---------------|------|------|-----------|
"""
        
        for idx, (query_id, stmt_id, summary, file_path, stmt_kind) in enumerate(queries, 1):
            summary = summary or "요약 정보 없음"
            content += f"| {idx} | {stmt_id or query_id} | {stmt_kind} | {summary[:100]}{'...' if len(summary) > 100 else ''} | {file_path} |\n"
        
        content += "\n---\n\n## 상세 정보\n\n"
        
        for idx, (query_id, stmt_id, summary, file_path, stmt_kind) in enumerate(queries, 1):
            content += f"### {idx}. {stmt_id or f'쿼리-{query_id}'}\n\n"
            content += f"- **타입:** {stmt_kind}\n"
            content += f"- **파일:** {file_path}\n"
            content += f"- **요약:** {summary or '요약 정보 없음'}\n\n"
        
        return content
    
    def _generate_jsp_markdown(self, jsp_files):
        """JSP 리스트 Markdown 생성"""
        content = f"""# JSP 리스트

**프로젝트:** {self.project_name}  
**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**총 JSP 파일 수:** {len(jsp_files)}개

---

## JSP 파일 목록

| 번호 | JSP 파일명 | 요약 | 파일 경로 |
|------|------------|------|-----------|
"""
        
        for idx, (file_id, file_path, summary) in enumerate(jsp_files, 1):
            file_name = os.path.basename(file_path)
            summary = summary or "요약 정보 없음"
            content += f"| {idx} | {file_name} | {summary[:100]}{'...' if len(summary) > 100 else ''} | {file_path} |\n"
        
        content += "\n---\n\n## 상세 정보\n\n"
        
        for idx, (file_id, file_path, summary) in enumerate(jsp_files, 1):
            file_name = os.path.basename(file_path)
            content += f"### {idx}. {file_name}\n\n"
            content += f"- **파일 경로:** {file_path}\n"
            content += f"- **요약:** {summary or '요약 정보 없음'}\n\n"
        
        return content

def main():
    parser = argparse.ArgumentParser(description='쿼리 및 JSP 리스트 생성')
    parser.add_argument('--project-name', required=True, help='프로젝트 이름')
    parser.add_argument('--type', choices=['query', 'jsp', 'all'], default='all', 
                       help='생성할 리스트 타입')
    
    args = parser.parse_args()
    
    try:
        generator = ListGenerator(args.project_name)
        
        if args.type in ['query', 'all']:
            generator.generate_query_list()
        
        if args.type in ['jsp', 'all']:
            generator.generate_jsp_list()
        
        print("리스트 생성이 완료되었습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()