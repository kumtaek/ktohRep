# 4차 개발 결과 리뷰 및 5차 개선 계획

(Phase1 전개 문서 · prd_final.md · phase1_v4_4_implementation.md 종합 검토 기반)

---

## 1. 지금까지의 개발 이력 요약 (구현/미구현 구분 및 사유)

### 1) 구현된 항목 (핵심)

- **JSP/MyBatis 파서 고도화(정규식 → 구조 기반 병행)**  
  - JSP 스크립틀릿·표현식·MyBatis XML에서 SQL 추출, JOIN/WHERE 단서 수집.
  - 보일러플레이트 정규표현식 보완 및 토큰화/트리 기반 파싱 일부 도입.
- **보안 취약점 1차 탐지(패턴 기반)**  
  - 동적 SQL 조립(`+`, `StringBuilder`, `${}`), XSS 의심(`out.print`에 사용자 입력 포함) 등 룰.
  - 취약점 객체(유형/메시지/라인/심각도/신뢰도) 생성까지 완료.
- **로깅/설정 일원화**  
  - 콘솔/파일 핸들러 통합, 실행 파라미터 및 환경에 따른 레벨 제어.
- **병렬 처리 경로 마련**  
  - 파일 단위 비동기 실행(`asyncio.gather`)과 ThreadPool 기반 분석 경로 모두 존재.
- **DB 스키마/엔티티 골격**  
  - File/Project/Edge/SqlUnit/Join/Filter 등 메타데이터 저장 구조.

### 2) 아직 미완/미구현 또는 연계 미흡 항목

- **취약점 탐지 결과의 “종단 전파” 미흡**  
  - 파서에서 `vulnerabilities`를 만들지만, 메인/저장 로직에서 언패킹/저장/리포팅이 누락되는 구간 존재.
- **메서드 호출/파일 include 의존성 해소 미완**  
  - `_resolve_method_calls()` 미구현, JSP `<%@ include %>`, `<jsp:include>`의 파일 ID 매핑 누락.
- **경로/임포트 불일치 가능성**  
  - `main.py`가 `src/`로 이동한 뒤에도 PYTHONPATH 추가가 `src` 자신을 가리켜 `from src...` 실패 소지.
- **DB 테이블 스키마(owner) 하드코딩**  
  - `'SAMPLE'` 등 고정 owner로 매칭해 실제 스키마와 어긋날 가능성.
- **신뢰도 점수 활용 부재**  
  - 계산만 하고 결과 필터링/경고/후처리에 반영하지 않음.
- **증분 분석 모드 논리 부재**  
  - 플래그/필드는 있으나 변경 파일 선별·분석 단축 로직 미구현.
- **병렬 처리 이원화**  
  - asyncio 경로와 ThreadPool 경로가 공존하나 실제 사용은 한쪽에 치우침 → 유지보수성 저하.

> 위 구분은 Phase1 관련 `.md` 문서(Phase1*.md, prd_final.md, phase1_v4_4_implementation.md)의 “구현/미구현” 표기를 기준으로 하고, 현재 코드 흐름 점검에서 드러난 연계 누락/미완성 지점을 보강해 정리한 것입니다.

---

## 2. 4차 개발 결과 상세 리뷰 (정확성 관점 핵심 이슈)

1) **경로/임포트 안정화**  
- 증상: `main.py`가 `src/` 하위로 이동했지만 `sys.path`에 `src`만 추가하면 `import src.xxx`가 실패 가능.  
- 영향: 런타임 `ModuleNotFoundError` → 파이프라인 중단.
2) **신뢰도 계산기 임포트 불일치**  
- 증상: 통합 클래스(`ImprovedConfidenceCalculator`)로 정리했으나, 일부 모듈에서 구명칭(`ConfidenceCalculator`) 참조.  
- 영향: ImportError 또는 구/신 클래스 혼용으로 로직 의도 불일치.
3) **취약점 결과 저장/리포팅 누락**  
- 증상: 파서가 반환한 `vulnerabilities`를 메인/저장 로직이 받지 않거나 DB 반영 누락.  
- 영향: 보안 이슈가 결과물에 드러나지 않아 **정확성 체감 저하**.
4) **메서드 호출·JSP include 의존성 미해소**  
- 증상: call edge `dst_id=None`, include edge 파일 ID 매핑 미완.  
- 영향: 영향도 분석 그래프가 끊겨 **재현율/정확도 저하**.
5) **DB 스키마(owner) 고정 매칭**  
- 증상: `'SAMPLE'` 등으로 고정 조회.  
- 영향: 실제 스키마와 불일치 시 테이블 매칭 누락.
6) **신뢰도 점수 미활용/튜닝 부재**  
- 증상: 계산값을 저장만 하거나 로그로만 사용.  
- 영향: 저신뢰 결과가 동일 가중치로 섞여 **오탐 유발**.
7) **증분 분석/병렬 경로 정리 필요**  
- 증상: 증분 로직 없음, 병렬 경로 이원화.  
- 영향: 대규모 프로젝트에서 속도/일관성 저하 → 최종 정확성에도 간접 악영향.

