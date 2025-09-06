python main.py --project-name sampleSrc --clean
python metadb_mermaid_erd_generator.py --project-name sampleSrc
python metadb_cytoscape_erd_generator.py --project-name sampleSrc
python generate_component_report.py --project-name sampleSrc --top-n 2
python generate_hierarchy_report.py --project-name sampleSrc --top-n 2


python main.py --project-name sampleSrc --clean
python metadb_mermaid_erd_generator.py --project-name sampleSrc
python metadb_cytoscape_erd_generator.py --project-name sampleSrc
python generate_component_report.py --project-name sampleSrc
python generate_hierarchy_report.py --project-name sampleSrc


# 모든 기능 리스트와 실행 커멘드 (순서대로)
# 1단계: 기본 인프라 및 설정 확인
# python ai_model_client.py
# 
# 2단계: 메타정보 생성 (필수 - 다른 모든 기능의 기반)
python main.py --project-name sampleSrc --clean
# python clean_parser.py
# python simple_parser_v2.py
# 3단계: 기본 분석 도구들 (메타정보 종속 없음)
# python generate_hierarchy_report.py --project-name sampleSrc
# python generate_erd_report.py --project-name sampleSrc
# python generate_ai_report.py --project-name sampleSrc
# python generate_ai_report.py --project-name sampleSrc erd local_gemma
# python generate_ai_report.py --project-name sampleSrc security local_gemma
# python generate_ai_report.py --project-name sampleSrc code_quality local_gemma
# python generate_ai_report.py --project-name sampleSrc architecture local_gemma
# 4단계: 메타정보 종속 기능들 (2단계 완료 후 실행)
# python check_metadata_status.py
# python test_metadb_erd.py
# python metadb_erd_analyzer.py
# python metadb_erd_report_generator.py


# python advanced_erd_generator.py
# 5단계: 통합 분석 도구들
# python generate_ai_component_diagram.py --project-name sampleSrc
# python ai_component_analyzer.py --project-name sampleSrc
# 6단계: 기타 유틸리티 기능들
# python validation/data_quality_validator.py
# python tools/metrics.py
# python tools/seed_jsp_files.py
# python tools/enrich_run.py
# 권장 실행 시나리오
# 시나리오 1: 전체 분석 (권장)
# python ai_model_client.py
# python main.py --project-name sampleSrc --clean
# python generate_hierarchy_report.py --project-name sampleSrc
# python generate_erd_report.py --project-name sampleSrc
# python test_metadb_erd.py
# python generate_ai_component_diagram.py --project-name sampleSrc
# python generate_ai_report.py --project-name sampleSrc comprehensive local_gemma
# 시나리오 2: 빠른 구조 파악
# python ai_model_client.py
# python generate_hierarchy_report.py --project-name sampleSrc
# python generate_erd_report.py --project-name sampleSrc
# 시나리오 3: 메타정보 기반 분석
# python main.py --project-name sampleSrc --clean
# python test_metadb_erd.py
# python advanced_erd_generator.py
# 시나리오 4: AI 중심 분석
# python ai_model_client.py
# python generate_ai_component_diagram.py --project-name sampleSrc
# python generate_ai_report.py --project-name sampleSrc --custom-prompt "보안 취약점에 집중해서 분석해주세요"
# 실행 전 필수 확인사항
# ../project/sampleSrc/ 디렉토리 존재 확인
# ../project/sampleSrc/src/ Java 소스 파일 존재 확인
# ../project/sampleSrc/DB_SCHEMA/ CSV 파일 존재 확인
# Ollama 서비스 실행 상태 확인 (curl http://localhost:11434/api/tags)
# ../project/sampleSrc/report/ 디렉토리 쓰기 권한 확인
# 문제 해결 가이드
# AI 모델 연결 실패 시: python generate_ai_report.py --test-connection
# 메타데이터베이스 오류 시: rm ../project/sampleSrc/metadata.db && python main.py --project-name sampleSrc --clean
# 리포트 생성 실패 시: chmod 755 ../project/sampleSrc/report/ && python generate_hierarchy_report.py --project-name sampleSrc --verbose
# 실행 시간 예상
# AI 모델 클라이언트 테스트: 1-2초
# 메타정보 생성: 30-60초
# 계층도 분석: 0.02초
# ERD 분석: 0.01초
# AI 소스코드 분석: 60-120초
# 메타디비 ERD 분석: 1-2초
# AI 컴포넌트 다이어그램: 50-60초
# 총 실행 시간 (전체 분석): 약 3-4분