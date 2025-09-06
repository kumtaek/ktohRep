import argparse
import sys
import os
from typing import Iterator

from dotenv import load_dotenv
import yaml

from llm.client import get_client


def main(argv=None) -> int:
    load_dotenv()
    # Windows 콘솔에서 UTF-8 출력을 보장합니다.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # 명령줄 인수를 파싱하기 위한 ArgumentParser를 설정합니다.
    p = argparse.ArgumentParser(description="Simple LLM CLI (Ollama or vLLM)")
    # 사용자 프롬프트 텍스트를 지정하는 인수를 추가합니다.
    p.add_argument("prompt", help="User prompt text")
    # 선택적 시스템 프롬프트를 지정하는 인수를 추가합니다.
    p.add_argument("--system", "-s", default=None, help="Optional system prompt")
    # LLM 제공자를 지정하는 인수를 추가합니다.
    p.add_argument("--provider", "-p", default=None, help="Provider: ollama|vllm|openai")
    # 출력 토큰을 스트리밍할지 여부를 지정하는 플래그 인수를 추가합니다.
    p.add_argument("--stream", action="store_true", help="Stream output tokens")
    # 샘플링 온도를 지정하는 인수를 추가합니다.
    p.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    # 생성할 최대 토큰 수를 지정하는 인수를 추가합니다.
    p.add_argument("--max-tokens", type=int, default=None, help="Max tokens to generate")

    args = p.parse_args(argv)

    # config.yaml 파일을 로드합니다.
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cfg_path = os.path.join(here, '..', '..', 'config', 'config.yaml')
    cfg = {}
    if os.path.exists(cfg_path):
        raw = open(cfg_path, 'r', encoding='utf-8').read()
        expanded = os.path.expandvars(raw)
        cfg = yaml.safe_load(expanded) or {}
    llm_cfg = (cfg.get('llm_assist') or {})

    # LLM 클라이언트를 가져옵니다.
    client = get_client(llm_cfg, args.provider)
    messages = []
    # 시스템 프롬프트가 있는 경우 메시지에 추가합니다.
    if args.system:
        messages.append({"role": "system", "content": args.system})
    # 사용자 프롬프트를 메시지에 추가합니다.
    messages.append({"role": "user", "content": args.prompt})

    # LLM 채팅을 호출합니다.
    res = client.chat(
        messages,
        stream=args.stream,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # 스트리밍 모드인 경우 청크를 출력하고, 그렇지 않은 경우 전체 응답을 출력합니다.
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
