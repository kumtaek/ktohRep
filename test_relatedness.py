#!/usr/bin/env python3
"""
Test script for the relatedness calculation system.
This script tests the implementation without requiring existing project data.
"""

import os
import sys
import yaml
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent / 'phase1'))

from phase1.models.database import DatabaseManager, Project
from phase1.scripts.calculate_relatedness import RelatednessCalculator

def test_database_connection():
    """Test basic database connectivity and list available projects."""
    print("=== Testing Database Connection ===")
    
    try:
        # Load config
        config_path = Path(__file__).parent / "config" / "config.yaml"
        if not config_path.exists():
            print(f"Config file not found at {config_path}")
            return False
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Adapt config for DatabaseManager (use project database settings)
        if 'database' in config and 'project' in config['database']:
            config['database'] = config['database']['project']
            # Use default project name if available
            if 'project' in config and 'default_project_name' in config['project']:
                project_name_for_db = config['project']['default_project_name']
                # Replace placeholder in path
                if 'sqlite' in config['database'] and 'path' in config['database']['sqlite']:
                    config['database']['sqlite']['path'] = config['database']['sqlite']['path'].replace('{project_name}', project_name_for_db)
        
        # Test database connection
        dbm = DatabaseManager(config)
        dbm.initialize()
        session = dbm.get_session()
        
        # List available projects
        projects = session.query(Project).all()
        print(f"Database connection successful")
        print(f"Found {len(projects)} projects in database:")
        
        for project in projects:
            print(f"   - ID: {project.project_id}, Name: '{project.name}', Path: {project.root_path}")
        
        session.close()
        return projects
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_relatedness_calculator(project_name: str = None):
    """Test the relatedness calculation system."""
    print("\n=== Testing Relatedness Calculator ===")
    
    try:
        # Load config
        config_path = Path(__file__).parent / "config" / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Adapt config for DatabaseManager (use project database settings)
        if 'database' in config and 'project' in config['database']:
            config['database'] = config['database']['project']
            # Use default project name if available
            if 'project' in config and 'default_project_name' in config['project']:
                project_name_for_db = config['project']['default_project_name']
                # Replace placeholder in path
                if 'sqlite' in config['database'] and 'path' in config['database']['sqlite']:
                    config['database']['sqlite']['path'] = config['database']['sqlite']['path'].replace('{project_name}', project_name_for_db)
        
        # If no project name provided, try to use the first available project
        if not project_name:
            dbm = DatabaseManager(config)
            dbm.initialize()
            session = dbm.get_session()
            projects = session.query(Project).first()
            session.close()
            
            if projects:
                project_name = projects.name
                print(f"Using project: '{project_name}'")
            else:
                print("No projects found in database. Cannot test.")
                return False
        
        # Test the calculator
        calculator = RelatednessCalculator(project_name, config)
        print(f"Calculator initialized for project: {project_name}")
        
        # Run the calculation
        calculator.run()
        print("Relatedness calculation completed successfully!")
        return True
        
    except Exception as e:
        print(f"Relatedness calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("Testing Relatedness Calculation System")
    print("=" * 50)
    
    # Test 1: Database connection
    projects = test_database_connection()
    if not projects:
        print("\nCannot proceed without database connection.")
        return False
    
    # Test 2: Relatedness calculation
    success = test_relatedness_calculator()
    
    print("\n" + "=" * 50)
    if success:
        print("All tests passed! The relatedness system is working correctly.")
        print("\nNext steps:")
        print("   1. Review the relatedness data in your database")
        print("   2. Integrate with visualization components") 
        print("   3. Fine-tune scoring weights in the strategies")
    else:
        print("Some tests failed. Check the error messages above.")
    
    return success

if __name__ == '__main__':
    main()