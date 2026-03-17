from __future__ import annotations

import requests
from config import OLLAMA_URL, OLLAMA_MODEL

def call_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = False,
) -> str:

    if json_mode:
        user_prompt = (
            user_prompt
            + "\n\nIMPORTANT: Return ONLY a single valid JSON object. "
            "No extra text, no markdown fences, no explanation outside the JSON."
        )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        raw = resp.json()["message"]["content"].strip()
    except requests.exceptions.ConnectionError:
        raise EnvironmentError(
            f"Cannot reach Ollama at {OLLAMA_URL}.\n"
            "Make sure Ollama is running: https://ollama.ai"
        )

    return _strip_fences(raw)

def _strip_fences(text: str) -> str:

    if text.startswith("```"):
        lines = text.splitlines()
        return "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()
    return text
