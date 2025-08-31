개선 설계 개요
연관성구현방안1.md, 연관성구현방안2.md, 연관성구현설계.md, 연관성구현설계_v2.md를 검토한 결과, 규칙 기반 점수 산정과 fcose 등 강제지향 레이아웃 도입에 관한 기본 구상이 이미 정리되어 있습니다. 아래는 추가로 고려해볼 수 있는 개선 방향과 코드 예시입니다.

1. 전략(Strategy) 기반 플러그인 구조
새 전략을 쉽게 추가할 수 있도록 RelatednessStrategy 프로토콜을 두고, 계산기는 등록된 전략을 순차 실행합니다.

# phase1/relatedness/strategies/base.py
from typing import Protocol, Callable

class RelatednessStrategy(Protocol):
    def run(
        self,
        session,
        project_id: int,
        update_score: Callable[[str, str, float, str], None],
    ) -> None: ...
# phase1/scripts/calculate_relatedness.py
from relatedness.strategies import EdgeStrategy, DirStrategy, NamingStrategy, LLMStrategy

class RelatednessCalculator:
    def __init__(...):
        self.strategies = [
            EdgeStrategy(), DirStrategy(),
            NamingStrategy(), LLMStrategy(cache_path="cache/relatedness.json")
        ]

    def run(self):
        for s in self.strategies:
            s.run(self.session, self.project_id, self._update_score)
        self.store_scores_to_db()
제안된 작업
플러그인 기반 연관성 전략 구조 도입
작업 보기
2. 비동기 LLM·임베딩 분석 + 캐시
LLM 호출은 비용이 크므로 asyncio로 병렬 처리하고, 결과는 파일 캐시로 재사용합니다.

# phase1/relatedness/strategies/llm.py
import asyncio, json
from pathlib import Path
from .base import RelatednessStrategy

class LLMStrategy(RelatednessStrategy):
    def __init__(self, cache_path: str):
        self.cache_file = Path(cache_path)
        self.cache = json.loads(self.cache_file.read_text()) if self.cache_file.exists() else {}

    async def _score_pair(self, ctx1, ctx2) -> float:
        prompt = f"...{ctx1}...{ctx2}..."
        # response = await llm_client.ask_async(prompt)
        # return float(response)
        return 0.0  # placeholder

    def run(self, session, project_id, update_score):
        pairs = self._pick_uncertain_pairs(session, project_id)
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(asyncio.gather(*[
            self._score_pair(p.ctx1, p.ctx2) for p in pairs
        ]))
        for pair, score in zip(pairs, results):
            if score > 0.1:
                update_score(pair.key1, pair.key2, score, "llm_semantic")
        self.cache_file.write_text(json.dumps(self.cache))
제안된 작업
LLM 기반 연관성 분석 비동기·캐시 구현
작업 보기
3. 연관성 기반 클러스터링과 시각화 연동
Relatedness 테이블에서 그래프를 구성하여 Louvain 군집화 후, fcose 레이아웃으로 배치합니다.

# visualize/builders/cluster_graph.py
import networkx as nx

def build_clustered_graph(session, project_id):
    G = nx.Graph()
    rels = session.query(Relatedness).filter_by(project_id=project_id).all()
    for r in rels:
        G.add_edge((r.source_type, r.source_id),
                   (r.target_type, r.target_id),
                   weight=r.score)
    clusters = nx.algorithms.community.louvain_communities(G, weight='weight')
    return G, clusters
// visualize/templates/cyto_base.html
const layout = cy.layout({
  name: 'fcose',
  quality: 'proof',
  nodeRepulsion: node => 4500,
  idealEdgeLength: edge => 80 / edge.data('weight')
});
layout.run();
제안된 작업
연관성 기반 클러스터링 및 fcose 레이아웃 적용
작업 보기
4. 연관성 질의 API
Phase2에서 자연어 질의에 “관련된 엔티티 묶음”을 반환할 수 있도록 간단한 조회 API를 제공합니다.

# phase2/services/related_query.py
from phase1.models.relatedness import Relatedness

def get_related_entities(session, project_id, node_type, node_id, threshold=0.5):
    rels = session.query(Relatedness)\
        .filter(Relatedness.project_id == project_id)\
        .filter(((Relatedness.source_type == node_type) & (Relatedness.source_id == node_id)) |
                ((Relatedness.target_type == node_type) & (Relatedness.target_id == node_id)))\
        .filter(Relatedness.score >= threshold)\
        .all()
    return [{
        "entity": (r.target_type, r.target_id) if r.source_id == node_id else (r.source_type, r.source_id),
        "score": r.score,
        "reason": r.reason
    } for r in rels]
제안된 작업
관련 엔티티 조회 API 구현
작업 보기
이러한 확장을 통해 기존 설계를 기반으로 한 연관성 분석 파이프라인이 더 유연하고 성능 친화적인 구조로 발전하며, 시각화와 질의 응답 단계에서의 활용도도 높아집니다.

좀 더 구체적으로 상세 설계를 해줘.
복사
연관성구현방안.md – 상세 설계 초안
아래 내용은 읽기 전용 환경에서 작성한 제안서이며, 연관성구현방안.md로 복사해 저장하여 사용하실 수 있습니다.

