#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inject YAML Front Matter under each test case heading in markdown files.

Targets:
- visualize/testcase/visualization_testcases.md
- web-dashboard/backend/testcase/backend_testcases.md

Heuristics:
- Visualization: parse inline command like `python -m visualize (erd|graph|component|sequence) ...`
  and turn into kind: visualize_cli + params/expected(files_exist from --out/--export-mermaid).
- Backend: parse endpoint lines like `GET /api/...` and build kind: http_get with expected status.
  If path is `/health`, normalize to `/api/health` (matches actual app).

Idempotent: if a heading is immediately followed by a Front Matter block (--- on next line), skip.
"""

import re
from pathlib import Path
import shlex

REPO = Path(__file__).resolve().parent.parent


def has_front_matter(lines, idx):
    # idx points to heading line; check next non-empty line is '---'
    j = idx + 1
    while j < len(lines) and lines[j].strip() == '':
        j += 1
    return j < len(lines) and lines[j].strip() == '---'


def parse_visualize_command(section_text):
    # find a backticked command python -m visualize ...
    m = re.search(r"`python\s+-m\s+visualize(?:\.cli)?\s+(erd|graph|component|sequence)([^`\n]*)`", section_text)
    if not m:
        return None
    cmd = m.group(0).strip('`')
    command = m.group(1)
    rest = m.group(2) or ''
    try:
        argv = shlex.split(rest)
    except Exception:
        argv = rest.split()
    params = {'command': command}
    out_files = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith('--'):
            key = tok[2:]
            val = True
            if i + 1 < len(argv) and not argv[i+1].startswith('--'):
                val = argv[i+1]
                i += 1
            params[key] = val
            if key in {'out', 'export-mermaid'} and isinstance(val, str):
                out_files.append(val)
        i += 1
    expected = {}
    if out_files:
        # store relative to repo root
        expected['files_exist'] = [str(Path(p)) for p in out_files]
    return {'kind': 'visualize_cli', 'params': params, 'expected': expected}


def inject_visualize(file_path: Path):
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        if line.strip().startswith('### '):
            if has_front_matter(lines, i):
                i += 1
                continue
            # gather section text until next heading
            start = i
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith('### '):
                buf.append(lines[j])
                j += 1
            section_text = '\n'.join(buf)
            meta = parse_visualize_command(section_text)
            if meta:
                # inject YAML block after current line
                out_lines.append('')
                out_lines.append('---')
                # name
                out_lines.append(f"name: {line.strip()[4:].strip()}")
                out_lines.append(f"kind: {meta['kind']}")
                # params
                params = meta.get('params') or {}
                if params:
                    out_lines.append('params:')
                    for k, v in params.items():
                        out_lines.append(f"  {k}: {v}")
                expected = meta.get('expected') or {}
                if expected:
                    out_lines.append('expected:')
                    files = expected.get('files_exist') or []
                    if files:
                        out_lines.append('  files_exist:')
                        for p in files:
                            out_lines.append(f"    - {p}")
                out_lines.append('---')
                i = j - 1  # next loop will add the heading of next section
        i += 1
    new_text = '\n'.join(out_lines) + ('\n' if not out_lines[-1].endswith('\n') else '')
    file_path.write_text(new_text, encoding='utf-8')


def parse_backend_endpoint(section_text):
    # Look for backticked `GET /...` or similar
    m = re.search(r"`(GET|POST|DELETE|PUT|PATCH)\s+([^`\s]+)`", section_text)
    if not m:
        return None
    method, path = m.group(1), m.group(2)
    # normalize path
    if path == '/health':
        path = '/api/health'
    url = f"http://127.0.0.1:8000{path}"
    # expected status: heuristics from keywords
    expected = {}
    if re.search(r'404', section_text):
        expected['status_code'] = 404
    elif re.search(r'422', section_text):
        expected['status_code'] = 422
    elif re.search(r'500', section_text):
        expected['status_code'] = 500
    else:
        expected['status_code'] = 200
    return {'kind': 'http_get', 'input': url, 'expected': expected}


def inject_backend(file_path: Path):
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        if line.strip().startswith('### '):
            if has_front_matter(lines, i):
                i += 1
                continue
            # gather section
            start = i
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith('### '):
                buf.append(lines[j])
                j += 1
            section_text = '\n'.join(buf)
            meta = parse_backend_endpoint(section_text)
            if meta:
                out_lines.append('')
                out_lines.append('---')
                out_lines.append(f"name: {line.strip()[4:].strip()}")
                out_lines.append(f"kind: {meta['kind']}")
                out_lines.append(f"input: {meta['input']}")
                exp = meta.get('expected') or {}
                if exp:
                    out_lines.append('expected:')
                    for k, v in exp.items():
                        out_lines.append(f"  {k}: {v}")
                out_lines.append('---')
                i = j - 1
        i += 1
    new_text = '\n'.join(out_lines) + ('\n' if not out_lines[-1].endswith('\n') else '')
    file_path.write_text(new_text, encoding='utf-8')


def main():
    vis = REPO / 'visualize' / 'testcase' / 'visualization_testcases.md'
    if vis.exists():
        inject_visualize(vis)
        print(f"Updated: {vis}")
    be = REPO / 'web-dashboard' / 'backend' / 'testcase' / 'backend_testcases.md'
    if be.exists():
        inject_backend(be)
        print(f"Updated: {be}")
    # phase1: inject based on filenames in headings (java/xml/jsp)
    p1 = REPO / 'phase1' / 'testcase' / 'testcases.md'
    if p1.exists():
        text = p1.read_text(encoding='utf-8', errors='ignore')
        lines = text.splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            out.append(line)
            if line.strip().startswith('### '):
                # skip if FM already exists
                if has_front_matter(lines, i):
                    i += 1
                    continue
                # extract filename in heading
                m = re.search(r"`([^`]+)`", line)
                target = m.group(1) if m else ''
                ext = target.lower().rsplit('.', 1)[-1] if '.' in target else ''
                # gather section for explicit PROJECT path
                j = i + 1
                buf = []
                while j < len(lines) and not lines[j].strip().startswith('### '):
                    buf.append(lines[j])
                    j += 1
                sec = '\n'.join(buf)
                path_match = re.search(r"`(PROJECT/[^`]+)`", sec)
                input_path = path_match.group(1) if path_match else None
                kind = None
                expected = []
                if ext == 'java':
                    kind = 'java_parser'
                    if not input_path:
                        input_path = f"PROJECT/IntegratedSource/src/main/java/{target}"
                    expected = ["  classes_min: 1", "  methods_min: 1"]
                elif ext == 'xml':
                    kind = 'jsp_mybatis_parser'
                    if not input_path:
                        input_path = f"PROJECT/IntegratedSource/src/main/resources/{target}"
                    expected = ["  sql_min: 1"]
                elif ext == 'jsp':
                    kind = 'jsp_mybatis_parser'
                    if not input_path:
                        input_path = f"PROJECT/IntegratedSource/src/main/webapp/{target}"
                    expected = ["  sql_min: 0"]
                if kind and input_path:
                    out.append('')
                    out.append('---')
                    out.append(f"name: {line.strip()[4:].strip()}")
                    out.append(f"kind: {kind}")
                    out.append(f"input: {input_path}")
                    out.append("skip_if_missing_input: true")
                    if expected:
                        out.append('expected:')
                        out.extend(expected)
                    out.append('---')
                    i = j - 1
            i += 1
        p1.write_text('\n'.join(out) + '\n', encoding='utf-8')
        print(f"Updated: {p1}")


if __name__ == '__main__':
    main()
