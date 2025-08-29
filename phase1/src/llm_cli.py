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

    # Optional: bridge config/config.yaml llm settings into env
    try:
        here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        cfg_path = os.path.join(here, '..', '..', 'config', 'config.yaml')
        if os.path.exists(cfg_path):
            raw = open(cfg_path, 'r', encoding='utf-8').read()
            expanded = os.path.expandvars(raw)
            cfg = yaml.safe_load(expanded) or {}
            llm_cfg = (cfg.get('llm_assist') or {})
            if llm_cfg.get('ollama_host'):
                os.environ['OLLAMA_HOST'] = str(llm_cfg['ollama_host'])
            if llm_cfg.get('ollama_model'):
                os.environ['OLLAMA_MODEL'] = str(llm_cfg['ollama_model'])
            if llm_cfg.get('vllm_base_url'):
                os.environ['VLLM_BASE_URL'] = str(llm_cfg['vllm_base_url'])
            if llm_cfg.get('vllm_api_key'):
                os.environ['VLLM_API_KEY'] = str(llm_cfg['vllm_api_key'])
            if llm_cfg.get('vllm_model'):
                os.environ['VLLM_MODEL'] = str(llm_cfg['vllm_model'])
            # provider override
            if llm_cfg.get('provider'):
                os.environ['LLM_PROVIDER'] = str(llm_cfg['provider'])
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

    client = get_client(args.provider)
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
