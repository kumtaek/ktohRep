# visualize/cli.py
import argparse
import json
import logging
import sys
import csv
import shutil
import re
import traceback
from pathlib import Path
from typing import Dict, Any, List

from .builders.dependency_graph import build_dependency_graph_json
from .builders.erd import build_erd_json
from .builders.component_diagram import build_component_graph_json
from .builders.sequence_diagram import build_sequence_graph_json
from .builders.relatedness_graph import build_relatedness_graph_json, get_relatedness_summary
from .templates.render import render_html
from .exporters.mermaid_exporter import MermaidExporter
from .renderers.cytoscape_erd_renderer import create_cytoscape_erd


def copy_static_files(output_dir: Path) -> None:
    """시각화에 필요한 static 파일들을 output 디렉토리에 복사"""
    # visualize 모듈의 static 디렉토리 경로 (현재 파일 기준으로 상대 경로)를 가져옵니다.
    current_file = Path(__file__)
    static_source_dir = current_file.parent / "static"
    
    # static 소스 디렉토리가 존재하지 않으면 함수를 종료합니다.
    if not static_source_dir.exists():
        return
        
    # static 파일이 복사될 대상 디렉토리 경로를 설정합니다.
    static_target_dir = output_dir / "static"
    
    # 기존 static 디렉토리가 있으면 제거한 후 새로 복사합니다.
    if static_target_dir.exists():
        shutil.rmtree(static_target_dir)
    
    # static 디렉토리 전체를 대상 디렉토리로 복사합니다.
    shutil.copytree(static_source_dir, static_target_dir)


def sanitize_filename(name: str) -> str:
    """파일 이름으로 안전하게 사용할 수 있도록 문자열을 정리합니다."""
    # 파일 이름에 안전하지 않은 문자를 밑줄로 대체합니다.
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)


def setup_logging(args) -> logging.Logger:
    """명령줄 인수를 기반으로 로깅 설정을 구성합니다."""
    # 로그 레벨을 결정합니다.
    if args.quiet:
        level = logging.WARNING
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    # 핸들러를 설정합니다.
    handlers = []
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding='utf-8'))
    else:
        handlers.append(logging.StreamHandler(sys.stderr))
    
    # 로깅을 구성합니다.
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    return logging.getLogger('visualize.cli')


def export_json(data: Dict[str, Any], json_path: str, logger: logging.Logger) -> None:
    """시각화 데이터를 JSON으로 내보냅니다."""
    try:
        json_file = Path(json_path)
        # JSON 파일의 부모 디렉토리가 없으면 생성합니다.
        json_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터를 JSON 형식으로 파일에 씁니다.
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON이 다음 위치로 내보내졌습니다: {json_file.absolute()}")
        
    except Exception as e:
        error_msg = f"JSON 내보내기 실패: {e}"
        traceback_str = traceback.format_exc()
        logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
        raise


