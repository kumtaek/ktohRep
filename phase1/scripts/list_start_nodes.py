#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 메타데이터 DB에서 시퀀스 다이어그램의 시작점으로 사용할 수 있는
메서드(FQN)와 JSP 파일 경로를 조회하는 간단한 스크립트.

사용법:
  python scripts/list_start_nodes.py --project-id 1 [--config config/config.yaml] [--limit 50] [--like keyword]

옵션:
  --project-id   대상 프로젝트 ID (필수)
  --config       설정 파일 경로 (기본: config/config.yaml)
  --limit        출력 개수 제한 (기본: 50)
  --like         키워드 필터(부분 일치, 대소문자 무시). 메서드 FQN/파일 경로에 적용

출력:
  - Methods: FQN (e.g., com.example.service.UserService.listUsers)
  - JSP Files: 파일 경로 (DB에 저장된 원본 경로)
"""

import argparse
import os
import sys
import yaml
from pathlib import Path


def _add_phase1_to_syspath():
    # Since this script is now inside phase1/scripts,
    # parents[1] points to the phase1 directory.
    phase1_root = Path(__file__).resolve().parents[1]
    phase1_src = phase1_root / 'src'
    for p in (str(phase1_root), str(phase1_src)):
        if p not in sys.path:
            sys.path.insert(0, p)


def load_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return yaml.safe_load(os.path.expandvars(raw))


def main():
    ap = argparse.ArgumentParser(description='List candidate start nodes for sequence diagrams')
    ap.add_argument('--project-id', type=int, required=True)
    ap.add_argument('--config', default='config/config.yaml')
    ap.add_argument('--limit', type=int, default=50)
    ap.add_argument('--like', help='keyword to filter FQN/paths (case-insensitive)')
    args = ap.parse_args()

    _add_phase1_to_syspath()

    # Lazy imports after path setup
    from src.models.database import DatabaseManager, File, Class, Method  # type: ignore
    from sqlalchemy import func, literal

    cfg = load_config(args.config)
    db = DatabaseManager(cfg)
    db.initialize()

    session = db.get_session()
    try:
        like = args.like.strip() if args.like else None

        # Methods (join Class->Method->File, build FQN.method)
        fqn_expr = func.coalesce(Class.fqn, Class.name) + literal('.') + Method.name
        q_m = (
            session.query(
                fqn_expr.label('fqn'),
                File.path.label('file_path')
            )
            .select_from(Class)
            .join(Method, Method.class_id == Class.class_id)
            .join(File, Class.file_id == File.file_id)
            .filter(File.project_id == args.project_id)
        )
        if like:
            pat = f"%{like.lower()}%"
            q_m = q_m.filter(func.lower(fqn_expr).like(pat))
        q_m = q_m.order_by('fqn').limit(args.limit)
        methods = q_m.all()

        # JSP Files
        q_j = (
            session.query(File.path)
            .filter(File.project_id == args.project_id)
            .filter(func.lower(File.path).like('%.jsp'))
            .order_by(File.path)
            .limit(args.limit)
        )
        if like:
            pat = f"%{like.lower()}%"
            q_j = q_j.filter(func.lower(File.path).like(pat))
        jsp_files = q_j.all()

    finally:
        session.close()

    print(f"[프로젝트 {args.project_id}] 시작 후보 조회 결과")
    print("")
    print(f"Methods (상위 {len(methods)}건):")
    for row in methods:
        fqn = row[0]
        print(f"  - {fqn}")
    if not methods:
        print("  (없음) — 분석 데이터가 없거나 필터에 걸렸을 수 있습니다")

    print("")
    print(f"JSP Files (상위 {len(jsp_files)}건):")
    for row in jsp_files:
        path = row[0]
        print(f"  - {path}")
    if not jsp_files:
        print("  (없음) — 분석 데이터가 없거나 필터에 걸렸을 수 있습니다")


if __name__ == '__main__':
    main()
