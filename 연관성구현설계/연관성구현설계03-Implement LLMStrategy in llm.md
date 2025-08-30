Implement LLMStrategy in llm.py
8월 30일
kumtaek/ktohRep
master
+103
-0

아카이브에 보관

공유하기

PR 만들기


1. `phase1/relatedness/strategies/llm.py`에 위와 같은 `LLMStrategy` 구현
2. `._pick_uncertain_pairs()`에서 규칙 기반 점수가 낮은 노드 쌍만 선택하도록 작성
3. 캐시 파일을 활용해 동일한 노드 쌍의 LLM 요청을 재사용
복사
Summary
Added a new LLMStrategy that queries an LLM for node pairs only when rule-based scores are uncertain, storing results to disk for reuse across runs

Implemented _pick_uncertain_pairs to sort and select only low-scoring pairs for LLM evaluation

Added JSON cache helpers to persist and reload previous LLM scores, avoiding duplicate requests

Testing
✅ pytest


파일 (3)개

phase1/relatedness/__init__.py
신규

phase1/relatedness/strategies/__init__.py
신규

phase1/relatedness/strategies/llm.py
신규


phase1/relatedness/__init__.py
신규

내용 없음
phase1/relatedness/strategies/__init__.py
신규

내용 없음
phase1/relatedness/strategies/llm.py
신규
+103
-0

import json
import os
import re
from typing import Dict, Iterable, List, Tuple

from phase1.llm.client import simple_chat

Pair = Tuple[str, str]


class LLMStrategy:
    """Determine relatedness for uncertain node pairs using an LLM.

    The strategy receives rule-based scores for node pairs and consults an LLM
    only for those with low scores. Responses are cached on disk so identical
    pairs are not re-queried.
    """

    def __init__(
        self,
        config: Dict,
        *,
        cache_path: str = ".llm_relatedness_cache.json",
        threshold: float = 0.4,
        max_pairs: int = 20,
    ) -> None:
        self.config = config
        self.cache_path = cache_path
        self.threshold = threshold
        self.max_pairs = max_pairs
        self._cache = self._load_cache()

    # ------------------------------------------------------------------
    # Public API
    def score_pairs(
        self,
        descriptions: Dict[Pair, Tuple[str, str]],
        rule_scores: Dict[Pair, float],
    ) -> Dict[Pair, float]:
        """Return LLM scores for pairs with low rule-based scores.

        ``descriptions`` should map ``(node_a, node_b)`` to two textual
        descriptions (e.g., code snippets or docstrings) that provide context
        to the LLM. ``rule_scores`` contains the preliminary score from
        rule-based strategies. Only low-scoring pairs are sent to the LLM.
        """

        results: Dict[Pair, float] = {}
        for pair in self._pick_uncertain_pairs(rule_scores):
            key = self._pair_key(*pair)
            if key in self._cache:
                results[pair] = self._cache[key]
                continue

            desc_a, desc_b = descriptions.get(pair, ("", ""))
            prompt = self._build_prompt(desc_a, desc_b)
            response = simple_chat(prompt, self.config)
            score = self._parse_score(response)

            self._cache[key] = score
            results[pair] = score

        if results:
            self._save_cache()
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    def _pick_uncertain_pairs(self, rule_scores: Dict[Pair, float]) -> Iterable[Pair]:
        """Select node pairs whose rule-based score is below the threshold."""
        sorted_pairs: List[Pair] = [p for p, s in sorted(rule_scores.items(), key=lambda x: x[1]) if s < self.threshold]
        return sorted_pairs[: self.max_pairs]

    def _build_prompt(self, desc_a: str, desc_b: str) -> str:
        return (
            "Two code elements are provided. Rate how related they are on a scale "
            "from 0 to 1. Respond with only a floating point number.\n\n"
            f"A: {desc_a}\n"
            f"B: {desc_b}"
        )

    def _parse_score(self, text: str) -> float:
        match = re.search(r"\d*\.\d+|1", text)
        try:
            return float(match.group()) if match else 0.0
        except Exception:
            return 0.0

    def _pair_key(self, a: str, b: str) -> str:
        return "::".join(sorted((a, b)))

    def _load_cache(self) -> Dict[str, float]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)