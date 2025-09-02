#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 디버깅 및 분석 스크립트
데이터베이스 내용을 분석하고 디버깅 정보를 제공하는 도구
"""
import sys
import json
from pathlib import Path

# 프로젝트 루트 경로를 시스템 경로에 추가합니다
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'phase1'))

from visualize.data_access import VizDB
import yaml


def main():
    """
    메인 실행 함수
    데이터베이스 연결 및 디버깅 정보 출력
    """
    project_name = 'sampleSrc'  # 기본 프로젝트명 설정
    
    # 설정 파일을 로드합니다.
    config_path = Path('config/config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # 설정 파일 내 프로젝트 이름을 대체합니다.
        config_str = json.dumps(full_config)
        config_str = config_str.replace('{project_name}', project_name)
        full_config = json.loads(config_str)
        
        # 데이터베이스 설정을 가져옵니다.
        project_config = full_config.get('database', {}).get('project', {
            'type': 'sqlite',
            'sqlite': {
                'path': f'./project/{project_name}/data/metadata.db',
                'wal_mode': True
            }
        })
    else:
        # 설정 파일이 없는 경우 기본 데이터베이스 경로를 설정합니다.
        project_config = {
            'type': 'sqlite',
            'sqlite': {
                'path': f'./project/{project_name}/data/metadata.db',
                'wal_mode': True
            }
        }

    db_path = project_config['sqlite']['path']
    print(f'Using database: {db_path}')
    
    if not Path(db_path).exists():
        print(f'Error: Database not found at {db_path}')
        return 1

    try:
        # 데이터베이스 연결을 생성합니다. VizDB는 전체 설정 구조를 예상합니다.
        full_db_config = {'database': {'project': project_config}}
        db = VizDB(full_db_config, project_name)
        
        with db.dbm.get_session() as session:
            from models.database import Base, Project, Method, Class, File, Edge, SqlUnit, Join, DbTable, DbColumn, DbPk, DbView, RequiredFilter, Summary, EnrichmentLog, Chunk, Embedding, JavaImport, EdgeHint, Relatedness, VulnerabilityFix, CodeMetric, Duplicate, DuplicateInstance, ParseResultModel
            from sqlalchemy import inspect, func

            # 프로젝트 ID를 가져옵니다.
            project = session.query(Project).filter(Project.name == project_name).first()
            if not project:
                print(f'Error: Project {project_name} not found in database')
                return 1
            project_id = project.project_id
            print(f'Project ID: {project_id}')

            # 모든 테이블의 레코드 수를 출력합니다.
            inspector = inspect(session.bind)
            table_names = inspector.get_table_names()

            print(f'\n--- 모든 테이블 레코드 수 ---')
            table_counts = {}
            for table_name in table_names:
                # Base.metadata.tables에서 테이블 객체를 가져옵니다.
                table_class = None
                for mapper in Base.registry.mappers:
                    if mapper.local_table.name == table_name:
                        table_class = mapper.class_
                        break
                
                if table_class:
                    count = session.query(table_class).count()
                    table_counts[table_name] = count
                    print(f'  {table_name}: {count} records')
                else:
                    print(f'  {table_name}: (클래스 매핑을 찾을 수 없음)')

            print(f'\n--- 프로젝트 관련 엔티티 수 (project_id={project_id}) ---')
            file_count = session.query(File).filter(File.project_id == project_id).count()
            class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
            method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            edge_count = session.query(Edge).filter(Edge.project_id == project_id).count()
            sql_unit_count = session.query(SqlUnit).join(File).filter(File.project_id == project_id).count()
            join_count = session.query(Join).join(SqlUnit).join(File).filter(File.project_id == project_id).count()
            filter_count = session.query(RequiredFilter).join(SqlUnit).join(File).filter(File.project_id == project_id).count()
            summary_count = session.query(Summary).filter(Summary.target_type.in_(['file', 'class', 'method', 'sql_unit'])).count()
            enrichment_log_count = session.query(EnrichmentLog).filter(EnrichmentLog.target_type.in_(['file', 'class', 'method', 'sql_unit'])).count()
            chunk_count = session.query(Chunk).filter(Chunk.target_type.in_(['file', 'class', 'method', 'sql_unit'])).count()
            embedding_count = session.query(Embedding).join(Chunk).filter(Chunk.target_type.in_(['file', 'class', 'method', 'sql_unit'])).count()
            java_import_count = session.query(JavaImport).join(File).filter(File.project_id == project_id).count()
            edge_hint_count = session.query(EdgeHint).filter(EdgeHint.project_id == project_id).count()
            relatedness_count = session.query(Relatedness).filter(Relatedness.project_id == project_id).count()
            vulnerability_fix_count = session.query(VulnerabilityFix).filter(VulnerabilityFix.target_type.in_(['file', 'class', 'method', 'sql_unit'])).count()
            code_metric_count = session.query(CodeMetric).filter(CodeMetric.target_type.in_(['file', 'class', 'method'])).count()
            duplicate_count = session.query(Duplicate).count()
            duplicate_instance_count = session.query(DuplicateInstance).join(File).filter(File.project_id == project_id).count()
            parse_result_count = session.query(ParseResultModel).join(File).filter(File.project_id == project_id).count()

            print(f'  Files: {file_count}')
            print(f'  Classes: {class_count}')
            print(f'  Methods: {method_count}')
            print(f'  Edges: {edge_count}')
            print(f'  SQL Units: {sql_unit_count}')
            print(f'  Joins: {join_count}')
            print(f'  Required Filters: {filter_count}')
            print(f'  Summaries: {summary_count}')
            print(f'  Enrichment Logs: {enrichment_log_count}')
            print(f'  Chunks: {chunk_count}')
            print(f'  Embeddings: {embedding_count}')
            print(f'  Java Imports: {java_import_count}')
            print(f'  Edge Hints: {edge_hint_count}')
            print(f'  Relatedness: {relatedness_count}')
            print(f'  Vulnerability Fixes: {vulnerability_fix_count}')
            print(f'  Code Metrics: {code_metric_count}')
            print(f'  Duplicates: {duplicate_count}')
            print(f'  Duplicate Instances: {duplicate_instance_count}')
            print(f'  Parse Results: {parse_result_count}')

            # Show sample SQL Units
            sql_units = session.query(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).limit(5).all()
            
            print(f'\nSample SQL Units:')
            for sql_unit in sql_units:
                print(f'  {sql_unit.mapper_ns}.{sql_unit.stmt_id} ({sql_unit.stmt_kind}) - ID: {sql_unit.sql_id}')
                
            # Show sample Joins
            joins = session.query(Join).join(SqlUnit).join(File).filter(
                File.project_id == project_id
            ).limit(5).all()
            
            print(f'\nSample Joins:')
            for join in joins:
                print(f'  SQL ID: {join.sql_id}, {join.l_table}.{join.l_col} {join.op} {join.r_table}.{join.r_col}')
            
            # Show sample methods
            methods = session.query(Method).join(Class).join(File).filter(
                File.project_id == project_id
            ).limit(10).all()
            
            print(f'\nSample methods:')
            for method in methods:
                print(f'  {method.class_.fqn}.{method.name}() - ID: {method.method_id}')
            
            # Show edge types
            edge_types = session.query(Edge.edge_kind, func.count(Edge.edge_id)).filter(
                Edge.project_id == project_id
            ).group_by(Edge.edge_kind).all()
            
            print(f'\nEdge types:')
            for edge_type, count in edge_types:
                print(f'  {edge_type}: {count}')
            
            # Show some call edges
            call_edges = session.query(Edge).filter(
                Edge.project_id == project_id,
                Edge.edge_kind.in_(['call', 'call_unresolved'])
            ).limit(5).all()
            
            print(f'\nSample call edges:')
            for edge in call_edges:
                src_method = session.query(Method).filter(Method.method_id == edge.src_id).first() if edge.src_id else None
                dst_method = session.query(Method).filter(Method.method_id == edge.dst_id).first() if edge.dst_id else None
                
                src_name = f'{src_method.class_.fqn}.{src_method.name}()' if src_method else f'Unknown({edge.src_id})'
                dst_name = f'{dst_method.class_.fqn}.{dst_method.name}()' if dst_method else f'Unknown({edge.dst_id})'
                
                print(f'  {edge.edge_kind}: {src_name} -> {dst_name}')
                
        return 0

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())