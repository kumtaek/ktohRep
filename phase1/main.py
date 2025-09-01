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
from datetime import datetime
import traceback

# 프로젝트 루트를 Python 패스에 추가하여 모듈 임포트를 가능하게 합니다.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from phase1.models.database import DatabaseManager, File
from phase1.parsers.java_parser import JavaParser
from phase1.parsers.jsp_mybatis_parser import JspMybatisParser
from phase1.parsers.sql_parser import SqlParser
from phase1.database.metadata_engine import MetadataEngine
from phase1.utils.csv_loader import CsvLoader
from phase1.utils.logger import setup_logging
from phase1.utils.confidence_calculator import ConfidenceCalculator
from phase1.utils.confidence_validator import ConfidenceValidator, ConfidenceCalibrator, GroundTruthEntry


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
            db_config = self.config.get('database', {}).get('project', {})
            self.db_manager = DatabaseManager(db_config)
            self.db_manager.initialize()
            self.logger.info("데이터베이스 연결 성공")
            # 파서를 초기화합니다.
            self.parsers = self._initialize_parsers()
            self.logger.info(f"파서 초기화 완료: {list(self.parsers.keys())}")
            # 메타데이터 엔진, CSV 로더, 신뢰도 계산기 및 유효성 검사기를 초기화합니다.
            self.metadata_engine = MetadataEngine(self.config, self.db_manager)
            self.csv_loader = CsvLoader(self.config)
            self.confidence_calculator = ConfidenceCalculator(self.config)
            self.confidence_validator = ConfidenceValidator(self.config, self.confidence_calculator)
            self.confidence_calibrator = ConfidenceCalibrator(self.confidence_validator)
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
        return json.loads(config_str)

    def _initialize_parsers(self) -> Dict[str, Any]:
        # 설정에 따라 파서들을 초기화합니다.
        parsers = {}
        if self.config.get('parsers', {}).get('java', {}).get('enabled', True):
            parsers['java'] = JavaParser(self.config)
        if self.config.get('parsers', {}).get('jsp', {}).get('enabled', True):
            parsers['jsp_mybatis'] = JspMybatisParser(self.config)
        if self.config.get('parsers', {}).get('sql', {}).get('enabled', True):
            parsers['sql'] = SqlParser(self.config)
        if self.config.get('parsers', {}).get('jar', {}).get('enabled', True):
            from phase1.parsers.jar_parser import JarParser
            parsers['jar'] = JarParser(self.config)
        # 사용 가능한 파서가 없으면 오류를 발생시킵니다.
        if not parsers:
            raise ValueError("사용 가능한 파서가 없습니다. 설정을 확인하세요.")
        return parsers

    async def analyze_project(self, project_root: str, project_name: str = None, incremental: bool = False):
        # 프로젝트 이름이 제공되지 않으면 루트 경로에서 이름을 추출합니다.
        if not project_name:
            project_name = os.path.basename(project_root.rstrip('/\\'))
        self.logger.info(f"프로젝트 분석 시작: {project_name}")
        # 프로젝트를 생성하고 ID를 가져옵니다.
        project_id = await self.metadata_engine.create_project(project_root, project_name)
        # DB 스키마 정보를 로드합니다.
        await self._load_db_schema(project_root, project_name, project_id)
        # 소스 파일 및 JAR 파일을 수집합니다.
        source_files = self._collect_source_files(project_root)
        jar_files = self._collect_dependency_jars(Path(project_root).parent)
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
        self.logger.info(f"프로젝트 분석 완료: {project_name}")

    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        self.logger.info(f"DB 스키마 정보 로드 시작: {project_name}")
        # CSV 로더를 사용하여 프로젝트 DB 스키마를 로드합니다.
        await self.csv_loader.load_project_db_schema(project_name, project_id)

    def _collect_source_files(self, project_root: str) -> List[str]:
        """소스 파일 수집"""
        source_files = []
        
        # 설정에서 포함/제외 패턴을 가져옵니다.
        include_patterns = self.config.get('file_patterns', {}).get('include', [
            "**/*.java", "**/*.jsp", "**/*.xml", "**/*.properties"
        ])
        exclude_patterns = self.config.get('file_patterns', {}).get('exclude', [
            "**/target/**", "**/build/**", "**/test/**", "**/.git/**"
        ])
        
        self.logger.debug(f"파일 수집 중: {project_root}")
        self.logger.debug(f"포함 패턴: {include_patterns}")
        self.logger.debug(f"제외 패턴: {exclude_patterns}")
        
        # 프로젝트 루트에서 파일을 검색합니다.
        root_path = Path(project_root)
        
        for include_pattern in include_patterns:
            # rglob를 사용하여 재귀적으로 파일을 찾습니다.
            for file_path in root_path.rglob(include_pattern.replace("**/", "")):
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
        self.logger.info(f"발견된 소스 파일: {len(source_files)}개")
        
        return source_files

    async def _filter_changed_files(self, source_files: List[str], project_id: int) -> List[str]:
        # ... (Implementation from previous version) ...
        return source_files # Placeholder

    def _collect_dependency_jars(self, project_base: Path) -> List[str]:
        """프로젝트의 의존 JAR 파일을 수집"""
        jar_files: List[str] = []
        # 설정에서 제외 패턴을 가져옵니다.
        exclude_patterns = self.config.get('file_patterns', {}).get('exclude', ["**/target/**", "**/build/**"])
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
                session = self.db_manager.get_session()
                try:
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
                    session.commit()
                    self.logger.debug(f"저장 완료: JAR {jar_path} - 클래스 {len(classes)}개, 메소드 {len(methods)}개")
                except Exception as e:
                    session.rollback()
                    error_msg = f"JAR 저장 오류 {jar_path}: {e}"
                    traceback_str = traceback.format_exc()
                    self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                finally:
                    session.close()
            except Exception as e:
                error_msg = f"JAR 분석 실패 {jar_path}: {e}"
                traceback_str = traceback.format_exc()
                self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")

    async def _analyze_files(self, source_files: List[str], project_id: int):
        """파일 분석 실행"""
        for file_path in source_files:
            try:
                self.logger.debug(f"파일 분석 시작: {file_path}")
                
                # 파일 확장자에 따라 적절한 파서를 선택합니다.
                file_ext = Path(file_path).suffix.lower()
                parser = None
                
                if file_ext == '.java':
                    parser = self.parsers.get('java')
                elif file_ext == '.jsp':
                    parser = self.parsers.get('jsp_mybatis')
                elif file_ext in ['.xml', '.sql']:
                    # Mybatis XML 파일 또는 일반 SQL 파일에 따라 파서를 선택합니다.
                    if 'mybatis' in file_path.lower() or file_ext == '.xml':
                        parser = self.parsers.get('jsp_mybatis')
                    else:
                        parser = self.parsers.get('sql')
                elif file_ext == '.properties':
                    continue  # Properties 파일은 현재 분석하지 않습니다.
                
                if parser:
                    parse_result = parser.parse_file(file_path, project_id)
                    if parse_result and len(parse_result) == 4:
                        file_obj, classes, methods, edges = parse_result
                        # 파서 결과를 데이터베이스에 저장합니다 (올바른 순서로).
                        session = self.db_manager.get_session()
                        try:
                            # 1. 파일 객체를 저장하고 ID를 확보합니다.
                            if file_obj:
                                session.add(file_obj)
                                session.flush()  # ID를 즉시 확보하기 위해 flush
                                file_id = file_obj.file_id
                            else:
                                file_id = None
                            
                            # 2. 클래스 객체의 file_id를 설정한 후 저장합니다.
                            class_id_map = {}  # class fqn -> class_id 매핑
                            for cls in classes:
                                if file_id:
                                    cls.file_id = file_id
                                session.add(cls)
                                session.flush()
                                class_id_map[cls.fqn] = cls.class_id
                            
                            # 3. 메소드 객체의 file_id, class_id를 설정한 후 저장합니다.
                            for method in methods:
                                if file_id:
                                    method.file_id = file_id
                                # Method가 Class에 속한 경우 class_id를 설정합니다 (owner_fqn 기준으로 찾기).
                                if hasattr(method, 'owner_fqn') and method.owner_fqn in class_id_map:
                                    method.class_id = class_id_map[method.owner_fqn]
                                session.add(method)
                                session.flush()

                            # 모든 메서드가 저장된 후, 엣지의 src_id를 해결합니다.
                            method_id_map = {f"{getattr(m, 'owner_fqn', '')}.{m.name}": m.method_id for m in methods}

                            # 4. 엣지 객체의 project_id, src_id, dst_id를 설정한 후 저장합니다.
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

                            session.commit()
                            self.logger.debug(
                                f"저장 완료: {file_path} - 클래스 {len(classes)}개, 메소드 {len(methods)}개, 엣지 {saved_edges}개"
                            )
                        except Exception as e:
                            session.rollback()
                            error_msg = f"데이터베이스 저장 오류 {file_path}: {e}"
                            traceback_str = traceback.format_exc()
                            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        finally:
                            session.close()
                else:
                    self.logger.debug(f"지원하지 않는 파일 형식: {file_path}")
                    
            except Exception as e:
                error_msg = f"파일 분석 오류 {file_path}: {e}"
                traceback_str = traceback.format_exc()
                self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")

    def _validate_confidence_formula_on_startup(self):
        # ... (Implementation from previous version) ...
        pass # Placeholder

