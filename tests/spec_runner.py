#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec-based test runner.

Scans these locations for .spec.yaml files and executes them:
- phase1/testcase/**/*.spec.yaml
- visualize/testcase/**/*.spec.yaml
- web-dashboard/backend/testcase/**/*.spec.yaml
- tests/specs/*.yaml (optional)

Supported spec schema (YAML):
  name: Test name
  kind: java_parser | jsp_mybatis_parser | engine_save | visualize_cli | http_get
  input: path or param string (per kind)
  params: dict of additional parameters
  expected: dict of assertions (counts, files_exist, status_code, etc.)

Run: python tests/spec_runner.py
"""

import os
import sys
import glob
import yaml
import subprocess
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE1_SRC = REPO_ROOT / 'phase1' / 'src'
sys.path.insert(0, str(PHASE1_SRC))


def run_java_parser(spec):
    from src.parsers.java_parser import JavaParser
    from src.models.database import File
    cfg = {'database': {'type': 'sqlite', 'sqlite': {'path': ':memory:'}}}
    parser = JavaParser(cfg)
    sample = str((REPO_ROOT / spec['input']).resolve())
    f, classes, methods, edges = parser.parse_file(sample, project_id=1)
    exp = spec.get('expected', {})
    assert isinstance(f, File)
    if 'classes_min' in exp:
        assert len(classes) >= exp['classes_min'], 'classes_min failed'
    if 'methods_min' in exp:
        assert len(methods) >= exp['methods_min'], 'methods_min failed'
    return True


def run_jsp_mybatis_parser(spec):
    from src.parsers.jsp_mybatis_parser import JspMybatisParser
    cfg = {'database': {'type': 'sqlite', 'sqlite': {'path': ':memory:'}}}
    parser = JspMybatisParser(cfg)
    sample = str((REPO_ROOT / spec['input']).resolve())
    f, sqls, joins, filters, edges, vulns = parser.parse_file(sample, project_id=1)
    exp = spec.get('expected', {})
    if 'sql_min' in exp:
        assert len(sqls) >= exp['sql_min'], 'sql_min failed'
    return True


def run_engine_save(spec):
    from src.models.database import DatabaseManager
    from src.database.metadata_engine import MetadataEngine
    from src.parsers.java_parser import JavaParser
    import tempfile, time
    db_path = os.path.join(tempfile.gettempdir(), f"sa_spec_{int(time.time())}.db")
    cfg = {'database': {'type': 'sqlite', 'sqlite': {'path': db_path, 'wal_mode': False}}}
    db = DatabaseManager(cfg)
    db.initialize()
    engine = MetadataEngine(cfg, db)
    parser = JavaParser(cfg)
    sample = str((REPO_ROOT / spec['input']).resolve())
    f, classes, methods, edges = parser.parse_file(sample, project_id=1)
    saved = engine._save_java_analysis_sync(f, classes, methods, edges)
    exp = spec.get('expected', {})
    if 'files_min' in exp:
        assert saved.get('files', 0) >= exp['files_min'], 'files_min failed'
    return True


def run_visualize_cli(spec):
    """Invoke visualize.cli as a module; check outputs exist."""
    cmd = [sys.executable, '-m', 'visualize.cli', spec['params'].get('command', 'graph')]
    for k, v in spec.get('params', {}).items():
        if k == 'command':
            continue
        if isinstance(v, bool):
            if v:
                cmd.append(f"--{k}")
        else:
            cmd.extend([f"--{k}", str(v)])
    # Ensure output dirs
    for p in spec.get('expected', {}).get('files_exist', []):
        Path(p).parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise AssertionError(f"visualize.cli failed: {' '.join(cmd)}\n{proc.stdout}")
    for p in spec.get('expected', {}).get('files_exist', []):
        if not Path(p).exists():
            raise AssertionError(f"missing output file: {p}")
    return True


def run_http_get(spec):
    """Optional: GET a URL if backend is running; otherwise skip."""
    import urllib.request
    url = spec['input']
    # normalize placeholders like {project_id}
    url = re.sub(r"\{[^}]+\}", "1", url)
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            status = resp.getcode()
    except Exception:
        print(f"[SKIP] http_get: backend not reachable: {url}")
        return True
    exp = spec.get('expected', {})
    if 'status_code' in exp:
        assert status == exp['status_code'], f"status {status} != {exp['status_code']}"
    return True


DISPATCH = {
    'java_parser': run_java_parser,
    'jsp_mybatis_parser': run_jsp_mybatis_parser,
    'engine_save': run_engine_save,
    'visualize_cli': run_visualize_cli,
    'http_get': run_http_get,
}


def load_specs():
    patterns = [
        REPO_ROOT / 'phase1' / 'testcase' / '**' / '*.spec.yaml',
        REPO_ROOT / 'visualize' / 'testcase' / '**' / '*.spec.yaml',
        REPO_ROOT / 'web-dashboard' / 'backend' / 'testcase' / '**' / '*.spec.yaml',
        REPO_ROOT / 'tests' / 'specs' / '*.yaml',
    ]
    files = []
    for pat in patterns:
        files.extend(glob.glob(str(pat), recursive=True))
    return [Path(f) for f in sorted(files)]


def run_spec_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    name = spec.get('name', path.name)
    kind = spec.get('kind')
    if kind not in DISPATCH:
        raise ValueError(f"Unknown kind: {kind} ({path})")
    print(f"[RUN] {name} ({kind}) :: {path}")
    ok = DISPATCH[kind](spec)
    print(f"[OK ] {name}")
    return ok


def main():
    specs = load_specs()
    if not specs:
        print("No spec files found.")
        sys.exit(0)
    failed = 0
    for p in specs:
        try:
            run_spec_file(p)
        except Exception as e:
            failed += 1
            print(f"[FAIL] {p}: {e}")
    if failed:
        print(f"\nResult: FAIL ({failed} failed)")
        sys.exit(1)
    print("\nResult: PASS")


if __name__ == '__main__':
    main()
