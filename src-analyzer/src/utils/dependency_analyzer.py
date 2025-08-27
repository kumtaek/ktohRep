"""
Dependency graph analysis module
Analyzes call relationships, data dependencies, and creates edges in the graph
"""

import re
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.database import (
    File, JavaClass, JavaMethod, SQLUnit, DBTable, DBColumn,
    Edge, create_database_engine
)


@dataclass
class DependencyEdge:
    """의존성 엣지 정보"""
    src_type: str
    src_id: int
    dst_type: str
    dst_id: int
    edge_kind: str
    confidence: float
    metadata: Dict[str, Any] = None


class DependencyAnalyzer:
    """의존성 분석기"""
    
    def __init__(self, session: Session, config: Dict = None):
        self.session = session
        self.config = config or {}
        self.edges_to_create = []
    
    def analyze_java_method_calls(self, project_id: int) -> List[DependencyEdge]:
        """Java 메소드 호출 관계 분석"""
        edges = []
        
        # Java 파일들 조회
        java_files = self.session.query(File).filter(
            and_(File.project_id == project_id, File.language == 'java')
        ).all()
        
        for file_obj in java_files:
            try:
                # 파일 내용 읽기
                with open(file_obj.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 파일 내 모든 메소드 조회
                classes = self.session.query(JavaClass).filter(JavaClass.file_id == file_obj.file_id).all()
                
                for class_obj in classes:
                    methods = self.session.query(JavaMethod).filter(JavaMethod.class_id == class_obj.class_id).all()
                    
                    for method in methods:
                        # 메소드 내 다른 메소드 호출 분석
                        called_methods = self._extract_method_calls_from_content(content, method.start_line, method.end_line)
                        
                        for called_method in called_methods:
                            # 호출된 메소드 찾기
                            target_method = self._find_method_by_name(called_method, project_id)
                            if target_method:
                                edge = DependencyEdge(
                                    src_type='method',
                                    src_id=method.method_id,
                                    dst_type='method',
                                    dst_id=target_method.method_id,
                                    edge_kind='calls',
                                    confidence=0.8,
                                    metadata={'call_name': called_method}
                                )
                                edges.append(edge)
            
            except Exception as e:
                print(f"Error analyzing method calls in {file_obj.path}: {e}")
        
        return edges
    
    def _extract_method_calls_from_content(self, content: str, start_line: int, end_line: int) -> List[str]:
        """소스코드에서 메소드 호출 추출"""
        method_calls = []
        
        # 라인별로 분할
        lines = content.splitlines()
        if start_line <= 0 or end_line <= 0 or start_line >= len(lines):
            return method_calls
        
        # 메소드 내용 추출
        method_content = '\n'.join(lines[start_line-1:min(end_line, len(lines))])
        
        # 메소드 호출 패턴 (간단한 정규식)
        call_patterns = [
            r'(\w+)\s*\(',  # 일반 메소드 호출
            r'this\.(\w+)\s*\(',  # this.method() 호출
            r'super\.(\w+)\s*\(',  # super.method() 호출
        ]
        
        for pattern in call_patterns:
            matches = re.findall(pattern, method_content)
            method_calls.extend(matches)
        
        # 중복 제거 및 필터링
        method_calls = list(set(method_calls))
        method_calls = [call for call in method_calls if self._is_likely_method_call(call)]
        
        return method_calls
    
    def _is_likely_method_call(self, method_name: str) -> bool:
        """메소드 호출일 가능성 확인"""
        # Java 키워드나 너무 일반적인 이름 제외
        excluded_names = {
            'if', 'for', 'while', 'switch', 'try', 'catch', 'finally',
            'new', 'return', 'break', 'continue', 'throw', 'assert',
            'System', 'String', 'Integer', 'Object', 'List', 'Map', 'Set'
        }
        
        if method_name in excluded_names:
            return False
        
        # 첫 글자가 소문자인 경우만 (Java 메소드 명명 규칙)
        return method_name and method_name[0].islower() and len(method_name) > 1
    
    def _find_method_by_name(self, method_name: str, project_id: int) -> Optional[JavaMethod]:
        """이름으로 메소드 찾기"""
        # 프로젝트 내 모든 메소드에서 검색
        method = self.session.query(JavaMethod).join(JavaClass).join(File).filter(
            and_(
                File.project_id == project_id,
                JavaMethod.name == method_name
            )
        ).first()
        
        return method
    
    def analyze_java_database_usage(self, project_id: int) -> List[DependencyEdge]:
        """Java 코드의 데이터베이스 사용 분석"""
        edges = []
        
        # Java 파일들 조회
        java_files = self.session.query(File).filter(
            and_(File.project_id == project_id, File.language == 'java')
        ).all()
        
        # 데이터베이스 테이블 조회
        db_tables = self.session.query(DBTable).all()
        table_names = [table.table_name.lower() for table in db_tables]
        
        for file_obj in java_files:
            try:
                with open(file_obj.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                # SQL 문자열이나 테이블명 참조 찾기
                for table in db_tables:
                    table_name = table.table_name.lower()
                    
                    # 테이블명이 코드에 포함되어 있는지 확인
                    if table_name in content:
                        # 어떤 메소드에서 사용되는지 찾기
                        classes = self.session.query(JavaClass).filter(JavaClass.file_id == file_obj.file_id).all()
                        
                        for class_obj in classes:
                            methods = self.session.query(JavaMethod).filter(JavaMethod.class_id == class_obj.class_id).all()
                            
                            for method in methods:
                                if self._method_uses_table(content, method, table_name):
                                    edge = DependencyEdge(
                                        src_type='method',
                                        src_id=method.method_id,
                                        dst_type='table',
                                        dst_id=table.table_id,
                                        edge_kind='uses_table',
                                        confidence=0.6,  # 낮은 신뢰도 (정적 분석의 한계)
                                        metadata={'table_name': table.table_name}
                                    )
                                    edges.append(edge)
            
            except Exception as e:
                print(f"Error analyzing database usage in {file_obj.path}: {e}")
        
        return edges
    
    def _method_uses_table(self, file_content: str, method: JavaMethod, table_name: str) -> bool:
        """특정 메소드가 테이블을 사용하는지 확인"""
        # 파일 내용에서 메소드 범위 추출
        lines = file_content.splitlines()
        if method.start_line <= 0 or method.end_line <= 0 or method.start_line >= len(lines):
            return False
        
        method_content = '\n'.join(lines[method.start_line-1:min(method.end_line, len(lines))])
        
        # 테이블명이 메소드 내에서 사용되는지 확인
        return table_name.lower() in method_content.lower()
    
    def analyze_mybatis_sql_relationships(self, project_id: int) -> List[DependencyEdge]:
        """MyBatis와 SQL 관계 분석"""
        edges = []
        
        # MyBatis 파일들 조회
        mybatis_files = self.session.query(File).filter(
            and_(File.project_id == project_id, File.language == 'mybatis')
        ).all()
        
        for file_obj in mybatis_files:
            # 파일의 SQL 유닛들 조회
            sql_units = self.session.query(SQLUnit).filter(SQLUnit.file_id == file_obj.file_id).all()
            
            for sql_unit in sql_units:
                try:
                    # Java 메소드와의 연결 찾기
                    if sql_unit.mapper_ns and sql_unit.stmt_id:
                        # 네임스페이스로 Java 클래스 찾기
                        java_class = self._find_class_by_namespace(sql_unit.mapper_ns, project_id)
                        if java_class:
                            # 매소드명으로 메소드 찾기
                            java_method = self.session.query(JavaMethod).filter(
                                and_(
                                    JavaMethod.class_id == java_class.class_id,
                                    JavaMethod.name == sql_unit.stmt_id
                                )
                            ).first()
                            
                            if java_method:
                                edge = DependencyEdge(
                                    src_type='method',
                                    src_id=java_method.method_id,
                                    dst_type='sql_unit',
                                    dst_id=sql_unit.sql_id,
                                    edge_kind='calls_sql',
                                    confidence=0.9,  # MyBatis는 명시적 매핑이므로 높은 신뢰도
                                    metadata={'mapper_namespace': sql_unit.mapper_ns, 'statement_id': sql_unit.stmt_id}
                                )
                                edges.append(edge)
                    
                    # SQL 유닛이 사용하는 테이블 관계 분석
                    table_edges = self._analyze_sql_unit_table_usage(sql_unit)
                    edges.extend(table_edges)
                
                except Exception as e:
                    print(f"Error analyzing SQL unit {sql_unit.sql_id}: {e}")
        
        return edges
    
    def _find_class_by_namespace(self, namespace: str, project_id: int) -> Optional[JavaClass]:
        """네임스페이스로 Java 클래스 찾기"""
        # 네임스페이스를 패키지명.클래스명으로 분리
        if '.' not in namespace:
            return None
        
        class_name = namespace.split('.')[-1]
        
        # 클래스명으로 검색
        java_class = self.session.query(JavaClass).join(File).filter(
            and_(
                File.project_id == project_id,
                JavaClass.name == class_name
            )
        ).first()
        
        return java_class
    
    def _analyze_sql_unit_table_usage(self, sql_unit: SQLUnit) -> List[DependencyEdge]:
        """SQL 유닛의 테이블 사용 분석"""
        edges = []
        
        try:
            # SQL 유닛의 조인과 필터에서 테이블 정보 추출
            joins = self.session.query(Join).filter(Join.sql_id == sql_unit.sql_id).all()
            
            for join in joins:
                # 조인에 참여하는 테이블들 찾기
                if join.l_table:
                    table = self.session.query(DBTable).filter(
                        DBTable.table_name.ilike(join.l_table)
                    ).first()
                    if table:
                        edge = DependencyEdge(
                            src_type='sql_unit',
                            src_id=sql_unit.sql_id,
                            dst_type='table',
                            dst_id=table.table_id,
                            edge_kind='reads_table',
                            confidence=join.confidence or 0.7,
                            metadata={'join_type': 'left_table'}
                        )
                        edges.append(edge)
                
                if join.r_table:
                    table = self.session.query(DBTable).filter(
                        DBTable.table_name.ilike(join.r_table)
                    ).first()
                    if table:
                        edge = DependencyEdge(
                            src_type='sql_unit',
                            src_id=sql_unit.sql_id,
                            dst_type='table',
                            dst_id=table.table_id,
                            edge_kind='reads_table',
                            confidence=join.confidence or 0.7,
                            metadata={'join_type': 'right_table'}
                        )
                        edges.append(edge)
        
        except Exception as e:
            print(f"Error analyzing SQL unit table usage: {e}")
        
        return edges
    
    def analyze_jsp_dependencies(self, project_id: int) -> List[DependencyEdge]:
        """JSP 의존성 분석"""
        edges = []
        
        # JSP 파일들 조회
        jsp_files = self.session.query(File).filter(
            and_(File.project_id == project_id, File.language == 'jsp')
        ).all()
        
        for file_obj in jsp_files:
            try:
                with open(file_obj.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # JSP include 관계 분석
                includes = self._extract_jsp_includes(content)
                for included_file in includes:
                    target_file = self._find_file_by_path_pattern(included_file, project_id)
                    if target_file:
                        edge = DependencyEdge(
                            src_type='file',
                            src_id=file_obj.file_id,
                            dst_type='file',
                            dst_id=target_file.file_id,
                            edge_kind='includes',
                            confidence=0.9,
                            metadata={'include_path': included_file}
                        )
                        edges.append(edge)
                
                # JSP에서 Java 클래스 사용 분석 (scriptlet에서)
                java_classes = self._extract_java_usage_from_jsp(content)
                for class_name in java_classes:
                    java_class = self._find_class_by_simple_name(class_name, project_id)
                    if java_class:
                        edge = DependencyEdge(
                            src_type='file',
                            src_id=file_obj.file_id,
                            dst_type='class',
                            dst_id=java_class.class_id,
                            edge_kind='uses_class',
                            confidence=0.6,  # 낮은 신뢰도 (동적 특성)
                            metadata={'usage_type': 'jsp_scriptlet'}
                        )
                        edges.append(edge)
            
            except Exception as e:
                print(f"Error analyzing JSP dependencies in {file_obj.path}: {e}")
        
        return edges
    
    def _extract_jsp_includes(self, content: str) -> List[str]:
        """JSP include 추출"""
        includes = []
        
        # jsp:include와 @include 패턴
        patterns = [
            r'<jsp:include\s+page="([^"]+)"',
            r'<%@\s*include\s+file="([^"]+)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            includes.extend(matches)
        
        return includes
    
    def _extract_java_usage_from_jsp(self, content: str) -> List[str]:
        """JSP에서 Java 클래스 사용 추출"""
        java_classes = []
        
        # 간단한 패턴으로 클래스 사용 추출
        patterns = [
            r'new\s+([A-Z][A-Za-z0-9]*)\s*\(',  # new ClassName()
            r'([A-Z][A-Za-z0-9]*)\s*\.',  # ClassName.method
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            java_classes.extend(matches)
        
        return list(set(java_classes))
    
    def _find_file_by_path_pattern(self, path_pattern: str, project_id: int) -> Optional[File]:
        """경로 패턴으로 파일 찾기"""
        files = self.session.query(File).filter(File.project_id == project_id).all()
        
        for file_obj in files:
            if path_pattern in file_obj.path or file_obj.path.endswith(path_pattern):
                return file_obj
        
        return None
    
    def _find_class_by_simple_name(self, class_name: str, project_id: int) -> Optional[JavaClass]:
        """단순 클래스명으로 찾기"""
        return self.session.query(JavaClass).join(File).filter(
            and_(
                File.project_id == project_id,
                JavaClass.name == class_name
            )
        ).first()
    
    def create_dependency_edges(self, project_id: int) -> Dict[str, int]:
        """모든 의존성 분석 및 엣지 생성"""
        print("Analyzing dependencies...")
        
        # 기존 의존성 엣지 삭제 (재분석)
        self.session.query(Edge).filter(
            Edge.src_id.in_(
                self.session.query(File.file_id).filter(File.project_id == project_id)
            )
        ).delete(synchronize_session=False)
        
        # 각 종류별 의존성 분석
        java_call_edges = self.analyze_java_method_calls(project_id)
        java_db_edges = self.analyze_java_database_usage(project_id)
        mybatis_edges = self.analyze_mybatis_sql_relationships(project_id)
        jsp_edges = self.analyze_jsp_dependencies(project_id)
        
        # 모든 엣지 수집
        all_edges = java_call_edges + java_db_edges + mybatis_edges + jsp_edges
        
        # 데이터베이스에 저장
        edges_created = 0
        for dep_edge in all_edges:
            try:
                edge = Edge(
                    src_type=dep_edge.src_type,
                    src_id=dep_edge.src_id,
                    dst_type=dep_edge.dst_type,
                    dst_id=dep_edge.dst_id,
                    edge_kind=dep_edge.edge_kind,
                    confidence=dep_edge.confidence
                )
                self.session.add(edge)
                edges_created += 1
            except Exception as e:
                print(f"Error creating edge: {e}")
        
        self.session.commit()
        
        return {
            'java_method_calls': len(java_call_edges),
            'java_database_usage': len(java_db_edges),
            'mybatis_relationships': len(mybatis_edges),
            'jsp_dependencies': len(jsp_edges),
            'total_edges_created': edges_created
        }
    
    def get_dependency_statistics(self, project_id: int) -> Dict[str, Any]:
        """의존성 통계 조회"""
        stats = {}
        
        # 엣지 종류별 통계
        edge_kinds = self.session.query(Edge.edge_kind, self.session.query(Edge).filter(
            Edge.src_id.in_(
                self.session.query(File.file_id).filter(File.project_id == project_id)
            )
        ).count().label('count')).group_by(Edge.edge_kind).all()
        
        for edge_kind, count in edge_kinds:
            stats[f'{edge_kind}_count'] = count
        
        return stats


# 고급 의존성 분석 (향후 확장)
class AdvancedDependencyAnalyzer:
    """고급 의존성 분석기 (향후 구현)"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze_data_flow(self, project_id: int) -> List[DependencyEdge]:
        """데이터 플로우 분석 (향후 구현)"""
        # TODO: Source-to-Sink 데이터 흐름 추적
        return []
    
    def analyze_transitive_dependencies(self, project_id: int) -> Dict[str, Any]:
        """전이적 의존성 분석 (향후 구현)"""
        # TODO: 다단계 의존성 체인 분석
        return {}
    
    def analyze_circular_dependencies(self, project_id: int) -> List[Dict]:
        """순환 의존성 분석 (향후 구현)"""
        # TODO: 순환 참조 탐지
        return []


if __name__ == "__main__":
    # 테스트 코드
    from ..models.database import create_database_engine
    
    engine, SessionLocal = create_database_engine("sqlite:///./data/test_metadata.db")
    
    with SessionLocal() as session:
        analyzer = DependencyAnalyzer(session)
        
        # 가상의 프로젝트 ID로 테스트
        project_id = 1
        
        # 의존성 분석 실행
        results = analyzer.create_dependency_edges(project_id)
        print(f"Dependency analysis results: {results}")
        
        # 통계 조회
        stats = analyzer.get_dependency_statistics(project_id)
        print(f"Dependency statistics: {stats}")