#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec-based test runner.

Scans these locations for .spec.yaml files and executes them:
- testcase/phase1/**/*.spec.yaml
- testcase/visualize/**/*.spec.yaml
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
# Ensure 'src' package is importable by adding its parent ('phase1') to sys.path
PHASE1_ROOT = REPO_ROOT / 'phase1'
if str(PHASE1_ROOT) not in sys.path:
    sys.path.insert(0, str(PHASE1_ROOT))
# Also add 'phase1/src' so modules importing 'models' directly resolve
PHASE1_SRC_DIR = PHASE1_ROOT / 'src'
if str(PHASE1_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_SRC_DIR))


def run_java_parser(spec):
    from src.parsers.java_parser import JavaParser
    from src.models.database import File
    cfg = {'database': {'type': 'sqlite', 'sqlite': {'path': ':memory:'}}}
    parser = JavaParser(cfg)
    sample_path = REPO_ROOT / spec['input']
    if spec.get('skip_if_missing_input') and not sample_path.exists():
        print(f"[SKIP] java_parser: missing input {sample_path}")
        return True
    sample = str(sample_path.resolve())
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
    sample_path = REPO_ROOT / spec['input']
    if spec.get('skip_if_missing_input') and not sample_path.exists():
        print(f"[SKIP] jsp_mybatis_parser: missing input {sample_path}")
        return True
    sample = str(sample_path.resolve())
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
    sample_path = REPO_ROOT / spec['input']
    if spec.get('skip_if_missing_input') and not sample_path.exists():
        print(f"[SKIP] engine_save: missing input {sample_path}")
        return True
    sample = str(sample_path.resolve())
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


def run_engine_llm_assist(spec):
    from src.models.database import DatabaseManager, EnrichmentLog
    from src.database.metadata_engine import MetadataEngine
    from src.parsers.java_parser import JavaParser
    import tempfile, time
    db_path = os.path.join(tempfile.gettempdir(), f"sa_spec_llm_{int(time.time())}.db")
    cfg = {
        'database': {'type': 'sqlite', 'sqlite': {'path': db_path, 'wal_mode': False}},
        'llm_assist': {
            'enabled': True,
            'dry_run': True,
            'low_conf_threshold': 1.0,
            'provider': 'ollama',
        },
    }
    db = DatabaseManager(cfg)
    db.initialize()
    engine = MetadataEngine(cfg, db)
    parsers = {'java': JavaParser(cfg)}
    sample_path = REPO_ROOT / spec['input']
    if spec.get('skip_if_missing_input') and not sample_path.exists():
        print(f"[SKIP] engine_llm_assist: missing input {sample_path}")
        return True
    sample = str(sample_path.resolve())
    saved = engine._analyze_single_file_sync(sample, project_id=1, parsers=parsers)
    # Verify enrichment log was created
    session = db.get_session()
    try:
        count = session.query(EnrichmentLog).count()
    finally:
        session.close()
    exp = spec.get('expected', {})
    min_logs = exp.get('enrichment_logs_min', 1)
    assert count >= min_logs, f"enrichment logs {count} < {min_logs}"
    return True

DISPATCH['engine_llm_assist'] = run_engine_llm_assist


