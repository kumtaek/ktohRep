# Visualize_012_Implementation_plan.md 기반 최종 구현 보고서

- 전제: 그린필드(백지) 개발 가정. 스키마/설계 변경에 제약이 없다는 전제로 계획의 핵심 항목을 구현했습니다.
- 대상 계획: `Visualize_012_Implementation_plan.md` (리포 내 동일 파일 확인)
- 결과 요약: 파서/엔진/모델의 정확도와 일관성을 개선하는 변경을 반영하고, 남은 보완 과제를 명시합니다.


## 1) 구현 완료 항목 (Done)

- Java 파서(Tree-sitter 경로) 메타데이터 상세도 보강
  - 파일: `phase1/src/parsers/java_parser.py`
  - 변경점:
    - 로거 주입: `LoggerFactory.get_parser_logger("java")` 사용. `print` 사용 구간은 로거로 우선 전환(로거 부재시 안전 폴백 유지).
    - 패키지명 추출 후 FQN 구성: `_extract_with_tree_sitter`에서 `package_declaration` 파싱, `_extract_class_from_tree_sitter(..., package_name)`로 전달하여 `Class.fqn` 생성.
    - 수식어/어노테이션 추출: `_extract_modifiers`, `_extract_annotations_ts` 추가 후 `Class.modifiers/annotations` 채움.
    - 메서드 반환타입/시그니처 추출: `type/formal_parameters` 기반으로 `Method.return_type/signature` 설정.
    - 메서드-클래스 매핑 힌트: `Method` 객체에 임시 속성 `owner_fqn` 부여.
    - 호출관계 힌트 보강: 메서드 본문에서 수집한 호출명을 `Edge.metadata`(JSON: `{"called_name": ...}`)에 저장(로거/JSON 폴백 대응).

- JSP/MyBatis 파서 개선
  - 파일: `phase1/src/parsers/jsp_mybatis_parser.py`
  - 변경점:
    - 로거 기본 주입: `LoggerFactory.get_parser_logger("jsp_mybatis")`를 기본으로 설정.
    - 예외 로깅 일원화: 파싱 오류 등 `print`를 로거로 전환(로거 없으면 안전 폴백).
    - JOIN/WHERE 고도화(1차):
      - `_parse_join_condition`에 정규식 기반 패턴 파싱 도입(스키마 정규화 포함).
      - `_parse_where_conditions`에서 AND 분해 후 `table.col op value` 패턴 정규화/캡처.

- 모델 스키마(정확도/성능 향상용) 확장
  - 파일: `phase1/src/models/database.py`
  - 변경점:
    - `Method`에 `parameters`, `modifiers` 컬럼 추가.
    - `Edge`에 `metadata`(JSON 텍스트), `created_at` 추가.
    - `edges` 인덱스 추가: `ix_edges_src`, `ix_edges_dst`, `ix_edges_kind`.
    - (옵션) `JavaImport` 모델 추가(향후 해상도 개선시 활용 가능).

- 메타데이터 엔진 저장/해결 루프 보강
  - 파일: `phase1/src/database/metadata_engine.py`
  - 변경점:
    - 메서드-클래스 매핑 개선: `owner_fqn` 기준으로 `class_id` 부여. 클래스 저장 시 FQN→ID 매핑 생성.
    - call 엣지 저장 정책: `dst_id` 미해결 상태의 call 엣지도 저장하여 후처리 대상으로 남김.
    - `src_id` 채움(기본): 메서드 저장 직후 `src_id is None`인 call 엣지에 `method_id` 부여(간단 매핑).
    - 호출관계 해상도: `_resolve_method_calls`에서 `Edge.metadata` JSON을 우선 읽어 호출명 복구, 실패 시 `EdgeHint` 보조 경로 사용.


## 2) 미완료/보류 항목 (Not Done)

