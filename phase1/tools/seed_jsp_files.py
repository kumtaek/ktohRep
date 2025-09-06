#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed File rows for JSP samples under tests/samples/jsp so JSP summarizer can find them.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE1_ROOT = REPO_ROOT / 'phase1'
for p in (REPO_ROOT, PHASE1_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from models.database import DatabaseManager, File


def load_config() -> Dict[str, Any]:
    cfg_path = REPO_ROOT / 'config' / 'config.yaml'
    if not cfg_path.exists():
        return {'database': {'type': 'sqlite', 'sqlite': {'path': str(REPO_ROOT / 'data' / 'metadata.db')}}}
    text = cfg_path.read_text(encoding='utf-8')
    expanded = os.path.expandvars(text)
    return yaml.safe_load(expanded) or {}


def main(argv=None) -> int:
    cfg = load_config()
    dbm = DatabaseManager(cfg)
    dbm.initialize()
    with dbm.get_auto_commit_session() as sess:
        base = REPO_ROOT / 'tests' / 'samples' / 'jsp'
        paths = list(base.glob('*.jsp'))
        added = 0
        for p in paths:
            p_str = str(p.resolve())
            exists = sess.query(File).filter(File.path == p_str).first()
            if exists:
                continue
            f = File(project_id=1, path=p_str, language='jsp')
            sess.add(f)
            added += 1
        print(f"Seeded JSP files: {added}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

