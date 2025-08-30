#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple metrics collector for SourceAnalyzer metadata DB.
Calculates coverage and quality indicators and emits Markdown.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
import yaml
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE1_ROOT = REPO_ROOT / 'phase1'
for p in (REPO_ROOT, PHASE1_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from models.database import DatabaseManager, DbTable, DbColumn, Join, Summary, File, SqlUnit, Method, EnrichmentLog


def load_config() -> Dict[str, Any]:
    cfg_path = REPO_ROOT / 'config' / 'config.yaml'
    if not cfg_path.exists():
        return {'database': {'type': 'sqlite', 'sqlite': {'path': str(REPO_ROOT / 'data' / 'metadata.db')}}}
    text = cfg_path.read_text(encoding='utf-8')
    expanded = os.path.expandvars(text)
    return yaml.safe_load(expanded) or {}


def ratio(a: int, b: int) -> float:
    return (a / b) if b else 0.0


def collect_metrics() -> Dict[str, Any]:
    config = load_config()
    dbm = DatabaseManager(config)
    dbm.initialize()
    sess = dbm.get_session()
    try:
        # Tables
        total_tables = sess.query(DbTable).count()
        tables_with_comment = sess.query(DbTable).filter(DbTable.table_comment.isnot(None)).count()
        # Columns
        total_cols = sess.query(DbColumn).count()
        cols_with_comment = sess.query(DbColumn).filter(DbColumn.column_comment.isnot(None)).count()
        # Joins
        total_joins = sess.query(Join).count()
        inferred_joins = sess.query(Join).filter(Join.inferred_pkfk == 1).count()
        avg_join_conf = 0.0
        if total_joins:
            vals = [j.confidence or 0.0 for j in sess.query(Join.confidence).all()]
            if vals:
                avg_join_conf = sum(vals) / len(vals)
        # Summaries
        total_sql = sess.query(SqlUnit).count()
        total_methods = sess.query(Method).count()
        total_jsp_files = sess.query(File).filter(File.language == 'jsp').count()
        sum_sql = sess.query(Summary).filter(Summary.target_type == 'sql_unit').count()
        sum_method = sess.query(Summary).filter(Summary.target_type == 'method').count()
        sum_file = sess.query(Summary).filter(Summary.target_type == 'file').count()
        # LLM logs
        llm_logs = sess.query(EnrichmentLog).count()
        return {
            'tables': {'total': total_tables, 'with_comment': tables_with_comment, 'coverage': ratio(tables_with_comment, total_tables)},
            'columns': {'total': total_cols, 'with_comment': cols_with_comment, 'coverage': ratio(cols_with_comment, total_cols)},
            'joins': {'total': total_joins, 'inferred': inferred_joins, 'inferred_ratio': ratio(inferred_joins, total_joins), 'avg_confidence': avg_join_conf},
            'summaries': {
                'sql_units': {'total': total_sql, 'with_summary': sum_sql, 'coverage': ratio(sum_sql, total_sql)},
                'methods': {'total': total_methods, 'with_summary': sum_method, 'coverage': ratio(sum_method, total_methods)},
                'files_jsp': {'total': total_jsp_files, 'with_summary': sum_file, 'coverage': ratio(sum_file, total_jsp_files)}
            },
            'llm': {'logs': llm_logs},
        }
    finally:
        sess.close()


def to_markdown(m: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"실데이터 메트릭 리포트 - {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("테이블/컬럼 코멘트")
    lines.append(f"- 테이블: {m['tables']['with_comment']} / {m['tables']['total']} (coverage {(m['tables']['coverage']*100):.1f}%)")
    lines.append(f"- 컬럼: {m['columns']['with_comment']} / {m['columns']['total']} (coverage {(m['columns']['coverage']*100):.1f}%)")
    lines.append("")
    lines.append("조인 해소/신뢰도")
    lines.append(f"- 조인 해소(inferred_pkfk=1): {m['joins']['inferred']} / {m['joins']['total']} (ratio {(m['joins']['inferred_ratio']*100):.1f}%)")
    lines.append(f"- 평균 조인 신뢰도: {m['joins']['avg_confidence']:.2f}")
    lines.append("")
    lines.append("요약 커버리지")
    lines.append(f"- SQL: {m['summaries']['sql_units']['with_summary']} / {m['summaries']['sql_units']['total']} (coverage {(m['summaries']['sql_units']['coverage']*100):.1f}%)")
    lines.append(f"- 메소드: {m['summaries']['methods']['with_summary']} / {m['summaries']['methods']['total']} (coverage {(m['summaries']['methods']['coverage']*100):.1f}%)")
    lines.append(f"- JSP 파일: {m['summaries']['files_jsp']['with_summary']} / {m['summaries']['files_jsp']['total']} (coverage {(m['summaries']['files_jsp']['coverage']*100):.1f}%)")
    lines.append("")
    lines.append("LLM 호출 로그")
    lines.append(f"- EnrichmentLog rows: {m['llm']['logs']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    m = collect_metrics()
    md = to_markdown(m)
    out = REPO_ROOT / '개발내역07.md'
    header = "개발내역 07 — 실데이터 메트릭 리포트\n=======================================\n\n"
    out.write_text(header + md + "\n", encoding='utf-8')
    print(md)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
