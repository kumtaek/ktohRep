# visualize/cli.py
import argparse
import json
import logging
import sys
import csv
import shutil
from pathlib import Path
from typing import Dict, Any, List

from .builders.dependency_graph import build_dependency_graph_json
from .builders.erd import build_erd_json
from .builders.component_diagram import build_component_graph_json
from .builders.sequence_diagram import build_sequence_graph_json
from .builders.relatedness_graph import build_relatedness_graph_json, get_relatedness_summary
from .templates.render import render_html
from .exporters.mermaid_exporter import MermaidExporter


def copy_static_files(output_dir: Path) -> None:
    """시각화에 필요한 static 파일들을 output 디렉토리에 복사"""
    # visualize 모듈의 static 디렉토리 경로 (현재 파일 기준으로 상대 경로)
    current_file = Path(__file__)
    static_source_dir = current_file.parent / "static"
    
    if not static_source_dir.exists():
        return
        
    static_target_dir = output_dir / "static"
    
    # 기존 static 디렉토리가 있으면 제거 후 새로 복사
    if static_target_dir.exists():
        shutil.rmtree(static_target_dir)
    
    # static 디렉토리 전체 복사
    shutil.copytree(static_source_dir, static_target_dir)


def setup_logging(args) -> logging.Logger:
    """Setup logging configuration based on command line arguments"""
    # Determine log level
    if args.quiet:
        level = logging.WARNING
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    # Setup handlers
    handlers = []
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding='utf-8'))
    else:
        handlers.append(logging.StreamHandler(sys.stderr))
    
    # Configure logging
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    return logging.getLogger('visualize.cli')


def export_json(data: Dict[str, Any], json_path: str, logger: logging.Logger) -> None:
    """Export visualization data as JSON"""
    try:
        json_file = Path(json_path)
        json_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON exported to: {json_file.absolute()}")
        
    except Exception as e:
        logger.error(f"Failed to export JSON: {e}")
        raise


