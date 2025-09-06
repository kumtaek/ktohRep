"""
ERD 생성기
CSV 테이블 정보와 MyBatis JOIN 분석을 통합하여 완전한 ERD를 생성하는 엔진
"""
import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import json

from .table_metadata_loader import TableMetadataLoader
from .mybatis_join_analyzer import MyBatisJoinAnalyzer

class ERDGenerator:
    """ERD 생성을 위한 통합 엔진"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.table_loader = TableMetadataLoader(metadata_engine)
        self.join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        self.logger = logging.getLogger(__name__)
    
    def generate_complete_erd(self, project_id: int, project_name: str,
                            csv_file_path: str, mybatis_xml_directory: str) -> Dict:
        """
        완전한 ERD 생성 프로세스
        1. CSV에서 테이블 정보 로드
        2. MyBatis XML에서 JOIN 관계 추출
        3. 누락된 테이블을 더미로 생성
        4. ERD 메타데이터 완성
        """
        try:
            self.logger.info(f"ERD 생성 시작: {project_name}")
            
            # 1단계: CSV에서 테이블 정보 로드
            self.logger.info("1단계: CSV 테이블 정보 로드 중...")
            csv_result = self.table_loader.load_tables_from_csv(project_id, csv_file_path)
            
            if not csv_result['success']:
                return {
                    'success': False,
                    'error': f"CSV 로드 실패: {csv_result['error']}",
                    'stage': 'csv_loading'
                }
            
            loaded_tables = csv_result['loaded_tables']
            loaded_columns = csv_result['loaded_columns']
            
            self.logger.info(f"CSV에서 {csv_result['table_count']}개 테이블 로드 완료")
            
            # 2단계: CSV 기반 외래키 관계 생성
            self.logger.info("2단계: CSV 외래키 관계 생성 중...")
            fk_result = self.table_loader.create_foreign_key_relationships(
                project_id, loaded_tables, loaded_columns
            )
            
            if not fk_result['success']:
                self.logger.warning(f"외래키 관계 생성 실패: {fk_result['error']}")
            else:
                self.logger.info(f"외래키 관계 {fk_result['relationship_count']}개 생성 완료")
            
            # 3단계: MyBatis XML에서 JOIN 관계 추출
            self.logger.info("3단계: MyBatis JOIN 관계 분석 중...")
            join_result = self.join_analyzer.analyze_multiple_mybatis_files(
                project_id, mybatis_xml_directory, loaded_tables
            )
            
            if not join_result['success']:
                self.logger.warning(f"JOIN 관계 분석 실패: {join_result['error']}")
                join_result = {
                    'success': True,
                    'joins_found': [],
                    'dummy_tables_created': {},
                    'join_count': 0,
                    'dummy_table_count': 0
                }
            else:
                self.logger.info(f"JOIN 관계 {join_result['join_count']}개 발견")
            
            # 4단계: ERD 메타데이터 생성
            self.logger.info("4단계: ERD 메타데이터 통합 중...")
            erd_metadata = self._create_erd_metadata(
                project_id, project_name, loaded_tables, loaded_columns,
                fk_result, join_result
            )
            
            # 5단계: ERD 텍스트 형식 생성
            self.logger.info("5단계: ERD 텍스트 다이어그램 생성 중...")
            text_erd = self._generate_text_erd(erd_metadata)
            
            total_tables = len(loaded_tables)
            total_relationships = fk_result.get('relationship_count', 0) + join_result.get('join_count', 0)
            
            self.logger.info(f"ERD 생성 완료: {total_tables}개 테이블, {total_relationships}개 관계")
            
            return {
                'success': True,
                'project_name': project_name,
                'erd_metadata': erd_metadata,
                'text_erd': text_erd,
                'statistics': {
                    'total_tables': total_tables,
                    'csv_tables': csv_result['table_count'],
                    'dummy_tables': fk_result.get('dummy_table_count', 0) + join_result.get('dummy_table_count', 0),
                    'total_relationships': total_relationships,
                    'foreign_key_relationships': fk_result.get('relationship_count', 0),
                    'join_relationships': join_result.get('join_count', 0),
                    'total_columns': len(loaded_columns)
                },
                'csv_result': csv_result,
                'fk_result': fk_result,
                'join_result': join_result
            }
            
        except Exception as e:
            self.logger.error(f"ERD 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'stage': 'erd_generation'
            }
    
    def _create_erd_metadata(self, project_id: int, project_name: str,
                           loaded_tables: Dict, loaded_columns: List[Dict],
                           fk_result: Dict, join_result: Dict) -> Dict:
        """ERD 메타데이터 구조 생성"""
        
        # 테이블 정보 정리
        tables = {}
        for table_name, table_id in loaded_tables.items():
            # 해당 테이블의 컬럼 정보 수집
            table_columns = [col for col in loaded_columns if col['table_name'] == table_name]
            
            # 프라이머리 키 컬럼 찾기
            pk_columns = [col['column_name'] for col in table_columns if col['is_primary_key']]
            
            # 외래키 컬럼 찾기
            fk_columns = [
                {
                    'column_name': col['column_name'],
                    'foreign_table': col['foreign_table'],
                    'foreign_column': col['foreign_column']
                }
                for col in table_columns if col['is_foreign_key']
            ]
            
            tables[table_name] = {
                'table_id': table_id,
                'table_name': table_name,
                'columns': table_columns,
                'primary_keys': pk_columns,
                'foreign_keys': fk_columns,
                'column_count': len(table_columns),
                'is_dummy': any('dummy' in str(table_id) for dummy_list in 
                              [fk_result.get('dummy_tables_created', {}).values(),
                               join_result.get('dummy_tables_created', {}).values()] 
                              for dummy_table_id in dummy_list if dummy_table_id == table_id)
            }
        
        # 관계 정보 정리
        relationships = []
        
        # 외래키 관계 추가
        for fk_rel in fk_result.get('relationships_created', []):
            relationships.append({
                'type': 'foreign_key',
                'source_table': fk_rel['source_table'],
                'target_table': fk_rel['target_table'],
                'source_column': fk_rel['source_column'],
                'target_column': fk_rel['target_column'],
                'relationship_strength': 'strong',
                'cardinality': 'many_to_one'
            })
        
        # JOIN 관계 추가
        for join_rel in join_result.get('joins_found', []):
            relationships.append({
                'type': 'join',
                'source_table': join_rel['source_table'],
                'target_table': join_rel['target_table'],
                'join_type': join_rel['join_type'],
                'join_condition': join_rel['join_condition'],
                'relationship_strength': 'weak',
                'cardinality': 'unknown'
            })
        
        return {
            'project_id': project_id,
            'project_name': project_name,
            'tables': tables,
            'relationships': relationships,
            'metadata': {
                'generation_timestamp': self._get_current_timestamp(),
                'generator_version': '1.0',
                'data_sources': {
                    'csv_tables': True,
                    'mybatis_joins': True
                }
            }
        }
    
    def _generate_text_erd(self, erd_metadata: Dict) -> str:
        """텍스트 형식 ERD 다이어그램 생성"""
        tables = erd_metadata['tables']
        relationships = erd_metadata['relationships']
        
        erd_text = f"""
