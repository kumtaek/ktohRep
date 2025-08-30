개발내역 01 — 로컬 Ollama / 운영 vLLM 클라이언트 및 CLI 추가
===========================================================

목표
----
- 로컬(Windows)에서 Ollama(`gemma3:1b`)를 호출하고, 운영에서는 vLLM(OpenAI 호환, `Qwen2.5`)을 호출할 수 있는 통합 파이썬 클라이언트를 제공.
- 간단한 CLI를 제공하여 모델 호출을 빠르게 테스트하고, Windows 콘솔에서 UTF-8 출력이 깨지지 않도록 처리.

주요 변경 사항
--------------
- 의존성 업데이트 (`requirements.txt`)
  - `requests>=2.31.0` 추가
  - `openai>=1.35.0` 추가 (OpenAI 호환 vLLM 엔드포인트 사용)

- LLM 클라이언트 모듈
  - `phase1/src/llm/client.py`
    - `OllamaClient`: `http://localhost:11434/api/chat` 호출, `stream/temperature/max_tokens/stop` 지원
    - `VLLMClient`: OpenAI SDK로 `base_url` 지정하여 vLLM(OpenAI 호환) 호출, 스트리밍 지원
    - `get_client(provider)`, `simple_chat(prompt, ...)` 제공
  - `phase1/src/llm/__init__.py`: 공개 API 내보내기

- CLI
  - `phase1/src/llm_cli.py`
    - 프롬프트/시스템 메시지/스트리밍/파라미터 지원
    - Windows 콘솔 UTF-8 출력 보정(`sys.stdout.reconfigure`)
    - 사용 예: `python -m phase1.src.llm_cli "안녕" -s "한국어로 간단히" --stream`

- 문서
  - `docs/LLM_SETUP.md`: 환경변수, 로컬/운영 설정, 사용 예시 수록

환경 변수
--------
- 공통: `LLM_PROVIDER=ollama|vllm|openai`(기본 `ollama`)
- 로컬 Ollama: `OLLAMA_HOST`(기본 `http://localhost:11434`), `OLLAMA_MODEL`(기본 `gemma3:1b`)
- 운영 vLLM: `VLLM_BASE_URL`, `VLLM_API_KEY`(또는 `EMPTY`), `VLLM_MODEL`(예: `Qwen2.5`)

검증 내역(로컬)
--------------
- Ollama 실행 상태에서 `gemma3:1b`로 비스트림/스트림 호출 확인
- 이모지 포함 응답 및 한국어 출력 시 Windows cp949 문제를 UTF-8 재설정으로 해결

추가 메모
--------
- 클라이언트는 OpenAI 호환 인터페이스에 의존하므로 운영 vLLM 엔드포인트는 `/v1` 경로와 Chat Completions API를 지원해야 함
- 차후 파이프라인 연동을 고려하여 함수형 API(`simple_chat`)를 제공함