def export_csv(data: Dict[str, Any], csv_dir: str, logger: logging.Logger) -> None:
    """Export visualization data as CSV files"""
    try:
        csv_path = Path(csv_dir)
        csv_path.mkdir(parents=True, exist_ok=True)
        
        # Export nodes
        nodes = data.get('nodes', [])
        if nodes:
            nodes_file = csv_path / 'nodes.csv'
            with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
                if nodes:
                    fieldnames = ['id', 'label', 'type', 'group']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for node in nodes:
                        row = {k: node.get(k, '') for k in fieldnames}
                        writer.writerow(row)
            
            logger.info(f"Nodes CSV exported to: {nodes_file.absolute()}")
        
        # Export edges
        edges = data.get('edges', [])
        if edges:
            edges_file = csv_path / 'edges.csv'
            with open(edges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'source', 'target', 'kind', 'confidence']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for edge in edges:
                    row = {k: edge.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            logger.info(f"Edges CSV exported to: {edges_file.absolute()}")
        
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")
        raise


def export_mermaid(data: Dict[str, Any], markdown_path: str, diagram_type: str, 
                  logger: logging.Logger, metadata: Dict[str, Any] = None,
                  label_max: int = 20, erd_cols_max: int = 10, 
                  class_methods_max: int = 10, class_attrs_max: int = 10,
                  min_confidence: float = 0.0, keep_edge_kinds: tuple = ("includes","call","use_table")) -> None:
    """Mermaid/Markdown 내보내기 (확장자에 따라 .md 또는 .mmd)"""
    try:
        exporter = MermaidExporter(
            label_max=label_max, 
            erd_cols_max=erd_cols_max,
            class_methods_max=class_methods_max,
            class_attrs_max=class_attrs_max,
            min_confidence=min_confidence,
            keep_edge_kinds=keep_edge_kinds
        )
        
        # Prepare metadata
        meta_info = metadata or {}
        title = f"Source Analyzer {diagram_type.upper()} Diagram"
        if meta_info.get('project_id'):
            title += f" (Project {meta_info['project_id']})"

        out_path = Path(markdown_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 확장자에 따라 내보내기 형태 결정
        if out_path.suffix.lower() in ['.mmd', '.mermaid']:
            content = exporter.export_mermaid(data, diagram_type)
        else:
            content = exporter.export_to_markdown(data, diagram_type, title, meta_info)
        
        # Write to file
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Mermaid/Markdown 내보내기 완료: {out_path.absolute()}")
        
    except Exception as e:
        logger.error(f"Mermaid/Markdown 내보내기 실패: {e}")
        raise

def main():
    p = argparse.ArgumentParser(prog='visualize', description='Source Analyzer 시각화 도구')
    
    # cmd를 subparser 대신 위치 인자로 변경하고, 기본값을 'all'로 설정
    p.add_argument('cmd', nargs='?', default='all', 
                   choices=['all', 'graph', 'erd', 'component', 'sequence', 'class', 'relatedness'],
                   help='생성할 시각화 종류 (기본값: all)')

    # 공통 인자 추가
    p.add_argument('--project-name', required=True, help='프로젝트 이름 (DB 스키마 로드용)')
    p.add_argument('--export-html', nargs='?', const='', default=None, help='출력 HTML 경로 (미지정 시 생성 생략, 값 없이 사용 시 기본 경로)')
    p.add_argument('--min-confidence', type=float, default=0.5, help='최소 신뢰도 임계값')
    p.add_argument('--max-nodes', type=int, default=2000, help='최대 노드 수')
    p.add_argument('--mermaid-label-max', type=int, default=20, help='Mermaid 라벨 최대 길이')
    p.add_argument('--mermaid-erd-max-cols', type=int, default=10, help='Mermaid ERD 컬럼 최대 표기 수')
    p.add_argument('--export-strategy', choices=['full', 'balanced', 'minimal'], default='balanced', help='Export strategy')
    p.add_argument('--class-methods-max', type=int, default=10, help='Class diagram methods max')
    p.add_argument('--class-attrs-max', type=int, default=10, help='Class diagram attributes max')
    p.add_argument('--keep-edge-kinds', default='include,call,use_table', help='Edge kinds to keep')
    p.add_argument('-v', '--verbose', action='count', default=0, help='로그 상세화 증가: -v=INFO, -vv=DEBUG')
    p.add_argument('-q', '--quiet', action='store_true', help='조용 모드: 경고/오류만 출력')
    p.add_argument('--log-file', help='로그를 파일로 기록')
    p.add_argument('--export-json', help='JSON으로 내보내기(파일 경로)')
    p.add_argument('--export-csv-dir', help='CSV로 내보내기(디렉토리 경로)')
    p.add_argument('--export-mermaid', nargs='?', const='', default=None, help='Mermaid/Markdown으로 내보내기(.md/.mmd 경로)')

    # 각 시각화별 특수 인자 추가
    p.add_argument('--kinds', default='use_table,include,extends,implements', help='[graph] 포함할 엣지 종류(콤마 구분)')
    p.add_argument('--focus', help='[graph] 시작 노드(이름/경로/테이블)')
    p.add_argument('--depth', type=int, default=2, help='[graph/sequence] 중심 기준 최대 깊이')
    p.add_argument('--tables', help='[erd] 포함할 테이블명 목록(콤마 구분)')
    p.add_argument('--owners', help='[erd] 포함할 스키마/소유자 목록(콤마 구분)')
    p.add_argument('--from-sql', help='[erd] 특정 SQL 기준 ERD (형식: mapper_ns:stmt_id)')
    p.add_argument('--start-file', help='[sequence] 시작 파일 경로')
    p.add_argument('--start-method', help='[sequence] 시작 메서드 이름')
    p.add_argument('--modules', help='[class] 포함할 모듈/파일 목록(콤마 구분)')
    p.add_argument('--include-private', action='store_true', help='[class] private 멤버 포함')
    p.add_argument('--max-methods', type=int, default=10, help='[class] 클래스당 최대 메서드 표시 수')
    p.add_argument('--min-score', type=float, default=0.5, help='[relatedness] 최소 연관성 점수 임계값 (0.0-1.0)')
    p.add_argument('--cluster-method', default='louvain', help='[relatedness] 클러스터링 방법')
    p.add_argument('--summary', action='store_true', help='[relatedness] 연관성 통계 요약만 출력')

    try:
        args = p.parse_args()
        logger = setup_logging(args)

        commands_to_run = []
        if args.cmd == 'all':
            commands_to_run = ['graph', 'erd', 'component', 'class', 'relatedness']
            logger.info("명령어가 지정되지 않았습니다. 'sequence'를 제외한 모든 시각화를 생성합니다.")
        else:
            commands_to_run.append(args.cmd)

        for cmd_name in commands_to_run:
            logger.info(f"--- {cmd_name.upper()} 시각화 생성 시작 ---")

            # Validate that at least one export option is provided for the specific command
            if args.export_html is None and args.export_mermaid is None:
                args.export_html = '' # Enable default html export for this run
                args.export_mermaid = '' # Enable default mermaid export for this run

            # Load config.yaml with project name substitution
            import yaml
            import os
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
            config = {}
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    raw = f.read()
                if hasattr(args, 'project_name') and args.project_name:
                    raw = raw.replace('{project_name}', args.project_name)
                config = yaml.safe_load(raw) or {}

            # Initialize VizDB and get project_id
            from .data_access import VizDB
            db = VizDB(config, args.project_name)
            project_id = db.get_project_id_by_name(args.project_name)
            
            if project_id is None:
                logger.error(f"오류: 프로젝트 '{args.project_name}'를 찾을 수 없습니다.")
                return 1

            data, html, diagram_type = None, None, cmd_name

            # Generate visualization data based on command
            if cmd_name == 'graph':
                kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []
                data = build_dependency_graph_json(config, project_id, args.project_name, kinds, args.min_confidence, 
                                                 args.focus, args.depth, args.max_nodes)
                html = render_html('graph_view.html', data)
            elif cmd_name == 'erd':
                data = build_erd_json(config, project_id, args.project_name, args.tables, args.owners, args.from_sql)
                html = render_html('erd_view.html', data)
            elif cmd_name == 'component':
                data = build_component_graph_json(config, project_id, args.project_name, args.min_confidence, args.max_nodes)
                html = render_html('graph_view.html', data)
            elif cmd_name == 'class':
                # Create Java class diagram from database information
                from .builders.class_diagram import build_java_class_diagram_json
                data = build_java_class_diagram_json(config, project_id, args.project_name, 
                                                   args.modules, args.max_methods, args.max_nodes)
                html = render_html('class_view.html', data)
            elif cmd_name == 'relatedness':
                if args.summary:
                    summary = get_relatedness_summary(config, project_id, args.project_name)
                    logger.info(f"연관성 통계: {summary}")
                    continue
                data = build_relatedness_graph_json(config, project_id, args.project_name, 
                                                   args.min_score, args.max_nodes, args.cluster_method)
                html = render_html('relatedness_view.html', data)
            elif cmd_name == 'sequence':
                if args.cmd == 'all' and (not args.start_file or not args.start_method):
                    logger.info("'all' 모드에서는 시퀀스 다이어그램을 생성하지 않습니다. --start-file과 --start-method 인자를 지정하여 수동으로 생성해주세요.")
                    continue
                elif not args.start_file or not args.start_method:
                    logger.warning("시퀀스 다이어그램을 생성하려면 --start-file과 --start-method 인자가 반드시 필요합니다.")
                    possible_files = db.get_files_with_methods(project_id, limit=20)
                    if possible_files:
                        logger.info("시작 파일로 사용할 수 있는 파일 목록 (최대 20개):")
                        for f_path in possible_files:
                            print(f"  - {f_path}")
                        logger.info("위 파일 중 하나와 해당 파일의 메소드 이름을 지정하여 다시 시도해주세요.")
                    else:
                        logger.warning("메소드를 포함한 파일을 찾을 수 없습니다. 프로젝트 분석을 먼저 실행하세요.")
                    continue
                data = build_sequence_graph_json(config, project_id, args.project_name, args.start_file, 
                                           args.start_method, args.depth, args.max_nodes)
                html = render_html('graph_view.html', data)
            
            if not data or not html:
                logger.warning(f"'{cmd_name}'에 대한 데이터를 생성하지 못했습니다. 건너뜁니다.")
                continue

            logger.debug(f"Generated {len(data.get('nodes', []))} nodes and {len(data.get('edges', []))} edges for {cmd_name}")

            # Export logic
            project_name_for_path = getattr(args, 'project_name', 'default')
            visualize_dir = f"./output/{project_name_for_path}/visualize"
            
            default_html_names = {'graph': 'graph.html', 'erd': 'erd.html', 'component': 'components.html', 'class': 'class.html', 'relatedness': 'relatedness.html'}
            default_mermaid_names = {'graph': 'dependency_graph.md', 'erd': 'erd.md', 'component': 'component.md', 'class': 'class.md', 'relatedness': 'relatedness.md'}

            current_export_html = args.export_html
            current_export_mermaid = args.export_mermaid

            if current_export_html == '':
                current_export_html = default_html_names.get(diagram_type, f'{diagram_type}.html')
            if current_export_mermaid == '':
                current_export_mermaid = default_mermaid_names.get(diagram_type, f'{diagram_type}.md')

            if current_export_html is not None:
                html_path = Path(visualize_dir) / current_export_html
                html_path.parent.mkdir(parents=True, exist_ok=True)
                
                # static 파일들을 output 디렉토리에 복사
                copy_static_files(html_path.parent)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"시각화 HTML 저장: {html_path.absolute()}")
                logger.info(f"Static 파일 복사 완료: {html_path.parent / 'static'}")

            if current_export_mermaid is not None:
                mermaid_path = Path(visualize_dir) / current_export_mermaid
                logger.info(f"Mermaid/Markdown 내보내기: {mermaid_path}")
                meta_filters = (data.get('metadata') or {}).get('filters')
                export_mermaid(data, str(mermaid_path), diagram_type, logger, {'project_id': project_id, 'filters': meta_filters})

    except KeyboardInterrupt:
        print('사용자에 의해 중단됨', file=sys.stderr)
        return 130
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    except Exception as e:
        logger.error(f"오류: 실행 중 예기치 못한 오류: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())