#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heuristic converter: Reads testcase markdown files and emits .spec.yaml skeletons.
Targets obvious references (ValidSimple.java, sample.jsp, mybatis_valid.xml, health/api/docs endpoints).
Safe to re-run; will not overwrite existing spec files unless --force.

Usage:
  python tests/spec_from_markdown.py --dry-run
  python tests/spec_from_markdown.py --force
"""

import re
import sys
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

MD_FILES = [
    REPO / 'testcase' / 'phase1' / 'testcases.md',
    REPO / 'testcase' / 'phase1' / 'phase1_testcases.md',
    REPO / 'testcase' / 'visualize' / 'visualization_testcases.md',
    REPO / 'web-dashboard' / 'backend' / 'testcase' / 'backend_testcases.md',
    REPO / 'docs' / 'testcase.md',
    REPO / 'testcase' / 'phase2' / 'phase2_testcases.md',
]


RULES = [
    # Java parser
    (re.compile(r'ValidSimple\.java', re.I), 'testcase/phase1/java_parser_from_md.spec.yaml', {
        'name': 'Java Parser (from md) ValidSimple',
        'kind': 'java_parser',
        'input': 'testcase/samples/java/ValidSimple.java',
        'expected': {'classes_min': 1, 'methods_min': 1},
    }),
    # JSP sample
    (re.compile(r'sample\.jsp', re.I), 'testcase/phase1/jsp_from_md.spec.yaml', {
        'name': 'JSP/MyBatis Parser (from md) sample.jsp',
        'kind': 'jsp_mybatis_parser',
        'input': 'testcase/samples/jsp/sample.jsp',
        'expected': {'sql_min': 0},
    }),
    # MyBatis valid
    (re.compile(r'mybatis_valid\.xml', re.I), 'testcase/phase1/mybatis_from_md.spec.yaml', {
        'name': 'MyBatis Parser (from md) valid xml',
        'kind': 'jsp_mybatis_parser',
        'input': 'testcase/samples/xml/mybatis_valid.xml',
        'expected': {'sql_min': 1},
    }),
    # Visualize exports
    (re.compile(r'ERD|graph|의존|Mermaid', re.I), 'testcase/visualize/from_md_graph.spec.yaml', {
        'name': 'Visualize CLI (from md) graph export',
        'kind': 'visualize_cli',
        'params': {'command': 'graph', 'project-id': 1, 'export-mermaid': './output/md_graph.md'},
        'expected': {'files_exist': ['output/md_graph.md']},
    }),
]


def write_spec(rel_path: str, content: dict, force=False, dry_run=False):
    dst = REPO / rel_path
    if dst.exists() and not force:
        print(f"[SKIP] exists: {dst}")
        return False
    text_lines = [
        f"name: {content['name']}",
        f"kind: {content['kind']}",
    ]
    if 'input' in content:
        text_lines.append(f"input: {content['input']}")
    if 'params' in content:
        text_lines.append('params:')
        for k, v in content['params'].items():
            text_lines.append(f"  {k}: {v}")
    if 'expected' in content:
        text_lines.append('expected:')
        for k, v in content['expected'].items():
            if isinstance(v, list):
                text_lines.append(f"  {k}:")
                for itm in v:
                    text_lines.append(f"    - {itm}")
            else:
                text_lines.append(f"  {k}: {v}")
    out = '\n'.join(text_lines) + '\n'
    if dry_run:
        print(f"[DRY] would write {dst}:\n{out}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding='utf-8')
    print(f"[GEN] {dst}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    hits = 0
    for md in MD_FILES:
        if not md.exists():
            continue
        text = md.read_text(encoding='utf-8', errors='ignore')
        for pat, rel, spec in RULES:
            if pat.search(text):
                if write_spec(rel, spec, force=args.force, dry_run=args.dry_run):
                    hits += 1
    print(f"Done. {hits} spec(s) generated or verified.")


if __name__ == '__main__':
    main()

