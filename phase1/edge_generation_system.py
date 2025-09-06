#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
통합 엣지 생성 시스템
파서 기반, LLM 기반 분석을 통합하여 포괄적인 엣지 정보를 메타DB에 생성합니다.
"""

import logging
import os
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from phase1.models.database import Project, Class, File, SqlUnit, DbTable, Edge

# 우리가 만든 모듈들
from phase1.utils.enhanced_edge_generator import EnhancedEdgeGenerator
from phase1.utils.edge_manager import EdgeManager
from phase1.llm.relationship_analyzer import RelationshipAnalyzer, ProjectContextBuilder

logger = logging.getLogger(__name__)


class EdgeGenerationSystem:
    """통합 엣지 생성 시스템"""
    
    def __init__(self, db_session: Session, project_path: str, project_id: int = 1, config_path: str = None):
        self.db_session = db_session
        self.project_path = Path(project_path)
        self.project_id = project_id
        
        # 컴포넌트 초기화
        self.edge_manager = EdgeManager(db_session, project_id, config_path)
        self.enhanced_generator = EnhancedEdgeGenerator(db_session, str(project_path), project_id)
        self.relationship_analyzer = RelationshipAnalyzer()
        self.context_builder = ProjectContextBuilder(db_session)
        
        # 실행 통계
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'phases_completed': [],
            'total_edges_created': 0,
            'errors': []
        }
    
    def generate_all_edges(self, enable_llm_analysis: bool = True, 
                          enable_advanced_parsing: bool = True) -> Dict[str, Any]:
        """모든 엣지를 생성하는 메인 메서드"""
        
        self.execution_stats['start_time'] = time.time()
        logger.info("=== 통합 엣지 생성 시스템 시작 ===")
        logger.info(f"프로젝트 경로: {self.project_path}")
        logger.info(f"프로젝트 ID: {self.project_id}")
        
        try:
            # 1단계: 프로젝트 컨텍스트 구축
            self._execute_phase("프로젝트 컨텍스트 구축", self._build_project_context)
            
            # 2단계: 기존 엣지 정리
            self._execute_phase("기존 엣지 정리", self._cleanup_existing_edges)
            
            # 3단계: 향상된 파서 기반 엣지 생성 
            if enable_advanced_parsing:
                self._execute_phase("향상된 파서 기반 엣지 생성", self._generate_parser_based_edges)
            
            # 4단계: SQL 조인 기반 엣지 생성
            self._execute_phase("SQL 조인 기반 엣지 생성", self._generate_sql_join_edges)
            
            # 5단계: LLM 기반 엣지 생성
            if enable_llm_analysis:
                self._execute_phase("LLM 기반 관계 분석", self._generate_llm_based_edges)
            
            # 6단계: 엣지 정제 및 검증
            self._execute_phase("엣지 정제 및 검증", self._refine_and_validate_edges)
            
            # 7단계: 최종 통계 및 보고서 생성
            self._execute_phase("최종 통계 생성", self._generate_final_statistics)
            
            # 변경사항 커밋
            self.edge_manager.commit_changes()
            
            self.execution_stats['end_time'] = time.time()
            self.execution_stats['duration_seconds'] = self.execution_stats['end_time'] - self.execution_stats['start_time']
            
            logger.info("=== 통합 엣지 생성 시스템 완료 ===")
            return self._build_completion_report()
            
        except Exception as e:
            logger.error(f"엣지 생성 시스템 실행 실패: {e}", exc_info=True)
            self.execution_stats['errors'].append(str(e))
            
            # 롤백
            self.db_session.rollback()
            raise
    
    def _execute_phase(self, phase_name: str, phase_function):
        """단계 실행 래퍼"""
        logger.info(f"--- {phase_name} 시작 ---")
        phase_start = time.time()
        
        try:
            result = phase_function()
            
            phase_duration = time.time() - phase_start
            self.execution_stats['phases_completed'].append({
                'name': phase_name,
                'duration': phase_duration,
                'result': result
            })
            
            logger.info(f"--- {phase_name} 완료 ({phase_duration:.2f}초) ---")
            return result
            
        except Exception as e:
            logger.error(f"{phase_name} 실패: {e}")
            self.execution_stats['errors'].append(f"{phase_name}: {str(e)}")
            raise
    
    def _build_project_context(self) -> Dict[str, Any]:
        """프로젝트 컨텍스트 구축"""
        
        context = self.context_builder.build_context(self.project_id)
        
        # 프로젝트 정보 확인
        project = self.db_session.query(Project).filter(Project.project_id == self.project_id).first()
        if project:
            context['project_name'] = project.project_name
        
        logger.info(f"프로젝트 컨텍스트: 클래스 {len(context.get('classes', []))}개, "
                   f"파일 {sum(len(files) for files in context.get('files', {}).values())}개")
        
        self.project_context = context
        return context
    
    def _cleanup_existing_edges(self) -> Dict[str, int]:
        """기존 엣지 정리"""
        
        # 기존 엣지 수 확인
        existing_count = self.db_session.query(Edge).filter(Edge.project_id == self.project_id).count()
        
        # 중복 엣지 제거
        duplicates_removed = self.edge_manager.remove_duplicates()
        
        # 최종 엣지 수 확인
        final_count = self.db_session.query(Edge).filter(Edge.project_id == self.project_id).count()
        
        result = {
            'existing_edges': existing_count,
            'duplicates_removed': duplicates_removed,
            'cleaned_edges': final_count
        }
        
        logger.info(f"엣지 정리 완료: 기존 {existing_count}개 → 정리 후 {final_count}개")
        return result
    
    def _generate_parser_based_edges(self) -> Dict[str, int]:
        """향상된 파서 기반 엣지 생성"""
        
        stats_before = self.edge_manager.get_statistics()
        
        # Enhanced Edge Generator 실행
        edges_created = self.enhanced_generator.generate_all_edges()
        
        stats_after = self.edge_manager.get_statistics()
        
        result = {
            'parser_edges_created': edges_created,
            'dummy_chunks_created': stats_after['dummy_chunks_created'] - stats_before.get('dummy_chunks_created', 0)
        }
        
        logger.info(f"파서 기반 엣지 생성 완료: {edges_created}개")
        return result
    
    def _generate_sql_join_edges(self) -> Dict[str, int]:
        """SQL 조인 기반 엣지 생성"""
        
        join_edges_created = 0
        
        # JOIN을 포함한 SQL Unit들 조회
        sql_units_with_joins = self.db_session.query(SqlUnit).filter(
            SqlUnit.normalized_fingerprint.like('%JOIN%')
        ).all()
        
        logger.info(f"JOIN 포함 SQL Unit {len(sql_units_with_joins)}개 분석")
        
        for sql_unit in sql_units_with_joins:
            try:
                # LLM을 사용하여 JOIN 관계 분석
                sql_relationships = self.relationship_analyzer.analyze_sql_join_relationships(
                    sql_unit.normalized_fingerprint,
                    sql_unit.stmt_id
                )
                
                # 분석된 관계를 엣지로 생성
                for rel in sql_relationships:
                    if rel['type'] == 'join':
                        # 테이블 간 JOIN 엣지 생성
                        edge = self.edge_manager.create_edge_by_names(
                            src_type='table',
                            src_name=rel['source'],
                            dst_type='table', 
                            dst_name=rel['target'],
                            edge_kind='join',
                            confidence=rel['confidence'],
                            meta=f"SQL JOIN: {rel['relationship']} (SQL: {sql_unit.stmt_id})"
                        )
                        
                        if edge:
                            join_edges_created += 1
                            
            except Exception as e:
                logger.warning(f"SQL 조인 분석 실패 {sql_unit.stmt_id}: {e}")
        
        logger.info(f"SQL 조인 엣지 생성 완료: {join_edges_created}개")
        return {'join_edges_created': join_edges_created}
    
    def _generate_llm_based_edges(self) -> Dict[str, int]:
        """LLM 기반 엣지 생성"""
        
        llm_edges_created = 0
        files_analyzed = 0
        
        # 복잡한 파일들 식별하여 LLM 분석
        complex_java_files = self._identify_complex_java_files()
        complex_xml_files = self._identify_complex_xml_files()
        complex_jsp_files = self._identify_complex_jsp_files()
        
        logger.info(f"LLM 분석 대상: Java {len(complex_java_files)}, XML {len(complex_xml_files)}, JSP {len(complex_jsp_files)}")
        
        # Java 파일 분석
        for java_file in complex_java_files:
            try:
                file_content = self._read_file_content(java_file)
                if file_content:
                    relationships = self.relationship_analyzer.analyze_java_relationships(
                        file_content, str(java_file), self.project_context
                    )
                    
                    created_count = self._process_llm_relationships(relationships, 'java', java_file)
                    llm_edges_created += created_count
                    files_analyzed += 1
                    
            except Exception as e:
                logger.warning(f"Java LLM 분석 실패 {java_file}: {e}")
        
        # XML 파일 분석
        for xml_file in complex_xml_files:
            try:
                file_content = self._read_file_content(xml_file)
                if file_content:
                    java_interfaces = self.project_context.get('mappers', [])
                    relationships = self.relationship_analyzer.analyze_mybatis_relationships(
                        file_content, str(xml_file), java_interfaces
                    )
                    
                    created_count = self._process_llm_relationships(relationships, 'xml', xml_file)
                    llm_edges_created += created_count
                    files_analyzed += 1
                    
            except Exception as e:
                logger.warning(f"XML LLM 분석 실패 {xml_file}: {e}")
        
        # JSP 파일 분석
        for jsp_file in complex_jsp_files:
            try:
                file_content = self._read_file_content(jsp_file)
                if file_content:
                    controller_methods = [cls for cls in self.project_context.get('classes', []) 
                                        if 'controller' in cls.lower()]
                    relationships = self.relationship_analyzer.analyze_jsp_relationships(
                        file_content, str(jsp_file), controller_methods
                    )
                    
                    created_count = self._process_llm_relationships(relationships, 'jsp', jsp_file)
                    llm_edges_created += created_count
                    files_analyzed += 1
                    
            except Exception as e:
                logger.warning(f"JSP LLM 분석 실패 {jsp_file}: {e}")
        
        result = {
            'llm_edges_created': llm_edges_created,
            'files_analyzed': files_analyzed
        }
        
        logger.info(f"LLM 기반 엣지 생성 완료: {llm_edges_created}개 ({files_analyzed}개 파일 분석)")
        return result
    
    def _refine_and_validate_edges(self) -> Dict[str, int]:
        """엣지 정제 및 검증"""
        
        # 중복 엣지 최종 제거
        duplicates_removed = self.edge_manager.remove_duplicates()
        
        # 낮은 신뢰도 엣지 필터링
        low_confidence_removed = self._filter_low_confidence_edges()
        
        # 순환 참조 검증 (필요시)
        circular_deps = self._check_circular_dependencies()
        
        result = {
            'duplicates_removed': duplicates_removed,
            'low_confidence_removed': low_confidence_removed,
            'circular_dependencies_found': len(circular_deps)
        }
        
        logger.info(f"엣지 정제 완료: 중복 제거 {duplicates_removed}개, 낮은 신뢰도 제거 {low_confidence_removed}개")
        return result
    
    def _generate_final_statistics(self) -> Dict[str, Any]:
        """최종 통계 생성"""
        
        # 엣지 유형별 통계
        edge_stats = self._get_edge_statistics_by_type()
        
        # 매니저 통계
        manager_stats = self.edge_manager.get_statistics()
        
        # 전체 통계 합계
        total_edges = self.db_session.query(Edge).filter(Edge.project_id == self.project_id).count()
        
        final_stats = {
            'total_edges': total_edges,
            'edge_types': edge_stats,
            'manager_stats': manager_stats,
            'execution_stats': self.execution_stats
        }
        
        self.execution_stats['total_edges_created'] = total_edges
        
        logger.info(f"최종 통계: 총 {total_edges}개 엣지 생성")
        return final_stats
    
    # 헬퍼 메서드들
    
    def _identify_complex_java_files(self) -> List[Path]:
        """복잡한 Java 파일들 식별"""
        java_files = list(self.project_path.rglob("*.java"))
        
        # 복잡도 기준: Controller, Service, 복잡한 비즈니스 로직이 있는 파일들
        complex_files = []
        for java_file in java_files:
            if any(keyword in str(java_file).lower() for keyword in 
                   ['controller', 'service', 'impl', 'manager']):
                complex_files.append(java_file)
        
        return complex_files[:10]  # 최대 10개만 LLM 분석
    
    def _identify_complex_xml_files(self) -> List[Path]:
        """복잡한 XML 파일들 식별"""
        xml_files = list(self.project_path.rglob("*.xml"))
        
        # MyBatis 매퍼 파일들만
        complex_files = []
        for xml_file in xml_files:
            if 'mapper' in str(xml_file).lower() or 'mybatis' in str(xml_file).lower():
                complex_files.append(xml_file)
        
        return complex_files[:5]  # 최대 5개만
    
    def _identify_complex_jsp_files(self) -> List[Path]:
        """복잡한 JSP 파일들 식별"""
        jsp_files = list(self.project_path.rglob("*.jsp"))
        return jsp_files[:5]  # 최대 5개만
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """파일 내용 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 내용이 너무 길면 제한
                return content[:5000] if len(content) > 5000 else content
        except Exception as e:
            logger.warning(f"파일 읽기 실패 {file_path}: {e}")
            return None
    
    def _process_llm_relationships(self, relationships: List[Dict], file_type: str, file_path: Path) -> int:
        """LLM 분석 결과를 엣지로 변환"""
        edges_created = 0
        
        for rel in relationships:
            try:
                # 관계 타입에 따라 엣지 생성
                if rel['type'] in ['dependency', 'reference', 'calls']:
                    edge = self.edge_manager.create_edge_by_names(
                        src_type='class' if file_type == 'java' else 'file',
                        src_name=rel['source'],
                        dst_type='class',
                        dst_name=rel['target'],
                        edge_kind=rel['type'],
                        confidence=rel['confidence'],
                        meta=f"LLM: {rel.get('relationship', '')} [{file_type}]"
                    )
                    
                    if edge:
                        edges_created += 1
                        
            except Exception as e:
                logger.warning(f"LLM 관계 처리 실패: {e}")
        
        return edges_created
    
    def _get_edge_statistics_by_type(self) -> Dict[str, int]:
        """엣지 유형별 통계"""
        from sqlalchemy import func
        
        edge_types = self.db_session.query(
            Edge.edge_kind, func.count(Edge.edge_id)
        ).filter(
            Edge.project_id == self.project_id
        ).group_by(Edge.edge_kind).all()
        
        return {edge_kind: count for edge_kind, count in edge_types}
    
    def _filter_low_confidence_edges(self) -> int:
        """낮은 신뢰도 엣지 필터링"""
        min_confidence = 0.3
        
        low_confidence_edges = self.db_session.query(Edge).filter(
            Edge.project_id == self.project_id,
            Edge.confidence < min_confidence
        ).all()
        
        for edge in low_confidence_edges:
            self.db_session.delete(edge)
        
        count = len(low_confidence_edges)
        if count > 0:
            logger.info(f"낮은 신뢰도 엣지 제거: {count}개 (< {min_confidence})")
        
        return count
    
    def _check_circular_dependencies(self) -> List[Dict]:
        """순환 참조 검증 (간단한 버전)"""
        # 실제 구현은 그래프 알고리즘 필요
        # 여기서는 간단히 동일한 클래스 간 양방향 dependency만 체크
        
        circular_deps = []
        
        dependency_edges = self.db_session.query(Edge).filter(
            Edge.project_id == self.project_id,
            Edge.edge_kind == 'dependency'
        ).all()
        
        # 간단한 양방향 의존성 체크
        edge_pairs = {}
        for edge in dependency_edges:
            key1 = (edge.src_type, edge.src_id, edge.dst_type, edge.dst_id)
            key2 = (edge.dst_type, edge.dst_id, edge.src_type, edge.src_id)
            
            if key2 in edge_pairs:
                circular_deps.append({
                    'edge1': key1,
                    'edge2': key2,
                    'type': 'bidirectional_dependency'
                })
            else:
                edge_pairs[key1] = edge
        
        if circular_deps:
            logger.warning(f"순환 참조 발견: {len(circular_deps)}개")
        
        return circular_deps
    
    def _build_completion_report(self) -> Dict[str, Any]:
        """완료 보고서 생성"""
        
        total_duration = self.execution_stats['duration_seconds']
        total_edges = self.execution_stats['total_edges_created']
        
        report = {
            'success': True,
            'execution_time': f"{total_duration:.2f}초",
            'total_edges_created': total_edges,
            'phases_completed': len(self.execution_stats['phases_completed']),
            'errors_count': len(self.execution_stats['errors']),
            'edge_generation_rate': f"{total_edges/total_duration:.1f} edges/sec" if total_duration > 0 else "N/A",
            'phases': self.execution_stats['phases_completed'],
            'manager_statistics': self.edge_manager.get_statistics()
        }
        
        if self.execution_stats['errors']:
            report['errors'] = self.execution_stats['errors']
        
        return report


