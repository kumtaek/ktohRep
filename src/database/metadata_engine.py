"""
메타데이터 엔진
분석된 메타데이터를 데이터베이스에 저장하고 관리하는 엔진
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import hashlib
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, func

from ..models.database import (
    DatabaseManager, Project, File, Class, Method, SqlUnit, 
    Join, RequiredFilter, Edge, Summary, EnrichmentLog,
    DbTable, DbColumn, DbPk, DbView
)

class MetadataEngine:
    """메타데이터 저장 및 관리 엔진"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        
    async def create_project(self, project_path: str, project_name: str) -> int:
        """
        새 프로젝트 생성 또는 기존 프로젝트 업데이트
        
        Args:
            project_path: 프로젝트 경로
            project_name: 프로젝트 이름
            
        Returns:
            프로젝트 ID
        """
        
        session = self.db_manager.get_session()
        
        try:
            # 기존 프로젝트 확인
            existing_project = session.query(Project).filter(
                Project.root_path == project_path
            ).first()
            
            if existing_project:
                # 기존 프로젝트 업데이트
                existing_project.updated_at = datetime.utcnow()
                existing_project.name = project_name
                session.commit()
                return existing_project.project_id
            else:
                # 새 프로젝트 생성
                new_project = Project(
                    root_path=project_path,
                    name=project_name
                )
                session.add(new_project)
                session.commit()
                return new_project.project_id
                
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def save_java_analysis(self, 
                                file_obj: File, 
                                classes: List[Class], 
                                methods: List[Method], 
                                edges: List[Edge]) -> Dict[str, int]:
        """
        Java 분석 결과 저장
        
        Args:
            file_obj: 파일 객체
            classes: 클래스 리스트
            methods: 메서드 리스트  
            edges: 의존성 엣지 리스트
            
        Returns:
            저장된 엔티티 수
        """
        
        session = self.db_manager.get_session()
        
        try:
            # 파일 저장
            session.add(file_obj)
            session.flush()  # ID 생성을 위해 flush
            
            saved_counts = {'files': 1, 'classes': 0, 'methods': 0, 'edges': 0}
            
            # 클래스 저장
            for class_obj in classes:
                class_obj.file_id = file_obj.file_id
                session.add(class_obj)
                session.flush()
                
                # 해당 클래스의 메서드들 저장
                class_methods = [m for m in methods if m.class_id is None]  # 임시로 None인 것들
                for method_obj in class_methods[:len(class_methods)//len(classes) if classes else 0]:
                    method_obj.class_id = class_obj.class_id
                    session.add(method_obj)
                    
                saved_counts['classes'] += 1
                
            saved_counts['methods'] = len(methods)
            
            # 의존성 엣지 저장 (ID 해결 후)
            for edge in edges:
                # 임시로 저장, 나중에 ID 해결 필요
                session.add(edge)
                saved_counts['edges'] += 1
                
            session.commit()
            return saved_counts
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def save_jsp_mybatis_analysis(self, 
                                       file_obj: File, 
                                       sql_units: List[SqlUnit], 
                                       joins: List[Join], 
                                       filters: List[RequiredFilter],
                                       edges: List[Edge]) -> Dict[str, int]:
        """
        JSP/MyBatis 분석 결과 저장
        
        Args:
            file_obj: 파일 객체
            sql_units: SQL 구문 리스트
            joins: 조인 조건 리스트
            filters: 필터 조건 리스트
            edges: 의존성 엣지 리스트
            
        Returns:
            저장된 엔티티 수
        """
        
        session = self.db_manager.get_session()
        
        try:
            # 파일 저장
            session.add(file_obj)
            session.flush()
            
            saved_counts = {'files': 1, 'sql_units': 0, 'joins': 0, 'filters': 0, 'edges': 0}
            
            # SQL 구문 저장
            for sql_unit in sql_units:
                sql_unit.file_id = file_obj.file_id
                session.add(sql_unit)
                session.flush()
                
                # 해당 SQL 구문의 조인과 필터 저장
                sql_joins = [j for j in joins if j.sql_id is None]  # 임시로 None인 것들
                sql_filters = [f for f in filters if f.sql_id is None]
                
                for join_obj in sql_joins:
                    join_obj.sql_id = sql_unit.sql_id
                    session.add(join_obj)
                    
                for filter_obj in sql_filters:
                    filter_obj.sql_id = sql_unit.sql_id
                    session.add(filter_obj)
                    
                saved_counts['sql_units'] += 1
                
            saved_counts['joins'] = len(joins)
            saved_counts['filters'] = len(filters)
            
            # 의존성 엣지 저장
            for edge in edges:
                session.add(edge)
                saved_counts['edges'] += 1
                
            session.commit()
            return saved_counts
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def build_dependency_graph(self, project_id: int):
        """
        프로젝트의 의존성 그래프 구축
        
        Args:
            project_id: 프로젝트 ID
        """
        
        session = self.db_manager.get_session()
        
        try:
            # 메서드 호출 관계 해결
            await self._resolve_method_calls(session, project_id)
            
            # 테이블 사용 관계 해결  
            await self._resolve_table_usage(session, project_id)
            
            # PK-FK 관계 추론
            await self._infer_pk_fk_relationships(session, project_id)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def _resolve_method_calls(self, session, project_id: int):
        """메서드 호출 관계 해결"""
        
        # 미해결된 메서드 호출 엣지들 조회
        unresolved_calls = session.query(Edge).filter(
            and_(
                Edge.edge_kind == 'call',
                Edge.dst_id.is_(None)
            )
        ).all()
        
        for edge in unresolved_calls:
            # 소스 메서드 정보 조회
            if edge.src_type == 'method':
                src_method = session.query(Method).filter(
                    Method.method_id == edge.src_id
                ).first()
                
                if src_method:
                    # 같은 프로젝트 내에서 호출 대상 메서드 찾기
                    # 이는 단순화된 구현으로, 실제로는 더 정교한 매칭 필요
                    pass
                    
    async def _resolve_table_usage(self, session, project_id: int):
        """테이블 사용 관계 해결"""
        
        # SQL 구문에서 테이블 사용 관계 추출
        sql_units = session.query(SqlUnit).join(File).filter(
            File.project_id == project_id
        ).all()
        
        for sql_unit in sql_units:
            # 조인 테이블들에서 사용 관계 생성
            joins = session.query(Join).filter(
                Join.sql_id == sql_unit.sql_id
            ).all()
            
            for join in joins:
                # SQL -> 테이블 사용 엣지 생성
                if join.l_table:
                    table_edge = Edge(
                        src_type='sql_unit',
                        src_id=sql_unit.sql_id,
                        dst_type='table',
                        dst_id=None,  # 테이블 ID 해결 필요
                        edge_kind='use_table',
                        confidence=0.8
                    )
                    session.add(table_edge)
                    
    async def _infer_pk_fk_relationships(self, session, project_id: int):
        """PK-FK 관계 추론"""
        
        # 조인 조건들을 분석하여 PK-FK 관계 추론
        joins = session.query(Join).join(SqlUnit).join(File).filter(
            File.project_id == project_id
        ).all()
        
        # 조인 패턴 분석
        join_patterns = {}
        
        for join in joins:
            pattern_key = f"{join.l_table}.{join.l_col}={join.r_table}.{join.r_col}"
            if pattern_key not in join_patterns:
                join_patterns[pattern_key] = []
            join_patterns[pattern_key].append(join)
            
        # 빈도가 높은 조인 패턴을 PK-FK로 추론
        for pattern, pattern_joins in join_patterns.items():
            if len(pattern_joins) >= 2:  # 2번 이상 나타나는 패턴
                for join in pattern_joins:
                    join.inferred_pkfk = 1
                    join.confidence = min(1.0, join.confidence + 0.2)
                    
    async def generate_project_summary(self, project_id: int) -> Dict[str, Any]:
        """
        프로젝트 분석 결과 요약 생성
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            요약 딕셔너리
        """
        
        session = self.db_manager.get_session()
        
        try:
            # 기본 통계
            file_count = session.query(File).filter(File.project_id == project_id).count()
            class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
            method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            sql_count = session.query(SqlUnit).join(File).filter(File.project_id == project_id).count()
            
            # 언어별 파일 수
            language_stats = session.query(File.language, func.count(File.file_id)).filter(
                File.project_id == project_id
            ).group_by(File.language).all()
            
            # 조인과 필터 통계
            join_count = session.query(Join).join(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).count()
            
            filter_count = session.query(RequiredFilter).join(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).count()
            
            # 의존성 엣지 통계
            edge_stats = session.query(Edge.edge_kind, func.count(Edge.edge_id)).group_by(
                Edge.edge_kind
            ).all()
            
            summary = {
                'basic_stats': {
                    'files': file_count,
                    'classes': class_count,
                    'methods': method_count,
                    'sql_units': sql_count,
                    'joins': join_count,
                    'filters': filter_count
                },
                'language_distribution': {lang: count for lang, count in language_stats},
                'dependency_stats': {kind: count for kind, count in edge_stats},
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            raise e
        finally:
            session.close()
            
    async def save_enrichment_log(self, 
                                 target_type: str, 
                                 target_id: int, 
                                 pre_confidence: float,
                                 post_confidence: float,
                                 model: str,
                                 prompt_id: str,
                                 params: Dict[str, Any]):
        """
        LLM 보강 로그 저장
        
        Args:
            target_type: 대상 타입
            target_id: 대상 ID
            pre_confidence: 보강 전 신뢰도
            post_confidence: 보강 후 신뢰도
            model: 사용된 모델
            prompt_id: 프롬프트 ID
            params: 파라미터
        """
        
        session = self.db_manager.get_session()
        
        try:
            log_entry = EnrichmentLog(
                target_type=target_type,
                target_id=target_id,
                pre_conf=pre_confidence,
                post_conf=post_confidence,
                model=model,
                prompt_id=prompt_id,
                params=str(params)  # JSON 문자열로 저장
            )
            
            session.add(log_entry)
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    async def get_project_files(self, project_id: int, 
                               language: Optional[str] = None,
                               modified_since: Optional[datetime] = None) -> List[File]:
        """
        프로젝트의 파일 목록 조회
        
        Args:
            project_id: 프로젝트 ID
            language: 언어 필터 (선택적)
            modified_since: 수정 시간 필터 (선택적)
            
        Returns:
            파일 리스트
        """
        
        session = self.db_manager.get_session()
        
        try:
            query = session.query(File).filter(File.project_id == project_id)
            
            if language:
                query = query.filter(File.language == language)
                
            if modified_since:
                query = query.filter(File.mtime > modified_since)
                
            return query.all()
            
        finally:
            session.close()
            
    async def check_file_changes(self, project_id: int) -> List[Tuple[str, str]]:
        """
        파일 변경 사항 확인 (증분 분석용)
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            (파일경로, 변경타입) 튜플 리스트
        """
        
        session = self.db_manager.get_session()
        
        try:
            changes = []
            
            # DB에 있는 파일들
            db_files = {f.path: f.hash for f in session.query(File).filter(
                File.project_id == project_id
            ).all()}
            
            # 실제 파일 시스템의 파일들과 비교
            project = session.query(Project).filter(
                Project.project_id == project_id
            ).first()
            
            if project:
                # 실제 구현에서는 파일 시스템 스캔 로직 필요
                pass
                
            return changes
            
        finally:
            session.close()