Add get_related_entities function and endpoint
8월 30일
kumtaek/ktohRep
master
+77
-0

아카이브에 보관

공유하기

PR 만들기


1. `phase2/services/related_query.py`에 `get_related_entities` 함수 작성
2. CLI 또는 웹 인터페이스에서 노드 ID와 임계값을 입력받아 관련 엔티티 목록을 출력하는 엔드포인트 추가
복사
Summary
Added a dedicated service function for retrieving related entities filtered by confidence threshold, supporting node identifiers in <type>:<id> format and returning structured results

Exposed a new /api/related endpoint in the web backend that imports the service and returns related entities for a given node and threshold, with validation and error handling

Testing
✅ pytest

✅ python -m py_compile phase2/services/related_query.py web-dashboard/backend/app.py


파일 (4)개

phase2/__init__.py
신규

phase2/services/__init__.py
신규

phase2/services/related_query.py
신규

web-dashboard/backend/app.py
+19
-0


phase2/__init__.py
신규

내용 없음
phase2/services/__init__.py
신규

내용 없음
phase2/services/related_query.py
신규
+58
-0

"""Utilities for querying related entities based on edge confidence."""
from __future__ import annotations

from typing import Any, Dict, List

from phase1.models.database import DatabaseManager, Edge


def get_related_entities(node_key: str, threshold: float, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return entities related to ``node_key`` with confidence above ``threshold``.

    Parameters
    ----------
    node_key: str
        Identifier in the form ``"<type>:<id>"`` (e.g. ``"class:12"``).
    threshold: float
        Minimum edge confidence to include.
    config: Dict[str, Any]
        Database configuration passed to :class:`DatabaseManager`.

    Returns
    -------
    List[Dict[str, Any]]
        List of dictionaries describing related entities.  Each entry contains
        ``node`` ("<type>:<id>"), ``edge_kind`` and ``confidence``.
    """
    if ":" not in node_key:
        raise ValueError("node_key must be in '<type>:<id>' format")

    node_type, node_id_str = node_key.split(":", 1)
    try:
        node_id = int(node_id_str)
    except ValueError as exc:
        raise ValueError("node id must be an integer") from exc

    dbm = DatabaseManager(config)
    session = dbm.get_session()
    results: List[Dict[str, Any]] = []
    try:
        edges = session.query(Edge).filter(
            ((Edge.src_type == node_type) & (Edge.src_id == node_id) & (Edge.confidence >= threshold))
            | ((Edge.dst_type == node_type) & (Edge.dst_id == node_id) & (Edge.confidence >= threshold))
        ).all()
        for edge in edges:
            if edge.src_type == node_type and edge.src_id == node_id:
                other_type, other_id = edge.dst_type, edge.dst_id
            else:
                other_type, other_id = edge.src_type, edge.src_id
            results.append(
                {
                    "node": f"{other_type}:{other_id}",
                    "edge_kind": edge.edge_kind,
                    "confidence": edge.confidence,
                }
            )
    finally:
        session.close()
    return results
web-dashboard/backend/app.py
+19
-0

@@ -4,50 +4,51 @@ FastAPI-based REST API with WebSocket support for real-time updates
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
from phase2.services.related_query import get_related_entities

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
@@ -213,50 +214,68 @@ def get_documentation(category, doc_id):
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


@app.route(API('/related'), methods=['GET'])
def related_entities():
    """Return entities related to a node above a confidence threshold."""
    node = request.args.get('node')
    threshold_arg = request.args.get('threshold', '0')
    try:
        threshold = float(threshold_arg)
    except ValueError:
        return jsonify({'error': 'threshold must be a number'}), 400
    if not node:
        return jsonify({'error': 'node parameter required'}), 400
    try:
        related = get_related_entities(node, threshold, config)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify({'node': node, 'threshold': threshold, 'related': related})


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