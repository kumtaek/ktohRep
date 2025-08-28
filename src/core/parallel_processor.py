"""
병렬 처리 검증 및 최적화 모듈
Phase 1 Priority 2: 병렬 처리 성능 최적화 및 검증
"""

import asyncio
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Tuple
import logging
import psutil
import os
from pathlib import Path
import json
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ProcessingMetrics:
    """처리 성능 메트릭"""
    total_files: int = 0
    processing_time: float = 0.0
    cpu_usage_avg: float = 0.0
    memory_usage_peak: float = 0.0
    thread_count: int = 0
    process_count: int = 0
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = None
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self):
        """모니터링 시작"""
        self.start_time = time.time()
        self.cpu_samples.clear()
        self.memory_samples.clear()
        self.monitoring = True
        
        self._monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitor_thread.start()
        
    def stop_monitoring(self) -> ProcessingMetrics:
        """모니터링 중지 및 결과 반환"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            
        processing_time = time.time() - self.start_time if self.start_time else 0
        cpu_avg = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        memory_peak = max(self.memory_samples) if self.memory_samples else 0
        
        return ProcessingMetrics(
            processing_time=processing_time,
            cpu_usage_avg=cpu_avg,
            memory_usage_peak=memory_peak
        )
        
    def _monitor_resources(self):
        """리소스 모니터링 스레드"""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                # CPU 사용률 샘플링
                cpu_percent = process.cpu_percent()
                self.cpu_samples.append(cpu_percent)
                
                # 메모리 사용률 샘플링
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # MB 단위
                self.memory_samples.append(memory_mb)
                
                time.sleep(0.1)  # 100ms 간격으로 샘플링
                
            except Exception as e:
                logging.warning(f"리소스 모니터링 오류: {e}")
                break


class ParallelProcessor:
    """병렬 처리 최적화 및 검증 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.performance_results = []
        
        # 시스템 리소스 정보
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / 1024 / 1024 / 1024
        
        self.logger.info(f"시스템 리소스: CPU {self.cpu_count}코어, 메모리 {self.memory_gb:.1f}GB")
        
    async def verify_parallel_processing(self, 
                                       test_files: List[str],
                                       parser_func: Callable,
                                       max_workers_list: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        병렬 처리 성능 검증
        
        Args:
            test_files: 테스트할 파일 목록
            parser_func: 파싱 함수
            max_workers_list: 테스트할 워커 수 목록
            
        Returns:
            성능 검증 결과
        """
        
        if max_workers_list is None:
            max_workers_list = [1, 2, 4, 8, 16]
            
        self.logger.info("병렬 처리 성능 검증 시작")
        self.logger.info(f"테스트 파일 수: {len(test_files)}")
        
        verification_results = {
            'system_info': {
                'cpu_count': self.cpu_count,
                'memory_gb': self.memory_gb,
                'test_files_count': len(test_files)
            },
            'performance_tests': [],
            'optimal_workers': 1,
            'recommendations': []
        }
        
        # 다양한 워커 수로 성능 테스트
        for workers in max_workers_list:
            if workers > self.cpu_count * 2:  # 과도한 워커 수 방지
                continue
                
            self.logger.info(f"워커 수 {workers}로 테스트 중...")
            
            # ThreadPoolExecutor 테스트
            thread_result = await self._test_thread_pool(test_files, parser_func, workers)
            thread_result['executor_type'] = 'ThreadPool'
            thread_result['workers'] = workers
            verification_results['performance_tests'].append(thread_result)
            
            # ProcessPoolExecutor 테스트 (CPU 집약적인 경우)
            if workers <= self.cpu_count:
                process_result = await self._test_process_pool(test_files, parser_func, workers)
                process_result['executor_type'] = 'ProcessPool'
                process_result['workers'] = workers
                verification_results['performance_tests'].append(process_result)
                
        # 최적의 워커 수 결정
        optimal_config = self._find_optimal_configuration(verification_results['performance_tests'])
        verification_results['optimal_workers'] = optimal_config['workers']
        verification_results['optimal_executor'] = optimal_config['executor_type']
        
        # 권장사항 생성
        verification_results['recommendations'] = self._generate_recommendations(
            verification_results['performance_tests'], 
            optimal_config
        )
        
        self.logger.info(f"최적 구성: {optimal_config['executor_type']} with {optimal_config['workers']} workers")
        
        return verification_results
        
    async def _test_thread_pool(self, 
                               files: List[str], 
                               parser_func: Callable, 
                               max_workers: int) -> Dict[str, Any]:
        """ThreadPoolExecutor 성능 테스트"""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 파일 처리 태스크 생성
                future_to_file = {
                    executor.submit(self._safe_parse_file, parser_func, file): file 
                    for file in files
                }
                
                # 결과 수집
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result['success']:
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f"{file_path}: {result['error']}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"{file_path}: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"ThreadPool 테스트 오류: {e}")
            errors.append(f"ThreadPool error: {str(e)}")
            
        metrics = monitor.stop_monitoring()
        metrics.total_files = len(files)
        metrics.thread_count = max_workers
        metrics.success_count = success_count
        metrics.error_count = error_count
        metrics.errors = errors[:10]  # 최대 10개 오류만 저장
        
        return self._metrics_to_dict(metrics)
        
    async def _test_process_pool(self, 
                                files: List[str], 
                                parser_func: Callable, 
                                max_workers: int) -> Dict[str, Any]:
        """ProcessPoolExecutor 성능 테스트"""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 파일 처리 태스크 생성
                future_to_file = {
                    executor.submit(self._safe_parse_file, parser_func, file): file 
                    for file in files
                }
                
                # 결과 수집
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result['success']:
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append(f"{file_path}: {result['error']}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"{file_path}: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"ProcessPool 테스트 오류: {e}")
            errors.append(f"ProcessPool error: {str(e)}")
            
        metrics = monitor.stop_monitoring()
        metrics.total_files = len(files)
        metrics.process_count = max_workers
        metrics.success_count = success_count
        metrics.error_count = error_count
        metrics.errors = errors[:10]  # 최대 10개 오류만 저장
        
        return self._metrics_to_dict(metrics)
        
    def _safe_parse_file(self, parser_func: Callable, file_path: str) -> Dict[str, Any]:
        """안전한 파일 파싱 (예외 처리 포함)"""
        try:
            start_time = time.time()
            result = parser_func(file_path)
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'file': file_path,
                'processing_time': processing_time,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'file': file_path,
                'error': str(e)
            }
            
    def _find_optimal_configuration(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """최적의 병렬 처리 구성 찾기"""
        
        best_config = None
        best_score = 0
        
        for result in test_results:
            # 성능 점수 계산 (처리 시간 역수 + 성공률)
            if result['processing_time'] > 0:
                time_score = 1.0 / result['processing_time']
                success_rate = result['success_count'] / result['total_files'] if result['total_files'] > 0 else 0
                
                # CPU 효율성 고려
                cpu_efficiency = 1.0 if result['cpu_usage_avg'] < 80 else 0.5
                
                # 메모리 효율성 고려
                memory_efficiency = 1.0 if result['memory_usage_peak'] < self.memory_gb * 1024 * 0.8 else 0.5
                
                total_score = time_score * success_rate * cpu_efficiency * memory_efficiency
                
                if total_score > best_score:
                    best_score = total_score
                    best_config = {
                        'workers': result['workers'],
                        'executor_type': result['executor_type'],
                        'score': total_score,
                        'processing_time': result['processing_time'],
                        'success_rate': success_rate
                    }
                    
        return best_config or {'workers': 4, 'executor_type': 'ThreadPool', 'score': 0}
        
    def _generate_recommendations(self, 
                                 test_results: List[Dict[str, Any]], 
                                 optimal_config: Dict[str, Any]) -> List[str]:
        """성능 최적화 권장사항 생성"""
        
        recommendations = []
        
        # 시스템 리소스 기반 권장사항
        if self.cpu_count >= 8:
            recommendations.append("다중 코어 시스템: ProcessPool을 고려하여 CPU 집약적 작업 처리")
        else:
            recommendations.append("제한된 코어: ThreadPool로 I/O 병목 최적화 집중")
            
        if self.memory_gb < 8:
            recommendations.append("메모리 부족: 작은 배치 크기와 제한된 워커 수 권장")
        elif self.memory_gb >= 16:
            recommendations.append("충분한 메모리: 대용량 배치 처리 가능")
            
        # 성능 테스트 결과 기반 권장사항
        thread_results = [r for r in test_results if r['executor_type'] == 'ThreadPool']
        process_results = [r for r in test_results if r['executor_type'] == 'ProcessPool']
        
        if thread_results and process_results:
            avg_thread_time = sum(r['processing_time'] for r in thread_results) / len(thread_results)
            avg_process_time = sum(r['processing_time'] for r in process_results) / len(process_results)
            
            if avg_process_time < avg_thread_time * 0.8:
                recommendations.append("ProcessPool이 ThreadPool보다 20% 이상 빠름 - CPU 집약적 작업에 적합")
            elif avg_thread_time < avg_process_time * 0.8:
                recommendations.append("ThreadPool이 ProcessPool보다 20% 이상 빠름 - I/O 집약적 작업에 적합")
                
        # 최적 워커 수 관련 권장사항
        optimal_workers = optimal_config['workers']
        if optimal_workers == 1:
            recommendations.append("단일 워커가 최적 - 파일 크기가 작거나 파싱 오버헤드가 큼")
        elif optimal_workers > self.cpu_count:
            recommendations.append(f"권장 워커 수({optimal_workers})가 CPU 코어({self.cpu_count})보다 많음 - I/O 대기 시간이 긺")
        else:
            recommendations.append(f"CPU 코어 수({self.cpu_count}) 범위 내 최적 워커 수: {optimal_workers}")
            
        return recommendations
        
    def _metrics_to_dict(self, metrics: ProcessingMetrics) -> Dict[str, Any]:
        """ProcessingMetrics를 딕셔너리로 변환"""
        return {
            'total_files': metrics.total_files,
            'processing_time': metrics.processing_time,
            'cpu_usage_avg': metrics.cpu_usage_avg,
            'memory_usage_peak': metrics.memory_usage_peak,
            'thread_count': metrics.thread_count,
            'process_count': metrics.process_count,
            'success_count': metrics.success_count,
            'error_count': metrics.error_count,
            'errors': metrics.errors or []
        }
        
    def optimize_async_processing(self, 
                                 source_files: List[str],
                                 parser_mapping: Dict[str, Callable],
                                 optimal_workers: int = None) -> Dict[str, Any]:
        """
        비동기 처리 최적화
        
        Args:
            source_files: 처리할 소스 파일 목록
            parser_mapping: 파일 확장자별 파서 매핑
            optimal_workers: 최적 워커 수 (None이면 자동 설정)
            
        Returns:
            최적화된 처리 결과
        """
        
        if optimal_workers is None:
            optimal_workers = min(self.cpu_count * 2, len(source_files))
            
        self.logger.info(f"비동기 처리 최적화 시작: {len(source_files)}개 파일, {optimal_workers} 워커")
        
        # 파일 타입별 그룹화
        file_groups = defaultdict(list)
        for file_path in source_files:
            ext = Path(file_path).suffix.lower()
            file_groups[ext].append(file_path)
            
        optimization_results = {
            'total_files': len(source_files),
            'file_groups': {ext: len(files) for ext, files in file_groups.items()},
            'processing_results': {},
            'total_processing_time': 0,
            'optimization_applied': []
        }
        
        start_time = time.time()
        
        # 파일 타입별 최적화된 병렬 처리
        for ext, files in file_groups.items():
            if ext in parser_mapping:
                parser_func = parser_mapping[ext]
                
                # 파일 수에 따른 워커 수 조정
                adjusted_workers = min(optimal_workers, len(files))
                
                self.logger.info(f"{ext} 파일 {len(files)}개 처리 중 (워커: {adjusted_workers})")
                
                group_start_time = time.time()
                
                # 배치 크기 최적화
                batch_size = max(1, len(files) // adjusted_workers)
                if batch_size > 50:  # 배치가 너무 크면 메모리 사용량 제한
                    batch_size = 50
                    optimization_results['optimization_applied'].append(f"{ext}: 배치 크기 제한 적용 (50)")
                    
                # 청크 단위 처리로 메모리 사용량 최적화
                processed_files = 0
                for i in range(0, len(files), batch_size * adjusted_workers):
                    batch_files = files[i:i + batch_size * adjusted_workers]
                    
                    # 배치 내 병렬 처리
                    with ThreadPoolExecutor(max_workers=adjusted_workers) as executor:
                        futures = [
                            executor.submit(self._safe_parse_file, parser_func, file)
                            for file in batch_files
                        ]
                        
                        batch_results = []
                        for future in as_completed(futures):
                            result = future.result()
                            batch_results.append(result)
                            processed_files += 1
                            
                            # 진행률 로깅 (매 100파일마다)
                            if processed_files % 100 == 0:
                                self.logger.info(f"{ext} 진행률: {processed_files}/{len(files)}")
                                
                group_processing_time = time.time() - group_start_time
                optimization_results['processing_results'][ext] = {
                    'files_processed': len(files),
                    'processing_time': group_processing_time,
                    'workers_used': adjusted_workers,
                    'batch_size': batch_size
                }
                
        optimization_results['total_processing_time'] = time.time() - start_time
        
        # 최적화 적용 사항 요약
        if not optimization_results['optimization_applied']:
            optimization_results['optimization_applied'].append("기본 병렬 처리 최적화 적용")
            
        self.logger.info(f"비동기 처리 완료: 총 {optimization_results['total_processing_time']:.2f}초")
        
        return optimization_results
        
    def save_performance_report(self, results: Dict[str, Any], output_path: str):
        """성능 검증 결과 리포트 저장"""
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': results.get('system_info', {}),
            'performance_verification': results,
            'summary': {
                'optimal_configuration': {
                    'workers': results.get('optimal_workers', 4),
                    'executor_type': results.get('optimal_executor', 'ThreadPool')
                },
                'recommendations': results.get('recommendations', [])
            }
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"성능 리포트 저장됨: {output_path}")


# 테스트용 파서 함수들
def dummy_java_parser(file_path: str) -> Dict[str, Any]:
    """테스트용 Java 파서"""
    time.sleep(0.01)  # 파싱 시간 시뮬레이션
    return {
        'file_type': 'java',
        'classes': 2,
        'methods': 5,
        'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }
    

def dummy_jsp_parser(file_path: str) -> Dict[str, Any]:
    """테스트용 JSP 파서"""
    time.sleep(0.02)  # 파싱 시간 시뮬레이션
    return {
        'file_type': 'jsp',
        'scriptlets': 3,
        'includes': 1,
        'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }


def dummy_xml_parser(file_path: str) -> Dict[str, Any]:
    """테스트용 XML 파서"""
    time.sleep(0.015)  # 파싱 시간 시뮬레이션
    return {
        'file_type': 'xml',
        'sql_statements': 4,
        'mappers': 1,
        'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }