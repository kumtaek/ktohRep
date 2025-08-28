# 최종 리뷰 리포트 (3차 개발 결과 점검 + 4차 개선 제안)

> 사용자의 다음 메시지 이후 제가 드린 모든 답변(요청 확인 포함)을 하나의 문서로 정리한 최종본입니다.  
> 기준 메시지:  
> 1) 그게 최종이고, 현재 소스가 최종 산출물이야. 그간 여러차례 개선 작업에 대한 명세는 .md 화일들 다 검토해보고 문제점 및 4차 개선작업을 제안해줘.  
> 2) 인터넷 검색 등 너의 창의적인 발생을 기대해볼께.  
> 3) 1단계_003차_개발후_1_리뷰_중복정리필요.md 화일에 명시되어 있고 직전에 니가 검토한 내용이야. 언급했듯이 그간 작업 내역인 .md화일들의 내용이 누락없이 현재 소스에 적용되어 있는지도 니가 점검해야 할 일이야.

---

## 0) 요청 확인(당시 답변 요지)

- 지금까지의 모든 .md 문서를 기반으로 한 개발 이력을 전반적으로 점검하고, **중복 정리 결과의 적정성과 누락 여부**, 그리고 **현재 소스 코드에서의 import 경로 및 영향도**까지 확인하겠습니다.  
- 이후 **정확성 향상**을 최우선 목표로 한 4차 개발 제안을 포함해 리뷰 리포트를 작성하겠습니다.

---

## 1) 3차 개발 결과 코드 리뷰

### 1-1. 중복 소스 통합 및 누락 사항 점검

**(A) `main.py` 이동에 따른 경로 설정 오류**  
- 3차 개발 후 `main.py`가 `./src`로 이동했지만, 코드에서 `sys.path` 추가가 **`src` 디렉토리**로 고정되어 있어 `from src...` 임포트가 실패할 수 있습니다.  
- **개선 방향:** `main.py`에서는 프로젝트 루트(= `src`의 부모)를 PYTHONPATH에 추가해야 합니다.

