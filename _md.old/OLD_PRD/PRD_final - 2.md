## 2단계: 질의응답 및 영향평가

### 4.1. 목표 및 정책

● 4.1.1. **자연어 질의**: **파일·메소드·SQL 요약/탐색/영향도 분석**
● 4.1.2. **재현율 우선**: 누락 최소화(과포함 허용), 결과에 CONFIDENCE/근거·라인Range 제시
● 4.1.3. **모델**: 기본 **Qwen2.5 7B**, 복잡도/불확실성↑ 시 **Qwen2.5 32B 폴백**

### 4.2. 오케스트레이터 플로우 (Advanced RAG)

● 4.2.1. **의도 분류**: 사용자의 자연어 질의 의도를 요약, 탐색, 영향 분석 등으로 정확하게 분류하는 로직 구현.
● 4.2.2. **초기 검색 (Retrieval)**: Faiss 인덱스를 사용해 1차적으로 관련성이 높은 증거 후보군을 신속하게 검색합니다.
● 4.2.3. **증거 확장 (Multi-hop Reasoning)**: 초기 검색 결과에서 핵심 엔티티(메서드명, 클래스명 등)를 추출하고, 이를 새로운 검색어로 사용하여 2차, 3차 검색을 반복 수행하며 관련 증거를 확장 수집합니다. (최대 홉 수 조절 가능) 이를 통해 단일 검색으로는 찾기 어려운, 여러 단계에 걸친 관계를 추론할 수 있습니다.
● 4.2.4. **정밀 재랭킹 (Re-ranking)**: 초기 임베딩 검색으로 top‑k 후보를 수집한 후, 확장된 증거 후보군 전체를 대상으로 원본 질문과의 관련성을 Cross‑Encoder 모델을 사용해 정밀하게 재계산합니다. 재랭커로는 기존에 사용하던 `monologg/koelectra-base-v3-discriminator`와 `BAAI/bge‑reranker‑base` 뿐만 아니라 2024년 3월 출시된 **BGE reranker v2**(긴 입력과 다국어를 지원하여 한국어·영어 혼합 질의에서 더욱 정확한 랭킹을 제공) 등 다양한 Cross‑Encoder 모델을 사용할 수 있습니다. Cross‑Encoder는 관련성이 높은 순으로 증거를 정렬하여 LLM에 전달할 최종 증거 목록을 선별합니다.
● 4.2.5. **모델 선택**: 최종 증거의 평균 신뢰도(`avg_conf`)와 개수를 바탕으로, 비용 효율적인 모델(Qwen2.5 7B) 또는 고성능 폴백 모델(Qwen2.5 32B)을 동적으로 선택합니다.
● 4.2.6. **프롬프트 엔지니어링 및 답변 생성**: 구조화된 시스템 프롬프트를 사용하여 LLM에게 명확한 역할과 답변 형식(Markdown, 출처 표기 등)을 지시합니다. 정제된 최종 증거를 첨부하여 LLM이 환각(Hallucination) 없이, 근거에 기반한 답변을 생성하도록 유도합니다.
● 4.2.7. **로그**: 전체 파이프라인의 각 단계(검색, 확장, 재랭킹)에서 사용된 파라미터, 중간 결과, 최종 답변, 모델 정보 등을 상세히 기록하여 추적성과 디버깅 용이성을 확보합니다.

### 4.3. API (OpenAPI 요약) (v2.0 요약 및 예시 반영)

```yaml
openapi: 3.0.3
info: {title: Source Q&A/Impact API, version: 1.0.0}
paths:
  /query:
    post:
      summary: 자연어 질의응답(요약/탐색/영향)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                project_root: {type: string}
                question: {type: string}
                recall_priority: {type: boolean, default: true}
                k: {type: integer, default: 20}
                max_hops: {type: integer, default: 2}
                model_pref: {type: string, enum: [auto, qwen2.5-7b, qwen2.5-32b], default: auto}
      responses:
        '200': {description: OK}
  /impact:
    post:
      summary: 특정 아티팩트(파일/메소드/SQL) 영향도 분석
  /search:
    post:
      summary: 구조/그래프 기반 탐색(필터링)
```

