#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
컴포넌트 보고서 생성기 - 컴포넌트 구조를 마크다운 보고서로 생성
"""

from typing import List
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentReportGenerator:
    """컴포넌트 보고서 생성기"""
    
    def __init__(self):
        self.report_content = []
    
    def generate_report(self, project_structure, top_n: int = None) -> str:
        """컴포넌트 구조 보고서 생성"""
        logger.info("컴포넌트 보고서 생성 시작")
        
        self.report_content = []
        self.top_n = top_n  # Top N 제한 설정
        
        # 헤더 생성
        self._generate_header(project_structure)
        
        # 전체 아키텍처 구조 생성
        self._generate_architecture_overview(project_structure)
        
        # 계층별 상세 구조 생성
        self._generate_layer_details(project_structure)
        
        # 컴포넌트 상세 정보 생성
        self._generate_component_details(project_structure)
        
        # 통계 정보 생성
        self._generate_statistics(project_structure)
        
        # 푸터 생성
        self._generate_footer(project_structure)
        
        report_text = "\n".join(self.report_content)
        logger.info(f"컴포넌트 보고서 생성 완료: {len(report_text)} 문자")
        
        return report_text
    
    def _generate_header(self, project_structure):
        """헤더 생성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.report_content.extend([
            f"# {project_structure.project_name} 프로젝트 컴포넌트 명세서",
            "",
            f"**생성일시**: {current_time}",
            f"**분석 시간**: {project_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**총 컴포넌트 수**: {project_structure.total_components}개",
            "",
            "---",
            ""
        ])
    
    def _generate_architecture_overview(self, project_structure):
        """전체 아키텍처 구조 생성"""
        self.report_content.extend([
            "## 🏗️ 전체 아키텍처 구조",
            "",
            "```",
            "┌─────────────────────┐",
            f"│ {project_structure.project_name} 프로젝트 │",
            "│ (Java Web App)      │",
            "└─────────────────────┘",
            "         ↓",
            "┌─────────────────────┐",
            "│ Presentation        │",
            "│ (Controller+View)   │",
            "└─────────────────────┘",
            "         ↓",
            "┌─────────────────────┐",
            "│ Business            │",
            "│ (Service+Util)      │",
            "└─────────────────────┘",
            "         ↓",
            "┌─────────────────────┐",
            "│ Data Access         │",
            "│ (Mapper+DAO)        │",
            "└─────────────────────┘",
            "         ↓",
            "┌─────────────────────┐",
            "│ Infrastructure      │",
            "│ (Config+DB)         │",
            "└─────────────────────┘",
            "```",
            "",
            "### 📊 계층별 컴포넌트 분포",
            ""
        ])
        
        # 계층별 통계 테이블
        self.report_content.append("| 계층 | 컴포넌트 수 | 주요 타입 |")
        self.report_content.append("|------|-------------|-----------|")
        
        for layer in project_structure.layers:
            component_count = len(layer.components)
            main_types = self._get_main_types(layer.components)
            self.report_content.append(f"| {layer.name} | {component_count}개 | {main_types} |")
        
        self.report_content.extend(["", "---", ""])
    
    def _generate_layer_details(self, project_structure):
        """계층별 상세 구조 생성"""
        self.report_content.extend([
            "## 📋 계층별 상세 구조",
            ""
        ])
        
        for i, layer in enumerate(project_structure.layers, 1):
            self.report_content.extend([
                f"### {i}. {layer.name} ({layer.description})",
                ""
            ])
            
            # 계층별 컴포넌트 그룹화
            type_groups = self._group_by_type(layer.components)
            
            for component_type, components in type_groups.items():
                # Top N 제한 적용
                if self.top_n and len(components) > self.top_n:
                    self.report_content.extend([
                        f"#### {component_type}s (Top {self.top_n}개 표시, 전체 {len(components)}개)",
                        ""
                    ])
                    display_components = components[:self.top_n]
                else:
                    self.report_content.extend([
                        f"#### {component_type}s",
                        ""
                    ])
                    display_components = components
                
                for component in display_components:
                    self.report_content.extend([
                        f"- **{component.name}**",
                        f"  - {component.description}",
                        f"  - 경로: `{component.file_path}`"
                    ])
                    
                    if component.methods:
                        methods_str = ", ".join(component.methods[:5])
                        self.report_content.append(f"  - 주요 메서드: {methods_str}")
                    
                    self.report_content.append("")
                
                # Top N 제한으로 숨겨진 컴포넌트가 있는 경우 안내
                if self.top_n and len(components) > self.top_n:
                    hidden_count = len(components) - self.top_n
                    self.report_content.extend([
                        f"*... 및 {hidden_count}개 추가 {component_type} 컴포넌트*",
                        ""
                    ])
            
            self.report_content.append("---")
            self.report_content.append("")
    
    def _generate_component_details(self, project_structure):
        """컴포넌트 상세 정보 생성"""
        self.report_content.extend([
            "## 🔍 상세 컴포넌트 구조",
            ""
        ])
        
        for layer in project_structure.layers:
            self.report_content.extend([
                f"### {layer.name} 상세 구조",
                ""
            ])
            
            # 계층별 컴포넌트를 박스 형태로 표시
            type_groups = self._group_by_type(layer.components)
            
            for component_type, components in type_groups.items():
                # Top N 제한 적용
                if self.top_n and len(components) > self.top_n:
                    self.report_content.extend([
                        f"#### {component_type}s (Top {self.top_n}개 표시, 전체 {len(components)}개)",
                        ""
                    ])
                    display_components = components[:self.top_n]
                else:
                    self.report_content.extend([
                        f"#### {component_type}s",
                        ""
                    ])
                    display_components = components
                
                # 컴포넌트 목록을 간단한 형태로 표시 (박스 대신)
                for component in display_components:
                    # 텍스트 길이 제한 (더 짧게)
                    name_display = component.name[:25] + ("..." if len(component.name) > 25 else "")
                    desc_display = component.description[:30] + ("..." if len(component.description) > 30 else "")
                    path_display = component.file_path[:25] + ("..." if len(component.file_path) > 25 else "")
                    
                    self.report_content.extend([
                        f"**{name_display}**",
                        f"- {desc_display}",
                        f"- `{path_display}`"
                    ])
                    
                    if component.methods:
                        methods_str = ", ".join(component.methods[:2])  # 3개에서 2개로 줄임
                        if len(methods_str) > 35:
                            methods_str = methods_str[:32] + "..."
                        self.report_content.append(f"- {methods_str}")
                    
                    self.report_content.append("")
                
                # Top N 제한으로 숨겨진 컴포넌트가 있는 경우 안내
                if self.top_n and len(components) > self.top_n:
                    hidden_count = len(components) - self.top_n
                    self.report_content.extend([
                        f"*... 및 {hidden_count}개 추가 {component_type} 컴포넌트*",
                        ""
                    ])
            
            self.report_content.append("---")
            self.report_content.append("")
    
    def _generate_statistics(self, project_structure):
        """통계 정보 생성"""
        self.report_content.extend([
            "## 📊 프로젝트 통계",
            ""
        ])
        
        # 전체 통계
        total_components = project_structure.total_components
        total_layers = len(project_structure.layers)
        
        self.report_content.extend([
            f"- **총 컴포넌트 수**: {total_components}개",
            f"- **계층 수**: {total_layers}개",
            f"- **평균 컴포넌트/계층**: {total_components/total_layers:.1f}개",
            ""
        ])
        
        # 계층별 통계
        self.report_content.append("### 계층별 상세 통계")
        self.report_content.append("")
        
        for layer in project_structure.layers:
            component_count = len(layer.components)
            percentage = (component_count / total_components) * 100
            
            self.report_content.extend([
                f"#### {layer.name}",
                f"- 컴포넌트 수: {component_count}개 ({percentage:.1f}%)",
                f"- 주요 타입: {', '.join(self._get_unique_types(layer.components))}",
                ""
            ])
        
        # 타입별 통계
        self.report_content.append("### 컴포넌트 타입별 통계")
        self.report_content.append("")
        
        all_components = []
        for layer in project_structure.layers:
            all_components.extend(layer.components)
        
        type_stats = {}
        for component in all_components:
            if component.type not in type_stats:
                type_stats[component.type] = 0
            type_stats[component.type] += 1
        
        for component_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_components) * 100
            self.report_content.append(f"- **{component_type}**: {count}개 ({percentage:.1f}%)")
        
        self.report_content.extend(["", "---", ""])
    
    def _generate_footer(self, project_structure):
        """푸터 생성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.report_content.extend([
            "## 📝 보고서 정보",
            "",
            f"- **생성일시**: {current_time}",
            f"- **분석 대상**: {project_structure.project_name}",
            f"- **총 컴포넌트**: {project_structure.total_components}개",
            f"- **분석 시간**: {project_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])
    
    def _get_main_types(self, components: List) -> str:
        """주요 타입 추출"""
        type_counts = {}
        for component in components:
            if component.type not in type_counts:
                type_counts[component.type] = 0
            type_counts[component.type] += 1
        
        # 상위 2개 타입만 반환
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        main_types = [t[0] for t in sorted_types[:2]]
        return ", ".join(main_types)
    
    def _group_by_type(self, components: List) -> dict:
        """타입별로 그룹화"""
        type_groups = {}
        for component in components:
            if component.type not in type_groups:
                type_groups[component.type] = []
            type_groups[component.type].append(component)
        
        # 타입별로 정렬
        for component_type in type_groups:
            type_groups[component_type].sort(key=lambda x: x.name)
        
        return type_groups
    
    def _get_unique_types(self, components: List) -> List[str]:
        """고유 타입 목록 반환"""
        types = set()
        for component in components:
            types.add(component.type)
        return sorted(list(types))
