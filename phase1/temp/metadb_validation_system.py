"""
Context7 기반 메타DB 검증 시스템
자동 생성 메타정보와 수작업 분석 결과를 비교하여 정확도를 검증하는 시스템
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import logging

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from phase1.models.database import DatabaseManager
from phase1.parsers.parser_factory import ParserFactory

class MetaDBValidationSystem:
    """
    Context7 기반 메타DB 검증 시스템
    - 자동 생성 메타정보와 수작업 분석 결과 비교
    - 정확도 차이 분석 및 원인 파악
    - 5% 이내 오차 달성을 위한 반복 개선 프로세스
    """
    
    def __init__(self, project_name: str, config: Dict[str, Any]):
        self.project_name = project_name
        self.config = config
        self.logger = self._setup_logging()
        
        # 메타DB 경로
        self.metadb_path = f"./project/{project_name}/metadata.db"
        
        # 수작업 분석 결과 파일 경로
        self.manual_analysis_path = "Dev.Report/파일별 메소드, 쿼리 개수 조사 결과.md"
        
        # 검증 결과 저장 경로
        self.validation_results_path = f"./project/{project_name}/report"
        
        # 정확도 임계값 (5%)
        self.accuracy_threshold = 0.05
        
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def validate_metadb_accuracy(self) -> Dict[str, Any]:
        """
        메타DB 정확도 검증 메인 함수
        
        Returns:
            검증 결과 딕셔너리
        """
        self.logger.info("Context7 기반 메타DB 정확도 검증 시작")
        
        try:
            # 1. 수작업 분석 결과 로드
            manual_results = self._load_manual_analysis()
            
            # 2. 메타DB에서 자동 생성된 결과 로드
            metadb_results = self._load_metadb_results()
            
            # 3. 정확도 비교 및 차이 분석
            accuracy_comparison = self._compare_accuracy(manual_results, metadb_results)
            
            # 4. 5% 이상 차이 발생 시 원인 분석
            if accuracy_comparison['overall_accuracy_gap'] > self.accuracy_threshold:
                self.logger.warning(f"정확도 차이가 임계값({self.accuracy_threshold*100}%) 초과: {accuracy_comparison['overall_accuracy_gap']*100:.2f}%")
                gap_analysis = self._analyze_accuracy_gap(manual_results, metadb_results)
                accuracy_comparison['gap_analysis'] = gap_analysis
                
                # 5. 개선 제안 생성
                improvement_suggestions = self._generate_improvement_suggestions(gap_analysis)
                accuracy_comparison['improvement_suggestions'] = improvement_suggestions
            else:
                self.logger.info(f"정확도 차이가 임계값({self.accuracy_threshold*100}%) 이내: {accuracy_comparison['overall_accuracy_gap']*100:.2f}%")
            
            # 6. 검증 결과 저장
            self._save_validation_results(accuracy_comparison)
            
            return accuracy_comparison
            
        except Exception as e:
            self.logger.error(f"메타DB 검증 중 오류 발생: {e}")
            raise
    
    def _load_manual_analysis(self) -> Dict[str, Any]:
        """수작업 분석 결과 로드"""
        self.logger.info("수작업 분석 결과 로드 중...")
        
        if not os.path.exists(self.manual_analysis_path):
            raise FileNotFoundError(f"수작업 분석 결과 파일을 찾을 수 없습니다: {self.manual_analysis_path}")
        
        with open(self.manual_analysis_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 수작업 분석 결과 파싱
        manual_results = self._parse_manual_analysis(content)
        
        self.logger.info(f"수작업 분석 결과 로드 완료: {len(manual_results)}개 파일")
        return manual_results
    
    def _parse_manual_analysis(self, content: str) -> Dict[str, Any]:
        """수작업 분석 결과 파싱"""
        manual_results = {}
        
        # 파일별 분석 결과 추출
        lines = content.split('\n')
        current_file = None
        
        for line in lines:
            line = line.strip()
            
            # 파일명 패턴 매칭
            if line.startswith('## ') and not line.startswith('### '):
                current_file = line.replace('## ', '').strip()
                manual_results[current_file] = {
                    'methods': 0,
                    'queries': 0,
                    'classes': 0,
                    'functions': 0,
                    'details': []
                }
            
            # 메소드/쿼리 개수 추출
            elif current_file and ('메소드' in line or '쿼리' in line or '함수' in line):
                if '메소드' in line:
                    # 메소드 개수 추출
                    import re
                    method_match = re.search(r'(\d+)\s*개', line)
                    if method_match:
                        manual_results[current_file]['methods'] = int(method_match.group(1))
                
                if '쿼리' in line:
                    # 쿼리 개수 추출
                    query_match = re.search(r'(\d+)\s*개', line)
                    if query_match:
                        manual_results[current_file]['queries'] = int(query_match.group(1))
                
                if '함수' in line:
                    # 함수 개수 추출
                    function_match = re.search(r'(\d+)\s*개', line)
                    if function_match:
                        manual_results[current_file]['functions'] = int(function_match.group(1))
        
        return manual_results
    
    def _load_metadb_results(self) -> Dict[str, Any]:
        """메타DB에서 자동 생성된 결과 로드"""
        self.logger.info("메타DB 결과 로드 중...")
        
        if not os.path.exists(self.metadb_path):
            raise FileNotFoundError(f"메타DB 파일을 찾을 수 없습니다: {self.metadb_path}")
        
        metadb_results = {}
        
        # SQLite 연결
        conn = sqlite3.connect(self.metadb_path)
        cursor = conn.cursor()
        
        try:
            # 파일별 메소드 개수 조회
            cursor.execute("""
                SELECT f.file_path, COUNT(m.id) as method_count
                FROM files f
                LEFT JOIN methods m ON f.id = m.file_id
                GROUP BY f.id, f.file_path
            """)
            
            for row in cursor.fetchall():
                file_path = row[0]
                method_count = row[1] or 0
                
                if file_path not in metadb_results:
                    metadb_results[file_path] = {
                        'methods': 0,
                        'queries': 0,
                        'classes': 0,
                        'functions': 0
                    }
                
                metadb_results[file_path]['methods'] = method_count
            
            # 파일별 쿼리 개수 조회
            cursor.execute("""
                SELECT f.file_path, COUNT(sq.id) as query_count
                FROM files f
                LEFT JOIN sql_units sq ON f.id = sq.file_id
                GROUP BY f.id, f.file_path
            """)
            
            for row in cursor.fetchall():
                file_path = row[0]
                query_count = row[1] or 0
                
                if file_path not in metadb_results:
                    metadb_results[file_path] = {
                        'methods': 0,
                        'queries': 0,
                        'classes': 0,
                        'functions': 0
                    }
                
                metadb_results[file_path]['queries'] = query_count
            
            # 파일별 클래스 개수 조회
            cursor.execute("""
                SELECT f.file_path, COUNT(c.id) as class_count
                FROM files f
                LEFT JOIN classes c ON f.id = c.file_id
                GROUP BY f.id, f.file_path
            """)
            
            for row in cursor.fetchall():
                file_path = row[0]
                class_count = row[1] or 0
                
                if file_path not in metadb_results:
                    metadb_results[file_path] = {
                        'methods': 0,
                        'queries': 0,
                        'classes': 0,
                        'functions': 0
                    }
                
                metadb_results[file_path]['classes'] = class_count
            
        finally:
            conn.close()
        
        self.logger.info(f"메타DB 결과 로드 완료: {len(metadb_results)}개 파일")
        return metadb_results
    
    def _compare_accuracy(self, manual_results: Dict[str, Any], metadb_results: Dict[str, Any]) -> Dict[str, Any]:
        """정확도 비교 및 차이 분석"""
        self.logger.info("정확도 비교 분석 중...")
        
        comparison_results = {
            'file_comparisons': {},
            'overall_accuracy_gap': 0.0,
            'summary': {
                'total_files': 0,
                'accurate_files': 0,
                'inaccurate_files': 0,
                'method_accuracy': 0.0,
                'query_accuracy': 0.0,
                'class_accuracy': 0.0,
                'function_accuracy': 0.0
            }
        }
        
        total_method_diff = 0
        total_query_diff = 0
        total_class_diff = 0
        total_function_diff = 0
        total_files = 0
        
        # 파일별 비교
        for file_path, manual_data in manual_results.items():
            # 파일 경로 정규화
            normalized_path = self._normalize_file_path(file_path)
            
            # 메타DB에서 해당 파일 찾기
            metadb_data = None
            for metadb_path, metadb_info in metadb_results.items():
                if self._is_same_file(normalized_path, metadb_path):
                    metadb_data = metadb_info
                    break
            
            if metadb_data is None:
                self.logger.warning(f"메타DB에서 파일을 찾을 수 없습니다: {file_path}")
                continue
            
            # 개수 비교
            method_diff = abs(manual_data['methods'] - metadb_data['methods'])
            query_diff = abs(manual_data['queries'] - metadb_data['queries'])
            class_diff = abs(manual_data['classes'] - metadb_data['classes'])
            function_diff = abs(manual_data['functions'] - metadb_data['functions'])
            
            # 정확도 계산
            method_accuracy = 1.0 - (method_diff / max(manual_data['methods'], 1))
            query_accuracy = 1.0 - (query_diff / max(manual_data['queries'], 1))
            class_accuracy = 1.0 - (class_diff / max(manual_data['classes'], 1))
            function_accuracy = 1.0 - (function_diff / max(manual_data['functions'], 1))
            
            comparison_results['file_comparisons'][file_path] = {
                'manual': manual_data,
                'metadb': metadb_data,
                'differences': {
                    'methods': method_diff,
                    'queries': query_diff,
                    'classes': class_diff,
                    'functions': function_diff
                },
                'accuracy': {
                    'methods': method_accuracy,
                    'queries': query_accuracy,
                    'classes': class_accuracy,
                    'functions': function_accuracy
                }
            }
            
            total_method_diff += method_diff
            total_query_diff += query_diff
            total_class_diff += class_diff
            total_function_diff += function_diff
            total_files += 1
        
        # 전체 정확도 계산
        if total_files > 0:
            total_manual_methods = sum(data['methods'] for data in manual_results.values())
            total_manual_queries = sum(data['queries'] for data in manual_results.values())
            total_manual_classes = sum(data['classes'] for data in manual_results.values())
            total_manual_functions = sum(data['functions'] for data in manual_results.values())
            
            comparison_results['summary']['method_accuracy'] = 1.0 - (total_method_diff / max(total_manual_methods, 1))
            comparison_results['summary']['query_accuracy'] = 1.0 - (total_query_diff / max(total_manual_queries, 1))
            comparison_results['summary']['class_accuracy'] = 1.0 - (total_class_diff / max(total_manual_classes, 1))
            comparison_results['summary']['function_accuracy'] = 1.0 - (total_function_diff / max(total_manual_functions, 1))
            
            # 전체 정확도 갭 계산
            overall_accuracy = (
                comparison_results['summary']['method_accuracy'] +
                comparison_results['summary']['query_accuracy'] +
                comparison_results['summary']['class_accuracy'] +
                comparison_results['summary']['function_accuracy']
            ) / 4
            
            comparison_results['overall_accuracy_gap'] = 1.0 - overall_accuracy
        
        comparison_results['summary']['total_files'] = total_files
        comparison_results['summary']['accurate_files'] = sum(
            1 for comp in comparison_results['file_comparisons'].values()
            if all(acc >= 0.95 for acc in comp['accuracy'].values())
        )
        comparison_results['summary']['inaccurate_files'] = total_files - comparison_results['summary']['accurate_files']
        
        self.logger.info(f"정확도 비교 완료: 전체 정확도 갭 {comparison_results['overall_accuracy_gap']*100:.2f}%")
        return comparison_results
    
    def _normalize_file_path(self, file_path: str) -> str:
        """파일 경로 정규화"""
        # 상대 경로로 변환
        normalized = file_path.replace('\\', '/')
        if normalized.startswith('./'):
            normalized = normalized[2:]
        return normalized
    
    def _is_same_file(self, path1: str, path2: str) -> bool:
        """두 파일 경로가 같은 파일을 가리키는지 확인"""
        # 파일명만 비교 (경로 구조가 다를 수 있음)
        filename1 = os.path.basename(path1)
        filename2 = os.path.basename(path2)
        return filename1 == filename2
    
    def _analyze_accuracy_gap(self, manual_results: Dict[str, Any], metadb_results: Dict[str, Any]) -> Dict[str, Any]:
        """정확도 차이 원인 분석"""
        self.logger.info("정확도 차이 원인 분석 중...")
        
        gap_analysis = {
            'common_issues': [],
            'file_specific_issues': {},
            'parser_issues': [],
            'recommendations': []
        }
        
        # 공통 문제점 분석
        method_under_count = 0
        method_over_count = 0
        query_under_count = 0
        query_over_count = 0
        
        for file_path, manual_data in manual_results.items():
            normalized_path = self._normalize_file_path(file_path)
            
            metadb_data = None
            for metadb_path, metadb_info in metadb_results.items():
                if self._is_same_file(normalized_path, metadb_path):
                    metadb_data = metadb_info
                    break
            
            if metadb_data is None:
                continue
            
            # 메소드 개수 차이 분석
            method_diff = metadb_data['methods'] - manual_data['methods']
            if method_diff < 0:
                method_under_count += 1
            elif method_diff > 0:
                method_over_count += 1
            
            # 쿼리 개수 차이 분석
            query_diff = metadb_data['queries'] - manual_data['queries']
            if query_diff < 0:
                query_under_count += 1
            elif query_diff > 0:
                query_over_count += 1
        
        # 공통 문제점 식별
        if method_under_count > len(manual_results) * 0.3:
            gap_analysis['common_issues'].append("메소드 추출 부족 - 파서가 일부 메소드를 놓치고 있음")
        
        if method_over_count > len(manual_results) * 0.3:
            gap_analysis['common_issues'].append("메소드 과추출 - 파서가 메소드가 아닌 것을 메소드로 인식")
        
        if query_under_count > len(manual_results) * 0.3:
            gap_analysis['common_issues'].append("쿼리 추출 부족 - SQL 파싱 정확도 개선 필요")
        
        if query_over_count > len(manual_results) * 0.3:
            gap_analysis['common_issues'].append("쿼리 과추출 - SQL 문자열 인식 정확도 개선 필요")
        
        # 파서별 문제점 분석
        gap_analysis['parser_issues'] = [
            "Context7 PRegEx 패턴 최적화 필요",
            "다이나믹 쿼리 파싱 정확도 개선",
            "중복 제거 로직 강화",
            "파일 타입별 파싱 전략 개선"
        ]
        
        # 개선 권장사항
        gap_analysis['recommendations'] = [
            "Context7 PRegEx 패턴을 더 정확하게 조정",
            "파일별 파싱 결과를 수동으로 검증하여 패턴 개선",
            "중복 제거 로직을 강화하여 과추출 방지",
            "다이나믹 쿼리 파싱 정확도 향상"
        ]
        
        return gap_analysis
    
    def _generate_improvement_suggestions(self, gap_analysis: Dict[str, Any]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        for issue in gap_analysis['common_issues']:
            if "메소드 추출 부족" in issue:
                suggestions.append("Java 파서의 메소드 시그니처 패턴을 더 포괄적으로 개선")
            elif "메소드 과추출" in issue:
                suggestions.append("Java 파서의 메소드 인식 정확도를 높이기 위해 패턴을 더 엄격하게 조정")
            elif "쿼리 추출 부족" in issue:
                suggestions.append("SQL 파서의 쿼리 인식 패턴을 개선하고 다이나믹 쿼리 처리 강화")
            elif "쿼리 과추출" in issue:
                suggestions.append("SQL 문자열 인식 정확도를 높이기 위해 컨텍스트 분석 강화")
        
        for parser_issue in gap_analysis['parser_issues']:
            suggestions.append(f"파서 개선: {parser_issue}")
        
        return suggestions
    
    def _save_validation_results(self, results: Dict[str, Any]):
        """검증 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"{self.validation_results_path}/metadb_validation_{timestamp}.json"
        
        # 결과 디렉토리 생성
        os.makedirs(self.validation_results_path, exist_ok=True)
        
        # JSON으로 저장
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 마크다운 리포트도 생성
        report_file = f"{self.validation_results_path}/metadb_validation_report_{timestamp}.md"
        self._generate_validation_report(results, report_file)
        
        self.logger.info(f"검증 결과 저장 완료: {results_file}")
        self.logger.info(f"검증 리포트 생성 완료: {report_file}")
    
    def _generate_validation_report(self, results: Dict[str, Any], report_file: str):
        """검증 리포트 생성"""
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Context7 기반 메타DB 검증 리포트\n\n")
            f.write(f"**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**프로젝트**: {self.project_name}\n\n")
            
            # 전체 요약
            summary = results['summary']
            f.write("## 전체 요약\n\n")
            f.write(f"- **전체 파일 수**: {summary['total_files']}\n")
            f.write(f"- **정확한 파일 수**: {summary['accurate_files']}\n")
            f.write(f"- **부정확한 파일 수**: {summary['inaccurate_files']}\n")
            f.write(f"- **전체 정확도 갭**: {results['overall_accuracy_gap']*100:.2f}%\n\n")
            
            # 구성요소별 정확도
            f.write("## 구성요소별 정확도\n\n")
            f.write(f"- **메소드 정확도**: {summary['method_accuracy']*100:.2f}%\n")
            f.write(f"- **쿼리 정확도**: {summary['query_accuracy']*100:.2f}%\n")
            f.write(f"- **클래스 정확도**: {summary['class_accuracy']*100:.2f}%\n")
            f.write(f"- **함수 정확도**: {summary['function_accuracy']*100:.2f}%\n\n")
            
            # 정확도 차이 분석
            if 'gap_analysis' in results:
                gap_analysis = results['gap_analysis']
                f.write("## 정확도 차이 분석\n\n")
                
                f.write("### 공통 문제점\n")
                for issue in gap_analysis['common_issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")
                
                f.write("### 파서 문제점\n")
                for issue in gap_analysis['parser_issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")
                
                f.write("### 개선 권장사항\n")
                for rec in gap_analysis['recommendations']:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            # 개선 제안
            if 'improvement_suggestions' in results:
                f.write("## 개선 제안\n\n")
                for suggestion in results['improvement_suggestions']:
                    f.write(f"- {suggestion}\n")
                f.write("\n")
            
            # 파일별 상세 결과
            f.write("## 파일별 상세 결과\n\n")
            for file_path, comparison in results['file_comparisons'].items():
                f.write(f"### {file_path}\n\n")
                f.write(f"**수작업 분석**: 메소드 {comparison['manual']['methods']}개, 쿼리 {comparison['manual']['queries']}개\n")
                f.write(f"**메타DB 결과**: 메소드 {comparison['metadb']['methods']}개, 쿼리 {comparison['metadb']['queries']}개\n")
                f.write(f"**차이**: 메소드 {comparison['differences']['methods']}개, 쿼리 {comparison['differences']['queries']}개\n")
                f.write(f"**정확도**: 메소드 {comparison['accuracy']['methods']*100:.2f}%, 쿼리 {comparison['accuracy']['queries']*100:.2f}%\n\n")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Context7 기반 메타DB 검증 시스템')
    parser.add_argument('--project-name', required=True, help='프로젝트 이름')
    parser.add_argument('--config', default='./phase1/config/config.yaml', help='설정 파일 경로')
    
    args = parser.parse_args()
    
    # 설정 로드
    import yaml
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 검증 시스템 실행
    validation_system = MetaDBValidationSystem(args.project_name, config)
    results = validation_system.validate_metadb_accuracy()
    
    print(f"검증 완료: 전체 정확도 갭 {results['overall_accuracy_gap']*100:.2f}%")
    
    if results['overall_accuracy_gap'] > 0.05:
        print("⚠️  정확도 차이가 5%를 초과합니다. 개선이 필요합니다.")
        if 'improvement_suggestions' in results:
            print("\n개선 제안:")
            for suggestion in results['improvement_suggestions']:
                print(f"- {suggestion}")
    else:
        print("✅ 정확도 차이가 5% 이내입니다. 목표 달성!")


if __name__ == "__main__":
    main()





