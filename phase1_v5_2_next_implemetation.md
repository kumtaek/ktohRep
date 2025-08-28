# 5차 개발 결과 리뷰 및 5.2 개선 계획

(Phase1_v5_1_implementation.md · phase1_v5_1_to_be_improved.md · prd_final.md 등 기존 산출물 검토 기반)

---

## 1. 지금까지의 개발 이력 요약 (구현/미구현 구분 및 사유)

### 1) 구현된 핵심 항목 (v5.1 기준)

- **증분 분석 모드 도입**: 파일 해시를 이용한 변경 감지 및 `--incremental` 플래그 지원으로 변경된 파일만 선별 분석하는 기능 구현. 대규모 프로젝트에서 약 80~90% 분석 시간 단축 기대.  
- **DB 스키마 소유자 설정 지원**: `'SAMPLE'` 등 하드코딩된 스키마명을 제거하고 `config.yaml`의 `database.default_schema` 값을 활용하여 동적으로 테이블 owner를 매칭하도록 개선. 다양한 환경에서 테이블 식별 정확도 향상.  
- **신뢰도 임계값 기반 필터링**: `processing.confidence_threshold` 설정을 추가하여 일정 신뢰도 미만의 엣지(edge)를 결과에서 제외하도록 로직 구현. 저신뢰성 잡음 데이터를 걸러내어 **분석 정확도 약 15% 향상**.  
- **보안 취약점 탐지 및 저장 강화**: OWASP Top 10 기반 **10가지 취약점 패턴**을 식별하는 테스트 케이스 및 코드 추가. JSP/SQL 파서가 반환하는 `vulnerabilities` 리스트를 메인 흐름에서 DB에 저장하도록 수정하여 취약점 결과의 **종단 전파**를 완성.  
- **메서드 호출 관계 해소**: `_resolve_method_calls()` 구현을 통해 호출 관계 엣지의 `dst_id=None`인 미해결 항목을 실제 메서드로 연결하도록 보완. 동일 클래스 우선 매칭 후 전역 범위 검색을 수행하고, 해소 성공/실패에 따라 엣지 신뢰도를 가산/감산하여 **영향도 그래프의 정확도 상승**. JSP 파일 간 include 관계도 파일 ID로 연결하여 그래프 단절을 해소함.  
- **기타 안정성 개선**: `main.py`에서 `sys.path` 경로 설정을 수정하여 어느 경로에서 실행해도 안정적으로 `src` 모듈을 임포트하도록 개선. `ConfidenceCalculator` 클래스 명칭/경로 불일치 문제를 해결하여 일관된 개선된 신뢰도 계산 클래스를 참조하도록 수정. 로깅 체계 일원화, config 파일 확장 및 복잡도 기반 신뢰도 계산(중첩도, 분기 수 등 반영) 등 부가 개선도 v5.1에 반영.

### 2) 미구현 또는 추가 개선이 필요한 항목

- **MyBatis `<include>` 및 `<bind>` 구문 정밀 처리 미흡**: MyBatis XML 내 SQL 조각 재사용(`<include>`)과 동적 변수 바인딩(`<bind>`)에 대한 파싱/분석이 아직 구현되지 않았습니다. 그로 인해 일부 쿼리의 실제 구조 (테이블, 조건)가 누락될 소지가 남아 있어 향후 개선이 필요합니다.  
- **PL/SQL 코드에 대한 지원 부족**: Oracle DB 내 저장 프로시저/함수(PL/SQL)에 대한 메타정보 수집이 이루어지지 않았습니다. 애플리케이션이 PL/SQL을 호출하는 경우 해당 의존성이 분석 결과에 포함되지 않는 한계가 있습니다.  
- **병렬 처리 경로 이원화 지속**: asyncio 기반 비동기 처리와 ThreadPool 기반 처리 로직이 동시에 존재하나 아직 하나로 통합되지 않았습니다.  
- **신뢰도 낮은 결과의 활용 제한**: 임계치 미만의 결과를 필터링하는 방식으로 정확도를 높였으나, 일부 낮은 신뢰도의 정보는 DB에 저장되지 않고 완전히 버려지는 상황입니다.  
- **증분 분석 보완 사항**: 증분 모드에서 삭제된 파일에 대한 처리 로직이 없습니다. 이전 분석에는 존재했지만 현재 삭제된 파일의 메타데이터가 DB에 남아 있을 수 있어, 시간이 지남에 따라 결과 일관성이 저하될 우려가 있습니다.  
- **LLM 및 AST 등 대형 기능 미도입**: LLM을 통한 메타정보 보강이나 Java/SQL 구문의 정밀 AST 파싱 등은 Phase2 혹은 6차 이후 단계에서 고려할 확장 기능으로서, 아직 Phase1 범위에는 구현되지 않았습니다.

---

## 2. 5차 개발 결과 리뷰 (정확성 관점 주요 이슈)

1) **MyBatis SQL `<include>` 처리 미비로 인한 쿼리 분석 누락**  
- include 구문이 제대로 해석되지 않아 공통 SQL 조각 누락 → 분석 정확도 저하

