"""
Java 프로젝트 계층도 분석 리포트 생성기
분석된 프로젝트 구조를 바탕으로 마크다운 형식의 리포트를 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from utils.hierarchy_analyzer import ProjectStructure, PackageInfo, JavaClassInfo

class HierarchyReportGenerator:
    """계층도 분석 리포트 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, project_structure: ProjectStructure, output_path: str = None, top_n: int = None) -> str:
        """
        계층도 분석 리포트 생성
        
        Args:
            project_structure: 분석된 프로젝트 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            top_n: 계층별 표시할 최대 항목 수 (None이면 제한 없음)
            
        Returns:
            생성된 리포트 내용
        """
        self.logger.info("계층도 분석 리포트 생성 시작")
        
        # 리포트 내용 생성
        report_content = self._generate_report_content(project_structure, top_n)
        
        # 파일로 저장
        if output_path:
            self._save_report(report_content, output_path)
            self.logger.info(f"리포트 저장 완료: {output_path}")
        
        return report_content
    
    def _generate_report_content(self, project_structure: ProjectStructure, top_n: int = None) -> str:
        """리포트 내용 생성"""
        project_name = Path(project_structure.root_path).name
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        
        # 헤더 생성
        content = f"""# 📁 {project_name} 디렉토리 계층도 분석 리포트

## 📋 보고서 정보
- **작성일시**: {current_time}
- **분석대상**: `{project_structure.root_path}`
- **분석자**: JavaHierarchyAnalyzer
- **보고서 유형**: 소스코드 계층도 분석

---

## 🏗️ 전체 프로젝트 구조

```
{project_name}/
{self._generate_project_tree(project_structure)}
```

---

## 📊 프로젝트 요약 정보

### 📈 **전체 통계**
- **📁 총 패키지 수**: {len(project_structure.packages)}개
- **📄 총 Java 파일 수**: {project_structure.total_files}개
- **🏗️ 총 클래스 수**: {project_structure.total_classes}개
- **📝 총 코드 라인 수**: {project_structure.total_lines:,}줄
- **📊 클래스당 평균 라인 수**: {project_structure.total_lines / project_structure.total_classes:.1f}줄

### 🕐 **분석 정보**
- **🔍 분석 시작 시간**: {project_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
- **📁 Java 소스 디렉토리**: {', '.join([Path(p.path).name for p in project_structure.packages])}

---

## 📦 Java 소스코드 상세 계층도

"""
        
        # 패키지별 상세 분석
        for package in project_structure.packages:
            content += self._generate_package_section(package, top_n)
        
        # 의존성 분석
        content += self._generate_dependency_analysis(project_structure)
        
        # 코드 품질 분석
        content += self._generate_code_quality_analysis(project_structure)
        
        # 아키텍처 분석
        content += self._generate_architecture_analysis(project_structure)
        
        # 결론 및 제언
        content += self._generate_conclusion(project_structure)
        
        return content
    
    def _generate_project_tree(self, project_structure: ProjectStructure) -> str:
        """프로젝트 트리 구조 생성"""
        tree_lines = []
        
        for package in project_structure.packages:
            tree_lines.extend(self._generate_package_tree(package, level=0))
        
        return '\n'.join(tree_lines)
    
    def _generate_package_tree(self, package: PackageInfo, level: int = 0) -> List[str]:
        """패키지 트리 구조 생성"""
        lines = []
        indent = "│   " * level
        
        # 패키지 정보
        if level == 0:
            lines.append(f"├── 📁 {package.name}/")
        else:
            lines.append(f"{indent}├── 📁 {package.name}/")
        
        # Java 파일들
        for i, java_class in enumerate(package.classes):
            is_last = (i == len(package.classes) - 1) and (len(package.sub_packages) == 0)
            prefix = "└──" if is_last else "├──"
            
            # 클래스 타입에 따른 아이콘
            icon = self._get_class_icon(java_class)
            
            if level == 0:
                lines.append(f"{prefix} 📄 {java_class.name}.java {icon}")
            else:
                lines.append(f"{indent}{prefix} 📄 {java_class.name}.java {icon}")
        
        # 하위 패키지들
        for i, sub_package in enumerate(package.sub_packages):
            is_last = (i == len(package.sub_packages) - 1)
            if is_last:
                lines.extend(self._generate_package_tree(sub_package, level + 1))
            else:
                lines.extend(self._generate_package_tree(sub_package, level + 1))
        
        return lines
    
    def _get_class_icon(self, java_class: JavaClassInfo) -> str:
        """클래스 타입에 따른 아이콘 반환"""
        if java_class.is_interface:
            return "🔌"
        elif java_class.is_abstract:
            return "📋"
        else:
            return "🏗️"
    
    def _generate_package_section(self, package: PackageInfo, top_n: int = None) -> str:
        """패키지별 상세 섹션 생성"""
        content = f"""### 🎯 **패키지: `{package.name}`**

#### 📊 **패키지 정보**
- **📁 경로**: `{package.path}`
- **📄 Java 파일 수**: {len(package.classes)}개
- **📝 총 코드 라인 수**: {package.total_lines:,}줄
- **📊 하위 패키지 수**: {len(package.sub_packages)}개

#### 📄 **Java 클래스 상세 정보**

"""
        
        # Top N 제한 적용
        if top_n and len(package.classes) > top_n:
            content += f"*(Top {top_n}개 표시, 전체 {len(package.classes)}개)*\n\n"
            display_classes = package.classes[:top_n]
        else:
            display_classes = package.classes
        
        # 클래스별 상세 정보
        for java_class in display_classes:
            content += self._generate_class_detail(java_class)
        
        # Top N 제한으로 숨겨진 클래스가 있는 경우 안내
        if top_n and len(package.classes) > top_n:
            hidden_count = len(package.classes) - top_n
            content += f"*... 및 {hidden_count}개 추가 클래스*\n\n"
        
        # 하위 패키지 정보
        if package.sub_packages:
            content += "\n#### 📁 **하위 패키지**\n"
            for sub_package in package.sub_packages:
                content += f"- **{sub_package.name}**: {sub_package.class_count}개 클래스, {sub_package.total_lines:,}줄\n"
        
        content += "\n---\n\n"
        return content
    
    def _generate_class_detail(self, java_class: JavaClassInfo) -> str:
        """클래스별 상세 정보 생성"""
        # 클래스 타입 정보
        class_type = []
        if java_class.is_interface:
            class_type.append("🔌 인터페이스")
        elif java_class.is_abstract:
            class_type.append("📋 추상 클래스")
        else:
            class_type.append("🏗️ 일반 클래스")
        
        if java_class.extends:
            class_type.append(f"📤 extends {java_class.extends}")
        
        if java_class.implements:
            class_type.append(f"🔗 implements {', '.join(java_class.implements)}")
        
        # 어노테이션 정보
        annotations_text = ""
        if java_class.annotations:
            annotations_text = f"\n- **🏷️ 어노테이션**: {', '.join(java_class.annotations)}"
        
        # 의존성 정보
        dependencies_text = ""
        if java_class.dependencies:
            dependencies_text = f"\n- **🔗 주요 의존성**: {', '.join(java_class.dependencies[:5])}{'...' if len(java_class.dependencies) > 5 else ''}"
        
        # 텍스트 길이 제한
        class_name_display = java_class.name[:25] + ("..." if len(java_class.name) > 25 else "")
        class_type_display = ', '.join(class_type)[:40] + ("..." if len(', '.join(class_type)) > 40 else "")
        annotations_display = ', '.join(java_class.annotations)[:30] + ("..." if len(', '.join(java_class.annotations)) > 30 else "") if java_class.annotations else ""
        dependencies_display = ', '.join(java_class.dependencies[:3])[:35] + ("..." if len(', '.join(java_class.dependencies[:3])) > 35 else "") if java_class.dependencies else ""
        
        content = f"""##### **{class_name_display}**
- {java_class.line_count:,}줄, {java_class.method_count}메서드, {java_class.comment_count}주석
- {class_type_display}"""
        
        if annotations_display:
            content += f"\n- 🏷️ {annotations_display}"
        
        if dependencies_display:
            content += f"\n- 🔗 {dependencies_display}"
        
        content += "\n\n"
        
        return content
    
    def _generate_dependency_analysis(self, project_structure: ProjectStructure) -> str:
        """의존성 분석 섹션 생성"""
        content = """## 🔗 의존성 분석

### 📊 **전체 의존성 현황**
"""
        
        # 모든 클래스의 의존성 수집
        all_dependencies = []
        for package in project_structure.packages:
            for java_class in package.classes:
                all_dependencies.extend(java_class.dependencies)
        
        # 의존성 빈도 분석
        dependency_freq = {}
        for dep in all_dependencies:
            dependency_freq[dep] = dependency_freq.get(dep, 0) + 1
        
        # 상위 의존성 정렬
        top_dependencies = sorted(dependency_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        content += "#### 🔝 **가장 많이 사용되는 의존성 (Top 10)**\n"
        for dep, count in top_dependencies:
            content += f"- **{dep}**: {count}회 사용\n"
        
        content += "\n---\n\n"
        return content
    
    def _generate_code_quality_analysis(self, project_structure: ProjectStructure) -> str:
        """코드 품질 분석 섹션 생성"""
        content = """## 📈 코드 품질 분석

### 📊 **코드 품질 지표**
"""
        
        # 클래스별 라인 수 분석
        class_line_counts = []
        for package in project_structure.packages:
            for java_class in package.classes:
                class_line_counts.append(java_class.line_count)
        
        if class_line_counts:
            avg_lines = sum(class_line_counts) / len(class_line_counts)
            max_lines = max(class_line_counts)
            min_lines = min(class_line_counts)
            
            content += f"""#### 📏 **클래스 크기 분석**
- **📊 평균 라인 수**: {avg_lines:.1f}줄
- **📈 최대 라인 수**: {max_lines:,}줄
- **📉 최소 라인 수**: {min_lines:,}줄

"""
            
            # 큰 클래스들 (100줄 이상)
            large_classes = [count for count in class_line_counts if count > 100]
            if large_classes:
                content += f"""#### ⚠️ **큰 클래스들 (100줄 이상)**
- **📊 큰 클래스 수**: {len(large_classes)}개
- **📈 전체 대비 비율**: {len(large_classes) / len(class_line_counts) * 100:.1f}%

**💡 제언**: 큰 클래스들은 단일 책임 원칙에 따라 분리하는 것을 고려해보세요.

"""
        
        content += "\n---\n\n"
        return content
    
    def _generate_architecture_analysis(self, project_structure: ProjectStructure) -> str:
        """아키텍처 분석 섹션 생성"""
        content = """## 🏛️ 아키텍처 분석

### 🎯 **패키지 구조 분석**
"""
        
        # 패키지별 클래스 분포
        package_distribution = []
        for package in project_structure.packages:
            package_distribution.append((package.name, package.class_count))
        
        # 클래스 수 기준으로 정렬
        package_distribution.sort(key=lambda x: x[1], reverse=True)
        
        content += "#### 📦 **패키지별 클래스 분포**\n"
        for package_name, class_count in package_distribution:
            percentage = (class_count / project_structure.total_classes) * 100
            content += f"- **{package_name}**: {class_count}개 클래스 ({percentage:.1f}%)\n"
        
        # 아키텍처 패턴 분석
        content += """

#### 🏗️ **아키텍처 패턴 추정**
"""
        
        # 패키지명 기반으로 아키텍처 패턴 추정
        architecture_patterns = self._identify_architecture_patterns(project_structure)
        for pattern, description in architecture_patterns.items():
            content += f"- **{pattern}**: {description}\n"
        
        content += "\n---\n\n"
        return content
    
    def _identify_architecture_patterns(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """아키텍처 패턴 식별"""
        patterns = {}
        
        package_names = [p.name.lower() for p in project_structure.packages]
        
        # MVC 패턴
        if any('controller' in name for name in package_names) and \
           any('service' in name for name in package_names) and \
           any('mapper' in name or 'dao' in name for name in package_names):
            patterns['MVC 패턴'] = "Controller-Service-Data Access 계층 구조가 확인됨"
        
        # 계층형 아키텍처
        if any('presentation' in name or 'web' in name for name in package_names) and \
           any('business' in name or 'service' in name for name in package_names) and \
           any('data' in name or 'persistence' in name for name in package_names):
            patterns['계층형 아키텍처'] = "Presentation-Business-Data 계층이 명확히 분리됨"
        
        # 도메인 주도 설계
        if any('domain' in name for name in package_names) and \
           any('application' in name for name in package_names) and \
           any('infrastructure' in name for name in package_names):
            patterns['도메인 주도 설계'] = "Domain-Application-Infrastructure 계층 구조가 확인됨"
        
        # 마이크로서비스
        if any('api' in name for name in package_names) and \
           any('config' in name for name in package_names):
            patterns['API 기반 설계'] = "REST API 및 설정 관리 구조가 확인됨"
        
        return patterns
    
    def _generate_conclusion(self, project_structure: ProjectStructure) -> str:
        """결론 및 제언 섹션 생성"""
        content = """## 📝 결론 및 제언

### 🎉 **현재 상태**
"""
        
        # 프로젝트 규모에 따른 평가
        if project_structure.total_classes < 10:
            content += "- ✅ **소규모 프로젝트**: 간단하고 관리하기 쉬운 구조"
        elif project_structure.total_classes < 50:
            content += "- ✅ **중간 규모 프로젝트**: 적절한 복잡도와 구조"
        else:
            content += "- ✅ **대규모 프로젝트**: 체계적인 구조화가 중요"
        
        # 코드 품질 평가
        avg_lines = project_structure.total_lines / project_structure.total_classes if project_structure.total_classes > 0 else 0
        if avg_lines < 50:
            content += "\n- ✅ **코드 품질**: 클래스 크기가 적절함"
        elif avg_lines < 100:
            content += "\n- ⚠️ **코드 품질**: 일부 클래스가 큼 (리팩토링 고려)"
        else:
            content += "\n- 🚨 **코드 품질**: 클래스 크기가 큼 (리팩토링 필요)"
        
        content += f"""

### 🚀 **개선 제언**
1. **📚 문서화 강화**: 각 클래스별 JavaDoc 주석 추가
2. **🧪 테스트 코드**: Unit Test 및 Integration Test 추가
3. **📊 코드 메트릭**: 정기적인 코드 품질 분석 및 모니터링
4. **🔍 의존성 관리**: 순환 의존성 체크 및 의존성 최소화
5. **🏗️ 아키텍처 개선**: 필요시 패키지 구조 재정리

### 📋 **다음 단계**
1. **소스코드 상세 분석**: 각 클래스의 메서드 및 로직 분석
2. **의존성 그래프 생성**: 클래스 간 관계 시각화
3. **코드 복잡도 분석**: 메서드별 복잡도 측정
4. **성능 프로파일링**: 병목 구간 식별 및 최적화

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
            self.logger.error(f"리포트 저장 실패: {e}")
            raise
