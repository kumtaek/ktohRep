"""
최적화된 메타데이터 엔진
- 필수 정보만 메타DB에 저장
- 상세 정보는 ./project 폴더에서 동적 조회
- 하이브리드 방식으로 성능 최적화
"""
import sqlite3
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import hashlib
from datetime import datetime

from utils.dynamic_file_reader import DynamicFileReader


class OptimizedMetadataEngine:
    """최적화된 메타데이터 엔진"""
    
    def __init__(self, db_path: str = "metadata_optimized.db", project_path: str = "./project"):
        self.db_path = db_path
        self.project_path = Path(project_path)
        self.file_reader = DynamicFileReader(project_path)
        self.init_database()
    
    def init_database(self):
        """최적화된 스키마로 데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            # 스키마 파일 읽기
            schema_path = Path(__file__).parent.parent / "database" / "optimized_schema.sql"
            if schema_path.exists():
                schema_sql = schema_path.read_text(encoding='utf-8')
                conn.executescript(schema_sql)
            conn.commit()
    
    def create_project(self, project_name: str, project_path: str) -> int:
        """프로젝트 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (project_name, project_path, last_analysis)
                VALUES (?, ?, ?)
            """, (project_name, project_path, datetime.now().isoformat()))
            project_id = cursor.lastrowid
            conn.commit()
            return project_id
    
    def add_file_index(self, project_id: int, file_path: str, file_type: str) -> int:
        """파일 인덱스 추가 (기본 정보만)"""
        file_name = Path(file_path).name
        file_hash = self._calculate_file_hash(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (project_id, file_path, file_name, file_type, hash_value)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, file_path, file_name, file_type, file_hash))
            file_id = cursor.lastrowid
            conn.commit()
            return file_id
    
    def add_component(self, project_id: int, file_id: int, component_name: str, 
                     component_type: str, line_start: int = None, line_end: int = None,
                     parent_component_id: int = None) -> int:
        """컴포넌트 추가 (위치 정보 포함)"""
        component_hash = self._calculate_component_hash(component_name, component_type)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO components 
                (project_id, file_id, component_name, component_type, line_start, line_end, parent_component_id, hash_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, file_id, component_name, component_type, line_start, line_end, parent_component_id, component_hash))
            component_id = cursor.lastrowid
            conn.commit()
            return component_id
    
    def add_relationship(self, project_id: int, src_component_id: int, dst_component_id: int,
                        relationship_type: str, confidence: float = 1.0):
        """관계 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO relationships (project_id, src_component_id, dst_component_id, relationship_type, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, src_component_id, dst_component_id, relationship_type, confidence))
            conn.commit()
    
    def add_business_tag(self, project_id: int, component_id: int, 
                        domain: str = None, layer: str = None, priority: int = 3):
        """비즈니스 태그 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO business_tags (project_id, component_id, domain, layer, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, component_id, domain, layer, priority))
            conn.commit()
    
    # 검색 메서드들
    def search_components(self, query: str, component_type: str = None) -> List[Dict]:
        """컴포넌트 검색 (메타DB 활용)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_clause = "WHERE component_name LIKE ?"
            params = [f"%{query}%"]
            
            if component_type:
                where_clause += " AND component_type = ?"
                params.append(component_type)
            
            cursor.execute(f"""
                SELECT * FROM v_component_details {where_clause}
                ORDER BY priority DESC, component_name
            """, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'component_id': row[0],
                    'component_name': row[1],
                    'component_type': row[2],
                    'file_path': row[3],
                    'file_name': row[4],
                    'line_start': row[5],
                    'line_end': row[6],
                    'domain': row[7],
                    'layer': row[8],
                    'priority': row[9]
                })
            
            return results
    
    def get_component_relationships(self, component_name: str) -> List[Dict]:
        """컴포넌트 관계 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM v_relationships 
                WHERE src_name = ? OR dst_name = ?
                ORDER BY relationship_type, confidence DESC
            """, (component_name, component_name))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append({
                    'relationship_id': row[0],
                    'relationship_type': row[1],
                    'src_name': row[2],
                    'src_type': row[3],
                    'src_file': row[4],
                    'dst_name': row[5],
                    'dst_type': row[6],
                    'dst_file': row[7],
                    'confidence': row[8]
                })
            
            return relationships
    
    # 하이브리드 조회 메서드들 (메타DB + 동적 파일 읽기)
    def get_component_full_details(self, component_name: str) -> Dict:
        """컴포넌트 전체 상세 정보 (하이브리드)"""
        # 1. 메타DB에서 기본 정보
        components = self.search_components(component_name)
        if not components:
            return {}
        
        component = components[0]
        
        # 2. 동적으로 파일에서 상세 정보
        file_details = self.file_reader.get_java_class_details(component['file_path'])
        
        # 3. 컨텍스트 정보
        context = self.file_reader.get_component_context(
            component['file_path'], 
            component_name, 
            context_lines=3
        )
        
        # 4. 관계 정보
        relationships = self.get_component_relationships(component_name)
        
        return {
            'basic_info': component,
            'file_details': file_details,
            'context': context,
            'relationships': relationships,
            'source': 'hybrid'  # 메타DB + 동적 조회
        }
    
    def search_with_context(self, query: str, include_content: bool = False) -> List[Dict]:
        """컨텍스트 포함 검색"""
        # 1. 메타DB에서 기본 검색
        base_results = self.search_components(query)
        
        enhanced_results = []
        for result in base_results:
            enhanced_result = result.copy()
            
            # 2. 필요시 파일 내용 추가
            if include_content:
                content = self.file_reader.get_file_content(result['file_path'])
                enhanced_result['file_content'] = content
            
            # 3. 컨텍스트 정보 추가
            context = self.file_reader.get_component_context(
                result['file_path'],
                result['component_name'],
                context_lines=2
            )
            enhanced_result['context'] = context
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def analyze_component_usage(self, component_name: str) -> Dict:
        """컴포넌트 사용 분석 (동적)"""
        # 프로젝트 전체에서 해당 컴포넌트 사용 패턴 검색
        usage_patterns = self.file_reader.search_code_patterns(
            component_name, 
            ['.java', '.jsp']
        )
        
        # 메타DB에서 관계 정보
        relationships = self.get_component_relationships(component_name)
        
        return {
            'component_name': component_name,
            'usage_patterns': usage_patterns,
            'formal_relationships': relationships,
            'usage_count': len(usage_patterns),
            'relationship_count': len(relationships)
        }
    
    # 유틸리티 메서드들
    def _calculate_file_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        try:
            content = self.file_reader.get_file_content(file_path)
            if content:
                return hashlib.sha256(content.encode()).hexdigest()
            return ""
        except:
            return ""
    
    def _calculate_component_hash(self, name: str, type_: str) -> str:
        """컴포넌트 해시 계산"""
        return hashlib.sha256(f"{name}:{type_}".encode()).hexdigest()
    
    def get_project_statistics(self, project_id: int) -> Dict:
        """프로젝트 통계"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 파일 수
            cursor.execute("SELECT COUNT(*) FROM files WHERE project_id = ?", (project_id,))
            file_count = cursor.fetchone()[0]
            
            # 컴포넌트 수
            cursor.execute("SELECT COUNT(*) FROM components WHERE project_id = ?", (project_id,))
            component_count = cursor.fetchone()[0]
            
            # 관계 수
            cursor.execute("SELECT COUNT(*) FROM relationships WHERE project_id = ?", (project_id,))
            relationship_count = cursor.fetchone()[0]
            
            # 컴포넌트 타입별 분포
            cursor.execute("""
                SELECT component_type, COUNT(*) 
                FROM components 
                WHERE project_id = ?
                GROUP BY component_type
            """, (project_id,))
            component_distribution = dict(cursor.fetchall())
            
            return {
                'project_id': project_id,
                'file_count': file_count,
                'component_count': component_count,
                'relationship_count': relationship_count,
                'component_distribution': component_distribution
            }
    
    def cleanup_metadata(self, project_id: int):
        """메타데이터 정리 (해시값으로 변경 감지)"""
        # 실제 파일과 메타DB 동기화
        pass


# 사용 편의를 위한 팩토리 클래스
class MetadataManager:
    """메타데이터 관리 통합 인터페이스"""
    
    def __init__(self, project_path: str = "./project"):
        self.engine = OptimizedMetadataEngine(project_path=project_path)
        self.project_path = project_path
    
    def quick_search(self, query: str) -> List[Dict]:
        """빠른 검색"""
        return self.engine.search_components(query)
    
    def deep_analysis(self, component_name: str) -> Dict:
        """심층 분석"""
        return self.engine.get_component_full_details(component_name)
    
    def usage_analysis(self, component_name: str) -> Dict:
        """사용 패턴 분석"""
        return self.engine.analyze_component_usage(component_name)