# 📊 {erd_metadata['project_name']} 데이터베이스 ERD

## 🗃️ 테이블 구조

"""
        
        # 테이블 정보 출력
        for table_name, table_info in tables.items():
            is_dummy = table_info.get('is_dummy', False)
            dummy_marker = " [더미]" if is_dummy else ""
            
            erd_text += f"""
┌{'─' * 65}┐
│ {table_name.upper()}{dummy_marker:<50} │
├{'─' * 65}┤
"""
            
            # 컬럼 정보
            columns = table_info['columns']
            pk_columns = set(table_info['primary_keys'])
            fk_columns = {fk['column_name']: fk for fk in table_info['foreign_keys']}
            
            for col in columns:
                col_name = col['column_name']
                data_type = col['data_type']
                
                # 아이콘 결정
                if col_name in pk_columns:
                    icon = "🔑"
                elif col_name in fk_columns:
                    icon = "🔗"
                else:
                    icon = "📊"
                
                # 컬럼 설명
                description = []
                if col_name in pk_columns:
                    description.append("Primary Key")
                if col_name in fk_columns:
                    fk_info = fk_columns[col_name]
                    description.append(f"→ {fk_info['foreign_table']}")
                if not col['is_nullable']:
                    description.append("NOT NULL")
                
                desc_text = " ".join(description) if description else "일반 컬럼"
                
                erd_text += f"│ {icon} {col_name:<15} │ {data_type:<12} │ {desc_text:<25} │\n"
            
            erd_text += f"└{'─' * 65}┘\n"
        
        # 관계 정보 출력
        erd_text += """
