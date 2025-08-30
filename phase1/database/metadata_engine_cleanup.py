"""
삭제된 파일 정리를 위한 MetadataEngine 확장
"""

from typing import Set
from sqlalchemy import and_, or_
from .metadata_engine import MetadataEngine
from models.database import File, Class, Method, SqlUnit, Edge, Join, RequiredFilter, Summary, EnrichmentLog, VulnerabilityFix


async def cleanup_deleted_files(self, deleted_file_paths: Set[str], project_id: int) -> int:
    """
    삭제된 파일들의 메타데이터 정리
    
    Args:
        deleted_file_paths: 삭제된 파일 경로 집합
        project_id: 프로젝트 ID
        
    Returns:
        정리된 파일 수
    """
    
    session = self.db_manager.get_session()
    
    try:
        cleaned_count = 0
        
        for file_path in deleted_file_paths:
            # 파일 객체 조회
            file_obj = session.query(File).filter(
                and_(
                    File.project_id == project_id,
                    File.path == file_path
                )
            ).first()
            
            if not file_obj:
                continue
                
            file_id = file_obj.file_id
            self.logger.debug(f"삭제된 파일 메타데이터 정리 시작: {file_path} (ID: {file_id})")
            
            # 1. 관련 엣지 삭제 (src_id 또는 dst_id가 이 파일의 요소를 참조하는 모든 엣지)
            # 파일과 직접 연결된 엣지들 (file -> file 관계)
            session.query(Edge).filter(
                or_(
                    and_(Edge.src_type == 'file', Edge.src_id == file_id),
                    and_(Edge.dst_type == 'file', Edge.dst_id == file_id)
                )
            ).delete()
            
            # 클래스들과 연결된 엣지들 제거
            class_ids = [c.class_id for c in session.query(Class).filter(Class.file_id == file_id).all()]
            if class_ids:
                session.query(Edge).filter(
                    or_(
                        and_(Edge.src_type == 'class', Edge.src_id.in_(class_ids)),
                        and_(Edge.dst_type == 'class', Edge.dst_id.in_(class_ids))
                    )
                ).delete(synchronize_session=False)
            
            # 메서드들과 연결된 엣지들 제거
            method_ids = [m.method_id for m in session.query(Method).join(Class).filter(Class.file_id == file_id).all()]
            if method_ids:
                session.query(Edge).filter(
                    or_(
                        and_(Edge.src_type == 'method', Edge.src_id.in_(method_ids)),
                        and_(Edge.dst_type == 'method', Edge.dst_id.in_(method_ids))
                    )
                ).delete(synchronize_session=False)
                
            # SQL 유닛들과 연결된 엣지들 제거
            sql_unit_ids = [s.sql_id for s in session.query(SqlUnit).filter(SqlUnit.file_id == file_id).all()]
            if sql_unit_ids:
                session.query(Edge).filter(
                    or_(
                        and_(Edge.src_type == 'sql_unit', Edge.src_id.in_(sql_unit_ids)),
                        and_(Edge.dst_type == 'sql_unit', Edge.dst_id.in_(sql_unit_ids))
                    )
                ).delete(synchronize_session=False)
            
            # 2. SQL 관련 테이블들 정리 (조인, 필터)
            if sql_unit_ids:
                session.query(Join).filter(Join.sql_id.in_(sql_unit_ids)).delete(synchronize_session=False)
                session.query(RequiredFilter).filter(RequiredFilter.sql_id.in_(sql_unit_ids)).delete(synchronize_session=False)
            
            # 3. SQL 유닛들 삭제
            session.query(SqlUnit).filter(SqlUnit.file_id == file_id).delete()
            
            # 4. 메서드들 삭제 (클래스를 통해)
            if class_ids:
                session.query(Method).filter(Method.class_id.in_(class_ids)).delete(synchronize_session=False)
            
            # 5. 클래스들 삭제
            session.query(Class).filter(Class.file_id == file_id).delete()
            
            # 6. 요약 정보 삭제 (파일에 연관된)
            session.query(Summary).filter(
                and_(
                    Summary.target_type == 'file',
                    Summary.target_id == file_id
                )
            ).delete()
            
            # 7. 보강 로그 삭제 (파일에 연관된)
            session.query(EnrichmentLog).filter(
                and_(
                    EnrichmentLog.target_type == 'file',
                    EnrichmentLog.target_id == file_id
                )
            ).delete()
            
            # 8. 취약점 수정 정보 삭제 (파일에 연관된)
            session.query(VulnerabilityFix).filter(
                and_(
                    VulnerabilityFix.target_type == 'file',
                    VulnerabilityFix.target_id == file_id
                )
            ).delete()
            
            # 9. 마지막으로 파일 객체 삭제
            session.delete(file_obj)
            
            cleaned_count += 1
            self.logger.debug(f"삭제된 파일 메타데이터 정리 완료: {file_path}")
        
        session.commit()
        self.logger.info(f"총 {cleaned_count}개 파일의 메타데이터가 정리되었습니다")
        
        return cleaned_count
        
    except Exception as e:
        session.rollback()
        self.logger.error("삭제된 파일 메타데이터 정리 중 오류", exception=e)
        raise e
    finally:
        session.close()


# MetadataEngine 클래스에 메서드 추가
MetadataEngine.cleanup_deleted_files = cleanup_deleted_files