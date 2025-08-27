"""
Main orchestrator for Source Analyzer
Coordinates the entire metadata generation process
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import create_database_engine, init_database
from src.database.metadata_engine import MetadataEngine
from src.utils.dependency_analyzer import DependencyAnalyzer
from src.utils.csv_loader import CSVSchemaLoader


class SourceAnalyzer:
    """소스 분석기 메인 클래스"""
    
    def __init__(self, config_path: str = None):
        """초기화"""
        self.config_path = config_path or './config/config.yaml'
        self.config = self.load_config()
        
        # 데이터베이스 및 엔진 초기화
        self.setup_database()
        self.metadata_engine = MetadataEngine(self.config)
        
        print(f"Source Analyzer initialized with config: {self.config_path}")
    
    def load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print(f"Configuration loaded from: {self.config_path}")
                return config
            else:
                # 기본 설정
                print(f"Config file not found: {self.config_path}, using default settings")
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """기본 설정 반환"""
        return {
            'project': {
                'root_path': './PROJECT',
                'supported_extensions': {
                    'java': ['.java'],
                    'jsp': ['.jsp', '.jspx'],
                    'mybatis': ['.xml'],
                    'sql': ['.sql'],
                    'properties': ['.properties']
                }
            },
            'database': {
                'type': 'sqlite',
                'path': './data/metadata.db'
            },
            'parsing': {
                'java': {
                    'thread_count': 4,
                    'max_file_size_mb': 10
                },
                'sql': {
                    'oracle_dialect': True,
                    'extract_joins': True,
                    'extract_filters': True
                },
                'mybatis': {
                    'namespace_extraction': True,
                    'dynamic_sql_analysis': True
                }
            },
            'confidence': {
                'thresholds': {
                    'high': 0.8,
                    'medium': 0.5,
                    'low': 0.2
                }
            },
            'db_schema': {
                'base_path': './PROJECT/{project_name}/DB_SCHEMA',
                'files': {
                    'tables': 'ALL_TABLES.csv',
                    'columns': 'ALL_TAB_COLUMNS.csv',
                    'table_comments': 'ALL_TAB_COMMENTS.csv',
                    'column_comments': 'ALL_COL_COMMENTS.csv',
                    'primary_keys': 'PK_INFO.csv',
                    'views': 'ALL_VIEWS.csv'
                }
            }
        }
    
    def setup_database(self):
        """데이터베이스 설정"""
        db_config = self.config.get('database', {})
        db_path = db_config.get('path', './data/metadata.db')
        
        # 데이터 디렉토리 생성
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 데이터베이스 엔진 생성
        self.engine, self.SessionLocal = create_database_engine(f"sqlite:///{db_path}")
        
        # 테이블 초기화
        init_database(self.engine)
        
        print(f"Database initialized: {db_path}")
    
    def analyze_project(self, project_path: str, project_name: str = None, load_schema: bool = True) -> Dict[str, Any]:
        """프로젝트 전체 분석 실행"""
        print(f"\n{'='*60}")
        print(f"Starting analysis of project: {project_path}")
        print(f"Project name: {project_name or 'auto-detected'}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            # 프로젝트 경로 검증
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"Project path does not exist: {project_path}")
            
            # 프로젝트 이름 자동 감지
            if not project_name:
                project_name = os.path.basename(os.path.abspath(project_path))
            
            results = {}
            
            # 1단계: 데이터베이스 스키마 로드 (선택적)
            if load_schema:
                print("\n[1/3] Loading database schema from CSV files...")
                with self.SessionLocal() as session:
                    csv_loader = CSVSchemaLoader(session, self.config)
                    
                    # 스키마 파일 검증
                    validation = csv_loader.validate_schema_files(project_name)
                    print(f"Schema files validation: {validation}")
                    
                    if any(validation.values()):
                        schema_summary = csv_loader.load_project_schema(project_name)
                        results['schema_loading'] = schema_summary
                        print(f"Schema loading completed: {schema_summary}")
                    else:
                        print("No schema files found, skipping schema loading")
                        results['schema_loading'] = {'status': 'skipped', 'reason': 'no_files'}
            
            # 2단계: 소스코드 메타데이터 생성
            print("\n[2/3] Extracting metadata from source code...")
            metadata_summary = self.metadata_engine.analyze_project(project_path, project_name)
            results['metadata_extraction'] = metadata_summary
            
            # 3단계: 의존성 분석
            print("\n[3/3] Analyzing dependencies and relationships...")
            with self.SessionLocal() as session:
                dependency_analyzer = DependencyAnalyzer(session, self.config)
                dependency_summary = dependency_analyzer.create_dependency_edges(metadata_summary['project_id'])
                results['dependency_analysis'] = dependency_summary
            
            # 전체 결과 요약
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results['summary'] = {
                'project_id': metadata_summary['project_id'],
                'project_name': project_name,
                'project_path': project_path,
                'analysis_duration_seconds': duration,
                'completed_at': end_time.isoformat(),
                'status': 'completed'
            }
            
            # 최종 통계
            final_stats = self.get_project_statistics(metadata_summary['project_id'])
            results['statistics'] = final_stats
            
            print(f"\n{'='*60}")
            print(f"Analysis completed successfully!")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Project ID: {metadata_summary['project_id']}")
            print(f"{'='*60}")
            
            return results
            
        except Exception as e:
            print(f"\nError during analysis: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'summary': {
                    'project_name': project_name,
                    'project_path': project_path,
                    'status': 'failed',
                    'error': str(e),
                    'completed_at': datetime.now().isoformat()
                }
            }
    
    def get_project_statistics(self, project_id: int) -> Dict[str, Any]:
        """프로젝트 통계 조회"""
        stats = self.metadata_engine.get_project_statistics(project_id)
        
        # 의존성 통계 추가
        with self.SessionLocal() as session:
            dependency_analyzer = DependencyAnalyzer(session, self.config)
            dep_stats = dependency_analyzer.get_dependency_statistics(project_id)
            stats.update(dep_stats)
        
        # 스키마 통계 추가
        with self.SessionLocal() as session:
            csv_loader = CSVSchemaLoader(session, self.config)
            schema_stats = csv_loader.get_schema_statistics()
            stats.update(schema_stats)
        
        return stats
    
    def create_sample_project(self, project_name: str = 'sample-app'):
        """샘플 프로젝트 및 스키마 생성"""
        project_path = os.path.join(self.config['project']['root_path'], project_name)
        
        print(f"Creating sample project: {project_path}")
        
        # 프로젝트 디렉토리 생성
        os.makedirs(project_path, exist_ok=True)
        
        # 샘플 데이터베이스 스키마 생성
        with self.SessionLocal() as session:
            csv_loader = CSVSchemaLoader(session, self.config)
            csv_loader.create_sample_schema_files(project_name)
        
        print(f"Sample project created: {project_path}")
        return project_path
    
    def list_projects(self) -> List[Dict]:
        """분석된 프로젝트 목록 조회"""
        with self.SessionLocal() as session:
            from src.models.database import Project
            
            projects = session.query(Project).all()
            project_list = []
            
            for project in projects:
                stats = self.get_project_statistics(project.project_id)
                project_info = {
                    'project_id': project.project_id,
                    'name': project.name,
                    'root_path': project.root_path,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at,
                    'statistics': stats
                }
                project_list.append(project_info)
            
            return project_list


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Source Code Metadata Analyzer')
    parser.add_argument('--config', '-c', default='./config/config.yaml',
                      help='Configuration file path')
    parser.add_argument('--project', '-p', required=False,
                      help='Project root path to analyze')
    parser.add_argument('--name', '-n', required=False,
                      help='Project name (optional)')
    parser.add_argument('--no-schema', action='store_true',
                      help='Skip database schema loading')
    parser.add_argument('--list', '-l', action='store_true',
                      help='List analyzed projects')
    parser.add_argument('--create-sample', action='store_true',
                      help='Create sample project and schema files')
    
    args = parser.parse_args()
    
    try:
        # Source Analyzer 초기화
        analyzer = SourceAnalyzer(args.config)
        
        # 명령 실행
        if args.list:
            # 프로젝트 목록 출력
            projects = analyzer.list_projects()
            print(f"\nAnalyzed Projects ({len(projects)}):")
            print("-" * 60)
            for project in projects:
                print(f"ID: {project['project_id']}, Name: {project['name']}")
                print(f"Path: {project['root_path']}")
                print(f"Files: {project['statistics'].get('total_files', 0)}, "
                      f"Classes: {project['statistics'].get('total_classes', 0)}")
                print("-" * 60)
        
        elif args.create_sample:
            # 샘플 프로젝트 생성
            sample_path = analyzer.create_sample_project()
            print(f"Sample project created at: {sample_path}")
            
            # 샘플 프로젝트 분석
            print("\nAnalyzing sample project...")
            results = analyzer.analyze_project(sample_path, 'sample-app', not args.no_schema)
            
            # 결과 출력
            if results['summary']['status'] == 'completed':
                print(f"\nSample analysis completed:")
                stats = results['statistics']
                for key, value in stats.items():
                    print(f"  {key}: {value}")
        
        elif args.project:
            # 지정된 프로젝트 분석
            results = analyzer.analyze_project(args.project, args.name, not args.no_schema)
            
            # 결과 출력
            if results['summary']['status'] == 'completed':
                print(f"\nAnalysis Results Summary:")
                for key, value in results['summary'].items():
                    print(f"  {key}: {value}")
                
                print(f"\nProject Statistics:")
                for key, value in results['statistics'].items():
                    print(f"  {key}: {value}")
            else:
                print(f"Analysis failed: {results['summary'].get('error', 'Unknown error')}")
        
        else:
            # 기본: 샘플 프로젝트가 있으면 분석, 없으면 생성
            sample_path = os.path.join(analyzer.config['project']['root_path'], 'sample-app')
            
            if os.path.exists(sample_path):
                print(f"Analyzing existing project: {sample_path}")
                results = analyzer.analyze_project(sample_path, 'sample-app', not args.no_schema)
                
                if results['summary']['status'] == 'completed':
                    print(f"\nProject Statistics:")
                    for key, value in results['statistics'].items():
                        print(f"  {key}: {value}")
            else:
                print("No project specified. Use --project to analyze a project or --create-sample to create a sample project.")
                parser.print_help()
    
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()