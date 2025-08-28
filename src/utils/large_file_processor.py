"""
대용량 파일 처리 최적화 모듈
개선할내역_v2.md Phase 1 Priority 3: 대용량 파일 메모리 효율적 처리
"""

import os
import mmap
import tempfile
import threading
import logging
from typing import Iterator, List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
import gc
import psutil
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import time


@dataclass
class FileChunk:
    """파일 청크 정보"""
    file_path: str
    start_pos: int
    end_pos: int
    chunk_id: int
    content: Optional[str] = None
    size: int = 0
    
    def __post_init__(self):
        if self.content is not None:
            self.size = len(self.content)


@dataclass
class ProcessingStats:
    """처리 통계"""
    total_files: int = 0
    large_files: int = 0
    total_size_mb: float = 0.0
    processing_time: float = 0.0
    memory_peak_mb: float = 0.0
    chunks_processed: int = 0
    optimization_applied: List[str] = None
    
    def __post_init__(self):
        if self.optimization_applied is None:
            self.optimization_applied = []


class MemoryMonitor:
    """메모리 사용량 모니터링"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.peak_memory = 0
        self.monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self):
        """모니터링 시작"""
        self.peak_memory = 0
        self.monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self._monitor_thread.start()
        
    def stop_monitoring(self) -> float:
        """모니터링 중지 및 피크 메모리 반환 (MB)"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        return self.peak_memory / 1024 / 1024  # MB 단위
        
    def _monitor_memory(self):
        """메모리 모니터링 스레드"""
        while self.monitoring:
            try:
                memory_bytes = self.process.memory_info().rss
                self.peak_memory = max(self.peak_memory, memory_bytes)
                time.sleep(0.1)  # 100ms 간격
            except Exception:
                break


