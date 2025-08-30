LLM Local/Prod Setup
====================

Overview
--------
- Local dev runs against Ollama on Windows (e.g., `gemma3:1b`).
- Prod runs against vLLM exposing an OpenAI-compatible endpoint (e.g., Qwen2.5).

Dependencies
------------
- `requests>=2.31.0`
- `openai>=1.35.0`
- `python-dotenv>=0.19.0` (already included)

Environment Variables
---------------------
- `LLM_PROVIDER`: `ollama` (default) | `vllm` | `openai`
- `OLLAMA_HOST`: default `http://localhost:11434`
- `OLLAMA_MODEL`: default `gemma3:1b`
- `VLLM_BASE_URL`: e.g., `http://<vllm-host>:8000/v1`
- `VLLM_API_KEY`: API key or `EMPTY` if not enforced
- `VLLM_MODEL`: e.g., `Qwen2.5` or your deployed model id

Quick Start (Local Ollama)
--------------------------
1. Ensure Ollama is running and `gemma3:1b` is available.
2. Create a `.env` file:

   LLM_PROVIDER=ollama
   OLLAMA_MODEL=gemma3:1b
   OLLAMA_HOST=http://localhost:11434

3. Run the CLI:

   python -m phase1.src.llm_cli "안녕! 로컬에서 잘 되니?"

Prod (vLLM OpenAI-compatible)
-----------------------------
1. Set environment:

   LLM_PROVIDER=vllm
   VLLM_BASE_URL=http://<vllm-host>:8000/v1
   VLLM_API_KEY=EMPTY
   VLLM_MODEL=Qwen2.5

2. Run the CLI (same command). The client routes to vLLM.

 Offline/Closed-Network Tips
 ---------------------------
- If the vLLM endpoint is unreachable (closed network), the assist engine can fall back to local Ollama when `llm_assist.fallback_to_ollama=true` (default).
- For CI/offline tests, set `llm_assist.dry_run=true` to bypass any model calls while exercising the full flow and logging.

Programmatic Usage
------------------
from llm import simple_chat

text = simple_chat(
    "Summarize this in 3 bullets.",
    system="Be concise and accurate.",
)
print(text)