● 4.3.1. **자연어 질의응답**: `/query` API 엔드포인트 구현. FastAPI를 사용하여 `project_root`, `question`, `recall_priority`, `k`, `max_hops`, `model_pref`를 입력으로 받는 비동기 POST 엔드포인트를 구현합니다.

- **`/query` 예시-업무로직**
  
  ```json
  POST /query
  { "project_root": "insurance-core",
    "question": "해약환급금 계산 로직이 어디에 구현돼 있나?",
    "recall_priority": true, "k": 40 }
  ```
  
  응답: RefundService.calculateRefund(), RefundRuleApplier.apply()

- **`/query` 예시-SQL 집계**
  
  ```json
  POST /query
  { "project_root": "insurance-core",
    "question": "월별 신규계약 집계 SQL과 테이블/조인 조건 알려줘" }
  ```
  
  응답: ContractMapper.getMonthlyNewCount, POLICY-CUSTOMER join, 필터 DEL_YN='N'

- **`/query` 예시-보안 취약**
  
  ```json
  POST /query
  { "project_root": "insurance-core",
    "question": "동적 SQL 중 보안상 취약해 보이는 구문은?" }
  ```
  
  응답: OrderMapper.searchOrders에서 ${param} 패턴 사용

● 4.3.2. **특정 아티팩트 영향도 분석**: `/impact` API 엔드포인트 구현. FastAPI를 사용하여 특정 아티팩트(파일/메소드/SQL)의 ID와 유형을 입력으로 받아 영향도를 분석하는 비동기 POST 엔드포인트를 구현합니다.

- **`/impact` 예시**
  
  ```json
  POST /impact
  { "project_root": "insurance-core",
    "artifact_type": "method",
    "artifact_ref": {"class":"com.life.RefundService","method":"calculateRefund"} }
  ```
  
  응답: RefundController.getRefund(), PolicyMapper.getPolicyDetail, POLICY table

● 4.3.3. **구조/그래프 기반 탐색**: `/search` API 엔드포인트 구현. FastAPI를 사용하여 필터링 조건을 입력으로 받아 구조/그래프 기반 탐색을 수행하는 비동기 POST 엔드포인트를 구현합니다.

- **`/search` 예시**
  
  ```json
  POST /search
  { "project_root": "insurance-core",
    "filters": {"entity":"method","annotation":"Transactional"} }
  ```
  
  응답: PaymentService.pay, RefundService.calculateRefund

---

## 5. 알고리즘 및 규칙

### 5.1. 알고리즘 요약

- Java/Spring: AST 분석 + 어노테이션 처리
- JSP/MyBatis: include, 동적 SQL superset 처리
- SQL: 조인·필수 필터 추출, PK/FK 매핑
- CONFIDENCE 산식: AST/Static/DB/LLM 가중 합산
- LLM guardrail: JSON 출력, temperature=0

### 5.2. 조인 및 필수 필터 규칙

● 5.2.1. **조인**: AST에서 `Join` 노드 수집, `A.col = B.col` 등 **동치 조건** 우선, 비동치도 저장(op)

● 5.2.2. **필수 필터**: MyBatis 동적 태그 영역 **외부의 WHERE 조건** 또는 모든 분기 공통 조건 → `always_applied=1`

● 5.2.3. **실관계 vs 인조 PK**: PK CSV와 무관하게 **빈도/위치 기반** 실조인 후보 추정, `inferred_pkfk=1`

### 5.3. CONFIDENCE 산식 (권장)

```
conf = w_ast*q_ast + w_static*q_static + w_db*q_db + w_llm*q_llm
- 동적 SQL/리플렉션/표현식 복잡도는 감점
- LLM 보강 시 post_conf = min(1.0, conf + delta(model, evidence))
- 전/후 및 근거를 enrichment_logs에 기록
```

---

## 6. 임베딩 및 RAG 상세

