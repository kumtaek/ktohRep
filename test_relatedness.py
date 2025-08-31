#!/usr/bin/env python3
"""
Test script for the relatedness calculation system.
This script tests the implementation without requiring existing project data.
"""

import os
import sys
import yaml
from pathlib import Path

# phase1 모듈 경로를 시스템 경로에 추가합니다.
sys.path.insert(0, str(Path(__file__).parent / 'phase1'))

from phase1.models.database import DatabaseManager, Project
from phase1.scripts.calculate_relatedness import RelatednessCalculator

def test_database_connection():
    """Test basic database connectivity and list available projects."""
    print("=== 데이터베이스 연결 테스트 ===")
    
    try:
        # 설정 파일을 로드합니다.
        config_path = Path(__file__).parent / "config" / "config.yaml"
        if not config_path.exists():
            print(f"설정 파일을 {config_path}에서 찾을 수 없습니다.")
            return False
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # DatabaseManager를 위해 설정을 조정합니다 (프로젝트 데이터베이스 설정 사용).
        if 'database' in config and 'project' in config['database']:
            config['database'] = config['database']['project']
            # 기본 프로젝트 이름이 있는 경우 사용합니다.
            if 'project' in config and 'default_project_name' in config['project']:
                project_name_for_db = config['project']['default_project_name']
                # 경로의 플레이스홀더를 대체합니다.
                if 'sqlite' in config['database'] and 'path' in config['database']['sqlite']:
                    config['database']['sqlite']['path'] = config['database']['sqlite']['path'].replace('{project_name}', project_name_for_db)
        
        # 데이터베이스 연결을 테스트합니다.
        dbm = DatabaseManager(config)
        dbm.initialize()
        session = dbm.get_session()
        
        # 사용 가능한 프로젝트를 나열합니다.
        projects = session.query(Project).all()
        print(f"데이터베이스 연결 성공")
        print(f"데이터베이스에서 {len(projects)}개의 프로젝트를 찾았습니다:")
        
        for project in projects:
            print(f"   - ID: {project.project_id}, Name: '{project.name}', Path: {project.root_path}")
        
        session.close()
        return projects
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_relatedness_calculator(project_name: str = None):
    """Test the relatedness calculation system."""
    print("\n=== 관련성 계산기 테스트 ===")
    
    try:
        # 설정 파일을 로드합니다.
        config_path = Path(__file__).parent / "config" / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # DatabaseManager를 위해 설정을 조정합니다 (프로젝트 데이터베이스 설정 사용).
        if 'database' in config and 'project' in config['database']:
            config['database'] = config['database']['project']
            # 기본 프로젝트 이름이 있는 경우 사용합니다.
            if 'project' in config and 'default_project_name' in config['project']:
                project_name_for_db = config['project']['default_project_name']
                # 경로의 플레이스홀더를 대체합니다.
                if 'sqlite' in config['database'] and 'path' in config['database']['sqlite']:
                    config['database']['sqlite']['path'] = config['database']['sqlite']['path'].replace('{project_name}', project_name_for_db)
        
        # 프로젝트 이름이 제공되지 않은 경우, 사용 가능한 첫 번째 프로젝트를 사용하려고 시도합니다.
        if not project_name:
            dbm = DatabaseManager(config)
            dbm.initialize()
            session = dbm.get_session()
            projects = session.query(Project).first()
            session.close()
            
            if projects:
                project_name = projects.name
                print(f"프로젝트 사용: '{project_name}'")
            else:
                print("데이터베이스에서 프로젝트를 찾을 수 없습니다. 테스트를 수행할 수 없습니다.")
                return False

        
        # 계산기를 테스트합니다.
        calculator = RelatednessCalculator(project_name, config)
        print(f"프로젝트 {project_name}에 대해 계산기가 초기화되었습니다.")
        
        # 계산을 실행합니다.
        calculator.run()
        print("관련성 계산이 성공적으로 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"관련성 계산 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("관련성 계산 시스템 테스트")
    print("=" * 50)
    
    # 테스트 1: 데이터베이스 연결
    projects = test_database_connection()
    if not projects:
        print("\n데이터베이스 연결 없이는 진행할 수 없습니다.")
        return False
    
    # 테스트 2: 관련성 계산
    success = test_relatedness_calculator()
    
    print("\n" + "=" * 50)
    if success:
        print("모든 테스트 통과! 관련성 시스템이 올바르게 작동하고 있습니다.")
        print("\n다음 단계:")
        print("   1. 데이터베이스의 관련성 데이터를 검토합니다.")
        print("   2. 시각화 구성 요소와 통합합니다.") 
        print("   3. 전략에서 점수 가중치를 미세 조정합니다.")
    else:
        print("일부 테스트가 실패했습니다. 위 오류 메시지를 확인하십시오.")
    
    return success


if __name__ == '__main__':
    main()