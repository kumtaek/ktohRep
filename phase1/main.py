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
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime

# 프로젝트 루트를 Python 패스에 추가
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
        self.config = self._load_merged_config(global_config_path, phase_config_path)
        self.logger = setup_logging(self.config)
        self.logger.info("=" * 60)
        self.logger.info("개선된 소스 분석기 시작")
        self.logger.info("=" * 60)
        
        try:
            db_config = self.config.get('database', {}).get('project', {})
            self.db_manager = DatabaseManager(db_config)
            self.db_manager.initialize()
            self.logger.info("데이터베이스 연결 성공")
            self.parsers = self._initialize_parsers()
            self.logger.info(f"파서 초기화 완료: {list(self.parsers.keys())}")
            self.metadata_engine = MetadataEngine(self.config, self.db_manager)
            self.csv_loader = CsvLoader(self.config)
            self.confidence_calculator = ConfidenceCalculator(self.config)
            self.confidence_validator = ConfidenceValidator(self.config, self.confidence_calculator)
            self.confidence_calibrator = ConfidenceCalibrator(self.confidence_validator)
            self._validate_confidence_formula_on_startup()
        except Exception as e:
            self.logger.critical(f"시스템 초기화 실패: {e}", exc_info=True)
            raise

    def _load_merged_config(self, global_config_path: str, phase_config_path: str) -> Dict[str, Any]:
        """전역 및 Phase별 설정 파일을 로드하고 병합 (Phase별 설정이 우선)"""
        global_config = {}
        phase_config = {}
        try:
            if os.path.exists(global_config_path):
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    global_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: 전역 설정 파일을 찾을 수 없습니다: {global_config_path}")
            if os.path.exists(phase_config_path):
                with open(phase_config_path, 'r', encoding='utf-8') as f:
                    phase_config = yaml.safe_load(os.path.expandvars(f.read())) or {}
            else:
                print(f"WARNING: Phase별 설정 파일을 찾을 수 없습니다: {phase_config_path}")
            def deep_merge(base, overlay):
                for key, value in overlay.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        base[key] = deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            config = deep_merge(global_config, phase_config)
            if self.project_name:
                config = self._substitute_project_name(config, self.project_name)
            self._set_default_config(config)
            return config
        except Exception as e:
            print(f"ERROR: 설정 파일 로드 및 병합 중 오류: {e}")
            raise

    def _set_default_config(self, config: Dict[str, Any]):
        config.setdefault('processing', {}).setdefault('max_workers', 4)
        config.setdefault('logging', {}).setdefault('level', 'INFO')

    def _substitute_project_name(self, config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        config_str = json.dumps(config)
        config_str = config_str.replace("{project_name}", project_name)
        return json.loads(config_str)

    def _initialize_parsers(self) -> Dict[str, Any]:
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
        if not parsers:
            raise ValueError("사용 가능한 파서가 없습니다. 설정을 확인하세요.")
        return parsers

    async def analyze_project(self, project_root: str, project_name: str = None, incremental: bool = False):
        if not project_name:
            project_name = os.path.basename(project_root.rstrip('/\\'))
        self.logger.info(f"프로젝트 분석 시작: {project_name}")
        project_id = await self.metadata_engine.create_project(project_root, project_name)
        await self._load_db_schema(project_root, project_name, project_id)
        source_files = self._collect_source_files(project_root)
        jar_files = self._collect_dependency_jars(Path(project_root).parent)
        if incremental:
            source_files = await self._filter_changed_files(source_files, project_id)
        if not source_files:
            self.logger.warning("분석할 소스 파일이 없습니다.")
            return
        await self._analyze_files(source_files, project_id)
        if jar_files:
            await self._analyze_jars(jar_files, project_id)
        await self.metadata_engine.build_dependency_graph(project_id)
        self.logger.info(f"프로젝트 분석 완료: {project_name}")

    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        self.logger.info(f"DB 스키마 정보 로드 시작: {project_name}")
        await self.csv_loader.load_project_db_schema(project_name, project_id)

    def _collect_source_files(self, project_root: str) -> List[str]:
        """소스 파일 수집"""
        source_files = []
        
        # 설정에서 포함/제외 패턴 가져오기
        include_patterns = self.config.get('file_patterns', {}).get('include', [
            "**/*.java", "**/*.jsp", "**/*.xml", "**/*.properties"
        ])
        exclude_patterns = self.config.get('file_patterns', {}).get('exclude', [
            "**/target/**", "**/build/**", "**/test/**", "**/.git/**"
        ])
        
        self.logger.debug(f"파일 수집 중: {project_root}")
        self.logger.debug(f"포함 패턴: {include_patterns}")
        self.logger.debug(f"제외 패턴: {exclude_patterns}")
        
        # 프로젝트 루트에서 파일 검색
        root_path = Path(project_root)
        
        for include_pattern in include_patterns:
            for file_path in root_path.rglob(include_pattern.replace("**/", "")):
                if file_path.is_file():
                    str_path = str(file_path)
                    
                    # 제외 패턴 확인
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
        exclude_patterns = self.config.get('file_patterns', {}).get('exclude', ["**/target/**", "**/build/**"])
        for jar_path in project_base.rglob('*.jar'):
            str_path = str(jar_path)
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(str_path, pattern) or pattern.replace("**/", "") in str_path:
                    should_exclude = True
                    break
            if not should_exclude:
                jar_files.append(str_path)
        self.logger.info(f"발견된 JAR 파일: {len(jar_files)}개")
        return jar_files

    async def _analyze_jars(self, jar_files: List[str], project_id: int):
        parser = self.parsers.get('jar')
        if not parser:
            return
        for jar_path in jar_files:
            try:
                file_obj, classes, methods, _ = parser.parse_file(jar_path, project_id)
                session = self.db_manager.get_session()
                try:
                    session.add(file_obj)
                    session.flush()
                    file_id = file_obj.file_id
                    class_id_map = {}
                    for cls in classes:
                        cls.file_id = file_id
                        session.add(cls)
                        session.flush()
                        class_id_map[cls.fqn] = cls.class_id
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
                    self.logger.error(f"JAR 저장 오류 {jar_path}: {e}")
                finally:
                    session.close()
            except Exception as e:
                self.logger.error(f"JAR 분석 실패 {jar_path}: {e}")

    async def _analyze_files(self, source_files: List[str], project_id: int):
        """파일 분석 실행"""
        for file_path in source_files:
            try:
                self.logger.debug(f"파일 분석 시작: {file_path}")
                
                # 파일 확장자에 따라 적절한 파서 선택
                file_ext = Path(file_path).suffix.lower()
                parser = None
                
                if file_ext == '.java':
                    parser = self.parsers.get('java')
                elif file_ext == '.jsp':
                    parser = self.parsers.get('jsp_mybatis')
                elif file_ext in ['.xml', '.sql']:
                    if 'mybatis' in file_path.lower() or file_ext == '.xml':
                        parser = self.parsers.get('jsp_mybatis')
                    else:
                        parser = self.parsers.get('sql')
                elif file_ext == '.properties':
                    continue  # Properties 파일은 현재 분석하지 않음
                
                if parser:
                    parse_result = parser.parse_file(file_path, project_id)
                    if parse_result and len(parse_result) == 4:
                        file_obj, classes, methods, edges = parse_result
                        # 파서 결과를 데이터베이스에 저장 (올바른 순서로)
                        session = self.db_manager.get_session()
                        try:
                            # 1. 파일 객체 저장하고 ID 확보
                            if file_obj:
                                session.add(file_obj)
                                session.flush()  # ID를 즉시 확보하기 위해 flush
                                file_id = file_obj.file_id
                            else:
                                file_id = None
                            
                            # 2. 클래스 객체의 file_id 설정 후 저장
                            class_id_map = {}  # class fqn -> class_id mapping
                            for cls in classes:
                                if file_id:
                                    cls.file_id = file_id
                                session.add(cls)
                                session.flush()
                                class_id_map[cls.fqn] = cls.class_id
                            
                            # 3. 메소드 객체의 file_id, class_id 설정 후 저장
                            for method in methods:
                                if file_id:
                                    method.file_id = file_id
                                # Method가 Class에 속한 경우 class_id 설정 (owner_fqn 기준으로 찾기)
                                if hasattr(method, 'owner_fqn') and method.owner_fqn in class_id_map:
                                    method.class_id = class_id_map[method.owner_fqn]
                                session.add(method)
                                session.flush()

                            # 모든 메서드가 저장된 후, 엣지의 src_id를 해결
                            method_id_map = {f"{getattr(m, 'owner_fqn', '')}.{m.name}": m.method_id for m in methods}

                            # 4. 엣지 객체의 project_id, src_id, dst_id 설정 후 저장
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
                            self.logger.error(f"데이터베이스 저장 오류 {file_path}: {e}")
                        finally:
                            session.close()
                else:
                    self.logger.debug(f"지원하지 않는 파일 형식: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"파일 분석 오류 {file_path}: {e}", exc_info=True)

    def _validate_confidence_formula_on_startup(self):
        # ... (Implementation from previous version) ...
        pass # Placeholder

def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(
        description='소스 코드 분석 도구 - 1단계 메타정보 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', default=str(script_dir / '../config/config.yaml'), help='전역 설정 파일 경로')
    parser.add_argument('--phase-config', default=str(script_dir / '../config/phase1/config.yaml'), help='Phase별 설정 파일 경로')
    parser.add_argument('--project-name', required=True, help='프로젝트 이름 (필수)')
    parser.add_argument('--source-path', help='소스 코드 경로 (기본값: config.yaml에 정의)')
    parser.add_argument('--incremental', action='store_true', help='증분 분석 모드')
    parser.add_argument('--clean', action='store_true', help='분석 전 기존 프로젝트 DB 파일을 삭제합니다.')
    parser.add_argument('--all', action='store_true', help='분석 후 자동으로 시각화까지 수행')
    parser.add_argument('--verbose', '-v', action='store_true', help='상세 로그 출력')
    parser.add_argument('--quiet', '-q', action='store_true', help='최소 로그 출력')
    
    args = parser.parse_args()
    project_name = args.project_name

    global_config_path = Path(args.config).resolve()
    phase_config_path = Path(args.phase_config).resolve()

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
                    print(f"오류: DB 파일 삭제 실패: {e}")
                    sys.exit(1)
            else:
                print(f"기존 DB 파일({db_path})이 없어 정리할 필요가 없습니다.")
        else:
            print("경고: 설정 파일에서 DB 경로를 찾을 수 없어 --clean을 실행할 수 없습니다.")

    project_base_dir = project_root / f"project/{project_name}"
    source_dir = Path(args.source_path) if args.source_path else project_base_dir / "src"
    source_dir.mkdir(parents=True, exist_ok=True)

    if not any(source_dir.iterdir()):
        print(f"경고: 소스 디렉토리가 비어있습니다: {source_dir}")

    try:
        analyzer = SourceAnalyzer(str(global_config_path), str(phase_config_path), project_name=project_name)
        if args.verbose:
            analyzer.logger.logger.setLevel(logging.DEBUG)
        elif args.quiet:
            analyzer.logger.logger.setLevel(logging.WARNING)
        
        asyncio.run(analyzer.analyze_project(str(source_dir), project_name, args.incremental))

        if args.all:
            print("\n[INFO] 전체 시각화 실행 중...")
            # ... (Visualization call logic) ...

    except Exception as e:
        print(f"분석 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()