---

## 3. 5차 개발 제안 (정확성 최우선, 성능은 차순위) — 구현 상세 & 스니펫

### A. 경로/임포트 정비 (필수 안정화)

- **목표:** 어디서 실행해도 `from src...`가 안정적으로 동작.
- **조치:** `main.py`에서 프로젝트 루트(`src`의 부모)를 PYTHONPATH에 추가.

```python
# src/main.py (머리)
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent  # <repo-root>
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

### B. 신뢰도 계산기 참조 일원화

- **목표:** 단일 구현 사용. 구명칭 참조 제거.
- **조치(간편):** alias 제공 또는 임포트 수정.

```python
# src/utils/confidence_calculator.py (파일 하단에)
ConfidenceCalculator = ImprovedConfidenceCalculator
```

또는

```python
# 사용처 예: src/parsers/jsp_mybatis_parser.py
from ..utils.confidence_calculator import ImprovedConfidenceCalculator as ConfidenceCalculator
```



※ 소스 전체적으로 ImprovedConfidenceCalculator와 같이 improved라는 단어가 포함된 경우 improved단어 제거.  제거 후 이를 참조하는 부분도 같이 improved가 제거되어야 함을 확인 할 것.
기존에 improved를 제거한 ConfidenceCalculator가 있는 경우 중복이 되는데  ConfidenceCalculator의 내용과 ImprovedConfidenceCalculator의 내용에서 중복 제거 누락이 안생기도록 로직 검토후 통합해야 함.  어떻게 통합할지는 .md 화일 내용 참고해서 판단할 것.



### C. 취약점 결과의 종단 전파 (저장/리포트)

- **목표:** 탐지된 취약점이 DB·리포트·UI에 일관 반영.
- **조치:** 파서 반환값 언패킹 → 저장 시 엔티티에 적재.

```python
# src/main.py (JSP/MyBatis 처리 흐름 예)
file_obj, sql_units, joins, filters, edges, vulnerabilities = jsp_parser.parse_file(path)
await metadata_engine.save_jsp_mybatis_analysis(
    file_obj, sql_units, joins, filters, edges, vulnerabilities
)
```

```python
# src/engine/metadata_engine.py (개념)
async def save_jsp_mybatis_analysis(self, file_obj, sql_units, joins, filters, edges, vulnerabilities):
    s = self.db_manager.get_session()
    try:
        # ... 기존 파일/SQL/edge 저장 ...
        for v in vulnerabilities:
            s.add(VulnerabilityLog(
                file_id=file_obj.file_id,
                vuln_type=v.vuln_type.value,
                severity=v.severity.value,
                message=v.message,
                line_number=v.line_number,
                confidence=v.confidence,
            ))
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
```

> **확장 제안:** 리포트 생성 시 Critical/High를 우선 노출, 해당 파일·라인 deep-link 제공.

### D. 의존성 정확도 향상 — 메서드 호출/Include 해소

- **목표:** 그래프 단절 제거 → 영향도 분석 재현율 상승.
- **조치:** 미해결 call edge 해소, JSP include 파일 ID 매핑.

```python
# src/engine/metadata_engine.py (개념)
async def _resolve_method_calls(self, session, project_id: int):
    unresolved = session.query(Edge).filter(
        Edge.edge_kind == 'call', Edge.dst_id.is_(None)
    ).all()
    for e in unresolved:
        if e.src_type != 'method':
            continue
        src = session.get(Method, e.src_id)
        if not src:
            continue
        # 1) 동일 클래스 우선
        cand = session.query(Method).filter_by(class_id=src.class_id, name=e.meta_called_name).first()
        if cand:
            e.dst_type, e.dst_id = 'method', cand.method_id
            continue
        # 2) 전역(패키지/임포트 정보 활용 여지)
        cand = session.query(Method).filter_by(name=e.meta_called_name, project_id=project_id).first()
        if cand:
            e.dst_type, e.dst_id = 'method', cand.method_id
```

```python
# JSP include 매핑 예 (저장 직후 처리)
for inc in include_deps:  # {'src': '/a.jsp', 'dst': '/b.jsp', 'confidence': 0.9}
    src_f = s.query(File).filter_by(path=inc['src'], project_id=proj_id).first()
    dst_f = s.query(File).filter_by(path=inc['dst'], project_id=proj_id).first()
    if src_f and dst_f:
        s.add(Edge(src_type='file', src_id=src_f.file_id,
                   dst_type='file', dst_id=dst_f.file_id,
                   edge_kind='includes', confidence=inc['confidence']))
