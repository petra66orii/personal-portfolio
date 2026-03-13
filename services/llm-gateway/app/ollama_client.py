from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class OllamaClientError(RuntimeError):
    """Raised when Ollama cannot produce a usable response."""


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: int):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def chat(self, *, model: str, messages: list[dict[str, str]], json_mode: bool = True) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        if json_mode:
            payload["format"] = "json"

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Ollama request failed: %s", exc)
            raise OllamaClientError("ollama_request_failed") from exc

        try:
            data = response.json()
            content = (data.get("message") or {}).get("content", "").strip()
        except ValueError as exc:
            raise OllamaClientError("ollama_invalid_json_response") from exc

        if not content:
            raise OllamaClientError("ollama_empty_content")
        return content
