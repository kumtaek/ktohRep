import os
import json
from typing import Iterator, List, Dict, Optional, Union, Any

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


def get_client(config: Dict[str, Any], provider: Optional[str] = None):
    provider = (provider or config.get("provider", "ollama")).strip().lower()
    if provider in ("ollama", "local"):
        return OllamaClient(config)
    if provider in ("vllm", "openai"):
        return VLLMClient(config)
    # Default to Ollama
    return OllamaClient(config)


def simple_chat(
    prompt: str,
    config: Dict[str, Any],
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

