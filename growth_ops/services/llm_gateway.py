from __future__ import annotations

import os
from typing import Any

import requests


class LLMGatewayError(RuntimeError):
    """Raised when llm_gateway is unavailable or returns invalid output."""


class LLMGatewayClient:
    def __init__(self, *, base_url: str | None = None, timeout_seconds: int | None = None):
        self.base_url = (
            base_url
            or os.getenv("LLM_GATEWAY_BASE_URL")
            or "http://llm_gateway:8001"
        ).rstrip("/")
        self.api_key = os.getenv("LLM_GATEWAY_API_KEY", "").strip()
        try:
            self.timeout_seconds = int(timeout_seconds or os.getenv("LLM_GATEWAY_TIMEOUT_SECONDS", "60"))
        except ValueError:
            self.timeout_seconds = 60

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["X-LLM-GATEWAY-KEY"] = self.api_key

        try:
            response = requests.post(
                f"{self.base_url}{path}",
                json=payload,
                headers=headers or None,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMGatewayError(f"llm_gateway_request_failed:{path}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMGatewayError(f"llm_gateway_invalid_json:{path}") from exc

        if not isinstance(data, dict):
            raise LLMGatewayError(f"llm_gateway_unexpected_shape:{path}")
        return data

    def draft_email(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/v1/draft-email", payload)

    def check_email(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/v1/check-email", payload)

    def report(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/v1/report", payload)
