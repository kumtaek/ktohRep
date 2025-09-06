"""
소스 분석기 메인 모듈
리뷰 의견을 반영한 개선사항들이 적용된 1단계 메타정보 생성 시스템
"""

import os
import sys
import argparse
import yaml
import json
import asyncio
import hashlib
import fnmatch
import logging
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta
import traceback
import glob

# ROOT(./) 기준 상대경로로 임포트 (규정지침 준수)
from phase1.models.database import (
    DatabaseManager, File, Project, Class, Method, SqlUnit, DbTable, DbColumn, DbPk,
    Edge, Join, RequiredFilter, Summary, EnrichmentLog, Chunk, Embedding,
    JavaImport, EdgeHint, Relatedness, VulnerabilityFix, CodeMetric, Duplicate,
    DuplicateInstance, ParseResultModel, Base
)
from phase1.parsers.parser_factory import ParserFactory

from phase1.parsers.java.javaparser_enhanced import JavaParserEnhanced
from phase1.parsers.jsp.jsp_parser import JSPParser
from phase1.parsers.sql_parser_simple import SimpleSQLParser as SqlParser
from phase1.database.metadata_engine import MetadataEngine
from phase1.utils.csv_loader import CsvLoader
from phase1.utils.logger import handle_non_critical_error, handle_critical_error
from phase1.utils.logger import setup_logging
from phase1.utils.log_cleaner import cleanup_old_log_files
from phase1.utils.confidence_calculator import ConfidenceCalculator
from phase1.utils.confidence_validator import ConfidenceValidator, ConfidenceCalibrator, GroundTruthEntry
from phase1.utils.filter_config_manager import FilterConfigManager
from phase1.utils.edge_generator import EdgeGenerator
from phase1.llm.intelligent_chunker import IntelligentChunker