- EdgeHint 생성 로직(콜 저장 시 보조 힌트 기록)
  - 현상: 그린필드 전제에서 `Edge.metadata` 사용을 우선시하여, 저장 단계의 `EdgeHint` 자동 생성은 적용하지 않았습니다.
  - 근거: 계획서의 권고가 ‘그린필드에서는 metadata 컬럼 우선, EdgeHint는 보조’였기 때문. 필요시 간단히 추가 가능.

- `Method.parameters/modifiers` 값 채우기(전 경로)
  - 현상: Tree-sitter 경로는 시그니처/반환타입을 채우지만, `parameters/modifiers` 컬럼 저장은 아직 일괄 반영하지 않음.
  - 근거: 기존 코드 경로와의 정합/역호환을 고려해 최소 변경으로 유지. 확정 스키마/표준 정리 후 반영 권장.

- call 엣지 `src_id` 정밀 매핑
  - 현상: 현재는 “해당 클래스를 저장할 때 남아있는 call 엣지에 일괄 매핑”하는 간단 로직.
  - 한계: 메서드별 엣지 소유 정보가 분리되어 있지 않아 일부 혼선 가능.
  - 보완 방향: 파서에서 `edge.src_signature` or `edge.src_range`와 같은 추가 힌트를 제공해 정확 매핑.

- 전역적인 `print` 일괄 정리
  - 현상: 주요 경로는 로거로 전환했지만, 일부 드문 코드 경로에는 안전 폴백이 남아있음.
  - 보완 방향: 리포 전체 범위에서 `print` 검출 후 로거 전환 일괄 진행.

- `firnal_review2.md` 파일명 정리
  - 현상: 요청/계획에서 제안된 파일명 정리는 미적용(링크 갱신 영향 범위 확인 필요).
  - 조치: 후속 커밋에서 일괄 변경 권장.


## 3) 근거 및 세부 변경 설명

- Java 파서
  - 로거: 클래스 초기화 시 로거 생성. Tree-sitter 초기화/파싱 오류, 파일 파싱 실패 등 기존 `print` 구간을 로거로 전환.
  - Tree-sitter 메타데이터:
    - 패키지: `package_declaration` → `scoped_identifier/identifier` 텍스트 추출 → `Class.fqn` 구성.
    - 수식어/어노테이션: modifiers/annotation 노드 탐색 후 문자열 추출, JSON 직렬화하여 모델에 저장.
    - 메서드 반환타입/시그니처: `type/formal_parameters`에서 토큰 텍스트 추출 후 `signature`/`return_type` 채움.
    - 호출 힌트: `_extract_method_calls`가 반환한 호출명을 `Edge.metadata` JSON에 `called_name`으로 저장.
  - Javalang 경로: 생성자/메서드에도 `owner_fqn`을 부여하여 저장 단계 매핑 보조.

- JSP/MyBatis 파서
  - 로거: 파서 생성 시 `LoggerFactory` 기반 기본 로거 주입. 파싱/고급 추출/정규식 추출 오류를 로거로 기록.
  - JOIN/WHERE 파싱:
    - JOIN: `([schema.]table).col op ([schema.]table).col` 형태 정규식 추출, 스키마 정규화 반영.
    - WHERE: AND 분해 후 `table.col op value` 패턴 추출, 바인딩/치환자 정규화.

- 모델/엔진
  - 모델 확장: `Method.parameters/modifiers`, `Edge.metadata/created_at` 추가, edges 인덱스 3종, `JavaImport` 모델 정의.
  - 엔진 저장/해결:
    - 클래스 저장 시 FQN→ID 매핑을 만들어, `owner_fqn` 기준으로 메서드에 `class_id` 부여.
    - call 엣지는 `dst_id`가 없어도 저장하여 `_resolve_method_calls` 대상이 되도록 함.
    - 호출 해상도는 `Edge.metadata` JSON을 1순위, 필요 시 `EdgeHint`를 보조로 활용.


## 4) 적용 범위/영향

