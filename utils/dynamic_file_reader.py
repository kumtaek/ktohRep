"""
동적 파일 정보 조회 유틸리티
메타DB에 저장하지 않고 실시간으로 ./project 폴더의 파일을 조회
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
import ast
import re

class DynamicFileReader:
    """./project 폴더의 파일들을 동적으로 읽어서 상세 정보 제공"""
    
    def __init__(self, project_path: str = "./project"):
        self.project_path = Path(project_path)
        self.cache = {}  # 간단한 캐시
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """파일 내용 읽기"""
        try:
            full_path = self.project_path / file_path
            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
            return None
        except Exception:
            return None
    
    def get_java_class_details(self, file_path: str) -> Dict:
        """Java 파일의 상세 정보 동적 추출"""
        content = self.get_file_content(file_path)
        if not content:
            return {}
        
        details = {
            'imports': [],
            'package': None,
            'classes': [],
            'methods': [],
            'fields': [],
            'annotations': []
        }
        
        lines = content.split('\n')
        
        # 패키지명 추출
        for line in lines:
            if line.strip().startswith('package '):
                details['package'] = line.strip().replace('package ', '').replace(';', '')
                break
        
        # import 추출
        for line in lines:
            if line.strip().startswith('import '):
                import_name = line.strip().replace('import ', '').replace(';', '')
                details['imports'].append(import_name)
        
        # 클래스, 메서드 추출 (간단한 정규식 사용)
        class_pattern = r'(public|private|protected)?\s*class\s+(\w+)'
        method_pattern = r'(public|private|protected)?\s*(static\s+)?(\w+)\s+(\w+)\s*\([^)]*\)'
        field_pattern = r'(public|private|protected)?\s*(static\s+)?(final\s+)?(\w+)\s+(\w+)'
        annotation_pattern = r'@(\w+)'
        
        for i, line in enumerate(lines, 1):
            # 클래스 찾기
            class_match = re.search(class_pattern, line)
            if class_match:
                details['classes'].append({
                    'name': class_match.group(2),
                    'line': i,
                    'modifier': class_match.group(1) or 'default'
                })
            
            # 메서드 찾기
            method_match = re.search(method_pattern, line)
            if method_match:
                details['methods'].append({
                    'name': method_match.group(4),
                    'return_type': method_match.group(3),
                    'line': i,
                    'modifier': method_match.group(1) or 'default',
                    'is_static': 'static' in line
                })
            
            # 어노테이션 찾기
            annotation_match = re.search(annotation_pattern, line)
            if annotation_match:
                details['annotations'].append({
                    'name': annotation_match.group(1),
                    'line': i
                })
        
        return details
    
    def get_method_body(self, file_path: str, method_name: str, start_line: int) -> Optional[str]:
        """특정 메서드의 본문 내용 추출"""
        content = self.get_file_content(file_path)
        if not content:
            return None
        
        lines = content.split('\n')
        if start_line > len(lines):
            return None
        
        # 메서드 시작점에서 중괄호 매칭하여 끝점 찾기
        brace_count = 0
        method_lines = []
        start_found = False
        
        for i, line in enumerate(lines[start_line-1:], start_line):
            if '{' in line:
                brace_count += line.count('{')
                start_found = True
            if '}' in line:
                brace_count -= line.count('}')
            
            if start_found:
                method_lines.append(line)
                
            if start_found and brace_count == 0:
                break
        
        return '\n'.join(method_lines)
    
    def get_sql_queries(self, file_path: str) -> List[Dict]:
        """JSP나 Java 파일에서 SQL 쿼리 추출"""
        content = self.get_file_content(file_path)
        if not content:
            return []
        
        queries = []
        
        # SQL 패턴들
        sql_patterns = [
            r'(SELECT\s+.*?(?:FROM|;))',
            r'(INSERT\s+INTO\s+.*?(?:VALUES|;))',
            r'(UPDATE\s+.*?(?:SET|;))',
            r'(DELETE\s+FROM\s+.*?(?:WHERE|;))'
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in sql_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    queries.append({
                        'query': match.group(1),
                        'line': i,
                        'type': match.group(1).split()[0].upper()
                    })
        
        return queries
    
    def search_code_patterns(self, pattern: str, file_types: List[str] = None) -> List[Dict]:
        """프로젝트 전체에서 코드 패턴 검색"""
        results = []
        file_types = file_types or ['.java', '.jsp', '.xml', '.sql']
        
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in file_types:
                content = self.get_file_content(str(file_path.relative_to(self.project_path)))
                if content and pattern in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern in line:
                            results.append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'line': i,
                                'content': line.strip()
                            })
        
        return results
    
    def get_component_context(self, file_path: str, component_name: str, context_lines: int = 5) -> Dict:
        """컴포넌트 주변 컨텍스트 정보 제공"""
        content = self.get_file_content(file_path)
        if not content:
            return {}
        
        lines = content.split('\n')
        
        # 컴포넌트 위치 찾기
        component_line = None
        for i, line in enumerate(lines):
            if component_name in line:
                component_line = i
                break
        
        if component_line is None:
            return {}
        
        start_line = max(0, component_line - context_lines)
        end_line = min(len(lines), component_line + context_lines + 1)
        
        return {
            'component_name': component_name,
            'file_path': file_path,
            'component_line': component_line + 1,
            'context': {
                'before': lines[start_line:component_line],
                'target': lines[component_line],
                'after': lines[component_line+1:end_line]
            }
        }
    
    def analyze_dependencies(self, file_path: str) -> Dict:
        """파일의 의존성 분석"""
        content = self.get_file_content(file_path)
        if not content:
            return {}
        
        dependencies = {
            'imports': [],
            'internal_calls': [],
            'external_libraries': []
        }
        
        # import 문 분석
        for line in content.split('\n'):
            if line.strip().startswith('import '):
                import_name = line.strip().replace('import ', '').replace(';', '')
                if import_name.startswith('java.'):
                    dependencies['external_libraries'].append(import_name)
                else:
                    dependencies['imports'].append(import_name)
        
        return dependencies


class MetaQueryOptimizer:
    """메타DB + 동적 파일 읽기 조합으로 최적화된 정보 제공"""
    
    def __init__(self, db_path: str, project_path: str = "./project"):
        self.db_path = db_path
        self.file_reader = DynamicFileReader(project_path)
    
    def get_component_full_info(self, component_name: str) -> Dict:
        """메타DB에서 기본 정보 + 동적으로 상세 정보 조합"""
        # 1. 메타DB에서 기본 정보 조회
        # 2. 파일에서 상세 정보 동적 조회
        # 3. 결합하여 반환
        pass
    
    def search_with_context(self, query: str) -> List[Dict]:
        """검색 결과에 컨텍스트 정보 추가"""
        # 1. 메타DB에서 검색
        # 2. 검색 결과에 대해 동적 컨텍스트 정보 추가
        pass