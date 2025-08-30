import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .client import get_client
from . import prompt_templates as T
from utils.confidence_calculator import ConfidenceCalculator
from models.database import EnrichmentLog


@dataclass
class AssistConfig:
    enabled: bool = True
    provider: str = "auto"  # auto|ollama|vllm|openai
    low_conf_threshold: float = 0.6
    max_calls_per_run: int = 50
    file_max_lines: int = 1200
    temperature: float = 0.0
    max_tokens: int = 512
    strict_json: bool = True
    cache: bool = True
    cache_dir: str = "./output/llm_cache"
    log_prompt: bool = False
    dry_run: bool = False
    fallback_to_ollama: bool = True
    # Provider details (optional overrides)
    vllm_base_url: Optional[str] = None
    vllm_api_key: Optional[str] = None
    vllm_model: Optional[str] = None
    ollama_host: Optional[str] = None
    ollama_model: Optional[str] = None


class LlmAssist:
    def __init__(self, config: Dict[str, Any], db_manager, logger, confidence_calculator: ConfidenceCalculator):
        self.logger = logger
        self.db_manager = db_manager
        self.confidence_calculator = confidence_calculator

        llm_cfg = (config or {}).get("llm_assist", {})
        self.cfg = AssistConfig(
            enabled=llm_cfg.get("enabled", True),
            provider=llm_cfg.get("provider", "auto"),
            low_conf_threshold=llm_cfg.get("low_conf_threshold", 0.6),
            max_calls_per_run=llm_cfg.get("max_calls_per_run", 50),
            file_max_lines=llm_cfg.get("file_max_lines", 1200),
            temperature=llm_cfg.get("temperature", 0.0),
            max_tokens=llm_cfg.get("max_tokens", 512),
            strict_json=llm_cfg.get("strict_json", True),
            cache=llm_cfg.get("cache", True),
            cache_dir=llm_cfg.get("cache_dir", "./output/llm_cache"),
            log_prompt=llm_cfg.get("log_prompt", False),
            dry_run=llm_cfg.get("dry_run", False),
            fallback_to_ollama=llm_cfg.get("fallback_to_ollama", True),
            vllm_base_url=llm_cfg.get("vllm_base_url"),
            vllm_api_key=llm_cfg.get("vllm_api_key"),
            vllm_model=llm_cfg.get("vllm_model"),
            ollama_host=llm_cfg.get("ollama_host"),
            ollama_model=llm_cfg.get("ollama_model"),
        )
        Path(self.cfg.cache_dir).mkdir(parents=True, exist_ok=True)
        self.calls_made = 0
        # 환경 변수 브리징: config 값이 존재하면 env로 주입하여 client가 참조할 수 있게 함
        self.calls_made = 0

    def should_assist(self, confidence: float) -> bool:
        return self.cfg.enabled and (confidence < self.cfg.low_conf_threshold) and (self.calls_made < self.cfg.max_calls_per_run)

    def assist_java(self, file_id: int, file_path: str, original_confidence: float) -> Optional[Dict[str, Any]]:
        if not self.should_assist(original_confidence):
            return None
        snippet = self._read_snippet(file_path)
        prompt_id, user = T.java_user_prompt(snippet)
        system = T.java_system_prompt()
        result_json, raw_text = self._call_or_cache(file_path, prompt_id, system, user)
        enrichment_result = self._evaluate_enrichment(result_json)
        final_conf, update_info = self.confidence_calculator.update_confidence_with_enrichment(original_confidence, enrichment_result)
        self._log_enrichment(file_id, original_confidence, final_conf, prompt_id, {
            "provider": self.cfg.provider,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
            "strict_json": self.cfg.strict_json,
            "dry_run": self.cfg.dry_run,
        })
        self.logger.info(f"LLM assist(java) applied: pre={original_confidence:.3f} -> post={final_conf:.3f}")
        return {"final_confidence": final_conf, "update": update_info, "json": result_json, "raw": raw_text}

    def assist_jsp(self, file_id: int, file_path: str, original_confidence: float) -> Optional[Dict[str, Any]]:
        if not self.should_assist(original_confidence):
            return None
        snippet = self._read_snippet(file_path)
        prompt_id, user = T.jsp_user_prompt(snippet)
        system = T.jsp_system_prompt()
        result_json, raw_text = self._call_or_cache(file_path, prompt_id, system, user)
        enrichment_result = self._evaluate_enrichment(result_json)
        final_conf, update_info = self.confidence_calculator.update_confidence_with_enrichment(original_confidence, enrichment_result)
        self._log_enrichment(file_id, original_confidence, final_conf, prompt_id, {
            "provider": self.cfg.provider,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
            "strict_json": self.cfg.strict_json,
            "dry_run": self.cfg.dry_run,
        })
        self.logger.info(f"LLM assist(jsp/xml) applied: pre={original_confidence:.3f} -> post={final_conf:.3f}")
        return {"final_confidence": final_conf, "update": update_info, "json": result_json, "raw": raw_text}

    # Internals

    def _read_snippet(self, file_path: str) -> str:
        try:
            text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        lines = text.splitlines()
        max_lines = self.cfg.file_max_lines
        if len(lines) <= max_lines:
            return text
        head = lines[: max_lines // 2]
        tail = lines[-max_lines // 2 :]
        return "\n".join(head + ["\n/* ...snip... */\n"] + tail)

    def _cache_key(self, file_path: str, prompt_id: str) -> str:
        try:
            data = Path(file_path).read_bytes()
        except Exception:
            data = b""
        sha = hashlib.sha256(data + prompt_id.encode("utf-8")).hexdigest()
        return sha

    def _call_or_cache(self, file_path: str, prompt_id: str, system: str, user: str) -> Tuple[Dict[str, Any], str]:
        key = self._cache_key(file_path, prompt_id)
        cache_path = Path(self.cfg.cache_dir) / f"{key}.json"
        raw_path = Path(self.cfg.cache_dir) / f"{key}.raw.txt"
        if self.cfg.cache and cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8", errors="ignore"))
                raw = raw_path.read_text(encoding="utf-8", errors="ignore") if raw_path.exists() else json.dumps(data, ensure_ascii=False)
                return data, raw
            except Exception:
                pass
        if self.cfg.dry_run:
            # Minimal plausible JSON for both schemas
            if "java" in prompt_id:
                data = {"classes": [{"name": "Sample", "methods": [{"name": "run"}]}]}
            else:
                data = {"sql_units": [{"stmt_kind": "select", "tables": ["DUAL"], "joins": [], "filters": []}]}
            raw = json.dumps(data, ensure_ascii=False)
        else:
            provider_setting = self.cfg.provider
            provider = None if provider_setting == "auto" else provider_setting
            messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
            data = {}
            raw = ""
            try:
                client = get_client(provider)
                raw_resp = client.chat(messages, stream=False, temperature=self.cfg.temperature, max_tokens=self.cfg.max_tokens)
                text = raw_resp.strip() if isinstance(raw_resp, str) else str(raw_resp)
                data = self._coerce_json(text)
                raw = text
            except Exception as e:
                # vLLM이 폐쇄망 등으로 접근 불가 시 Ollama로 폴백
                if self.cfg.fallback_to_ollama and provider in ("vllm", "openai"):
                    try:
                        self.logger.info(f"LLM primary provider failed ({provider}); falling back to ollama: {e}")
                    except Exception:
                        pass
                    client2 = get_client("ollama")
                    raw_resp2 = client2.chat(messages, stream=False, temperature=self.cfg.temperature, max_tokens=self.cfg.max_tokens)
                    text2 = raw_resp2.strip() if isinstance(raw_resp2, str) else str(raw_resp2)
                    data = self._coerce_json(text2)
                    raw = text2
                else:
                    raise
        try:
            cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            raw_path.write_text(raw, encoding="utf-8")
        except Exception:
            pass
        return data, raw

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        # Strict: attempt exact JSON first
        try:
            return json.loads(text)
        except Exception:
            pass
        # Heuristic: extract first {...} block
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
        except Exception:
            pass
        # Fallback empty
        return {}

    def _evaluate_enrichment(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        # Simple heuristic scoring for confidence update inputs
        size_hint = 0
        if "classes" in parsed and isinstance(parsed["classes"], list):
            size_hint += min(1.0, len(parsed["classes"]) * 0.2)
            for c in parsed["classes"]:
                if isinstance(c, dict) and c.get("methods"):
                    size_hint += min(1.0, len(c.get("methods", [])) * 0.1)
        if "sql_units" in parsed and isinstance(parsed["sql_units"], list):
            size_hint += min(1.0, len(parsed["sql_units"]) * 0.3)
        # Bound into [0,1]
        quality = max(0.0, min(1.0, 0.4 + size_hint * 0.3))
        model_quality = self.cfg.model_quality
        return {
            "confidence": quality,
            "model_quality": model_quality,
            "evidence_strength": 0.6 if parsed else 0.4,
        }

    def _log_enrichment(self, file_id: int, pre: float, post: float, prompt_id: str, params: Dict[str, Any]):
        try:
            session = self.db_manager.get_session()
            with session.begin():
                row = EnrichmentLog(
                    target_type="file",
                    target_id=file_id,
                    pre_conf=pre,
                    post_conf=post,
                    model=self.cfg.ollama_model or self.cfg.vllm_model or "unknown",
                    prompt_id=prompt_id,
                    params=json.dumps(params, ensure_ascii=False),
                )
                session.add(row)
        except Exception as e:
            self.logger.error(f"Failed to log enrichment: {e}")
