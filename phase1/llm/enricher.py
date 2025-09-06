from typing import Optional, Dict, Any
import os

from llm.client import get_client


def generate_text(system: str, user: str, *, provider: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 256, dry_run: bool = False) -> str:
    if dry_run:
        # Minimal deterministic stub
        return "요약/설명(드라이런): 입력 컨텍스트 기반 자동 생성"
    client = get_client(provider)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    text = client.chat(messages, stream=False, temperature=temperature, max_tokens=max_tokens)
    return text if isinstance(text, str) else str(text)

