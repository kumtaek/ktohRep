# Source Docs Generator (JSP / Spring / MyBatis-Oracle)
오프라인/폐쇄망 환경에서 **소스코드만**으로 다음 산출물을 생성합니다.

## 생성 산출물 (docs/)
- endpoints.csv : 컨트롤러 매핑 요약
- sql_catalog.csv : MyBatis 매퍼/SQL 카탈로그
- deps_summary.txt, deps.dot, deps.png : jdeps 기반 의존성(선택)
- config_inventory.csv : 프로파일별 설정 키 인벤토리
- config_diff.txt : 프로파일 간 차이
- error_registry.csv : 에러코드/예외/메시지 매핑

## 요구사항
- 필수: Python 3.8+, `rg`(ripgrep)
- 권장: `ctags`, `jdeps`(JDK 포함), `dot`(graphviz), `mvn` 또는 `gradle`
- 운영체제: Linux(RHEL) / WSL / macOS

## 사용법
```bash
# 1) 프로젝트 루트에서 실행 권한 부여
chmod +x scripts/*.sh

# 2) 전체 실행 (현재 디렉터리를 분석)
make all

# 또는 각각 실행
scripts/generate_endpoints.sh .
python3 scripts/generate_sql_catalog.py .
scripts/generate_deps.sh .
python3 scripts/generate_config_inventory.py .
python3 scripts/generate_error_registry.py .
```

## 참고
- `rg` 기반 정적 스캔은 정확도가 100%가 아닙니다. 실행 환경에서 springdoc-openapi 사용 시 `/v3/api-docs`를 가져와 병합하는 것이 가장 정확합니다.