def export_csv(data: Dict[str, Any], csv_dir: str, logger: logging.Logger) -> None:
    """시각화 데이터를 CSV 파일로 내보냅니다."""
    try:
        csv_path = Path(csv_dir)
        # CSV 디렉토리가 없으면 생성합니다.
        csv_path.mkdir(parents=True, exist_ok=True)
        
        # 노드 데이터를 CSV로 내보냅니다.
        nodes = data.get('nodes', [])
        if nodes:
            nodes_file = csv_path / 'nodes.csv'
            with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
                if nodes:
                    fieldnames = ['id', 'label', 'type', 'group']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for node in nodes:
                        row = {k: node.get(k, '') for k in fieldnames}
                        writer.writerow(row)
            
            logger.info(f"노드 CSV가 다음 위치로 내보내졌습니다: {nodes_file.absolute()}")
        
        # 엣지 데이터를 CSV로 내보냅니다.
        edges = data.get('edges', [])
        if edges:
            edges_file = csv_path / 'edges.csv'
            with open(edges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'source', 'target', 'kind', 'confidence']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for edge in edges:
                    row = {k: edge.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            logger.info(f"엣지 CSV가 다음 위치로 내보내졌습니다: {edges_file.absolute()}")
        
    except Exception as e:
        error_msg = f"CSV 내보내기 실패: {e}"
        traceback_str = traceback.format_exc()
        logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
        raise


def export_mermaid(data: Dict[str, Any], markdown_path: str, diagram_type: str, 
                  logger: logging.Logger, metadata: Dict[str, Any] = None,
                  label_max: int = 20, erd_cols_max: int = 10, 
                  class_methods_max: int = 10, class_attrs_max: int = 10,
                  min_confidence: float = 0.0, keep_edge_kinds: tuple = ("includes","call","use_table")) -> None:
    """Mermaid/Markdown 내보내기 (확장자에 따라 .md 또는 .mmd)"""
    try:
        # MermaidExporter를 초기화합니다.
        exporter = MermaidExporter(
            label_max=label_max, 
            erd_cols_max=erd_cols_max,
            class_methods_max=class_methods_max,
            class_attrs_max=class_attrs_max,
            min_confidence=min_confidence,
            keep_edge_kinds=keep_edge_kinds
        )
        
        # 메타데이터를 준비합니다.
        meta_info = metadata or {}
        title = f"Source Analyzer {diagram_type.upper()} Diagram"
        if meta_info.get('project_id'):
            title += f" (Project {meta_info['project_id']})"

        out_path = Path(markdown_path)
        # 출력 경로의 부모 디렉토리가 없으면 생성합니다.
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 확장자에 따라 내보내기 형태를 결정합니다.
        if out_path.suffix.lower() in ['.mmd', '.mermaid']:
            content = exporter.export_mermaid(data, diagram_type)
        else:
            content = exporter.export_to_markdown(data, diagram_type, title, meta_info)
        
        # 파일에 내용을 씁니다.
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Mermaid/Markdown 내보내기 완료: {out_path.absolute()}")
        
    except Exception as e:
        error_msg = f"Mermaid/Markdown 내보내기 실패: {e}"
        traceback_str = traceback.format_exc()
        logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
        raise

def main():
    
    print(f"main@cli")
    
    # 시각화 도구의 명령줄 인수를 파싱하기 위한 ArgumentParser를 설정합니다.
    p = argparse.ArgumentParser(prog='visualize', description='Source Analyzer 시각화 도구')
    
    # === 오늘 개발된 기능: ERD HTML 버전들 ===
    p.add_argument('--diagram-type', default='erd', 
                   choices=['erd'],
                   help='생성할 시각화 종류 (ERD: Cytoscape.js HTML + Mermaid HTML 버전)')

    # 공통 인자
    p.add_argument('--project-name', required=True, help='프로젝트 이름 (DB 스키마 로드용)')
    p.add_argument('-v', '--verbose', action='count', default=0, help='로그 상세화 증가: -v=INFO, -vv=DEBUG')
    p.add_argument('-q', '--quiet', action='store_true', help='조용 모드: 경고/오류만 출력')
    p.add_argument('--log-file', help='로그를 파일로 기록')

    # ERD 관련 인자
    p.add_argument('--tables', help='[erd] 포함할 테이블명 목록(콤마 구분)')
    p.add_argument('--owners', help='[erd] 포함할 스키마/소유자 목록(콤마 구분)')
    p.add_argument('--from-sql', help='[erd] 특정 SQL 기준 ERD (형식: mapper_ns:stmt_id)')
    
    # === 오늘 개발된 기능: Mermaid HTML ERD ===
    p.add_argument('--export-mermaid', nargs='?', const='', default=None, help='Mermaid HTML로 내보내기(.html 경로)')

    # === 기개발분: 향후 제거 예정 ===
    # p.add_argument('--export-html', nargs='?', const='', default=None, help='출력 HTML 경로 (미지정 시 생성 생략, 값 없이 사용 시 기본 경로)')
    # p.add_argument('--min-confidence', type=float, default=0.5, help='최소 신뢰도 임계값')
    # p.add_argument('--max-nodes', type=int, default=2000, help='최대 노드 수')
    # p.add_argument('--mermaid-label-max', type=int, default=20, help='Mermaid 라벨 최대 길이')
    # p.add_argument('--mermaid-erd-max-cols', type=int, default=10, help='Mermaid ERD 컬럼 최대 표기 수')
    # p.add_argument('--export-strategy', choices=['full', 'balanced', 'minimal'], default='balanced', help='Export strategy')
    # p.add_argument('--class-methods-max', type=int, default=10, help='Class diagram methods max')
    # p.add_argument('--class-attrs-max', type=int, default=10, help='Class diagram attributes max')
    # p.add_argument('--keep-edge-kinds', default='include,call,use_table', help='Edge kinds to keep')
    # p.add_argument('--export-json', help='JSON으로 내보내기(파일 경로)')
    # p.add_argument('--export-csv-dir', help='CSV로 내보내기(디렉토리 경로)')
    # p.add_argument('--export-mermaid', nargs='?', const='', default=None, help='Mermaid/Markdown으로 내보내기(.md/.mmd 경로)')
    # 
    # # 각 시각화별 특수 인자 (기개발분)
    # p.add_argument('--kinds', default='call', help='[graph] 포함할 엣지 종류(콤마 구분)')
    # p.add_argument('--focus', help='[graph] 시작 노드(이름/경로/테이블)')
    # p.add_argument('--depth', type=int, default=2, help='[graph/sequence] 중심 기준 최대 깊이')
    # p.add_argument('--cytoscape', action='store_true', help='[erd] Cytoscape.js ERD도 함께 생성')
    # p.add_argument('--start-file', help='[sequence] 시작 파일 경로')
    # p.add_argument('--start-method', help='[sequence] 시작 메서드 이름')
    # p.add_argument('--modules', help='[class] 포함할 모듈/파일 목록(콤마 구분)')
    # p.add_argument('--include-private', action='store_true', help='[class] private 멤버 포함')
    # p.add_argument('--max-methods', type=int, default=10, help='[class] 클래스당 최대 메서드 표시 수')
    # p.add_argument('--min-score', type=float, default=0.5, help='[relatedness] 최소 연관성 점수 임계값 (0.0-1.0)')
    # p.add_argument('--cluster-method', default='louvain', help='[relatedness] 클러스터링 방법')
    # p.add_argument('--summary', action='store_true', help='[relatedness] 연관성 통계 요약만 출력')
    
    print('start')
    try:
        args = p.parse_args()
        logger = setup_logging(args)

        commands_to_run = []
        # 명령어가 지정되지 않은 경우 (기본값 'all'), 'sequence'를 제외한 모든 시각화를 생성합니다.
        if args.diagram_type == 'all':
            commands_to_run = ['graph', 'erd', 'component', 'class', 'relatedness']
            logger.info("명령어가 지정되지 않았습니다. 'sequence'를 제외한 모든 시각화를 생성합니다.")
        else:
            # 특정 명령어가 지정된 경우 해당 명령만 실행합니다.
            commands_to_run.append(args.diagram_type)

        print(f"commands_to_run = {commands_to_run}")

        # 프로젝트명 검증
        if not hasattr(args, 'project_name') or not args.project_name or args.project_name.strip() == '':
            logger.error("오류: 프로젝트명이 유효하지 않습니다.")
            return 1

        # Load config.yaml with project name substitution once
        import yaml
        import os
        config_path = Path(__file__).parent / "config" / "config.yaml"
        config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            if hasattr(args, 'project_name') and args.project_name:
                raw = raw.replace('{project_name}', args.project_name)
            config = yaml.safe_load(raw) or {}

        # Initialize VizDB and get project_id once
        from .data_access import VizDB
        db = VizDB(config, args.project_name)
        project_id = db.get_project_id_by_name(args.project_name)
        
        if project_id is None:
            logger.error(f"오류: 프로젝트 '{args.project_name}'를 찾을 수 없습니다.")
            return 1

        # === 기개발분: export 옵션 검증 (향후 제거 예정) ===
        # ERD는 자동으로 Cytoscape.js HTML 파일을 생성하므로 export 옵션 불필요
        # if args.export_html is None and args.export_mermaid is None:
        #     args.export_html = '' # Enable default html export
        #     args.export_mermaid = '' # Enable default mermaid export

        for cmd_name in commands_to_run:
            print(f"[시작] --- {cmd_name.upper()} 시각화 생성 시작 ---")

            data, html, diagram_type = None, None, cmd_name
            
            # ERD 명령어의 경우 html 변수 초기화
            if cmd_name == 'erd':
                html = ""  # 빈 문자열로 초기화

            # 명령에 따라 시각화 데이터를 생성합니다.
            if cmd_name == 'erd':
                # === 새로 개발된 기능: Cytoscape.js ERD ===
                print('# ERD 데이터를 구축합니다.')
                logger.info("🗃️ 데이터베이스 ERD 분석 중...")
                if args.tables:
                    logger.info(f"📋 대상 테이블: {args.tables}")
                data = build_erd_json(config, project_id, args.project_name, args.tables, args.owners, args.from_sql)
                # 기존 ERD HTML/MD 생성 완전 비활성화 (Cytoscape.js만 사용)
                html = ""  # 빈 문자열로 설정하여 기존 파일 생성 방지
                
                # Cytoscape.js ERD 자동 생성
                logger.info("🎨 Cytoscape.js ERD 생성 중...")
                try:
                    # visualize_dir 변수 정의
                    project_name_for_path = getattr(args, 'project_name', 'default')
                    visualize_dir = Path(f"./project/{project_name_for_path}/report")
                    visualize_dir.mkdir(parents=True, exist_ok=True)
                    
                    # static 폴더 생성 및 JavaScript 라이브러리 복사 (project 폴더 삭제 대비)
                    static_dir = visualize_dir / "static" / "js"
                    static_dir.mkdir(parents=True, exist_ok=True)
                    
                    # JavaScript 라이브러리 복사
                    source_js_dir = Path("./visualize/static/js")
                    if source_js_dir.exists():
                        import shutil
                        for js_file in source_js_dir.glob("*.js"):
                            target_file = static_dir / js_file.name
                            if not target_file.exists() or js_file.stat().st_mtime > target_file.stat().st_mtime:
                                shutil.copy2(js_file, static_dir)
                        logger.info(f"✅ JavaScript 라이브러리 복사 완료: {static_dir}")
                    else:
                        logger.warning(f"⚠️  JavaScript 라이브러리 소스 디렉토리를 찾을 수 없습니다: {source_js_dir}")
                    
                    cytoscape_output_dir = Path(visualize_dir)
                    cytoscape_path = create_cytoscape_erd(data, args.project_name, cytoscape_output_dir)
                    logger.info(f"✅ Cytoscape.js ERD 생성 완료: {cytoscape_path}")
                except Exception as e:
                    logger.warning(f"Cytoscape.js ERD 생성 실패: {e}")
            
            # === 기개발분: 향후 제거 예정 ===
            elif cmd_name == 'graph':
                # 의존성 그래프 데이터를 구축합니다.
                logger.info("📊 의존성 그래프 데이터 분석 중...")
                kinds = args.kinds.split(',') if hasattr(args, 'kinds') and args.kinds else []
                logger.info(f"🔍 엣지 타입: {kinds}")
                data = build_dependency_graph_json(config, project_id, args.project_name, kinds, args.min_confidence, 
                                                 args.focus, args.depth, args.max_nodes)
                logger.info("🎨 HTML 렌더링 중...")
                html = render_html('graph_view.html', data)
            elif cmd_name == 'component':
                # 컴포넌트 그래프 데이터를 구축합니다.
                logger.info("🧩 컴포넌트 구조 분석 중...")
                data = build_component_graph_json(config, project_id, args.project_name, args.min_confidence, args.max_nodes)
                logger.info("🎨 HTML 렌더링 중...")
                html = render_html('graph_view.html', data)
            elif cmd_name == 'class':
                # 데이터베이스 정보로부터 Java 클래스 다이어그램을 생성합니다.
                logger.info("☕ Java 클래스 구조 분석 중...")
                from .builders.class_diagram import build_java_class_diagram_json
                data = build_java_class_diagram_json(config, project_id, args.project_name, 
                                                   args.modules, args.max_methods, args.max_nodes)
                logger.info("🎨 HTML 렌더링 중...")
                html = render_html('class_view.html', data)
            elif cmd_name == 'relatedness':
                # 연관성 통계 요약만 출력하는 경우 처리합니다.
                if args.summary:
                    summary = get_relatedness_summary(config, project_id, args.project_name)
                    logger.info(f"연관성 통계: {summary}")
                    continue
                # 연관성 그래프 데이터를 구축합니다.
                logger.info("🔗 코드 연관성 분석 중... (LLM 처리로 시간이 오래 걸릴 수 있습니다)")
                logger.info(f"⚙️ 클러스터링 방법: {args.cluster_method}, 최소 점수: {args.min_score}")
                data = build_relatedness_graph_json(config, project_id, args.project_name, 
                                                   args.min_score, args.max_nodes, args.cluster_method)
                html = render_html('relatedness_view.html', data)
            elif cmd_name == 'sequence':
                # 시작 파일 또는 메서드가 지정되지 않은 경우 프로젝트 전체를 스캔하여 시퀀스 다이어그램을 생성합니다.
                if not args.start_file and not args.start_method:
                    logger.info("시작 파일/메서드가 지정되지 않았습니다. 프로젝트 전체를 스캔하여 시퀀스 다이어그램을 생성합니다.")
                    file_methods = db.get_files_with_methods(project_id, limit=None)
                    if not file_methods:
                        logger.warning("메소드를 포함한 파일을 찾을 수 없습니다. 프로젝트 분석을 먼저 실행하세요.")
                        continue

                    project_name_for_path = getattr(args, 'project_name', 'default')
                    visualize_dir = Path(f"./project/{project_name_for_path}/report")
                    visualize_dir.mkdir(parents=True, exist_ok=True)
                    copy_static_files(visualize_dir)

                    for fm in file_methods:
                        start_file = fm['file_path']
                        start_method = fm['method_name']
                        try:
                            # 각 파일/메서드 쌍에 대해 시퀀스 그래프 데이터를 구축합니다.
                            data = build_sequence_graph_json(config, project_id, args.project_name,
                                                             start_file, start_method,
                                                             args.depth, args.max_nodes, hide_unresolved=True)
                            
                            # 참여자가 1개 이하인 경우 파일 생성하지 않음
                            if not data or len(data.get('participants', [])) <= 1:
                                logger.info(f"시퀀스 다이어그램 건너뛰기 (참여자 부족): {start_file}:{start_method}")
                                continue
                            
                            html = render_html('sequence_view.html', data)

                            base = sanitize_filename(f"{Path(start_file).stem}_{start_method}")
                            html_path = visualize_dir / f"{base}_sequence.html"
                            with open(html_path, 'w', encoding='utf-8') as f:
                                f.write(html)

                            mermaid_path = visualize_dir / f"{base}_sequence.md"
                            export_mermaid(data, str(mermaid_path), 'sequence', logger,
                                           {'project_id': project_id})

                            logger.info(f"시퀀스 다이어그램 저장: {html_path}")
                        except Exception as e:
                            error_msg = f"{start_file}:{start_method} 처리 실패: {e}"
                            traceback_str = traceback.format_exc()
                            logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                    continue

                # 지정된 시작 파일 및 메서드에 대해 시퀀스 그래프 데이터를 구축합니다.
                data = build_sequence_graph_json(config, project_id, args.project_name,
                                                 args.start_file, args.start_method,
                                                 args.depth, args.max_nodes, hide_unresolved=True)
                # 호출 엣지가 없는 경우 경고를 기록합니다.
                if not data.get('edges'):
                    logger.warning("시퀀스 다이어그램 결과에 호출 엣지가 없습니다. 최소 참여자만 표시됩니다.")
                html = render_html('sequence_view.html', data)
            
            # 데이터 또는 HTML이 생성되지 않은 경우 경고를 기록하고 다음 명령으로 건너뜀니다.
            # ERD 명령어의 경우 Cytoscape.js만 사용하므로 HTML 체크 건너뛰기
            if not data:
                logger.warning(f"'{cmd_name}'에 대한 데이터를 생성하지 못했습니다. 건너뜁니다.")
                continue
            if cmd_name != 'erd' and not html:
                logger.warning(f"'{cmd_name}'에 대한 HTML을 생성하지 못했습니다. 건너뜁니다.")
                continue

            logger.info(f"📊 생성 완료: 노드 {len(data.get('nodes', []))}개, 엣지 {len(data.get('edges', []))}개")
            logger.debug(f"Generated {len(data.get('nodes', []))} nodes and {len(data.get('edges', []))} edges for {cmd_name}")

            # ERD 명령어의 경우 Cytoscape.js만 사용하므로 기존 파일 생성 건너뛰기
            if cmd_name == 'erd':
                logger.info("🎨 Cytoscape.js ERD만 생성됨 - 기존 HTML/MD 파일 생성 건너뛰기")
                # html을 None으로 설정하여 파일 생성 방지
                html = None
                
            # 내보내기 로직
            project_name_for_path = getattr(args, 'project_name', 'default')
            visualize_dir = f"./project/{project_name_for_path}/report"
            
            # 기본 HTML 및 Mermaid 파일 이름을 정의합니다.
            default_html_names = {'graph': 'graph.html', 'erd': 'erd.html', 'component': 'components.html', 'sequence': 'sequence.html', 'class': 'class.html', 'relatedness': 'relatedness.html'}
            default_mermaid_names = {'graph': 'dependency_graph.md', 'erd': 'erd.md', 'component': 'component.md', 'sequence': 'sequence.md', 'class': 'class.md', 'relatedness': 'relatedness.md'}

            # === 기개발분: export 옵션 참조 (향후 제거 예정) ===
            # current_export_html = args.export_html
            current_export_html = None  # ERD는 자동 생성되므로 불필요
            
            # 오늘 개발된 기능: Mermaid ERD
            current_export_mermaid = args.export_mermaid

            # === 오늘 개발된 기능: Mermaid ERD 내보내기 로직 ===
            # Mermaid 내보내기가 활성화된 경우 Mermaid/Markdown 파일을 저장합니다.
            if current_export_mermaid is not None and data is not None:
                from .exporters.mermaid_exporter import MermaidExporter
                from datetime import datetime
                
                # 타임스탬프 기반 파일명 생성: erd_mermaid_yyyymmdd_hms.html
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if current_export_mermaid == '' or current_export_mermaid == 'erd.md':
                    mermaid_filename = f"erd_mermaid_{timestamp}.html"
                else:
                    mermaid_filename = current_export_mermaid
                    
                mermaid_path = Path(visualize_dir) / mermaid_filename
                logger.info(f"📝 Mermaid/Markdown 생성 중: {mermaid_filename}")
                
                # MermaidExporter 인스턴스 생성
                exporter = MermaidExporter()
                
                # Markdown으로 내보내기
                markdown_content = exporter.export_to_markdown(data, diagram_type, 
                                                             title=f"{args.project_name} ERD", 
                                                             metadata={'project_id': project_id})
                
                # 파일 저장
                with open(mermaid_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
                logger.info(f"✅ Mermaid 파일 저장 완료: {mermaid_path}")
            
            # === 기개발분: HTML 내보내기 로직 (향후 제거 예정) ===
            # # HTML 내보내기가 활성화된 경우 HTML 파일을 저장합니다.
            # if current_export_html is not None and html is not None:
            #     logger.info("💾 파일 저장 준비 중...")
            #     html_path = Path(visualize_dir) / current_export_html
            #     html_path.parent.mkdir(parents=True, exist_ok=True)
            #     
            #     # static 파일들을 output 디렉토리에 복사합니다.
            #     logger.info("📁 정적 파일 복사 중...")
            #     copy_static_files(html_path.parent)
            #     
            #     logger.info(f"💾 HTML 파일 저장 중: {current_export_html}")
            #     with open(html_path, 'w', encoding='utf-8') as f:
            #         f.write(html)
            #     logger.info(f"✅ 시각화 HTML 저장 완료: {html_path.absolute()}")
            #     logger.info(f"✅ Static 파일 복사 완료: {html_path.parent / 'static'}")
            # elif current_export_html is not None and html is None:
            #     logger.info("🎨 HTML 내용이 없어서 파일 생성 건너뛰기")

    except KeyboardInterrupt:
        print('사용자에 의해 중단됨', file=sys.stderr)
        return 130
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    except Exception as e:
        error_msg = f"실행 중 예기치 못한 오류: {e}"
        traceback_str = traceback.format_exc()
        logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())