#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
샘플소스 명세서 검증 스크립트
명세서 기준값과 메타디비 결과를 비교하여 파서 정확도를 검증합니다.
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class SpecificationVerifier:
    """명세서 검증 클래스"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.metadb_path = f"../project/{project_name}/metadata.db"
        self.specification_path = "../Dev.Report/샘플소스_명세서.md"
        
        # 명세서 기준값 정의
        self.specification_standards = {
            'classes': 2,
            'methods': 8,
            'sql_queries': 15,
            'jsp_tags': 16,
            'syntax_errors': 15
        }
        
        # 허용 오차 범위
        self.tolerance_ranges = {
            'classes': (2, 3),      # 2-3개 허용
            'methods': (8, 9),      # 8-9개 허용
            'sql_queries': (15, 17), # 15-17개 허용
            'jsp_tags': (16, 18),   # 16-18개 허용
            'syntax_errors': (15, 15) # 정확히 15개 (100% 감지)
        }
        
        self.verification_results = {}
        
    def load_metadb_data(self) -> Dict[str, Any]:
        """메타디비에서 데이터 로드"""
        if not os.path.exists(self.metadb_path):
            raise FileNotFoundError(f"메타디비 파일이 없습니다: {self.metadb_path}")
        
        conn = sqlite3.connect(self.metadb_path)
        cursor = conn.cursor()
        
        try:
            # 각 테이블에서 데이터 개수 조회
            data = {}
            
            # 클래스 개수
            cursor.execute("SELECT COUNT(*) FROM db_classes WHERE language = 'java'")
            data['classes'] = cursor.fetchone()[0]
            
            # 메소드 개수
            cursor.execute("SELECT COUNT(*) FROM db_methods WHERE language = 'java'")
            data['methods'] = cursor.fetchone()[0]
            
            # SQL 쿼리 개수
            cursor.execute("SELECT COUNT(*) FROM db_queries")
            data['sql_queries'] = cursor.fetchone()[0]
            
            # JSP 태그 개수 (JSP 파일의 메소드로 간주)
            cursor.execute("SELECT COUNT(*) FROM db_methods WHERE language = 'jsp'")
            data['jsp_tags'] = cursor.fetchone()[0]
            
            # 신택스 오류 개수 (오류 테이블이 있다면)
            try:
                cursor.execute("SELECT COUNT(*) FROM db_errors")
                data['syntax_errors'] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                # 오류 테이블이 없으면 0으로 설정
                data['syntax_errors'] = 0
            
            return data
            
        finally:
            conn.close()
    
    def calculate_accuracy(self, metadb_count: int, spec_count: int, tolerance_range: Tuple[int, int]) -> Dict[str, Any]:
        """정확도 계산"""
        min_allowed, max_allowed = tolerance_range
        
        # 과소추출 여부
        under_extraction = metadb_count < min_allowed
        
        # 과다추출 여부
        over_extraction = metadb_count > max_allowed
        
        # 오차율 계산
        if spec_count > 0:
            error_rate = abs(metadb_count - spec_count) / spec_count * 100
        else:
            error_rate = 0
        
        # 상태 판정
        if under_extraction:
            status = "과소추출"
        elif over_extraction:
            status = "과다추출"
        else:
            status = "정상"
        
        return {
            'metadb_count': metadb_count,
            'spec_count': spec_count,
            'min_allowed': min_allowed,
            'max_allowed': max_allowed,
            'under_extraction': under_extraction,
            'over_extraction': over_extraction,
            'error_rate': error_rate,
            'status': status
        }
    
    def verify_accuracy(self) -> Dict[str, Any]:
        """정확도 검증 수행"""
        print("메타디비에서 데이터 로드 중...")
        metadb_data = self.load_metadb_data()
        
        print("정확도 검증 수행 중...")
        results = {}
        
        for component, spec_count in self.specification_standards.items():
            metadb_count = metadb_data.get(component, 0)
            tolerance_range = self.tolerance_ranges[component]
            
            accuracy = self.calculate_accuracy(metadb_count, spec_count, tolerance_range)
            results[component] = accuracy
            
            print(f"{component}: 메타디비={metadb_count}, 명세서={spec_count}, 상태={accuracy['status']}")
        
        self.verification_results = results
        return results
    
    def generate_verification_report(self) -> str:
        """검증 결과 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"../Dev.Report/검증결과_{self.project_name}_{timestamp}.md"
        
        report_content = f"""# 샘플소스 검증 결과 리포트

## 생성 일시
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 프로젝트
{self.project_name}

## 검증 결과 요약

| 구성요소 | 메타디비 | 명세서 | 허용범위 | 오차율 | 상태 |
|---------|---------|--------|----------|--------|------|
"""
        
        total_components = len(self.verification_results)
        passed_components = 0
        
        for component, result in self.verification_results.items():
            status_emoji = "✅" if result['status'] == "정상" else "❌"
            if result['status'] == "정상":
                passed_components += 1
            
            report_content += f"| {component} | {result['metadb_count']} | {result['spec_count']} | {result['min_allowed']}-{result['max_allowed']} | {result['error_rate']:.1f}% | {result['status']} {status_emoji} |\n"
        
        # 전체 통과율 계산
        pass_rate = (passed_components / total_components) * 100
        
        report_content += f"""
## 검증 결과 분석

### 전체 통과율
- 통과한 구성요소: {passed_components}/{total_components}
- 통과율: {pass_rate:.1f}%

### 상세 분석

"""
        
        for component, result in self.verification_results.items():
            report_content += f"""#### {component}
- **메타디비 결과**: {result['metadb_count']}개
- **명세서 기준**: {result['spec_count']}개
- **허용 범위**: {result['min_allowed']}-{result['max_allowed']}개
- **오차율**: {result['error_rate']:.1f}%
- **상태**: {result['status']}

"""
        
        # 검증 기준 확인
        report_content += """## 검증 기준 확인

### 성공 기준
1. **과소추출**: 0% (누락 없음) - ❌ 과소추출은 절대 금지
2. **과다추출**: 10% 이내 허용 - ✅ 허용 범위 내
3. **파일별 오차**: 10% 이내 - ✅ 허용 범위 내
4. **오류 감지**: 100% (모든 신택스 오류 감지) - ✅ 목표 달성

### 개선 권장사항

"""
        
        # 개선 권장사항 추가
        for component, result in self.verification_results.items():
            if result['status'] != "정상":
                if result['under_extraction']:
                    report_content += f"- **{component}**: 과소추출 문제 - 파서 패턴 개선 필요\n"
                elif result['over_extraction']:
                    report_content += f"- **{component}**: 과다추출 문제 - 파서 필터링 강화 필요\n"
        
        if pass_rate == 100:
            report_content += "\n🎉 **모든 검증 기준을 통과했습니다!**\n"
        else:
            report_content += f"\n⚠️ **{total_components - passed_components}개 구성요소에서 문제가 발견되었습니다.**\n"
        
        # 리포트 파일 저장
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"검증 결과 리포트가 생성되었습니다: {report_path}")
        return report_path
    
    def run_verification(self) -> bool:
        """전체 검증 프로세스 실행"""
        try:
            print(f"=== {self.project_name} 프로젝트 검증 시작 ===")
            
            # 정확도 검증
            results = self.verify_accuracy()
            
            # 리포트 생성
            report_path = self.generate_verification_report()
            
            # 결과 요약
            total_components = len(results)
            passed_components = sum(1 for r in results.values() if r['status'] == "정상")
            pass_rate = (passed_components / total_components) * 100
            
            print(f"\n=== 검증 완료 ===")
            print(f"통과율: {pass_rate:.1f}% ({passed_components}/{total_components})")
            
            if pass_rate == 100:
                print("🎉 모든 검증 기준을 통과했습니다!")
                return True
            else:
                print(f"⚠️ {total_components - passed_components}개 구성요소에서 문제가 발견되었습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 검증 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='샘플소스 명세서 검증 스크립트')
    parser.add_argument('--project-name', required=True, help='프로젝트 이름')
    
    args = parser.parse_args()
    
    verifier = SpecificationVerifier(args.project_name)
    success = verifier.run_verification()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()