```python
# main.py - 프로젝트 루트 경로 추가 (수정안)
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent  # src의 부모 디렉토리
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

**(B) 신뢰도 계산 모듈의 중복/불일치**  
- 개선된 `ImprovedConfidenceCalculator`가 도입되었으나, 일부 파일은 여전히 **구 파일명**(`improved_confidence_calculator.py`)을 임포트하거나, **구 클래스명**(`ConfidenceCalculator`)을 참조합니다.  
- **영향:** 런타임 import 오류 / 클래스 불일치.  
- **개선 방향:** 파일을 **단일 모듈**(`src/utils/confidence_calculator.py`)로 일원화하고, 모든 참조를 동일한 클래스명으로 맞춥니다.

```python
# 예) 모두 다음과 같이 통일
from src.utils.confidence_calculator import ImprovedConfidenceCalculator
# 필요 시
from src.utils.confidence_calculator import ImprovedConfidenceCalculator as ConfidenceCalculator
```

**(C) 이름 충돌(예: `ParseResult`)**  
- ORM 모델(`models/database.py`)의 `ParseResult`와 유틸 데이터클래스 `ParseResult`가 공존해 **네이밍 충돌/혼란** 발생 가능.  
- **개선 방향:** ORM 쪽을 `ParseResultModel` 등으로 리네이밍하거나, 임포트 시 명시적 별칭을 강제.

```python
from src.models.database import ParseResult as ParseResultModel  # 명시적 별칭
```

**(D) 로깅 시스템 통합 상태**  
- `src/utils/logger.py`로 **콘솔/파일 로깅이 일원화**되어 중복 로거 문제는 해소된 것으로 판단.  
- **권고:** 설정 주입(레벨/포맷/파일 경로)이 일관되게 적용되는지 점검.

**(E) 리뷰/개발 .md → 코드 반영 누락 점검 (샘플)**  
- 3차 개발 명세에서 기술된 항목은 대체로 반영되었으나, 아래 항목은 **연계/활용 미흡** 또는 **마무리 누락**:
  - **병렬 처리:** `MetadataEngine.analyze_files_parallel` 구현 대비, 실제 실행 경로는 별도 `asyncio.gather` 중심 → **병렬화 경로 이원화** 및 **증분 옵션 미활용**.
  - **신뢰도 점수 활용:** 계산만 하고 결과 선별·경고·후처리(LLM 보강 등)에 **직접 반영되지 않음**.
  - **취약점 탐지 결과:** JSP/MyBatis 파서가 `vulnerabilities`를 반환하지만, **`main.py` 언패킹 불일치** 및 **저장/출력 누락**.
  - **메서드 호출 해소:** `_resolve_method_calls` 미구현으로 **호출 관계 Edge** 정확도 저하.
  - **JSP include 의존성:** 파일 ID 미연결로 **Edge 저장 누락** 케이스 존재.
  - **DB 테이블 사용 주체(owner) 하드코딩:** 예: `'SAMPLE'` 고정 등의 임시 처리 → 실제 스키마와 어긋날 위험.

---

### 1-2. 정확성 관점 핵심 문제 요약
1) 경로/임포트 불일치로 **모듈 로드 실패 위험**  
2) 신뢰도/취약점 등의 **핵심 신호가 결과에 반영되지 않음**  
3) 메서드 호출/JSP include 등 **의존 관계 해소 누락** → 영향도 분석 정확도 저하  
4) 문서(PRD/리뷰)의 의도 대비 **증분 분석/정적 분석 범위가 미흡**

---

## 2) 4차 개발(정확성 우선) 개선 제안 + 핵심 스니펫

### 2-1. 모듈 경로 및 import 정리
- `main.py` 경로 수정(위 A안 적용) + `src/__init__.py` 존재 확인.  
- 신뢰도 계산기 임포트 **일원화**(위 B안 적용).  
- 이름 충돌은 **별칭/리네이밍**으로 제거(위 C안).

### 2-2. 취약점 탐지 결과를 1급 산출물로 편입
**목표:** 탐지 결과를 DB/리포트/UI까지 **끝단까지 전파** → 정확성 체감 상승

```python
# metadata_engine.py (개요) : JSP/MyBatis 저장 로직에 vulnerabilities 반영
async def save_jsp_mybatis_analysis(self, file_obj, sql_units, joins, filters, edges, vulnerabilities):
    session = self.db_manager.get_session()
    # 1) 기존 메타데이터 저장
    # ... (생략)
    # 2) 취약점 저장
    for vuln in vulnerabilities:
        session.add(VulnerabilityLog(
            file_id=file_obj.file_id,
            vuln_type=vuln.vuln_type,     # e.g., "SQL_INJECTION"
            severity=vuln.severity,       # e.g., "HIGH"
            message=vuln.message,
            line=vuln.line_number,
            confidence=vuln.confidence
        ))
    session.commit()
```

```python
# main.py : JSP 파서 반환값 언패킹 일치시키기 (6개 받기)
file_obj, sql_units, joins, filters, edges, vulnerabilities = jsp_parser.parse_file(path)
await metadata_engine.save_jsp_mybatis_analysis(
    file_obj, sql_units, joins, filters, edges, vulnerabilities
)
```

### 2-3. 의존성 정확도 향상(메서드 호출 + JSP include)
**호출 관계 해소:** AST/심볼 해석 기반으로 **정확 매칭** 구현  
- Java: `javalang`/Tree-Sitter/JavaParser(+SymbolSolver) 활용
- 우선은 **동일 클래스 내 호출** → **패키지/임포트 기반 외부 클래스 호출** 순으로 단계적 해소

```python
# metadata_engine._resolve_method_calls (개념 예시)
for edge in unresolved_calls:  # dst_id 없음
    src = session.get(Method, edge.src_id)
    if not src: 
        continue
    # 1) 동일 클래스 내 동명이칭 메서드 우선
    cand = session.query(Method).filter_by(class_id=src.class_id, name=edge.meta_called_name).first()
    if cand:
        edge.dst_type, edge.dst_id = 'method', cand.method_id
        continue
    # 2) 전역 검색(패키지/임포트 정보 활용해 범위 축소)
    cand = session.query(Method).filter_by(name=edge.meta_called_name).first()
    if cand:
        edge.dst_type, edge.dst_id = 'method', cand.method_id
