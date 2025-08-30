"""
Source Analyzer Web Dashboard - Backend API
FastAPI-based REST API with WebSocket support for real-time updates
"""

import sys
import os
import yaml
import logging
from datetime import datetime
from pathlib import Path

# Add phase1 to the Python path for importing phase1 modules
from pathlib import Path as _Path
_REPO_ROOT = _Path(__file__).resolve().parents[2]
_PHASE1_ROOT = _REPO_ROOT / 'phase1'
for _p in (str(_REPO_ROOT), str(_PHASE1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import Flask, jsonify, request, Response
try:
    import markdown as _md
except Exception:
    _md = None
from flask_cors import CORS
from database.metadata_engine import MetadataEngine
from models.database import DatabaseManager

def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml'))
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    # Expand ${VAR} placeholders from environment for convenience
    expanded = os.path.expandvars(raw)
    return yaml.safe_load(expanded)

def setup_logging(config):
    # Prefer server-level overrides, fallback to root logging section
    server_cfg = config.get('server', {}) if isinstance(config, dict) else {}
    log_level = (server_cfg.get('log_level') or config.get('logging', {}).get('level', 'INFO')).upper()
    log_file = server_cfg.get('log_file') or config.get('logging', {}).get('file', './logs/app.log')
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    #logging.getLogger('werkzeug').setLevel(logging.WARNING) # Suppress Flask access logs
    #logging.getLogger('werkzeug2').setLevel(logging.DEBUG) # Suppress Flask access logs

config = load_config()
setup_logging(config)

# App + static config
server_cfg = config.get('server', {}) if isinstance(config, dict) else {}
static_cfg = server_cfg.get('static', {}) if isinstance(server_cfg, dict) else {}
if static_cfg.get('enabled', False):
    # Resolve default folder relative to repo root
    repo_root = Path(__file__).resolve().parents[2]
    default_folder = repo_root / 'web-dashboard' / 'frontend' / 'dist'
    folder = Path(static_cfg.get('folder') or default_folder).resolve()
    url_path = static_cfg.get('url_path', '/static')
    app = Flask(__name__, static_folder=str(folder), static_url_path=url_path)
else:
    app = Flask(__name__)

# CORS from config
cors_cfg = server_cfg.get('cors', {}) if isinstance(server_cfg, dict) else {}
if cors_cfg.get('enabled', True):
    origins = cors_cfg.get('allow_origins', ['*'])
    methods = cors_cfg.get('allow_methods', ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    headers = cors_cfg.get('allow_headers', ['*'])
    credentials = bool(cors_cfg.get('credentials', False))
    expose_headers = cors_cfg.get('expose_headers', [])
    try:
        CORS(
            app,
            resources={r"/*": {"origins": origins}},
            methods=methods,
            allow_headers=headers,
            supports_credentials=credentials,
            expose_headers=expose_headers,
        )
    except Exception:
        CORS(app)
app.logger.setLevel(logging.DEBUG) # Set app logger to DEBUG

# API prefix helper
API_PREFIX = server_cfg.get('api_prefix', '/api')
def API(path: str) -> str:
    base = API_PREFIX or ''
    if not base.startswith('/'):
        base = '/' + base
    base = base.rstrip('/')
    if not path.startswith('/'):
        path = '/' + path
    return f"{base}{path}" if base else path

# Initialize MetadataEngine (fix: pass full config and initialize DB)
db_manager = DatabaseManager(config)
db_manager.initialize()
metadata_engine = MetadataEngine(config, db_manager)

@app.route('/')
def hello_world():
    return jsonify(message="Hello from SourceAnalyzer Backend!")

@app.route(API('/health'))
def health():
    return jsonify(status="healthy", timestamp=datetime.now().isoformat())

@app.route(API('/metadata'), methods=['GET'])
def get_metadata():
    try:
        metadata = metadata_engine.get_all_metadata()
        return jsonify(metadata)
    except Exception as e:
        app.logger.error(f"Error fetching metadata: {e}")
        return jsonify(error=str(e)), 500

@app.route(API('/metadata/<int:file_id>'), methods=['GET'])
def get_metadata_by_file_id(file_id):
    try:
        metadata = metadata_engine.get_metadata_by_file_id(file_id)
        if metadata:
            return jsonify(metadata)
        return jsonify(message="Metadata not found"), 404
    except Exception as e:
        app.logger.error(f"Error fetching metadata for file_id {file_id}: {e}")
        return jsonify(error=str(e)), 500

@app.route(API('/metadata/path'), methods=['GET'])
def get_metadata_by_path():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify(error="File path parameter is required"), 400
    try:
        metadata = metadata_engine.get_metadata_by_file_path(file_path)
        if metadata:
            return jsonify(metadata)
        return jsonify(message="Metadata not found"), 404
    except Exception as e:
        app.logger.error(f"Error fetching metadata for path {file_path}: {e}")
        return jsonify(error=str(e)), 500

@app.route(API('/scan'), methods=['POST'])
def scan_project():
    data = request.get_json()
    project_path = data.get('project_path')
    if not project_path:
        return jsonify(error="Project path is required"), 400

    try:
        # This is a placeholder for the actual scanning logic
        # In a real scenario, you would trigger your scanner here
        # and return its status or results.
        app.logger.info(f"Scanning project: {project_path}")
        # Simulate a scan operation
        scan_result = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "scanned_path": project_path,
            "findings": [] # Placeholder for actual findings
        }
        return jsonify(scan_result)
    except Exception as e:
        app.logger.error(f"Error during project scan for {project_path}: {e}")
        return jsonify(error=str(e)), 500

@app.route(API('/docs/<category>/<doc_id>'), methods=['GET'])
def get_documentation(category, doc_id):
    """Serve offline docs as pretty HTML by default.

    Priority:
      1) repo_root/docs/<category>/<CODE>.md (render to HTML)
      2) repo_root/docs/<category>/<CODE>.html (return as-is)

    Query params:
      - raw=1  -> return raw markdown (text/markdown) if md exists
      - format=md -> same as raw=1
    """
    repo_root = Path(__file__).parent.parent.parent
    cat = str(category).lower()
    code = str(doc_id).upper()

    # Prefer Markdown in ./docs
    md_path = repo_root / 'docs' / cat / f'{code}.md'
    if md_path.exists():
        app.logger.info(f"Serving markdown doc: {md_path}")
        try:
            content = md_path.read_text(encoding='utf-8')
            want_raw = request.args.get('raw') == '1' or request.args.get('format') == 'md'
            if want_raw:
                return Response(content, mimetype='text/markdown; charset=utf-8')
            html = _render_markdown_html_pretty(content, title=f"{code}")
            return Response(html, mimetype='text/html; charset=utf-8')
        except Exception as e:
            app.logger.error(f"Error reading markdown {md_path}: {e}")
            return jsonify(error=str(e)), 500


    # Finally: legacy ./docs HTML if present
    html_path = repo_root / 'docs' / cat / f'{code}.html'
    if html_path.exists():
        app.logger.info(f"Serving html doc: {html_path}")
        try:
            content = html_path.read_text(encoding='utf-8')
            return Response(content, mimetype='text/html; charset=utf-8')
        except Exception as e:
            app.logger.error(f"Error reading html {html_path}: {e}")
            return jsonify(error=str(e)), 500

    app.logger.warning(f"Documentation not found for {category}/{doc_id}")
    return jsonify(message="Documentation not found"), 404

@app.route(API('/docs/owasp/<code>'))
def get_owasp_doc(code):
    return get_documentation('owasp', code)

@app.route(API('/docs/cwe/<code>'))
def get_cwe_doc(code):
    # normalize code like 89 -> CWE-89
    c = code.upper()
    if not c.startswith('CWE-'):
        c = f'CWE-{c}'
    return get_documentation('cwe', c)


def _render_markdown_html_pretty(md_text: str, title: str = "Document") -> str:
    """Render markdown to standalone HTML with highlighting and nice styles."""
    pygments_css = ''
    if _md is None:
        safe = (md_text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body = f"<pre>{safe}</pre>"
    else:
        try:
            from pygments.formatters import HtmlFormatter  # type: ignore
            formatter = HtmlFormatter(style='friendly')
            pygments_css = formatter.get_style_defs('.codehilite')
        except Exception:
            pygments_css = ''
        try:
            md = _md.Markdown(
                extensions=['fenced_code', 'tables', 'toc', 'sane_lists', 'attr_list', 'codehilite'],
                extension_configs={
                    'toc': {'permalink': True},
                    'codehilite': {'guess_lang': False, 'pygments_style': 'friendly', 'noclasses': False}
                }
            )
            body = md.convert(md_text or '')
        except Exception:
            safe = (md_text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            body = f"<pre>{safe}</pre>"
            pygments_css = ''
    base_css = f"""
    :root {{ color-scheme: light; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Noto Sans KR', 'Helvetica Neue', Arial, 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol', sans-serif; margin: 0; background: #fff; color: #24292e; }}
    .page {{ max-width: 980px; margin: 0 auto; padding: 24px 16px 40px; }}
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: .3rem; }}
    .markdown-body a {{ color: #0969da; text-decoration: none; }}
    .markdown-body a:hover {{ text-decoration: underline; }}
    .markdown-body pre, .markdown-body code {{ background: #f6f8fa; }}
    .markdown-body pre {{ padding: .8rem; overflow: auto; border-radius: 6px; }}
    .markdown-body table {{ border-collapse: collapse; display: block; overflow: auto; }}
    .markdown-body table, .markdown-body th, .markdown-body td {{ border: 1px solid #d0d7de; }}
    .markdown-body th, .markdown-body td {{ padding: .4rem .6rem; }}
    .toc {{ font-size: .9rem; background: #fafbfc; border: 1px solid #d0d7de; border-radius: 6px; padding: .6rem .8rem; }}
    .header {{ position: sticky; top: 0; z-index: 10; background: #ffffffcc; backdrop-filter: blur(6px); border-bottom: 1px solid #eaecef; }}
    .header .inner {{ max-width: 980px; margin: 0 auto; padding: 10px 16px; font-weight: 600; }}
    {pygments_css}
    """
    html = f"""
    <!DOCTYPE html>
    <html lang=\"ko\">
    <head>
      <meta charset=\"UTF-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
      <title>{title}</title>
      <style>{base_css}</style>
    </head>
    <body>
      <div class=\"header\"><div class=\"inner\">{title}</div></div>
      <main class=\"page\">
        <article class=\"markdown-body\">{body}</article>
      </main>
    </body>
    </html>
    """
    return html
def _render_markdown_html(md_text: str, title: str = "Document") -> str:
    """Render markdown to standalone HTML. Falls back to pre tag if markdown lib missing."""
    if _md is None:
        safe = (md_text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body = f"<pre>{safe}</pre>"
    else:
        extensions = ['fenced_code', 'tables', 'toc']
        try:
            body = _md.markdown(md_text, extensions=extensions)
        except Exception:
            safe = (md_text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            body = f"<pre>{safe}</pre>"
    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Noto Sans KR', 'Helvetica Neue', Arial, 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol', sans-serif; margin: 2rem auto; max-width: 980px; padding: 0 1rem; line-height: 1.6; }
    pre, code { background: #f6f8fa; }
    pre { padding: 0.8rem; overflow: auto; }
    h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: .3rem; }
    table { border-collapse: collapse; }
    table, th, td { border: 1px solid #dfe2e5; }
    th, td { padding: .4rem .6rem; }
    .container { margin: 0 auto; }
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{title}</title>
      <style>{css}</style>
    </head>
    <body>
      <div class="container">
      {body}
      </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    server_cfg = config.get('server', {}) if isinstance(config, dict) else {}
    host = server_cfg.get('host', '127.0.0.1')
    port = int(server_cfg.get('port', 8000))
    debug = bool(server_cfg.get('debug', True))
    app.run(debug=debug, host=host, port=port)
