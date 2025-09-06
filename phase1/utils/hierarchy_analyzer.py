"""
Java 소스코드 계층도 분석 엔진
디렉토리 구조를 스캔하여 패키지, 클래스, 의존성 등을 분석합니다.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import ast
import logging

@dataclass
class JavaClassInfo:
    """Java 클래스 정보"""
    name: str
    file_path: str
    package: str
    line_count: int
    class_count: int
    method_count: int
    comment_count: int
    imports: List[str]
    dependencies: List[str]
    annotations: List[str]
    is_interface: bool
    is_abstract: bool
    extends: Optional[str]
    implements: List[str]

@dataclass
class PackageInfo:
    """패키지 정보"""
    name: str
    path: str
    class_count: int
    total_lines: int
    classes: List[JavaClassInfo]
    sub_packages: List['PackageInfo']

@dataclass
class ProjectStructure:
    """프로젝트 구조 정보"""
    root_path: str
    packages: List[PackageInfo]
    total_classes: int
    total_lines: int
    total_files: int
    analysis_time: datetime

class JavaHierarchyAnalyzer:
    """Java 프로젝트 계층도 분석기"""
    
    def __init__(self, project_path: str):
        """
        분석기 초기화
        
        Args:
            project_path: 분석할 프로젝트 경로
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        
        # Java 파일 패턴
        self.java_pattern = re.compile(r'\.java$')
        
        # Java 키워드 패턴
        self.class_pattern = re.compile(r'class\s+(\w+)')
        self.interface_pattern = re.compile(r'interface\s+(\w+)')
        self.abstract_pattern = re.compile(r'abstract\s+class\s+(\w+)')
        self.extends_pattern = re.compile(r'extends\s+(\w+)')
        self.implements_pattern = re.compile(r'implements\s+([\w\s,]+)')
        self.import_pattern = re.compile(r'import\s+([\w.]+)')
        self.annotation_pattern = re.compile(r'@(\w+)')
        self.package_pattern = re.compile(r'package\s+([\w.]+)')
        
    def analyze_project(self) -> ProjectStructure:
        """
        프로젝트 전체 분석
        
        Returns:
            프로젝트 구조 정보
        """
        self.logger.info(f"프로젝트 분석 시작: {self.project_path}")
        
        start_time = datetime.now()
        
        # Java 소스 디렉토리 찾기
        java_dirs = self._find_java_directories()
        
        # 패키지 분석
        packages = []
        total_classes = 0
        total_lines = 0
        total_files = 0
        
        for java_dir in java_dirs:
            package_info = self._analyze_package(java_dir)
            if package_info:
                packages.append(package_info)
                total_classes += package_info.class_count
                total_lines += package_info.total_lines
                total_files += len(package_info.classes)
        
        # 프로젝트 구조 정보 생성
        project_structure = ProjectStructure(
            root_path=str(self.project_path),
            packages=packages,
            total_classes=total_classes,
            total_lines=total_lines,
            total_files=total_files,
            analysis_time=start_time
        )
        
        self.logger.info(f"프로젝트 분석 완료: {total_classes}개 클래스, {total_lines}줄")
        
        return project_structure
    
    def _find_java_directories(self) -> List[Path]:
        """Java 소스 디렉토리 찾기"""
        java_dirs = []
        
        # 일반적인 Java 프로젝트 구조
        common_paths = [
            self.project_path / "src" / "main" / "java",
            self.project_path / "src" / "java",
            self.project_path / "java",
            self.project_path / "app" / "src" / "main" / "java"
        ]
        
        for path in common_paths:
            if path.exists():
                java_dirs.append(path)
                self.logger.info(f"Java 소스 디렉토리 발견: {path}")
        
        # 추가로 Java 파일이 있는 디렉토리 찾기
        for root, dirs, files in os.walk(self.project_path):
            if any(self.java_pattern.search(f) for f in files):
                java_dirs.append(Path(root))
        
        return list(set(java_dirs))  # 중복 제거
    
    def _analyze_package(self, package_path: Path) -> Optional[PackageInfo]:
        """패키지 분석"""
        try:
            package_name = self._get_package_name(package_path)
            
            # Java 파일 찾기
            java_files = [f for f in package_path.glob("*.java")]
            
            if not java_files:
                return None
            
            # 클래스 분석
            classes = []
            total_lines = 0
            
            for java_file in java_files:
                class_info = self._analyze_java_file(java_file, package_name)
                if class_info:
                    classes.append(class_info)
                    total_lines += class_info.line_count
            
            # 하위 패키지 분석
            sub_packages = []
            for sub_dir in package_path.iterdir():
                if sub_dir.is_dir() and not sub_dir.name.startswith('.'):
                    sub_package = self._analyze_package(sub_dir)
                    if sub_package:
                        sub_packages.append(sub_package)
            
            return PackageInfo(
                name=package_name,
                path=str(package_path),
                class_count=len(classes),
                total_lines=total_lines,
                classes=classes,
                sub_packages=sub_packages
            )
            
        except Exception as e:
            self.logger.error(f"패키지 분석 실패 {package_path}: {e}")
            return None
    
    def _get_package_name(self, package_path: Path) -> str:
        """패키지명 추출"""
        # src/main/java 이후의 경로를 패키지명으로 사용
        if "src/main/java" in str(package_path):
            parts = str(package_path).split("src/main/java")
            if len(parts) > 1:
                package_path = parts[1]
        
        # 경로를 패키지명으로 변환
        package_name = str(package_path).replace(str(self.project_path), "").strip("\\/")
        package_name = package_name.replace("\\", ".").replace("/", ".")
        
        return package_name if package_name else "default"
    
    def _analyze_java_file(self, file_path: Path, package_name: str) -> Optional[JavaClassInfo]:
        """Java 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            line_count = len(lines)
            
            # 패키지 선언 찾기
            package_match = self.package_pattern.search(content)
            if package_match:
                package_name = package_match.group(1)
            
            # 클래스 정보 추출
            class_name = self._extract_class_name(content)
            if not class_name:
                return None
            
            # 클래스 타입 확인
            is_interface = bool(self.interface_pattern.search(content))
            is_abstract = bool(self.abstract_pattern.search(content))
            
            # 상속 및 구현 정보
            extends = self._extract_extends(content)
            implements = self._extract_implements(content)
            
            # import 및 의존성
            imports = self._extract_imports(content)
            dependencies = self._extract_dependencies(content)
            
            # 어노테이션
            annotations = self._extract_annotations(content)
            
            # 메서드 수 계산 (간단한 패턴 매칭)
            method_count = len(re.findall(r'(public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{?[^\{]*\{?', content))
            
            # 주석 수 계산
            comment_count = self._count_comments(content)
            
            return JavaClassInfo(
                name=class_name,
                file_path=str(file_path),
                package=package_name,
                line_count=line_count,
                class_count=1,
                method_count=method_count,
                comment_count=comment_count,
                imports=imports,
                dependencies=dependencies,
                annotations=annotations,
                is_interface=is_interface,
                is_abstract=is_abstract,
                extends=extends,
                implements=implements
            )
            
        except Exception as e:
            self.logger.error(f"Java 파일 분석 실패 {file_path}: {e}")
            return None
    
    def _extract_class_name(self, content: str) -> Optional[str]:
        """클래스명 추출"""
        # class 선언 찾기
        class_match = self.class_pattern.search(content)
        if class_match:
            return class_match.group(1)
        
        # interface 선언 찾기
        interface_match = self.interface_pattern.search(content)
        if interface_match:
            return interface_match.group(1)
        
        return None
    
    def _extract_extends(self, content: str) -> Optional[str]:
        """extends 정보 추출"""
        extends_match = self.extends_pattern.search(content)
        return extends_match.group(1) if extends_match else None
    
    def _extract_implements(self, content: str) -> List[str]:
        """implements 정보 추출"""
        implements_match = self.implements_pattern.search(content)
        if implements_match:
            return [imp.strip() for imp in implements_match.group(1).split(',')]
        return []
    
    def _extract_imports(self, content: str) -> List[str]:
        """import 문 추출"""
        imports = re.findall(self.import_pattern, content)
        return [imp.strip() for imp in imports]
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """의존성 추출 (import된 클래스들)"""
        imports = self._extract_imports(content)
        dependencies = []
        
        for imp in imports:
            # 패키지에서 클래스명만 추출
            if '.' in imp:
                class_name = imp.split('.')[-1]
                dependencies.append(class_name)
            else:
                dependencies.append(imp)
        
        return dependencies
    
    def _extract_annotations(self, content: str) -> List[str]:
        """어노테이션 추출"""
        annotations = re.findall(self.annotation_pattern, content)
        return list(set(annotations))  # 중복 제거
    
    def _count_comments(self, content: str) -> int:
        """주석 수 계산"""
        # 한 줄 주석
        single_line_comments = len(re.findall(r'//.*$', content, re.MULTILINE))
        
        # 여러 줄 주석
        multi_line_comments = len(re.findall(r'/\*.*?\*/', content, re.DOTALL))
        
        return single_line_comments + multi_line_comments
    
    def generate_summary(self, project_structure: ProjectStructure) -> Dict[str, Any]:
        """프로젝트 요약 정보 생성"""
        return {
            'project_name': Path(project_structure.root_path).name,
            'analysis_time': project_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': project_structure.total_files,
            'total_classes': project_structure.total_classes,
            'total_lines': project_structure.total_lines,
            'package_count': len(project_structure.packages),
            'average_lines_per_class': round(project_structure.total_lines / project_structure.total_classes, 2) if project_structure.total_classes > 0 else 0,
            'java_source_directories': [str(Path(p.path).relative_to(project_structure.root_path)) for p in project_structure.packages]
        }
