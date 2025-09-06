"""
최종 ERD 생성 테스트 - 직접 테이블과 관계를 생성하여 ERD 출력
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def create_manual_erd():
    """수동으로 테이블과 관계를 생성하여 ERD 생성"""
    print("=== 수동 ERD 생성 테스트 ===\n")
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ManualERD", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 생성
        tables = {}
        
        # users 테이블
        tables['users'] = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name='users',
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        # user_types 테이블
        tables['user_types'] = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name='user_types',
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        # products 테이블
        tables['products'] = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name='products',
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        # categories 테이블
        tables['categories'] = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name='categories',
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        # brands 테이블
        tables['brands'] = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name='brands',
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        print(f"생성된 테이블: {len(tables)}개")
        
        # 관계 생성
        relationships = []
        
        # users -> user_types
        metadata_engine.add_relationship(
            project_id=project_id,
            src_component_id=tables['users'],
            dst_component_id=tables['user_types'],
            relationship_type='foreign_key',
            confidence=1.0
        )
        relationships.append("users -> user_types (user_type)")
        
        # products -> categories
        metadata_engine.add_relationship(
            project_id=project_id,
            src_component_id=tables['products'],
            dst_component_id=tables['categories'],
            relationship_type='foreign_key',
            confidence=1.0
        )
        relationships.append("products -> categories (category_id)")
        
        # products -> brands
        metadata_engine.add_relationship(
            project_id=project_id,
            src_component_id=tables['products'],
            dst_component_id=tables['brands'],
            relationship_type='foreign_key',
            confidence=1.0
        )
        relationships.append("products -> brands (brand_id)")
        
        print(f"생성된 관계: {len(relationships)}개")
        
        # 텍스트 ERD 생성
        print("\n" + "="*80)
        print("📊 SampleECommerce 데이터베이스 ERD")
        print("="*80)
        print()
        
        # 테이블 구조 출력
        print("🗃️ 테이블 구조")
        print()
        
        table_info = {
            'users': ['id (PK)', 'user_id', 'username', 'email', 'password', 'name', 'age', 'status', 'user_type (FK)', 'phone', 'address', 'created_date', 'updated_date'],
            'user_types': ['type_code (PK)', 'type_name', 'description'],
            'products': ['id (PK)', 'product_id', 'product_name', 'price', 'status', 'category_id (FK)', 'brand_id (FK)', 'stock_quantity', 'description', 'del_yn', 'created_date', 'updated_date'],
            'categories': ['category_id (PK)', 'category_name', 'description', 'status', 'created_date'],
            'brands': ['brand_id (PK)', 'brand_name', 'description', 'status', 'created_date']
        }
        
        for table_name, columns in table_info.items():
            print(f"┌{'─' * 65}┐")
            print(f"│ {table_name.upper():<63} │")
            print(f"├{'─' * 65}┤")
            
            for column in columns:
                icon = "🔑" if "(PK)" in column else "🔗" if "(FK)" in column else "📊"
                print(f"│ {icon} {column:<60} │")
            
            print(f"└{'─' * 65}┘")
            print()
        
        # 관계 정보 출력
        print("🔗 테이블 관계")
        print()
        print("📋 Foreign Key 관계:")
        for rel in relationships:
            print(f"├─ {rel}")
        print()
        
        # 관계도 시각화
        print("📈 관계 시각화")
        print()
        print("USER_TYPES ◄──────┐")
        print("    │             │")
        print("    │ 1:N         │")
        print("    ▼             │")
        print("  USERS           │")
        print("                  │")
        print("                  │")
        print("CATEGORIES ◄──────┼──────┐")
        print("    │             │      │")
        print("    │ 1:N         │      │ 1:N")
        print("    ▼             │      ▼")
        print(" PRODUCTS ◄───────┘    BRANDS")
        print()
        
        # 통계 정보
        print("📊 ERD 통계")
        print()
        print("```")
        print(f"총 테이블 수: {len(tables)}개")
        print(f"총 관계 수: {len(relationships)}개")
        print(f"├─ Foreign Key: {len(relationships)}개")
        print(f"└─ JOIN: 0개")
        print("```")
        print()
        print("="*80)
        
        # 파일로 저장
        output_file = "./docs/SampleECommerce_ERD_Manual.md"
        Path(output_file).parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 SampleECommerce 데이터베이스 ERD\n\n")
            f.write("## 🗃️ 테이블 구조\n\n")
            
            for table_name, columns in table_info.items():
                f.write(f"### {table_name.upper()}\n")
                f.write(f"```\n")
                for column in columns:
                    f.write(f"- {column}\n")
                f.write("```\n\n")
            
            f.write("## 🔗 테이블 관계\n\n")
            for rel in relationships:
                f.write(f"- {rel}\n")
            
            f.write(f"\n## 📊 통계\n\n")
            f.write(f"- 총 테이블: {len(tables)}개\n")
            f.write(f"- 총 관계: {len(relationships)}개\n")
        
        print(f"💾 ERD 파일 저장 완료: {output_file}")
        print("\n테스트 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_manual_erd()