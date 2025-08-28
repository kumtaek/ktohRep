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
                  label_max: int = 20, erd_cols_max: int = 10) -> None:
    """Mermaid/Markdown ?대낫?닿린 (?뺤옣?먯뿉 ?곕씪 .md ?먮뒗 .mmd)"""
    try:
        exporter = MermaidExporter(label_max=label_max, erd_cols_max=erd_cols_max)
        
        # Prepare metadata
        meta_info = metadata or {}
        title = f"Source Analyzer {diagram_type.upper()} Diagram"
        if meta_info.get('project_id'):
            title += f" (Project {meta_info['project_id']})"

        out_path = Path(markdown_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # ?뺤옣?먯뿉 ?곕씪 ?대낫?닿린 ?뺥깭 寃곗젙
        if out_path.suffix.lower() in ['.mmd', '.mermaid']:
            content = exporter.export_mermaid(data, diagram_type)
        else:
            content = exporter.export_to_markdown(data, diagram_type, title, meta_info)
        
        # Write to file
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Mermaid/Markdown ?대낫?닿린 ?꾨즺: {out_path.absolute()}")
        
    except Exception as e:
        logger.error(f"Mermaid/Markdown ?대낫?닿린 ?ㅽ뙣: {e}")
        raise


def main():
    p = argparse.ArgumentParser(prog='visualize', description='Source Analyzer 시각화 도구')
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--project-id', type=int, required=True, help='프로젝트 ID')
        sp.add_argument('--out', required=True, help='異쒕젰 HTML 寃쎈줈')
        sp.add_argument('--min-confidence', type=float, default=0.5, help='理쒖냼 ?좊ː???꾧퀎媛?)
        sp.add_argument('--max-nodes', type=int, default=2000, help='理쒕? ?몃뱶 ??)
        # Mermaid ?듭뀡
        sp.add_argument('--mermaid-label-max', type=int, default=20, help='Mermaid ?쇰꺼 理쒕? 湲몄씠')
        sp.add_argument('--mermaid-erd-max-cols', type=int, default=10, help='Mermaid ERD 而щ읆 理쒕? ?쒓린 ??)
        # Logging options
        sp.add_argument('-v', '--verbose', action='count', default=0, 
                       help='濡쒓렇 ?곸꽭??利앷?: -v=INFO, -vv=DEBUG')
        sp.add_argument('-q', '--quiet', action='store_true', 
                       help='議곗슜 紐⑤뱶: 寃쎄퀬/?ㅻ쪟留?異쒕젰')
        sp.add_argument('--log-file', help='?쒖??ㅻ쪟 ????뚯씪濡?濡쒓퉭')
        # Export options
        sp.add_argument('--export-json', help='JSON?쇰줈 ?대낫?닿린(?뚯씪 寃쎈줈)')
        sp.add_argument('--export-csv-dir', help='CSV濡??대낫?닿린(?붾젆?좊━ 寃쎈줈)')
        sp.add_argument('--export-mermaid', help='Mermaid/Markdown?쇰줈 ?대낫?닿린(.md/.mmd 寃쎈줈)')
    
    # Graph command
    g = sub.add_parser('graph', help='?섏〈??洹몃옒???앹꽦')
    add_common(g)
    g.add_argument('--kinds', default='use_table,include,extends,implements', 
                   help='?ы븿???ｌ? 醫낅쪟(肄ㅻ쭏 援щ텇)')
    g.add_argument('--focus', help='?쒖옉 ?몃뱶(?대쫫/寃쎈줈/?뚯씠釉?')
    g.add_argument('--depth', type=int, default=2, help='?ъ빱??湲곗? 理쒕? 源딆씠')

    # ERD command
    e = sub.add_parser('erd', help='ERD ?앹꽦')
    add_common(e)
    e.add_argument('--tables', help='?ы븿???뚯씠釉?紐⑸줉(肄ㅻ쭏 援щ텇)')
    e.add_argument('--owners', help='?ы븿???ㅽ궎留??뚯쑀??紐⑸줉(肄ㅻ쭏 援щ텇)')
    e.add_argument('--from-sql', help='?뱀젙 SQL 湲곗? ERD (?뺤떇: mapper_ns:stmt_id)')

    # Component diagram command
    c = sub.add_parser('component', help='而댄룷?뚰듃 ?ㅼ씠?닿렇???앹꽦')
    add_common(c)

    # Sequence diagram command
    s = sub.add_parser('sequence', help='?쒗???ㅼ씠?닿렇???앹꽦')
    add_common(s)
    s.add_argument('--start-file', help='?쒖옉 ?뚯씪 寃쎈줈')
    s.add_argument('--start-method', help='?쒖옉 硫붿꽌???대쫫')
    s.add_argument('--depth', type=int, default=3, help='理쒕? ?몄텧 源딆씠')

    try:
        args = p.parse_args()
        logger = setup_logging(args)
        
        logger.info(f"?쒓컖???앹꽦 ?쒖옉: {args.cmd}")
        logger.debug(f"?몄옄: {vars(args)}")
        
        kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []

        # Generate visualization data
        if args.cmd == 'graph':
            logger.info(f"?섏〈??洹몃옒???앹꽦: ?꾨줈?앺듃 {args.project_id}")
            data = build_dependency_graph_json(args.project_id, kinds, args.min_confidence, 
                                             args.focus, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'graph'
            
        elif args.cmd == 'erd':
            logger.info(f"ERD ?앹꽦: ?꾨줈?앺듃 {args.project_id}")
            data = build_erd_json(args.project_id, args.tables, args.owners, args.from_sql)
            html = render_html('erd_view.html', data)
            diagram_type = 'erd'
            
        elif args.cmd == 'component':
            logger.info(f"而댄룷?뚰듃 ?ㅼ씠?닿렇???앹꽦: ?꾨줈?앺듃 {args.project_id}")
            data = build_component_graph_json(args.project_id, args.min_confidence, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'component'
            
        else:  # sequence
            logger.info(f"?쒗???ㅼ씠?닿렇???앹꽦: ?꾨줈?앺듃 {args.project_id}")
            data = build_sequence_graph_json(args.project_id, args.start_file, 
                                           args.start_method, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            diagram_type = 'sequence'

        logger.debug(f"Generated {len(data.get('nodes', []))} nodes and {len(data.get('edges', []))} edges")

        # Export data if requested
        if args.export_json:
            logger.info(f"JSON ?대낫?닿린: {args.export_json}")
            export_json(data, args.export_json, logger)
            
        if args.export_csv_dir:
            logger.info(f"CSV ?대낫?닿린: {args.export_csv_dir}")
            export_csv(data, args.export_csv_dir, logger)

        if args.export_mermaid:
            logger.info(f"Mermaid/Markdown ?대낫?닿린: {args.export_mermaid}")
            export_mermaid(data, args.export_mermaid, diagram_type, logger, {'project_id': args.project_id}, label_max=getattr(args, 'mermaid_label_max', 20), erd_cols_max=getattr(args, 'mermaid_erd_max_cols', 10))

        # Generate and save HTML
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"?쒓컖??HTML ??? {output_path.absolute()}")
        
    except KeyboardInterrupt:
        print('?ъ슜?먯뿉 ?섑빐 以묐떒??, file=sys.stderr)
        return 130
    except SystemExit as e:
        # argparse error
        return e.code if isinstance(e.code, int) else 2
    except FileNotFoundError as e:
        print(f"?ㅻ쪟: ?뚯씪??李얠쓣 ???놁뒿?덈떎: {e}", file=sys.stderr)
        print("?뺤씤: ?뚯씪 寃쎈줈, 沅뚰븳, --project-id ?몄옄", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"?ㅻ쪟: ?ㅽ뻾 以??덇린移?紐삵븳 ?ㅻ쪟: {e}", file=sys.stderr)
        print("?뺤씤: ?낅젰 ?몄옄, ?곗씠??以鍮??곹깭, -v 濡쒓퉭 ?듭뀡", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