### 6.1. 임베딩

● 6.1.1. **모델**: 다국어 지원 및 소스코드에 특화된 임베딩 모델을 사용합니다. 특히 한국어 및 소스코드의 의미를 효과적으로 벡터화하기 위해 `BAAI/bge-m3` (한국어 최적화 버전) 또는 `jhgan00/ko-sentence-transformers`와 같이 한국어에 특화된 모델을 검토합니다. **(대안: `OpenAIEmbeddings`는 오프라인/무료 라이선스 기준 미충족으로 제외. `BAAI/bge-m3` 한국어 최적화 버전을 주요 대안으로 고려)**. 모델은 오프라인 환경에 배포됩니다.

- `BAAI/bge-m3` 모델 카드는 100개 이상의 언어를 지원하고 최대 8 192 토큰의 장문 컨텍스트를 처리하며, 스파스(BM25)·멀티벡터 검색을 동시에 수행하는 하이브리드 임베딩을 권장합니다. 검색 이후에는 `BAAI/bge-reranker-base` 또는 v2 모델을 Cross‑Encoder 재랭커로 사용하여 정확도를 높일 수 있습니다.
  ● 6.1.2. **인덱스**: `faiss-cpu`를 사용하여 메모리 효율적인 벡터 인덱스를 구축하고(GPU도 선택적으로 사용가능하도록), 빠른 유사도 검색을 수행합니다. 파일명은 `faiss.index`입니다.
  ● 6.1.3. **청킹**: 분석된 메소드, SQL 구문, 요약 등을 의미 있는 단위(300-600 토큰)로 분할하여 검색 정확도를 높입니다.

- **임베딩 정의 강화**: chunks는 메소드/SQL/JSP 블록을 토큰 단위 분할, embeddings는 언어/코드 모델 벡터 저장.

### 6.2. 검색

● 6.2.1. **검색 방식**: 기존의 키워드 기반 BoW(Bag-of-Words) 검색 방식과 **의미론적 검색(Semantic Search)**를 병용하고 REORDER하며, 희소(BM25) 점수와 임베딩 유사도 점수를 혼합하는 **하이브리드 검색(Hybrid Retrieval)** 전략을 적용합니다.
● 6.2.2. **아키텍처**: 다국어 지원, 소스코드에 특화된 임베딩 라이브러리(예: LangChain의 `HuggingFaceInstructEmbeddings`와 같은 인터페이스를 활용하며, 실제 임베딩은 로컬 모델로 대체)를 통해 텍스트를 고차원 벡터로 임베딩하고, `Faiss` 벡터 데이터베이스를 사용하여 유사도 기반의 빠르고 정확한 검색을 수행합니다.

- **임베딩 Dual 전략 상세**:
  1) 언어 임베딩(BAAI/bge-m3 또는 jhgan00/ko-sentence-transformers) top-k_L, 코드 임베딩(CodeT5+) top-k_C 검색
  2) 각 score를 정규화(z-score 또는 min-max), 필요시 Platt scaling
  3) 교집합 항목은 α·L+β·C, 단일 공간은 해당 가중만 반영
  4) 코드공간 고득점 항목은 키워드/그래프근접성/언어공간 하한선 중 하나 이상 충족 시 반영 (스푸리어스 방지)
  5) 상위 M 후보는 cross-encoder 재랭킹 후 최종 top-n

---

## 7. 성능 및 용량 계획 (A30, 단일 서버)

### 7.1. 성능 최적화

● **파서/ETL**: CPU 다코어 활용(멀티스레드); LLM 요청은 배치/비동기
● **메모리**: SQLite WAL 모드, 인덱스 일괄 생성, 요약/코멘트 분리 저장으로 I/O 절감

### 7.2. 용량 추정 (1M LOC, SQL 5k개 기준)

● 7.2.1. **SQLite DB**: 1~3GB
● 7.2.2. **FAISS**: 1~2GB(임베딩 dim/압축에 의존)

---

## 8. 배포 및 운영

### 8.1. 배포 환경

