# visualize/cli.py
import argparse
import json
import os
from pathlib import Path

from .builders.dependency_graph import build_dependency_graph_json
from .builders.erd import build_erd_json
from .builders.component_diagram import build_component_graph_json
from .builders.sequence_diagram import build_sequence_graph_json
from .templates.render import render_html


def main():
    p = argparse.ArgumentParser(prog='visualize', description='Source Analyzer Visualization Tool')
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--project-id', type=int, required=True, help='Project ID')
        sp.add_argument('--out', required=True, help='Output HTML path')
        sp.add_argument('--min-confidence', type=float, default=0.5, help='Minimum confidence threshold')
        sp.add_argument('--max-nodes', type=int, default=2000, help='Maximum nodes to display')
    
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

    args = p.parse_args()
    kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []

    try:
        if args.cmd == 'graph':
            print(f"Generating dependency graph for project {args.project_id}...")
            data = build_dependency_graph_json(args.project_id, kinds, args.min_confidence, 
                                             args.focus, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)
            
        elif args.cmd == 'erd':
            print(f"Generating ERD for project {args.project_id}...")
            data = build_erd_json(args.project_id, args.tables, args.owners, args.from_sql)
            html = render_html('erd_view.html', data)
            
        elif args.cmd == 'component':
            print(f"Generating component diagram for project {args.project_id}...")
            data = build_component_graph_json(args.project_id, args.min_confidence, args.max_nodes)
            html = render_html('graph_view.html', data)
            
        else:  # sequence
            print(f"Generating sequence diagram for project {args.project_id}...")
            data = build_sequence_graph_json(args.project_id, args.start_file, 
                                           args.start_method, args.depth, args.max_nodes)
            html = render_html('graph_view.html', data)

        # Ensure output directory exists
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Visualization saved to: {output_path.absolute()}")
        
    except Exception as e:
        print(f"Error generating visualization: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())