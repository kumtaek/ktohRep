# 연관성 분석 최종 구현 상세 설명

## 1. 최종 목표

소스코드와 데이터베이스 내의 다양한 엔티티(파일, 클래스, 테이블 등) 간의 '연관성'을 정량적인 점수(score)로 계산하고, 이를 데이터베이스에 메타데이터로 구축한다. 이 데이터는 향후 시각화 리포트에서 연관된 엔티티들을 지능적으로 군집화하거나, 특정 엔티티와 관련된 항목을 조회하는 데 사용된다.

## 2. 핵심 아키텍처: 전략 패턴 (Strategy Pattern)

연관성 계산 로직의 유연성과 확장성을 위해 '전략 패턴'을 채택한다. 

- **`RelatednessCalculator` (Context)**: 연관성 계산의 전체 과정을 관리하는 주체. 내부에 여러 '전략' 객체들을 리스트로 유지한다.
- **`RelatednessStrategy` (Strategy)**: 연관성을 계산하는 단일 규칙(알고리즘)을 정의하는 인터페이스(프로토콜). `apply` 메소드를 가진다.
- **`DirectEdgeStrategy`, `DirectoryProximityStrategy` 등 (Concrete Strategies)**: 각기 다른 규칙(엣지 기반, 디렉토리 기반 등)에 따라 실제 연관성을 계산하는 구체적인 클래스.

**데이터 흐름:**
1. `RelatednessCalculator`가 실행되면, 자신이 가진 전략(`Strategy`) 리스트를 순회한다.
2. 각 `Strategy`는 자신의 알고리즘에 따라 연관성을 계산하고, `Calculator`가 제공하는 콜백 함수(`_update_score`)를 호출하여 결과를 전달한다.
3. `Calculator`는 모든 전략의 실행 결과를 취합하여 메모리에 임시 저장한다.
4. 모든 전략 실행이 끝나면, 최종적으로 집계된 연관성 점수들을 `Relatedness` 테이블에 한 번에 저장한다.

## 3. 단계별 구현 로직 상세

### 3.1. `RelatednessCalculator` 초기화 및 실행

`phase1/scripts/calculate_relatedness.py`에 위치하며, 다음과 같이 동작한다.

```python
# RelatednessCalculator 클래스 일부

class RelatednessCalculator:
    def __init__(self, project_name: str, config: dict):
        # 1. DB 세션 및 프로젝트 ID 초기화
        self.dbm = DatabaseManager(config)
        self.session = self.dbm.get_session()
        self.project_id = self._get_project_id()

        # 2. 최종 점수를 메모리에 임시 저장할 딕셔너리
        #    Key: (node1_key, node2_key), Value: (score, reason)
        self.relatedness_scores = defaultdict(lambda: (0.0, 'none'))

        # 3. 사용할 전략 클래스들을 인스턴스화하여 리스트로 관리
        self.strategies = [
            DirectEdgeStrategy(),
            DirectoryProximityStrategy(),
            NamingConventionStrategy(),
            # LLMStrategy() # 향후 추가
        ]

    def run(self):
        # 4. 등록된 모든 전략을 순차적으로 실행
        for strategy in self.strategies:
            print(f"  - Applying {strategy.name} strategy...")
            # 각 전략에 DB 세션, 프로젝트 ID, 점수 업데이트 콜백 함수를 전달
            strategy.apply(self.session, self.project_id, self._update_score)
        
        # 5. 모든 계산이 끝난 후 최종 결과를 DB에 저장
        self.store_scores_to_db()
```

### 3.2. 점수 업데이트 및 통합 로직 (`_update_score`)

모든 전략은 이 콜백 함수를 통해 계산 결과를 중앙(`relatedness_scores`)으로 전달한다. 이 과정에서 점수 통합 정책이 적용된다.

- **로직**: 
  1. 두 노드의 키(`node1_key`, `node2_key`)를 받으면, 순서에 상관없이 동일한 키를 생성하기 위해 정렬한다. (e.g., `('class:1', 'file:10')`)
  2. 이 키로 `relatedness_scores` 딕셔너리에서 현재 저장된 점수를 조회한다.
  3. **(핵심 정책)** 새로 계산된 점수가 기존 점수보다 높을 경우에만 값을 덮어쓴다. 이를 통해 여러 연관성 근거 중 가장 강한 연결고리(가장 높은 점수)가 최종 점수로 채택된다.

