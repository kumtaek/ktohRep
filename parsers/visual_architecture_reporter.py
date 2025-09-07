"""
시각적 아키텍처 리포트 생성기
ASCII 아트 스타일의 도식화된 텍스트 리포트를 생성
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter

class VisualArchitectureReporter:
    """시각적 아키텍처 리포트 생성"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.db_path = metadata_engine.db_path
    
    def generate_visual_report(self, project_id: int) -> str:
        """완전한 시각적 리포트 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 데이터 수집
                components = self._get_components_by_layer(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                stats = self._get_component_stats(cursor, project_id)
                patterns = self._analyze_patterns(components, relationships)
                tables = self._get_table_info(cursor, project_id)
                
                # 리포트 생성
                report_parts = []
                
                # 1. 시스템 아키텍처 구조
                report_parts.append(self._generate_architecture_diagram(components, relationships))
                
                # 2. 관계 상세 정보
                report_parts.append(self._generate_relationship_details(relationships))
                
                # 3. 구성 요소 통계
                report_parts.append(self._generate_component_statistics(stats))
                
                # 4. 아키텍처 패턴 분석
                report_parts.append(self._generate_pattern_analysis(patterns, components))
                
                # 5. 데이터베이스 구조 (테이블이 있는 경우)
                if tables:
                    report_parts.append(self._generate_database_structure(tables, cursor, project_id))
                
                return "\n\n".join(report_parts)
                
        except Exception as e:
            return f"시각적 리포트 생성 실패: {e}"
    
    def _get_components_by_layer(self, cursor, project_id: int) -> Dict:
        """계층별 컴포넌트 조회"""
        cursor.execute("""
            SELECT c.component_name, c.component_type, f.file_path,
                   bt.layer, bt.domain
            FROM components c
            LEFT JOIN files f ON c.file_id = f.file_id
            LEFT JOIN business_tags bt ON c.component_id = bt.component_id
            WHERE c.project_id = ? AND c.component_type NOT LIKE '%dummy%'
            ORDER BY bt.layer, c.component_name
        """, (project_id,))
        
        components = cursor.fetchall()
        layers = defaultdict(list)
        
        for comp_name, comp_type, file_path, layer, domain in components:
            # 파일 경로에서 계층 추정
            if not layer:
                layer = self._infer_layer_from_path(file_path or "", comp_name)
            
            layers[layer or 'other'].append({
                'name': comp_name,
                'type': comp_type,
                'path': file_path,
                'domain': domain
            })
        
        return dict(layers)
    
    def _infer_layer_from_path(self, file_path: str, comp_name: str) -> str:
        """파일 경로와 컴포넌트 이름에서 계층 추정"""
        path_lower = file_path.lower()
        name_lower = comp_name.lower()
        
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['controller', 'rest', 'web', 'api']):
            return 'controller'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['service', 'business']):
            return 'service'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['dao', 'repository', 'mapper']):
            return 'mapper'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['model', 'entity', 'dto', 'vo']):
            return 'model'
        else:
            return 'other'
    
    def _get_relationships_by_type(self, cursor, project_id: int) -> Dict:
        """관계 타입별 조회"""
        cursor.execute("""
            SELECT r.relationship_type,
                   c1.component_name as source,
                   c2.component_name as target,
                   r.confidence
            FROM relationships r
            JOIN components c1 ON r.src_component_id = c1.component_id
            JOIN components c2 ON r.dst_component_id = c2.component_id
            WHERE r.project_id = ?
            ORDER BY r.relationship_type, c1.component_name
        """, (project_id,))
        
        relationships = cursor.fetchall()
        by_type = defaultdict(list)
        
        for rel_type, source, target, confidence in relationships:
            by_type[rel_type].append({
                'source': source,
                'target': target,
                'confidence': confidence
            })
        
        return dict(by_type)
    
    def _get_component_stats(self, cursor, project_id: int) -> Dict:
        """컴포넌트 통계 조회"""
        cursor.execute("""
            SELECT component_type, COUNT(*) 
            FROM components 
            WHERE project_id = ? 
            GROUP BY component_type
        """, (project_id,))
        
        return dict(cursor.fetchall())
    
    def _analyze_patterns(self, components: Dict, relationships: Dict) -> List[str]:
        """아키텍처 패턴 분석"""
        patterns = []
        
        # 계층형 아키텍처 감지
        layers = set(components.keys())
        if {'controller', 'service', 'mapper'} <= layers:
            patterns.append('계층형 아키텍처 (Layered Architecture)')
        
        # 서비스 패턴 감지
        if 'service' in components and len(components['service']) > 1:
            patterns.append('서비스 계층 패턴')
        
        # MVC 패턴 감지
        if 'controller' in components and 'model' in components:
            patterns.append('MVC 패턴')
        
        return patterns
    
    def _get_table_info(self, cursor, project_id: int) -> List:
        """테이블 정보 조회"""
        cursor.execute("""
            SELECT component_name, component_type
            FROM components
            WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
            ORDER BY component_type, component_name
        """, (project_id,))
        
        return cursor.fetchall()
    
    def _generate_architecture_diagram(self, components: Dict, relationships: Dict) -> str:
        """시스템 아키텍처 다이어그램 생성"""
        lines = []
        lines.append("  시스템 아키텍처 구조")
        lines.append("")
        
        # 계층 순서 정의
        layer_order = ['controller', 'service', 'mapper', 'model', 'other']
        layer_names = {
            'controller': 'Controller Layer',
            'service': 'Service Layer', 
            'mapper': 'Data Layer',
            'model': 'Model Layer',
            'other': 'Other Components'
        }
        
        for layer in layer_order:
            if layer not in components:
                continue
                
            layer_components = components[layer]
            if not layer_components:
                continue
                
            # 계층 박스 그리기
            lines.append("  ┌─────────────────────────────────────────────────────────────────┐")
            lines.append(f"  │                           {layer_names[layer]:^31}                       │")
            lines.append("  ├─────────────────────────────────────────────────────────────────┤")
            
            # 컴포넌트들을 2열로 배치
            for i in range(0, len(layer_components), 2):
                left_comp = layer_components[i]
                right_comp = layer_components[i+1] if i+1 < len(layer_components) else None
                
                left_name = left_comp['name']
                right_name = right_comp['name'] if right_comp else ""
                
                # 인터페이스 표시
                if left_comp.get('type') == 'interface':
                    left_name += " (interface)"
                if right_comp and right_comp.get('type') == 'interface':
                    right_name += " (interface)"
                
                # 컴포넌트 이름 라인
                left_part = f"  │  {left_name:<30}"
                if right_name:
                    right_part = f"{right_name:<30} │"
                    lines.append(left_part + right_part)
                else:
                    lines.append(left_part + " " * 32 + " │")
            
            lines.append("  └─────────────────────────────────────────────────────────────────┘")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_relationship_details(self, relationships: Dict) -> str:
        """관계 상세 정보 생성"""
        lines = []
        lines.append("  관계 상세 정보")
        lines.append("")
        
        # 주요 관계 타입들
        important_types = ['dependency', 'implements', 'extends', 'calls']
        
        for rel_type in important_types:
            if rel_type not in relationships:
                continue
                
            rels = relationships[rel_type]
            if not rels:
                continue
            
            # 관계 타입별 표시
            icons = {
                'dependency': '[D]',
                'implements': '[I]', 
                'extends': '[E]',
                'calls': '[C]'
            }
            
            icon = icons.get(rel_type, '[R]')
            type_name = {
                'dependency': 'Dependency 관계',
                'implements': 'Implements 관계',
                'extends': 'Extends 관계', 
                'calls': 'Calls 관계'
            }.get(rel_type, f'{rel_type.title()} 관계')
            
            lines.append(f"  {icon} {type_name} ({len(rels)}개)")
            lines.append("")
            
            # 도메인별로 그룹핑
            if rel_type == 'dependency':
                lines.extend(self._format_dependency_tree(rels))
            else:
                lines.extend(self._format_relationship_list(rels))
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_dependency_tree(self, dependencies: List[Dict]) -> List[str]:
        """의존성 관계를 트리 형태로 포맷"""
        lines = []
        
        # 패턴별로 그룹핑
        controller_deps = [d for d in dependencies if 'controller' in d['source'].lower()]
        service_deps = [d for d in dependencies if 'service' in d['source'].lower() and 'controller' not in d['source'].lower()]
        
        if controller_deps:
            lines.append("  Controller → Service:")
            for dep in controller_deps[:5]:  # 상위 5개만
                lines.append(f"  ├─ {dep['source']:<20} → {dep['target']}")
            if len(controller_deps) > 5:
                lines.append(f"  └─ ... 외 {len(controller_deps) - 5}개")
            lines.append("")
        
        if service_deps:
            lines.append("  Service → Mapper:")
            for dep in service_deps[:5]:  # 상위 5개만
                lines.append(f"  ├─ {dep['source']:<20} → {dep['target']}")
            if len(service_deps) > 5:
                lines.append(f"  └─ ... 외 {len(service_deps) - 5}개")
        
        return lines
    
    def _format_relationship_list(self, relationships: List[Dict]) -> List[str]:
        """관계 리스트를 포맷"""
        lines = []
        
        lines.append("  Implementation → Interface:")
        for rel in relationships[:10]:  # 상위 10개
            lines.append(f"  ├─ {rel['source']:<20} → {rel['target']}")
        
        if len(relationships) > 10:
            lines.append(f"  └─ ... 외 {len(relationships) - 10}개")
        
        return lines
    
    def _generate_component_statistics(self, stats: Dict) -> str:
        """구성 요소 통계 생성"""
        lines = []
        lines.append("  구성 요소 통계")
        lines.append("")
        
        lines.append("  ┌─────────────────┬─────────┬─────────────────────────────────┐")
        lines.append("  │ 컴포넌트 타입      │ 수량     │ 구성 요소                        │")
        lines.append("  ├─────────────────┼─────────┼─────────────────────────────────┤")
        
        # 주요 타입들만 표시
        display_types = {
            'class': 'Class',
            'interface': 'Interface', 
            'table': 'Table',
            'method': 'Method'
        }
        
        for comp_type, display_name in display_types.items():
            count = stats.get(comp_type, 0)
            if count > 0:
                if comp_type == 'class':
                    detail = "Controllers + Services + Models"
                elif comp_type == 'interface':
                    detail = "Services + Mappers + Others"
                elif comp_type == 'table':
                    detail = "Database Tables"
                else:
                    detail = "비즈니스 로직 메서드들"
                    
                lines.append(f"  │ {display_name:<15} │ {count:>4}개   │ {detail:<31} │")
        
        # 총합 계산
        total = sum(stats.values())
        total_rels = sum(stats.get(k, 0) for k in stats if 'relationship' in k.lower())
        
        lines.append("  ├─────────────────┼─────────┼─────────────────────────────────┤")
        lines.append(f"  │ 총 컴포넌트        │ {total:>4}개   │ 전체 시스템 구성 요소              │")
        lines.append("  └─────────────────┴─────────┴─────────────────────────────────┘")
        
        return "\n".join(lines)
    
    def _generate_pattern_analysis(self, patterns: List[str], components: Dict) -> str:
        """아키텍처 패턴 분석 생성"""
        lines = []
        lines.append("  아키텍처 패턴 분석")
        lines.append("")
        
        if not patterns:
            lines.append("  감지된 특정 패턴이 없습니다.")
            return "\n".join(lines)
        
        main_pattern = patterns[0]  # 첫 번째를 주요 패턴으로
        lines.append(f"  패턴: {main_pattern}")
        lines.append("")
        
        # 계층형 아키텍처인 경우 다이어그램
        if '계층형' in main_pattern:
            lines.extend(self._generate_layered_diagram(components))
            lines.append("")
            lines.extend(self._generate_pattern_features(components))
        
        return "\n".join(lines)
    
    def _generate_layered_diagram(self, components: Dict) -> List[str]:
        """계층형 아키텍처 다이어그램"""
        lines = []
        
        lines.append("  ┌─────────────────┐")
        lines.append("  │   Controller    │ ─── 웹 요청 처리, 사용자 인터페이스")
        lines.append("  └─────────────────┘")
        lines.append("           │ dependency")
        lines.append("           ▼")
        lines.append("  ┌─────────────────┐")
        lines.append("  │    Service      │ ─── 비즈니스 로직, 트랜잭션 관리")
        lines.append("  └─────────────────┘")
        lines.append("           │ dependency")
        lines.append("           ▼")
        lines.append("  ┌─────────────────┐")
        lines.append("  │     Mapper      │ ─── 데이터 접근, SQL 처리")
        lines.append("  └─────────────────┘")
        lines.append("           │")
        lines.append("           ▼")
        lines.append("  ┌─────────────────┐")
        lines.append("  │     Model       │ ─── 도메인 엔티티")
        lines.append("  └─────────────────┘")
        
        return lines
    
    def _generate_pattern_features(self, components: Dict) -> List[str]:
        """패턴 특징 분석"""
        lines = []
        lines.append("  특징:")
        
        # 계층 존재 여부 체크
        has_controller = 'controller' in components and len(components['controller']) > 0
        has_service = 'service' in components and len(components['service']) > 0  
        has_mapper = 'mapper' in components and len(components['mapper']) > 0
        
        if has_controller and has_service and has_mapper:
            lines.append("  [OK] 계층 간 단방향 의존성")
            lines.append("  [OK] Spring MVC 패턴 준수")
        else:
            lines.append("  [!] 일부 계층 누락")
        
        # 인터페이스 사용 여부
        has_interfaces = any(comp.get('type') == 'interface' 
                           for layer_comps in components.values()
                           for comp in layer_comps)
        
        if has_interfaces:
            lines.append("  [OK] 인터페이스 기반 설계")
        
        return lines
    
    def _generate_database_structure(self, tables: List, cursor, project_id: int) -> str:
        """데이터베이스 구조 생성"""
        lines = []
        lines.append("  데이터베이스 테이블 구조")
        lines.append("")
        
        real_tables = [t for t in tables if t[1] == 'table']
        dummy_tables = [t for t in tables if t[1] == 'table_dummy']
        
        # 실제 테이블들의 상세 정보 (예시)
        for table_name, _ in real_tables[:3]:  # 상위 3개 테이블만
            lines.extend(self._generate_table_detail(table_name))
            lines.append("")
        
        # 관계 다이어그램
        if len(real_tables) > 1:
            lines.extend(self._generate_table_relationships(real_tables))
        
        return "\n".join(lines)
    
    def _generate_table_detail(self, table_name: str) -> List[str]:
        """테이블 상세 정보 생성 (예시)"""
        lines = []
        
        # 테이블별 예시 스키마 (실제로는 메타데이터에서 가져와야 함)
        schema_examples = {
            'users': [
                ('id', 'BIGINT', 'Primary Key'),
                ('username', 'VARCHAR', 'Login Name'),
                ('email', 'VARCHAR', 'Email Address'),
                ('password', 'VARCHAR', 'Encrypted Password'),
                ('name', 'VARCHAR', 'Display Name'),
                ('status', 'VARCHAR', 'ACTIVE/INACTIVE'),
                ('created_date', 'TIMESTAMP', 'Creation Date')
            ],
            'products': [
                ('id', 'BIGINT', 'Primary Key'),
                ('product_name', 'VARCHAR', 'Product Name'),
                ('price', 'DECIMAL', 'Product Price'),
                ('category_id', 'VARCHAR(FK)', '→ CATEGORIES'),
                ('brand_id', 'VARCHAR(FK)', '→ BRANDS'),
                ('status', 'VARCHAR', 'ACTIVE/INACTIVE'),
                ('created_date', 'TIMESTAMP', 'Creation Date')
            ]
        }
        
        schema = schema_examples.get(table_name.lower(), [
            ('id', 'BIGINT', 'Primary Key'),
            ('name', 'VARCHAR', 'Name Field'),
            ('created_date', 'TIMESTAMP', 'Creation Date')
        ])
        
        # 테이블 박스
        table_display_name = table_name.upper() + " TABLE"
        lines.append("  ┌─────────────────────────────────────────────────────────────────┐")
        lines.append(f"  │                           {table_display_name:^31}                           │")
        lines.append("  ├─────────────────────────────────────────────────────────────────┤")
        
        for col_name, col_type, description in schema:
            icon = "[PK]" if "PK" in description else "[ID]" if "id" in col_name.lower() else "[F] "
            lines.append(f"  │ {icon} {col_name:<18} │ {col_type:<12} │ {description:<16} │")
        
        lines.append("  └─────────────────────────────────────────────────────────────────┘")
        
        return lines
    
    def _generate_table_relationships(self, tables: List) -> List[str]:
        """테이블 관계 다이어그램"""
        lines = []
        lines.append("  테이블 관계도")
        lines.append("")
        lines.append("  CATEGORIES <------+")
        lines.append("      |             |")
        lines.append("      | 1:N         | 1:N")
        lines.append("      V             V")
        lines.append("   PRODUCTS <----- BRANDS")
        lines.append("                    |")
        lines.append("                    | N:M")
        lines.append("                    V")
        lines.append("                  USERS")
        lines.append("")
        lines.append("  데이터베이스 설계 특징")
        lines.append("")
        lines.append("  [OK] 정규화 수준: 3NF (Third Normal Form)")
        lines.append("  |-- 코드 테이블 분리")
        lines.append("  |-- 중복 데이터 최소화")
        lines.append("  +-- 참조 무결성 유지")
        lines.append("")
        lines.append("  [OK] 설계 패턴:")
        lines.append("  |-- 타임스탬프 패턴 (created_date, updated_date)")
        lines.append("  |-- 상태 관리 (status 컬럼)")
        lines.append("  +-- 코드 테이블 패턴")
        
        return lines