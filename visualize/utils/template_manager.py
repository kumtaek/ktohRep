#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
템플릿 관리자: 프로젝트별 report 폴더 자동 복사 및 관리
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    """프로젝트별 리포트 템플릿 관리자"""
    
    def __init__(self, base_templates_dir: str = "./visualize/templates"):
        """
        템플릿 관리자 초기화
        
        Args:
            base_templates_dir: 기본 템플릿이 저장된 디렉토리 경로
        """
        self.base_templates_dir = Path(base_templates_dir)
        self.required_templates = [
            "erd_view.html",
            "graph_view.html", 
            "class_view.html",
            "sequence_view.html",
            "relatedness_view.html",
            "cyto_base.html"
        ]
    
    def ensure_project_report_dir(self, project_name: str) -> Path:
        """
        프로젝트별 report 폴더가 존재하는지 확인하고, 없으면 템플릿에서 복사
        
        Args:
            project_name: 프로젝트 이름
            
        Returns:
            프로젝트 report 폴더 경로
        """
        project_report_dir = Path(f"./project/{project_name}/report")
        
        # report 폴더가 없거나 비어있으면 템플릿 복사
        if not project_report_dir.exists() or not any(project_report_dir.iterdir()):
            logger.info(f"프로젝트 {project_name}의 report 폴더가 비어있습니다. 템플릿을 복사합니다.")
            self._copy_templates_to_project(project_name, project_report_dir)
        else:
            logger.info(f"프로젝트 {project_name}의 report 폴더가 이미 존재합니다.")
        
        return project_report_dir
    
    def _copy_templates_to_project(self, project_name: str, target_dir: Path):
        """
        기본 템플릿을 프로젝트 report 폴더로 복사
        
        Args:
            project_name: 프로젝트 이름
            target_dir: 대상 디렉토리
        """
        try:
            # 대상 디렉토리 생성
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 필요한 템플릿 파일들 복사
            copied_files = []
            for template_name in self.required_templates:
                source_file = self.base_templates_dir / template_name
                target_file = target_dir / template_name
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    copied_files.append(template_name)
                    logger.debug(f"템플릿 복사: {template_name}")
                else:
                    logger.warning(f"템플릿 파일을 찾을 수 없습니다: {source_file}")
            
            # static 폴더의 JavaScript 라이브러리도 복사
            static_dir = Path("./static")
            if static_dir.exists():
                target_static_dir = target_dir / "static"
                if not target_static_dir.exists():
                    shutil.copytree(static_dir, target_static_dir)
                    logger.info(f"static 폴더 복사 완료: {target_static_dir}")
            
            logger.info(f"프로젝트 {project_name}에 {len(copied_files)}개 템플릿 복사 완료")
            
        except Exception as e:
            logger.error(f"템플릿 복사 중 오류 발생: {e}")
            raise
    
    def get_project_template_path(self, project_name: str, template_name: str) -> Optional[Path]:
        """
        프로젝트별 템플릿 파일 경로 반환
        
        Args:
            project_name: 프로젝트 이름
            template_name: 템플릿 파일명
            
        Returns:
            템플릿 파일 경로 또는 None
        """
        project_template_path = Path(f"./project/{project_name}/report/{template_name}")
        
        if project_template_path.exists():
            return project_template_path
        
        # 프로젝트에 없으면 기본 템플릿 경로 반환
        base_template_path = self.base_templates_dir / template_name
        if base_template_path.exists():
            return base_template_path
        
        return None
    
    def list_project_templates(self, project_name: str) -> List[str]:
        """
        프로젝트별 사용 가능한 템플릿 목록 반환
        
        Args:
            project_name: 프로젝트 이름
            
        Returns:
            사용 가능한 템플릿 파일명 목록
        """
        project_report_dir = Path(f"./project/{project_name}/report")
        available_templates = []
        
        if project_report_dir.exists():
            for template_name in self.required_templates:
                template_path = project_report_dir / template_name
                if template_path.exists():
                    available_templates.append(template_name)
        
        return available_templates
    
    def update_project_templates(self, project_name: str, force: bool = False) -> bool:
        """
        프로젝트별 템플릿을 최신 버전으로 업데이트
        
        Args:
            project_name: 프로젝트 이름
            force: 강제 업데이트 여부
            
        Returns:
            업데이트 성공 여부
        """
        try:
            project_report_dir = Path(f"./project/{project_name}/report")
            
            if not project_report_dir.exists():
                logger.info(f"프로젝트 {project_name}의 report 폴더가 없습니다. 새로 생성합니다.")
                self._copy_templates_to_project(project_name, project_report_dir)
                return True
            
            if force:
                logger.info(f"프로젝트 {project_name}의 템플릿을 강제 업데이트합니다.")
                # 기존 폴더 삭제 후 새로 복사
                shutil.rmtree(project_report_dir)
                self._copy_templates_to_project(project_name, project_report_dir)
                return True
            
            # 필요한 템플릿이 누락된 경우에만 복사
            missing_templates = []
            for template_name in self.required_templates:
                if not (project_report_dir / template_name).exists():
                    missing_templates.append(template_name)
            
            if missing_templates:
                logger.info(f"프로젝트 {project_name}에 누락된 템플릿이 있습니다: {missing_templates}")
                self._copy_templates_to_project(project_name, project_report_dir)
                return True
            
            logger.info(f"프로젝트 {project_name}의 모든 템플릿이 최신 상태입니다.")
            return True
            
        except Exception as e:
            logger.error(f"템플릿 업데이트 중 오류 발생: {e}")
            return False

# 전역 인스턴스
template_manager = TemplateManager()

def ensure_project_report_dir(project_name: str) -> Path:
    """
    프로젝트별 report 폴더 보장 (편의 함수)
    
    Args:
        project_name: 프로젝트 이름
        
    Returns:
        프로젝트 report 폴더 경로
    """
    return template_manager.ensure_project_report_dir(project_name)
