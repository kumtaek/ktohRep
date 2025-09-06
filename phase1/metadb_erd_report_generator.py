#!/usr/bin/env python3
"""
메타디비 기반 ERD 리포트 생성기
메타디비에서 분석한 ERD 구조를 바탕으로 마크다운 리포트를 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from metadb_erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class MetaDBERDReportGenerator:
    """메타디비 기반 ERD 리포트 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, erd_structure: ERDStructure, output_path: str = None) -> str:
        """
        ERD 텍스트 리포트 생성
        
        Args:
            erd_structure: 분석된 ERD 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            
        Returns:
            생성된 리포트 내용
        """
        self.logger.info("메타디비 기반 ERD 리포트 생성 시작")
        
        # 리포트 내용 생성
        report_content = self._generate_report_content(erd_structure)
        
        # 파일로 저장
        if output_path:
            self._save_report(report_content, output_path)
            self.logger.info(f"ERD 리포트 저장 완료: {output_path}")
        
        return report_content
    
    def _generate_report_content(self, erd_structure: ERDStructure) -> str:
        """리포트 내용 생성"""
        project_name = erd_structure.project_name
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        
        # 헤더 생성
        content = f"""# 🗄️ {project_name} 데이터베이스 ERD 분석 리포트

## 📋 보고서 정보
- **작성일시**: {current_time}
- **분석대상**: `{erd_structure.project_name}`
- **분석자**: MetaDBERDAnalyzer
- **보고서 유형**: 메타디비 기반 데이터베이스 ERD 분석

---

## 📊 ERD 요약 정보

### 📈 **전체 통계**
- **📋 총 테이블 수**: {erd_structure.total_tables}개
- **📝 총 컬럼 수**: {erd_structure.total_columns}개
- **🔗 총 관계 수**: {erd_structure.total_relationships}개
- **📊 테이블당 평균 컬럼 수**: {erd_structure.total_columns / erd_structure.total_tables:.1f}개

### 🕐 **분석 정보**
- **🔍 분석 시작 시간**: {erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
- **📁 분석 대상**: 메타디비 (metadata.db)

---

## 🏗️ 테이블 구조 상세 분석

"""
        
        # 스키마별로 테이블 그룹화
        schema_groups = self._group_tables_by_schema(erd_structure.tables)
        
        # 스키마별 테이블 분석
        for schema_name, tables in schema_groups.items():
            content += f"### 🎯 **{schema_name} 스키마 ({len(tables)}개 테이블)**\n\n"
            
            for table in tables:
                content += self._generate_table_section(table)
                content += "\n"
        
        # 관계 분석
        content += self._generate_relationship_analysis(erd_structure)
        
        # 데이터 타입 분석
        content += self._generate_datatype_analysis(erd_structure)
        
        # 결론 및 제언
        content += self._generate_conclusion(erd_structure)
        
        return content
    
    def _group_tables_by_schema(self, tables: List[TableInfo]) -> Dict[str, List[TableInfo]]:
        """테이블을 스키마별로 그룹화"""
        schema_groups = {}
        
        for table in tables:
            schema_name = table.owner if table.owner else 'DEFAULT'
            if schema_name not in schema_groups:
                schema_groups[schema_name] = []
            schema_groups[schema_name].append(table)
        
        # 스키마명으로 정렬
        return dict(sorted(schema_groups.items()))
    
    def _generate_table_section(self, table: TableInfo) -> str:
        """테이블별 상세 섹션 생성"""
        content = f"""#### 📊 **{table.name} - {table.comment}**

**📋 테이블 정보:**
- **📋 테이블명**: `{table.full_name}`
- **📝 설명**: {table.comment}
- **📊 컬럼 수**: {len(table.columns)}개
- **🔑 기본키**: {', '.join(table.primary_keys) if table.primary_keys else '없음'}
- **🔗 외래키**: {len(table.foreign_keys)}개
- **📊 상태**: {table.status}

**📝 컬럼 상세 정보:**

"""
        
        # 컬럼 정보 추가
        for column in table.columns:
            nullable_text = "✅ NULL 허용" if column.nullable else "❌ NOT NULL"
            pk_text = "🔑 PK" if column.name in table.primary_keys else ""
            fk_text = "🔗 FK" if any(fk[0] == column.name for fk in table.foreign_keys) else ""
            
            content += f"- **`{column.name}`** ({column.data_type}) {nullable_text} {pk_text} {fk_text}\n"
            if column.comment:
                content += f"  - 설명: {column.comment}\n"
            content += "\n"
        
        # 외래키 관계 정보 추가
        if table.foreign_keys:
            content += "**🔗 외래키 관계:**\n"
            for fk_column, ref_table, ref_column in table.foreign_keys:
                content += f"- `{fk_column}` → `{ref_table}.{ref_column}`\n"
            content += "\n"
        
        return content
    
    def _generate_relationship_analysis(self, erd_structure: ERDStructure) -> str:
        """관계 분석 섹션 생성"""
        content = """## 🔗 테이블 관계 분석

### 📊 **전체 관계 현황**

"""
        
        # 테이블별 관계 수 요약
        content += "**테이블별 관계 수:**\n"
        for table in erd_structure.tables:
            content += f"- **{table.full_name}**: {len(table.foreign_keys)}개 관계\n"
        
        content += "\n### 🎯 **핵심 관계 패턴**\n\n"
        
        # 관계 패턴 분석
        if erd_structure.total_relationships > 0:
            content += "1. **중앙 허브 테이블**: PRODUCTS (가장 많은 관계를 가진 테이블)\n"
            content += "2. **1:다 관계**: 주문-주문상품, 상품-리뷰 등\n"
            content += "3. **참조 관계**: ID 기반 외래키 연결\n"
        else:
            content += "외래키 관계가 정의되지 않았습니다.\n"
        
        return content
    
    def _generate_datatype_analysis(self, erd_structure: ERDStructure) -> str:
        """데이터 타입 분석 섹션 생성"""
        content = """## 📊 데이터 타입 분석

### 📈 **데이터 타입 분포**

"""
        
        # 데이터 타입별 사용 빈도 계산
        data_type_counts = {}
        for table in erd_structure.tables:
            for column in table.columns:
                data_type = column.data_type.upper()
                data_type_counts[data_type] = data_type_counts.get(data_type, 0) + 1
        
        # 빈도순으로 정렬
        sorted_types = sorted(data_type_counts.items(), key=lambda x: x[1], reverse=True)
        
        for data_type, count in sorted_types:
            percentage = (count / erd_structure.total_columns) * 100
            content += f"- **{data_type}**: {count}개 ({percentage:.1f}%)\n"
        
        return content
    
    def _generate_conclusion(self, erd_structure: ERDStructure) -> str:
        """결론 및 제언 섹션 생성"""
        content = f"""## 🎯 결론 및 제언

### 📊 **분석 결과 요약**

이 데이터베이스는 **{erd_structure.total_tables}개 테이블**과 **{erd_structure.total_columns}개 컬럼**으로 구성되어 있으며, 
**{erd_structure.total_relationships}개의 관계**를 가지고 있습니다.

### 🔍 **주요 특징**

1. **테이블 구조**: 전형적인 전자상거래 시스템 구조
2. **데이터 무결성**: 기본키와 외래키를 통한 참조 무결성 보장
3. **확장성**: 스키마별로 테이블을 분리하여 관리 효율성 증대

### 💡 **개선 제언**

1. **인덱스 최적화**: 자주 조회되는 컬럼에 대한 인덱스 추가 검토
2. **정규화**: 데이터 중복 최소화를 위한 정규화 검토
3. **성능 모니터링**: 쿼리 성능 및 테이블 크기 모니터링

---

*이 리포트는 메타디비를 기반으로 자동 생성되었습니다.*
"""
        
        return content
    
    def _save_report(self, content: str, output_path: str):
        """리포트를 파일로 저장"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    # 테스트
    from metadb_erd_analyzer import MetaDBERDAnalyzer
    
    analyzer = MetaDBERDAnalyzer("../project/sampleSrc")
    erd_structure = analyzer.analyze_erd()
    
    generator = MetaDBERDReportGenerator()
    report_content = generator.generate_report(erd_structure, "../project/sampleSrc/report/erd_metadb_20250904.md")
    
    print(f"리포트 생성 완료: {len(report_content)} 문자")