● 8.1.1. **오프라인 설치**: 모든 Python 패키지(wheelhouse), Java 라이브러리(JAR 번들), LLM 및 임베딩 모델 파일, 오프라인 환경에서 설치 및 배포를 수행합니다. 외부 네트워크 접근 없이 모든 구성 요소가 설치 및 실행 가능하도록 패키징 전략을 수립합니다.

### 8.2. 설정

● 8.2.1. **`config.yaml`**: 모델 엔드포인트, 임베딩 모델, 경로, 임계치 설정

### 8.3. 증분 처리

● 8.3.1. **변경분만 재분석 가능하도록 개발**

### 8.4. 로그 및 모니터링

● 8.4.1. **질의 커버리지, 모델 사용 비율(7B/32B), 평균 지연, 실패율 로깅**
● 8.4.2. **모니터링 시스템**: Prometheus와 Grafana를 통합하여 시스템 성능 지표, LLM 사용량, API 응답 시간 등을 시각화하고 모니터링합니다.

---

## 9. 보안 및 컴플라이언스

● 9.1. **원문 코드/SQL 미저장**(경로/라인Range/해시만)
● 9.2. **내부망 전용**, 외부 통신 차단
● 9.3. **쿼리/응답 로깅 시 민감 정보 제거**(경로/라인Range만 기록)

---

## 10. 테스트 및 수용 기준 (샘플)

- 영향평가 재현율 ≥ 0.9, 정확도 ≥ 0.75
- SQL 조인/필터 식별 일치율 ≥ 0.85
- 100k LOC 분석 ≤ 30분
- API 응답 평균 2s(7B), 복잡 쿼리 ≤ 10s(32B)

● 10.1. **정확도/재현율**: 샘플 200개 영향평가 케이스에서 **재현율 ≥ 0.9**, 정확도 ≥ 0.75
● 10.2. **조인/필수 필터**: 랜덤 100 SQL에서 수동 라벨과 일치율 ≥ 0.85
● 10.3. **성능**: 100k LOC 프로젝트 전체 분석 ≤ 30분(서버 스펙 기준, LLM 보강 제외)
● 10.4. **API**: 평균 응답 2s(7B), 복잡 쿼리 32B 폴백 ≤ 10s(캐시 적중 시 5s 이하)

---

## 11. 리스크 및 대응

● 11.1. **동적 SQL 다양성** → 최대 포함(superset) 전략 + 보수적 확장

● 11.2. **LLM 응답 일관성** → 근거 제시 강제, 스스로 검증 프롬프트, 32B 폴백

---

## 12. 부록

### 12.1. 오케스트레이터 의사코드

```python
def answer(question, project, recall_priority=True):
    intent = classify(question)
    plan = make_plan(intent, question)
    seeds = structured_search(project, plan.filters)
    hops = expand_call_graph(seeds, max_hops=plan.hops, recall_first=True)
    docs = vector_search(project, question, seeds+hops, k=plan.k)
    evidence = rank_and_merge(docs, seeds, hops)
    model = choose_model(evidence, base="qwen2.5-7b", fallback="qwen2.5-32b")
    draft = llm_generate(model, question, evidence, force_citations=True)
    if recall_priority and is_low_recall(draft, evidence):
        plan = widen(plan); return answer(question, project, recall_priority)
    return finalize(draft, evidence)
```

### 12.2. 프롬프트 스케치 (ko/en)

● 12.2.1. **지시**: “다음 근거만으로 답하되, 누락을 줄이기 위해 관련 항목을 **포괄**하라. 각 항목에 경로/라인Range/CONFIDENCE를 병기하라.”
● 12.2.2. **안전장치**: “원문 코드/SQL을 추정해 재현하지 마라. 제공된 요약/구조만 사용하라.”

### 12.3. 품질 및 유지보수 가이드

● 12.3.1. **해시 기반 변경 감지**와 ‘국소’ 그래프 재계산
● 12.3.2. **LLM 보강은 큐 기반 비동기**(시간제한/예산제한 설정)