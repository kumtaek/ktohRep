import argparse
import sys
import os
from typing import Iterator

from dotenv import load_dotenv
import yaml

from .llm.client import get_client


def main(argv=None) -> int:
    load_dotenv()
    # Ensure UTF-8 output on Windows consoles
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Simple LLM CLI (Ollama or vLLM)")
    p.add_argument("prompt", help="User prompt text")
    p.add_argument("--system", "-s", default=None, help="Optional system prompt")
    p.add_argument("--provider", "-p", default=None, help="Provider: ollama|vllm|openai")
    p.add_argument("--stream", action="store_true", help="Stream output tokens")
    p.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    p.add_argument("--max-tokens", type=int, default=None, help="Max tokens to generate")

    args = p.parse_args(argv)

    # Load config.yaml
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cfg_path = os.path.join(here, '..', '..', 'config', 'config.yaml')
    cfg = {}
    if os.path.exists(cfg_path):
        raw = open(cfg_path, 'r', encoding='utf-8').read()
        expanded = os.path.expandvars(raw)
        cfg = yaml.safe_load(expanded) or {}
    llm_cfg = (cfg.get('llm_assist') or {})

    client = get_client(llm_cfg, args.provider)
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})

    res = client.chat(
        messages,
        stream=args.stream,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    if args.stream:
        assert isinstance(res, Iterator)
        for chunk in res:
            print(chunk, end="", flush=True)
        print()
    else:
        print(res)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
