Implement LLM strategy methods
8월 30일
kumtaek/ktohRep
master
+145
-0

아카이브에 보관

공유하기

PR 만들기


1. `phase1/relatedness/strategies/llm.py` 작성
2. `_pick_uncertain_pairs`, `_score_pair` 메서드 구현
3. 캐시(`cache/relatedness.json`) 활용
복사
Summary
Added a new LLM-based strategy that initializes and persists relatedness scores using a JSON cache file to avoid redundant calls

Implemented _pick_uncertain_pairs to return unscored or low-scoring pairs for further evaluation while respecting cache contents and limits

Implemented _score_pair to query the configured LLM, parse a numeric score, and store results in the cache for reuse

Testing
✅ python -m py_compile phase1/relatedness/strategies/llm.py

✅ pytest -q


파일 (4)개

cache/relatedness.json
신규

phase1/relatedness/__init__.py
신규

phase1/relatedness/strategies/__init__.py
신규

phase1/relatedness/strategies/llm.py
신규


cache/relatedness.json
신규
+1
-0

{}
phase1/relatedness/__init__.py
신규

내용 없음
phase1/relatedness/strategies/__init__.py
신규

내용 없음
phase1/relatedness/strategies/llm.py
신규
+144
-0

"""LLM-based relatedness scoring strategy.

This module provides a simple semantic relatedness strategy that queries
an LLM to assign a score between 0 and 1 for a pair of entities. Results
are cached to avoid redundant LLM calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from phase1.llm.client import simple_chat


class LLMStrategy:
    """Semantic relatedness scorer using an LLM.

    Parameters
    ----------
    config:
        Global configuration dictionary containing an ``llm_assist`` section
        compatible with :func:`phase1.llm.client.simple_chat`.
    cache_path:
        Optional path to the JSON cache file. If omitted, ``cache/relatedness.json``
        under the project root is used.
    """

    def __init__(self, config: Dict, cache_path: Path | None = None) -> None:
        self.config = config
        root = Path(__file__).resolve().parents[3]
        self.cache_path = cache_path or root / "cache" / "relatedness.json"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, float] = {}
        if self.cache_path.exists():
            try:
                self._cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self._cache = {}

    # ------------------------------------------------------------------
    def _cache_key(self, node1: str, node2: str) -> str:
        """Return a stable cache key for a pair of nodes."""
        return "||".join(sorted([node1, node2]))

    def _save_cache(self) -> None:
        self.cache_path.write_text(
            json.dumps(self._cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    def _pick_uncertain_pairs(
        self,
        scores: Dict[Tuple[str, str], Tuple[float, str]],
        *,
        threshold: float = 0.6,
        limit: int = 20,
    ) -> List[Tuple[str, str]]:
        """Select pairs whose score is below ``threshold``.

        Parameters
        ----------
        scores:
            Mapping of ``(node1, node2)`` to ``(score, reason)``.
        threshold:
            Minimum score regarded as "certain". Pairs with a score below this
            value are considered uncertain and may be evaluated by the LLM.
        limit:
            Maximum number of pairs to return.
        """

        selected: List[Tuple[str, str]] = []
        for (n1, n2), (score, _reason) in scores.items():
            if score >= threshold:
                continue
            key = self._cache_key(n1, n2)
            if key in self._cache:
                continue
            selected.append((n1, n2))
            if len(selected) >= limit:
                break
        return selected

    # ------------------------------------------------------------------
    def _score_pair(self, node1_desc: str, node2_desc: str) -> float:
        """Query the LLM for a semantic relatedness score.

        The result is cached in ``cache/relatedness.json``.
        """

        key = self._cache_key(node1_desc, node2_desc)
        if key in self._cache:
            return self._cache[key]

        system_prompt = (
            "You are an assistant that rates how related two software entities are. "
            "Respond with a single number between 0 and 1 inclusive."
        )
        user_prompt = (
            f"Entity A: {node1_desc}\n"
            f"Entity B: {node2_desc}\n"
            "Relatedness score:"  # instruct to output number only
        )
        try:
            response = simple_chat(
                user_prompt,
                self.config.get("llm_assist", {}),
                system=system_prompt,
                max_tokens=8,
            )
            score = float(str(response).strip())
        except Exception:
            # If anything goes wrong, default to 0.0
            score = 0.0

        self._cache[key] = score
        self._save_cache()
        return score

    # ------------------------------------------------------------------
    def score_pairs(
        self,
        pairs: Iterable[Tuple[str, str]],
        *,
        descriptions: Dict[str, str],
    ) -> Dict[Tuple[str, str], float]:
        """Public helper to score multiple pairs.

        Parameters
        ----------
        pairs:
            Iterable of node identifier pairs.
        descriptions:
            Mapping from node identifier to a human-readable description to send
            to the LLM.
        """
        results: Dict[Tuple[str, str], float] = {}
        for n1, n2 in pairs:
            desc1 = descriptions.get(n1, n1)
            desc2 = descriptions.get(n2, n2)
            results[(n1, n2)] = self._score_pair(desc1, desc2)
        return results