def run_engine_augment_unit(spec):
    """Unit-style test: call engine augmentation methods with sample JSON."""
    from src.models.database import DatabaseManager, File, Class, Method, SqlUnit, Join, RequiredFilter
    from src.database.metadata_engine import MetadataEngine
    import tempfile, time
    db_path = os.path.join(tempfile.gettempdir(), f"sa_spec_aug_{int(time.time())}.db")
    cfg = {'database': {'type': 'sqlite', 'sqlite': {'path': db_path, 'wal_mode': False}}}
    db = DatabaseManager(cfg)
    db.initialize()
    engine = MetadataEngine(cfg, db)
    # Create a file row to attach artifacts
    session = db.get_session()
    try:
        with session.begin():
            f = File(project_id=1, path='tests/samples/java/ValidSimple.java', language='java')
            session.add(f)
            session.flush()
            file_id = f.file_id
    finally:
        session.close()
    target = (spec.get('params') or {}).get('target', 'java')
    if target == 'java':
        data = {"classes": [{"name": "Sample", "methods": [{"name": "run", "signature": "run()"}]}]}
        added = engine._augment_java_from_json(file_id=file_id, data=data)
        # Query back
        session = db.get_session()
        try:
            clz = session.query(Class).filter(Class.file_id == file_id).count()
            mtd = session.query(Method).join(Class).filter(Class.file_id == file_id).count()
        finally:
            session.close()
        exp = spec.get('expected', {})
        assert clz >= exp.get('classes_min', 1), f"classes {clz} < {exp.get('classes_min', 1)}"
        assert mtd >= exp.get('methods_min', 1), f"methods {mtd} < {exp.get('methods_min', 1)}"
    else:
        # SQL augment
        data = {"sql_units": [{"stmt_kind": "select", "tables": ["DUAL"], "joins": [], "filters": []}]}
        added = engine._augment_sql_from_json(file_id=file_id, file_path='tests/samples/xml/mybatis_valid.xml', data=data)
        session = db.get_session()
        try:
            su = session.query(SqlUnit).filter(SqlUnit.file_id == file_id).count()
            jn = session.query(Join).join(SqlUnit).filter(SqlUnit.file_id == file_id).count()
            flt = session.query(RequiredFilter).join(SqlUnit).filter(SqlUnit.file_id == file_id).count()
        finally:
            session.close()
        exp = spec.get('expected', {})
        assert su >= exp.get('sql_units_min', 1), f"sql_units {su} < {exp.get('sql_units_min', 1)}"
        assert jn >= exp.get('joins_min', 0), f"joins {jn} < {exp.get('joins_min', 0)}"
        assert flt >= exp.get('filters_min', 0), f"filters {flt} < {exp.get('filters_min', 0)}"
    return True

DISPATCH['engine_augment_unit'] = run_engine_augment_unit


def run_engine_llm_db_enrich(spec):
    """Create minimal schema rows and run LLM enrichment (dry-run)."""
    from src.models.database import DatabaseManager, DbTable, DbColumn, Join, SqlUnit
    from src.database.metadata_engine import MetadataEngine
    import tempfile, time
    db_path = os.path.join(tempfile.gettempdir(), f"sa_spec_enrich_{int(time.time())}.db")
    cfg = {
        'database': {'type': 'sqlite', 'sqlite': {'path': db_path, 'wal_mode': False}},
        'llm_assist': {'enabled': True, 'dry_run': True, 'provider': 'ollama'}
    }
    db = DatabaseManager(cfg)
    db.initialize()
    engine = MetadataEngine(cfg, db)
    # Seed a table/column without comments and a simple join
    session = db.get_session()
    try:
        with session.begin():
            t1 = DbTable(owner='SAMPLE', table_name='USERS', status='VALID', table_comment=None)
            session.add(t1)
            session.flush()
            c1 = DbColumn(table_id=t1.table_id, column_name='ID', data_type='NUMBER', nullable='N', column_comment=None)
            session.add(c1)
            t2 = DbTable(owner='SAMPLE', table_name='ORDERS', status='VALID', table_comment=None)
            session.add(t2)
            session.flush()
            c2 = DbColumn(table_id=t2.table_id, column_name='USER_ID', data_type='NUMBER', nullable='N', column_comment=None)
            session.add(c2)
            su = SqlUnit(file_id=0, origin='mybatis', stmt_kind='select', normalized_fingerprint='test')
            session.add(su)
            session.flush()
            j = Join(sql_id=su.sql_id, l_table='USERS', l_col='ID', op='=', r_table='ORDERS', r_col='USER_ID', inferred_pkfk=0)
            session.add(j)
    finally:
        session.close()
    # Enrich comments
    _ = engine.llm_enrich_table_and_column_comments(max_tables=2, max_columns=2)
    # Infer join keys (dry-run heuristic)
    _ = engine.llm_infer_join_keys(max_items=1)
    # Assert
    session = db.get_session()
    try:
        t1c = session.query(DbTable).filter(DbTable.table_name == 'USERS').first()
        t2c = session.query(DbTable).filter(DbTable.table_name == 'ORDERS').first()
        assert t1c and (t1c.table_comment or '').strip(), 'table comment not enriched'
        assert t2c and (t2c.table_comment or '').strip(), 'table comment not enriched'
        join = session.query(Join).first()
        assert join and join.inferred_pkfk == 1, 'join not inferred as pkfk'
    finally:
        session.close()
    return True