def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    # 명령줄 인수를 파싱하기 위한 ArgumentParser를 설정합니다.
    parser = argparse.ArgumentParser(
        description='소스 코드 분석 도구 - 1단계 메타정보 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 전역 설정 파일 경로 인수를 추가합니다.
    parser.add_argument('--config', default=str(script_dir / '../config/config.yaml'), help='전역 설정 파일 경로')
    # Phase별 설정 파일 경로 인수를 추가합니다.
    parser.add_argument('--phase-config', default=str(script_dir / '../config/phase1/config.yaml'), help='Phase별 설정 파일 경로')
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
    # 최소 로그 출력 플래그 인수를 추가합니다.
    parser.add_argument('--quiet', '-q', action='store_true', help='최소 로그 출력')
    
    args = parser.parse_args()
    project_name = args.project_name

    global_config_path = Path(args.config).resolve()
    phase_config_path = Path(args.phase_config).resolve()

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
    source_dir = Path(args.source_path) if args.source_path else project_base_dir / "src"
    source_dir.mkdir(parents=True, exist_ok=True)

    # 소스 디렉토리가 비어있는지 확인합니다.
    if not any(source_dir.iterdir()):
        print(f"경고: 소스 디렉토리가 비어있습니다: {source_dir}")

    try:
        # SourceAnalyzer를 초기화하고 로그 레벨을 설정합니다.
        analyzer = SourceAnalyzer(str(global_config_path), str(phase_config_path), project_name=project_name)
        if args.verbose:
            analyzer.logger.logger.setLevel(logging.DEBUG)
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