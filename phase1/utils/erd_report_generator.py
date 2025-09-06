"""
ERD 텍스트 리포트 생성기
분석된 ERD 구조를 바탕으로 텍스트/마크다운 형식의 리포트를 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from utils.erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class ERDReportGenerator:
    """ERD 텍스트 리포트 생성기"""
    
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
        self.logger.info("ERD 텍스트 리포트 생성 시작")
        
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
- **분석자**: ERDAnalyzer
- **보고서 유형**: 데이터베이스 ERD 분석

---

## 📊 ERD 요약 정보

### 📈 **전체 통계**
- **📋 총 테이블 수**: {erd_structure.total_tables}개
- **📝 총 컬럼 수**: {erd_structure.total_columns}개
- **🔗 총 관계 수**: {erd_structure.total_relationships}개
- **📊 테이블당 평균 컬럼 수**: {erd_structure.total_columns / erd_structure.total_tables:.1f}개

### 🕐 **분석 정보**
- **🔍 분석 시작 시간**: {erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
- **📁 분석 대상**: DB_SCHEMA 폴더

---

## 🏗️ 테이블 구조 상세 분석

"""
        
        # 테이블별 상세 분석
        for table in erd_structure.tables:
            content += self._generate_table_section(table)
        
        # 관계 분석
        content += self._generate_relationship_analysis(erd_structure)
        
        # 데이터 타입 분석
        content += self._generate_datatype_analysis(erd_structure)
        
        # 결론 및 제언
        content += self._generate_conclusion(erd_structure)
        
        return content
    
    def _generate_table_section(self, table: TableInfo) -> str:
        """테이블별 상세 섹션 생성"""
        content = f"""### 🎯 **테이블: `{table.name}`**

#### 📊 **테이블 정보**
- **📋 테이블명**: `{table.name}`
- **📝 설명**: {table.comment}
- **📊 컬럼 수**: {len(table.columns)}개
- **🔑 기본키**: {', '.join(table.primary_keys) if table.primary_keys else '없음'}
- **🔗 외래키**: {len(table.foreign_keys)}개

#### 📝 **컬럼 상세 정보**

"""
        
        # 컬럼별 상세 정보
        for column in table.columns:
            content += self._generate_column_detail(column)
        
        content += "\n---\n\n"
        return content
    
    def _generate_column_detail(self, column: ColumnInfo) -> str:
        """컬럼별 상세 정보 생성"""
        # 컬럼 타입 정보
        column_type = []
        if column.primary_key:
            column_type.append("🔑 기본키")
        if column.foreign_key:
            column_type.append("🔗 외래키")
        if not column.nullable:
            column_type.append("❌ NOT NULL")
        else:
            column_type.append("✅ NULL 허용")
        
        # 참조 정보
        reference_text = ""
        if column.foreign_key and column.referenced_table:
            reference_text = f"\n- **🔗 참조**: `{column.referenced_table}.{column.referenced_column or 'ID'}`"
        
        # 기본값 정보
        default_text = ""
        if column.default_value:
            default_text = f"\n- **💡 기본값**: `{column.default_value}`"
        
        # 주석 정보
        comment_text = ""
        if column.comment:
            comment_text = f"\n- **💬 설명**: {column.comment}"
        
        content = f"""##### 📝 **{column.name}**
- **🏷️ 데이터 타입**: `{column.data_type}`
- **🏷️ 컬럼 타입**: {', '.join(column_type)}{reference_text}{default_text}{comment_text}

"""
        
        return content
    
    def _generate_relationship_analysis(self, erd_structure: ERDStructure) -> str:
        """관계 분석 섹션 생성"""
        content = """## 🔗 테이블 관계 분석

### 📊 **전체 관계 현황**
"""
        
        # 모든 외래키 관계 수집
        all_relationships = []
        for table in erd_structure.tables:
            for fk in table.foreign_keys:
                all_relationships.append(fk)
        
        if all_relationships:
            content += f"#### 🔗 **외래키 관계 목록**\n"
            for i, (column, ref_table, ref_column, constraint) in enumerate(all_relationships, 1):
                content += f"{i}. **{column}** → **{ref_table}.{ref_column or 'ID'}** (`{constraint}`)\n"
            
            # 테이블별 관계 수 분석
            table_relationship_count = {}
            for table in erd_structure.tables:
                table_relationship_count[table.name] = len(table.foreign_keys)
            
            # 관계 수 기준으로 정렬
            sorted_tables = sorted(table_relationship_count.items(), key=lambda x: x[1], reverse=True)
            
            content += "\n#### 📊 **테이블별 관계 수**\n"
            for table_name, rel_count in sorted_tables:
                if rel_count > 0:
                    content += f"- **{table_name}**: {rel_count}개 관계\n"
        else:
            content += "#### ℹ️ **외래키 관계 없음**\n"
            content += "현재 스키마에 외래키 관계가 정의되어 있지 않습니다.\n"
        
        content += "\n---\n\n"
        return content
    
    def _generate_datatype_analysis(self, erd_structure: ERDStructure) -> str:
        """데이터 타입 분석 섹션 생성"""
        content = """## 📊 데이터 타입 분석

### 📈 **데이터 타입 분포**
"""
        
        # 모든 컬럼의 데이터 타입 수집
        datatype_freq = {}
        for table in erd_structure.tables:
            for column in table.columns:
                datatype = column.data_type.upper()
                datatype_freq[datatype] = datatype_freq.get(datatype, 0) + 1
        
        if datatype_freq:
            # 빈도 기준으로 정렬
            sorted_datatypes = sorted(datatype_freq.items(), key=lambda x: x[1], reverse=True)
            
            content += "#### 🔝 **가장 많이 사용되는 데이터 타입 (Top 10)**\n"
            for datatype, count in sorted_datatypes[:10]:
                percentage = (count / erd_structure.total_columns) * 100
                content += f"- **{datatype}**: {count}개 컬럼 ({percentage:.1f}%)\n"
            
            # 데이터 타입별 특징 분석
            content += "\n#### 💡 **데이터 타입별 특징**\n"
            
            # 숫자형
            numeric_types = [dt for dt in datatype_freq.keys() if any(n in dt for n in ['INT', 'NUMBER', 'DECIMAL', 'FLOAT', 'DOUBLE'])]
            if numeric_types:
                numeric_count = sum(datatype_freq[dt] for dt in numeric_types)
                content += f"- **🔢 숫자형**: {numeric_count}개 컬럼 ({numeric_count/erd_structure.total_columns*100:.1f}%)\n"
            
            # 문자형
            string_types = [dt for dt in datatype_freq.keys() if any(s in dt for s in ['VARCHAR', 'CHAR', 'TEXT', 'STRING'])]
            if string_types:
                string_count = sum(datatype_freq[dt] for dt in string_types)
                content += f"- **📝 문자형**: {string_count}개 컬럼 ({string_count/erd_structure.total_columns*100:.1f}%)\n"
            
            # 날짜형
            date_types = [dt for dt in datatype_freq.keys() if any(d in dt for d in ['DATE', 'TIME', 'TIMESTAMP'])]
            if date_types:
                date_count = sum(datatype_freq[dt] for dt in date_types)
                content += f"- **📅 날짜형**: {date_count}개 컬럼 ({date_count/erd_structure.total_columns*100:.1f}%)\n"
        
        content += "\n---\n\n"
        return content
    
    def _generate_conclusion(self, erd_structure: ERDStructure) -> str:
        """결론 및 제언 섹션 생성"""
        content = """## 📝 결론 및 제언

### 🎉 **현재 상태**
"""
        
        # 데이터베이스 규모에 따른 평가
        if erd_structure.total_tables < 5:
            content += "- ✅ **소규모 데이터베이스**: 간단하고 관리하기 쉬운 구조"
        elif erd_structure.total_tables < 20:
            content += "- ✅ **중간 규모 데이터베이스**: 적절한 복잡도와 구조"
        else:
            content += "- ✅ **대규모 데이터베이스**: 체계적인 구조화가 중요"
        
        # 관계 복잡도 평가
        if erd_structure.total_relationships == 0:
            content += "\n- ⚠️ **관계 복잡도**: 외래키 관계가 정의되지 않음 (정규화 고려 필요)"
        elif erd_structure.total_relationships < erd_structure.total_tables:
            content += "\n- ✅ **관계 복잡도**: 적절한 테이블 간 관계"
        else:
            content += "\n- 🚨 **관계 복잡도**: 복잡한 테이블 간 관계 (성능 최적화 고려)"
        
        content += f"""

### 🚀 **개선 제언**
1. **🔗 관계 정의**: 외래키 제약조건 명시적 정의
2. **📝 컬럼 설명**: 각 컬럼별 상세한 설명 추가
3. **🔑 인덱스 최적화**: 자주 조회되는 컬럼에 인덱스 추가
4. **📊 데이터 타입 최적화**: 적절한 데이터 타입 및 크기 설정
5. **🏗️ 정규화**: 데이터 중복 제거 및 정규화 고려

### 📋 **다음 단계**
1. **상세 스키마 문서화**: 각 테이블별 용도 및 비즈니스 규칙 정리
2. **성능 분석**: 쿼리 성능 및 인덱스 최적화
3. **데이터 품질 검증**: 데이터 무결성 및 일관성 체크
4. **보안 검토**: 접근 권한 및 데이터 암호화 검토

---
"""
        
        return content
    
    def _save_report(self, content: str, output_path: str):
        """리포트를 파일로 저장"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.logger.error(f"ERD 리포트 저장 실패: {e}")
            raise