class LargeFileProcessor:
    """대용량 파일 처리 최적화 클래스"""
    
    # 파일 크기 임계값 (바이트)
    LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50MB
    HUGE_FILE_THRESHOLD = 500 * 1024 * 1024  # 500MB
    
    # 청크 크기 (바이트)
    DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
    SMALL_CHUNK_SIZE = 4 * 1024 * 1024   # 4MB
    LARGE_CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 메모리 제한 (시스템 메모리의 70%)
        total_memory = psutil.virtual_memory().total
        self.memory_limit = int(total_memory * 0.7)
        
        # 임시 파일 디렉토리
        self.temp_dir = self.config.get('temp_directory', tempfile.gettempdir())
        
        self.logger.info(f"대용량 파일 프로세서 초기화: 메모리 제한 {self.memory_limit // 1024 // 1024}MB")
        
    def is_large_file(self, file_path: str) -> bool:
        """파일이 대용량인지 확인"""
        try:
            file_size = os.path.getsize(file_path)
            return file_size >= self.LARGE_FILE_THRESHOLD
        except OSError:
            return False
            
    def get_file_category(self, file_path: str) -> str:
        """파일 크기 카테고리 반환"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size >= self.HUGE_FILE_THRESHOLD:
                return "huge"
            elif file_size >= self.LARGE_FILE_THRESHOLD:
                return "large"
            else:
                return "normal"
        except OSError:
            return "unknown"
            
    def get_optimal_chunk_size(self, file_size: int) -> int:
        """파일 크기에 따른 최적 청크 크기 결정"""
        if file_size >= self.HUGE_FILE_THRESHOLD:
            return self.LARGE_CHUNK_SIZE
        elif file_size >= self.LARGE_FILE_THRESHOLD:
            return self.DEFAULT_CHUNK_SIZE
        else:
            return self.SMALL_CHUNK_SIZE
            
    def chunk_file_by_lines(self, file_path: str, 
                           lines_per_chunk: int = 10000) -> Iterator[FileChunk]:
        """파일을 라인 단위로 청크 분할"""
        
        chunk_id = 0
        current_lines = []
        line_count = 0
        start_pos = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    current_lines.append(line)
                    line_count += 1
                    
                    if line_count >= lines_per_chunk:
                        end_pos = f.tell()
                        content = ''.join(current_lines)
                        
                        yield FileChunk(
                            file_path=file_path,
                            start_pos=start_pos,
                            end_pos=end_pos,
                            chunk_id=chunk_id,
                            content=content
                        )
                        
                        # 다음 청크 준비
                        chunk_id += 1
                        current_lines.clear()
                        line_count = 0
                        start_pos = end_pos
                        
                # 마지막 청크 처리
                if current_lines:
                    content = ''.join(current_lines)
                    yield FileChunk(
                        file_path=file_path,
                        start_pos=start_pos,
                        end_pos=start_pos + len(content.encode('utf-8')),
                        chunk_id=chunk_id,
                        content=content
                    )
                    
        except Exception as e:
            self.logger.error(f"라인 청크 분할 오류 {file_path}: {e}")
            
    def chunk_file_by_size(self, file_path: str, 
                          chunk_size: int = None) -> Iterator[FileChunk]:
        """파일을 크기 단위로 청크 분할 (메모리 맵 사용)"""
        
        if chunk_size is None:
            file_size = os.path.getsize(file_path)
            chunk_size = self.get_optimal_chunk_size(file_size)
            
        chunk_id = 0
        
        try:
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    file_size = mm.size()
                    
                    for start in range(0, file_size, chunk_size):
                        end = min(start + chunk_size, file_size)
                        
                        # 라인 경계에서 분할하도록 조정
                        if end < file_size:
                            # 다음 개행 문자 찾기
                            while end < file_size and mm[end:end+1] != b'\n':
                                end += 1
                            if end < file_size:
                                end += 1  # 개행 문자 포함
                                
                        chunk_data = mm[start:end]
                        try:
                            content = chunk_data.decode('utf-8', errors='ignore')
                        except UnicodeDecodeError:
                            content = chunk_data.decode('latin1', errors='ignore')
                            
                        yield FileChunk(
                            file_path=file_path,
                            start_pos=start,
                            end_pos=end,
                            chunk_id=chunk_id,
                            content=content
                        )
                        
                        chunk_id += 1
                        
        except Exception as e:
            self.logger.error(f"크기 청크 분할 오류 {file_path}: {e}")
            
    def process_large_file_streaming(self, 
                                   file_path: str,
                                   processor_func: Callable[[str], Any],
                                   chunk_method: str = "size") -> Dict[str, Any]:
        """
        대용량 파일 스트리밍 처리
        
        Args:
            file_path: 처리할 파일 경로
            processor_func: 청크 처리 함수
            chunk_method: 청크 분할 방법 ("size" 또는 "lines")
            
        Returns:
            처리 결과
        """
        
        start_time = time.time()
        memory_monitor = MemoryMonitor()
        memory_monitor.start_monitoring()
        
        file_size = os.path.getsize(file_path)
        self.logger.info(f"대용량 파일 처리 시작: {file_path} ({file_size // 1024 // 1024}MB)")
        
        results = []
        chunks_processed = 0
        
        try:
            # 청크 분할 방법 선택
            if chunk_method == "lines":
                chunks = self.chunk_file_by_lines(file_path)
            else:
                chunks = self.chunk_file_by_size(file_path)
                
            # 청크별 처리
            for chunk in chunks:
                try:
                    # 메모리 사용량 확인
                    current_memory = psutil.Process().memory_info().rss
                    if current_memory > self.memory_limit:
                        # 가비지 컬렉션 강제 실행
                        gc.collect()
                        self.logger.warning(f"메모리 제한 근접, 가비지 컬렉션 실행: {current_memory // 1024 // 1024}MB")
                        
                    # 청크 처리
                    chunk_result = processor_func(chunk.content)
                    results.append({
                        'chunk_id': chunk.chunk_id,
                        'start_pos': chunk.start_pos,
                        'end_pos': chunk.end_pos,
                        'size': chunk.size,
                        'result': chunk_result
                    })
                    
                    chunks_processed += 1
                    
                    # 처리된 청크의 내용 메모리에서 해제
                    chunk.content = None
                    
                    # 주기적 가비지 컬렉션
                    if chunks_processed % 10 == 0:
                        gc.collect()
                        
                except Exception as e:
                    self.logger.error(f"청크 처리 오류 (chunk_id: {chunk.chunk_id}): {e}")
                    
        except Exception as e:
            self.logger.error(f"파일 처리 오류 {file_path}: {e}")
            
        processing_time = time.time() - start_time
        peak_memory_mb = memory_monitor.stop_monitoring()
        
        self.logger.info(f"대용량 파일 처리 완료: {chunks_processed}개 청크, "
                        f"{processing_time:.2f}초, 피크 메모리: {peak_memory_mb:.1f}MB")
        
        return {
            'file_path': file_path,
            'file_size_mb': file_size / 1024 / 1024,
            'chunks_processed': chunks_processed,
            'processing_time': processing_time,
            'peak_memory_mb': peak_memory_mb,
            'results': results,
            'chunk_method': chunk_method
        }
        
    def process_multiple_large_files(self, 
                                   file_paths: List[str],
                                   processor_func: Callable[[str], Any],
                                   max_workers: int = 2) -> Dict[str, Any]:
        """
        여러 대용량 파일 병렬 처리
        
        Args:
            file_paths: 처리할 파일 경로 목록
            processor_func: 처리 함수
            max_workers: 최대 워커 수 (대용량 파일은 적은 워커 수 권장)
            
        Returns:
            전체 처리 결과
        """
        
        start_time = time.time()
        memory_monitor = MemoryMonitor()
        memory_monitor.start_monitoring()
        
        # 파일 크기별 분류
        file_categories = {
            'normal': [],
            'large': [],
            'huge': []
        }
        
        total_size = 0
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                category = self.get_file_category(file_path)
                file_categories[category].append(file_path)
                
        self.logger.info(f"다중 파일 처리 시작: 총 {len(file_paths)}개 파일, "
                        f"{total_size // 1024 // 1024}MB")
        self.logger.info(f"분류: 일반 {len(file_categories['normal'])}개, "
                        f"대용량 {len(file_categories['large'])}개, "
                        f"초대용량 {len(file_categories['huge'])}개")
        
        all_results = []
        processing_stats = ProcessingStats()
        processing_stats.total_files = len(file_paths)
        processing_stats.total_size_mb = total_size / 1024 / 1024
        
        try:
            # 1. 초대용량 파일 순차 처리
            for file_path in file_categories['huge']:
                self.logger.info(f"초대용량 파일 처리: {file_path}")
                result = self.process_large_file_streaming(
                    file_path, processor_func, chunk_method="size"
                )
                all_results.append(result)
                processing_stats.large_files += 1
                processing_stats.chunks_processed += result['chunks_processed']
                processing_stats.optimization_applied.append(f"{file_path}: 스트리밍 청크 처리")
                
            # 2. 대용량 파일 제한된 병렬 처리
            if file_categories['large']:
                with ThreadPoolExecutor(max_workers=min(max_workers, 2)) as executor:
                    future_to_file = {
                        executor.submit(
                            self.process_large_file_streaming, 
                            file_path, processor_func, "lines"
                        ): file_path
                        for file_path in file_categories['large']
                    }
                    
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            result = future.result()
                            all_results.append(result)
                            processing_stats.large_files += 1
                            processing_stats.chunks_processed += result['chunks_processed']
                            processing_stats.optimization_applied.append(f"{file_path}: 병렬 청크 처리")
                        except Exception as e:
                            self.logger.error(f"대용량 파일 처리 오류 {file_path}: {e}")
                            
            # 3. 일반 파일 고속 병렬 처리
            if file_categories['normal']:
                with ThreadPoolExecutor(max_workers=max_workers * 2) as executor:
                    future_to_file = {
                        executor.submit(self._process_normal_file, file_path, processor_func): file_path
                        for file_path in file_categories['normal']
                    }
                    
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            result = future.result()
                            all_results.append(result)
                            processing_stats.optimization_applied.append(f"{file_path}: 일반 처리")
                        except Exception as e:
                            self.logger.error(f"일반 파일 처리 오류 {file_path}: {e}")
                            
        except Exception as e:
            self.logger.error(f"다중 파일 처리 오류: {e}")
            
        processing_stats.processing_time = time.time() - start_time
        processing_stats.memory_peak_mb = memory_monitor.stop_monitoring()
        
        self.logger.info(f"다중 파일 처리 완료: {processing_stats.processing_time:.2f}초, "
                        f"피크 메모리: {processing_stats.memory_peak_mb:.1f}MB")
        
        return {
            'processing_stats': processing_stats,
            'file_results': all_results,
            'file_categories': {k: len(v) for k, v in file_categories.items()},
            'optimization_summary': self._generate_optimization_summary(processing_stats)
        }
        
    def _process_normal_file(self, file_path: str, processor_func: Callable[[str], Any]) -> Dict[str, Any]:
        """일반 크기 파일 처리"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            result = processor_func(content)
            
            return {
                'file_path': file_path,
                'file_size_mb': os.path.getsize(file_path) / 1024 / 1024,
                'chunks_processed': 1,
                'result': result,
                'chunk_method': 'full'
            }
        except Exception as e:
            self.logger.error(f"일반 파일 처리 오류 {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e)
            }
            
    def create_temp_file_chunks(self, 
                              file_path: str,
                              chunk_size: int = None) -> List[str]:
        """대용량 파일을 임시 청크 파일들로 분할"""
        
        if chunk_size is None:
            file_size = os.path.getsize(file_path)
            chunk_size = self.get_optimal_chunk_size(file_size)
            
        temp_files = []
        chunk_id = 0
        
        try:
            with open(file_path, 'rb') as source_file:
                while True:
                    chunk_data = source_file.read(chunk_size)
                    if not chunk_data:
                        break
                        
                    # 임시 파일 생성
                    temp_file = tempfile.NamedTemporaryFile(
                        mode='wb',
                        delete=False,
                        dir=self.temp_dir,
                        prefix=f"chunk_{os.path.basename(file_path)}_{chunk_id}_"
                    )
                    
                    temp_file.write(chunk_data)
                    temp_file.close()
                    
                    temp_files.append(temp_file.name)
                    chunk_id += 1
                    
        except Exception as e:
            # 오류 발생 시 생성된 임시 파일들 정리
            self.cleanup_temp_files(temp_files)
            raise e
            
        self.logger.info(f"임시 청크 파일 생성 완료: {len(temp_files)}개")
        return temp_files
        
    def cleanup_temp_files(self, temp_files: List[str]):
        """임시 파일들 정리"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                self.logger.warning(f"임시 파일 삭제 실패 {temp_file}: {e}")
                
    def _generate_optimization_summary(self, stats: ProcessingStats) -> Dict[str, Any]:
        """최적화 적용 요약 생성"""
        
        optimization_summary = {
            'memory_efficiency': {
                'peak_memory_mb': stats.memory_peak_mb,
                'memory_per_file_mb': stats.memory_peak_mb / max(stats.total_files, 1),
                'efficiency_rating': 'high' if stats.memory_peak_mb < 500 else 'medium' if stats.memory_peak_mb < 1000 else 'low'
            },
            'processing_efficiency': {
                'total_time_seconds': stats.processing_time,
                'time_per_mb': stats.processing_time / max(stats.total_size_mb, 1),
                'chunks_processed': stats.chunks_processed,
                'large_files_handled': stats.large_files
            },
            'optimizations_applied': stats.optimization_applied,
            'recommendations': []
        }
        
        # 권장사항 생성
        if stats.memory_peak_mb > 1000:
            optimization_summary['recommendations'].append(
                "메모리 사용량이 높습니다. 청크 크기를 줄이거나 배치 크기를 제한하세요."
            )
            
        if stats.processing_time / max(stats.total_size_mb, 1) > 1.0:
            optimization_summary['recommendations'].append(
                "처리 속도가 느립니다. 병렬 처리 워커 수를 늘리거나 청크 크기를 조정하세요."
            )
            
        if stats.large_files / max(stats.total_files, 1) > 0.3:
            optimization_summary['recommendations'].append(
                "대용량 파일 비율이 높습니다. 스트리밍 처리와 메모리 모니터링을 강화하세요."
            )
            
        return optimization_summary


# 테스트용 파일 처리 함수
def sample_processor(content: str) -> Dict[str, Any]:
    """샘플 파일 처리 함수"""
    lines = content.count('\n')
    words = len(content.split())
    chars = len(content)
    
    # 간단한 패턴 검색 시뮬레이션
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
    sql_count = sum(content.upper().count(keyword) for keyword in sql_keywords)
    
    return {
        'lines': lines,
        'words': words,
        'characters': chars,
        'sql_statements': sql_count,
        'processed_at': time.time()
    }