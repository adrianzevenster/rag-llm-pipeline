# rag/ragflow/ollama_client.py
from __future__ import annotations

import os
from typing import Any, Dict

import requests


def _base_url() -> str:
    return os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")


def ollama_generate(model: str, prompt: str, *, timeout_s: int = 180) -> str:
    """
    Uses Ollama via OpenAI-compatible endpoint first:
      POST /v1/chat/completions

    Falls back to:
      POST /api/generate
    """
    base = _base_url()

    # 1) OpenAI-compatible
    oai_url = f"{base}/v1/chat/completions"
    oai_payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    r = requests.post(oai_url, json=oai_payload, timeout=timeout_s)
    if r.status_code != 404:
        r.raise_for_status()
        data = r.json()
        choices = data.get("choices") or []
        if not choices:
            return ""
        msg = (choices[0].get("message") or {})
        return (msg.get("content") or "").strip()

    # 2) Fallback: /api/generate
    gen_url = f"{base}/api/generate"
    gen_payload: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(gen_url, json=gen_payload, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()