## 🔗 테이블 관계

### 📋 Foreign Key 관계
"""
        
        fk_relationships = [r for r in relationships if r['type'] == 'foreign_key']
        if fk_relationships:
            for rel in fk_relationships:
                erd_text += f"├─ {rel['source_table']}.{rel['source_column']} → {rel['target_table']}.{rel['target_column']}\n"
        else:
            erd_text += "├─ Foreign Key 관계 없음\n"
        
        erd_text += """
### 🔄 JOIN 관계
"""
        
        join_relationships = [r for r in relationships if r['type'] == 'join']
        if join_relationships:
            for rel in join_relationships:
                erd_text += f"├─ {rel['source_table']} {rel['join_type']} JOIN {rel['target_table']}\n"
                if rel.get('join_condition'):
                    erd_text += f"   └─ ON: {rel['join_condition'][:50]}{'...' if len(rel['join_condition']) > 50 else ''}\n"
        else:
            erd_text += "├─ JOIN 관계 없음\n"
        
        # 관계도 시각화
        erd_text += """
## 📈 관계 시각화

"""
        
        # 간단한 관계도 생성
        table_names = list(tables.keys())
        for rel in fk_relationships + join_relationships:
            source = rel['source_table']
            target = rel['target_table']
            rel_type = "FK" if rel['type'] == 'foreign_key' else f"JOIN({rel.get('join_type', 'INNER')})"
            
            erd_text += f"{source} ──[{rel_type}]──► {target}\n"
        
        # 통계 정보
        total_tables = len(tables)
        total_relationships = len(relationships)
        dummy_tables = len([t for t in tables.values() if t.get('is_dummy', False)])
        
        erd_text += f"""
## 📊 ERD 통계

```
총 테이블 수: {total_tables}개
├─ 실제 테이블: {total_tables - dummy_tables}개
└─ 더미 테이블: {dummy_tables}개

총 관계 수: {total_relationships}개
├─ Foreign Key: {len(fk_relationships)}개
└─ JOIN: {len(join_relationships)}개

생성 시각: {erd_metadata['metadata']['generation_timestamp']}
```
"""
        
        return erd_text
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_erd_to_file(self, erd_result: Dict, output_path: str) -> bool:
        """ERD 결과를 파일로 저장"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if erd_result['success']:
                    f.write(erd_result['text_erd'])
                    
                    # 메타데이터를 JSON으로 추가
                    f.write("\n\n## 🔧 ERD 메타데이터 (JSON)\n\n```json\n")
                    f.write(json.dumps(erd_result['erd_metadata'], indent=2, ensure_ascii=False))
                    f.write("\n```")
                    
                    self.logger.info(f"ERD 파일 저장 완료: {output_path}")
                    return True
                else:
                    f.write(f"# ERD 생성 실패\n\n오류: {erd_result['error']}")
                    self.logger.error(f"ERD 생성 실패 결과 저장: {output_path}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"ERD 파일 저장 실패: {e}")
            return False