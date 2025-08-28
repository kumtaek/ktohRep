# visualize/templates/render.py
import json
import os
from pathlib import Path


def render_html(template_name: str, data: dict) -> str:
    """Render HTML template with data"""
    template_dir = Path(__file__).parent
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"템플릿을 찾을 수 없습니다: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Replace data placeholder with JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    rendered_html = template_content.replace('__DATA_PLACEHOLDER__', json_data)
    
    return rendered_html
