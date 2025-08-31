import os
import json
from typing import Iterator, List, Dict, Optional, Union, Any
from pathlib import Path

import yaml
import requests

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional import
    OpenAI = None  # type: ignore


Message = Dict[str, str]


class OllamaClient:
    def __init__(
        self,
        config: Dict[str, Any],
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.config = config
        self.base_url = base_url or self.config.get("ollama_host", "http://localhost:11434").rstrip("/")
        self.model = model or self.config.get("ollama_model", "gemma3:1b")

    def is_model_available(self) -> bool:
        try:
            resp = requests.post(f"{self.base_url}/api/show", json={"name": self.model}, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def chat(
        self,
        messages: List[Message],
        *,
        stream: bool = False,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        timeout: int = 60,
    ) -> Union[str, Iterator[str]]:
        payload: Dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {},
        }

        opts = payload["options"]  # type: ignore[assignment]
        if isinstance(opts, dict):
            if temperature is not None:
                opts["temperature"] = temperature
            if max_tokens is not None:
                # Ollama uses num_predict instead of max_tokens
                opts["num_predict"] = max_tokens
            if stop is not None:
                opts["stop"] = stop

        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json=payload, stream=stream, timeout=timeout)
        resp.raise_for_status()

        if stream:
            def gen() -> Iterator[str]:
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                    msg = data.get("message") or {}
                    if isinstance(msg, dict):
                        piece = msg.get("content")
                        if isinstance(piece, str) and piece:
                            yield piece
                    if data.get("done"):
                        break
            return gen()
        else:
            data = resp.json()
            msg = data.get("message") or {}
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
            # Fallback for /api/generate shape
            if isinstance(data.get("response"), str):
                return data["response"]
            return ""


class VLLMClient:
    def __init__(
        self,
        config: Dict[str, Any],
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        if OpenAI is None:
            raise RuntimeError(
                "openai package not available. Add `openai>=1.35.0` to requirements and install."
            )
        self.config = config
        self.base_url = base_url or self.config.get("vllm_base_url", "http://localhost:8000/v1")
        self.api_key = api_key or self.config.get("vllm_api_key", "EMPTY")
        self.model = model or self.config.get("vllm_model", "Qwen2.5")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat(
        self,
        messages: List[Message],
        *,
        stream: bool = False,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
    ) -> Union[str, Iterator[str]]:
        if stream:
            def gen() -> Iterator[str]:
                with self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop=stop,
                    stream=True,
                ) as s:
                    for chunk in s:
                        choice = chunk.choices[0]
                        delta = getattr(choice, "delta", None)
                        if delta is None:
                            continue
                        content = getattr(delta, "content", None)
                        if content:
                            yield content
            return gen()
        else:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            return res.choices[0].message.content or ""


def _load_llm_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if config is not None:
        return config
    try:
        root = Path(__file__).resolve().parents[2]
        cfg_path = root / "config" / "config.yaml"
        if cfg_path.exists():
            raw = cfg_path.read_text(encoding="utf-8")
            expanded = os.path.expandvars(raw)
            full = yaml.safe_load(expanded) or {}
            return full.get("llm", {})
    except Exception:
        pass
    return {}


def get_client(config: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
    if isinstance(config, str) and provider is None:
        provider = config
        config = None
    print(f"DEBUG: get_client called with provider='{provider}'")
    cfg = _load_llm_config(config)
    provider = (provider or cfg.get("provider", "ollama")).strip().lower()
    if provider in ("ollama", "local"):
        base_url = cfg.get("ollama_host", "http://localhost:11434").rstrip("/")
        base_model = cfg.get("base_model") or cfg.get("ollama_model", "gemma3:1b")
        fallback_model = cfg.get("fallback_model")
        enabled = cfg.get("enabled", True)
        client = OllamaClient({"ollama_host": base_url, "ollama_model": base_model})
        print(f"DEBUG: Checking if base model '{base_model}' is available at {base_url}...")
        
        # If LLM is disabled, return client without availability check
        if not enabled:
            print(f"DEBUG: LLM is disabled by config. Returning client without availability check.")
            return client
        
        # LLM is enabled, so we must validate models are available
        base_available = client.is_model_available()
        if base_available:
            print(f"DEBUG: Base model '{base_model}' is available.")
            return client
        
        print(f"DEBUG: Base model '{base_model}' is NOT available.")
        
        # Check fallback model if different from base model
        if fallback_model and fallback_model != base_model:
            fb_client = OllamaClient({"ollama_host": base_url, "ollama_model": fallback_model})
            print(f"DEBUG: Checking if fallback model '{fallback_model}' is available at {base_url}...")
            if fb_client.is_model_available():
                print(f"DEBUG: Fallback model '{fallback_model}' is available.")
                return fb_client
            print(f"DEBUG: Fallback model '{fallback_model}' is NOT available.")
        
        # Both base and fallback models are unavailable and LLM is enabled
        error_message = f"LLM is enabled but no models are available. "
        if fallback_model and fallback_model != base_model:
            error_message += f"Tried models: {base_model}, {fallback_model}"
        else:
            error_message += f"Tried model: {base_model}"
        
        error_message += f"\nPlease ensure Ollama is running at {base_url} and the models are available, or set llm.enabled: false in config.yaml"
        
        raise RuntimeError(error_message)
    if provider in ("vllm", "openai"):
        return VLLMClient(cfg)
    # Default to Ollama
    return OllamaClient(cfg)


def simple_chat(
    prompt: str,
    config: Optional[Dict[str, Any]] = None,
    *,
    system: Optional[str] = None,
    provider: Optional[str] = None,
    stream: bool = False,
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = None,
) -> Union[str, Iterator[str]]:
    messages: List[Message] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = get_client(config, provider)
    return client.chat(messages, stream=stream, temperature=temperature, max_tokens=max_tokens)