```

> **장기 확대:** JavaParser/Tree-Sitter + SymbolSolver로 서명 기반 정확 매칭.

### E. DB 스키마(owner) 매칭 유연화

- **목표:** 실 스키마 반영 → 테이블 매칭 누락 최소화.
- **조치:** 고정 owner 제거, 설정/다중 스키마 고려.

```python
default_owner = self.config.get('database', {}).get('default_schema')
q = session.query(DbTable).filter(DbTable.table_name == join.l_table.upper())
if default_owner:
    q = q.filter(DbTable.owner == default_owner)
db_table = q.first()
```

### F. 신뢰도 점수 운영(필터/경고/튜닝)

- **목표:** 저신뢰 결과 억제 → Precision 향상.
- **조치:** 최소 신뢰도 임계값, suspect 플래그, 저장 제외/경고.

```python
# 예: 파일/단위별 conf 적용 (개념)
if conf_score < self.config.get('confidence', {}).get('min_confidence', 0.1):
    self.logger.warning(f"[{file_path}] 신뢰도 {conf_score:.2f} → 결과 생략")
    return {}
# 또는 DB에 is_suspect=1로 저장하고 UI/리포트에서 기본 숨김
```

> **추가:** EnrichmentLog에 전후 신뢰도 기록(LLM 보강 대비).

### G. 증분 분석 모드 구현

- **목표:** 변경 파일만 분석 → 대규모에서도 안정적 정확성(시간 내 완료).
- **조치:** 이전 해시/mtime 대조로 대상 선별.

```python
if args.incremental:
    prev = session.query(File).filter_by(project_id=project_id).all()
    prev_map = {f.path: f.hash for f in prev}
    modified = []
    for p in source_files:
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if p not in prev_map or prev_map[p] != h:
            modified.append(p)
    source_files = modified
```

### H. 병렬 처리 경로 일원화

- **목표:** 한 가지 전략으로 관리(테스트/디버그 용이).  
- **조치:** `asyncio` 기반으로 통일하고, CPU 바운드는 `run_in_executor`로 위임.

---

## 4. “향후 구현(TODO/예정)” 항목 중 5차에 실현 권고 리스트

1) **취약점 종단 전파(저장·리포트)** — *정확성 체감 즉시 향상*  
2) **메서드 호출/Include 해소** — *영향도 분석 재현율 개선*  
3) **경로/임포트/스키마 유연화** — *실행/매칭 오류 선제 차단*  
4) **신뢰도 임계값/경고 운영** — *저신뢰 잡음 억제 → Precision 상승*  
5) **증분 분석** — *현실적 운영성(대규모에서도 결과 품질 유지)*  
6) (탐색) **MyBatis `<include>`/`<bind>` 정밀 처리**, **PL/SQL 1단계 지원**

---

## 5. 왜 이렇게 우선순위를 뒀나 (결정 사유)

- **정확성 최우선 원칙**: 결과에 직접 반영되는 신호(취약점/의존성/신뢰도)를 **끝단까지 연결**하는 작업이 ROI가 가장 큼.
- **운영 안정성**: 경로/스키마/증분은 정확성의 “전제 조건” (실행/매칭 실패 → 결과 자체가 부정확).
- **확장 대비**: 6차 이후 LLM/AST 확장 때 **정확한 메타데이터**가 필요 → 지금 정합성 확보가 필수.

---

## 6. 실행 체크리스트

- [ ] `main.py` PYTHONPATH 수정 및 전 모듈 임포트 점검
- [ ] 신뢰도 계산기 참조 전면 일원화
- [ ] JSP/MyBatis 취약점 `vulnerabilities` 저장/리포트 반영
- [ ] `_resolve_method_calls` 구현 및 JSP include 매핑 저장
- [ ] DB owner 매칭 유연화(설정/다중 스키마)
- [ ] 신뢰도 임계값 정책 도입(필터/경고)
- [ ] 증분 분석 모드 활성화
- [ ] 병렬 처리 경로 통일 및 부하 테스트

---

## 7. 결론

4차까지 마련된 기반을 **정확성 중심**으로 연결·보강하면, Phase1 분석기는 **재현율/정확도 모두 개선**됩니다. 본 문서의 스니펫은 최소 침습으로 적용 가능한 형태이며, 적용 이후에는 취약점/의존성/신뢰도 신호가 **일관되고 신뢰할 수 있는 결과**로 귀결될 것입니다. 이후 단계에서는 AST/심볼 해석·PL/SQL 정밀화·LLM 보강으로 **차세대 품질**을 지향할 수 있습니다.
