from __future__ import annotations

import json
import logging
from json import JSONDecodeError
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from .config import Settings
from .ollama_client import OllamaClient, OllamaClientError
from .prompt_loader import load_prompt
from .schemas import HealthResponse, ReportRequest, ReportResponse, ReportResult

settings = Settings.from_env()
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("llm_gateway")

app = FastAPI(title="Miss Bott LLM Gateway", version="0.1.0")
ollama_client = OllamaClient(
    base_url=settings.ollama_base_url,
    timeout_seconds=settings.llm_timeout_seconds,
)


def _parse_json(content: str) -> dict:
    try:
        parsed = json.loads(content)
    except JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(content[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Model output must be a JSON object")
    return parsed


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="llm_gateway",
        model_report=settings.llm_model_report,
    )


@app.post("/v1/report", response_model=ReportResponse)
def generate_report(payload: ReportRequest) -> ReportResponse:
    prompt_path = settings.prompts_dir / "website_reporter.md"
    prompt = load_prompt(prompt_path)
    request_id = str(uuid4())

    schema_json = json.dumps(ReportResult.model_json_schema(), separators=(",", ":"))
    user_payload = json.dumps(payload.model_dump(mode="json"), separators=(",", ":"))
    base_messages = [
        {
            "role": "system",
            "content": (
                f"{prompt.content}\n\n"
                "Return only JSON and match this schema exactly:\n"
                f"{schema_json}"
            ),
        },
        {"role": "user", "content": user_payload},
    ]

    last_error: str = "unknown_error"
    for attempt in range(settings.llm_max_retries + 1):
        messages = list(base_messages)
        if attempt > 0:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Previous output was invalid. Return only strict JSON matching the schema, "
                        "with no prose, markdown, or trailing text."
                    ),
                }
            )

        try:
            content = ollama_client.chat(
                model=settings.llm_model_report,
                messages=messages,
                json_mode=True,
            )
            parsed = _parse_json(content)
            report = ReportResult.model_validate(parsed)
            logger.info(
                "report_generated request_id=%s attempt=%d model=%s prompt=%s",
                request_id,
                attempt + 1,
                settings.llm_model_report,
                prompt.prompt_name,
            )
            return ReportResponse(
                request_id=request_id,
                model=settings.llm_model_report,
                prompt_name=prompt.prompt_name,
                prompt_version=settings.prompt_version_website_reporter
                or prompt.prompt_version,
                **report.model_dump(),
            )
        except (OllamaClientError, JSONDecodeError, ValidationError, ValueError) as exc:
            last_error = str(exc)
            logger.warning(
                "report_generation_retry request_id=%s attempt=%d error=%s",
                request_id,
                attempt + 1,
                last_error,
            )

    raise HTTPException(
        status_code=502,
        detail={
            "error": "report_generation_failed",
            "request_id": request_id,
            "reason": last_error,
        },
    )
