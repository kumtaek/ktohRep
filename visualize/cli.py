# visualize/cli.py
import argparse
import json
import logging
import sys
import csv
from pathlib import Path
from typing import Dict, Any, List

from .builders.dependency_graph import build_dependency_graph_json
from .builders.erd import build_erd_json
from .builders.component_diagram import build_component_graph_json
from .builders.sequence_diagram import build_sequence_graph_json
from .templates.render import render_html
from .exporters.mermaid_exporter import MermaidExporter


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
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--project-name', required=True, help='프로젝트 이름 (DB 스키마 로드용)')
        sp.add_argument('--export-html', help='출력 HTML 경로 (미지정 시 HTML 생성 생략)')
        sp.add_argument('--min-confidence', type=float, default=0.5, help='최소 신뢰도 임계값')
        sp.add_argument('--max-nodes', type=int, default=2000, help='최대 노드 수')
        # Mermaid 옵션
        sp.add_argument('--mermaid-label-max', type=int, default=20, help='Mermaid 라벨 최대 길이')
        sp.add_argument('--mermaid-erd-max-cols', type=int, default=10, help='Mermaid ERD 컬럼 최대 표기 수')
        # Export strategy options
        sp.add_argument('--export-strategy', choices=['full', 'balanced', 'minimal'], default='balanced', help='Export strategy')
        sp.add_argument('--class-methods-max', type=int, default=10, help='Class diagram methods max')
        sp.add_argument('--class-attrs-max', type=int, default=10, help='Class diagram attributes max')
        sp.add_argument('--keep-edge-kinds', default='include,call,use_table', help='Edge kinds to keep')
        # Logging options
        sp.add_argument('-v', '--verbose', action='count', default=0, 
                       help='로그 상세화 증가: -v=INFO, -vv=DEBUG')
        sp.add_argument('-q', '--quiet', action='store_true', 
                       help='조용 모드: 경고/오류만 출력')
        sp.add_argument('--log-file', help='로그를 파일로 기록')
        # Export options
        sp.add_argument('--export-json', help='JSON으로 내보내기(파일 경로)')
        sp.add_argument('--export-csv-dir', help='CSV로 내보내기(디렉토리 경로)')
        sp.add_argument('--export-mermaid', help='Mermaid/Markdown으로 내보내기(.md/.mmd 경로)')
    
    # Graph command
    g = sub.add_parser('graph', help='의존성 그래프 생성')
    add_common(g)
    g.add_argument('--kinds', default='use_table,include,extends,implements', 
                   help='포함할 엣지 종류(콤마 구분)')
    g.add_argument('--focus', help='시작 노드(이름/경로/테이블)')
    g.add_argument('--depth', type=int, default=2, help='중심 기준 최대 깊이')

    # ERD command
    e = sub.add_parser('erd', help='ERD 생성')
    add_common(e)
    e.add_argument('--tables', help='포함할 테이블명 목록(콤마 구분)')
    e.add_argument('--owners', help='포함할 스키마/소유자 목록(콤마 구분)')
    e.add_argument('--from-sql', help='특정 SQL 기준 ERD (형식: mapper_ns:stmt_id)')

    # Component diagram command
    c = sub.add_parser('component', help='컴포넌트 다이어그램 생성')
    add_common(c)

    # Sequence diagram command
    s = sub.add_parser('sequence', help='시퀀스 다이어그램 생성')
    add_common(s)
    s.add_argument('--start-file', help='시작 파일 경로')
    s.add_argument('--start-method', help='시작 메서드 이름')
    s.add_argument('--depth', type=int, default=3, help='최대 추적 깊이')

    # Class diagram command (NEW)
    cl = sub.add_parser('class', help='클래스 다이어그램 생성')
    add_common(cl)
    cl.add_argument('--modules', help='포함할 모듈/파일 목록(콤마 구분)')
    cl.add_argument('--include-private', action='store_true', help='private 멤버 포함')
    cl.add_argument('--max-methods', type=int, default=10, help='클래스당 최대 메서드 표시 수')

    try:
        args = p.parse_args()
        logger = setup_logging(args)

        # Validate that at least one export option is provided
        if not args.export_html and not args.export_mermaid:
            logger.error("오류: --export-html 또는 --export-mermaid 중 하나는 반드시 지정해야 합니다.")
            return 1

        # Load config.yaml with project name substitution
        import yaml
        import os
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = f.read()
                
            # Project name substitution if provided
            if hasattr(args, 'project_name') and args.project_name:
                raw = raw.replace('{project_name}', args.project_name)
            
            config = yaml.safe_load(raw) or {}

        logger.info(f"시각화 생성 시작: {args.cmd}")
        logger.debug(f"인자: {vars(args)}")
        
        # Initialize VizDB and get project_id
        from .data_access import VizDB
        db = VizDB(config, args.project_name)
        project_id = db.get_project_id_by_name(args.project_name)
        
        if project_id is None:
            logger.error(f"오류: 프로젝트 '{args.project_name}'를 찾을 수 없습니다. 먼저 프로젝트를 생성해야 합니다.")
            return 1

        kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []

        # Generate visualization data
        if args.cmd == 'graph':
            logger.info(f"의존성 그래프 생성: 프로젝트 {args.project_name} (ID: {project_id})")
            data = build_dependency_graph_json(config, project_id, args.project_name, kinds, args.min_confidence, 
                                             args.focus, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'graph'
            
        elif args.cmd == 'erd':
            logger.info(f"ERD 생성: 프로젝트 {args.project_name} (ID: {project_id})")
            data = build_erd_json(config, project_id, args.project_name, args.tables, args.owners, args.from_sql)
            html = render_html('erd_view.html', data)
            diagram_type = 'erd'
            
        elif args.cmd == 'component':
            logger.info(f"컴포넌트 다이어그램 생성: 프로젝트 {args.project_name} (ID: {project_id})")
            data = build_component_graph_json(config, project_id, args.project_name, args.min_confidence, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'component'
            
        elif args.cmd == 'class':
            logger.info(f"클래스 다이어그램 생성: 프로젝트 {args.project_name} (ID: {project_id})")
            # Import the new class diagram builder
            from .builders.class_diagram import build_class_diagram_json
            data = build_class_diagram_json(config, project_id, args.project_name, args.modules, 
                                          args.include_private, args.max_methods, args.max_nodes)
            html = render_html('class_view.html', data)
            diagram_type = 'class'
            
        else:  # sequence
            logger.info(f"시퀀스 다이어그램 생성: 프로젝트 {args.project_name} (ID: {project_id})")
            data = build_sequence_graph_json(config, project_id, args.project_name, args.start_file, 
                                           args.start_method, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'sequence'

        logger.debug(f"Generated {len(data.get('nodes', []))} nodes and {len(data.get('edges', []))} edges")

        # Export data if requested (with project-based path resolution)
        project_name = getattr(args, 'project_name', None) or 'default'
        visualize_dir = f"./project/{project_name}/output/visualize"
        
        if args.export_json:
            # Make path relative to project visualize directory if not absolute
            json_path = args.export_json
            if not Path(json_path).is_absolute():
                json_path = Path(visualize_dir) / json_path
            logger.info(f"JSON 내보내기: {json_path}")
            export_json(data, str(json_path), logger)
            
        if args.export_csv_dir:
            # Make path relative to project visualize directory if not absolute
            csv_path = args.export_csv_dir
            if not Path(csv_path).is_absolute():
                csv_path = Path(visualize_dir) / csv_path
            logger.info(f"CSV 내보내기: {csv_path}")
            export_csv(data, str(csv_path), logger)

        # Define default filenames based on diagram type
        default_html_names = {
            'graph': 'graph.html',
            'erd': 'erd.html',
            'component': 'components.html',
            'sequence': 'sequence.html',
            'class': 'class.html'
        }
        default_mermaid_names = {
            'graph': 'dependency_graph.md',
            'erd': 'erd.md',
            'component': 'component.md',
            'sequence': 'sequence.md',
            'class': 'class.md'
        }

        # Set default paths if arguments are present but no value is given
        if args.export_html is not None and args.export_html == '':
            args.export_html = default_html_names.get(diagram_type, f'{diagram_type}.html')
        if args.export_mermaid is not None and args.export_mermaid == '':
            args.export_mermaid = default_mermaid_names.get(diagram_type, f'{diagram_type}.md')

        if args.export_mermaid:
            # Make path relative to project visualize directory if not absolute
            mermaid_path = args.export_mermaid
            if not Path(mermaid_path).is_absolute():
                mermaid_path = Path(visualize_dir) / mermaid_path
            logger.info(f"Mermaid/Markdown 내보내기: {mermaid_path}")
            keep_edge_kinds = tuple(args.keep_edge_kinds.split(',')) if hasattr(args, 'keep_edge_kinds') else ("include","call","use_table")
            # Include builder filters for documentation context
            meta_filters = (data.get('metadata') or {}).get('filters') if isinstance(data, dict) else None
            export_mermaid(
                data, str(mermaid_path), diagram_type, logger,
                {'project_id': args.project_id, 'filters': meta_filters}, 
                label_max=getattr(args, 'mermaid_label_max', 20), 
                erd_cols_max=getattr(args, 'mermaid_erd_max_cols', 10),
                class_methods_max=getattr(args, 'class_methods_max', 10),
                class_attrs_max=getattr(args, 'class_attrs_max', 10),
                min_confidence=args.min_confidence,
                keep_edge_kinds=keep_edge_kinds
            )

        # Generate and save HTML (optional with project-based path resolution)
        if args.export_html:
            html_path = args.export_html
            # Make path relative to project visualize directory if not absolute
            if not Path(html_path).is_absolute():
                html_path = Path(visualize_dir) / html_path
            
            output_path = Path(html_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"시각화 HTML 저장: {output_path.absolute()}")
        
    except KeyboardInterrupt:
        print('사용자에 의해 중단됨', file=sys.stderr)
        return 130
    except SystemExit as e:
        # argparse error
        return e.code if isinstance(e.code, int) else 2
    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다: {e}", file=sys.stderr)
        print("확인: 파일 경로, 권한, --project-id 인자", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"오류: 실행 중 예기치 못한 오류: {e}", file=sys.stderr)
        print("확인: 입력 인자, 데이터베이스 상태, -v 로깅 옵션", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
