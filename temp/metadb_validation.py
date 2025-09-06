#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메타DB 정확도 검증 스크립트
Context7 파서로 생성된 메타정보와 수작업 분석 결과를 비교하여 정확도를 검증합니다.
"""

import os
import sys
import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class MetaDBValidator:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.metadb_path = f"../project/{project_name}/metadata.db"
        self.manual_report_path = "../Dev.Report/Dev.Report/파일별 메소드, 쿼리 개수 조사 결과.md"
        self.src_path = f"../project/{project_name}/src"
        
        # 수작업 분석 결과 저장
        self.manual_results = {}
        # 메타DB 결과 저장
        self.metadb_results = {}
        # 실제 소스코드 검증 결과 저장
        self.source_verification = {}
        
    def load_manual_analysis(self) -> Dict[str, Any]:
        """수작업 분석 결과를 로드합니다."""
        print("수작업 분석 결과 로딩 중...")
        
        if not os.path.exists(self.manual_report_path):
            print(f"수작업 분석 결과 파일이 없습니다: {self.manual_report_path}")
            return {}
            
        with open(self.manual_report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 파일별 메소드, 쿼리 개수 추출
        manual_data = {}
        
        # 파일별 결과 섹션 찾기
        file_section_match = re.search(r'## 파일별 분석 결과.*?(?=##|$)', content, re.DOTALL)
        if file_section_match:
            file_section = file_section_match.group(0)
            
            # 각 파일별 결과 추출
            file_pattern = r'### (.+?)\n.*?메소드: (\d+)개.*?쿼리: (\d+)개'
            matches = re.findall(file_pattern, file_section, re.DOTALL)
            
            for file_path, method_count, query_count in matches:
                manual_data[file_path.strip()] = {
                    'methods': int(method_count),
                    'queries': int(query_count)
                }
        
        # 요약 통계 추출
        summary_match = re.search(r'## 요약.*?Java 파일: (\d+)개.*?메소드: (\d+)개.*?쿼리: (\d+)개', content, re.DOTALL)
        if summary_match:
            java_files, total_methods, total_queries = summary_match.groups()
            manual_data['_summary'] = {
                'java_files': int(java_files),
                'total_methods': int(total_methods),
                'total_queries': int(total_queries)
            }
            
        self.manual_results = manual_data
        print(f"수작업 분석 결과 로딩 완료: {len(manual_data)}개 항목")
        return manual_data
    
    def load_metadb_analysis(self) -> Dict[str, Any]:
        """메타DB에서 분석 결과를 로드합니다."""
        print("메타DB 분석 결과 로딩 중...")
        
        if not os.path.exists(self.metadb_path):
            print(f"메타DB 파일이 없습니다: {self.metadb_path}")
            return {}
            
        metadb_data = {}
        
        try:
            conn = sqlite3.connect(self.metadb_path)
            cursor = conn.cursor()
            
            # 파일별 메소드 개수 조회
            cursor.execute("""
                SELECT f.path, COUNT(s.sql_id) as method_count
                FROM files f
                LEFT JOIN sql_units s ON f.file_id = s.file_id
                WHERE f.language = 'java'
                GROUP BY f.file_id, f.path
            """)
            
            java_methods = cursor.fetchall()
            
            # 파일별 쿼리 개수 조회
            cursor.execute("""
                SELECT f.path, COUNT(s.sql_id) as query_count
                FROM files f
                LEFT JOIN sql_units s ON f.file_id = s.file_id
                WHERE s.stmt_kind IS NOT NULL
                GROUP BY f.file_id, f.path
            """)
            
            java_queries = cursor.fetchall()
            
            # 파일별 데이터 통합
            for file_path, method_count in java_methods:
                if file_path not in metadb_data:
                    metadb_data[file_path] = {'methods': 0, 'queries': 0}
                metadb_data[file_path]['methods'] = method_count
                
            for file_path, query_count in java_queries:
                if file_path not in metadb_data:
                    metadb_data[file_path] = {'methods': 0, 'queries': 0}
                metadb_data[file_path]['queries'] = query_count
            
            # 전체 통계 조회
            cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
            total_java_files = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sql_units WHERE file_id IN (SELECT file_id FROM files WHERE language = 'java')")
            total_methods = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sql_units WHERE stmt_kind IS NOT NULL")
            total_queries = cursor.fetchone()[0]
            
            metadb_data['_summary'] = {
                'java_files': total_java_files,
                'total_methods': total_methods,
                'total_queries': total_queries
            }
            
            conn.close()
            
        except Exception as e:
            print(f"메타DB 조회 중 오류 발생: {e}")
            return {}
            
        self.metadb_results = metadb_data
        print(f"메타DB 분석 결과 로딩 완료: {len(metadb_data)}개 항목")
        return metadb_data
    
    def verify_source_code(self) -> Dict[str, Any]:
        """실제 소스코드를 직접 검증합니다."""
        print("실제 소스코드 검증 중...")
        
        if not os.path.exists(self.src_path):
            print(f"소스코드 경로가 없습니다: {self.src_path}")
            return {}
            
        source_data = {}
        
        # Java 파일들 검색
        java_files = []
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        total_methods = 0
        total_queries = 0
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 메소드 개수 계산 (간단한 패턴 매칭)
                method_pattern = r'(public|private|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{'
                methods = re.findall(method_pattern, content)
                method_count = len(methods)
                
                # 쿼리 개수 계산 (SQL 문자열 패턴)
                query_patterns = [
                    r'"[^"]*SELECT[^"]*"',
                    r'"[^"]*INSERT[^"]*"',
                    r'"[^"]*UPDATE[^"]*"',
                    r'"[^"]*DELETE[^"]*"',
                    r"'[^']*SELECT[^']*'",
                    r"'[^']*INSERT[^']*'",
                    r"'[^']*UPDATE[^']*'",
                    r"'[^']*DELETE[^']*'"
                ]
                
                query_count = 0
                for pattern in query_patterns:
                    queries = re.findall(pattern, content, re.IGNORECASE)
                    query_count += len(queries)
                
                # 상대 경로로 변환
                rel_path = os.path.relpath(java_file, self.src_path)
                source_data[rel_path] = {
                    'methods': method_count,
                    'queries': query_count
                }
                
                total_methods += method_count
                total_queries += query_count
                
            except Exception as e:
                print(f"파일 분석 중 오류 발생 {java_file}: {e}")
                continue
        
        source_data['_summary'] = {
            'java_files': len(java_files),
            'total_methods': total_methods,
            'total_queries': total_queries
        }
        
        self.source_verification = source_data
        print(f"실제 소스코드 검증 완료: {len(source_data)}개 항목")
        return source_data
    
    def compare_results(self) -> Dict[str, Any]:
        """수작업, 메타DB, 실제 소스코드 결과를 비교합니다."""
        print("결과 비교 분석 중...")
        
        comparison = {
            'file_comparison': {},
            'summary_comparison': {},
            'accuracy_analysis': {},
            'discrepancies': []
        }
        
        # 파일별 비교
        all_files = set()
        all_files.update(self.manual_results.keys())
        all_files.update(self.metadb_results.keys())
        all_files.update(self.source_verification.keys())
        all_files.discard('_summary')  # 요약 제외
        
        for file_path in all_files:
            manual = self.manual_results.get(file_path, {'methods': 0, 'queries': 0})
            metadb = self.metadb_results.get(file_path, {'methods': 0, 'queries': 0})
            source = self.source_verification.get(file_path, {'methods': 0, 'queries': 0})
            
            comparison['file_comparison'][file_path] = {
                'manual': manual,
                'metadb': metadb,
                'source': source,
                'method_diff_manual_metadb': manual['methods'] - metadb['methods'],
                'query_diff_manual_metadb': manual['queries'] - metadb['queries'],
                'method_diff_manual_source': manual['methods'] - source['methods'],
                'query_diff_manual_source': manual['queries'] - source['queries'],
                'method_diff_metadb_source': metadb['methods'] - source['methods'],
                'query_diff_metadb_source': metadb['queries'] - source['queries']
            }
            
            # 5% 이상 차이 발생 시 불일치로 기록
            if source['methods'] > 0:
                method_accuracy_manual = abs(manual['methods'] - source['methods']) / source['methods'] * 100
                method_accuracy_metadb = abs(metadb['methods'] - source['methods']) / source['methods'] * 100
                
                if method_accuracy_manual > 5 or method_accuracy_metadb > 5:
                    comparison['discrepancies'].append({
                        'file': file_path,
                        'type': 'method',
                        'manual_accuracy': method_accuracy_manual,
                        'metadb_accuracy': method_accuracy_metadb,
                        'source_count': source['methods']
                    })
            
            if source['queries'] > 0:
                query_accuracy_manual = abs(manual['queries'] - source['queries']) / source['queries'] * 100
                query_accuracy_metadb = abs(metadb['queries'] - source['queries']) / source['queries'] * 100
                
                if query_accuracy_manual > 5 or query_accuracy_metadb > 5:
                    comparison['discrepancies'].append({
                        'file': file_path,
                        'type': 'query',
                        'manual_accuracy': query_accuracy_manual,
                        'metadb_accuracy': query_accuracy_metadb,
                        'source_count': source['queries']
                    })
        
        # 요약 비교
        manual_summary = self.manual_results.get('_summary', {})
        metadb_summary = self.metadb_results.get('_summary', {})
        source_summary = self.source_verification.get('_summary', {})
        
        comparison['summary_comparison'] = {
            'manual': manual_summary,
            'metadb': metadb_summary,
            'source': source_summary
        }
        
        # 정확도 분석
        if source_summary.get('total_methods', 0) > 0:
            method_accuracy_manual = abs(manual_summary.get('total_methods', 0) - source_summary['total_methods']) / source_summary['total_methods'] * 100
            method_accuracy_metadb = abs(metadb_summary.get('total_methods', 0) - source_summary['total_methods']) / source_summary['total_methods'] * 100
        else:
            method_accuracy_manual = method_accuracy_metadb = 0
            
        if source_summary.get('total_queries', 0) > 0:
            query_accuracy_manual = abs(manual_summary.get('total_queries', 0) - source_summary['total_queries']) / source_summary['total_queries'] * 100
            query_accuracy_metadb = abs(metadb_summary.get('total_queries', 0) - source_summary['total_queries']) / source_summary['total_queries'] * 100
        else:
            query_accuracy_manual = query_accuracy_metadb = 0
        
        comparison['accuracy_analysis'] = {
            'method_accuracy_manual': method_accuracy_manual,
            'method_accuracy_metadb': method_accuracy_metadb,
            'query_accuracy_manual': query_accuracy_manual,
            'query_accuracy_metadb': query_accuracy_metadb,
            'overall_accuracy_manual': (method_accuracy_manual + query_accuracy_manual) / 2,
            'overall_accuracy_metadb': (method_accuracy_metadb + query_accuracy_metadb) / 2
        }
        
        return comparison
    
    def generate_report(self, comparison: Dict[str, Any]) -> str:
        """검증 결과 리포트를 생성합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"../Dev.Report/Dev.Report/메타DB_정확도_검증_결과_{timestamp}.md"
        
        report_content = f"""# 메타DB 정확도 검증 결과

## 검증 개요
- **검증 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **프로젝트**: {self.project_name}
- **검증 대상**: 수작업 분석 vs 메타DB vs 실제 소스코드

## 요약 비교

### 전체 통계
| 구분 | 수작업 | 메타DB | 실제소스 | 수작업 정확도 | 메타DB 정확도 |
|------|--------|--------|----------|---------------|---------------|
| Java 파일 | {comparison['summary_comparison']['manual'].get('java_files', 0)} | {comparison['summary_comparison']['metadb'].get('java_files', 0)} | {comparison['summary_comparison']['source'].get('java_files', 0)} | - | - |
| 총 메소드 | {comparison['summary_comparison']['manual'].get('total_methods', 0)} | {comparison['summary_comparison']['metadb'].get('total_methods', 0)} | {comparison['summary_comparison']['source'].get('total_methods', 0)} | {comparison['accuracy_analysis']['method_accuracy_manual']:.2f}% | {comparison['accuracy_analysis']['method_accuracy_metadb']:.2f}% |
| 총 쿼리 | {comparison['summary_comparison']['manual'].get('total_queries', 0)} | {comparison['summary_comparison']['metadb'].get('total_queries', 0)} | {comparison['summary_comparison']['source'].get('total_queries', 0)} | {comparison['accuracy_analysis']['query_accuracy_manual']:.2f}% | {comparison['accuracy_analysis']['query_accuracy_metadb']:.2f}% |

### 전체 정확도
- **수작업 분석 전체 정확도**: {comparison['accuracy_analysis']['overall_accuracy_manual']:.2f}%
- **메타DB 전체 정확도**: {comparison['accuracy_analysis']['overall_accuracy_metadb']:.2f}%

## 5% 이상 차이 발생 파일

"""
        
        if comparison['discrepancies']:
            report_content += "| 파일 | 타입 | 수작업 정확도 | 메타DB 정확도 | 실제 개수 |\n"
            report_content += "|------|------|---------------|---------------|----------|\n"
            
            for disc in comparison['discrepancies']:
                report_content += f"| {disc['file']} | {disc['type']} | {disc['manual_accuracy']:.2f}% | {disc['metadb_accuracy']:.2f}% | {disc['source_count']} |\n"
        else:
            report_content += "5% 이상 차이가 발생한 파일이 없습니다.\n"
        
        report_content += f"""

## 파일별 상세 비교

"""
        
        # 파일별 비교 결과 (상위 10개만 표시)
        file_comparisons = list(comparison['file_comparison'].items())[:10]
        
        for file_path, data in file_comparisons:
            report_content += f"""
### {file_path}
- **수작업**: 메소드 {data['manual']['methods']}개, 쿼리 {data['manual']['queries']}개
- **메타DB**: 메소드 {data['metadb']['methods']}개, 쿼리 {data['metadb']['queries']}개  
- **실제소스**: 메소드 {data['source']['methods']}개, 쿼리 {data['source']['queries']}개
- **차이 (수작업-메타DB)**: 메소드 {data['method_diff_manual_metadb']:+d}개, 쿼리 {data['query_diff_manual_metadb']:+d}개
- **차이 (수작업-실제)**: 메소드 {data['method_diff_manual_source']:+d}개, 쿼리 {data['query_diff_manual_source']:+d}개
- **차이 (메타DB-실제)**: 메소드 {data['method_diff_metadb_source']:+d}개, 쿼리 {data['query_diff_metadb_source']:+d}개

"""
        
        report_content += f"""
## 결론 및 권장사항

### 정확도 평가
- 수작업 분석 정확도: {comparison['accuracy_analysis']['overall_accuracy_manual']:.2f}%
- 메타DB 정확도: {comparison['accuracy_analysis']['overall_accuracy_metadb']:.2f}%

### 개선 필요사항
"""
        
        if comparison['accuracy_analysis']['overall_accuracy_manual'] > 5:
            report_content += f"- 수작업 분석의 정확도가 {comparison['accuracy_analysis']['overall_accuracy_manual']:.2f}%로 5%를 초과합니다. 수작업 분석 방법을 재검토해야 합니다.\n"
        
        if comparison['accuracy_analysis']['overall_accuracy_metadb'] > 5:
            report_content += f"- 메타DB의 정확도가 {comparison['accuracy_analysis']['overall_accuracy_metadb']:.2f}%로 5%를 초과합니다. 파서 로직을 개선해야 합니다.\n"
        
        if not comparison['discrepancies']:
            report_content += "- 모든 파일이 5% 이내의 정확도를 유지하고 있습니다.\n"
        
        report_content += f"""
### 다음 단계
1. 5% 이상 차이가 발생한 파일들에 대한 상세 분석
2. 파서 로직 개선 (필요시)
3. 수작업 분석 방법 개선 (필요시)
4. 재검증 및 정확도 향상

---
*이 리포트는 자동으로 생성되었습니다.*
"""
        
        # 리포트 파일 저장
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"검증 결과 리포트 생성 완료: {report_path}")
        return report_path
    
    def run_validation(self) -> Dict[str, Any]:
        """전체 검증 프로세스를 실행합니다."""
        print("=== 메타DB 정확도 검증 시작 ===")
        
        # 1. 수작업 분석 결과 로드
        manual_data = self.load_manual_analysis()
        
        # 2. 메타DB 분석 결과 로드
        metadb_data = self.load_metadb_analysis()
        
        # 3. 실제 소스코드 검증
        source_data = self.verify_source_code()
        
        # 4. 결과 비교
        comparison = self.compare_results()
        
        # 5. 리포트 생성
        report_path = self.generate_report(comparison)
        
        print("=== 메타DB 정확도 검증 완료 ===")
        
        return {
            'manual_data': manual_data,
            'metadb_data': metadb_data,
            'source_data': source_data,
            'comparison': comparison,
            'report_path': report_path
        }

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python metadb_validation.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    validator = MetaDBValidator(project_name)
    results = validator.run_validation()
    
    # 결과 요약 출력
    print("\n=== 검증 결과 요약 ===")
    accuracy = results['comparison']['accuracy_analysis']
    print(f"수작업 분석 정확도: {accuracy['overall_accuracy_manual']:.2f}%")
    print(f"메타DB 정확도: {accuracy['overall_accuracy_metadb']:.2f}%")
    print(f"불일치 파일 수: {len(results['comparison']['discrepancies'])}개")
    print(f"상세 리포트: {results['report_path']}")

if __name__ == "__main__":
    main()
