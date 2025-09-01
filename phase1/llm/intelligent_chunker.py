"""
지능적 코드 청킹 시스템
파일을 의미있는 단위(클래스, 메서드, 쿼리)로 분할하여 LLM 요약 효율성 극대화
"""
import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CodeChunk:
    """코드 청크 정보"""
    chunk_type: str  # 'class', 'method', 'query', 'config', 'import'
    name: str        # 청크 식별자 (클래스명, 메서드명, 쿼리ID 등)
    content: str     # 실제 코드 내용
    start_line: int  # 시작 라인 번호
    end_line: int    # 끝 라인 번호
    context: str     # 주변 컨텍스트 정보
    metadata: Dict   # 추가 메타데이터

class IntelligentChunker:
    """의미있는 단위로 코드를 청킹하는 클래스"""
    
    def __init__(self):
        self.java_patterns = {
            'class': r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)',
            'interface': r'(?:public\s+|private\s+|protected\s+)?interface\s+(\w+)', 
            'method': r'(?:public\s+|private\s+|protected\s+|static\s+)*\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{',
            'annotation': r'@(\w+)'
        }
        
        self.jsp_patterns = {
            'scriptlet': r'<%([^%]|%(?!>))*%>',
            'expression': r'<%=([^%]|%(?!>))*%>',
            'directive': r'<%@([^%]|%(?!>))*%>',
            'jstl': r'<c:(\w+)[^>]*>.*?</c:\1>',
            'html_block': r'<(\w+)[^>]*>.*?</\1>'
        }
        
        self.xml_patterns = {
            'mybatis_select': r'<select[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</select>',
            'mybatis_insert': r'<insert[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</insert>',
            'mybatis_update': r'<update[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</update>',
            'mybatis_delete': r'<delete[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</delete>',
            'resultmap': r'<resultMap[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</resultMap>'
        }

    def chunk_java_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """Java 파일을 의미있는 단위로 청킹"""
        chunks = []
        lines = content.split('\n')
        
        # 1. 패키지와 임포트 블록
        import_block = self._extract_import_block(lines)
        if import_block:
            chunks.append(CodeChunk(
                chunk_type='import',
                name='imports',
                content=import_block,
                start_line=1,
                end_line=len(import_block.split('\n')),
                context=f"파일: {file_path}",
                metadata={'file_path': file_path}
            ))
        
        # 2. 클래스별 청킹
        class_chunks = self._extract_java_classes(content, file_path)
        chunks.extend(class_chunks)
        
        return chunks
    
    def chunk_jsp_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """JSP 파일을 의미있는 단위로 청킹"""
        chunks = []
        
        # 1. JSP 지시어 블록
        directives = re.findall(r'<%@([^%]|%(?!>))*%>', content, re.DOTALL)
        if directives:
            chunks.append(CodeChunk(
                chunk_type='directive',
                name='jsp_directives',
                content='\n'.join(directives),
                start_line=1,
                end_line=len(directives),
                context=f"JSP 파일: {file_path}",
                metadata={'file_path': file_path, 'count': len(directives)}
            ))
        
        # 2. 스크립틀릿 블록들
        scriptlet_chunks = self._extract_jsp_scriptlets(content, file_path)
        chunks.extend(scriptlet_chunks)
        
        # 3. JSTL 태그 블록들  
        jstl_chunks = self._extract_jstl_blocks(content, file_path)
        chunks.extend(jstl_chunks)
        
        return chunks
    
    def chunk_xml_file(self, content: str, file_path: str) -> List[CodeChunk]:
        """XML 파일을 의미있는 단위로 청킹 (주로 MyBatis)"""
        chunks = []
        
        # MyBatis 쿼리별로 청킹
        for query_type in ['select', 'insert', 'update', 'delete']:
            pattern = rf'<{query_type}[^>]*id\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</{query_type}>'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for query_id, query_content in matches:
                chunks.append(CodeChunk(
                    chunk_type=f'mybatis_{query_type}',
                    name=query_id,
                    content=f'<{query_type} id="{query_id}">\n{query_content.strip()}\n</{query_type}>',
                    start_line=content.find(f'id="{query_id}"') // len(content.split('\n')[0]) + 1,
                    end_line=0,  # TODO: 정확한 라인 계산
                    context=f"MyBatis 파일: {file_path}",
                    metadata={'query_type': query_type, 'query_id': query_id, 'file_path': file_path}
                ))
        
        return chunks
    
    def _extract_import_block(self, lines: List[str]) -> str:
        """Java 파일에서 import 블록 추출"""
        import_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('package ') or stripped.startswith('import ') or not stripped:
                import_lines.append(line)
            else:
                break
        return '\n'.join(import_lines) if import_lines else ""
    
    def _extract_java_classes(self, content: str, file_path: str) -> List[CodeChunk]:
        """Java 파일에서 클래스별로 청킹"""
        chunks = []
        lines = content.split('\n')
        
        # 클래스 정의 찾기
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(?:final\s+)?(?:class|interface)\s+(\w+)'
        
        current_class = None
        current_class_start = 0
        brace_count = 0
        in_class = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 클래스 정의 시작
            class_match = re.search(class_pattern, line)
            if class_match:
                current_class = class_match.group(1)
                current_class_start = i
                in_class = True
                brace_count = 0
            
            # 중괄호 카운팅으로 클래스 범위 추적
            if in_class:
                brace_count += line.count('{') - line.count('}')
                
                # 클래스 끝 (중괄호가 0이 되면)
                if brace_count == 0 and current_class:
                    class_content = '\n'.join(lines[current_class_start:i+1])
                    
                    # 클래스 내 메서드들도 개별 청킹
                    method_chunks = self._extract_java_methods(class_content, current_class, current_class_start, file_path)
                    chunks.extend(method_chunks)
                    
                    # 클래스 전체도 하나의 청크로 추가 (메서드 시그니처만)
                    class_summary = self._create_class_summary(class_content, current_class)
                    chunks.append(CodeChunk(
                        chunk_type='class',
                        name=current_class,
                        content=class_summary,
                        start_line=current_class_start + 1,
                        end_line=i + 1,
                        context=f"Java 파일: {file_path}",
                        metadata={'class_name': current_class, 'file_path': file_path}
                    ))
                    
                    in_class = False
                    current_class = None
        
        return chunks
    
    def _extract_java_methods(self, class_content: str, class_name: str, class_start_line: int, file_path: str) -> List[CodeChunk]:
        """클래스 내 메서드들을 개별 청킹"""
        chunks = []
        lines = class_content.split('\n')
        
        method_pattern = r'(?:public\s+|private\s+|protected\s+|static\s+)*\s*(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        
        current_method = None
        method_start = 0
        brace_count = 0
        in_method = False
        
        for i, line in enumerate(lines):
            method_match = re.search(method_pattern, line)
            if method_match and not line.strip().startswith('//'):
                current_method = method_match.group(1)
                method_start = i
                in_method = True
                brace_count = 0
            
            if in_method:
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0 and current_method:
                    method_content = '\n'.join(lines[method_start:i+1])
                    
                    chunks.append(CodeChunk(
                        chunk_type='method',
                        name=f"{class_name}.{current_method}",
                        content=method_content,
                        start_line=class_start_line + method_start + 1,
                        end_line=class_start_line + i + 1,
                        context=f"클래스: {class_name}, 파일: {file_path}",
                        metadata={
                            'class_name': class_name,
                            'method_name': current_method,
                            'file_path': file_path
                        }
                    ))
                    
                    in_method = False
                    current_method = None
        
        return chunks
    
    def _extract_jsp_scriptlets(self, content: str, file_path: str) -> List[CodeChunk]:
        """JSP 파일에서 스크립틀릿 블록들 추출"""
        chunks = []
        scriptlets = re.finditer(r'<%([^%@=](?:[^%]|%(?!>))*?)%>', content, re.DOTALL)
        
        for i, match in enumerate(scriptlets):
            scriptlet_content = match.group(0)
            chunks.append(CodeChunk(
                chunk_type='scriptlet',
                name=f'scriptlet_{i+1}',
                content=scriptlet_content,
                start_line=content[:match.start()].count('\n') + 1,
                end_line=content[:match.end()].count('\n') + 1,
                context=f"JSP 파일: {file_path}",
                metadata={'file_path': file_path, 'index': i+1}
            ))
        
        return chunks
    
    def _extract_jstl_blocks(self, content: str, file_path: str) -> List[CodeChunk]:
        """JSP 파일에서 JSTL 태그 블록들 추출"""
        chunks = []
        jstl_pattern = r'<c:(\w+)[^>]*>(.*?)</c:\1>'
        jstl_blocks = re.finditer(jstl_pattern, content, re.DOTALL)
        
        for i, match in enumerate(jstl_blocks):
            tag_name = match.group(1)
            block_content = match.group(0)
            
            chunks.append(CodeChunk(
                chunk_type='jstl',
                name=f'jstl_{tag_name}_{i+1}',
                content=block_content,
                start_line=content[:match.start()].count('\n') + 1,
                end_line=content[:match.end()].count('\n') + 1,
                context=f"JSP 파일: {file_path}",
                metadata={'tag_name': tag_name, 'file_path': file_path, 'index': i+1}
            ))
        
        return chunks
    
    def _create_class_summary(self, class_content: str, class_name: str) -> str:
        """클래스의 구조적 요약 생성 (메서드 시그니처만)"""
        lines = class_content.split('\n')
        summary_lines = []
        
        # 클래스 선언부
        for line in lines:
            if 'class ' + class_name in line:
                summary_lines.append(line.strip())
                break
        
        # 필드 선언들
        field_pattern = r'(?:private|public|protected)\s+(?:static\s+)?(?:final\s+)?\w+\s+\w+;'
        for line in lines:
            if re.search(field_pattern, line.strip()):
                summary_lines.append('  ' + line.strip())
        
        # 메서드 시그니처들
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)'
        for line in lines:
            method_match = re.search(method_pattern, line.strip())
            if method_match:
                summary_lines.append('  ' + line.strip() + ' { ... }')
        
        return '\n'.join(summary_lines)
    
    def chunk_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """파일 확장자에 따라 적절한 청킹 수행"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.java':
            return self.chunk_java_file(content, file_path)
        elif file_extension == '.jsp':
            return self.chunk_jsp_file(content, file_path)
        elif file_extension == '.xml':
            return self.chunk_xml_file(content, file_path)
        else:
            # 기본 청킹 (라인 기반)
            return self._chunk_by_lines(content, file_path)
    
    def _chunk_by_lines(self, content: str, file_path: str, max_lines: int = 50) -> List[CodeChunk]:
        """라인 기반 기본 청킹"""
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), max_lines):
            chunk_lines = lines[i:i+max_lines]
            chunks.append(CodeChunk(
                chunk_type='block',
                name=f'block_{i//max_lines + 1}',
                content='\n'.join(chunk_lines),
                start_line=i + 1,
                end_line=min(i + max_lines, len(lines)),
                context=f"파일: {file_path}",
                metadata={'file_path': file_path}
            ))
        
        return chunks

class ChunkBasedSummarizer:
    """청킹 기반 LLM 요약 시스템"""
    
    def __init__(self, chunker: IntelligentChunker):
        self.chunker = chunker
    
    def summarize_file_by_chunks(self, file_path: str, content: str) -> Dict[str, str]:
        """파일을 청킹하여 각 청크별로 요약 생성"""
        chunks = self.chunker.chunk_file(file_path, content)
        summaries = {}
        
        for chunk in chunks:
            summary = self._summarize_chunk(chunk)
            if summary:
                summaries[f"{chunk.chunk_type}:{chunk.name}"] = summary
        
        return summaries
    
    def _summarize_chunk(self, chunk: CodeChunk) -> Optional[str]:
        """개별 청크에 대한 LLM 요약 생성"""
        try:
            # 청크 타입별 맞춤형 프롬프트
            if chunk.chunk_type == 'method':
                prompt = f"""다음 Java 메서드를 분석하고 기능을 요약해주세요.

