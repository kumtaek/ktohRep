2.2. 문서-코드 일관성 및 문제점

- **전반적인 일관성**: 주요 `.md` 문서들은 프로젝트의 개발 현황과 계획을 잘 반영하고 있으며, 핵심 코드 파일들에서 문서에 기술된 기능들의 구현을 확인할 수 있었습니다.
- **Tree-sitter 활용의 깊이**: `java_parser.py`에서 Tree-sitter 폴백 메커니즘은 구현되었으나, Tree-sitter를 통한 클래스/메서드 메타데이터(수식어, 어노테이션, FQN, 시그니처, 반환 타입) 추출의 상세도가 `javalang` 대비 아직 부족한 것으로 보입니다. `CRITICAL_ACCURACY_IMPROVEMENTS_IMPLEMENTED.md`에서 언급된 "Comprehensive AST-based method extraction" 목표를 완전히 달성하기 위해서는 추가 개선이 필요합니다.
- **메서드 호출 관계 해결의 정교함**: `java_parser.py`의 메서드 호출 추출 및 `metadata_engine.py`의 `_resolve_method_calls`는 현재 단순화된 구현이거나 전역 검색에 의존하는 경향이 있어, 복잡한 Java 프로젝트에서 정확한 호출 관계를 식별하는 데 한계가 있을 수 있습니다. `analysis_report.md`에서 지적된 "Java 외부 의존성 해결" 및 "심볼 테이블 강화"와 연관된 부분입니다.
- **SQL 패턴 추출의 완성도**: `jsp_mybatis_parser.py`에서 `sqlparse`를 활용한 고급 SQL 패턴 추출이 도입되었으나, `_parse_join_condition` 및 `_parse_where_conditions`는 "간단 구현"으로 명시되어 있어, 복잡한 조인 및 필터 조건 추출의 정확성을 높이기 위한 추가 작업이 필요해 보입니다.
- **메서드/SQLUnit ID 할당 로직**: `metadata_engine.py`의 `_save_java_analysis_sync` 및 `_save_jsp_mybatis_analysis_sync`에서 메서드 및 조인/필터에 대한 `class_id`/`sql_id` 할당 로직은 현재 리스트 순서에 의존하는 방식으로 구현되어 있어, 잠재적인 버그 발생 가능성이 있습니다. 명시적인 매핑 또는 ID 전달 방식의 개선이 필요합니다.
- **로깅 일관성**: 일부 파서 파일(`java_parser.py`, `jsp_mybatis_parser.py`)에서 `print` 문을 사용하여 오류를 출력하는 부분이 발견되었습니다. `utils.logger.LoggerFactory`를 활용한 일관된 로깅 시스템으로 전환하는 것이 좋습니다.



3.2. `E:\SourceAnalyzer.git\phase1\src\parsers\java_parser.py`

- **구현 현황**: `parser_type` 설정에 따른 `javalang` 및 Tree-sitter 파서 선택 로직과 안전한 폴백 메커니즘이 잘 구현되어 있습니다. 이는 `CRITICAL_ACCURACY_IMPROVEMENTS_IMPLEMENTED.md`의 핵심 개선사항을 직접적으로 반영합니다.
- **문제점**: Tree-sitter 기반 추출 시 클래스/메서드의 상세 메타데이터(수식어, 어노테이션, FQN, 시그니처, 반환 타입) 추출이 아직 불완전합니다. `javalang` 및 Tree-sitter 모두 메서드 호출 관계 추출이 단순화되어 있어, 정확한 호출 그래프 구축을 위한 개선이 필요합니다.


3.3. `E:\SourceAnalyzer.git\phase1\src\database\metadata_engine.py`

- **구현 현황**: `_get_async_session`, `_get_sync_session` 컨텍스트 매니저를 통한 안전한 DB 세션 관리 및 트랜잭션 경계 설정이 잘 구현되어 있습니다. 병렬 파일 분석 (`analyze_files_parallel`), `ConfidenceCalculator` 통합, `VulnerabilityFix` 저장, `_resolve_table_usage`의 설정 기반 스키마 매칭 등 핵심 기능들이 안정적으로 동작합니다. `save_enrichment_log`를 통해 LLM 보강 이력 추적의 기반이 마련되었습니다.
- **문제점**: `_save_java_analysis_sync` 및 `_save_jsp_mybatis_analysis_sync` 내에서 메서드 및 조인/필터에 대한 `class_id`/`sql_id` 할당 로직이 잠재적인 오류를 유발할 수 있습니다. `_resolve_method_calls`의 전역 검색 방식은 복잡한 프로젝트에서 모호한 호출 관계를 유발할 수 있습니다.




주요 권고 사항:**

1. **파서의 메타데이터 추출 상세도 향상**: `java_parser.py`의 Tree-sitter 기반 추출 시 클래스/메서드의 상세 메타데이터(수식어, 어노테이션, FQN, 시그니처, 반환 타입) 추출을 보강하여 `CRITICAL_ACCURACY_IMPROVEMENTS_IMPLEMENTED.md`의 목표를 완전히 달성해야 합니다.
2. **메서드 호출 관계 해결 정교화**: `java_parser.py` 및 `metadata_engine.py`에서 메서드 호출 관계 추출 및 해결 로직을 개선하여 FQN, 임포트 정보 등을 활용한 보다 정확한 호출 그래프를 구축해야 합니다.
3. **SQL 조인/필터 추출 완성도**: `jsp_mybatis_parser.py`의 `_parse_join_condition` 및 `_parse_where_conditions`를 고도화하여 복잡한 SQL 구문에서 조인 및 필터 조건을 더 정확하게 추출해야 합니다.
4. **메서드/SQLUnit ID 할당 로직 개선**: `metadata_engine.py`의 `_save_java_analysis_sync` 및 `_save_jsp_mybatis_analysis_sync`에서 `class_id`/`sql_id` 할당 로직을 리스트 순서 의존성 없이 명시적이고 견고한 방식으로 개선해야 합니다.
5. **로깅 시스템 일원화**: 모든 파일에서 `utils.logger.LoggerFactory`를 활용한 일관된 로깅 시스템을 적용하여 `print` 문 사용을 최소화해야 합니다.