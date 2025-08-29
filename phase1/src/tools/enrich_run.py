#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run LLM-based enrichment passes (summaries) with simple limits.

Usage examples:
  python -m phase1.src.tools.enrich_run --sql 20 --method 50 --jsp 10 --dry-run
  python -m phase1.src.tools.enrich_run --sql 50 --dry-run=false
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE1_ROOT = REPO_ROOT / 'phase1'
PHASE1_SRC = PHASE1_ROOT / 'src'
for p in (PHASE1_ROOT, PHASE1_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from src.models.database import DatabaseManager
from src.database.metadata_engine import MetadataEngine


def load_config() -> Dict[str, Any]:
    cfg_path = REPO_ROOT / 'config' / 'config.yaml'
    if not cfg_path.exists():
        return {'database': {'type': 'sqlite', 'sqlite': {'path': str(REPO_ROOT / 'data' / 'metadata.db')}}}
    text = cfg_path.read_text(encoding='utf-8')
    expanded = os.path.expandvars(text)
    return yaml.safe_load(expanded) or {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description='Run LLM enrichment passes')
    ap.add_argument('--sql', type=int, default=0, help='Max SQL summaries to generate')
    ap.add_argument('--method', type=int, default=0, help='Max method summaries to generate')
    ap.add_argument('--jsp', type=int, default=0, help='Max JSP file summaries to generate')
    ap.add_argument('--dry-run', dest='dry_run', default=None, help='Override llm_assist.dry_run (true/false)')
    args = ap.parse_args(argv)

    cfg = load_config()
    # Override dry_run if specified
    if args.dry_run is not None:
        v = str(args.dry_run).strip().lower()
        dr = True if v in ('1','true','yes','y','on') else False
        cfg.setdefault('llm_assist', {})['dry_run'] = dr

    dbm = DatabaseManager(cfg)
    dbm.initialize()
    engine = MetadataEngine(cfg, dbm)

    total = 0
    if args.sql > 0:
        total += engine.llm_summarize_sql_units(max_items=args.sql)
    if args.method > 0:
        total += engine.llm_summarize_methods(max_items=args.method)
    if args.jsp > 0:
        total += engine.llm_summarize_jsp_files(max_items=args.jsp)

    print(f"Generated summaries: {total}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
