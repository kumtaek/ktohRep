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
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime

# 프로젝트 루트를 Python 패스에 추가 (수정됨: src의 부모 디렉토리 추가)
project_root = Path(__file__).parent.parent  # src의 부모 디렉토리
sys.path.insert(0, str(project_root))

from src.models.database import DatabaseManager, File
from src.parsers.java_parser import JavaParser
from src.parsers.jsp_mybatis_parser import JspMybatisParser
from src.parsers.sql_parser import SqlParser
from src.database.metadata_engine import MetadataEngine
from src.utils.csv_loader import CsvLoader
from src.utils.logger import setup_logging, LoggerFactory, PerformanceLogger
from src.utils.confidence_calculator import ConfidenceCalculator


class SourceAnalyzer:
    """소스 분석기 메인 클래스"""
    
    def __init__(self, config_path: str):
        """
        소스 분석기 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        
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
            
        except Exception as e:
            self.logger.critical("시스템 초기화 실패", exception=e)
            raise
            
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드 (개선된 예외 처리)"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 기본값 설정
            self._set_default_config(config)
            
            return config
            
        except FileNotFoundError:
            print(f"오류: 설정 파일을 찾을 수 없습니다: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"오류: 설정 파일 파싱 실패: {e}")
            raise
        except Exception as e:
            print(f"오류: 설정 파일 로드 중 예상치 못한 오류: {e}")
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
                    return self._create_empty_result(project_id, project_name)
                
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
                
    def _create_empty_result(self, project_id: int, project_name: str) -> Dict[str, Any]:
        """빈 분석 결과 생성"""
        return {
            'project_id': project_id,
            'project_name': project_name,
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
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        }
        
    async def _load_db_schema(self, project_root: str, project_name: str, project_id: int):
        """DB 스키마 정보 로드 (개선된 오류 처리)"""
        
        db_schema_path = os.path.join(project_root, "DB_SCHEMA")
        if not os.path.exists(db_schema_path):
            self.logger.warning(f"DB 스키마 경로가 없습니다: {db_schema_path}")
            return
            
        self.logger.info(f"DB 스키마 정보 로딩 중: {db_schema_path}")
        
        required_files = self.config['db_schema']['required_files']
        loaded_files = []
        
        for csv_file in required_files:
            csv_path = os.path.join(db_schema_path, csv_file)
            
            try:
                if os.path.exists(csv_path):
                    result = await self.csv_loader.load_csv(csv_path, project_id)
                    loaded_files.append(csv_file)
                    self.logger.info(f"CSV 로드 완료: {csv_file} ({result['records']}건)")
                else:
                    self.logger.warning(f"CSV 파일 없음: {csv_path}")
                    
            except Exception as e:
                self.logger.error(f"CSV 로드 실패: {csv_file}", exception=e)
                
        if loaded_files:
            self.logger.info(f"DB 스키마 로딩 완료: {len(loaded_files)}/{len(required_files)} 파일")
        else:
            self.logger.warning("DB 스키마 파일이 로드되지 않았습니다.")
            
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
                # 제외 패턴에 해당하는 디렉토리 건너뛰기
                dirs[:] = [d for d in dirs if not any(
                    self._match_pattern(os.path.join(root, d), pattern) 
                    for pattern in exclude_patterns
                )]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 포함 패턴 확인
                    if any(self._match_pattern(file_path, pattern) for pattern in include_patterns):
                        # 제외 패턴 확인
                        if not any(self._match_pattern(file_path, pattern) for pattern in exclude_patterns):
                            source_files.append(file_path)
                            
        except Exception as e:
            self.logger.error(f"파일 수집 중 오류: {project_root}", exception=e)
            
        self.logger.debug(f"수집된 파일 수: {len(source_files)}")
        return source_files
        
    async def _filter_changed_files(self, source_files: List[str], project_id: int) -> List[str]:
        """증분 분석을 위한 변경된 파일 필터링"""
        changed_files = []
        
        # 기존 파일 해시 정보 조회
        session = self.db_manager.get_session()
        try:
            existing_files = session.query(File).filter(File.project_id == project_id).all()
            existing_hashes = {f.path: f.hash for f in existing_files}
            
            for file_path in source_files:
                try:
                    # 현재 파일 해시 계산
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        current_hash = hashlib.sha256(content).hexdigest()
                    
                    # 해시 비교로 변경 여부 확인
                    if file_path not in existing_hashes or existing_hashes[file_path] != current_hash:
                        changed_files.append(file_path)
                        self.logger.debug(f"변경된 파일 감지: {file_path}")
                    
                except Exception as e:
                    # 파일 읽기 실패 시 안전하게 포함
                    self.logger.warning(f"파일 해시 계산 실패 {file_path}: {e}")
                    changed_files.append(file_path)
            
        except Exception as e:
            self.logger.error("증분 분석 파일 필터링 중 오류", exception=e)
            # 오류 시 전체 파일 반환
            return source_files
        finally:
            session.close()
            
        return changed_files
        
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """파일 패턴 매칭 (개선된 로직)"""
        import fnmatch
        
        # 절대 경로와 상대 경로 모두 확인
        abs_path = os.path.abspath(file_path)
        rel_path = os.path.relpath(file_path)
        basename = os.path.basename(file_path)
        
        return (fnmatch.fnmatch(abs_path, pattern) or 
                fnmatch.fnmatch(rel_path, pattern) or 
                fnmatch.fnmatch(basename, pattern))
        
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
                'analysis_timestamp': datetime.utcnow().isoformat()
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

def main():
    """메인 함수"""
    
    parser = argparse.ArgumentParser(
        description='소스 코드 분석 도구 - 1단계 메타정보 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시 사용법:
  python main.py PROJECT/sample-app
  python main.py PROJECT/sample-app --project-name "샘플 앱"
  python main.py PROJECT/sample-app --config custom_config.yaml
        """
    )
    
    parser.add_argument('project_path', help='분석할 프로젝트 경로')
    parser.add_argument('--config', default='./config/config.yaml', 
                       help='설정 파일 경로 (기본값: ./config/config.yaml)')
    parser.add_argument('--project-name', help='프로젝트 이름 (기본값: 폴더명)')
    parser.add_argument('--incremental', action='store_true', 
                       help='증분 분석 모드 (변경된 파일만 분석)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='상세 로그 출력')
    parser.add_argument('--quiet', '-q', action='store_true', 
                       help='최소 로그 출력')
    
    args = parser.parse_args()
    
    # 입력 검증
    if not os.path.exists(args.project_path):
        print(f"❌ 오류: 프로젝트 경로가 존재하지 않습니다: {args.project_path}")
        sys.exit(1)
        
    if not os.path.exists(args.config):
        print(f"❌ 오류: 설정 파일이 존재하지 않습니다: {args.config}")
        sys.exit(1)
        
    try:
        # 소스 분석기 초기화
        print("소스 분석기 초기화 중...")
        analyzer = SourceAnalyzer(args.config)
        
        # 로그 레벨 조정 (로거가 없으면 기본 로깅 사용)
        if hasattr(analyzer.logger, 'logger'):
            if args.verbose:
                analyzer.logger.logger.setLevel('DEBUG')
            elif args.quiet:
                analyzer.logger.logger.setLevel('WARNING')
        
        # 프로젝트 분석 실행
        print(f"프로젝트 분석 시작: {args.project_path}")
        result = asyncio.run(analyzer.analyze_project(
            args.project_path, 
            args.project_name,
            args.incremental
        ))
        
        # 결과 출력
        print_analysis_results(result)
        
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