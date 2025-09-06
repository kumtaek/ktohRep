#!/usr/bin/env python3
"""
LLM Analysis Tool
프로젝트의 JSP, Java, Method, Query 등을 LLM으로 분석하여 요약 정보를 생성하고
데이터베이스 스키마 코멘트를 보강하는 도구
"""

import argparse
import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Dict, Any
import yaml

# 상대경로 import를 위한 경로 설정
phase1_root = Path(__file__).parent.parent
project_root = phase1_root.parent

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG, # DEBUG 레벨로 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # 콘솔로 출력
    ]
)
logger = logging.getLogger('llm_analyzer') # 기존 llm_analyzer 로거 사용

from llm.summarizer import CodeSummarizer, generate_table_specification_md, generate_source_specification_md
from models.database import DatabaseManager
from utils.logger import handle_critical_error, handle_non_critical_error
# from utils.logger import setup_logger # 더 이상 사용하지 않음

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = Path(__file__).parents[2] / "config" / "config.yaml"

    if not config_file.exists():
        logger.error(f"Config file not found: {config_file}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

def get_project_config(global_config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
    """Get project-specific configuration"""
    project_config = global_config.copy()

    # Replace {project_name} placeholders in paths
    def replace_project_name(obj):
        if isinstance(obj, str):
            return obj.replace("{project_name}", project_name)
        elif isinstance(obj, dict):
            return {k: replace_project_name(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_project_name(item) for item in obj]
        else:
            return obj

    project_config = replace_project_name(project_config)
    return project_config

def summarize_code_elements(config: Dict[str, Any], project_name: str, batch_size: int = 10, debug: bool = False, force_recreate: bool = False):
    """JSP, Java, Method, Query 요소들에 대한 LLM 요약 생성"""
    
    # Setup project-specific config
    project_config = get_project_config(config, project_name)
    log_file = Path(project_config['project']['paths']['log_dir']) / 'llm_analysis.log'
    logger.info(f"log_file = {log_file}")
    
    # Setup logging (기존 로거 사용)
    # logger = setup_logger('llm_analyzer', str(log_file))
    logger.info(f"Starting LLM analysis for project: {project_name}")
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"log_file = {log_file}")
    
    # Initialize database manager to get project_id
    dbm = DatabaseManager(project_config['database']['project'])
    dbm.initialize()

    session = dbm.get_session()
    try:
        logger.info('# Get or create project')
        from models.database import Project
        project = session.query(Project).filter(Project.name == project_name).first()
        if not project:
            logger.info(f"Project '{project_name}' not found in database")
            return

        project_id = project.project_id
        logger.info(f"Found project ID: {project_id}")

    finally:
        session.close()

    logger.info('# Initialize summarizer')
    summarizer = CodeSummarizer(project_config, debug=debug, force_recreate=force_recreate)

    try:
        # Process code summaries
        logger.info("Processing file summaries...")
        summarizer.process_project_summaries(project_id, batch_size)

        logger.info("Code element summarization completed!")

    except Exception as e:
        handle_critical_error(logger, "코드 요약 처리 실패", e)


def enhance_db_comments(config: Dict[str, Any], project_name: str, batch_size: int = 10, debug: bool = False):
    """데이터베이스 테이블/컬럼 코멘트를 LLM으로 보강"""
    logger.info(f"Starting database comment enhancement for project: {project_name}")

    # Setup project-specific config
    project_config = get_project_config(config, project_name)

    # Setup logging (기존 로거 사용)
    log_file = Path(project_config['project']['paths']['log_dir']) / 'db_comment_enhancement.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # logger = setup_logger('db_comment_enhancer', str(log_file))

    # Initialize summarizer
    summarizer = CodeSummarizer(project_config, debug=debug, force_recreate=False) # enhance-db는 force_recreate 옵션 없음

    try:
        # Process table/column comments
        logger.info("Processing table and column comment enhancement...")
        summarizer.process_table_comments(batch_size)

        logger.info("Success: Database comment enhancement completed!")

    except Exception as e:
        handle_critical_error(logger, "코멘트 향상 처리 실패", e)


def analyze_joins(config: Dict[str, Any], project_name: str, batch_size: int = 10, debug: bool = False):
    logger.info("""SQL 조인조건 LLM 분석""")
    logger.info(f"Starting join analysis for project: {project_name}")

    # Setup project-specific config
    project_config = get_project_config(config, project_name)

    # Setup logging (기존 로거 사용)
    log_file = Path(project_config['project']['paths']['log_dir']) / 'join_analysis.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # logger = setup_logger('join_analyzer', str(log_file))

    logger.info('# Initialize database manager to get project_id')
    dbm = DatabaseManager(project_config['database']['project'])
    dbm.initialize()

    session = dbm.get_session()
    try:
        logger.debug('# Get or create project')
        from models.database import Project
        project = session.query(Project).filter(Project.name == project_name).first()
        if not project:
            logger.info(f"Project '{project_name}' not found in database")
            return

        project_id = project.project_id
        logger.info(f"Found project ID: {project_id}")

    finally:
        session.close()

    logger.info('# Initialize summarizer')
    summarizer = CodeSummarizer(project_config, debug=debug, force_recreate=False) # analyze-joins는 force_recreate 옵션 없음

    try:
        # Process missing joins
        logger.info("Analyzing SQL joins...")
        summarizer.process_missing_joins(project_id, batch_size)

        logger.info("Join analysis completed!")

    except Exception as e:
        handle_critical_error(logger, "조인 분석 처리 실패", e)


def generate_source_spec_md(config: Dict[str, Any], project_name: str, output_file: str = None):
    """소스코드 명세서 마크다운 파일 생성"""
    logger.info(f"Generating source specification markdown for project: {project_name}")

    # Setup project-specific config
    project_config = get_project_config(config, project_name)

    # Default output path
    if not output_file:
        output_dir = Path(project_config['project']['paths']['output_dir'])
        output_file = str(output_dir / "소스코드명세서.md")

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Generate source specification
        generate_source_specification_md(project_config, output_file)

        logger.info(f"Source specification generated: {output_file}")

    except Exception as e:
        handle_critical_error(logger, "소스 명세서 생성 실패", e)


def generate_table_spec_md(config: Dict[str, Any], project_name: str, output_file: str = None):
    """테이블 명세서 마크다운 파일 생성"""
    logger.info(f"Generating table specification markdown for project: {project_name}")

    # Setup project-specific config
    project_config = get_project_config(config, project_name)

    # Default output path
    if not output_file:
        output_dir = Path(project_config['project']['paths']['output_dir'])
        output_file = str(output_dir / "테이블명세서.md")

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Generate table specification
        generate_table_specification_md(project_config, output_file)

        logger.info(f"Success: Table specification generated: {output_file}")

    except Exception as e:
        handle_critical_error(logger, "테이블 명세서 생성 실패", e)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Analysis Tool for Source Code and Database Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze code elements (JSP, Java, Methods, Queries)
  python llm_analyzer.py summarize --project-name sampleSrc --batch-size 20

  # Enhance database comments
  python llm_analyzer.py enhance-db --project-name sampleSrc

  # Generate table specification markdown
  python llm_analyzer.py table-spec --project-name sampleSrc --output 테이블명세서.md

  # Run full analysis (all operations)
  python llm_analyzer.py full-analysis --project-name sampleSrc
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # Common arguments
    for subparser in []:  # Will be added to each subparser
        pass

    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Generate LLM summaries for code elements')
    summarize_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    summarize_parser.add_argument('--batch-size', '-b', type=int, default=10, help='Number of items to process in each batch')
    summarize_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')
    summarize_parser.add_argument('--debug', '-d', action='store_true', help='Show debug information including LLM interactions')
    summarize_parser.add_argument('--force-recreate', action='store_true', help='Force recreation of LLM summaries by clearing existing ones')


    # Enhance DB command
    enhance_parser = subparsers.add_parser('enhance-db', help='Enhance database table/column comments')
    enhance_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    enhance_parser.add_argument('--batch-size', '-b', type=int, default=10, help='Number of items to process in each batch')
    enhance_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')
    enhance_parser.add_argument('--debug', '-d', action='store_true', help='Show debug information including LLM interactions')

    # Join analysis command
    join_parser = subparsers.add_parser('analyze-joins', help='Analyze SQL join conditions using LLM')
    join_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    join_parser.add_argument('--batch-size', '-b', type=int, default=10, help='Number of SQL units to process in each batch')
    join_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')
    join_parser.add_argument('--debug', '-d', action='store_true', help='Show debug information including LLM interactions')

    # Source spec command
    source_spec_parser = subparsers.add_parser('source-spec', help='Generate source code specification markdown')
    source_spec_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    source_spec_parser.add_argument('--output', '-o', type=str, help='Output file path (default: ./output/{project}/소스코드명세서.md)')
    source_spec_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')

    # Table spec command
    table_spec_parser = subparsers.add_parser('table-spec', help='Generate table specification markdown')
    table_spec_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    table_spec_parser.add_argument('--output', '-o', type=str, help='Output file path (default: ./output/{project}/테이블명세서.md)')
    table_spec_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')

    # Full analysis command
    full_parser = subparsers.add_parser('full-analysis', help='Run complete LLM analysis (all operations)')
    full_parser.add_argument('--project-name', '-p', type=str, required=True, help='Project name to analyze')
    full_parser.add_argument('--batch-size', '-b', type=int, default=10, help='Number of items to process in each batch')
    full_parser.add_argument('--output', '-o', type=str, help='Output file path for specifications')
    full_parser.add_argument('--config', '-c', type=str, help='Path to config.yaml file')
    full_parser.add_argument('--debug', '-d', action='store_true', help='Show debug information including LLM interactions')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Load configuration
    try:
        config = load_config(args.config)

        # Check if LLM is enabled
        if not config.get('llm', {}).get('enabled', True):
            logger.warning("Warning:  LLM is disabled in configuration. Enable it in config.yaml to use this tool.")
            return

    except Exception as e:
        handle_critical_error(logger, "설정 파일 로드 실패", e)

    try:
        if args.command == 'summarize':
            summarize_code_elements(config, args.project_name, args.batch_size, getattr(args, 'debug', False), getattr(args, 'force_recreate', False))

        elif args.command == 'enhance-db':
            enhance_db_comments(config, args.project_name, args.batch_size, getattr(args, 'debug', False))

        elif args.command == 'analyze-joins':
            print('start of analyze-joins')
            analyze_joins(config, args.project_name, args.batch_size, getattr(args, 'debug', False))

        elif args.command == 'source-spec':
            generate_source_spec_md(config, args.project_name, args.output)

        elif args.command == 'table-spec':
            generate_table_spec_md(config, args.project_name, args.output)

        elif args.command == 'full-analysis':
            print("Starting full LLM analysis...")

            # Step 1: Code summarization
            logger.info("Step 1: Code Element Summarization")
            # full-analysis 명령에서는 force_recreate 옵션을 summarize_code_elements에 전달
            summarize_code_elements(config, args.project_name, args.batch_size, getattr(args, 'debug', False), getattr(args, 'force_recreate', False))

            # Step 2: DB comment enhancement
            print("\nStep 2: Database Comment Enhancement")
            enhance_db_comments(config, args.project_name, args.batch_size, getattr(args, 'debug', False))

            # Step 3: Analyze joins
            print("\nStep 3: SQL Join Analysis")
            analyze_joins(config, args.project_name, args.batch_size, getattr(args, 'debug', False))

            # Step 4: Generate specifications
            print("\nStep 4: Generate Specifications")

            # Generate table specification
            table_output = args.output or f"output/{args.project_name}/테이블명세서.md"
            generate_table_spec_md(config, args.project_name, table_output)

            # Generate source specification
            source_output = f"output/{args.project_name}/소스코드명세서.md"
            generate_source_spec_md(config, args.project_name, source_output)

            print("\nFull LLM analysis completed!")
            print(f"Generated files:")
            print(f"  - Table specification: {table_output}")
            print(f"  - Source specification: {source_output}")

    except KeyboardInterrupt:
        logger.error("\nError: Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        handle_critical_error(logger, "예상치 못한 오류 발생", e)

if __name__ == '__main__':
    main()