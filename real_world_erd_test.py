"""
실제 상황 ERD 테스트
CSV: 테이블 구조만 (외래키 관계 없음)
MyBatis XML: JOIN 관계에서 테이블 간 관계 추출
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def real_world_test():
    print("=== 실제 상황 ERD 생성 테스트 ===\n")
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("RealWorldERD", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 1단계: CSV에서 테이블 구조만 로드 (외래키 관계 없음)
        print("\n1단계: CSV 테이블 구조 로드...")
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"✅ CSV 로드 성공: {csv_result['table_count']}개 테이블, {csv_result['column_count']}개 컬럼")
            
            # 외래키 컬럼 확인
            fk_columns = [col for col in csv_result['loaded_columns'] if col['is_foreign_key']]
            print(f"외래키 컬럼: {len(fk_columns)}개 (예상: 0개)")
        else:
            print(f"❌ CSV 로드 실패: {csv_result['error']}")
            return
        
        # 2단계: MyBatis XML에서 JOIN 관계 분석
        print("\n2단계: MyBatis XML JOIN 관계 분석...")
        join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        
        if not Path(xml_directory).exists():
            print(f"❌ MyBatis XML 디렉토리 없음: {xml_directory}")
            return
        
        join_result = join_analyzer.analyze_multiple_mybatis_files(
            project_id, xml_directory, csv_result['loaded_tables']
        )
        
        if join_result['success']:
            print(f"✅ JOIN 분석 성공: {join_result['join_count']}개 관계 발견")
            print(f"처리된 파일: {join_result['file_count']}개")
            print(f"더미 테이블: {join_result['dummy_table_count']}개")
        else:
            print(f"❌ JOIN 분석 실패: {join_result['error']}")
            return
        
        # 3단계: 발견된 JOIN 관계 출력
        print("\n3단계: 발견된 JOIN 관계:")
        joins_found = join_result.get('joins_found', [])
        if joins_found:
            for join_rel in joins_found:
                print(f"  - {join_rel['source_table']} {join_rel['join_type']} JOIN {join_rel['target_table']}")
                if join_rel.get('join_condition'):
                    condition = join_rel['join_condition'][:50] + "..." if len(join_rel['join_condition']) > 50 else join_rel['join_condition']
                    print(f"    ON: {condition}")
        else:
            print("  - JOIN 관계를 찾지 못했습니다.")
        
        # 4단계: 텍스트 ERD 생성
        print("\n4단계: ERD 생성...")
        
        # 모든 테이블 정보 수집 (원래 테이블 + 더미 테이블)
        all_tables = csv_result['loaded_tables'].copy()
        all_tables.update(join_result.get('dummy_tables_created', {}))
        
        print("\n" + "="*80)
        print("📊 실제 상황 기반 ERD 생성 결과")
        print("="*80)
        print()
        
        print("🗃️ 테이블 목록:")
        csv_tables = list(csv_result['loaded_tables'].keys())
        dummy_tables = list(join_result.get('dummy_tables_created', {}).keys())
        
        print(f"📋 CSV 기반 테이블 ({len(csv_tables)}개):")
        for table in sorted(csv_tables):
            print(f"  ✅ {table}")
        
        if dummy_tables:
            print(f"\n🔍 JOIN에서 발견된 추가 테이블 ({len(dummy_tables)}개):")
            for table in sorted(dummy_tables):
                print(f"  🆕 {table} [더미]")
        
        print(f"\n🔗 발견된 관계 ({len(joins_found)}개):")
        if joins_found:
            for join_rel in joins_found:
                join_type_icon = {"INNER": "🔄", "LEFT": "◀", "RIGHT": "▶", "FULL OUTER": "⬌"}.get(join_rel['join_type'], "🔗")
                print(f"  {join_type_icon} {join_rel['source_table']} ──{join_rel['join_type']}── {join_rel['target_table']}")
        else:
            print("  ❌ 관계를 찾지 못했습니다.")
        
        # 5단계: 분석 결과 요약
        print(f"\n📊 분석 요약:")
        print(f"├─ 총 테이블: {len(all_tables)}개")
        print(f"│  ├─ CSV 테이블: {len(csv_tables)}개")
        print(f"│  └─ 더미 테이블: {len(dummy_tables)}개")
        print(f"├─ JOIN 관계: {len(joins_found)}개")
        print(f"├─ 외래키 관계: 0개 (CSV에서 명시되지 않음)")
        print(f"└─ 분석된 XML 파일: {join_result.get('file_count', 0)}개")
        
        # 6단계: JOIN 관계 기반 ERD 시각화
        if joins_found:
            print(f"\n📈 관계 시각화 (JOIN 기반):")
            print()
            
            # 관계별로 그룹화
            relationships_by_target = {}
            for join_rel in joins_found:
                target = join_rel['target_table']
                source = join_rel['source_table']
                join_type = join_rel['join_type']
                
                if target not in relationships_by_target:
                    relationships_by_target[target] = []
                relationships_by_target[target].append(f"{source} ({join_type})")
            
            for target_table, sources in relationships_by_target.items():
                print(f"{target_table}")
                for i, source in enumerate(sources):
                    connector = "└─" if i == len(sources) - 1 else "├─"
                    print(f"  {connector} {source}")
                print()
        
        print("="*80)
        
        # 7단계: 결과 파일 저장
        output_file = "./docs/RealWorld_ERD_Result.md"
        Path(output_file).parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 실제 상황 기반 ERD 생성 결과\n\n")
            f.write("## 🎯 분석 방식\n\n")
            f.write("- **CSV**: 테이블 구조만 (외래키 관계 없음)\n")
            f.write("- **MyBatis XML**: JOIN 관계에서 테이블 간 관계 추출\n\n")
            
            f.write("## 🗃️ 테이블 목록\n\n")
            f.write(f"### CSV 기반 테이블 ({len(csv_tables)}개)\n\n")
            for table in sorted(csv_tables):
                f.write(f"- ✅ **{table}**\n")
            
            if dummy_tables:
                f.write(f"\n### JOIN에서 발견된 추가 테이블 ({len(dummy_tables)}개)\n\n")
                for table in sorted(dummy_tables):
                    f.write(f"- 🆕 **{table}** [더미]\n")
            
            f.write(f"\n## 🔗 발견된 관계 ({len(joins_found)}개)\n\n")
            if joins_found:
                for join_rel in joins_found:
                    f.write(f"- **{join_rel['source_table']}** {join_rel['join_type']} JOIN **{join_rel['target_table']}**\n")
                    if join_rel.get('join_condition'):
                        f.write(f"  - `{join_rel['join_condition']}`\n")
            else:
                f.write("- ❌ 관계를 찾지 못했습니다.\n")
            
            f.write(f"\n## 📊 통계\n\n")
            f.write(f"- 총 테이블: {len(all_tables)}개\n")
            f.write(f"- CSV 테이블: {len(csv_tables)}개\n")
            f.write(f"- 더미 테이블: {len(dummy_tables)}개\n")
            f.write(f"- JOIN 관계: {len(joins_found)}개\n")
            f.write(f"- 분석된 XML 파일: {join_result.get('file_count', 0)}개\n")
        
        print(f"💾 결과 파일 저장: {output_file}")
        print("\n✅ 실제 상황 ERD 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    real_world_test()