DISPATCH['engine_llm_db_enrich'] = run_engine_llm_db_enrich


def run_engine_llm_jsp_summary(spec):
    """Create File row for JSP and run JSP summary (dry-run)."""
    from src.models.database import DatabaseManager, File, Summary
    from src.database.metadata_engine import MetadataEngine
    import tempfile, time
    db_path = os.path.join(tempfile.gettempdir(), f"sa_spec_jsp_{int(time.time())}.db")
    cfg = {
        'database': {'type': 'sqlite', 'sqlite': {'path': db_path, 'wal_mode': False}},
        'llm_assist': {'enabled': True, 'dry_run': True, 'provider': 'ollama', 'file_max_lines': 200}
    }
    db = DatabaseManager(cfg)
    db.initialize()
    engine = MetadataEngine(cfg, db)
    # Seed a JSP file record
    jsp_path = str((REPO_ROOT / 'tests' / 'samples' / 'jsp' / 'sample.jsp').resolve())
    session = db.get_session()
    try:
        with session.begin():
            f = File(project_id=1, path=jsp_path, language='jsp')
            session.add(f)
            session.flush()
            file_id = f.file_id
    finally:
        session.close()
    created = engine.llm_summarize_jsp_files(max_items=1)
    session = db.get_session()
    try:
        s = session.query(Summary).filter(Summary.target_type == 'file', Summary.target_id == file_id).first()
        assert s and (s.content or '').strip(), 'jsp summary not created'
    finally:
        session.close()
    return True

DISPATCH['engine_llm_jsp_summary'] = run_engine_llm_jsp_summary


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


def parse_front_matters_from_md(md_path: Path):
    """Parse YAML front matter blocks delimited by --- in a markdown file.
    Returns a list of spec dicts with at least 'kind' and action fields.
    """
    try:
        text = md_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []
    lines = text.splitlines()
    specs = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == '---':
            j = i + 1
            block = []
            while j < len(lines) and lines[j].strip() != '---':
                block.append(lines[j])
                j += 1
            if j < len(lines) and lines[j].strip() == '---':
                yaml_text = '\n'.join(block)
                try:
                    data = yaml.safe_load(yaml_text)
                    if isinstance(data, dict) and 'kind' in data:
                        specs.append(data)
                except Exception:
                    pass
                i = j  # skip to end marker
        i += 1
    return specs


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
    # also parse markdown front matter from docs
    md_docs = [
        REPO_ROOT / 'visualize' / 'testcase' / 'visualization_testcases.md',
        REPO_ROOT / 'web-dashboard' / 'backend' / 'testcase' / 'backend_testcases.md',
        REPO_ROOT / 'phase1' / 'testcase' / 'testcases.md',
    ]
    md_specs = []
    for md in md_docs:
        if md.exists():
            md_specs.extend(parse_front_matters_from_md(md))
    if not specs and not md_specs:
        print("No spec files or markdown front matter specs found.")
        sys.exit(0)
    failed = 0
    # run file-based specs
    for p in specs:
        try:
            run_spec_file(p)
        except Exception as e:
            failed += 1
            print(f"[FAIL] {p}: {e}")
    # run md-based specs
    for s in md_specs:
        try:
            print(f"[RUN] {s.get('name','(md spec)')} ({s.get('kind')}) :: [markdown]")
            kind = s.get('kind')
            if kind not in DISPATCH:
                raise ValueError(f"Unknown kind: {kind}")
            DISPATCH[kind](s)
            print(f"[OK ] {s.get('name','(md spec)')}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] [markdown spec]: {e}")
    if failed:
        print(f"\nResult: FAIL ({failed} failed)")
        sys.exit(1)
    print("\nResult: PASS")


if __name__ == '__main__':
    main()