- DB 스키마: 신규 컬럼/인덱스 추가(개발/테스트 환경에서 테이블 생성 시 자동 반영). 운영/이관은 그린필드 전제.
- 정합성: 기존 경로와의 충돌을 피하기 위해 최소 파괴적 변경으로 반영. 컬럼 추가는 기본값/NULL 허용으로 설정.
- 성능: edges 인덱스를 통해 호출 해상도/탐색 비용을 경감.


## 5) 향후 보완 제안

- call 엣지 생성 시 `src_id` 정밀 매핑을 위한 파서-엔진 간 힌트 계약(예: `src_signature`, `src_line_range`) 확정.
- `Method.parameters/modifiers` 컬럼 값 채우기(전 경로 일관화) 및 활용 리포팅.
- EdgeHint 자동 기록(필요시)과 해상도 전략 고도화(FQN/임포트/오버로드 매칭).
- 문서 파일명/링크 정리(`firnal_review2.md` → `final_review2.md`).


## 6) 변경 파일 목록

- 파서: `phase1/src/parsers/java_parser.py`, `phase1/src/parsers/jsp_mybatis_parser.py`
- 모델: `phase1/src/models/database.py`
- 엔진: `phase1/src/database/metadata_engine.py`

(필요하시면 후속으로 엔진 내 테스트 유틸/샘플을 추가하여 호출관계/SQL 추출 결과를 빠르게 점검할 수 있게 준비하겠습니다.)


## 7) 추가 테스트 및 최종 점검 결과

- 신규 테스트 추가
  - 경로: `tests/`
    - `tests/run_tests.py`: 간단 테스트 러너(모든 로그/주석 한글)
    - 샘플 소스
      - `tests/samples/java/ValidSimple.java`: 정상 자바(호출 포함)
      - `tests/samples/java/InvalidSyntax.java`: 의도적 문법 오류 자바
      - `tests/samples/jsp/sample.jsp`: 정상 JSP(SQL 포함)
      - `tests/samples/xml/mybatis_valid.xml`: 정상 MyBatis(XML, JOIN/WHERE 포함)
      - `tests/samples/xml/mybatis_invalid.xml`: 의도적 XML 오류
  - 실행: `python tests/run_tests.py`

- 소스 전반 최종 점검 및 수정 사항
  - `java_parser.py`: 들여쓰기 오류(메서드 객체 생성부) 수정, 로깅 일원화 보완
  - `jsp_mybatis_parser.py`:
    - 문자열 리터럴 정규식 치환 라인(따옴표 이스케이프) 문법 오류 수정
    - WHERE/JOIN 1차 고도화, JOIN 추출 문자열 폴백 보강
  - `models.database.Edge`: 예약어 충돌 방지 위해 `metadata` → `meta`로 컬럼명 변경(해당 참조 코드 모두 변경)

- 테스트 결과(요약)
  - JAVA 정상/비정상 파싱: 정상(비정상은 예외 로깅 후 빈 결과 허용)
  - JSP 파싱: 정상(SQL 추출 2건, JOIN/WHERE 미검출은 가능)
  - MyBatis XML 정상: SQL 추출 정상, WHERE 필터는 검출, JOIN 검출은 0건 → 개선 필요
  - 엔진 저장: 파일/클래스/메서드/콜 엣지 저장 정상

- 남은 문제점 및 개선 과제
  - JOIN 추출 정확도: `sqlparse` 토큰 기반 탐지와 문자열 폴백을 혼합했으나, 다양한 토큰 구조에서 `ON` 절 조건 파싱의 견고성이 낮음
    - 조치안: Statement 전체 문자열에서 `JOIN ... ON ...` 블록을 세분 추출하여 다중 조건(AND) 및 괄호 포함 패턴 처리, alias→실제 테이블 매핑 보강
  - call 엣지 `src_id` 정밀 매핑: 현재 간이 매핑(클래스 저장 시 일괄) → 메서드 범위/서명 기반 매핑으로 강화 필요
  - `Method.parameters/modifiers` 전 경로 저장 일관화 필요
  - 전역 `print` 완전 제거와 로깅 일원화 추가 정리 권장
