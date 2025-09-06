#!/usr/bin/env python3
# llm_summarize.py - CLI tool for LLM-based code summarization
import sys
import argparse
import yaml
from pathlib import Path
from phase1.llm.summarizer import CodeSummarizer, generate_table_specification_md
from visualize.data_access import VizDB
import logging

def load_config():
    """Load configuration from config.yaml"""
    # 설정 파일 경로를 구성합니다.
    config_path = Path(__file__).parent / "phase1" / "config" / "config.yaml"
    # 설정 파일을 읽어 YAML 형식으로 로드합니다.
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # 명령줄 인수를 파싱하기 위한 ArgumentParser를 설정합니다.
    parser = argparse.ArgumentParser(description='LLM-based Code Summarization')
    # 프로젝트 이름을 지정하는 인수를 추가합니다.
    parser.add_argument('--project-name', required=True, help='Project name to process')
    # 처리할 배치 크기를 지정하는 인수를 추가합니다.
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    # 코드 요약만 처리할지 여부를 지정하는 플래그 인수를 추가합니다.
    parser.add_argument('--code-only', action='store_true', help='Process only code summaries (files, methods, SQL)')
    # 테이블/컬럼 주석만 처리할지 여부를 지정하는 플래그 인수를 추가합니다.
    parser.add_argument('--tables-only', action='store_true', help='Process only table/column comments')
    # 테이블 사양 마크다운을 생성할지 여부를 지정하는 플래그 인수를 추가합니다.
    parser.add_argument('--generate-spec', action='store_true', help='Generate table specification markdown')
    # --force-recreate 인수를 추가합니다.
    parser.add_argument('--force-recreate', action='store_true', help='Force recreation of all summaries by deleting existing ones')
    
    args = parser.parse_args()
    
    try:
        config = load_config()
        
        # 프로젝트 이름을 기반으로 프로젝트 ID를 가져옵니다.
        viz_db = VizDB(config, args.project_name)
        project_id = viz_db.get_project_id_by_name(args.project_name)
        
        if not project_id:
            print(f"오류: 프로젝트 '{args.project_name}'을(를) 찾을 수 없습니다.")
            return 1
        
        print(f"[DEBUG] force_recreate 플래그: {args.force_recreate}")

        # CodeSummarizer에 force_recreate 인수를 전달합니다.
        summarizer = CodeSummarizer(config, debug=True, force_recreate=args.force_recreate)
        
        # LLM이 설정에서 활성화되어 있는지 확인합니다.
        if not config.get('llm', {}).get('enabled', True):
            print("경고: 설정에서 LLM이 비활성화되었습니다. 요약 기능을 사용하려면 config.yaml에서 활성화하십시오.")
            return 1
        
        if args.generate_spec:
            # 테이블 사양 마크다운 파일을 생성합니다.
            output_path = f"./project/{args.project_name}/report/table_specification.md"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            generate_table_specification_md(config, output_path)
            print(f"테이블 사양 생성됨: {output_path}")
            return 0
        
        if not args.tables_only:
            print(f"프로젝트 {args.project_name}에 대한 코드 요약을 처리합니다.")
            summarizer.process_project_summaries(project_id, args.batch_size)
            print("코드 요약 완료")
        
        if not args.code_only:
            print("테이블/컬럼 주석을 처리합니다.")
            summarizer.process_table_comments(args.batch_size)
            print("테이블 주석 개선 완료")
        
        print("LLM 요약 프로세스가 성공적으로 완료되었습니다.")
        return 0
        
    except Exception as e:
        print(f"오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
