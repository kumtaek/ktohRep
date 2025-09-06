#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메타정보 계층도 생성기
소스 코드 파일 간의 의존성 관계를 트리 구조로 분석하여 계층도를 생성합니다.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime
import sqlite3
from collections import defaultdict, deque

class HierarchyGenerator:
    """메타정보 계층도 생성기"""
    
    def __init__(self, db_path: str, project_name: str):
        """
        계층도 생성기 초기화
        
        Args:
            db_path: 메타데이터베이스 경로
            project_name: 프로젝트 이름
        """
        self.db_path = db_path
        self.project_name = project_name
        self.connection = None
        self.hierarchy_data = {}
        
    def connect_database(self):
        """데이터베이스에 연결"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return False
    
    def close_database(self):
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
    
    def analyze_file_hierarchy(self) -> Dict[str, Any]:
        """파일 계층 구조를 분석합니다."""
        if not self.connection:
            return {}
        
        try:
            # 파일 정보 조회
            files_query = """
            SELECT file_id, path, language, loc
            FROM files
            ORDER BY path
            """
            
            files = self.connection.execute(files_query).fetchall()
            
            # 클래스 정보 조회
            classes_query = """
            SELECT c.class_id, c.fqn, c.name, c.start_line, c.end_line, f.path
            FROM classes c
            JOIN files f ON c.file_id = f.file_id
            ORDER BY c.fqn
            """
            
            classes = self.connection.execute(classes_query).fetchall()
            
            # 메서드 정보 조회
            methods_query = """
            SELECT m.method_id, m.name, m.signature, c.fqn, f.path
            FROM methods m
            JOIN classes c ON m.class_id = c.class_id
            JOIN files f ON c.file_id = f.file_id
            ORDER BY c.fqn, m.name
            """
            
            methods = self.connection.execute(methods_query).fetchall()
            
            # 엣지(의존성) 정보 조회
            edges_query = """
            SELECT e.edge_id, e.src_type, e.dst_type, e.edge_kind, e.confidence,
                   f1.path as src_path, f2.path as dst_path
            FROM edges e
            JOIN files f1 ON e.src_id = f1.file_id
            JOIN files f2 ON e.dst_id = f2.file_id
            WHERE e.edge_kind IN ('import', 'call', 'extend', 'implement')
            ORDER BY e.confidence DESC
            """
            
            edges = self.connection.execute(edges_query).fetchall()
            
            # 계층 구조 구성
            hierarchy = self._build_hierarchy(files, classes, methods, edges)
            
            return hierarchy
            
        except Exception as e:
            print(f"계층 구조 분석 실패: {e}")
            return {}
    
    def _build_hierarchy(self, files: List, classes: List, methods: List, edges: List) -> Dict[str, Any]:
        """계층 구조를 구성합니다."""
        hierarchy = {
            'project_name': self.project_name,
            'analysis_time': datetime.now().isoformat(),
            'files': {},
            'classes': {},
            'methods': {},
            'dependencies': {},
            'layers': {}
        }
        
        # 파일 계층 구성
        for file in files:
            file_path = file['path']
            file_info = {
                'id': file['file_id'],
                'language': file['language'],
                'loc': file['loc'],
                'classes': [],
                'dependencies': [],
                'dependents': []
            }
            hierarchy['files'][file_path] = file_info
        
        # 클래스 계층 구성
        for cls in classes:
            class_fqn = cls['fqn']
            file_path = cls['path']
            class_info = {
                'id': cls['class_id'],
                'name': cls['name'],
                'file': file_path,
                'start_line': cls['start_line'],
                'end_line': cls['end_line'],
                'methods': [],
                'dependencies': [],
                'dependents': []
            }
            hierarchy['classes'][class_fqn] = class_info
            
            # 파일에 클래스 추가
            if file_path in hierarchy['files']:
                hierarchy['files'][file_path]['classes'].append(class_fqn)
        
        # 메서드 계층 구성
        for method in methods:
            method_name = method['name']
            class_fqn = method['fqn']
            file_path = method['path']
            method_info = {
                'id': method['method_id'],
                'name': method_name,
                'signature': method['signature'],
                'class': class_fqn,
                'file': file_path,
                'dependencies': [],
                'dependents': []
            }
            hierarchy['methods'][f"{class_fqn}.{method_name}"] = method_info
            
            # 클래스에 메서드 추가
            if class_fqn in hierarchy['classes']:
                hierarchy['classes'][class_fqn]['methods'].append(method_name)
        
        # 의존성 관계 구성
        for edge in edges:
            src_path = edge['src_path']
            dst_path = edge['dst_path']
            edge_kind = edge['edge_kind']
            confidence = edge['confidence']
            
            dependency_info = {
                'type': edge_kind,
                'confidence': confidence,
                'source': src_path,
                'target': dst_path
            }
            
            # 파일 간 의존성
            if src_path in hierarchy['files']:
                hierarchy['files'][src_path]['dependencies'].append(dst_path)
            if dst_path in hierarchy['files']:
                hierarchy['files'][dst_path]['dependents'].append(src_path)
            
            # 의존성 목록에 추가
            dependency_key = f"{src_path} -> {dst_path}"
            hierarchy['dependencies'][dependency_key] = dependency_info
        
        # 레이어 구조 분석
        hierarchy['layers'] = self._analyze_layers(hierarchy['files'])
        
        return hierarchy
    
    def _analyze_layers(self, files: Dict) -> Dict[str, List[str]]:
        """파일들을 레이어별로 분류합니다."""
        layers = {
            'controller': [],
            'service': [],
            'mapper': [],
            'entity': [],
            'config': [],
            'util': [],
            'other': []
        }
        
        for file_path, file_info in files.items():
            file_name = Path(file_path).name.lower()
            
            if any(keyword in file_name for keyword in ['controller', 'servlet', 'action']):
                layers['controller'].append(file_path)
            elif any(keyword in file_path for keyword in ['service', 'manager', 'handler']):
                layers['service'].append(file_path)
            elif any(keyword in file_path for keyword in ['mapper', 'dao', 'repository']):
                layers['mapper'].append(file_path)
            elif any(keyword in file_path for keyword in ['entity', 'model', 'dto', 'vo']):
                layers['entity'].append(file_path)
            elif any(keyword in file_path for keyword in ['config', 'configuration', 'setup']):
                layers['config'].append(file_path)
            elif any(keyword in file_path for keyword in ['util', 'helper', 'tool']):
                layers['util'].append(file_path)
            else:
                layers['other'].append(file_path)
        
        return layers
    
    def generate_markdown_report(self, output_path: str = None) -> str:
        """계층도 마크다운 리포트를 생성합니다."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 프로젝트 report 폴더에 저장
            project_report_dir = Path(f"./project/{self.project_name}/report")
            project_report_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(project_report_dir / f"메타정보_계층도분석리포트_{timestamp}.md")
        
        hierarchy = self.analyze_file_hierarchy()
        
        # 마크다운 내용 생성
        markdown_content = self._create_markdown_content(hierarchy)
        
        # 파일 저장
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"계층도 리포트가 생성되었습니다: {output_path}")
        except Exception as e:
            print(f"파일 저장 실패: {e}")
        
        return output_path
    
    def _create_markdown_content(self, hierarchy: Dict[str, Any]) -> str:
        """마크다운 내용을 생성합니다."""
        content = []
        
        # 헤더
        content.append(f"# 🏗️ {self.project_name} 메타정보 계층도 분석 리포트")
        content.append("")
        content.append(f"**📅 생성 시간**: {hierarchy['analysis_time']}")
        content.append(f"**🔍 프로젝트**: {self.project_name}")
        content.append("")
        
        # 요약 정보 (카드 형태)
        content.append("## 📊 분석 요약")
        content.append("")
        content.append("| 📁 파일 | 🏛️ 클래스 | ⚙️ 메서드 | 🔗 의존성 |")
        content.append("|---------|-----------|-----------|-----------|")
        content.append(f"| **{len(hierarchy['files'])}개** | **{len(hierarchy['classes'])}개** | **{len(hierarchy['methods'])}개** | **{len(hierarchy['dependencies'])}개** |")
        content.append("")
        
        # 레이어별 구조 (개선된 형태)
        content.append("## 🏗️ 레이어별 구조")
        content.append("")
        
        # 레이어별 통계 계산
        layer_stats = {}
        for layer_name, files in hierarchy['layers'].items():
            if files:
                total_classes = sum(len(hierarchy['files'][f]['classes']) for f in files)
                total_methods = sum(len(hierarchy['files'][f]['classes']) * 3 for f in files)  # 추정치
                total_loc = sum(hierarchy['files'][f]['loc'] for f in files)
                layer_stats[layer_name] = {
                    'files': len(files),
                    'classes': total_classes,
                    'methods': total_methods,
                    'loc': total_loc
                }
        
        # 레이어별 상세 정보
        for layer_name, files in sorted(hierarchy['layers'].items()):
            if files:
                stats = layer_stats.get(layer_name, {})
                content.append(f"### 🎯 {layer_name.title()} 레이어")
                content.append("")
                content.append(f"**📊 통계**: {stats.get('files', 0)}개 파일, {stats.get('classes', 0)}개 클래스, {stats.get('loc', 0)}줄")
                content.append("")
                
                # 파일들을 그룹별로 정리
                file_groups = defaultdict(list)
                for file_path in files:
                    dir_path = str(Path(file_path).parent)
                    file_name = Path(file_path).name
                    file_groups[dir_path].append(file_name)
                
                for dir_path, file_names in sorted(file_groups.items()):
                    if dir_path != '.':
                        content.append(f"**📁 {dir_path}**")
                        content.append("")
                        for file_name in sorted(file_names):
                            file_info = hierarchy['files'].get(file_path, {})
                            class_count = len(file_info.get('classes', []))
                            loc_count = file_info.get('loc', 0)
                            content.append(f"  - `{file_name}` ({class_count}클래스, {loc_count}줄)")
                        content.append("")
                    else:
                        for file_name in sorted(file_names):
                            file_info = hierarchy['files'].get(file_path, {})
                            class_count = len(file_info.get('classes', []))
                            loc_count = file_info.get('loc', 0)
                            content.append(f"  - `{file_name}` ({class_count}클래스, {loc_count}줄)")
                        content.append("")
        
        # 파일 계층도 (개선된 트리 구조)
        content.append("## 📁 파일 계층도")
        content.append("")
        content.append("### 🌳 트리 구조")
        content.append("```")
        content.extend(self._generate_improved_tree_structure(hierarchy['files']))
        content.append("```")
        content.append("")
        
        # 의존성 관계 (개선된 테이블)
        if hierarchy['dependencies']:
            content.append("## 🔗 의존성 관계")
            content.append("")
            content.append("### 📋 의존성 테이블")
            content.append("")
            content.append("| 🔴 소스 파일 | 🟢 타겟 파일 | 🔗 관계 유형 | 📊 신뢰도 | 📁 소스 경로 | 📁 타겟 경로 |")
            content.append("|---------------|---------------|-------------|-----------|-------------|-------------|")
            
            # 의존성을 신뢰도 순으로 정렬
            sorted_deps = sorted(hierarchy['dependencies'].items(), 
                               key=lambda x: x[1]['confidence'], reverse=True)
            
            for dep_key, dep_info in sorted_deps:
                source = Path(dep_info['source']).name
                target = Path(dep_info['target']).name
                dep_type = self._get_dependency_icon(dep_info['type']) + " " + dep_info['type']
                confidence = f"{dep_info['confidence']:.2f}"
                source_path = str(Path(dep_info['source']).parent)
                target_path = str(Path(dep_info['target']).parent)
                
                content.append(f"| `{source}` | `{target}` | {dep_type} | **{confidence}** | `{source_path}` | `{target_path}` |")
            
            content.append("")
            
            # 의존성 통계
            dep_types = {}
            for dep_info in hierarchy['dependencies'].values():
                dep_type = dep_info['type']
                dep_types[dep_type] = dep_types.get(dep_type, 0) + 1
            
            content.append("### 📈 의존성 통계")
            content.append("")
            for dep_type, count in sorted(dep_types.items()):
                icon = self._get_dependency_icon(dep_type)
                content.append(f"- {icon} **{dep_type}**: {count}개")
            content.append("")
        
        # Mermaid 다이어그램 (개선된 형태)
        content.append("## 📈 Mermaid 다이어그램")
        content.append("")
        
        if hierarchy['dependencies']:
            content.append("### 🔗 파일 의존성 그래프")
            content.append("```mermaid")
            content.extend(self._generate_improved_mermaid_graph(hierarchy['files'], hierarchy['dependencies']))
            content.append("```")
            content.append("")
        
        content.append("### 🏗️ 레이어 구조")
        content.append("```mermaid")
        content.extend(self._generate_improved_layer_mermaid(hierarchy['layers']))
        content.append("```")
        content.append("")
        
        # 상세 정보 (개선된 형태)
        content.append("## 📋 상세 정보")
        content.append("")
        
        # 파일별 상세 정보 (카테고리별로 그룹화)
        content.append("### 📁 파일별 상세 정보")
        content.append("")
        
        for layer_name, files in sorted(hierarchy['layers'].items()):
            if files:
                content.append(f"#### 🎯 {layer_name.title()} 레이어")
                content.append("")
                
                for file_path in sorted(files):
                    file_info = hierarchy['files'][file_path]
                    file_name = Path(file_path).name
                    file_ext = Path(file_path).suffix
                    
                    # 파일 타입별 아이콘
                    file_icon = self._get_file_icon(file_ext)
                    
                    content.append(f"##### {file_icon} {file_name}")
                    content.append("")
                    content.append(f"| 속성 | 값 |")
                    content.append(f"|------|----|")
                    content.append(f"| **📁 경로** | `{file_path}` |")
                    content.append(f"| **🔤 언어** | {file_info['language']} |")
                    content.append(f"| **📏 라인 수** | {file_info['loc']}줄 |")
                    content.append(f"| **🏛️ 클래스 수** | {len(file_info['classes'])}개 |")
                    content.append(f"| **🔗 의존성 수** | {len(file_info['dependencies'])}개 |")
                    content.append(f"| **🎯 의존 대상 수** | {len(file_info['dependents'])}개 |")
                    content.append("")
                    
                    if file_info['classes']:
                        content.append("**🏛️ 포함 클래스**:")
                        for class_fqn in file_info['classes']:
                            content.append(f"- `{class_fqn}`")
                        content.append("")
                    
                    if file_info['dependencies']:
                        content.append("**🔗 의존 파일**:")
                        for dep_file in file_info['dependencies']:
                            dep_name = Path(dep_file).name
                            dep_icon = self._get_file_icon(Path(dep_file).suffix)
                            content.append(f"- {dep_icon} `{dep_name}`")
                        content.append("")
                    
                    content.append("---")
                    content.append("")
        
        # 푸터
        content.append("## 🎉 분석 완료")
        content.append("")
        content.append(f"이 리포트는 **{self.project_name}** 프로젝트의 메타정보를 기반으로 생성되었습니다.")
        content.append("")
        content.append("**📊 주요 특징**:")
        content.append("- 🏗️ 레이어별 구조 분석")
        content.append("- 🔗 파일 간 의존성 관계")
        content.append("- 📈 Mermaid 다이어그램 시각화")
        content.append("- 📋 상세한 메타정보 제공")
        content.append("")
        content.append(f"**⏰ 생성 시간**: {hierarchy['analysis_time']}")
        content.append("")
        content.append("---")
        content.append("*이 리포트는 SourceAnalyzer Phase1 시스템에 의해 자동 생성되었습니다.*")
        
        return "\n".join(content)
    
    def _get_dependency_icon(self, dep_type: str) -> str:
        """의존성 타입별 아이콘을 반환합니다."""
        icons = {
            'import': '📥',
            'call': '📞',
            'extend': '🔗',
            'implement': '⚡',
            'use': '🔧',
            'create': '➕',
            'read': '📖',
            'write': '✏️'
        }
        return icons.get(dep_type, '🔗')
    
    def _get_file_icon(self, file_ext: str) -> str:
        """파일 확장자별 아이콘을 반환합니다."""
        icons = {
            '.java': '☕',
            '.jsp': '🌐',
            '.xml': '📄',
            '.sql': '🗄️',
            '.properties': '⚙️',
            '.jar': '📦',
            '.class': '🎯',
            '.html': '🌍',
            '.css': '🎨',
            '.js': '📜'
        }
        return icons.get(file_ext.lower(), '📄')
    
    def _generate_improved_tree_structure(self, files: Dict) -> List[str]:
        """개선된 트리 구조를 생성합니다."""
        tree_lines = []
        
        # 프로젝트 루트
        tree_lines.append(f"🏗️ {self.project_name}/")
        
        # 파일들을 경로별로 그룹화
        path_groups = defaultdict(list)
        for file_path in files.keys():
            path_parts = Path(file_path).parts
            if len(path_parts) > 1:
                group_key = "/".join(path_parts[:-1])
                path_groups[group_key].append(Path(file_path).name)
        
        # 그룹별로 트리 생성 (개선된 형태)
        for group_path, file_names in sorted(path_groups.items()):
            tree_lines.append(f"📁 {group_path}/")
            for i, file_name in enumerate(sorted(file_names)):
                file_ext = Path(file_name).suffix
                file_icon = self._get_file_icon(file_ext)
                
                if i == len(file_names) - 1:
                    tree_lines.append(f"    └── {file_icon} {file_name}")
                else:
                    tree_lines.append(f"    ├── {file_icon} {file_name}")
        
        return tree_lines
    
    def _generate_improved_mermaid_graph(self, files: Dict, dependencies: Dict) -> List[str]:
        """개선된 Mermaid 그래프를 생성합니다."""
        mermaid_lines = []
        mermaid_lines.append("graph TD")
        
        # 파일 노드 생성 (중복 제거, 고유 ID 생성)
        file_id_map = {}  # 파일 경로 -> 고유 ID 매핑
        seen_files = set()
        used_node_ids = set()  # 전역 ID 추적으로 중복 방지 강화
        
        for file_path, file_info in files.items():
            # 중복 파일 경로 완전 제거
            if file_path in seen_files:
                continue
            seen_files.add(file_path)
            
            file_name = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()
            
            # 고유 ID 생성 (파일명 기반, 중복 방지)
            base_name = Path(file_path).stem
            safe_name = base_name.replace('-', '_').replace('.', '_').replace(' ', '_')
            
            # 경로에서 레이어 정보 추출
            path_parts = [part.lower() for part in Path(file_path).parts]
            if any('controller' in part for part in path_parts):
                layer_prefix = 'controller'
            elif any('service' in part for part in path_parts):
                layer_prefix = 'service'
            elif any('mapper' in part for part in path_parts):
                layer_prefix = 'mapper'
            elif any(part in ['entity', 'model', 'dto', 'vo'] for part in path_parts):
                layer_prefix = 'entity'
            elif any('config' in part for part in path_parts):
                layer_prefix = 'config'
            elif any('util' in part for part in path_parts):
                layer_prefix = 'util'
            else:
                layer_prefix = 'other'
            
            # 보다 강화된 고유 ID 생성 (파일명과 경로 해시 포함)
            path_hash = abs(hash(file_path)) % 10000  # 4자리 해시
            
            if file_ext == '.xml' and 'usermapper' in base_name.lower():
                file_id = f"{layer_prefix}_UserMapperXml_{path_hash}"
            elif file_ext == '.java' and 'usermapper' in base_name.lower():
                file_id = f"{layer_prefix}_UserMapperJava_{path_hash}"
            elif file_ext == '.xml' and 'integratedmapper' in base_name.lower():
                file_id = f"{layer_prefix}_IntegratedMapperXml_{path_hash}"
            elif file_ext == '.java' and 'integratedmapper' in base_name.lower():
                file_id = f"{layer_prefix}_IntegratedMapperJava_{path_hash}"
            elif file_ext == '.jsp' and 'userlist' in base_name.lower():
                file_id = f"{layer_prefix}_UserListJsp_{path_hash}"
            else:
                file_id = f"{layer_prefix}_{safe_name}_{file_ext.replace('.', '')}_{path_hash}"
            
            # 중복 ID 방지 (더 강화된 방식)
            counter = 1
            original_file_id = file_id
            while file_id in used_node_ids:
                file_id = f"{original_file_id}_{counter}"
                counter += 1
            
            used_node_ids.add(file_id)
            file_id_map[file_path] = file_id
            
            # 파일 타입별 표시 (라벨도 고유하게)
            unique_label = f"{file_name} ({path_hash})"
            if file_ext == '.java':
                mermaid_lines.append(f"    {file_id}[\"Java: {unique_label}\"]:::java")
            elif file_ext == '.jsp':
                mermaid_lines.append(f"    {file_id}[\"JSP: {unique_label}\"]:::jsp")
            elif file_ext == '.xml':
                mermaid_lines.append(f"    {file_id}[\"XML: {unique_label}\"]:::xml")
            elif file_ext == '.sql':
                mermaid_lines.append(f"    {file_id}[\"SQL: {unique_label}\"]:::sql")
            else:
                mermaid_lines.append(f"    {file_id}[\"File: {unique_label}\"]:::other")
        
        # 의존성 관계 생성 (중복 제거)
        seen_edges = set()
        for source_path, deps in dependencies.items():
            for dep_info in deps:
                target_path = dep_info['target']
                dep_type = dep_info['type']
                confidence = dep_info.get('confidence', 0.5)
                
                edge_key = f"{source_path}_{target_path}_{dep_type}"
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    
                    # 파일 ID 찾기
                    source_id = file_id_map.get(source_path)
                    target_id = file_id_map.get(target_path)
                    
                    if source_id and target_id:
                        # 신뢰도에 따른 스타일 적용
                        if confidence >= 0.8:
                            style = ":::high-confidence"
                        elif confidence >= 0.5:
                            style = ":::medium-confidence"
                        else:
                            style = ":::low-confidence"
                        
                        mermaid_lines.append(f"    {source_id} -->|{dep_type}| {target_id}{style}")
        
        mermaid_lines.append("")
        mermaid_lines.append("    classDef java fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
        mermaid_lines.append("    classDef jsp fill:#f3e5f5,stroke:#4a148c,stroke-width:2px")
        mermaid_lines.append("    classDef xml fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px")
        mermaid_lines.append("    classDef sql fill:#fff3e0,stroke:#e65100,stroke-width:2px")
        mermaid_lines.append("    classDef other fill:#f5f5f5,stroke:#424242,stroke-width:2px")
        mermaid_lines.append("    classDef high-confidence fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px")
        mermaid_lines.append("    classDef medium-confidence fill:#fff9c4,stroke:#f57f17,stroke-width:2px")
        mermaid_lines.append("    classDef low-confidence fill:#ffcdd2,stroke:#c62828,stroke-width:1px")
        
        return mermaid_lines
    
    def _generate_improved_layer_mermaid(self, layers: Dict) -> List[str]:
        """컴팩트하고 보기 좋은 레이어별 Mermaid 다이어그램을 생성합니다."""
        mermaid_lines = []
        mermaid_lines.append("graph TD")
        
        # 전역 노드 ID 추적 (중복 방지)
        used_node_ids = set()
        seen_file_paths = set()  # 중복 파일 경로 추적
        layer_order = ['controller', 'service', 'mapper', 'entity', 'config', 'util', 'other']
        
        # 계층별로 순서대로 배치
        for layer_name in layer_order:
            files = layers.get(layer_name, [])
            if files:
                # 중복 파일 제거
                unique_files = []
                for file_path in files:
                    if file_path not in seen_file_paths:
                        seen_file_paths.add(file_path)
                        unique_files.append(file_path)
                
                if not unique_files:  # 중복 제거 후 파일이 없으면 스킵
                    continue
                
                # 레이어 이름을 짧게 표시 (호환성을 위해 라벨 제거)
                layer_title = layer_name.title()
                layer_id = f"Layer_{layer_name}"
                mermaid_lines.append(f"    %% {layer_title} Layer")
                mermaid_lines.append(f"    subgraph {layer_id}[\"{layer_title}\"]")
                
                # 파일들을 간단하게 나열 (디렉토리 그룹화 제거)
                for file_path in sorted(unique_files):
                    file_name = Path(file_path).name
                    file_ext = Path(file_path).suffix.lower()
                    base_name = Path(file_path).stem
                    
                    # 파일명 단축 (확장자별 접두사 제거)
                    short_name = base_name.replace('Controller', 'Ctrl') \
                                         .replace('Service', 'Svc') \
                                         .replace('Mapper', 'Map') \
                                         .replace('Configuration', 'Config') \
                                         .replace('Util', 'U')
                    
                    # 고유 ID 생성 (파일 경로 해시 포함)
                    safe_name = base_name.replace('-', '_').replace('.', '_').replace(' ', '_')
                    path_hash = abs(hash(file_path)) % 10000
                    
                    # 파일 확장자에 따른 ID 구분 (더 강화된 방식)
                    if file_ext == '.xml' and 'usermapper' in base_name.lower():
                        file_id = f"{layer_name}_UserMapperXml_{path_hash}"
                    elif file_ext == '.java' and 'usermapper' in base_name.lower():
                        file_id = f"{layer_name}_UserMapperJava_{path_hash}"
                    elif file_ext == '.xml' and 'integratedmapper' in base_name.lower():
                        file_id = f"{layer_name}_IntegratedMapperXml_{path_hash}"
                    elif file_ext == '.java' and 'integratedmapper' in base_name.lower():
                        file_id = f"{layer_name}_IntegratedMapperJava_{path_hash}"
                    elif file_ext == '.jsp' and 'userlist' in base_name.lower():
                        file_id = f"{layer_name}_UserListJsp_{path_hash}"
                    else:
                        file_id = f"{layer_name}_{safe_name}_{file_ext.replace('.', '')}_{path_hash}"
                    
                    # 중복 ID 방지 (더 강화된 방식)
                    counter = 1
                    original_file_id = file_id
                    while file_id in used_node_ids:
                        file_id = f"{original_file_id}_{counter}"
                        counter += 1
                    used_node_ids.add(file_id)
                    
                    # 고유한 라벨 생성 (경로 정보 포함으로 중복 방지)
                    path_parts = Path(file_path).parts
                    if len(path_parts) > 2:
                        # 상위 폴더명을 포함하여 라벨 고유성 확보
                        parent_dir = path_parts[-2] if len(path_parts) > 1 else ""
                        unique_label = f"{short_name}.{file_ext.replace('.', '')} ({parent_dir})"
                    else:
                        unique_label = f"{short_name}.{file_ext.replace('.', '')}"
                    
                    if file_ext == '.java':
                        mermaid_lines.append(f"        {file_id}[\"{unique_label}\"]:::javaStyle")
                    elif file_ext == '.jsp':
                        mermaid_lines.append(f"        {file_id}[\"{unique_label}\"]:::jspStyle")
                    elif file_ext == '.xml':
                        mermaid_lines.append(f"        {file_id}[\"{unique_label}\"]:::xmlStyle")
                    else:
                        mermaid_lines.append(f"        {file_id}[\"{unique_label}\"]:::defaultStyle")
                
                mermaid_lines.append("    end")
                mermaid_lines.append("")
        
        # 계층간 의존성 화살표 추가 (실제 노드간 연결)
        layer_connections = []
        
        # Controller -> Service 대표 연결
        if layers.get('controller') and layers.get('service'):
            # 각 레이어의 첫 번째 파일로 대표 연결
            ctrl_files = list(layers['controller'])
            svc_files = list(layers['service'])
            
            if ctrl_files and svc_files:
                # 대표 파일의 ID 생성 (기존 로직과 동일하게)
                ctrl_file = ctrl_files[0]
                svc_file = svc_files[0]
                
                ctrl_hash = abs(hash(ctrl_file)) % 10000
                svc_hash = abs(hash(svc_file)) % 10000
                
                ctrl_base = Path(ctrl_file).stem.replace('-', '_').replace('.', '_').replace(' ', '_')
                svc_base = Path(svc_file).stem.replace('-', '_').replace('.', '_').replace(' ', '_')
                
                ctrl_id = f"controller_{ctrl_base}_java_{ctrl_hash}"
                svc_id = f"service_{svc_base}_java_{svc_hash}"
                
                layer_connections.append(f"    {ctrl_id} -.-> {svc_id}")
        
        # Service -> Mapper 대표 연결
        if layers.get('service') and layers.get('mapper'):
            svc_files = list(layers['service'])
            mapper_files = list(layers['mapper'])
            
            if svc_files and mapper_files:
                # 대표 파일의 ID 생성
                svc_file = svc_files[0]
                mapper_file = mapper_files[0]
                
                svc_hash = abs(hash(svc_file)) % 10000
                mapper_hash = abs(hash(mapper_file)) % 10000
                
                svc_base = Path(svc_file).stem.replace('-', '_').replace('.', '_').replace(' ', '_')
                mapper_base = Path(mapper_file).stem.replace('-', '_').replace('.', '_').replace(' ', '_')
                
                svc_id = f"service_{svc_base}_java_{svc_hash}"
                
                # Mapper는 java/xml 구분
                mapper_ext = Path(mapper_file).suffix.lower()
                if mapper_ext == '.xml' and 'usermapper' in mapper_base.lower():
                    mapper_id = f"mapper_UserMapperXml_{mapper_hash}"
                elif mapper_ext == '.java' and 'usermapper' in mapper_base.lower():
                    mapper_id = f"mapper_UserMapperJava_{mapper_hash}"
                else:
                    mapper_id = f"mapper_{mapper_base}_{mapper_ext.replace('.', '')}_{mapper_hash}"
                
                layer_connections.append(f"    {svc_id} -.-> {mapper_id}")
        
        # 연결이 있을 때만 추가
        if layer_connections:
            mermaid_lines.append("")
            mermaid_lines.append("    %% Layer Dependencies (Representative Node Connections)")
            mermaid_lines.extend(layer_connections)
        
        mermaid_lines.append("")
        
        # 스타일 정의 (Material Design 표준 색상)
        mermaid_lines.append("    classDef javaStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px")
        mermaid_lines.append("    classDef jspStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px")
        mermaid_lines.append("    classDef xmlStyle fill:#e8f5e9,stroke:#388e3c,stroke-width:2px")
        mermaid_lines.append("    classDef defaultStyle fill:#f5f5f5,stroke:#616161,stroke-width:2px")
        
        return mermaid_lines
    
    def _get_layer_icon(self, layer_name: str) -> str:
        """레이어별 아이콘을 반환합니다."""
        icons = {
            'controller': '🎮',
            'service': '⚙️',
            'mapper': '🗺️',
            'entity': '🏗️',
            'config': '⚙️',
            'util': '🔧',
            'other': '📁'
        }
        return icons.get(layer_name, '📁')


def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) < 3:
        print("사용법: python hierarchy_generator.py <db_path> <project_name> [output_path]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    project_name = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    generator = HierarchyGenerator(db_path, project_name)
    
    if generator.connect_database():
        try:
            output_file = generator.generate_markdown_report(output_path)
            print(f"계층도 분석이 완료되었습니다: {output_file}")
        finally:
            generator.close_database()
    else:
        print("데이터베이스 연결에 실패했습니다.")


if __name__ == "__main__":
    main()
