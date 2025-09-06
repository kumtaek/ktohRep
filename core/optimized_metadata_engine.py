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
    
    def __init__(self, db_path: str = "./project/sampleSrc/metadata_optimized.db", project_path: str = "./project"):
        self.db_path = db_path
        self.project_path = Path(project_path)
        self.file_reader = DynamicFileReader(project_path)
        self.init_database()
        self._ensure_dummy_file()
    
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
    
    def find_file(self, project_id: int, file_path: str) -> Optional[int]:
        """주어진 프로젝트와 파일 경로로 기존 파일의 ID를 찾습니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_id FROM files
                WHERE project_id = ? AND file_path = ?
            """, (project_id, file_path))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_file_index(self, project_id: int, file_path: str, file_type: str) -> int:
        """파일 인덱스 추가 (중복 체크 후 추가)"""
        # 먼저 중복 체크
        existing_id = self.find_file(project_id, file_path)
        if existing_id:
            return existing_id  # 중복이면 기존 ID 반환
        
        file_name = Path(file_path).name
        file_hash = self._calculate_file_hash(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO files (project_id, file_path, file_name, file_type, hash_value)
                    VALUES (?, ?, ?, ?, ?)
                """, (project_id, file_path, file_name, file_type, file_hash))
                file_id = cursor.lastrowid
                conn.commit()
                return file_id
            except sqlite3.IntegrityError:
                # UNIQUE 제약조건 위반 시 기존 레코드 찾아서 반환
                conn.rollback()
                existing_id = self.find_file(project_id, file_path)
                return existing_id if existing_id else None
    
    def find_component(self, project_id: int, file_id: int, component_name: str, component_type: str, parent_component_id: Optional[int] = None) -> Optional[int]:
        """
        주어진 정보로 기존 컴포넌트의 ID를 찾습니다. 없으면 None을 반환합니다.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT component_id FROM components
            WHERE project_id = ? AND file_id = ? AND component_name = ? AND component_type = ?
            """
            params = [project_id, file_id, component_name, component_type]

            if parent_component_id:
                query += " AND parent_component_id = ?"
                params.append(parent_component_id)
            else:
                query += " AND parent_component_id IS NULL"

            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_or_create_dummy_file(self, project_id: int) -> int:
        """CSV나 가상 테이블을 위한 더미 파일 ID 반환 (항상 0)"""
        return 0

    def _ensure_dummy_file(self):
        """더미 파일 ID 0이 존재하도록 보장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # file_id = 0인 더미 파일이 있는지 확인
            cursor.execute("SELECT file_id FROM files WHERE file_id = 0")
            if not cursor.fetchone():
                # 없으면 생성
                cursor.execute("""
                    INSERT OR REPLACE INTO files (file_id, project_id, file_path, file_name, file_type, hash_value)
                    VALUES (0, 0, '<virtual>', '<virtual>', 'virtual', 'dummy')
                """)
            conn.commit()

    def add_component(self, project_id: int, file_id: Optional[int], component_name: str, 
                     component_type: str, line_start: Optional[int] = None, line_end: Optional[int] = None,
                     parent_component_id: Optional[int] = None) -> int:
        """컴포넌트 추가 (중복 체크 후 추가)"""
        # file_id가 None인 경우 더미 파일 ID 사용
        if file_id is None:
            file_id = self.get_or_create_dummy_file(project_id)
        
        # 먼저 중복 체크
        existing_id = self.find_component(project_id, file_id, component_name, component_type, parent_component_id)
        if existing_id:
            return existing_id  # 중복이면 기존 ID 반환
        
        component_hash = self._calculate_component_hash(component_name, component_type)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO components 
                    (project_id, file_id, component_name, component_type, line_start, line_end, parent_component_id, hash_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (project_id, file_id, component_name, component_type, line_start, line_end, parent_component_id, component_hash))
                component_id = cursor.lastrowid
                conn.commit()
                return component_id
            except sqlite3.IntegrityError as e:
                # UNIQUE 제약조건 위반 시 기존 레코드 찾아서 반환
                conn.rollback()
                existing_id = self.find_component(project_id, file_id, component_name, component_type, parent_component_id)
                return existing_id if existing_id else None
    
    def add_relationship(self, project_id: int, src_component_id: int, dst_component_id: int,
                        relationship_type: str, confidence: float = 1.0):
        """관계 추가 - 중복 방지"""
        with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 중복 체크 후 INSERT 또는 UPDATE
                cursor.execute("""
                    INSERT OR IGNORE INTO relationships (project_id, src_component_id, dst_component_id, relationship_type, confidence)
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
    
    def get_all_components(self, project_id: int) -> List[Dict]:
        """프로젝트의 모든 컴포넌트 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.component_id, c.component_name, c.component_type, f.file_path
                FROM components c
                JOIN files f ON c.file_id = f.file_id
                WHERE c.project_id = ?
                ORDER BY c.component_name
            """, (project_id,))
            
            components = []
            for row in cursor.fetchall():
                components.append({
                    'component_id': row[0],
                    'component_name': row[1],
                    'component_type': row[2],
                    'file_path': row[3]
                })
            
            return components
    
    def get_all_files(self, project_id: int) -> List[Dict]:
        """프로젝트의 모든 파일 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_id, file_path, file_type
                FROM files 
                WHERE project_id = ?
                ORDER BY file_path
            """, (project_id,))
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    'file_id': row[0],
                    'file_path': row[1],
                    'file_type': row[2]
                })
            
            return files
    
    def cleanup_metadata(self, project_id: int):
        """메타데이터 정리 (해시값으로 변경 감지)"""
        # 실제 파일과 메타DB 동기화
        pass
    
    def remove_duplicates(self, project_id: int):
        """최종 중복 제거 - 동일한 컴포넌트/관계의 중복 레코드 제거"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 컴포넌트 중복 제거 (동일한 project_id, file_id, component_name, component_type, parent_component_id)
            print("DEBUG: Removing duplicate components...")
            cursor.execute("""
                DELETE FROM components 
                WHERE component_id NOT IN (
                    SELECT MIN(component_id) 
                    FROM components 
                    WHERE project_id = ?
                    GROUP BY project_id, file_id, component_name, component_type, 
                             COALESCE(parent_component_id, -1)
                ) AND project_id = ?
            """, (project_id, project_id))
            components_removed = cursor.rowcount
            print(f"DEBUG: Removed {components_removed} duplicate components")
            
            # 2. 관계 중복 제거 (동일한 project_id, src_component_id, dst_component_id, relationship_type)
            print("DEBUG: Removing duplicate relationships...")
            cursor.execute("""
                DELETE FROM relationships 
                WHERE relationship_id NOT IN (
                    SELECT MIN(relationship_id) 
                    FROM relationships 
                    WHERE project_id = ?
                    GROUP BY project_id, src_component_id, dst_component_id, relationship_type
                ) AND project_id = ?
            """, (project_id, project_id))
            relationships_removed = cursor.rowcount
            print(f"DEBUG: Removed {relationships_removed} duplicate relationships")
            
            # 3. 파일 중복 제거 (동일한 project_id, file_path)
            print("DEBUG: Removing duplicate files...")
            cursor.execute("""
                DELETE FROM files 
                WHERE file_id NOT IN (
                    SELECT MIN(file_id) 
                    FROM files 
                    WHERE project_id = ?
                    GROUP BY project_id, file_path
                ) AND project_id = ?
            """, (project_id, project_id))
            files_removed = cursor.rowcount
            print(f"DEBUG: Removed {files_removed} duplicate files")
            
            conn.commit()
            
            return {
                'components_removed': components_removed,
                'relationships_removed': relationships_removed,
                'files_removed': files_removed
            }


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