메서드명: {chunk.name}
컨텍스트: {chunk.context}

코드:
{chunk.content}

이 메서드의 목적과 핵심 기능을 1-2문장으로 요약해주세요."""

            elif chunk.chunk_type == 'mybatis_select':
                prompt = f"""다음 MyBatis SELECT 쿼리를 분석하고 기능을 요약해주세요.

쿼리 ID: {chunk.name}
컨텍스트: {chunk.context}

쿼리:
{chunk.content}

이 쿼리가 어떤 데이터를 조회하는지 1-2문장으로 요약해주세요."""

            elif chunk.chunk_type == 'class':
                prompt = f"""다음 Java 클래스의 구조를 분석하고 역할을 요약해주세요.

클래스명: {chunk.name}
컨텍스트: {chunk.context}

클래스 구조:
{chunk.content}

이 클래스의 책임과 주요 기능을 1-2문장으로 요약해주세요."""

            else:
                prompt = f"""다음 코드 블록을 분석하고 기능을 요약해주세요.

타입: {chunk.chunk_type}
이름: {chunk.name}
컨텍스트: {chunk.context}

코드:
{chunk.content[:1000]}...

이 코드 블록의 목적과 기능을 1-2문장으로 요약해주세요."""
            
            # 실제 LLM 호출은 CodeSummarizer에서 처리
            # 이 클래스는 청킹 로직만 담당
            return None
            
        except Exception as e:
            logger.error(f"청크 요약 실패 {chunk.name}: {e}")
            return None
    
    def create_enhanced_table_comment(self, table_name: str, chunk_summaries: Dict[str, str]) -> str:
        """청킹 요약 정보를 활용한 지능적 테이블 커멘트 생성"""
        relevant_summaries = []
        
        # 테이블명과 관련된 청크들 찾기
        for chunk_key, summary in chunk_summaries.items():
            if table_name.lower() in summary.lower() or table_name.lower() in chunk_key.lower():
                relevant_summaries.append(f"- {chunk_key}: {summary}")
        
        context_info = '\n'.join(relevant_summaries) if relevant_summaries else "관련 코드 정보 없음"
        
        enhanced_prompt = f"""다음 테이블에 대한 상세하고 유용한 커멘트를 생성해주세요.

테이블명: {table_name}

관련 코드 분석 정보:
{context_info}

비즈니스 목적, 사용 패턴, 데이터 특성을 고려하여 개발자가 이해하기 쉬운 한글 커멘트를 작성해주세요."""

        # 실제 LLM 호출은 CodeSummarizer에서 처리
        return f"{table_name} 테이블 - 청킹 기반 지능형 분석 준비 완료"