1. 메타데이터 구조 확장
위치	변경 내용
phase1/models/meta.py (또는 동등 구조)	Relatedness 엔티티 추가
- project_id, source_type, source_id, target_type, target_id, score, reason
phase1/output/*.json	각 노드에 related_nodes, relation_score, cluster_id 필드 추가
DB 마이그레이션	relatedness 테이블 생성: 복합 PK(source*, target*), score(FLOAT), reason(TEXT)
정책: score는 0~1.0 범위로 정규화하며, 동일 방향·반대 방향 모두 저장(무향 그래프라도 탐색 편의를 위해).

2. 규칙 기반 연관성 추출 로직
2.1 Strategy 기반 설계
phase1/relatedness/strategies/
  ├── base.py            # RelatednessStrategy 프로토콜
  ├── edge.py            # 호출/참조 정보 이용
  ├── dir.py             # 디렉터리·패키지 기반
  ├── naming.py          # 네이밍 유사도 기반
  └── llm.py             # LLM 활용 (3.항)
2.2 점수 산정 예시
규칙	점수
직접 호출/테이블 참조/상속	+0.6
동일 디렉터리/패키지	+0.3
이름 유사도(Levenshtein 등)	+0.1
# phase1/relatedness/strategies/edge.py
class EdgeStrategy(RelatednessStrategy):
    def run(self, session, project_id, update_score):
        for edge in session.query(CallGraph).filter_by(project_id=project_id):
            update_score(("class", edge.src_id), ("class", edge.dst_id),
                         0.6, "direct_call")
3. LLM/비정형 분석
3.1 비동기 처리 + 캐싱
# phase1/relatedness/strategies/llm.py
class LLMStrategy(RelatednessStrategy):
    CACHE_PATH = Path("cache/relatedness.json")

    def run(self, session, project_id, update_score):
        pairs = self._pick_uncertain_pairs(session, project_id)
        loop = asyncio.get_event_loop()
        tasks = [self._score_pair(p) for p in pairs]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        for pair, (score, reason) in zip(pairs, results):
            update_score(pair.key1, pair.key2, score, f"llm:{reason}")
_pick_uncertain_pairs: 규칙 기반 score < 0.4인 쌍을 추출.

_score_pair 내부는 LLM or 임베딩 API 호출; 결과는 캐시에 저장 후 재사용.

장기적으로 OpenAI, HuggingFace 등 플러그블 구조 지원.

4. 연관성 기반 군집화 & 시각화
4.1 클러스터 빌더
# visualize/builders/cluster_graph.py
def build_clustered_graph(session, project_id):
    G = nx.Graph()
    rels = session.query(Relatedness).filter_by(project_id=project_id).all()
    for r in rels:
        G.add_edge((r.source_type, r.source_id),
                   (r.target_type, r.target_id),
                   weight=r.score)
    clusters = nx.algorithms.community.louvain_communities(G, weight="weight")
    return G, clusters
4.2 시각화 반영
각 노드에 data.cluster_id 주입 → visualize/schema.py 수정.

cyto_base.html

const layout = cy.layout({
  name: 'fcose',
  quality: 'default',
  nodeRepulsion: n => 4500,
  idealEdgeLength: e => 80 / e.data('weight')
});
layout.run();
ERD/HTML/Markdown builder(visualize/builders/*)에서 cluster_id 기반 색상·정렬 적용.

5. 연관성 질의 API
위치	기능
phase2/services/related_query.py	노드 ID, 타입, 임계값을 입력받아 관련 엔티티 목록 반환
phase2/routes/related.py (웹/CLI)	/api/related 혹은 CLI 명령어 phase2/query_related 제공
def get_related_entities(session, project_id, node_type, node_id, threshold=0.5):
    q = session.query(Relatedness).filter(Relatedness.project_id == project_id)
    q = q.filter(or_(
        (Relatedness.source_type == node_type) & (Relatedness.source_id == node_id),
        (Relatedness.target_type == node_type) & (Relatedness.target_id == node_id)
    ))
    rels = q.filter(Relatedness.score >= threshold).all()
    ...
6. 파이프라인 요약
Phase1: 소스·DB 메타 분석 → 규칙·LLM 전략으로 Relatedness 계산 → DB/JSON 저장

Phase2: 관련성 조회 API·자연어 질의 응답 시 Relatedness 활용

visualize: cluster_graph 빌드 → fcose 레이아웃, 클러스터 색상 → HTML/MD 보고서 개선

7. 테스트 및 튜닝
project/<name> 샘플에 대해 파이프라인 실행 후 결과 검증

노드 수가 많을 때 fcose 성능 확인, 필요 시 레이아웃 파라미터 조정

사용자 피드백으로 규칙 가중치, LLM 임계값, 클러스터링 알고리즘 변경

부록: 구현 Task-Stubs
플러그인 기반 연관성 전략 구조 도입

제안된 작업
Relatedness 전략 구조 도입
작업 보기
LLM 기반 연관성 분석 비동기·캐시 구현

제안된 작업
LLMStrategy 구현
작업 보기
연관성 기반 클러스터링 및 fcose 레이아웃 적용

제안된 작업
클러스터링 + fcose 적용
작업 보기
관련 엔티티 조회 API 구현

제안된 작업
get_related_entities API
작업 보기
이 설계를 바탕으로 구현을 진행하면, ERD를 포함한 모든 시각화 리포트에서 연관성 있는 객체들이 자연스럽게 묶여 배치되고, 규칙 기반 + LLM 분석을 통해 보다 정교한 연관성 탐색·질의응답이 가능해집니다.