```

**JSP include 연결:** 파서 단계에서 **source/target 경로**를 반환 → 저장 단계에서 **파일 ID 매핑 후 Edge 생성**

```python
# save_jsp_mybatis_analysis 내부 (개념 예시)
for inc in include_deps:  # [{'src': '/a.jsp', 'dst': '/b.jsp', 'confidence': 0.9}, ...]
    src_file = session.query(File).filter_by(path=inc['src'], project_id=proj_id).first()
    dst_file = session.query(File).filter_by(path=inc['dst'], project_id=proj_id).first()
    if src_file and dst_file:
        session.add(Edge(
            src_type='file', src_id=src_file.file_id,
            dst_type='file', dst_id=dst_file.file_id,
            edge_kind='includes', confidence=inc['confidence']
        ))
```

### 2-4. 정적 분석 범위 확대(정확성 핵심)
- **PL/SQL 파싱**: ANTLR4 PL/SQL grammar + SQLGlot로 SQL 정규화 → **조인/필터 추출 누락 최소화**  
- **Java AST/심볼 해석**: 상속/오버로드/람다/스트림 API까지 정확히 모델링 → **호출 관계 정확도↑**  
- **MyBatis XML 처리 강화**: `<include>`, `<bind>`, 동적 SQL 태그 등 정밀 반영  
- **정규표현식 의존 완화**: AST 기반으로 스크립틀릿/동적 문자열에서의 SQL을 최대한 구조화

### 2-5. 신뢰도 점수의 실사용
- **임계값 전략:** `confidence_threshold` 아래 항목은 결과에 경고 플래그 또는 기본 숨김 처리.  
- **튜닝:** 동적 SQL/리플렉션/미해결 호출 등 **감점 룰** 세분화.  
- **LLM 보강 로그 준비:** `EnrichmentLog`에 프롬프트/모델/결과/점수 변동을 기록 → 품질 추적/회귀 방지.

### 2-6. 증분 분석 가동(성능 부차적 향상 + 정확성 안정화)
- 파일 해시/mtime 비교로 **변경 파일만 분석**.  
- 변경 파급(의존성 기반) 고려해 **필요 범위만 재분석** → 결과 일관성 유지.

---

## 3) 액션 아이템 체크리스트 (실행 순서 제안)

1. **경로/임포트 정리**: `main.py` path fix, 신뢰도 계산기 import 일원화, `ParseResult` 네이밍 충돌 해소  
2. **파서 반환값/저장 로직 정합화**: `vulnerabilities` DB 저장/리포트 반영  
3. **호출/Include 의존성 해소**: `_resolve_method_calls` 구현, JSP include ID 매핑 저장  
4. **정적 분석 확장**: PL/SQL 파싱 파이프라인, Java AST·심볼 해석 도입 계획 수립  
5. **신뢰도 점수 운영화**: 임계값 정책/경고, LLM 보강 로그 골격 구현  
6. **증분 분석 활성화**: 해시/mtime 기반 변경 감지 및 부분 재분석

---

## 4) 결론

3차에서 **핵심 구조와 로깅/신뢰도/취약점 탐지 기반은 마련**되었습니다. 4차에서는 이 신호들을 **끝단까지 연결**(DB/리포트/질의응답)하고, **의존성 해소의 정확성**을 끌어올리며, **정적 분석 범위 확대**를 통해 누락을 줄이는 전략이 최우선입니다. 이 로드맵대로 진행하면 **정확성(Precision/Recall) 체감이 뚜렷**해지고, 성능(증분/병렬)은 자연스럽게 뒤따라 개선될 것입니다.
