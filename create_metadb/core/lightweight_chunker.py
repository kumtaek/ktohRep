"""
경량 청킹 시스템

소스 코드를 의미 단위로 청킹하여 과도한 세분화를 방지합니다.
"""

import re
import logging
from typing import Dict, List, Any
from pathlib import Path

class LightweightChunker:
    """경량 청킹 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"LightweightChunker")
        
        # 청킹 규칙 정의
        self.chunking_rules = {
            'java': {
                'class_pattern': r'public\s+class\s+(\w+).*?\{',
                'method_pattern': r'(public|private|protected)\s+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{',
                'import_pattern': r'import\s+([^;]+);'
            },
            'jsp': {
                'page_pattern': r'<%@\s+page[^%]*%>',
                'include_pattern': r'<%@\s+include[^%]*%>',
                'taglib_pattern': r'<%@\s+taglib[^%]*%>'
            },
            'xml': {
                'mapper_pattern': r'<mapper[^>]*>',
                'resultmap_pattern': r'<resultMap[^>]*>',
                'sql_pattern': r'<select[^>]*>|<insert[^>]*>|<update[^>]*>|<delete[^>]*>'
            },
            'sql': {
                'statement_pattern': r'(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s+.*?;',
                'function_pattern': r'CREATE\s+(OR\s+REPLACE\s+)?FUNCTION\s+(\w+)',
                'procedure_pattern': r'CREATE\s+(OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)'
            }
        }
    
    def chunk_file(self, file_path: str) -> List[Dict]:
        """파일을 청킹"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.java':
                return self._chunk_java_file(file_path, content)
            elif file_extension == '.jsp':
                return self._chunk_jsp_file(file_path, content)
            elif file_extension == '.xml':
                return self._chunk_xml_file(file_path, content)
            elif file_extension == '.sql':
                return self._chunk_sql_file(file_path, content)
            else:
                return self._chunk_generic_file(file_path, content)
                
        except Exception as e:
            self.logger.error(f"파일 청킹 실패 {file_path}: {e}")
            return []
    
    def _chunk_java_file(self, file_path: str, content: str) -> List[Dict]:
        """Java 파일 청킹"""
        chunks = []
        
        # 1. 클래스 청크
        class_matches = re.finditer(self.chunking_rules['java']['class_pattern'], content, re.DOTALL)
        for match in class_matches:
            class_name = match.group(1)
            class_start = match.start()
            
            # 클래스 끝 찾기 (중괄호 매칭)
            class_end = self._find_matching_brace(content, class_start)
            
            if class_end > class_start:
                class_content = content[class_start:class_end]
                
                chunks.append({
                    'id': f"{Path(file_path).stem}_{class_name}",
                    'type': 'class',
                    'name': class_name,
                    'content': class_content,
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'file_type': 'java',
                    'package_name': self._extract_package_name(content),
                    'class_name': class_name,
                    'start_line': content[:class_start].count('\n') + 1,
                    'end_line': content[:class_end].count('\n') + 1,
                    'hash_value': self._calculate_content_hash(class_content)
                })
        
        # 2. 메서드 청크 (클래스 내부의 메서드들)
        method_matches = re.finditer(self.chunking_rules['java']['method_pattern'], content, re.DOTALL)
        for match in method_matches:
            method_name = match.group(2)
            method_start = match.start()
            
            # 메서드 끝 찾기
            method_end = self._find_matching_brace(content, method_start)
            
            if method_end > method_start:
                method_content = content[method_start:method_end]
                
                chunks.append({
                    'id': f"{Path(file_path).stem}_{method_name}",
                    'type': 'method',
                    'name': method_name,
                    'content': method_content,
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'file_type': 'java',
                    'package_name': self._extract_package_name(content),
                    'class_name': self._extract_class_name(content),
                    'start_line': content[:method_start].count('\n') + 1,
                    'end_line': content[:method_end].count('\n') + 1,
                    'hash_value': self._calculate_content_hash(method_content)
                })
        
        return chunks
    
    def _chunk_jsp_file(self, file_path: str, content: str) -> List[Dict]:
        """JSP 파일 청킹"""
        chunks = []
        
        # JSP 파일을 하나의 청크로 처리 (과도한 세분화 방지)
        chunks.append({
            'id': f"{Path(file_path).stem}_page",
            'type': 'jsp_page',
            'name': Path(file_path).stem,
            'content': content,
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'file_type': 'jsp',
            'package_name': '',
            'class_name': '',
            'start_line': 1,
            'end_line': len(content.split('\n')),
            'hash_value': self._calculate_content_hash(content)
        })
        
        return chunks
    
    def _chunk_xml_file(self, file_path: str, content: str) -> List[Dict]:
        """XML 파일 청킹 (MyBatis 등)"""
        chunks = []
        
        # MyBatis Mapper 파일인 경우
        if 'mapper' in content.lower():
            # SQL 단위별로 청킹
            sql_patterns = [
                r'<select[^>]*id=["\'](\w+)["\'][^>]*>(.*?)</select>',
                r'<insert[^>]*id=["\'](\w+)["\'][^>]*>(.*?)</insert>',
                r'<update[^>]*id=["\'](\w+)["\'][^>]*>(.*?)</update>',
                r'<delete[^>]*id=["\'](\w+)["\'][^>]*>(.*?)</delete>'
            ]
            
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    sql_id = match.group(1)
                    sql_content = match.group(2)
                    
                    chunks.append({
                        'id': f"{Path(file_path).stem}_{sql_id}",
                        'type': 'sql_unit',
                        'name': sql_id,
                        'content': sql_content,
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'file_type': 'xml',
                        'package_name': '',
                        'class_name': '',
                        'start_line': content[:match.start()].count('\n') + 1,
                        'end_line': content[:match.end()].count('\n') + 1,
                        'hash_value': self._calculate_content_hash(sql_content)
                    })
        else:
            # 일반 XML 파일은 하나의 청크로 처리
            chunks.append({
                'id': f"{Path(file_path).stem}_xml",
                'type': 'xml_document',
                'name': Path(file_path).stem,
                'content': content,
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_type': 'xml',
                'package_name': '',
                'class_name': '',
                'start_line': 1,
                'end_line': len(content.split('\n')),
                'hash_value': self._calculate_content_hash(content)
            })
        
        return chunks
    
    def _chunk_sql_file(self, file_path: str, content: str) -> List[Dict]:
        """SQL 파일 청킹"""
        chunks = []
        
        # SQL 문장별로 청킹
        sql_statements = re.finditer(self.chunking_rules['sql']['statement_pattern'], content, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(sql_statements):
            sql_content = match.group(0)
            sql_type = match.group(1).upper()
            
            chunks.append({
                'id': f"{Path(file_path).stem}_sql_{i+1}",
                'type': 'sql_unit',
                'name': f"{sql_type}_{i+1}",
                'content': sql_content,
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_type': 'sql',
                'package_name': '',
                'class_name': '',
                'start_line': content[:match.start()].count('\n') + 1,
                'end_line': content[:match.end()].count('\n') + 1,
                'hash_value': self._calculate_content_hash(sql_content)
            })
        
        return chunks
    
    def _chunk_generic_file(self, file_path: str, content: str) -> List[Dict]:
        """일반 파일 청킹"""
        return [{
            'id': f"{Path(file_path).stem}_file",
            'type': 'file',
            'name': Path(file_path).stem,
            'content': content,
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'file_type': Path(file_path).suffix[1:],
            'package_name': '',
            'class_name': '',
            'start_line': 1,
            'end_line': len(content.split('\n')),
            'hash_value': self._calculate_content_hash(content)
        }]
    
    def _find_matching_brace(self, content: str, start_pos: int) -> int:
        """중괄호 매칭하여 끝 위치 찾기"""
        brace_count = 0
        pos = start_pos
        
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return pos + 1
            pos += 1
        
        return len(content)
    
    def _extract_package_name(self, content: str) -> str:
        """패키지명 추출"""
        package_match = re.search(r'package\s+([^;]+);', content)
        return package_match.group(1) if package_match else ''
    
    def _extract_class_name(self, content: str) -> str:
        """클래스명 추출"""
        class_match = re.search(r'public\s+class\s+(\w+)', content)
        return class_match.group(1) if class_match else ''
    
    def _calculate_content_hash(self, content: str) -> str:
        """내용 해시값 계산"""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
