#!/usr/bin/env python3
# llm_summarize.py - CLI tool for LLM-based code summarization
import sys
import argparse
import yaml
from pathlib import Path
from phase1.llm.summarizer import CodeSummarizer, generate_table_specification_md
from visualize.data_access import VizDB

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='LLM-based Code Summarization')
    parser.add_argument('--project-name', required=True, help='Project name to process')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--code-only', action='store_true', help='Process only code summaries (files, methods, SQL)')
    parser.add_argument('--tables-only', action='store_true', help='Process only table/column comments')
    parser.add_argument('--generate-spec', action='store_true', help='Generate table specification markdown')
    
    args = parser.parse_args()
    
    try:
        config = load_config()
        
        # Get project ID
        viz_db = VizDB(config, args.project_name)
        project_id = viz_db.get_project_id_by_name(args.project_name)
        
        if not project_id:
            print(f"Error: Project '{args.project_name}' not found")
            return 1
        
        summarizer = CodeSummarizer(config)
        
        # Check if LLM is enabled
        if not config.get('llm', {}).get('enabled', True):
            print("Warning: LLM is disabled in config. Enable it in config.yaml to use summarization.")
            return 1
        
        if args.generate_spec:
            output_path = f"./output/{args.project_name}/table_specification.md"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            generate_table_specification_md(config, output_path)
            print(f"Generated table specification: {output_path}")
            return 0
        
        if not args.tables_only:
            print(f"Processing code summaries for project: {args.project_name}")
            summarizer.process_project_summaries(project_id, args.batch_size)
            print("Code summarization completed")
        
        if not args.code_only:
            print("Processing table/column comments")
            summarizer.process_table_comments(args.batch_size)
            print("Table comment enhancement completed")
        
        print("LLM summarization process completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())