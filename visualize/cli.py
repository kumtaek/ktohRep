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


def main():
    p = argparse.ArgumentParser(prog='visualize', description='Source Analyzer Visualization Tool')
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--project-id', type=int, required=True, help='Project ID')
        sp.add_argument('--out', required=True, help='Output HTML path')
        sp.add_argument('--min-confidence', type=float, default=0.5, help='Minimum confidence threshold')
        sp.add_argument('--max-nodes', type=int, default=2000, help='Maximum nodes to display')
        # Logging options
        sp.add_argument('-v', '--verbose', action='count', default=0, 
                       help='Increase verbosity: -v=INFO, -vv=DEBUG')
        sp.add_argument('-q', '--quiet', action='store_true', 
                       help='Quiet mode: only show warnings and errors')
        sp.add_argument('--log-file', help='Log to file instead of stderr')
        # Export options
        sp.add_argument('--export-json', help='Export data as JSON to specified path')
        sp.add_argument('--export-csv-dir', help='Export data as CSV files to specified directory')
    
    # Graph command
    g = sub.add_parser('graph', help='Generate dependency graph')
    add_common(g)
    g.add_argument('--kinds', default='use_table,include,extends,implements', 
                   help='Edge kinds to include (comma-separated)')
    g.add_argument('--focus', help='Start node (name/path/table)')
    g.add_argument('--depth', type=int, default=2, help='Maximum depth from focus node')

    # ERD command
    e = sub.add_parser('erd', help='Generate ERD')
    add_common(e)
    e.add_argument('--tables', help='Specific tables to include (comma-separated)')
    e.add_argument('--owners', help='Specific schema owners (comma-separated)')
    e.add_argument('--from-sql', help='Generate ERD from SQL (format: mapper_ns:stmt_id)')

    # Component diagram command
    c = sub.add_parser('component', help='Generate component diagram')
    add_common(c)

    # Sequence diagram command
    s = sub.add_parser('sequence', help='Generate sequence diagram')
    add_common(s)
    s.add_argument('--start-file', help='Starting file path')
    s.add_argument('--start-method', help='Starting method name')
    s.add_argument('--depth', type=int, default=3, help='Maximum call depth')

    try:
        args = p.parse_args()
        logger = setup_logging(args)
        
        logger.info(f"Starting visualization generation: {args.cmd}")
        logger.debug(f"Arguments: {vars(args)}")
        
        kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []

        # Generate visualization data
        if args.cmd == 'graph':
            logger.info(f"Generating dependency graph for project {args.project_id}")
            data = build_dependency_graph_json(args.project_id, kinds, args.min_confidence, 
                                             args.focus, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            
        elif args.cmd == 'erd':
            logger.info(f"Generating ERD for project {args.project_id}")
            data = build_erd_json(args.project_id, args.tables, args.owners, args.from_sql)
            html = render_html('erd_view.html', data)
            
        elif args.cmd == 'component':
            logger.info(f"Generating component diagram for project {args.project_id}")
            data = build_component_graph_json(args.project_id, args.min_confidence, args.max_nodes)
            html = render_html('graph_view.html', data)
            
        else:  # sequence
            logger.info(f"Generating sequence diagram for project {args.project_id}")
            data = build_sequence_graph_json(args.project_id, args.start_file, 
                                           args.start_method, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)

        logger.debug(f"Generated {len(data.get('nodes', []))} nodes and {len(data.get('edges', []))} edges")

        # Export data if requested
        if args.export_json:
            logger.info(f"Exporting JSON to {args.export_json}")
            export_json(data, args.export_json, logger)
            
        if args.export_csv_dir:
            logger.info(f"Exporting CSV to {args.export_csv_dir}")
            export_csv(data, args.export_csv_dir, logger)

        # Generate and save HTML
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"Visualization saved to: {output_path.absolute()}")
        
    except KeyboardInterrupt:
        print('Interrupted by user', file=sys.stderr)
        return 130
    except SystemExit as e:
        # argparse error
        return e.code if isinstance(e.code, int) else 2
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        print("Check: file paths, permissions, and --project-id argument", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error during execution: {e}", file=sys.stderr)
        print("Check: input arguments, data preparation status, use -v for verbose logging", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())