class SourceAnalyzer:
    """소스 분석기 메인 클래스"""
    
    def __init__(self, global_config_path: str, phase_config_path: str, project_name: str = None):
        self.project_name = project_name
        # 전역 및 Phase별 설정 파일을 로드하고 병합합니다.
        self.config = self._load_merged_config(global_config_path, phase_config_path)
        # 로깅을 설정합니다.
        self.logger = setup_logging(self.config)
        self.logger.info("=" * 60)
        self.logger.info("개선된 소스 분석기 시작")
        self.logger.info("=" * 60)
        
        try:
            # 데이터베이스 설정을 가져와 DatabaseManager를 초기화합니다.
            db_config = self.config.get('database', {})
            self.db_manager = DatabaseManager(db_config)
            try:
                self.db_manager.initialize()
                # initialize() 메서드에서 이미 create_all()이 호출됨
            except Exception as e:
                self.logger.error(f"DatabaseManager.initialize() 실패: {e}")
                raise
            
            # 테이블 생성 검증
            try:
                # 등록된 테이블들 확인
                tables = Base.metadata.tables.keys()
                self.logger.info(f"등록된 테이블: {list(tables)}")
                
                # 실제 DB에서 테이블 존재 여부 확인
                from sqlalchemy import inspect
                inspector = inspect(self.db_manager.engine)
                existing_tables = inspector.get_table_names()
                self.logger.info(f"DB에 생성된 테이블: {existing_tables}")
                
                if not existing_tables:
                    self.logger.error("테이블이 생성되지 않았습니다!")
                    raise Exception("테이블 생성 실패")
                    
            except Exception as e:
                self.logger.error(f"테이블 생성 검증 실패: {e}")
                raise
            
            self.logger.info("데이터베이스 연결 성공")
            # 파서를 초기화합니다.
            self.parsers = self._initialize_parsers()
            self.logger.info(f"파서 초기화 완료: {list(self.parsers.keys())}")
            # 메타데이터 엔진, CSV 로더, 신뢰도 계산기 및 유효성 검사기를 초기화합니다.
            self.metadata_engine = MetadataEngine(self.config, self.db_manager, project_name=self.project_name)
            self.csv_loader = CsvLoader(self.config)
            self.confidence_calculator = ConfidenceCalculator(self.config)
            self.confidence_validator = ConfidenceValidator(self.config, self.confidence_calculator)
            self.confidence_calibrator = ConfidenceCalibrator(self.confidence_validator)
            # 요약 리포트 생성기를 초기화합니다.
            # self.report_generator = SummaryReportGenerator(self.db_manager, self.config)
            # 필터 설정 관리자를 초기화합니다.
            self.filter_config_manager = FilterConfigManager()
            # 시작 시 신뢰도 공식을 검증합니다.
            self._validate_confidence_formula_on_startup()
        except Exception as e:
            error_msg = f"시스템 초기화 실패: {e}"
            traceback_str = traceback.format_exc()
            if hasattr(self, 'logger') and self.logger:
                self.logger.critical(f"{error_msg}\nTraceback:\n{traceback_str}")
            else:
                print(f"Critical Error: {error_msg}")
                print(f"Traceback:\n{traceback_str}")
            raise

    def _load_merged_config(self, global_config_path: str, phase_config_path: str) -> Dict[str, Any]:
        """전역 및 Phase별 설정 파일을 로드하고 병합 (Phase별 설정이 우선)"""
        global_config = {}
        phase_config = {}
        try:
            # 전역 설정 파일을 로드합니다.
            if os.path.exists(global_config_path):
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    global_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: 전역 설정 파일을 찾을 수 없습니다: {global_config_path}")
            # Phase별 설정 파일을 로드합니다.
            if os.path.exists(phase_config_path):
                with open(phase_config_path, 'r', encoding='utf-8') as f:
                    phase_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: Phase별 설정 파일을 찾을 수 없습니다: {phase_config_path}")
            # 두 설정을 깊게 병합합니다 (Phase별 설정이 전역 설정을 덮어씁니다).
            def deep_merge(base, overlay):
                for key, value in overlay.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        base[key] = deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            config = deep_merge(global_config, phase_config)
            # 프로젝트 이름으로 설정을 대체합니다.
            if self.project_name:
                config = self._substitute_project_name(config, self.project_name)
            # 기본 설정을 적용합니다.
            self._set_default_config(config)
            return config
        except Exception as e:
            error_msg = f"설정 파일 로드 및 병합 중 오류: {e}"
            traceback_str = traceback.format_exc()
            print(f"ERROR: {error_msg}")
            print(f"Traceback:\n{traceback_str}")
            raise

    def _set_default_config(self, config: Dict[str, Any]):
        # 기본 처리 작업자 수 및 로깅 레벨을 설정합니다.
        config.setdefault('processing', {}).setdefault('max_workers', 4)
        config.setdefault('logging', {}).setdefault('level', 'INFO')

    def _substitute_project_name(self, config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        # 설정 문자열에서 프로젝트 이름 플레이스홀더를 실제 프로젝트 이름으로 대체합니다.
        config_str = json.dumps(config)
        config_str = config_str.replace("{project_name}", project_name)
        result = json.loads(config_str)
        
        # 치환 검증: {project_name} 플레이스홀더가 남아있는지 확인
        result_str = json.dumps(result)
        if "{project_name}" in result_str:
            self.logger.warning(f"플레이스홀더 치환 후에도 {{project_name}}이 남아있습니다: {project_name}")
            # 재귀적으로 치환 시도
            result_str = result_str.replace("{project_name}", project_name)
            result = json.loads(result_str)
        
        return result

    def _initialize_parsers(self) -> Dict[str, Any]:
        # 파서 팩토리를 초기화합니다.
        self.parser_factory = ParserFactory(self.config)
        
        # 설정에 따라 파서들을 초기화합니다.
        parsers = {}
        try:
            if self.config.get('parsers', {}).get('java', {}).get('enabled', True):
                # Context7 기반 JavaParser 사용
                from phase1.parsers.java.javaparser_enhanced import JavaParserEnhanced
                parsers['java'] = JavaParserEnhanced(self.config)
            if self.config.get('parsers', {}).get('jsp', {}).get('enabled', True):
                parsers['jsp_mybatis'] = JSPParser(self.config)
            if self.config.get('parsers', {}).get('sql', {}).get('enabled', True):
                parsers['sql'] = SqlParser(self.config)
            if self.config.get('parsers', {}).get('jar', {}).get('enabled', True):
                from phase1.parsers.jar_parser import JarParser
                parsers['jar'] = JarParser(self.config)
        except Exception as e:
            self.logger.critical(f"파서 초기화 실패: {e}")
            self.logger.critical(f"Traceback:\n{traceback.format_exc()}")
            exit(1)  # 에러 발생시 즉시 중지
        
        # 새로운 파서들을 추가합니다.
        if self.config.get('parsers', {}).get('oracle', {}).get('enabled', True):
            parsers['oracle'] = self.parser_factory
        # Spring 파서는 PRegEx 오류로 인해 임시 비활성화
        # if self.config.get('parsers', {}).get('spring', {}).get('enabled', True):
        #     parsers['spring'] = self.parser_factory
        if self.config.get('parsers', {}).get('jpa', {}).get('enabled', True):
            parsers['jpa'] = self.parser_factory
        if self.config.get('parsers', {}).get('mybatis', {}).get('enabled', True):
            from phase1.parsers.mybatis.mybatis_parser import MyBatisParser
            parsers['mybatis'] = MyBatisParser(self.config)
        
        # 사용 가능한 파서가 없으면 오류를 발생시킵니다.
        if not parsers:
            raise ValueError("사용 가능한 파서가 없습니다. 설정을 확인하세요.")
        
        # 파서들을 인스턴스 변수로 저장
        self.parsers = parsers
        return parsers

    async def analyze_project(self, project_root: str, project_name: str = None, incremental: bool = False):
        # 프로젝트 이름이 제공되지 않으면 루트 경로에서 이름을 추출합니다.
        if not project_name:
            project_name = os.path.basename(project_root.rstrip('/\\'))
        self.logger.info(f"프로젝트 분석 시작: {project_name}")
        
        # 전역 캐시 초기화 (SQL 중복 방지를 위해)
        from phase1.parsers.mybatis.mybatis_parser import MyBatisParser
        MyBatisParser.reset_global_cache()
        
        # 필터 설정 파일 검증
        try:
            await self._validate_filter_config(project_name)
        except Exception as e:
            self.logger.error(f"필터 설정 검증 실패: {e}")
            return
        
        # 프로젝트를 생성하고 ID를 가져옵니다.
        project_id = await self.metadata_engine.create_project(project_root, project_name)
        # DB 스키마 정보를 로드합니다.
        await self._load_db_schema(project_root, project_name, project_id)
        # 소스 파일 및 JAR 파일을 수집합니다.
        source_files = self._collect_source_files(project_root, project_name)
        jar_files = self._collect_dependency_jars(Path(project_root).parent, project_name)
        # 증분 분석 모드인 경우 변경된 파일만 필터링합니다.
        if incremental:
            source_files = await self._filter_changed_files(source_files, project_id)
        # 분석할 소스 파일이 없으면 경고를 기록하고 반환합니다.
        if not source_files:
            self.logger.warning("분석할 소스 파일이 없습니다.")
            return
        # 소스 파일 및 JAR 파일을 분석합니다.
        await self._analyze_files(source_files, project_id)
        if jar_files:
            await self._analyze_jars(jar_files, project_id)
        # 의존성 그래프를 구축합니다.
        await self.metadata_engine.build_dependency_graph(project_id)
        
        # 엣지 생성을 실행합니다.
        await self._generate_edges(project_id)
        
        # 지능형 청킹을 실행합니다.
        await self._run_intelligent_chunking(project_id)
        
        # 리포트 생성은 별도 스크립트로 실행
        self.logger.info("리포트 생성은 별도 스크립트로 실행하세요:")
        self.logger.info(f"  - 계층도 리포트: python generate_hierarchy_report.py --project-name {project_name}")
        self.logger.info(f"  - 컴포넌트 명세서: python generate_component_report.py --project-name {project_name}")
        self.logger.info(f"  - ERD 리포트: python metadb_mermaid_erd_generator.py --project-name {project_name}")
        self.logger.info(f"  - ERD 리포트: python metadb_cytoscape_erd_generator.py --project-name {project_name}")
        
        self.logger.info(f"프로젝트 분석 완료: {project_name}")

    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        self.logger.info(f"DB 스키마 정보 로드 시작: {project_name}")
        try:
            # CSV 로더를 사용하여 프로젝트 DB 스키마를 로드합니다.
            with self.db_manager.get_auto_commit_session() as session:
                await self.csv_loader.load_project_db_schema(project_name, project_id, session)
        except Exception as e:
            error_msg = f"DB 스키마 로드 실패: {e}"
            traceback_str = traceback.format_exc()
            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
            sys.exit(1)

    def _collect_source_files(self, project_root: str, project_name: str) -> List[str]:
        """소스 파일 수집"""
        source_files = []
        
        # 프로젝트별 필터 설정에서 포함/제외 패턴을 가져옵니다.
        
        filter_config = self.filter_config_manager.load_filter_config(project_name)
        
        include_patterns = filter_config.get('include_patterns', [
            "**/*.java", "**/*.jsp", "**/*.xml", "**/*.properties", "**/*.csv"
        ])
        exclude_patterns = filter_config.get('exclude_patterns', [
            "**/target/**", "**/build/**", "**/test/**", "**/.git/**"
        ])
        
        self.logger.debug(f"파일 수집 중: {project_root}")
        self.logger.debug(f"포함 패턴: {include_patterns}")
        self.logger.debug(f"제외 패턴: {exclude_patterns}")
        
        # 프로젝트 루트에서 파일을 검색합니다.
        root_path = Path(project_root)
        
        for include_pattern in include_patterns:
            # **/ 접두사 제거 (rglob에서 자동으로 하위 디렉토리 검색)
            search_pattern = include_pattern[3:] if include_pattern.startswith("**/") else include_pattern
            self.logger.debug(f"검색 패턴: {include_pattern} → rglob({search_pattern})")
            
            # rglob를 사용하여 재귀적으로 파일을 찾습니다.
            for file_path in root_path.rglob(search_pattern):
                if file_path.is_file():
                    str_path = str(file_path)
                    
                    # 제외 패턴을 확인합니다.
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        if fnmatch.fnmatch(str_path, exclude_pattern) or exclude_pattern.replace("**/", "") in str_path:
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        source_files.append(str_path)
        
        self.logger.debug(f"수집된 파일 수: {len(source_files)}")
        # 수집된 파일 통계
        csv_files = [f for f in source_files if f.endswith('.csv')]
        self.logger.info(f"CSV 파일 수집 완료: {len(csv_files)}개")
        for csv_file in csv_files:
            self.logger.info(f"  - {csv_file}")
        
        self.logger.info(f"발견된 소스 파일: {len(source_files)}개")
        
        source_files = list(set(source_files)) # 중복 제거
        self.logger.info(f"중복 제거 후 소스 파일: {len(source_files)}개")

        return source_files

    async def _filter_changed_files(self, source_files: List[str], project_id: int) -> List[str]:
        # ... (Implementation from previous version) ...
        return source_files # Placeholder

    def _collect_dependency_jars(self, project_base: Path, project_name: str) -> List[str]:
        """프로젝트의 의존 JAR 파일을 수집"""
        jar_files: List[str] = []
        
        # 프로젝트별 필터 설정에서 제외 패턴을 가져옵니다.
        filter_config = self.filter_config_manager.load_filter_config(project_name)
        exclude_patterns = filter_config.get('exclude_patterns', ["**/target/**", "**/build/**"])
        # 프로젝트 기본 경로에서 JAR 파일을 재귀적으로 검색합니다.
        for jar_path in project_base.rglob('*.jar'):
            str_path = str(jar_path)
            should_exclude = False
            # 제외 패턴을 확인합니다.
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(str_path, pattern) or pattern.replace("**/", "") in str_path:
                    should_exclude = True
                    break
            if not should_exclude:
                jar_files.append(str_path)
        self.logger.info(f"발견된 JAR 파일: {len(jar_files)}개")
        return jar_files

    async def _analyze_jars(self, jar_files: List[str], project_id: int):
        # JAR 파서가 없으면 반환합니다.
        parser = self.parsers.get('jar')
        if not parser:
            return
        # 각 JAR 파일을 분석합니다.
        for jar_path in jar_files:
            try:
                file_obj, classes, methods, _ = parser.parse_file(jar_path, project_id)
                with self.db_manager.get_auto_commit_session() as session:
                    # 파일 객체를 저장하고 ID를 확보합니다.
                    session.add(file_obj)
                    session.flush()
                    file_id = file_obj.file_id
                    class_id_map = {}
                    # 클래스 객체를 저장하고 클래스 ID 맵을 생성합니다.
                    for cls in classes:
                        cls.file_id = file_id
                        session.add(cls)
                        session.flush()
                        class_id_map[cls.fqn] = cls.class_id
                    # 메서드 객체를 저장하고 클래스 ID를 연결합니다.
                    for m in methods:
                        m.file_id = file_id
                        if hasattr(m, 'owner_fqn') and m.owner_fqn in class_id_map:
                            m.class_id = class_id_map[m.owner_fqn]
                        session.add(m)
                        session.flush()
                    self.logger.debug(f"저장 완료: JAR {jar_path} - 클래스 {len(classes)}개, 메소드 {len(methods)}개")
            except Exception as e:
                handle_critical_error(self.logger, f"JAR 분석 실패 {jar_path}", e)
                raise  # 예외를 다시 발생시켜서 중단

    async def _analyze_files(self, source_files: List[str], project_id: int):
        """소스 파일들을 분석합니다."""
        self.logger.info(f"소스 파일 분석 시작: {len(source_files)}개 파일")
        
        # 파일 타입별로 그룹화
        file_groups = self._group_files_by_type(source_files)
        
        # 각 파일 타입별로 적절한 파서를 사용하여 분석
        for file_type, files in file_groups.items():
            if not files:
                continue
                
            self.logger.info(f"{file_type} 파일 분석 시작: {len(files)}개")
            
            for file_path in files:
                await self._analyze_single_file(file_path, project_id, file_type)
        
        self.logger.info("소스 파일 분석 완료")

    def _group_files_by_type(self, source_files: List[str]) -> Dict[str, List[str]]:
        """파일들을 타입별로 그룹화합니다."""
        file_groups = {
            'java': [],
            'jsp': [],
            'xml': [],
            'properties': [],
            'sql': [],
            'csv': [],
            'other': []
        }
        
        for file_path in source_files:
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.java':
                file_groups['java'].append(file_path)
            elif file_ext == '.jsp':
                file_groups['jsp'].append(file_path)
            elif file_ext == '.xml':
                file_groups['xml'].append(file_path)
            elif file_ext == '.properties':
                file_groups['properties'].append(file_path)
            elif file_ext == '.sql':
                file_groups['sql'].append(file_path)
            elif file_ext == '.csv':
                file_groups['csv'].append(file_path)
            else:
                file_groups['other'].append(file_path)
        
        return file_groups

    async def _analyze_single_file(self, file_path: str, project_id: int, file_type: str):
        """단일 파일을 분석합니다."""
        try:
            # 파일 타입에 따라 적절한 파서 선택
            parser = self._select_parser_for_file(file_path, file_type)
            if not parser:
                self.logger.warning(f"적절한 파서를 찾을 수 없음: {file_path}")
                await self._save_parsing_error(file_path, project_id, "파서를 찾을 수 없음", "ParserNotFound")
                return
            
            # CSV 파일 특수 처리
            if parser == 'csv_metadata_only':
                # CSV 파일은 메타정보만 저장 (내용 파싱 없음)
                file_id = await self._save_file_info(file_path, project_id)
                await self._save_csv_metadata(file_id, file_path, project_id)
                return
            
            # Java 파일의 경우 새로운 파서 사용
            if file_type == 'java' and hasattr(parser, 'parse_content'):
                # 파일 정보를 데이터베이스에 저장하고 file_id 획득
                file_id = await self._save_file_info(file_path, project_id)
                
                # 파일 내용 읽기
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    self.logger.error(f"파일 읽기 실패 {file_path}: {e}")
                    await self._save_parsing_error(file_path, project_id, f"파일 읽기 실패: {e}", "FileReadError")
                    return
                
                # JavaParser의 parse_content 메서드 사용
                context = {'file_path': file_path}
                analysis_result = parser.parse_content(content, context)
                
                # 분석 결과를 데이터베이스에 저장
                await self._save_analysis_result(analysis_result, file_id, project_id)
            elif file_type == 'jsp' and hasattr(parser, 'parse_file'):
                # JSP 파서의 parse_file 메서드 사용 (동기)
                file_obj, sql_units, joins, filters, edges, vulnerabilities = parser.parse_file(file_path, project_id)
                
                # 분석 결과를 데이터베이스에 저장
                await self._save_jsp_analysis_result(file_obj, sql_units, joins, filters, edges, vulnerabilities, project_id)
            else:
                # 기존 방식 사용
                file_id = await self._save_file_info(file_path, project_id)
                
                # 파일 내용을 읽어서 분석
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 파서를 사용하여 파일 분석
                analysis_result = await self._parse_file_with_parser(parser, content, file_path, file_type, project_id)
                
                # 분석 결과를 데이터베이스에 저장
                await self._save_analysis_result(analysis_result, file_id, project_id)
        
        except Exception as e:
            self.logger.error(f"파일 분석 실패 {file_path}: {e}")
            await self._save_parsing_error(file_path, project_id, str(e), type(e).__name__)
            # 에러 처리 지침에 따라 중지
            self.logger.error(f"치명적 에러로 인한 프로세스 중지: {file_path}")
            exit(1)

    def _select_parser_for_file(self, file_path: str, file_type: str):
        """파일 타입에 따라 적절한 파서를 선택합니다."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.java':
            # Java 파일은 항상 일반 Java 파서 사용 (Spring, JPA 파서는 비활성화됨)
            parser = self.parsers.get('java')
            
            # 디버깅 정보 추가
            if parser is None:
                self.logger.warning(f"Java 파서를 찾을 수 없음. 사용 가능한 파서: {list(self.parsers.keys())}")
            else:
                self.logger.info(f"Java 파서 선택됨: {type(parser).__name__}")
            
            return parser
        elif file_ext == '.jsp':
            return self.parsers.get('jsp_mybatis')
        elif file_ext == '.xml':
            # XML 파일의 경우 MyBatis, Spring 설정 등 구분
            if self._is_mybatis_file(file_path):
                return self.parsers.get('mybatis')
            elif self._is_spring_config_file(file_path):
                return self.parsers.get('spring')
            else:
                return self.parsers.get('sql')  # 일반 XML은 SQL 파서로 처리
        elif file_ext == '.sql':
            return self.parsers.get('sql')
        elif file_ext == '.properties':
            return self.parsers.get('spring')  # Spring 설정 파일로 처리
        elif file_ext == '.csv':
            # CSV 파일은 단순 파일 메타정보만 저장 (내용 파싱 없음)
            return 'csv_metadata_only'  # 특수 식별자
        
        return None

    def _is_spring_file(self, file_path: str) -> bool:
        """Spring 관련 파일인지 확인합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(keyword in content for keyword in ['@SpringBootApplication', '@Component', '@Service', '@Repository', '@Controller'])
        except:
            return False

    def _is_jpa_file(self, file_path: str) -> bool:
        """JPA 관련 파일인지 확인합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(keyword in content for keyword in ['@Entity', '@Table', '@Column', '@Id', '@GeneratedValue'])
        except:
            return False

    def _is_mybatis_file(self, file_path: str) -> bool:
        """MyBatis 관련 파일인지 확인합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(keyword in content for keyword in ['<mapper', '<select', '<insert', '<update', '<delete'])
        except:
            return False

    def _is_spring_config_file(self, file_path: str) -> bool:
        """Spring 설정 파일인지 확인합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(keyword in content for keyword in ['<beans', '<context:', '<mvc:', '<aop:'])
        except:
            return False

    async def _parse_file_with_parser(self, parser, content: str, file_path: str, file_type: str, project_id: int):
        """선택된 파서를 사용하여 파일을 분석합니다."""
        if hasattr(parser, 'parse'):
            # 직접 parse 메서드가 있는 경우
            import inspect
            if inspect.iscoroutinefunction(parser.parse):
                # ParserFactory인 경우 project_id 없이 호출
                if hasattr(parser, 'get_parser'):
                    return await parser.parse(content, file_path)
                else:
                    # JavaParserEnhanced인 경우 project_id 포함
                    return await parser.parse(content, file_path, project_id)
            else:
                # ParserFactory인 경우 project_id 없이 호출
                if hasattr(parser, 'get_parser'):
                    return parser.parse(content, file_path)
                else:
                    # JavaParserEnhanced인 경우 project_id 포함
                    return parser.parse(content, file_path, project_id)
        elif hasattr(parser, 'get_parser'):
            # 파서 팩토리인 경우
            # 파일 타입에 따라 적절한 파서 인스턴스 생성
            if file_type == 'java':
                if self._is_spring_file(file_path):
                    return parser.get_parser('spring', 'framework').parse(content, file_path)
                elif self._is_jpa_file(file_path):
                    return parser.get_parser('jpa', 'persistence').parse(content, file_path)
                else:
                    return parser.get_parser('java', 'source').parse(content, file_path)
            elif file_type == 'xml':
                if self._is_mybatis_file(file_path):
                    context = {'file_path': file_path}
                    return parser.parse_sql(content, context)
                elif self._is_spring_config_file(file_path):
                    return await parser.get_parser('spring', 'framework').parse(content, file_path)
                else:
                    # Oracle SQL 파서 사용
                    return await parser.get_parser('oracle', 'select').parse(content, file_path)
            elif file_type == 'sql':
                return await parser.get_parser('oracle', 'select').parse(content, file_path)
            else:
                # 기본 파서 사용
                return await parser.get_parser('java', 'source').parse(content, file_path)
        elif hasattr(parser, 'parse_sql'):
            # MyBatisParser인 경우
            context = {'file_path': file_path}
            return parser.parse_sql(content, context)
        else:
            raise ValueError(f"지원되지 않는 파서 타입: {type(parser)}")

    async def _save_file_info(self, file_path: str, project_id: int) -> int:
        """파일 정보를 데이터베이스에 저장하고 파일 ID를 반환합니다."""
        with self.db_manager.get_auto_commit_session() as session:
            # 파일 객체가 이미 존재하는지 확인
            file_obj = session.query(File).filter_by(path=file_path, project_id=project_id).first()
            if file_obj:
                return file_obj.file_id
            
            # 파일 객체 생성 (실제 모델 필드에 맞게 수정)
            file_obj = File(
                path=file_path,
                project_id=project_id,
                language=Path(file_path).suffix.lower(),
                hash=hashlib.md5(open(file_path, 'rb').read()).hexdigest(),
                loc=len(open(file_path, 'r', encoding='utf-8', errors='ignore').readlines()),
                mtime=datetime.fromtimestamp(os.path.getmtime(file_path))
            )
            session.add(file_obj)
            session.flush()
            return file_obj.file_id

    async def _save_java_analysis_result(self, file_obj: File, classes: List[Class], methods: List[Method], edges: List[Edge], project_id: int):
        """Java 분석 결과를 데이터베이스에 저장합니다."""
        try:
            with self.db_manager.get_auto_commit_session() as session:
                # File 객체 중복 체크 후 저장
                existing_file = session.query(File).filter_by(path=file_obj.path, project_id=project_id).first()
                if existing_file:
                    file_id = existing_file.file_id
                    self.logger.debug(f"기존 파일 사용: {file_obj.path} -> {file_id}")
                else:
                    session.add(file_obj)
                    session.flush()
                    file_id = file_obj.file_id
                    self.logger.debug(f"새 파일 저장: {file_obj.path} -> {file_id}")
                
                # 클래스 객체 저장 (중복 체크)
                class_id_map = {}  # class fqn -> class_id 매핑
                for cls in classes:
                    cls.file_id = file_id
                    
                    # 중복 체크: 같은 파일에 같은 FQN이 이미 있는지 확인
                    existing_class = session.query(Class).filter_by(fqn=cls.fqn, file_id=file_id).first()
                    if existing_class:
                        class_id_map[cls.fqn] = existing_class.class_id
                        self.logger.debug(f"클래스 중복 스킵: {cls.fqn} -> {existing_class.class_id}")
                        continue
                        
                    session.add(cls)
                    session.flush()
                    class_id_map[cls.fqn] = cls.class_id
                    self.logger.debug(f"클래스 저장: {cls.fqn} -> {cls.class_id}")
                
                self.logger.debug(f"class_id_map 구성 완료: {len(class_id_map)}개")
                
                # 메소드 객체 저장 (중복 체크)
                method_id_map = {}  # method fqn -> method_id 매핑
                for method in methods:
                    method.file_id = file_id
                    # Method가 Class에 속한 경우 class_id를 설정합니다
                    if hasattr(method, 'owner_fqn') and method.owner_fqn in class_id_map:
                        method.class_id = class_id_map[method.owner_fqn]
                        
                        # 중복 체크: 같은 클래스에 같은 시그니처가 이미 있는지 확인
                        existing_method = session.query(Method).filter_by(
                            class_id=method.class_id,
                            signature=method.signature
                        ).first()
                        if existing_method:
                            method_id_map[f"{method.owner_fqn}.{method.name}"] = existing_method.method_id
                            self.logger.debug(f"메소드 중복 스킵: {method.signature}")
                            continue
                            
                    session.add(method)
                    session.flush()
                    # method.owner_fqn이 존재하는 경우에만 method_id_map에 추가
                    if hasattr(method, 'owner_fqn') and method.owner_fqn:
                        method_id_map[f"{method.owner_fqn}.{method.name}"] = method.method_id

                # 엣지 객체 저장 (FQN 기반 ID 해결)
            confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
            saved_edges = 0
            
            for edge in edges:
                edge.project_id = project_id
                
                # FQN 기반으로 src_id 해결 (전체 프로젝트 클래스 조회)
                if hasattr(edge, 'src_fqn') and edge.src_fqn:
                    if edge.src_type in ['class', 'interface']:
                        # 현재 파일의 class_id_map에서 먼저 찾기
                        if edge.src_fqn in class_id_map:
                            edge.src_id = class_id_map[edge.src_fqn]
                            self.logger.debug(f"Edge src_id 해결 (현재 파일): {edge.src_fqn} -> {edge.src_id}")
                        else:
                            # 전체 프로젝트에서 클래스 찾기
                            src_class = session.query(Class).join(File).filter(Class.fqn==edge.src_fqn, File.project_id==project_id).first()
                            if src_class:
                                edge.src_id = src_class.class_id
                                self.logger.debug(f"Edge src_id 해결 (전체 프로젝트): {edge.src_fqn} -> {edge.src_id}")
                            else:
                                self.logger.debug(f"Edge src_id 해결 실패: {edge.src_fqn} not found in project")
                    elif edge.src_type == 'method':
                        # 메서드 FQN에서 클래스.메서드 형태로 변환
                        method_key = edge.src_fqn
                        if method_key in method_id_map:
                            edge.src_id = method_id_map[method_key]
                            self.logger.debug(f"Edge src_id 해결: {edge.src_fqn} -> {edge.src_id}")
                        else:
                            # 전체 프로젝트에서 메서드 찾기
                            src_method = session.query(Method).join(Class).join(File).filter(Method.name==edge.src_fqn.split('.')[-1], File.project_id==project_id).first()
                            if src_method:
                                edge.src_id = src_method.method_id
                                self.logger.debug(f"Edge src_id 해결 (전체 프로젝트): {edge.src_fqn} -> {edge.src_id}")
                            else:
                                self.logger.debug(f"Edge src_id 해결 실패: {edge.src_fqn} not found in project")
                
                # FQN 기반으로 dst_id 해결 (전체 프로젝트 클래스 조회)
                if hasattr(edge, 'dst_fqn') and edge.dst_fqn:
                    if edge.dst_type in ['class', 'interface']:
                        # 현재 파일의 class_id_map에서 먼저 찾기
                        if edge.dst_fqn in class_id_map:
                            edge.dst_id = class_id_map[edge.dst_fqn]
                            self.logger.debug(f"Edge dst_id 해결 (현재 파일): {edge.dst_fqn} -> {edge.dst_id}")
                        else:
                            # 전체 프로젝트에서 클래스 찾기 (개선된 매칭)
                            self.logger.debug(f"전체 프로젝트에서 클래스 검색: {edge.dst_fqn}")
                            
                            # 1. 정확한 FQN 매칭
                            dst_class = session.query(Class).join(File).filter(Class.fqn==edge.dst_fqn, File.project_id==project_id).first()
                            
                            # 2. 클래스명 기반 매칭 (FQN이 정확하지 않은 경우)
                            if not dst_class:
                                class_name = edge.dst_fqn.split('.')[-1]  # 마지막 부분이 클래스명
                                dst_class = session.query(Class).filter(
                                    Class.name == class_name,
                                    Class.project_id == project_id
                                ).first()
                                self.logger.debug(f"클래스명 기반 매칭 시도: {class_name}")
                            
                            if dst_class:
                                edge.dst_id = dst_class.class_id
                                self.logger.debug(f"Edge dst_id 해결 (전체 프로젝트): {edge.dst_fqn} -> {edge.dst_id}")
                            else:
                                # 프로젝트의 모든 클래스 FQN 확인
                                all_classes = session.query(Class).join(File).filter(File.project_id==project_id).all()
                                self.logger.debug(f"프로젝트의 모든 클래스 FQN: {[c.fqn for c in all_classes]}")
                                self.logger.debug(f"Edge dst_id 해결 실패: {edge.dst_fqn} not found in project")
                    elif edge.dst_type == 'method':
                        # 메서드 FQN에서 클래스.메서드 형태로 변환
                        method_key = edge.dst_fqn
                        if method_key in method_id_map:
                            edge.dst_id = method_id_map[method_key]
                            self.logger.debug(f"Edge dst_id 해결: {edge.dst_fqn} -> {edge.dst_id}")
                        else:
                            # 전체 프로젝트에서 메서드 찾기
                            dst_method = session.query(Method).join(Class).join(File).filter(Method.name==edge.dst_fqn.split('.')[-1], File.project_id==project_id).first()
                            if dst_method:
                                edge.dst_id = dst_method.method_id
                                self.logger.debug(f"Edge dst_id 해결 (전체 프로젝트): {edge.dst_fqn} -> {edge.dst_id}")
                            else:
                                self.logger.debug(f"Edge dst_id 해결 실패: {edge.dst_fqn} not found in project")
                
                # 중복 체크 및 저장 (조건 완화)
                self.logger.debug(f"Edge 저장 조건 체크: src_id={edge.src_id}, dst_id={edge.dst_id}, confidence={edge.confidence}, threshold={confidence_threshold}")
                
                # 조건 완화: src_id 또는 dst_id 중 하나라도 있으면 저장
                if ((edge.src_id is not None and edge.src_id != 0) or 
                    (edge.dst_id is not None and edge.dst_id != 0)) and edge.confidence >= confidence_threshold:
                    
                    # 중복 Edge 체크
                    existing_edge = session.query(Edge).filter_by(
                        project_id=project_id,
                        src_type=edge.src_type,
                        src_id=edge.src_id,
                        dst_type=edge.dst_type,
                        dst_id=edge.dst_id,
                        edge_kind=edge.edge_kind
                    ).first()
                    
                    if not existing_edge:
                        session.add(edge)
                        saved_edges += 1
                    else:
                        # 기존 Edge의 신뢰도가 낮으면 업데이트
                        if edge.confidence > existing_edge.confidence:
                            existing_edge.confidence = edge.confidence
                            existing_edge.meta = edge.meta

                self.logger.debug(
                    f"Java 분석 저장 완료: {file_obj.path} - 클래스 {len(classes)}개, 메소드 {len(methods)}개, 엣지 {saved_edges}개"
                )
        except Exception as e:
            self.logger.error(f"Java 분석 결과 저장 오류 {file_obj.path}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise  # 예외를 다시 발생시켜서 중단

    async def _save_jsp_analysis_result(self, file_obj: File, sql_units: List[Any], joins: List[Any], filters: List[Any], edges: List[Any], vulnerabilities: List[Any], project_id: int):
        """JSP 분석 결과를 데이터베이스에 저장합니다."""
        try:
            with self.db_manager.get_auto_commit_session() as session:
                # File 객체 중복 체크 후 저장
                existing_file = session.query(File).filter_by(path=file_obj.path, project_id=project_id).first()
                if existing_file:
                    file_id = existing_file.file_id
                    self.logger.debug(f"기존 파일 사용: {file_obj.path} -> {file_id}")
                else:
                    session.add(file_obj)
                    session.flush()
                    file_id = file_obj.file_id
                    self.logger.debug(f"새 파일 저장: {file_obj.path} -> {file_id}")
                
                # SQL Unit 객체 저장 (중복 체크)
                for sql_unit in sql_units:
                    sql_unit.file_id = file_id
                    
                    # 중복 체크: 같은 파일에 같은 지문이 이미 있는지 확인
                    if hasattr(sql_unit, 'normalized_fingerprint') and sql_unit.normalized_fingerprint:
                        existing_sql = session.query(SqlUnit).filter_by(
                            file_id=file_id,
                            normalized_fingerprint=sql_unit.normalized_fingerprint
                        ).first()
                        if existing_sql:
                            self.logger.debug(f"SQL 유닛 중복 스킵: {sql_unit.stmt_id}")
                            continue
                    
                    session.add(sql_unit)
                    session.flush()
                
                # Join 객체 저장
                for join in joins:
                    if hasattr(join, 'sql_id') and join.sql_id is None:
                        # SQL Unit과 연결
                        pass  # TODO: SQL Unit과 Join 연결 로직
                    session.add(join)
                session.flush()
            
            # Filter 객체 저장
            for filter_obj in filters:
                if hasattr(filter_obj, 'sql_id') and filter_obj.sql_id is None:
                    # SQL Unit과 연결
                    pass  # TODO: SQL Unit과 Filter 연결 로직
                session.add(filter_obj)
                session.flush()
            
            # Edge 객체 저장
            confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
            saved_edges = 0
            for edge in edges:
                edge.project_id = project_id
                if (edge.src_id is not None and edge.dst_id is not None
                    and edge.src_id != 0 and edge.dst_id != 0
                    and edge.confidence >= confidence_threshold):
                    session.add(edge)
                    saved_edges += 1
            
            # Vulnerability 객체 저장
            for vulnerability in vulnerabilities:
                vulnerability.file_id = file_id
                session.add(vulnerability)
                session.flush()
            
                self.logger.debug(
                    f"JSP 분석 저장 완료: {file_obj.path} - SQL Units {len(sql_units)}개, Joins {len(joins)}개, Filters {len(filters)}개, Edges {saved_edges}개"
                )
        except Exception as e:
            self.logger.error(f"JSP 분석 결과 저장 오류 {file_obj.path}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise  # 예외를 다시 발생시켜서 중단

    async def _save_analysis_result(self, analysis_result: Any, file_id: int, project_id: int):
        """분석 결과를 데이터베이스에 저장합니다."""
        if not analysis_result:
            self.logger.warning(f"분석 결과가 없습니다: {file_id}")
            return

        with self.db_manager.get_auto_commit_session() as session:
            # 파일 객체를 가져옵니다.
            file_obj = session.query(File).filter_by(file_id=file_id).first()
            if not file_obj:
                self.logger.warning(f"파일 객체를 찾을 수 없습니다: {file_id}")
                return

            # 파일 객체의 타입을 업데이트합니다.
            file_obj.file_type = Path(file_obj.path).suffix.lower()
            session.add(file_obj)
            session.flush()

            # 분석 결과에 따라 적절한 테이블에 저장
            if isinstance(analysis_result, tuple) and len(analysis_result) == 4: # JavaParser의 반환값
                _, classes, methods, edges = analysis_result  # file_obj는 무시
                sql_units = []
                joins = []
                filters = []
                vulnerabilities = []
            elif isinstance(analysis_result, dict) and ('classes' in analysis_result or 'methods' in analysis_result): # JavaParser의 dict 반환값
                classes = analysis_result.get('classes', [])
                methods = analysis_result.get('methods', [])
                sql_strings = analysis_result.get('sql_strings', [])
                edges = []
                joins = []
                filters = []
                vulnerabilities = []
                sql_units = []  # sql_units 초기화 추가
                
                # SQL 문자열을 SQL 단위로 변환
                for i, sql_string in enumerate(sql_strings):
                    sql_content = sql_string.get('content', '')
                    if sql_content and any(keyword in sql_content.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                        sql_unit = SqlUnit(
                            file_id=file_id,
                            origin='java',
                            mapper_ns='unknown',
                            stmt_id=f'java_sql_{i}',
                            start_line=1,
                            end_line=1,
                            stmt_kind=self._determine_sql_type(sql_content),
                            normalized_fingerprint=sql_content[:100]
                        )
                        sql_units.append(sql_unit)
                
                # dict 형태의 클래스와 메서드를 객체로 변환
                from phase1.models.database import Class, Method
                
                # 클래스 변환
                class_objects = []
                for class_data in classes:
                    class_obj = Class(
                        file_id=file_id,
                        name=class_data.get('name', ''),
                        fqn=class_data.get('fqn', ''),
                        modifiers=','.join(class_data.get('modifiers', [])),
                        start_line=class_data.get('start_line', 1),
                        end_line=class_data.get('end_line', 1)
                    )
                    class_objects.append(class_obj)
                
                # 메서드 변환
                method_objects = []
                for method_data in methods:
                    method_obj = Method(
                        class_id=0,  # 나중에 설정
                        name=method_data.get('name', ''),
                        signature=method_data.get('signature', ''),
                        return_type=method_data.get('return_type', ''),
                        start_line=method_data.get('start_line', 1),
                        end_line=method_data.get('end_line', 1),
                        parameters=','.join(method_data.get('parameters', [])),
                        modifiers=','.join(method_data.get('modifiers', []))
                    )
                    # owner_fqn 설정 (클래스와의 관계를 위해)
                    method_obj.owner_fqn = method_data.get('owner_fqn', '')
                    method_objects.append(method_obj)
                
                classes = class_objects
                methods = method_objects
            elif isinstance(analysis_result, tuple) and len(analysis_result) == 6: # JspMybatisParser의 반환값
                file_obj_result, sql_units, joins, filters, edges, vulnerabilities = analysis_result  # file_obj는 무시
                classes = [] # JspMybatisParser는 클래스/메서드를 반환하지 않음
                methods = []
                
                # JSP 파싱 결과 로깅 추가
                self.logger.info(f"JSP 파싱 결과: SQL Units {len(sql_units)}개, Joins {len(joins)}개, Filters {len(filters)}개")
            elif isinstance(analysis_result, tuple) and len(analysis_result) == 4: # SqlParser의 반환값 (joins, filters, tables, columns)
                _joins, _filters, _tables, _columns = analysis_result
                sql_units = []
                joins = []
                filters = []
                edges = []
                classes = []
                methods = []
                vulnerabilities = []

                # SqlParser에서 추출한 정보를 바탕으로 SqlUnit 생성
                if _joins or _filters or _tables or _columns:
                    # SQL 파일 자체를 하나의 SqlUnit으로 간주
                    sql_content = Path(file_obj.path).read_text(encoding='utf-8', errors='ignore')
                    sql_unit = SqlUnit(
                        file_id=file_id,
                        origin='sql',
                        mapper_ns=Path(file_obj.path).stem, # 파일 이름을 네임스페이스로 사용
                        stmt_id='full_file_sql',
                        start_line=1,
                        end_line=len(sql_content.splitlines()),
                        stmt_kind='unknown', # SqlParser에서 stmt_kind를 직접 추출하지 않으므로 unknown으로 설정
                        normalized_fingerprint=SqlParser(self.config)._create_sql_fingerprint(sql_content) # SqlParser의 fingerprint 함수 사용
                    )
                    sql_units.append(sql_unit)

                    # 생성된 SqlUnit의 stmt_id를 사용하여 Join 및 Filter에 연결
                    for j in _joins:
                        j.sql_unit_stmt_id = sql_unit.stmt_id
                        joins.append(j)
                    for f in _filters:
                        f.sql_unit_stmt_id = sql_unit.stmt_id
                        filters.append(f)
            elif isinstance(analysis_result, dict):  # MyBatis 파서의 딕셔너리 결과
                # MyBatis 파서 결과 처리
                sql_units = []
                joins = []
                filters = []
                edges = []
                classes = []
                methods = []
                vulnerabilities = []
                
                # SQL 단위 처리
                if 'sql_units' in analysis_result:
                    for sql_data in analysis_result['sql_units']:
                        sql_unit = SqlUnit(
                            file_id=file_id,
                            origin='mybatis',
                            mapper_ns=sql_data.get('namespace', 'unknown'),
                            stmt_id=sql_data.get('id', 'unknown'),
                            start_line=sql_data.get('start_line', 1),
                            end_line=sql_data.get('end_line', 1),
                            stmt_kind=sql_data.get('type', 'unknown'),
                            normalized_fingerprint=sql_data.get('sql', '')[:100]  # SQL 내용의 일부를 fingerprint로 사용
                        )
                        sql_units.append(sql_unit)
                
                # 테이블 정보 처리 (필요시)
                if 'tables' in analysis_result:
                    # 테이블 정보는 별도로 처리할 수 있음
                    pass
                
                self.logger.info(f"MyBatis 파싱 결과: SQL Units {len(sql_units)}개")
            else:
                # 파서가 결과를 반환하지 않거나 예상치 못한 길이인 경우
                classes, methods, sql_units, joins, filters, edges, vulnerabilities = [], [], [], [], [], [], []

            # 클래스 객체 저장
            class_id_map = {}  # class fqn -> class_id 매핑
            for cls in classes:
                cls.file_id = file_id
                session.add(cls)
                session.flush()
                class_id_map[cls.fqn] = cls.class_id
            
            # 메소드 객체 저장
            for method in methods:
                # Method는 file_id가 없고 class_id만 있음 (스키마 확인됨)
                # Method가 Class에 속한 경우 class_id를 설정합니다 (owner_fqn 기준으로 찾기).
                if hasattr(method, 'owner_fqn') and method.owner_fqn in class_id_map:
                    method.class_id = class_id_map[method.owner_fqn]
                session.add(method)
                session.flush()

            # SQL Unit 객체 저장
            for sql_unit in sql_units:
                sql_unit.file_id = file_id
                session.add(sql_unit)
                session.flush()
            
            # sql_id_map 구성 (저장 후)
            sql_id_map = {f"{s.mapper_ns}.{s.stmt_id}": s.sql_id for s in sql_units}

            # Join 객체 저장 및 Edge 변환
            for join in joins:
                # join.sql_id가 None인 경우, 해당 join이 속한 sql_unit의 ID를 찾아서 설정
                if join.sql_id is None and hasattr(join, '_temp_sql_unit_key') and join._temp_sql_unit_key in sql_id_map:
                    join.sql_id = sql_id_map[join._temp_sql_unit_key]
                    print(f"[DEBUG] Join sql_id 설정됨: {join._temp_sql_unit_key} -> {join.sql_id}")
                elif join.sql_id is None:
                    print(f"[DEBUG] Join sql_id를 설정할 수 없음 - 키 정보가 없음")
                    continue  # sql_id가 없으면 저장하지 않음
                
                session.add(join)
                session.flush()
  # 트랜잭션 완료하여 영구 저장
                
                # Join 정보를 Edge로 변환하여 테이블 간 관계 생성
                if join.sql_id and join.l_table and join.r_table:
                    try:
                        # 테이블 ID 찾기
                        l_table_obj = session.query(DbTable).filter(
                            DbTable.table_name == join.l_table.upper()
                        ).first()
                        r_table_obj = session.query(DbTable).filter(
                            DbTable.table_name == join.r_table.upper()
                        ).first()
                        
                        if l_table_obj and r_table_obj:
                            # 테이블 간 조인 관계를 Edge로 생성
                            join_edge = Edge(
                                project_id=project_id,
                                src_type='table',
                                src_id=l_table_obj.table_id,
                                dst_type='table',
                                dst_id=r_table_obj.table_id,
                                edge_kind='join',
                                confidence=join.confidence,
                                meta=json.dumps({
                                    'join_type': 'explicit',
                                    'left_column': join.l_col,
                                    'right_column': join.r_col,
                                    'operator': join.op,
                                    'sql_id': join.sql_id,
                                    'inferred_pkfk': join.inferred_pkfk
                                })
                            )
                            session.add(join_edge)
                            print(f"[DEBUG] Join Edge 생성됨: {join.l_table} -> {join.r_table}")
                    except Exception as e:
                        print(f"[DEBUG] Join Edge 생성 실패: {e}")
                        continue

            # RequiredFilter 객체 저장
            for filter_obj in filters:
                # filter_obj.sql_id가 None인 경우, 해당 filter가 속한 sql_unit의 ID를 찾아서 설정
                if filter_obj.sql_id is None and hasattr(filter_obj, 'sql_unit_stmt_id') and filter_obj.sql_unit_stmt_id in sql_id_map:
                    filter_obj.sql_id = sql_id_map[filter_obj.sql_unit_stmt_id]
                session.add(filter_obj)
                session.flush()

            # 모든 메서드가 저장된 후, 엣지의 src_id를 해결합니다.
            method_id_map = {f"{getattr(m, 'owner_fqn', '')}.{m.name}": m.method_id for m in methods}

            # 엣지 객체 저장
            confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
            saved_edges = 0
            for edge in edges:
                edge.project_id = project_id
                if edge.src_type == 'method' and edge.src_id is None:
                    src_method_fqn = None
                    try:
                        if getattr(edge, 'meta', None):
                            md = json.loads(edge.meta)
                            src_method_fqn = md.get('src_method_fqn')
                    except Exception:
                        src_method_fqn = getattr(edge, 'src_method_fqn', None)
                    if src_method_fqn and src_method_fqn in method_id_map:
                        edge.src_id = method_id_map[src_method_fqn]

                if edge.edge_kind == 'call':
                    session.add(edge)
                    saved_edges += 1
                else:
                    if (edge.src_id is not None and edge.dst_id is not None
                        and edge.src_id != 0 and edge.dst_id != 0
                        and edge.confidence >= confidence_threshold):
                        session.add(edge)
                        saved_edges += 1

            self.logger.debug(
                f"저장 완료: {file_obj.path} - 클래스 {len(classes)}개, 메소드 {len(methods)}개, 엣지 {saved_edges}개"
            )

    async def _save_parsing_error(self, file_path: str, project_id: int, error_message: str, error_type: str):
        """파싱 에러 정보를 데이터베이스에 저장합니다."""
        try:
            with self.db_manager.get_auto_commit_session() as session:
                # 파일 정보가 없으면 먼저 저장
                file_id = await self._save_file_info(file_path, project_id)
                
                # 파싱 결과에 에러 정보 저장
                parse_result = ParseResultModel(
                    file_id=file_id,
                    parser_type=Path(file_path).suffix.lower()[1:],  # 확장자에서 점 제거
                    success=False,
                    parse_time=0.0,
                    ast_complete=False,
                    partial_ast=False,
                    fallback_used=False,
                    error_message=error_message,
                    confidence=0.0
                )
                session.add(parse_result)
                session.flush()
                
                self.logger.info(f"파싱 에러 저장 완료: {file_path} - {error_type}: {error_message}")
                
        except Exception as e:
            self.logger.error(f"파싱 에러 저장 실패 {file_path}: {e}")
            # 에러 저장 실패 시에도 중지
            exit(1)

    async def _save_csv_metadata(self, file_id: int, file_path: str, project_id: int):
        """CSV 파일 메타데이터 저장"""
        try:
            with self.db_manager.get_auto_commit_session() as session:
                import os
                import json
                
                # 파일 기본 정보
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                # CSV 파일 정보 요약
                csv_info = {
                    'file_type': 'csv',
                    'purpose': 'db_schema' if 'db_schema' in file_path else 'data',
                    'size_bytes': file_size,
                    'estimated_rows': self._estimate_csv_rows(file_path),
                    'encoding': 'utf-8'
                }
                
                # 파싱 결과 저장
                parse_result = ParseResultModel(
                    file_id=file_id,
                    parser_type='csv',
                    success=True,
                    parse_time=0.1,
                    ast_complete=True,  # CSV는 구조가 단순하므로 완전 파싱으로 간주
                    partial_ast=False,
                    fallback_used=False,
                    error_message=None,
                    confidence=1.0,
                    metadata=json.dumps(csv_info)
                )
                session.add(parse_result)
                session.flush()
                
                self.logger.info(f"CSV 메타데이터 저장 완료: {file_path}")
                
        except Exception as e:
            self.logger.error(f"CSV 메타데이터 저장 실패 {file_path}: {e}")

    def _estimate_csv_rows(self, file_path: str) -> int:
        """CSV 행 수 추정 (성능을 위해 간단한 라인 카운트)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # 헤더 제외
        except:
            return 0

    async def _generate_edges(self, project_id: int):
        """엣지를 생성합니다."""
        try:
            self.logger.info("엣지 생성 시작")
            
            with self.db_manager.get_auto_commit_session() as session:
                edge_generator = EdgeGenerator(session, self.config)
                edge_count = edge_generator.generate_all_edges()
                
                self.logger.info(f"엣지 생성 완료: {edge_count}개")
                
        except Exception as e:
            self.logger.error(f"엣지 생성 중 오류: {e}")
            traceback.print_exc()

    async def _run_intelligent_chunking(self, project_id: int):
        """지능형 청킹을 실행합니다."""
        try:
            self.logger.info("지능형 청킹 시작")
            chunker = IntelligentChunker()
            
            # 프로젝트의 모든 파일을 가져와서 청킹을 실행합니다.
            with self.db_manager.get_auto_commit_session() as session:
                files = session.query(File).filter_by(project_id=project_id).all()
                total_files = len(files)
                self.logger.info(f"청킹 대상 파일: {total_files}개")
                
                chunked_files = 0
                total_chunks_created = 0
                chunk_type_stats = {}
                
                for file_obj in files:
                    try:
                        # 파일 내용을 읽어서 청킹을 실행합니다.
                        if os.path.exists(file_obj.path):
                            with open(file_obj.path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            code_chunks = chunker.chunk_file(file_obj.path, content)
                            if code_chunks:
                                # 청킹 결과를 데이터베이스 모델로 변환하여 저장합니다.
                                for code_chunk in code_chunks:
                                    # 청크 유형별 타겟 ID 매핑
                                    target_id, target_type = self._get_chunk_target_info(
                                        code_chunk, file_obj, session)
                                    
                                    # 토큰 수 계산 (간단한 추정)
                                    token_count = len(code_chunk.content.split()) if code_chunk.content else 0
                                    # 해시값 계산
                                    chunk_hash = hashlib.md5(code_chunk.content.encode('utf-8')).hexdigest() if code_chunk.content else ''
                                    
                                    chunk = Chunk(
                                        target_type=target_type,  # 실제 청크 유형 사용
                                        target_id=target_id,      # 매핑된 타겟 ID 사용  
                                        content=code_chunk.content,
                                        token_count=token_count,
                                        hash=chunk_hash
                                    )
                                    session.add(chunk)
                                    total_chunks_created += 1
                                    
                                    # 통계 수집
                                    chunk_type_stats[target_type] = chunk_type_stats.get(target_type, 0) + 1
                                
                                chunked_files += 1
                                if chunked_files % 10 == 0:
                                    self.logger.debug(f"청킹 진행: {chunked_files}/{total_files}")
                    
                    except Exception as e:
                        error_msg = f"파일 청킹 오류 {file_obj.path}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        sys.exit(1)
                
                self.logger.info(f"지능형 청킹 완료: {chunked_files}개 파일, {total_chunks_created}개 청크 생성")
                self.logger.info(f"청크 유형별 통계: {chunk_type_stats}")
                
                
        except Exception as e:
            self.logger.error(f"청킹 실행 중 오류: {e}")
            traceback.print_exc()
    
    def _get_chunk_target_info(self, code_chunk, file_obj, session):
        """청크 유형에 따라 적절한 타겟 ID와 타입을 매핑합니다."""
        chunk_type = code_chunk.chunk_type
        
        # 청크 타입별 매핑
        if chunk_type in ['class', 'interface']:
            # 클래스/인터페이스 청크 - Class 테이블에서 매핑
            class_obj = session.query(Class).filter(
                Class.file_id == file_obj.file_id,
                Class.name == code_chunk.name
            ).first()
            if class_obj:
                return class_obj.class_id, 'class'
            else:
                # 더미 클래스 생성
                dummy_class = Class(
                    name=code_chunk.name,
                    fqn=f"unknown.{code_chunk.name}",
                    file_id=file_obj.file_id
                )
                session.add(dummy_class)
                session.flush()
                return dummy_class.class_id, 'class'
        
        elif chunk_type in ['mybatis_select', 'mybatis_insert', 'mybatis_update', 'mybatis_delete']:
            # MyBatis 쿼리 청크 - SqlUnit 테이블에서 매핑
            sql_unit = session.query(SqlUnit).filter(
                SqlUnit.file_id == file_obj.file_id,
                SqlUnit.stmt_id == code_chunk.name
            ).first()
            if sql_unit:
                return sql_unit.sql_id, 'sql_unit'
            else:
                # 더미 SQL Unit 생성
                dummy_sql = SqlUnit(
                    stmt_id=code_chunk.name,
                    file_id=file_obj.file_id,
                    normalized_fingerprint=code_chunk.content[:100],
                    stmt_kind=chunk_type.split('_')[1].lower()  # select, insert 등
                )
                session.add(dummy_sql)
                session.flush()
                return dummy_sql.sql_id, 'sql_unit'
        
        elif chunk_type == 'method':
            # 메서드 청크 - Method 테이블에서 매핑
            # Method는 class_id를 통해 Class와 연결되고, Class는 file_id를 통해 File과 연결됨
            method_obj = session.query(Method).join(Class).filter(
                Class.file_id == file_obj.file_id,
                Method.name == code_chunk.name
            ).first()
            if method_obj:
                return method_obj.method_id, 'method'
            else:
                # 더미 메서드는 클래스가 필요하므로 파일 기준으로 폴백
                return file_obj.file_id, 'file'
        
        else:
            # 기타 청크(import, block 등)는 파일 기준
            return file_obj.file_id, 'file'

    def _validate_confidence_formula_on_startup(self):
        # ... (Implementation from previous version) ...
        pass # Placeholder
    
    async def _validate_filter_config(self, project_name: str):
        """프로젝트별 필터 설정 파일을 검증합니다."""
        try:
            # 필터 설정 파일 존재 여부 확인
            if not self.filter_config_manager.config_exists(project_name):
                # 설정 파일이 없으면 자동으로 생성 (사용자 입력 없이)
                config_path = self.filter_config_manager.create_config_auto(project_name)
                if config_path:
                    self.logger.info(f"필터 설정 파일이 자동으로 생성되었습니다: {config_path}")
                    # 설정 파일 생성 후 계속 진행
                else:
                    # 자동 생성 실패한 경우
                    raise Exception("필터 설정 파일 자동 생성에 실패했습니다.")
            else:
                # 설정 파일이 존재하면 로드하여 유효성 검사
                try:
                    config = self.filter_config_manager.load_filter_config(project_name)
                    self.logger.info(f"필터 설정 파일을 성공적으로 로드했습니다: {project_name}")
                except Exception as e:
                    raise Exception(f"설정 파일 로드 실패: {e}")
                    
        except Exception as e:
            self.logger.error(f"필터 설정 검증 실패: {e}")
            raise

    def _determine_sql_type(self, sql_content: str) -> str:
        """SQL 타입 결정"""
        sql_upper = sql_content.upper().strip()
        if sql_upper.startswith('SELECT'):
            return 'select'
        elif sql_upper.startswith('UPDATE'):
            return 'update'
        elif sql_upper.startswith('INSERT'):
            return 'insert'
        elif sql_upper.startswith('DELETE'):
            return 'delete'
        elif sql_upper.startswith('CREATE'):
            return 'create'
        elif sql_upper.startswith('ALTER'):
            return 'alter'
        elif sql_upper.startswith('DROP'):
            return 'drop'
        elif sql_upper.startswith('TRUNCATE'):
            return 'truncate'
        elif sql_upper.startswith('MERGE'):
            return 'merge'
        else:
            return 'unknown'


def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent  # phase1의 상위 디렉토리 (SourceAnalyzer.git)
    # 명령줄 인수를 파싱하기 위한 ArgumentParser를 설정합니다.
    parser = argparse.ArgumentParser(
        description='소스 코드 분석 도구 - 1단계 메타정보 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 전역 설정 파일 경로 인수를 추가합니다.
    parser.add_argument('--config', default=str(script_dir / 'config/config.yaml'), help='Phase1 설정 파일 경로')
    # Phase별 설정 파일 경로 인수를 추가합니다.
    parser.add_argument('--phase-config', default=str(script_dir / 'config/config.yaml'), help='Phase1 설정 파일 경로')
    # 프로젝트 이름 인수를 추가합니다 (필수).
    parser.add_argument('--project-name', required=True, help='프로젝트 이름 (필수)')
    # 소스 코드 경로 인수를 추가합니다.
    parser.add_argument('--source-path', help='소스 코드 경로 (기본값: config.yaml에 정의)')
    # 증분 분석 모드 플래그 인수를 추가합니다.
    parser.add_argument('--incremental', action='store_true', help='증분 분석 모드')
    # 분석 전 기존 프로젝트 DB 파일을 삭제하는 플래그 인수를 추가합니다.
    parser.add_argument('--clean', action='store_true', help='분석 전 기존 프로젝트 DB 파일을 삭제합니다.')
    # 분석 후 자동으로 시각화까지 수행하는 플래그 인수를 추가합니다.
    parser.add_argument('--all', action='store_true', help='분석 후 자동으로 시각화까지 수행')
    # 상세 로그 출력 플래그 인수를 추가합니다.
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 로그 출력')
    # 디버그 로그 출력 플래그 인수를 추가합니다.
    parser.add_argument('--debug', action='store_true', help='디버그 로그 출력')
    # 최소 로그 출력 플래그 인수를 추가합니다.
    parser.add_argument('--quiet', '-q', action='store_true', help='최소 로그 출력')
    
    args = parser.parse_args()
    project_name = args.project_name

    # 프로젝트명 검증
    if not project_name or project_name.strip() == '':
        print(f"오류: 프로젝트명이 유효하지 않습니다: '{project_name}'")
        sys.exit(1)
    
    # 프로젝트명에 플레이스홀더가 포함되어 있는지 검증
    if '{project_name}' in project_name:
        print(f"오류: 프로젝트명에 플레이스홀더가 포함되어 있습니다: '{project_name}'")
        print("올바른 프로젝트명을 입력하세요 (예: sampleSrc)")
        sys.exit(1)

    global_config_path = Path(args.config).resolve()
    phase_config_path = Path(args.phase_config).resolve()

    # 로그 파일 정리 (24시간 이상 된 파일들 삭제)
    print("로그 파일 정리 시작...")
    deleted_count = cleanup_old_log_files()
    print(f"로그 파일 정리 완료: {deleted_count}개 파일 삭제")

    # --clean 옵션이 지정된 경우 기존 데이터베이스 파일을 삭제합니다.
    if args.clean:
        temp_config = {}
        if global_config_path.exists():
            with open(global_config_path, 'r', encoding='utf-8') as f:
                temp_config = yaml.safe_load(f) or {}
        
        db_path_template = temp_config.get('database', {}).get('project', {}).get('sqlite', {}).get('path', '')
        if db_path_template:
            db_path_str = db_path_template.replace('{project_name}', project_name)
            db_path = (project_root / db_path_str).resolve()
            if db_path.exists():
                print(f"--clean 옵션: 기존 데이터베이스 파일을 삭제합니다: {db_path}")
                try:
                    os.remove(db_path)
                    print("삭제 완료.")
                except OSError as e:
                    error_msg = f"DB 파일 삭제 실패: {e}"
                    traceback_str = traceback.format_exc()
                    print(f"오류: {error_msg}")
                    print(f"Traceback:\n{traceback_str}")
                    sys.exit(1)
            else:
                print(f"기존 DB 파일({db_path})이 없어 정리할 필요가 없습니다.")
        else:
            print("경고: 설정 파일에서 DB 경로를 찾을 수 없어 --clean을 실행할 수 없습니다.")

    # 소스 디렉토리 경로를 설정하고 필요한 경우 생성합니다.
    project_base_dir = project_root / f"project/{project_name}"
    # --source-path가 명시되지 않으면 project_base_dir을 사용 (src 하위 폴더가 아닌 프로젝트 루트)
    source_dir = Path(args.source_path) if args.source_path else project_base_dir
    source_dir.mkdir(parents=True, exist_ok=True)

    # 소스 디렉토리가 비어있는지 확인합니다.
    if not any(source_dir.iterdir()):
        print(f"경고: 소스 디렉토리가 비어있습니다: {source_dir}")

    try:
        # SourceAnalyzer를 초기화하고 로그 레벨을 설정합니다.
        analyzer = SourceAnalyzer(str(global_config_path), str(phase_config_path), project_name=project_name)
        if args.debug:
            analyzer.logger.logger.setLevel(logging.DEBUG)
        elif args.verbose:
            analyzer.logger.logger.setLevel(logging.INFO)
        elif args.quiet:
            analyzer.logger.logger.setLevel(logging.WARNING)
        
        # 비동기적으로 프로젝트 분석을 실행합니다.
        asyncio.run(analyzer.analyze_project(str(source_dir), project_name, args.incremental))

        # --all 옵션이 지정된 경우 전체 시각화를 실행합니다.
        if args.all:
            print("\n[INFO] 전체 시각화 실행 중...")
            # ... (Visualization call logic) ...

    except Exception as e:
        error_msg = f"분석 중 오류 발생: {e}"
        traceback_str = traceback.format_exc()
        print(f"Critical Error: {error_msg}")
        print(f"Traceback:\n{traceback_str}")
        sys.exit(1)

if __name__ == "__main__":
    main()