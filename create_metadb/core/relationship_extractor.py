"""
관계 추출기

소스 코드에서 핵심 관계(calls, dependency, import, foreign_key, join)를 추출합니다.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from create_metadb.parsers.java.java_parser import JavaParser
from create_metadb.parsers.sql.sql_parser import SqlParser
from create_metadb.parsers.jsp.jsp_parser import JspParser

class RelationshipExtractor:
    """관계 추출기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"RelationshipExtractor")
        
        # 파서 초기화
        self.java_parser = JavaParser()
        self.sql_parser = SqlParser()
        self.jsp_parser = JspParser()
        
        # 관계 타입 정의
        self.relationship_types = {
            'calls': '메서드 호출 관계',
            'dependency': '클래스 의존성 관계', 
            'import': '패키지 import 관계',
            'foreign_key': 'DB 테이블 관계',
            'join': 'SQL 조인 관계',
            'uses_service': 'Service 사용 관계',
            'uses_repository': 'Repository 사용 관계'
        }
    
    def extract_relationships(self, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """파일에서 관계 추출"""
        relationships = []
        
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.java':
                relationships.extend(self._extract_java_relationships(file_path, chunks))
            elif file_extension == '.sql':
                relationships.extend(self._extract_sql_relationships(file_path, chunks))
            elif file_extension == '.jsp':
                relationships.extend(self._extract_jsp_relationships(file_path, chunks))
            elif file_extension == '.xml':
                relationships.extend(self._extract_xml_relationships(file_path, chunks))
            
            self.logger.info(f"관계 추출 완료 {file_path}: {len(relationships)}개")
            
        except Exception as e:
            self.logger.error(f"관계 추출 실패 {file_path}: {e}")
        
        return relationships
    
    def _extract_java_relationships(self, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """Java 파일에서 관계 추출"""
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Import 관계 추출
            import_relationships = self._extract_import_relationships(content, file_path)
            relationships.extend(import_relationships)
            
            # 2. 메서드 호출 관계 추출
            call_relationships = self._extract_method_call_relationships(content, file_path, chunks)
            relationships.extend(call_relationships)
            
            # 3. 의존성 관계 추출 (Spring, MyBatis 등)
            dependency_relationships = self._extract_dependency_relationships(content, file_path)
            relationships.extend(dependency_relationships)
            
            # 4. Service/Repository 사용 관계 추출
            service_relationships = self._extract_service_relationships(content, file_path)
            relationships.extend(service_relationships)
            
        except Exception as e:
            self.logger.error(f"Java 관계 추출 실패 {file_path}: {e}")
        
        return relationships
    
    def _extract_import_relationships(self, content: str, file_path: str) -> List[Dict]:
        """Import 관계 추출"""
        relationships = []
        
        # Java import 패턴
        import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*);'
        imports = re.findall(import_pattern, content)
        
        for import_path in imports:
            # 패키지명에서 클래스명 추출
            class_name = import_path.split('.')[-1]
            
            relationships.append({
                'source_type': 'file',
                'source_name': Path(file_path).name,
                'source_path': file_path,
                'target_type': 'class',
                'target_name': class_name,
                'target_path': import_path,
                'relationship_type': 'import',
                'confidence': 1.0
            })
        
        return relationships
    
    def _extract_method_call_relationships(self, content: str, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """메서드 호출 관계 추출"""
        relationships = []
        
        # 메서드 호출 패턴들
        call_patterns = [
            r'(\w+)\.(\w+)\s*\(',  # object.method(
            r'(\w+)\s*\(',         # method(
            r'this\.(\w+)\s*\(',   # this.method(
            r'super\.(\w+)\s*\('   # super.method(
        ]
        
        for pattern in call_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) >= 2:
                    object_name = match.group(1)
                    method_name = match.group(2)
                else:
                    method_name = match.group(1)
                    object_name = None
                
                # 청크에서 해당 메서드 찾기
                target_chunk = self._find_method_chunk(method_name, chunks)
                if target_chunk:
                    relationships.append({
                        'source_type': 'file',
                        'source_name': Path(file_path).name,
                        'source_path': file_path,
                        'target_type': 'method',
                        'target_name': method_name,
                        'target_path': target_chunk.get('file_path', ''),
                        'relationship_type': 'calls',
                        'confidence': 0.8
                    })
        
        return relationships
    
    def _extract_dependency_relationships(self, content: str, file_path: str) -> List[Dict]:
        """의존성 관계 추출 (Spring, MyBatis 등)"""
        relationships = []
        
        # Spring @Autowired 패턴
        autowired_pattern = r'@Autowired\s+private\s+(\w+)\s+(\w+);'
        autowired_matches = re.finditer(autowired_pattern, content)
        
        for match in autowired_matches:
            class_name = match.group(1)
            field_name = match.group(2)
            
            relationships.append({
                'source_type': 'class',
                'source_name': Path(file_path).stem,
                'source_path': file_path,
                'target_type': 'class',
                'target_name': class_name,
                'target_path': '',
                'relationship_type': 'dependency',
                'confidence': 0.9
            })
        
        # MyBatis Mapper 패턴
        mapper_pattern = r'(\w+Mapper)\s+(\w+);'
        mapper_matches = re.finditer(mapper_pattern, content)
        
        for match in mapper_matches:
            mapper_name = match.group(1)
            field_name = match.group(2)
            
            relationships.append({
                'source_type': 'class',
                'source_name': Path(file_path).stem,
                'source_path': file_path,
                'target_type': 'mapper',
                'target_name': mapper_name,
                'target_path': '',
                'relationship_type': 'uses_repository',
                'confidence': 0.9
            })
        
        return relationships
    
    def _extract_service_relationships(self, content: str, file_path: str) -> List[Dict]:
        """Service 사용 관계 추출"""
        relationships = []
        
        # Service 사용 패턴
        service_pattern = r'(\w+Service)\s+(\w+);'
        service_matches = re.finditer(service_pattern, content)
        
        for match in service_matches:
            service_name = match.group(1)
            field_name = match.group(2)
            
            relationships.append({
                'source_type': 'class',
                'source_name': Path(file_path).stem,
                'source_path': file_path,
                'target_type': 'service',
                'target_name': service_name,
                'target_path': '',
                'relationship_type': 'uses_service',
                'confidence': 0.9
            })
        
        return relationships
    
    def _extract_sql_relationships(self, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """SQL 파일에서 관계 추출"""
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # SQL 조인 관계 추출
            join_relationships = self._extract_join_relationships(content, file_path)
            relationships.extend(join_relationships)
            
            # 외래키 관계 추출
            fk_relationships = self._extract_foreign_key_relationships(content, file_path)
            relationships.extend(fk_relationships)
            
        except Exception as e:
            self.logger.error(f"SQL 관계 추출 실패 {file_path}: {e}")
        
        return relationships
    
    def _extract_join_relationships(self, content: str, file_path: str) -> List[Dict]:
        """SQL 조인 관계 추출"""
        relationships = []
        
        # JOIN 패턴들
        join_patterns = [
            r'JOIN\s+(\w+)\s+ON\s+([^)]+)',
            r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^)]+)',
            r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^)]+)'
        ]
        
        for pattern in join_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                join_condition = match.group(2)
                
                relationships.append({
                    'source_type': 'sql_unit',
                    'source_name': Path(file_path).stem,
                    'source_path': file_path,
                    'target_type': 'table',
                    'target_name': table_name,
                    'target_path': '',
                    'relationship_type': 'join',
                    'confidence': 0.9,
                    'metadata': {
                        'join_condition': join_condition,
                        'join_type': 'inner' if 'INNER' in pattern else 'left' if 'LEFT' in pattern else 'right'
                    }
                })
        
        return relationships
    
    def _extract_foreign_key_relationships(self, content: str, file_path: str) -> List[Dict]:
        """외래키 관계 추출"""
        relationships = []
        
        # FOREIGN KEY 패턴
        fk_pattern = r'FOREIGN\s+KEY\s+\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)'
        fk_matches = re.finditer(fk_pattern, content, re.IGNORECASE)
        
        for match in fk_matches:
            fk_column = match.group(1)
            ref_table = match.group(2)
            ref_column = match.group(3)
            
            relationships.append({
                'source_type': 'table',
                'source_name': Path(file_path).stem,
                'source_path': file_path,
                'target_type': 'table',
                'target_name': ref_table,
                'target_path': '',
                'relationship_type': 'foreign_key',
                'confidence': 1.0,
                'metadata': {
                    'fk_column': fk_column,
                    'ref_column': ref_column
                }
            })
        
        return relationships
    
    def _extract_jsp_relationships(self, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """JSP 파일에서 관계 추출"""
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # JSP include 관계 추출
            include_pattern = r'<%@\s+include\s+file=["\']([^"\']+)["\']\s*%>'
            include_matches = re.finditer(include_pattern, content)
            
            for match in include_matches:
                include_file = match.group(1)
                
                relationships.append({
                    'source_type': 'file',
                    'source_name': Path(file_path).name,
                    'source_path': file_path,
                    'target_type': 'file',
                    'target_name': Path(include_file).name,
                    'target_path': include_file,
                    'relationship_type': 'include',
                    'confidence': 0.9
                })
            
        except Exception as e:
            self.logger.error(f"JSP 관계 추출 실패 {file_path}: {e}")
        
        return relationships
    
    def _extract_xml_relationships(self, file_path: str, chunks: List[Dict]) -> List[Dict]:
        """XML 파일에서 관계 추출 (MyBatis 등)"""
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # MyBatis resultMap 참조 관계
            resultmap_pattern = r'resultMap=["\']([^"\']+)["\']'
            resultmap_matches = re.finditer(resultmap_pattern, content)
            
            for match in resultmap_matches:
                resultmap_name = match.group(1)
                
                relationships.append({
                    'source_type': 'xml',
                    'source_name': Path(file_path).stem,
                    'source_path': file_path,
                    'target_type': 'resultmap',
                    'target_name': resultmap_name,
                    'target_path': '',
                    'relationship_type': 'references',
                    'confidence': 0.8
                })
            
        except Exception as e:
            self.logger.error(f"XML 관계 추출 실패 {file_path}: {e}")
        
        return relationships
    
    def _find_method_chunk(self, method_name: str, chunks: List[Dict]) -> Optional[Dict]:
        """청크에서 메서드 찾기"""
        for chunk in chunks:
            if chunk.get('type') == 'method' and chunk.get('name') == method_name:
                return chunk
        return None
