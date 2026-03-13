from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    log_level: str
    ollama_base_url: str
    llm_model_report: str
    prompt_version_website_reporter: str
    llm_max_retries: int
    llm_timeout_seconds: int
    prompts_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        default_prompts_dir = Path(__file__).resolve().parent / "prompts"
        return cls(
            log_level=os.getenv("LLM_GATEWAY_LOG_LEVEL", "INFO").upper(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            llm_model_report=os.getenv("LLM_MODEL_REPORT", "qwen2.5:14b-instruct-q4_K_M"),
            prompt_version_website_reporter=os.getenv(
                "PROMPT_VERSION_WEBSITE_REPORTER",
                "2026-03-12",
            ),
            llm_max_retries=max(0, _int_env("LLM_MAX_RETRIES", 2)),
            llm_timeout_seconds=max(5, _int_env("LLM_TIMEOUT_SECONDS", 120)),
            prompts_dir=Path(os.getenv("PROMPTS_DIR", str(default_prompts_dir))),
        )
