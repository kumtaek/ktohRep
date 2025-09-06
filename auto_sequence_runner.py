#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# auto_sequence_runner.py
# 수동 파라미터 없이 시퀀스 다이어그램을 자동으로 생성하는 스크립트입니다.
# 이 스크립트는 프로젝트의 소스 코드를 분석하여 시퀀스 다이어그램을 만들고 다양한 형식으로 저장합니다.
"""
import sys
import json
from pathlib import Path

# 프로젝트 루트 경로를 시스템 경로에 추가합니다.
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'phase1'))

from visualize.builders.enhanced_sequence_diagram import build_automatic_sequence_diagrams
from visualize.data_access import VizDB
import yaml


def _generate_mermaid_sequence(diagram):
    """
    주어진 다이어그램 데이터로부터 Mermaid 시퀀스 다이어그램 구문을 생성합니다.
    참여자(participants)와 상호작용(interactions) 정보를 기반으로 Mermaid 형식의 문자열을 반환합니다.
    """
    lines = ['sequenceDiagram']
    
    # 다이어그램 참여자를 추가합니다.
    for participant in diagram['participants']:
        pid = participant['id'].replace(':', '_')
        label = participant['label'].replace('"', '\"')
        lines.append(f'    participant {pid} as {label}')
    
    lines.append('')
    
    # 다이어그램 상호작용을 추가합니다.
    for interaction in diagram['interactions']:
        from_id = interaction['from_participant'].replace(':', '_')
        to_id = interaction['to_participant'].replace(':', '_')
        message = interaction['message'].replace('"', '\"')
        
        # 미해결 호출인 경우 점선 화살표를 사용합니다.
        if interaction.get('unresolved', False):
            lines.append(f'    {from_id}-->>+{to_id}: {message}')
        else:
            lines.append(f'    {from_id}->>+{to_id}: {message}')
    
    return '\n'.join(lines)


def _create_fallback_sequence_diagrams(db, project_id: int, project_name: str) -> list:
    """
    Create fallback sequence diagrams when no edges are available
    """
    diagrams = []
    
    try:
        with db.dbm.get_session() as session:
            from models.database import Method, Class, File
            from sqlalchemy import func
            
            # Get methods grouped by class
            classes_with_methods = session.query(
                Class.class_id,
                Class.fqn,
                Class.name,
                func.count(Method.method_id).label('method_count')
            ).join(Method).join(File).filter(
                File.project_id == project_id
            ).group_by(Class.class_id).order_by(
                func.count(Method.method_id).desc()
            ).limit(5).all()
            
            for i, (class_id, class_fqn, class_name, method_count) in enumerate(classes_with_methods):
                if method_count < 2:  # Need at least 2 methods for a meaningful sequence
                    continue
                
                # Get methods for this class
                methods = session.query(Method).filter(
                    Method.class_id == class_id
                ).order_by(Method.method_id).all()
                
                # Create artificial sequence diagram
                participants = []
                interactions = []
                
                for j, method in enumerate(methods):
                    participants.append({
                        'id': f'method:{method.method_id}',
                        'type': 'method',
                        'label': f'{class_name}.{method.name}()',
                        'actor_type': 'control',
                        'order': j,
                        'details': {
                            'name': method.name,
                            'class': class_fqn,
                            'signature': method.signature or f'{method.name}()',
                            'artificial': True
                        }
                    })
                
                # Create artificial interactions (sequential flow)
                for j in range(len(methods) - 1):
                    interactions.append({
                        'id': f'interaction_{j}',
                        'sequence_order': j,
                        'type': 'synchronous',
                        'from_participant': f'method:{methods[j].method_id}',
                        'to_participant': f'method:{methods[j+1].method_id}',
                        'message': f'calls {methods[j+1].name}()',
                        'confidence': 0.3,  # Low confidence for artificial
                        'artificial': True
                    })
                
                if participants and interactions:
                    diagram = {
                        'type': 'sequence',
                        'title': f'Artificial Flow: {class_name}',
                        'participants': participants,
                        'interactions': interactions,
                        'entry_point': {
                            'id': methods[0].method_id,
                            'name': f'{class_name}.{methods[0].name}',
                            'full_name': f'{class_fqn}.{methods[0].name}',
                            'category': 'artificial',
                            'artificial': True
                        },
                        'metadata': {
                            'total_participants': len(participants),
                            'total_interactions': len(interactions),
                            'max_depth_reached': 1,
                            'unresolved_calls': 0,
                            'artificial': True,
                            'note': 'This diagram shows artificial sequential flow due to missing call relationships'
                        }
                    }
                    diagrams.append(diagram)
    
    except Exception as e:
        print(f'Error creating fallback diagrams: {e}')
        import traceback
        traceback.print_exc()
    
    return diagrams


def main():
    import argparse
    parser = argparse.ArgumentParser(description='자동 시퀀스 다이어그램 생성 스크립트')
    parser.add_argument('--project-name', required=True, help='분석 대상 프로젝트 이름')
    args = parser.parse_args()
    project_name = args.project_name
    
    # 프로젝트명 검증
    if not project_name or project_name.strip() == '':
        print(f"오류: 프로젝트명이 유효하지 않습니다: '{project_name}'")
        return 1
    
    print(f"Auto-generating sequence diagrams for project: {project_name}")
    
    # Load configuration
    config_path = Path('config/config.yaml')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # Replace project name in config
        config_str = json.dumps(full_config)
        config_str = config_str.replace('{project_name}', project_name)
        full_config = json.loads(config_str)
        
        # The config structure has database.project, we need to use that
        project_config = full_config.get('database', {}).get('project', {
            'type': 'sqlite',
            'sqlite': {
                'path': f'./project/{project_name}/data/metadata.db',
                'wal_mode': True
            }
        })
        
        db_path = project_config['sqlite']['path']
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
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f'Error: Database not found at {db_path}')
        print(f'Please run the analyzer first: run_analyzer.bat --project-name {project_name}')
        return 1

    try:
        # Create database connection - VizDB expects the full config structure
        full_db_config = {'database': {'project': project_config}}
        db = VizDB(full_db_config, project_name)
        
        # Get project ID
        with db.dbm.get_session() as session:
            from models.database import Project
            project = session.query(Project).filter(Project.name == project_name).first()
            if not project:
                print(f'Error: Project {project_name} not found in database')
                return 1
            project_id = project.project_id

        print(f'Found project ID: {project_id}')
        
        # Generate automatic sequence diagrams
        diagrams = build_automatic_sequence_diagrams(
            project_config, 
            project_id, 
            project_name,
            max_diagrams=5,
            depth=4,
            max_nodes=100
        )
        
        print(f'\nGenerated {len(diagrams)} sequence diagrams:')
        
        if not diagrams:
            print("No sequence diagrams from automatic entry points.")
            print("This is likely due to missing method call relationships (0 edges found).")
            print("Creating fallback sequence diagrams from available methods...")
            
            # Create fallback diagrams using available methods
            diagrams = _create_fallback_sequence_diagrams(db, project_id, project_name)
            
            if not diagrams:
                print("Still no diagrams could be generated from available methods.")
                return 0
            else:
                print(f"Generated {len(diagrams)} fallback sequence diagrams.")
        
        # Save diagrams to output directory
        output_dir = Path(f'output/{project_name}/visualize')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary = []
        
        for i, diagram in enumerate(diagrams):
            title = diagram.get('title', 'Untitled')
            entry_point = diagram.get('entry_point', {})
            
            print(f'\n  Diagram {i+1}: {title}')
            print(f'    Entry Point: {entry_point.get("full_name", "Unknown")}')
            print(f'    Category: {entry_point.get("category", "Unknown")}')
            print(f'    Participants: {diagram["metadata"]["total_participants"]}')
            print(f'    Interactions: {diagram["metadata"]["total_interactions"]}')
            print(f'    Unresolved calls: {diagram["metadata"]["unresolved_calls"]}')
            
            summary.append({
                'diagram': i+1,
                'title': title,
                'entry_point': entry_point.get('full_name', 'Unknown'),
                'category': entry_point.get('category', 'Unknown'),
                'participants': diagram["metadata"]["total_participants"],
                'interactions': diagram["metadata"]["total_interactions"],
                'unresolved_calls': diagram["metadata"]["unresolved_calls"]
            })
            
            # Save JSON
            json_path = output_dir / f'auto_sequence_{i+1}.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(diagram, f, indent=2, ensure_ascii=False)
            
            # Generate Mermaid sequence diagram
            mermaid_content = _generate_mermaid_sequence(diagram)
            md_path = output_dir / f'auto_sequence_{i+1}.md'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f'# {title}\n\n')
                f.write(f'**Entry Point**: {entry_point.get("full_name", "Unknown")}\n\n')
                f.write(f'**Category**: {entry_point.get("category", "Unknown")}\n\n')
                f.write(f'**Statistics**:\n')
                f.write(f'- Participants: {diagram["metadata"]["total_participants"]}\n')
                f.write(f'- Interactions: {diagram["metadata"]["total_interactions"]}\n')
                f.write(f'- Unresolved calls: {diagram["metadata"]["unresolved_calls"]}\n\n')
                f.write('```mermaid\n')
                f.write(mermaid_content)
                f.write('\n```\n')
            
            print(f'    Saved to: {json_path}')
            print(f'    Markdown: {md_path}')
        
        # Create summary file
        summary_path = output_dir / 'auto_sequence_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'project': project_name,
                'generated_diagrams': len(diagrams),
                'summary': summary
            }, f, indent=2, ensure_ascii=False)
        
        print(f'\nAll diagrams saved to: {output_dir}')
        print(f'Summary saved to: {summary_path}')
        
        # Create HTML index file
        html_path = output_dir / 'auto_sequence_index.html'
        _create_html_index(html_path, project_name, summary)
        print(f'HTML index: {html_path}')
        
        return 0

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return 1


def _create_html_index(html_path: Path, project_name: str, summary: list):
    """Create HTML index file for sequence diagrams"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Auto-Generated Sequence Diagrams - {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .diagram {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .stats {{ background: #f5f5f5; padding: 10px; border-radius: 4px; }}
        .category {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .controller {{ background: #e3f2fd; }}
        .service {{ background: #f3e5f5; }}
        .main {{ background: #e8f5e8; }}
        .high_activity {{ background: #fff3e0; }}
        a {{ text-decoration: none; color: #1976d2; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Auto-Generated Sequence Diagrams</h1>
    <p><strong>Project:</strong> {project_name}</p>
    <p><strong>Generated:</strong> {len(summary)} diagrams</p>
    
"""
    
    for item in summary:
        category_class = item['category'].replace(' ', '_')
        html_content += f"""
    <div class="diagram">
        <h3>{item['title']}</h3>
        <p><strong>Entry Point:</strong> {item['entry_point']} 
           <span class="category {category_class}">{item['category']}</span></p>
        
        <div class="stats">
            <strong>Statistics:</strong>
            Participants: {item['participants']} | 
            Interactions: {item['interactions']} | 
            Unresolved: {item['unresolved_calls']}
        </div>
        
        <p>
            <a href="auto_sequence_{item['diagram']}.json">JSON</a> | 
            <a href="auto_sequence_{item['diagram']}.md">Markdown</a>
        </p>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == '__main__':
    sys.exit(main())