#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
엣지 생성 테스트 스크립트
"""

import sys
import os
import logging
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_edge_generation():
    """엣지 생성을 테스트합니다."""
    try:
        # 단순한 설정 생성
        config = {
            'database': {
                'project': {
                    'sqlite': {
                        'path': './project/sampleSrc/metadata.db'
                    }
                }
            },
            'default_schema': {
                'default_owner': 'SAMPLE'
            }
        }
        
        # DB 연결
        db_path = config['database']['project']['sqlite']['path']
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 프로젝트 ID 확인
        from models.database import Project
        project = session.query(Project).filter_by(name="sampleSrc").first()
        if not project:
            print("프로젝트를 찾을 수 없습니다: sampleSrc")
            return
            
        print(f"프로젝트 ID: {project.project_id}")
        
        # 엣지 생성기 초기화
        from utils.edge_generator import EdgeGenerator
        edge_generator = EdgeGenerator(session, config)
        
        print("엣지 생성 시작...")
        edge_count = edge_generator.generate_all_edges()
        print(f"엣지 생성 완료: {edge_count}개")
        
        # 결과 확인
        from models.database import Edge
        edges = session.query(Edge).all()
        print(f"DB에 저장된 엣지 수: {len(edges)}")
        
        if edges:
            print("\n첫 5개 엣지:")
            for i, edge in enumerate(edges[:5]):
                print(f"  {i+1}. {edge.src_type}({edge.src_id}) -> {edge.dst_type}({edge.dst_id}) [{edge.edge_kind}]")
        
        session.close()
        
    except Exception as e:
        logger.exception(f"엣지 생성 테스트 실패: {e}")

if __name__ == "__main__":
    test_edge_generation()