def main():
    """메인 실행 함수 - 테스트용"""
    import sys
    from phase1.database.metadata_engine import MetadataEngine
    
    if len(sys.argv) < 2:
        print("사용법: python edge_generation_system.py <프로젝트_경로>")
        return
    
    project_path = sys.argv[1]
    
    # DB 세션 생성 (메인 프로세스와 동일한 방식)
    from phase1.models.database import DatabaseManager
    import yaml
    
    # 설정 파일 로드
    config_path = Path(__file__).parent / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    db_config = config.get('database', {})
    db_manager = DatabaseManager(db_config)
    db_manager.initialize()
    
    with db_manager.get_auto_commit_session() as session:
        try:
            # 엣지 생성 시스템 실행
            edge_system = EdgeGenerationSystem(
                db_session=session,
                project_path=project_path,
                project_id=1
            )
            
            result = edge_system.generate_all_edges(
                enable_llm_analysis=True,
                enable_advanced_parsing=True
            )
            
            print("\n=== 엣지 생성 완료 ===")
            print(f"총 엣지 수: {result['total_edges_created']}")
            print(f"실행 시간: {result['execution_time']}")
            print(f"생성 속도: {result['edge_generation_rate']}")
            
            if result.get('errors_count', 0) > 0:
                print(f"오류 수: {result['errors_count']}")
                
        except Exception as e:
            logger.error(f"시스템 실행 실패: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            import sys
            sys.exit(1)


if __name__ == "__main__":
    main()