"""
소스 분석기 메인 모듈
리뷰 의견을 반영한 개선사항들이 적용된 1단계 메타정보 생성 시스템
"""

import os
import sys
import argparse
import yaml
import asyncio
import hashlib
import fnmatch
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime

# 프로젝트 루트를 Python 패스에 추가 (수정됨: phase1이 루트가 됨)
project_root = Path(__file__).parent.parent  # phase1의 부모 디렉토리 (프로젝트 루트)
sys.path.insert(0, str(project_root))

from models.database import DatabaseManager, File
from parsers.java_parser import JavaParser
from parsers.jsp_mybatis_parser import JspMybatisParser
from parsers.sql_parser import SqlParser
from database.metadata_engine import MetadataEngine
from utils.csv_loader import CsvLoader
from utils.logger import setup_logging, LoggerFactory, PerformanceLogger
from utils.confidence_calculator import ConfidenceCalculator
from utils.confidence_validator import ConfidenceValidator, ConfidenceCalibrator, GroundTruthEntry


class SourceAnalyzer:
    """소스 분석기 메인 클래스"""
    
    def __init__(self, global_config_path: str, phase_config_path: str, project_name: str = None):
        """
        소스 분석기 초기화
        
        Args:
            global_config_path: 전역 설정 파일 경로
            phase_config_path: Phase별 설정 파일 경로
            project_name: 프로젝트 이름
        """
        self.project_name = project_name
        self.config = self._load_merged_config(global_config_path, phase_config_path)
        
        # 로깅 시스템 초기화
        self.logger = setup_logging(self.config)
        
        self.logger.info("=" * 60)
        self.logger.info("개선된 소스 분석기 시작")
        self.logger.info("=" * 60)
        
        try:
            # 데이터베이스 매니저 초기화
            self.db_manager = DatabaseManager(self.config)
            self.db_manager.initialize()
            self.logger.info("데이터베이스 연결 성공")
            
            # 파서들 초기화
            self.parsers = self._initialize_parsers()
            self.logger.info(f"파서 초기화 완료: {list(self.parsers.keys())}")
            
            # 메타데이터 엔진 초기화
            self.metadata_engine = MetadataEngine(self.config, self.db_manager)
            
            # CSV 로더 초기화
            self.csv_loader = CsvLoader(self.config)
            
            # 신뢰도 계산기 초기화
            self.confidence_calculator = ConfidenceCalculator(self.config)
            
            # Confidence Validation 시스템 초기화
            self.confidence_validator = ConfidenceValidator(self.config, self.confidence_calculator)
            self.confidence_calibrator = ConfidenceCalibrator(self.confidence_validator)
            
            # 시작 시 자동으로 confidence formula 검증 실행
            self._validate_confidence_formula_on_startup()
            
        except Exception as e:
            self.logger.critical("시스템 초기화 실패", exception=e)
            raise
            
    def _load_merged_config(self, global_config_path: str, phase_config_path: str) -> Dict[str, Any]:
        """전역 및 Phase별 설정 파일을 로드하고 병합 (Phase별 설정이 우선)"""
        global_config = {}
        phase_config = {}

        try:
            # 전역 설정 로드
            if os.path.exists(global_config_path):
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    global_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: 전역 설정 파일을 찾을 수 없습니다: {global_config_path}")

            # Phase별 설정 로드
            if os.path.exists(phase_config_path):
                with open(phase_config_path, 'r', encoding='utf-8') as f:
                    phase_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: Phase별 설정 파일을 찾을 수 없습니다: {phase_config_path}")

            # 설정 병합 (Phase별 설정이 전역 설정을 덮어씀)
            # 깊은 병합을 위해 재귀 함수 사용
            def deep_merge(base, overlay):
                for key, value in overlay.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        base[key] = deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            
            config = deep_merge(global_config, phase_config)
            # self.logger.debug(f"병합된 설정 (초기): {config}") # logger not ready yet

            # 프로젝트명 템플릿 치환
            if self.project_name:
                config = self._substitute_project_name(config, self.project_name)
                
            # 기본값 설정 (병합된 설정에 대해)
            self._set_default_config(config)
            
            return config
            
        except yaml.YAMLError as e:
            print(f"ERROR: 설정 파일 파싱 실패: {e}")
            raise
        except Exception as e:
            print(f"ERROR: 설정 파일 로드 및 병합 중 예상치 못한 오류: {e}")
            raise
            
    def _set_default_config(self, config: Dict[str, Any]):
        """기본 설정값 설정"""
        
        # 기본 처리 설정
        if 'processing' not in config:
            config['processing'] = {}
        processing = config['processing']
        processing.setdefault('max_workers', 4)
        processing.setdefault('batch_size', 10)
        processing.setdefault('chunk_size', 512)
        processing.setdefault('confidence_threshold', 0.5)
        
        # 기본 로깅 설정
        if 'logging' not in config:
            config['logging'] = {}
        logging_config = config['logging']
        logging_config.setdefault('level', 'INFO')
        logging_config.setdefault('file', './logs/analyzer.log')
        
        # 기본 신뢰도 설정
        if 'confidence' not in config:
            config['confidence'] = {}
        confidence_config = config['confidence']
        confidence_config.setdefault('weights', {
            'ast': 0.4,
            'static': 0.3,
            'db_match': 0.2,
            'heuristic': 0.1
        })
        
        # LLM 보강 기본 설정 (llm 또는 llm_assist 섹션과 호환)
        if 'llm_assist' not in config:
            config['llm_assist'] = {}
        llm_cfg = config['llm_assist']
        # llm 섹션이 있을 경우 일부 값을 기본치로 전파
        legacy_llm = config.get('llm', {})
        if isinstance(legacy_llm, dict):
            # vLLM endpoint -> base_url
            llm_cfg.setdefault('vllm_base_url', legacy_llm.get('vllm_endpoint'))
            # base_model -> vllm_model 기본
            llm_cfg.setdefault('vllm_model', legacy_llm.get('base_model'))
            # temperature/max_tokens 전파
            if 'temperature' in legacy_llm:
                llm_cfg.setdefault('temperature', legacy_llm.get('temperature'))
            if 'max_tokens' in legacy_llm:
                llm_cfg.setdefault('max_tokens', legacy_llm.get('max_tokens'))
        llm_cfg.setdefault('enabled', True)
        llm_cfg.setdefault('provider', 'auto')  # auto|ollama|vllm
        llm_cfg.setdefault('low_conf_threshold', 0.6)
        llm_cfg.setdefault('max_calls_per_run', 50)
        llm_cfg.setdefault('file_max_lines', 1200)
        llm_cfg.setdefault('temperature', 0.0)
        llm_cfg.setdefault('max_tokens', 512)
        llm_cfg.setdefault('strict_json', True)
        llm_cfg.setdefault('cache', True)
        llm_cfg.setdefault('cache_dir', './output/llm_cache')
        llm_cfg.setdefault('log_prompt', False)
        llm_cfg.setdefault('dry_run', False)
        llm_cfg.setdefault('fallback_to_ollama', True)
        
    def _substitute_project_name(self, config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """설정 파일의 프로젝트명 템플릿을 실제 프로젝트명으로 치환"""
        import json
        
        # 설정을 JSON 문자열로 변환 후 프로젝트명 치환
        config_str = json.dumps(config)
        config_str = config_str.replace("{project_name}", project_name)
        
        return json.loads(config_str)
        
    def _initialize_parsers(self) -> Dict[str, Any]:
        """파서들 초기화 (개선된 예외 처리)"""
        parsers = {}
        
        try:
            # Java 파서
            if self.config.get('parsers', {}).get('java', {}).get('enabled', True):
                parsers['java'] = JavaParser(self.config)
                self.logger.info("Java 파서 초기화 완료")
                
            # JSP/MyBatis 파서  
            if self.config.get('parsers', {}).get('jsp', {}).get('enabled', True):
                parsers['jsp_mybatis'] = JspMybatisParser(self.config)
                self.logger.info("JSP/MyBatis 파서 초기화 완료")
                
            # SQL 파서
            if self.config.get('parsers', {}).get('sql', {}).get('enabled', True):
                parsers['sql'] = SqlParser(self.config)
                self.logger.info("SQL 파서 초기화 완료")
                
        except Exception as e:
            self.logger.error("파서 초기화 중 오류", exception=e)
            raise
            
        if not parsers:
            raise ValueError("사용 가능한 파서가 없습니다. 설정을 확인하세요.")
            
        return parsers
        
    async def analyze_project(self, project_root: str, project_name: str = None, incremental: bool = False) -> Dict[str, Any]:
        """
        프로젝트 전체 분석 (개선된 병렬 처리)
        
        Args:
            project_root: 프로젝트 루트 경로
            project_name: 프로젝트 이름 (없으면 폴더명 사용)
            incremental: 증분 분석 모드 (변경된 파일만 분석)
            
        Returns:
            분석 결과 딕셔너리
        """
        
        if not project_name:
            project_name = os.path.basename(project_root.rstrip('/\\'))
            
        start_time = time.time()
        
        with PerformanceLogger(self.logger, f"프로젝트 '{project_name}' 전체 분석"):
            
            try:
                # 1. 프로젝트 등록
                self.logger.info(f"프로젝트 등록 중: {project_name} ({project_root})")
                project_id = await self.metadata_engine.create_project(project_root, project_name)
                
                # 2. DB 스키마 정보 로드
                await self._load_db_schema(project_root, project_name, project_id)
                
                # 3. 소스 파일들 수집
                source_files = self._collect_source_files(project_root)
                self.logger.info(f"발견된 소스 파일: {len(source_files)}개")
                
                # 증분 분석 모드인 경우 변경된 파일만 선별
                if incremental:
                    source_files = await self._filter_changed_files(source_files, project_id)
                    self.logger.info(f"증분 분석 대상 파일: {len(source_files)}개")
                
                if not source_files:
                    self.logger.warning("분석할 소스 파일이 없습니다.")
                    return self._create_empty_result(project_id, project_name, project_root)
                
                # 4. 파일들 분석 (병렬 처리)
                analysis_results = await self._analyze_files(source_files, project_id)
                
                # 5. 의존성 그래프 구축
                self.logger.info("의존성 그래프 구축 중")
                await self.metadata_engine.build_dependency_graph(project_id)
                
                # 6. 분석 결과 요약
                summary = await self._generate_analysis_summary(project_id, analysis_results)
                
                total_time = time.time() - start_time
                self.logger.info(f"프로젝트 분석 완료: {project_name} ({total_time:.2f}초)")
                
                return {
                    'project_id': project_id,
                    'project_name': project_name,
                    'project_root': project_root,
                    'analysis_time': total_time,
                    'files_analyzed': len(source_files),
                    'analysis_results': analysis_results,
                    'summary': summary
                }
                
            except Exception as e:
                self.logger.error(f"프로젝트 분석 실패: {project_name}", exception=e)
                raise
                
    def _create_empty_result(self, project_id: int, project_name: str, project_root: str = '') -> Dict[str, Any]:
        """빈 분석 결과 생성"""
        return {
            'project_id': project_id,
            'project_name': project_name,
            'project_root': project_root,
            'analysis_time': 0,
            'files_analyzed': 0,
            'analysis_results': {
                'total_files': 0,
                'success_count': 0,
                'error_count': 0,
                'java_files': 0,
                'jsp_files': 0,
                'xml_files': 0,
                'total_classes': 0,
                'total_methods': 0,
                'total_sql_units': 0,
                'errors': []
            },
            'summary': {
                'basic_stats': {
                    'files': 0, 'classes': 0, 'methods': 0, 'sql_units': 0,
                    'joins': 0, 'filters': 0
                },
                'language_distribution': {},
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        """DB 스키마 정보 로드 (프로젝트별 자동 검색)"""
        
        self.logger.info(f"DB 스키마 정보 로드 시작: 프로젝트 '{project_name}'")
        
        try:
            # 새로운 프로젝트별 CSV 로더 사용
            load_result = await self.csv_loader.load_project_db_schema(project_name, project_id)
            
            if load_result['errors']:
                for error in load_result['errors']:
                    self.logger.warning(error)
            
            if load_result['loaded_files']:
                self.logger.info(f"DB 스키마 로드 완료: {len(load_result['loaded_files'])}개 파일, {load_result['total_records']}건 레코드")
                for filename, file_result in load_result['loaded_files'].items():
                    record_count = sum(file_result.values())
                    self.logger.info(f"  - {filename}: {record_count}건")
            else:
                self.logger.info(f"DB 스키마 CSV 파일이 없습니다: {load_result['schema_dir']}")
                self.logger.info("  필요시 다음 CSV 파일들을 해당 디렉토리에 업로드하세요:")
                self.logger.info("  - ALL_TABLES.csv, ALL_TAB_COLUMNS.csv, PK_INFO.csv, ALL_VIEWS.csv")
        
        except Exception as e:
            self.logger.error(f"DB 스키마 로드 중 예외 발생: {e}")
            
    def _collect_source_files(self, project_root: str) -> List[str]:
        """소스 파일들 수집 (개선된 필터링)"""
        
        source_files = []
        file_patterns = self.config.get('file_patterns', {})
        include_patterns = file_patterns.get('include', ['**/*.java', '**/*.jsp', '**/*.xml'])
        exclude_patterns = file_patterns.get('exclude', ['**/target/**', '**/build/**', '**/.git/**'])
        
        self.logger.debug(f"파일 수집 중: {project_root}")
        self.logger.debug(f"포함 패턴: {include_patterns}")
        self.logger.debug(f"제외 패턴: {exclude_patterns}")
        
        try:
            for root, dirs, files in os.walk(project_root):
                # Calculate relative path of current directory from project_root
                current_dir_rel_path = os.path.relpath(root, project_root)
                
                # Filter out directories that match exclude patterns
                dirs[:] = [d for d in dirs if not any(
                    fnmatch.fnmatch(os.path.join(current_dir_rel_path, d), pattern)
                    for pattern in exclude_patterns
                )]
                
                for file in files:
                    file_path_abs = os.path.join(root, file)
                    file_path_rel_to_root = os.path.relpath(file_path_abs, project_root) # New relative path
                    
                    # Check include patterns
                    if any(fnmatch.fnmatch(file_path_rel_to_root, pattern) for pattern in include_patterns):
                        # Check exclude patterns
                        if not any(fnmatch.fnmatch(file_path_rel_to_root, pattern) for pattern in exclude_patterns):
                            source_files.append(file_path_abs) # Store absolute path
                            
        except Exception as e:
            self.logger.error(f"파일 수집 중 오류: {project_root}", exception=e)
            
        self.logger.debug(f"수집된 파일 수: {len(source_files)}")
        return source_files
        
    async def _filter_changed_files(self, source_files: List[str], project_id: int) -> List[str]:
        """증분 분석을 위한 변경된 파일 필터링 및 삭제된 파일 처리"""
        changed_files = []
        
        # 기존 파일 해시 정보 조회
        session = self.db_manager.get_session()
        try:
            existing_files = session.query(File).filter(File.project_id == project_id).all()
            existing_hashes = {f.path: f.hash for f in existing_files}
            current_files_set = set(source_files)
            existing_files_set = set(existing_hashes.keys())
            
            # 삭제된 파일 처리 (기존 DB에는 있지만 현재 파일 시스템에는 없는 파일들)
            deleted_files = existing_files_set - current_files_set
            if deleted_files:
                self.logger.info(f"삭제된 파일 감지: {len(deleted_files)}개")
                await self._handle_deleted_files(deleted_files, project_id)
            
            # 변경된 파일 또는 새로운 파일 감지
            for file_path in source_files:
                try:
                    # 파일 크기 확인으로 처리 전략 결정
                    file_size = os.path.getsize(file_path)
                    size_threshold_hash = self.config.get('processing', {}).get('size_threshold_hash', 50 * 1024)  # 50KB
                    size_threshold_mtime = self.config.get('processing', {}).get('size_threshold_mtime', 10 * 1024 * 1024)  # 10MB
                    
                    if file_size < size_threshold_hash:
                        # 작은 파일: 항상 해시 계산
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            current_hash = hashlib.sha256(content).hexdigest()
                        
                        if file_path not in existing_hashes or existing_hashes[file_path] != current_hash:
                            changed_files.append(file_path)
                            self.logger.debug(f"변경된 파일 감지 (소형): {file_path}")
                            
                    elif file_size < size_threshold_mtime:
                        # 중간 크기 파일: mtime 먼저 확인 후 필요시 해시
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        # 기존 파일의 mtime과 비교
                        existing_file = next((f for f in existing_files if f.path == file_path), None)
                        if not existing_file or existing_file.mtime < file_mtime:
                            # mtime이 다르면 해시 확인
                            with open(file_path, 'rb') as f:
                                content = f.read()
                                current_hash = hashlib.sha256(content).hexdigest()
                            
                            if file_path not in existing_hashes or existing_hashes[file_path] != current_hash:
                                changed_files.append(file_path)
                                self.logger.debug(f"변경된 파일 감지 (중형): {file_path}")
                        
                    else:
                        # 대형 파일: mtime만 확인
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        existing_file = next((f for f in existing_files if f.path == file_path), None)
                        
                        if not existing_file or existing_file.mtime < file_mtime:
                            changed_files.append(file_path)
                            self.logger.debug(f"변경된 파일 감지 (대형): {file_path}")
                    
                except Exception as e:
                    # 파일 읽기 실패 시 안전하게 포함
                    self.logger.warning(f"파일 변경 감지 실패 {file_path}: {e}")
                    changed_files.append(file_path)
            
        except Exception as e:
            self.logger.error("증분 분석 파일 필터링 중 오류", exception=e)
            # 오류 시 전체 파일 반환
            return source_files
        finally:
            session.close()
            
        return changed_files
    
    async def _handle_deleted_files(self, deleted_files: set, project_id: int):
        """삭제된 파일들의 메타데이터 정리"""
        
        self.logger.info(f"삭제된 파일 메타데이터 정리 시작: {len(deleted_files)}개 파일")
        
        try:
            # 메타데이터 엔진을 통해 삭제 처리
            cleaned_count = await self.metadata_engine.cleanup_deleted_files(deleted_files, project_id)
            
            # JSP/MyBatis 파서의 캐시도 정리 (있는 경우)
            if 'jsp_mybatis' in self.parsers:
                for file_path in deleted_files:
                    try:
                        self.parsers['jsp_mybatis'].handle_deleted_file(file_path)
                    except Exception as e:
                        self.logger.warning(f"파서 캐시 정리 실패 {file_path}: {e}")
            
            self.logger.info(f"삭제된 파일 메타데이터 정리 완료: {cleaned_count}개 정리됨")
            
        except Exception as e:
            self.logger.error("삭제된 파일 처리 중 오류", exception=e)
            raise
        
    
        
    async def _generate_analysis_summary(self, project_id: int, 
                                       analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 요약 생성 (개선된 통계)"""
        
        try:
            # 기본 메타데이터 엔진 요약
            engine_summary = await self.metadata_engine.generate_project_summary(project_id)
            
            # 추가 통계 정보
            enhanced_summary = {
                **engine_summary,
                'processing_stats': {
                    'success_rate': (analysis_results['success_count'] / 
                                   max(1, analysis_results['total_files'])) * 100,
                    'error_rate': (analysis_results['error_count'] / 
                                 max(1, analysis_results['total_files'])) * 100,
                    'files_per_type': {
                        'java': analysis_results['java_files'],
                        'jsp': analysis_results['jsp_files'],
                        'xml': analysis_results['xml_files']
                    }
                },
                'quality_indicators': {
                    'avg_classes_per_java_file': (
                        analysis_results['total_classes'] / max(1, analysis_results['java_files'])
                    ),
                    'avg_methods_per_class': (
                        analysis_results['total_methods'] / max(1, analysis_results['total_classes'])
                    ),
                    'sql_units_found': analysis_results['total_sql_units']
                }
            }
            
            return enhanced_summary
            
        except Exception as e:
            self.logger.error("분석 요약 생성 중 오류", exception=e)
            return {
                'error': str(e),
                'basic_stats': {'files': 0, 'classes': 0, 'methods': 0, 'sql_units': 0},
                'analysis_timestamp': datetime.now().isoformat()
            }
            
    async def _analyze_files(self, source_files: List[str], project_id: int) -> Dict[str, Any]:
        """소스 파일들 분석"""
        
        analysis_results = {
            'total_files': len(source_files),
            'success_count': 0,
            'error_count': 0,
            'java_files': 0,
            'jsp_files': 0,
            'xml_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_sql_units': 0,
            'errors': []
        }
        
        # 병렬 처리를 위한 세마포어
        max_workers = self.config['processing'].get('max_workers', 4)
        semaphore = asyncio.Semaphore(max_workers)
        
        # 파일별 분석 태스크 생성
        tasks = [
            self._analyze_single_file(file_path, project_id, semaphore) 
            for file_path in source_files
        ]
        
        # 병렬 실행
        file_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        for i, result in enumerate(file_results):
            if isinstance(result, Exception):
                analysis_results['errors'].append({
                    'file': source_files[i],
                    'error': str(result)
                })
                analysis_results['error_count'] += 1
            else:
                analysis_results['success_count'] += 1
                
                # 파일 타입별 카운팅
                file_path = source_files[i]
                if file_path.endswith('.java'):
                    analysis_results['java_files'] += 1
                elif file_path.endswith('.jsp'):
                    analysis_results['jsp_files'] += 1
                elif file_path.endswith('.xml'):
                    analysis_results['xml_files'] += 1
                    
                # 요소별 카운팅
                if result:
                    analysis_results['total_classes'] += result.get('classes', 0)
                    analysis_results['total_methods'] += result.get('methods', 0)
                    analysis_results['total_sql_units'] += result.get('sql_units', 0)
                    
        return analysis_results
        
    async def _analyze_single_file(self, file_path: str, project_id: int, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """단일 파일 분석"""
        
        async with semaphore:
            try:
                self.logger.debug(f"파일 분석 시작: {file_path}")
                
                result = {'classes': 0, 'methods': 0, 'sql_units': 0}
                
                # 파일 타입에 따른 파서 선택
                if 'java' in self.parsers and self.parsers['java'].can_parse(file_path):
                    file_obj, classes, methods, edges = self.parsers['java'].parse_file(file_path, project_id)
                    
                    # 데이터베이스에 저장
                    await self.metadata_engine.save_java_analysis(file_obj, classes, methods, edges)
                    
                    result['classes'] = len(classes)
                    result['methods'] = len(methods)
                    
                elif 'jsp_mybatis' in self.parsers and self.parsers['jsp_mybatis'].can_parse(file_path):
                    file_obj, sql_units, joins, filters, edges, vulnerabilities = self.parsers['jsp_mybatis'].parse_file(file_path, project_id)
                    
                    # 데이터베이스에 저장
                    await self.metadata_engine.save_jsp_mybatis_analysis(file_obj, sql_units, joins, filters, edges, vulnerabilities)
                    
                    result['sql_units'] = len(sql_units)
                    
                return result
                
            except Exception as e:
                self.logger.error(f"파일 분석 오류 {file_path}: {e}")
                raise
    
    def _validate_confidence_formula_on_startup(self):
        """
        시스템 시작 시 confidence formula 검증 수행
        정제식 분석 #22를 해결하기 위한 중요한 기능
        """
        try:
            self.logger.info("Confidence formula 검증 시작...")
            
            # Ground truth 데이터가 없으면 샘플 데이터 생성
            if len(self.confidence_validator.ground_truth_data) == 0:
                self.logger.warning("Ground truth 데이터가 없음 - 샘플 데이터 사용")
                return
            
            # Confidence formula 검증 실행
            validation_result = self.confidence_validator.validate_confidence_formula()
            
            if 'mean_absolute_error' in validation_result:
                mae = validation_result['mean_absolute_error']
                self.logger.info(f"Confidence formula MAE: {mae:.3f}")
                
                # 조정 필요성 확인
                if mae > 0.10:  # 10% 이상 오류
                    self.logger.warning(f"Confidence 오류가 큼: {mae:.1%} - 캘리브레이션 균인")
                    self._attempt_confidence_calibration()
                else:
                    self.logger.info("현재 confidence formula가 적절함")
            
        except Exception as e:
            self.logger.error(f"Confidence 검증 중 오류: {e}")
            # 시스템 시작을 막지는 않도록 함
    
    def _attempt_confidence_calibration(self):
        """
        Confidence formula 캘리브레이션 시도
        """
        try:
            self.logger.info("자동 confidence 캘리브레이션 시도...")
            
            calibration_result = self.confidence_validator.calibrate_weights()
            
            if calibration_result.get('recommendation') == 'apply':
                improvement = calibration_result.get('improvement_percentage', 0)
                self.logger.info(f"캘리브레이션으로 {improvement:.1f}% 개선 예상")
                
                # 자동으로 적용
                if self.confidence_calibrator.apply_calibration(self.confidence_calculator):
                    self.logger.info("캘리브레이션이 적용됨")
                else:
                    self.logger.warning("캘리브레이션 적용 실패")
            else:
                self.logger.info("현재 가중치가 최적 상태")
                
        except Exception as e:
            self.logger.error(f"캘리브레이션 시도 중 오류: {e}")
    
    def generate_confidence_accuracy_report(self, output_path: str = None) -> Dict[str, Any]:
        """
        종합적인 confidence 정확도 보고서 생성
        
        Args:
            output_path: 보고서 저장 경로 (선택사항)
            
        Returns:
            정확도 보고서 데이터
        """
        try:
            self.logger.info("Confidence 정확도 보고서 생성 중...")
            
            # 종합 보고서 생성
            report = self.confidence_validator.generate_confidence_accuracy_report()
            
            # 파일로 저장 (지정된 경우)
            if output_path:
                import json
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Confidence 보고서 저장됨: {output_path}")
            
            # 요약 정보 로깅
            if 'validation_report' in report:
                val_report = report['validation_report']
                if 'mean_absolute_error' in val_report:
                    mae = val_report['mean_absolute_error']
                    self.logger.info(f"Current confidence MAE: {mae:.3f}")
                    
                if 'error_distribution' in val_report:
                    error_dist = val_report['error_distribution']
                    excellent_pct = error_dist['excellent']['percentage'] * 100
                    poor_pct = error_dist['poor']['percentage'] * 100
                    self.logger.info(f"Error distribution: {excellent_pct:.1f}% excellent, {poor_pct:.1f}% poor")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Confidence 보고서 생성 실패: {e}")
            return {'error': str(e)}
    
    def add_ground_truth_entry(self, file_path: str, parser_type: str, 
                               expected_confidence: float, **kwargs) -> bool:
        """
        Ground truth 데이터 엔트리 추가
        
        Args:
            file_path: 파일 경로
            parser_type: 파서 타입
            expected_confidence: 기대 신뢰도 (0.0-1.0)
            **kwargs: 기타 ground truth 데이터
            
        Returns:
            성공 여부
        """
        try:
            entry = GroundTruthEntry(
                file_path=file_path,
                parser_type=parser_type,
                expected_confidence=expected_confidence,
                expected_classes=kwargs.get('expected_classes', 0),
                expected_methods=kwargs.get('expected_methods', 0),
                expected_sql_units=kwargs.get('expected_sql_units', 0),
                verified_tables=kwargs.get('verified_tables', []),
                complexity_factors=kwargs.get('complexity_factors', {}),
                notes=kwargs.get('notes', ''),
                verifier=kwargs.get('verifier', 'manual')
            )
            
            self.confidence_validator.add_ground_truth_entry(entry)
            self.logger.info(f"Ground truth 엔트리 추가됨: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ground truth 엔트리 추가 실패: {e}")
            return False

    def export_metadata_to_md(self, output_dir: str, project_name: str) -> Dict[str, Any]:
        """
        메타데이터를 Markdown 파일로 내보내기
        
        Args:
            output_dir: 출력 디렉토리 경로
            project_name: 프로젝트 이름
            
        Returns:
            내보내기 결과 정보
        """
        try:
            from datetime import datetime
            import os
            
            # 출력 디렉토리 생성
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 데이터베이스에서 메타데이터 조회
            session = self.db_manager.get_session()
            from models.database import Project
            files = session.query(File).join(Project).filter(Project.name == project_name).all()
            
            if not files:
                return {
                    'success': False,
                    'error': f'프로젝트 "{project_name}"의 메타데이터를 찾을 수 없습니다.'
                }
            
            created_files = []
            
            # 1. 프로젝트 요약 보고서 생성
            summary_file = output_path / f"{project_name}_metadata_summary.md"
            self._create_summary_report(summary_file, project_name, files)
            created_files.append(str(summary_file))
            
            # 2. 파일별 상세 보고서 생성
            details_dir = output_path / "file_details"
            details_dir.mkdir(exist_ok=True)
            
            for file_obj in files:
                detail_file = details_dir / f"{self._sanitize_filename(file_obj.path)}.md"
                self._create_file_detail_report(detail_file, file_obj)
                created_files.append(str(detail_file))
            
            # 3. 신뢰도 분석 보고서 생성 (confidence 정보가 있는 경우)
            confidence_file = output_path / f"{project_name}_confidence_analysis.md"
            self._create_confidence_report(confidence_file, project_name, files)
            created_files.append(str(confidence_file))
            
            session.close()
            
            return {
                'success': True,
                'files_created': len(created_files),
                'file_list': created_files
            }
            
        except Exception as e:
            self.logger.error(f"MD 내보내기 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """파일명을 안전하게 변환"""
        import re
        # 특수문자를 언더스코어로 변환
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 연속된 언더스코어를 하나로 변환
        safe_name = re.sub(r'_{2,}', '_', safe_name)
        return safe_name.strip('_')
    
    def _create_summary_report(self, file_path: Path, project_name: str, files: list):
        """프로젝트 요약 보고서 생성"""
        from collections import defaultdict
        
        # 통계 계산
        file_types = defaultdict(int)
        total_confidence = 0
        confidence_count = 0
        
        for file_obj in files:
            ext = Path(file_obj.path).suffix
            file_types[ext] += 1
            
            # Note: File model doesn't have confidence field, skip confidence calculation
            # if file_obj.confidence and file_obj.confidence > 0:
            #     total_confidence += file_obj.confidence
            #     confidence_count += 1
        
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        content = f"""# {project_name} 메타데이터 분석 보고서

## 생성 정보
- **생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **프로젝트명**: {project_name}
- **분석 파일 수**: {len(files)}개

## 파일 타입별 분석
"""
        
        for ext, count in sorted(file_types.items()):
            content += f"- **{ext or '확장자 없음'}**: {count}개\n"
        
        content += f"""
## 신뢰도 분석
- **평균 신뢰도**: {avg_confidence:.2%} ({confidence_count}개 파일)
- **신뢰도 데이터 없음**: {len(files) - confidence_count}개 파일

## 파일 목록
| 파일 경로 | 타입 | 신뢰도 | 최종 업데이트 |
|-----------|------|--------|---------------|
"""
        
        for file_obj in files:
            confidence_str = "N/A"  # No confidence field in File model
            content += f"| {file_obj.path} | {Path(file_obj.path).suffix} | {confidence_str} | {file_obj.mtime or 'N/A'} |\n"
        
        file_path.write_text(content, encoding='utf-8')
    
    def _create_file_detail_report(self, file_path: Path, file_obj):
        """개별 파일 상세 보고서 생성"""
        content = f"""# 파일 분석 상세 보고서

## 파일 정보
- **경로**: {file_obj.path}
- **파일 타입**: {Path(file_obj.path).suffix}
- **언어**: {file_obj.language or 'N/A'}
- **라인수**: {file_obj.loc or 'N/A'}
- **최종 수정일**: {file_obj.mtime or 'N/A'}
- **해시**: {file_obj.hash or 'N/A'}

## 분석 결과
- **신뢰도**: N/A (File model에 신뢰도 필드 없음)
- **파일 ID**: {file_obj.file_id}
- **프로젝트 ID**: {file_obj.project_id}

## 메타데이터
메타데이터는 관련 클래스 및 메서드 정보를 참조하세요.
"""
        
        file_path.write_text(content, encoding='utf-8')
    
    def _create_confidence_report(self, file_path: Path, project_name: str, files: list):
        """신뢰도 분석 보고서 생성"""
        # Note: File model doesn't have confidence field, so skip confidence analysis
        content = f"""# {project_name} 신뢰도 분석 보고서

현재 데이터베이스 모델에서는 파일별 신뢰도 데이터를 저장하지 않습니다.
신뢰도 분석은 실행 시점에서만 계산되며, 향후 버전에서 개선될 예정입니다.

## 파일 목록
| 파일 경로 | 언어 | 라인수 |
|-----------|------|-------|
"""
        
        for file_obj in files:
            content += f"| {file_obj.path} | {file_obj.language or 'N/A'} | {file_obj.loc or 'N/A'} |\n"
        
        file_path.write_text(content, encoding='utf-8')

def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(
        description='소스 코드 분석 도구 - 1단계 메타정보 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시 사용법:
  python main.py --project-name my-project
  python main.py --project-name sample-app --all
  python main.py --project-name my-project --config custom_config.yaml
        """
    )
    
    parser.add_argument('--config', default='../config/config.yaml', 
                       help='전역 설정 파일 경로 (기본값: ../config/config.yaml)')
    parser.add_argument('--phase-config', default='../config/phase1/config.yaml', 
                       help='Phase별 설정 파일 경로 (기본값: ../config/phase1/config.yaml)')
    parser.add_argument('--project-name', required=True,
                       help='프로젝트 이름 (필수)')
    parser.add_argument('--source-path', 
                       help='소스 코드 경로 (기본값: ../project/{project-name}/src)')
    parser.add_argument('--incremental', action='store_true',
                       help='증분 분석 모드 (변경된 파일만 분석)')
    parser.add_argument('--all', action='store_true',
                       help='분석 후 자동으로 시각화까지 수행')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='상세 로그 출력')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='최소 로그 출력')
    parser.add_argument('--include-ext',
                       help='포함할 파일 확장자 (쉼표로 구분, 예: java,jsp,xml)')
    parser.add_argument('--include-paths',
                       help='포함할 경로 패턴 (쉼표로 구분)')
    parser.add_argument('--exclude-paths',
                       help='제외할 경로 패턴 (쉼표로 구분)')
    parser.add_argument('--export-md', nargs='?', const=True,
                       help='메타데이터를 Markdown으로 내보내기 (선택적으로 출력 디렉토리 지정)')
    parser.add_argument('--add-ground-truth', nargs=3, metavar=('FILE_PATH', 'PARSER_TYPE', 'EXPECTED_CONF'),
                       help='Ground truth 데이터 추가')
    parser.add_argument('--validate-confidence', action='store_true',
                       help='Confidence formula 검증 수행')
    parser.add_argument('--calibrate-confidence', action='store_true',
                       help='Confidence formula 자동 캘리브레이션')
    parser.add_argument('--confidence-report',
                       help='Confidence 정확도 보고서 생성 (파일 경로)')
    
    # Parse arguments
    args = parser.parse_args()
    project_name = args.project_name
    
    # No need to check os.path.exists(args.config) here, as _load_merged_config handles it
    
    # 프로젝트 경로 자동 생성 (phase1에서 실행되므로 상위 디렉토리 참조)
    project_base_dir = f"../project/{project_name}"
    
    # 소스 경로 결정 (source-path가 지정되면 해당 경로 사용)
    if args.source_path:
        project_source_dir = args.source_path
    else:
        project_source_dir = f"../project/{project_name}/src"
    
    # 프로젝트 디렉토리 생성 (없으면 생성)
    os.makedirs(project_base_dir, exist_ok=True)
    os.makedirs(project_source_dir, exist_ok=True)
    os.makedirs(f"../project/{project_name}/data", exist_ok=True)
    os.makedirs(f"../project/{project_name}/output", exist_ok=True)
    os.makedirs(f"../project/{project_name}/output/visualize", exist_ok=True)
    os.makedirs(f"../project/{project_name}/logs", exist_ok=True)
    os.makedirs(f"../project/{project_name}/db_schema", exist_ok=True)
    
    # 소스 디렉토리 존재 확인
    if not os.path.exists(project_source_dir) or not os.listdir(project_source_dir):
        print(f"경고: 소스 디렉토리가 비어있습니다: {project_source_dir}")
        print(f"   분석할 소스 코드를 {project_source_dir}에 위치시키세요.")
    
    try:
        # 설정 파일 로드 및 병합
        print(f"소스 분석기 초기화 중... (프로젝트: {project_name})")
        analyzer = SourceAnalyzer(args.config, args.phase_config, project_name=project_name)
        
        # 로그 레벨 조정 (로거가 없으면 기본 로깅 사용)
        if hasattr(analyzer.logger, 'logger'):
            if args.verbose:
                analyzer.logger.logger.setLevel('DEBUG')
            elif args.quiet:
                analyzer.logger.logger.setLevel('WARNING')
        
        # Validation 관련 명령어 처리
        validation_performed = False
        
        # Ground truth 데이터 추가
        if args.add_ground_truth:
            file_path, parser_type, expected_conf = args.add_ground_truth
            try:
                expected_confidence = float(expected_conf)
                if analyzer.add_ground_truth_entry(file_path, parser_type, expected_confidence):
                    print(f"[OK] Ground truth 엔트리 추가됨: {file_path}")
                else:
                    print(f"[ERROR] Ground truth 엔트리 추가 실패: {file_path}")
                validation_performed = True
            except ValueError:
                print(f"[ERROR] 오류: 잘못된 confidence 값: {expected_conf}")
        
        # Confidence 검증
        if args.validate_confidence:
            print("[INFO] Confidence formula 검증 실행 중...")
            validation_result = analyzer.confidence_validator.validate_confidence_formula()
            
            if 'mean_absolute_error' in validation_result:
                mae = validation_result['mean_absolute_error']
                print(f"[RESULT] Confidence MAE: {mae:.3f}")
                
                if 'error_distribution' in validation_result:
                    error_dist = validation_result['error_distribution']
                    excellent_pct = error_dist['excellent']['percentage'] * 100
                    poor_pct = error_dist['poor']['percentage'] * 100
                    print(f"[RESULT] 오류 분포: {excellent_pct:.1f}% 우수, {poor_pct:.1f}% 불량")
            validation_performed = True
        
        # Confidence 캘리브레이션
        if args.calibrate_confidence:
            print("[INFO] Confidence formula 자동 캘리브레이션 실행 중...")
            calibration_result = analyzer.confidence_validator.calibrate_weights()
            
            if calibration_result.get('recommendation') == 'apply':
                improvement = calibration_result.get('improvement_percentage', 0)
                print(f"[INFO] 캘리브레이션으로 {improvement:.1f}% 개선 가능")
                
                if analyzer.confidence_calibrator.apply_calibration(analyzer.confidence_calculator):
                    print("[OK] 캘리브레이션 적용 완료")
                else:
                    print("[ERROR] 캘리브레이션 적용 실패")
            else:
                print("[INFO] 현재 가중치가 이미 최적 상태")
            validation_performed = True
        
        # Confidence 리포트 생성
        if args.confidence_report:
            print(f"[INFO] Confidence 정확도 보고서 생성 중: {args.confidence_report}")
            report = analyzer.generate_confidence_accuracy_report(args.confidence_report)
            
            if 'error' not in report:
                print(f"[OK] 보고서 생성 완료: {args.confidence_report}")
                
                # 요약 정보 출력
                if 'validation_report' in report and 'mean_absolute_error' in report['validation_report']:
                    mae = report['validation_report']['mean_absolute_error']
                    print(f"[RESULT] 현재 오류율: {mae:.1%}")
            else:
                print(f"[ERROR] 보고서 생성 실패: {report['error']}")
            validation_performed = True
        
        # Validation 명령만 실행한 경우 여기서 종료
        if validation_performed:
            print("\n[DONE] Validation 작업 완료")
            return
        
        # 프로젝트 분석 실행
        print(f"프로젝트 분석 시작: {project_source_dir}")
        # 런타임 파일 패턴 오버라이드 적용
        if args.include_ext or args.include_paths or args.exclude_paths:
            fps = analyzer.config.setdefault('file_patterns', {})
            
            # Include patterns
            include_patterns: List[str] = []
            if args.include_ext:
                for ext in [x.strip() for x in args.include_ext.split(',') if x.strip()]:
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    include_patterns.append(f"**/*{ext}")
            if args.include_paths:
                for p in [x.strip() for x in args.include_paths.split(',') if x.strip()]:
                    include_patterns.append(p) # Directly add path as pattern
            if include_patterns:
                fps['include'] = include_patterns

            # Exclude patterns
            exclude_patterns: List[str] = []
            if args.exclude_paths:
                for p in [x.strip() for x in args.exclude_paths.split(',') if x.strip()]:
                    exclude_patterns.append(p) # Directly add path as pattern
            if exclude_patterns:
                fps['exclude'] = exclude_patterns

        result = asyncio.run(analyzer.analyze_project(
            project_source_dir, 
            project_name,
            args.incremental
        ))
        
        # 결과 출력
        print_analysis_results(result)
        
        # --all 플래그 처리: 시각화 자동 실행
        if args.all:
            print(f"\n[INFO] 전체 시각화 실행 중...")
            try:
                import subprocess
                visualize_output_dir = f"../project/{project_name}/output/visualize"
                
                # visualize/cli.py 실행
                viz_cmd = [
                    'python', 'visualize/cli.py', 
                    '--project-name', project_name,
                    '--output-dir', visualize_output_dir,
                    '--all'  # 모든 시각화 생성
                ]
                
                result = subprocess.run(viz_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[OK] 시각화 완료: {visualize_output_dir}")
                else:
                    print(f"[WARNING] 시각화 중 경고 또는 오류 발생")
                    if result.stderr:
                        print(f"   오류: {result.stderr.strip()}")
                        
            except Exception as e:
                print(f"[ERROR] 시각화 실행 중 오류: {e}")
        
        # 메타데이터 MD 내보내기 처리
        if args.export_md is not None: # Check if --export-md was provided at all
            output_dir_for_md = args.export_md
            if output_dir_for_md is True: # If --export-md was provided without a value
                output_dir_for_md = f"../project/{project_name}/output/reports" # Default path
            
            print(f"\n[INFO] 메타데이터를 Markdown으로 내보내는 중: {output_dir_for_md}")
            try:
                export_result = analyzer.export_metadata_to_md(output_dir_for_md, project_name)
                if export_result.get('success'):
                    print(f"[OK] Markdown 내보내기 완료: {export_result['files_created']}개 파일 생성")
                    for file_path in export_result.get('file_list', []):
                        print(f"   - {file_path}")
                else:
                    print(f"[ERROR] Markdown 내보내기 실패: {export_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"[ERROR] Markdown 내보내기 중 오류: {e}")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"분석 중 오류가 발생했습니다: {e}")
        sys.exit(1)


def print_analysis_results(result: Dict[str, Any]):
    """분석 결과를 보기 좋게 출력"""
    
    print("\n" + "=" * 70)
    print("분석 완료!")
    print("=" * 70)
    
    # 기본 정보
    print(f"프로젝트: {result['project_name']}")
    print(f"경로: {result['project_root']}")
    print(f"분석 시간: {result['analysis_time']:.2f}초")
    print()
    
    # 파일 처리 현황
    results = result['analysis_results']
    print("파일 처리 현황:")
    print(f"  - 전체 파일: {result['files_analyzed']}개")
    print(f"  - 성공: {results['success_count']}개")
    print(f"  - 실패: {results['error_count']}개")
    if results['error_count'] > 0:
        print(f"  - 성공률: {(results['success_count']/results['total_files']*100):.1f}%")
    print()
    
    # 파일 타입별 분석
    print("파일 타입별 분석:")
    print(f"  - Java 파일: {results['java_files']}개")
    print(f"  - JSP 파일: {results['jsp_files']}개")
    print(f"  - XML 파일: {results['xml_files']}개")
    print()
    
    # 분석 결과
    print("분석 결과:")
    print(f"  - 클래스 수: {results['total_classes']}개")
    print(f"  - 메서드 수: {results['total_methods']}개")
    print(f"  - SQL 구문 수: {results['total_sql_units']}개")
    print()
    
    # 품질 지표
    if 'quality_indicators' in result['summary']:
        quality = result['summary']['quality_indicators']
        print("품질 지표:")
        print(f"  - Java 파일당 평균 클래스 수: {quality['avg_classes_per_java_file']:.1f}개")
        print(f"  - 클래스당 평균 메서드 수: {quality['avg_methods_per_class']:.1f}개")
        print(f"  - 발견된 SQL 구문: {quality['sql_units_found']}개")
        print()
    
    # 오류 정보 (있는 경우)
    if results['errors']:
        print("오류 상세:")
        for i, error in enumerate(results['errors'][:5]):  # 최대 5개만 표시
            if isinstance(error, dict) and 'file' in error:
                print(f"  {i+1}. {error['file']}: {error['error']}")
            else:
                print(f"  {i+1}. {error}")
        
        if len(results['errors']) > 5:
            print(f"  ... 및 {len(results['errors'])-5}개 추가 오류")
        print()
    
    # 성능 요약
    if result['files_analyzed'] > 0 and result['analysis_time'] > 0:
        files_per_sec = result['files_analyzed'] / result['analysis_time']
        print(f"성능: {files_per_sec:.1f}파일/초")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
