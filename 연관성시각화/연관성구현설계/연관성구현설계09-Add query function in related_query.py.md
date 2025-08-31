Add query function in related_query.py
8월 30일
kumtaek/ktohRep
master
+112
-0

아카이브에 보관

공유하기

PR 만들기


1. `phase2/services/related_query.py`에 조회 함수 작성
2. 웹/CLI 엔드포인트(`phase2/routes/related.py` 등) 추가
복사
Summary
Added a new get_related_edges service to fetch related edge information from the metadata database based on source type and ID

Introduced a Flask blueprint and CLI entry point that expose related-edge queries over HTTP and the command line

Testing
✅ python -m py_compile phase2/services/related_query.py phase2/routes/related.py

⚠️ pytest -q (no tests found)


파일 (5)개

phase2/__init__.py
신규

phase2/routes/__init__.py
신규

phase2/routes/related.py
신규

phase2/services/__init__.py
신규

phase2/services/related_query.py
신규



phase2/__init__.py
신규

내용 없음
phase2/routes/__init__.py
신규

내용 없음
phase2/routes/related.py
신규
+80
-0

"""Web and CLI interfaces for querying related metadata."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, List

import yaml
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from phase1.models.database import DatabaseManager
from phase2.services.related_query import get_related_edges

# Blueprint for web usage
bp = Blueprint("related", __name__)


def _load_config(config_path: Path | None = None) -> dict:
    """Load configuration file and return dictionary."""
    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        raw = f.read()
    return yaml.safe_load(os.path.expandvars(raw)) or {}


def _get_session(config: dict) -> Session:
    """Create a new database session using project database settings."""
    db_cfg = config.get("database", {}).get("project") or config.get("database", {})
    dbm = DatabaseManager({"database": db_cfg})
    dbm.initialize()
    return dbm.get_session()


@bp.route("/related", methods=["GET"])
def related_endpoint() -> Any:
    """HTTP endpoint returning related edges for a source node."""
    src_type = request.args.get("src_type")
    src_id = request.args.get("src_id", type=int)
    if not src_type or src_id is None:
        return jsonify({"error": "src_type and src_id are required"}), 400

    config = _load_config()
    session = _get_session(config)
    try:
        edges = get_related_edges(session, src_type, src_id)
        return jsonify({"edges": edges})
    finally:
        session.close()


def main(argv: List[str] | None = None) -> int:
    """CLI entry point for related edge lookup."""
    ap = argparse.ArgumentParser(description="Query related edges from metadata DB")
    ap.add_argument("src_type", help="Source type, e.g., class or method")
    ap.add_argument("src_id", type=int, help="Source identifier")
    ap.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "config" / "config.yaml"),
        help="Path to configuration file",
    )
    args = ap.parse_args(argv)

    cfg = _load_config(Path(args.config))
    session = _get_session(cfg)
    try:
        edges = get_related_edges(session, args.src_type, args.src_id)
        for e in edges:
            print(
                f"{e['edge_kind']} -> {e['dst_type']}:{e['dst_id']} (confidence={e['confidence']:.2f})"
            )
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
phase2/services/__init__.py
신규

내용 없음
phase2/services/related_query.py
신규
+32
-0

"""Utilities for querying related edges from metadata database."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from phase1.models.database import Edge


def get_related_edges(session: Session, src_type: str, src_id: int) -> List[Dict[str, Any]]:
    """Return edges originating from a given source.

    Args:
        session: Active SQLAlchemy session.
        src_type: Source type (e.g., ``"class"``, ``"method"``).
        src_id: Identifier of the source object.

    Returns:
        A list of dictionaries describing each matching edge. Each dictionary
        contains ``dst_type``, ``dst_id``, ``edge_kind`` and ``confidence``.
    """
    edges = (
        session.query(Edge)
        .filter(Edge.src_type == src_type, Edge.src_id == src_id)
        .all()
    )
    return [
        {
            "dst_type": e.dst_type,
            "dst_id": e.dst_id,
            "edge_kind": e.edge_kind,
            "confidence": e.confidence,
        }
        for e in edges
    ]