2) **MyBatis `<bind>` 동적 변수의 분석 반영 한계**  
- 동적 변수 바인딩 분석 부재 → 취약점 탐지 및 메타정보 누락

3) **삭제된 소스 파일에 대한 잔여 메타정보**  
- 증분 모드에서 삭제된 파일 처리 없음 → 오래된 Edge 잔존

4) **신뢰도 임계치 적용에 따른 정보 손실 우려**  
- 저신뢰 결과를 완전히 버려서 재현율 저하 가능성

5) **분산 처리 경로의 일관성 문제**  
- asyncio vs ThreadPool 이원화로 결과 불일치 가능성

---

## 3. 5.2차 개발 제안 (정확성 최우선 개선 사항) — 구현 방안 & 스니펫

### A. MyBatis `<include>`/`<bind>` 구문 지원 강화

```python
# MyBatis XML 파싱 단계 (개념적 구현)
sql_blocks = {}  
for node in mapper_xml.findall('sql'):
    sql_blocks[node.get('id')] = node.text

for elem in mapper_xml:
    if elem.tag == 'include':
        refid = elem.get('refid')
        included_sql = sql_blocks.get(refid, '')
        query_text = query_text.replace(f'<include refid="{refid}" />', included_sql)
    elif elem.tag == 'bind':
        var_name = elem.get('name')
        var_expr = elem.get('value')
        logger.info(f"Detected MyBatis bind: {var_name} = {var_expr}")
```

---

### B. 증분 분석 시 삭제 파일 처리 로직 추가

```python
prev_files = {f.path for f in session.query(File).filter_by(project_id=project_id).all()}
curr_files = {path for path in scan_source_paths(project_root)}
removed_files = prev_files - curr_files

for file_path in removed_files:
    file_obj = session.query(File).filter_by(project_id=project_id, path=file_path).first()
    if file_obj:
        session.query(Edge).filter(Edge.src_id == file_obj.file_id or Edge.dst_id == file_obj.file_id).delete()
        session.query(Class).filter_by(file_id=file_obj.file_id).delete()
        session.query(File).filter_by(file_id=file_obj.file_id).delete()
        logger.warning(f"Removed file metadata cleanup: {file_path}")
```

---

### C. DB 테이블 스키마 매칭 유연성 추가

```python
default_owner = config.get('database', {}).get('default_schema')
q = session.query(DbTable).filter(DbTable.table_name == target_table.upper())
if default_owner:
    db_table = q.filter(DbTable.owner == default_owner).first()
    if not db_table:
        logger.warning(f"Default schema '{default_owner}' not matched; trying global search")
        db_table = session.query(DbTable).filter(DbTable.table_name == target_table.upper()).first()
else:
    db_table = q.first()
```

---

### D. 저신뢰 결과 처리 방식 개선 (‘suspect’ 표기 도입)

```python
confidence_threshold = config.get('processing', {}).get('confidence_threshold', 0.5)
for edge in edges:
    edge.is_suspect = False
    if edge.confidence < confidence_threshold:
        edge.is_suspect = True
    session.add(edge)

edges_to_report = session.query(Edge).filter_by(project_id=pid, is_suspect=False).all()
generate_report(edges_to_report)
```

---

### E. 병렬 처리 경로 단일화 (asyncio 통합)

```python
# 기존 ThreadPool 기반
results = []
with ThreadPoolExecutor() as pool:
    for file in files:
        results.append(pool.submit(analyze_file, file))
    for r in results:
        process(r.result())

# 개선 후 asyncio 통합
async def analyze_all_files(file_list):
    tasks = [analyze_file_async(file) for file in file_list]
    results = await asyncio.gather(*tasks)
    for res in results:
        process(res)
```

---

### F. (탐색) Oracle PL/SQL 초기 지원

- Java 코드 내 `CallableStatement` → Edge 추가  
- DB 메타정보 `ALL_PROCEDURES`, `ALL_SOURCE` → CSV 기반 매핑 고려

---

## 4. 5.2 개발 권고 항목 목록

1. **MyBatis `<include>`/`<bind>` 처리**  
2. **증분 분석 삭제 파일 정리**  
3. **DB 스키마 매칭 범위 확장**  
4. **저신뢰 Edge suspect 표기**  
5. **병렬 처리 경로 단일화**  
6. (옵션) **PL/SQL 호출 관계 지원**

---

## 5. 우선순위 선정 근거

- 정확성 및 신뢰도 향상 최우선  
- 데이터 정합성과 일관성  
- 정확성 vs 재현율 균형  
- 유지보수성 및 확장 대비  
- 범위와 난이도의 균형  

---

## 6. 차기 단계에서 제외된 항목 및 제외 사유

- **LLM 보강 시스템 연계**: Phase2 예정, 현 단계 제외  
- **정밀 AST 파싱 및 심볼 해석**: 구현 복잡도와 ROI 고려, 보류  
- **Neo4j 등 그래프 DB 연동**: 정확성에는 영향 적음, Phase2 이후 고려  
- **기타 경미한 개선 사항**: 핵심 정확도에 직접 영향 없음, 후순위
