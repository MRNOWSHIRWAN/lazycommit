"""Talk to any OpenAI-compatible chat endpoint (Ollama, llama.cpp, LM Studio).

Only the standard library is used: no SDK, no API key, no cloud account.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "http://localhost:11434/v1"  # Ollama's default
DEFAULT_MODEL = "qwen2.5-coder:0.5b-instruct"


class BackendError(RuntimeError):
    pass


def chat(
    messages: list[dict],
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 60,
    temperature: float = 0.0,
    timeout: float = 120.0,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    ).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise BackendError(
            f"could not reach a local model server at {base_url} ({exc}). "
            "Start one first, e.g. `ollama serve` (https://ollama.com) or "
            "llama.cpp's llama-server, then pull an open-weight model such "
            f"as `{model}`."
        ) from exc
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise BackendError(f"unexpected response from {url}: {data!r}") from exc
