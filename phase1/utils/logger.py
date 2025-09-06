"""
통합 로깅 시스템
모든 파서와 엔진에서 사용할 수 있는 표준화된 로깅 인터페이스 제공
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
import inspect


class AnalyzerLogger:
    """소스 분석기 전용 로거"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        분석기 로거 초기화
        
        Args:
            name: 로거 이름
            config: 로거 설정 딕셔너리
        """
        self.name = name
        self.config = config or {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정 및 초기화"""
        logger = logging.getLogger(self.name)
        
        # 중복 핸들러 방지
        if logger.handlers:
            return logger
            
        # 로그 레벨 설정
        log_level = self.config.get('level', 'INFO')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 포매터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 파일 핸들러 - 타임스탬프 포함 파일명 생성
        log_file = self.config.get('file', './logs/analyzer.log')
        if log_file:
            # 로그 디렉토리 생성
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # 타임스탬프가 포함된 파일명 생성
            if '{timestamp}' in log_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_file = log_file.replace('{timestamp}', timestamp)
            
            # 회전 파일 핸들러 (최대 100MB, 백업 3개)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=3,
                encoding='utf-8-sig'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        return logger
        
    def debug(self, message: str, **kwargs):
        """디버그 메시지 로깅"""
        self.logger.debug(message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """정보 메시지 로깅"""
        self.logger.info(message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """경고 메시지 로깅"""
        self.logger.warning(message, **kwargs)
        
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """오류 메시지 로깅 (스택 트레이스 포함)"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, **kwargs)
        else:
            self.logger.error(message, **kwargs)
            
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """치명적 오류 메시지 로깅"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, **kwargs)
        else:
            self.logger.critical(message, **kwargs)
            
    def log_parsing_start(self, file_path: str, parser_type: str):
        """파싱 시작 로깅"""
        self.info(f"파싱 시작: {parser_type} | {file_path}")
        
    def log_parsing_success(self, file_path: str, parser_type: str, 
                          classes: int = 0, methods: int = 0, sql_units: int = 0):
        """파싱 성공 로깅"""
        self.info(f"파싱 성공: {parser_type} | {file_path} | "
                 f"클래스: {classes}, 메서드: {methods}, SQL: {sql_units}")
                 
    def log_parsing_failure(self, file_path: str, parser_type: str, 
                          exception: Exception, fallback_used: bool = False):
        """파싱 실패 로깅"""
        fallback_msg = " (폴백 파서 사용됨)" if fallback_used else ""
        self.error(f"파싱 실패: {parser_type} | {file_path}{fallback_msg}", 
                  exception=exception)
                  
    def log_confidence_calculation(self, target_type: str, target_id: int, 
                                 pre_confidence: float, post_confidence: float, 
                                 factors: Dict[str, float]):
        """신뢰도 계산 로깅"""
        self.debug(f"신뢰도 계산: {target_type}#{target_id} | "
                  f"{pre_confidence:.3f} -> {post_confidence:.3f} | "
                  f"요인: {factors}")
                  
    def log_database_operation(self, operation: str, table: str, 
                             records: int = 0, success: bool = True):
        """데이터베이스 작업 로깅"""
        status = "성공" if success else "실패"
        self.info(f"DB {operation}: {table} | {records}건 | {status}")
        
    def log_performance_metric(self, operation: str, duration: float, 
                             items_processed: int = 0):
        """성능 메트릭 로깅"""
        rate = f", {items_processed/duration:.1f}건/초" if items_processed > 0 else ""
        self.info(f"성능: {operation} | {duration:.2f}초{rate}")
        
    def log_memory_usage(self, operation: str, memory_mb: float):
        """메모리 사용량 로깅"""
        self.debug(f"메모리: {operation} | {memory_mb:.1f}MB")


class LoggerFactory:
    """로거 팩토리 클래스"""
    
    _loggers: Dict[str, AnalyzerLogger] = {}
    _default_config: Optional[Dict[str, Any]] = None
    
    @classmethod
    def setup_default_config(cls, config: Dict[str, Any]):
        """기본 로거 설정"""
        cls._default_config = config.get('logging', {})
        
    @classmethod
    def get_logger(cls, name: str, config: Optional[Dict[str, Any]] = None) -> AnalyzerLogger:
        """로거 인스턴스 반환 (싱글톤 패턴)"""
        if name not in cls._loggers:
            logger_config = config or cls._default_config or {}
            cls._loggers[name] = AnalyzerLogger(name, logger_config)
        return cls._loggers[name]
        
    @classmethod
    def get_parser_logger(cls, parser_name: str) -> AnalyzerLogger:
        """파서 전용 로거 반환"""
        return cls.get_logger(f"parser.{parser_name}")
        
    @classmethod
    def get_engine_logger(cls) -> AnalyzerLogger:
        """엔진 전용 로거 반환"""
        return cls.get_logger("engine.metadata")
        
    @classmethod
    def get_analyzer_logger(cls) -> AnalyzerLogger:
        """분석기 전용 로거 반환"""
        return cls.get_logger("analyzer.dependency")


class PerformanceLogger:
    """성능 측정 및 로깅을 위한 컨텍스트 매니저"""
    
    def __init__(self, logger: AnalyzerLogger, operation: str, 
                 items_count: int = 0):
        """
        성능 측정 로거 초기화
        
        Args:
            logger: 사용할 로거 인스턴스
            operation: 측정할 작업명
            items_count: 처리할 아이템 수
        """
        self.logger = logger
        self.operation = operation
        self.items_count = items_count
        self.start_time = None
        
    def __enter__(self):
        """컨텍스트 진입 시 성능 측정 시작"""
        self.start_time = datetime.now()
        self.logger.debug(f"성능 측정 시작: {self.operation}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 종료 시 성능 계산 및 로깅"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type is None:
                # 정상 완료
                self.logger.log_performance_metric(
                    self.operation, duration, self.items_count
                )
            else:
                # 예외 발생
                self.logger.error(f"성능 측정 중단: {self.operation} | "
                                f"{duration:.2f}초 후 오류 발생", 
                                exception=exc_val)


class ExceptionHandler:
    """예외 처리 및 로깅을 위한 데코레이터와 컨텍스트 매니저"""
    
    @staticmethod
    def log_and_reraise(logger: AnalyzerLogger, operation: str):
        """예외를 로깅하고 다시 발생시키는 데코레이터"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"{operation} 실행 중 오류", exception=e)
                    raise
            return wrapper
        return decorator
        
    @staticmethod
    def log_and_return_none(logger: AnalyzerLogger, operation: str, 
                          return_value=None):
        """예외를 로깅하고 기본값을 반환하는 데코레이터"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"{operation} 실행 중 오류 (기본값 반환)", 
                               exception=e)
                    return return_value
            return wrapper
        return decorator


def handle_critical_error(logger, error_msg: str, exception: Exception = None, exit_code: int = 1):
    """
    치명적 에러 처리 공통 함수
    에러 로그를 남기고 프로그램을 종료합니다.
    
    Args:
        logger: 로거 인스턴스 (AnalyzerLogger 또는 표준 logger)
        error_msg: 에러 메시지
        exception: 발생한 예외 (선택사항)
        exit_code: 종료 코드 (기본값: 1)
    """
    # 전체 스택 트레이스에서 실제 에러 발생 지점 찾기
    tb = traceback.extract_tb(sys.exc_info()[2]) if exception else traceback.extract_stack()
    
    if tb and len(tb) >= 2:
        # 마지막에서 두 번째 프레임이 실제 에러 발생 지점 (마지막은 이 함수)
        error_frame = tb[-2]
        actual_filename = os.path.basename(error_frame.filename)
        actual_line = error_frame.lineno
        actual_function = error_frame.name
        
        # 전체 에러 메시지 구성
        full_error_msg = f"[{actual_filename}:{actual_line}] {actual_function}() - {error_msg}"
    else:
        # 스택 정보가 없는 경우 기본 메시지
        full_error_msg = f"CRITICAL ERROR - {error_msg}"
    
    if exception:
        full_error_msg += f" | Exception: {str(exception)}"
    
    # 전체 트레이스백 정보 추가
    traceback_str = traceback.format_exc()
    full_error_msg += f"\nFull Traceback:\n{traceback_str}"
    
    # 로거 타입에 따라 로깅
    if hasattr(logger, 'error'):
        if isinstance(logger, AnalyzerLogger):
            logger.error(full_error_msg)
        else:
            logger.error(full_error_msg)
    else:
        print(f"CRITICAL ERROR: {full_error_msg}")
    
    # 프로그램 종료
    sys.exit(exit_code)


def handle_non_critical_error(logger, error_msg: str, exception: Exception = None):
    """
    일반 에러 처리 공통 함수
    에러 로그만 남기고 계속 진행합니다.
    
    Args:
        logger: 로거 인스턴스
        error_msg: 에러 메시지  
        exception: 발생한 예외 (선택사항)
    """
    # 호출자 정보 수집
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name
    
    # 전체 에러 메시지 구성
    full_error_msg = f"[{filename}:{line_number}] {function_name}() - {error_msg}"
    
    if exception:
        full_error_msg += f" | Exception: {str(exception)}"
        
    # 로거 타입에 따라 로깅
    if hasattr(logger, 'error'):
        if isinstance(logger, AnalyzerLogger):
            logger.error(full_error_msg)
        else:
            logger.error(full_error_msg)
    else:
        print(f"ERROR: {full_error_msg}")


def setup_logging(config: Dict[str, Any]):
    """
    전체 시스템의 로깅 설정 초기화
    
    Args:
        config: 로깅 설정이 포함된 전체 설정 딕셔너리
        
    Returns:
        초기화된 메인 로거 인스턴스
    """
    LoggerFactory.setup_default_config(config)
    
    # 메인 로거 초기화 - 로깅 설정을 직접 전달
    logging_config = config.get('logging', {})
    main_logger = LoggerFactory.get_logger("main", logging_config)
    main_logger.info("로깅 시스템 초기화 완료")
    
    return main_logger