```python
# RelatednessCalculator._update_score 메소드
def _update_score(self, node1_key: str, node2_key: str, score: float, reason: str):
    if not node1_key or not node2_key or node1_key == node2_key:
        return

    # 1. 순서에 무관한 고유 키 생성
    key = tuple(sorted((node1_key, node2_key)))
    
    # 2. 현재 점수 조회
    current_score, _ = self.relatedness_scores[key]

    # 3. 더 높은 점수일 경우에만 업데이트
    if score > current_score:
        self.relatedness_scores[key] = (score, reason)
```

### 3.3. 전략별 계산 로직

#### 1) `DirectEdgeStrategy` (직접 연결 기반)
- **목표**: DB의 `Edge` 테이블에 이미 존재하는 명시적인 관계(호출, 상속, FK 등)를 연관성 점수로 변환한다.
- **로직**: 
  1. `Edge` 테이블에서 현재 프로젝트의 모든 엣지를 조회한다. (`O(E)`) 
  2. `edge_kind`(e.g., 'fk', 'call')에 따라 미리 정의된 점수(`score_map`)를 할당한다.
  3. 각 엣지의 `source`와 `target`에 대해 `_update_score`를 호출한다.

#### 2) `DirectoryProximityStrategy` (디렉토리 근접성 기반)
- **목표**: 같은 디렉토리 내에 위치하는 파일들은 서로 연관성이 높다고 간주한다.
- **로직**: 
  1. `File` 테이블에서 모든 파일 정보를 가져와 `os.path.dirname`으로 디렉토리 경로를 키로 하는 딕셔너리에 파일들을 그룹화한다. (`O(F)`) 
  2. 각 디렉토리 그룹을 순회하며, 그룹 내 파일 수가 2개 이상인 경우에만 `itertools.combinations`로 모든 파일 쌍을 생성한다.
  3. 각 파일 쌍에 대해 `_update_score`를 고정된 점수(e.g., 0.6)와 함께 호출한다.

#### 3) `NamingConventionStrategy` (이름 규칙 기반)
- **목표**: `User`, `UserService`, `UserController`처럼 특정 접미사를 공유하는 엔티티들의 연관성을 계산한다.
- **로직**: 
  1. `File`, `Class` 등 이름 분석이 필요한 엔티티들을 DB에서 조회한다.
  2. `Service`, `Controller`, `Repository` 등 공통 접미사 목록을 정의한다.
  3. 각 엔티티 이름에서 접미사를 제거하여 '베이스 이름'(e.g., 'User')을 추출하고, 이 베이스 이름을 키로 엔티티들을 그룹화한다.
  4. 각 베이스 이름 그룹을 순회하며, 그룹 내 엔티티가 2개 이상일 경우 모든 쌍을 생성한다.
  5. 각 쌍에 대해 `_update_score`를 높은 점수(e.g., 0.8)와 함께 호출한다.

### 3.4. 최종 결과 데이터베이스 저장 (`store_scores_to_db`)
- **목표**: 메모리의 `relatedness_scores`에 최종 집계된 점수들을 `Relatedness` 테이블에 효율적으로 저장한다.
- **로직**: 
  1. (중요) 기존에 계산된 현재 프로젝트의 `Relatedness` 데이터를 모두 삭제한다. 이는 계산을 다시 실행할 때마다 최신 상태를 유지하기 위함이다.
  2. `relatedness_scores` 딕셔너리를 순회하며 각 항목을 `Relatedness` 테이블 스키마에 맞는 딕셔너리 형태로 변환한 리스트를 생성한다.
  3. SQLAlchemy의 `session.bulk_insert_mappings()`를 사용하여 변환된 리스트를 단 한 번의 DB 트랜잭션으로 삽입(Bulk Insert)한다. 이는 수만 개의 관계를 하나씩 `INSERT`하는 것보다 월등히 빠르다.
  4. 트랜잭션을 커밋한다.

## 4. 결론

이러한 단계별 구현 방식은 **효율성, 확장성, 유지보수성**을 모두 고려한 최적의 접근법이다. 각 로직이 명확히 분리되어 있어 테스트가 용이하며, 향후 LLM을 이용한 의미 분석 등 더 복잡한 전략을 추가하더라도 기존 코드에 미치는 영향을 최소화할 수 있다.