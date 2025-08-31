#!/usr/bin/env python3
"""
Debug script to analyze what's in the database
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'phase1'))

from visualize.data_access import VizDB
import yaml


def main():
    project_name = 'sampleSrc'
    
    # Load configuration
    config_path = Path('config/config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # Replace project name in config
        config_str = json.dumps(full_config)
        config_str = config_str.replace('{project_name}', project_name)
        full_config = json.loads(config_str)
        
        project_config = full_config.get('database', {}).get('project', {
            'type': 'sqlite',
            'sqlite': {
                'path': f'./project/{project_name}/data/metadata.db',
                'wal_mode': True
            }
        })
    else:
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
        # Create database connection - VizDB expects the full config structure
        full_db_config = {'database': {'project': project_config}}
        db = VizDB(full_db_config, project_name)
        
        with db.dbm.get_session() as session:
            from models.database import Project, Method, Class, File, Edge
            
            # Get project ID
            project = session.query(Project).filter(Project.name == project_name).first()
            if not project:
                print(f'Error: Project {project_name} not found in database')
                return 1
            project_id = project.project_id
            print(f'Project ID: {project_id}')
            
            # Count basic entities
            file_count = session.query(File).filter(File.project_id == project_id).count()
            class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
            method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            edge_count = session.query(Edge).filter(Edge.project_id == project_id).count()
            
            print(f'\nDatabase contents:')
            print(f'  Files: {file_count}')
            print(f'  Classes: {class_count}')
            print(f'  Methods: {method_count}')
            print(f'  Edges: {edge_count}')
            
            # Show sample methods
            methods = session.query(Method).join(Class).join(File).filter(
                File.project_id == project_id
            ).limit(10).all()
            
            print(f'\nSample methods:')
            for method in methods:
                print(f'  {method.class_.fqn}.{method.name}() - ID: {method.method_id}')
            
            # Show edge types
            from sqlalchemy import func
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