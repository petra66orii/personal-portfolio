from __future__ import annotations

import json
import logging
import secrets
from json import JSONDecodeError
from typing import Type
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ValidationError

from .config import Settings
from .ollama_client import OllamaClient, OllamaClientError
from .prompt_loader import load_prompt
from .schemas import (
    CheckEmailRequest,
    CheckEmailResponse,
    CheckEmailResult,
    DraftEmailRequest,
    DraftEmailResponse,
    DraftEmailResult,
    HealthResponse,
    ReportRequest,
    ReportResponse,
    ReportResult,
)

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


def _require_api_key(
    x_llm_gateway_key: str | None = Header(default=None, alias="X-LLM-GATEWAY-KEY"),
) -> None:
    if not settings.llm_gateway_require_api_key:
        return

    expected_key = settings.llm_gateway_api_key
    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail={"error": "llm_gateway_api_key_not_configured"},
        )

    if not x_llm_gateway_key or not secrets.compare_digest(x_llm_gateway_key, expected_key):
        raise HTTPException(status_code=401, detail={"error": "unauthorized"})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="llm_gateway",
        model_report=settings.llm_model_report,
    )


def _generate_structured_output(
    *,
    route_name: str,
    prompt_file: str,
    model_name: str,
    prompt_version: str,
    request_payload: dict,
    result_model: Type[BaseModel],
) -> tuple[str, str, BaseModel]:
    prompt_path = settings.prompts_dir / prompt_file
    try:
        prompt = load_prompt(prompt_path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "prompt_load_failed",
                "route": route_name,
                "reason": str(exc),
            },
        ) from exc

    request_id = str(uuid4())
    schema_json = json.dumps(result_model.model_json_schema(), separators=(",", ":"))
    user_payload = json.dumps(request_payload, separators=(",", ":"))
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
                model=model_name,
                messages=messages,
                json_mode=True,
            )
            parsed = _parse_json(content)
            validated = result_model.model_validate(parsed)
            logger.info(
                "%s_generated request_id=%s attempt=%d model=%s prompt=%s",
                route_name,
                request_id,
                attempt + 1,
                model_name,
                prompt.prompt_name,
            )
            return request_id, prompt.prompt_name, validated
        except (OllamaClientError, JSONDecodeError, ValidationError, ValueError) as exc:
            last_error = str(exc)
            logger.warning(
                "%s_generation_retry request_id=%s attempt=%d error=%s",
                route_name,
                request_id,
                attempt + 1,
                last_error,
            )

    raise HTTPException(
        status_code=502,
        detail={
            "error": f"{route_name}_generation_failed",
            "request_id": request_id,
            "reason": last_error,
        },
    )


@app.post("/v1/report", response_model=ReportResponse)
def generate_report(
    payload: ReportRequest,
    _: None = Depends(_require_api_key),
) -> ReportResponse:
    request_id, prompt_name, validated = _generate_structured_output(
        route_name="report",
        prompt_file="website_reporter.md",
        model_name=settings.llm_model_report,
        prompt_version=settings.prompt_version_website_reporter,
        request_payload=payload.model_dump(mode="json"),
        result_model=ReportResult,
    )
    report = ReportResult.model_validate(validated.model_dump())
    return ReportResponse(
        request_id=request_id,
        model=settings.llm_model_report,
        prompt_name=prompt_name,
        prompt_version=settings.prompt_version_website_reporter,
        **report.model_dump(),
    )


@app.post("/v1/draft-email", response_model=DraftEmailResponse)
def draft_email(
    payload: DraftEmailRequest,
    _: None = Depends(_require_api_key),
) -> DraftEmailResponse:
    request_id, prompt_name, validated = _generate_structured_output(
        route_name="draft_email",
        prompt_file="outreach_writer.md",
        model_name=settings.llm_model_draft_email,
        prompt_version=settings.prompt_version_outreach_writer,
        request_payload=payload.model_dump(mode="json"),
        result_model=DraftEmailResult,
    )
    result = DraftEmailResult.model_validate(validated.model_dump())
    return DraftEmailResponse(
        request_id=request_id,
        model=settings.llm_model_draft_email,
        prompt_name=prompt_name,
        prompt_version=settings.prompt_version_outreach_writer,
        **result.model_dump(),
    )


@app.post("/v1/check-email", response_model=CheckEmailResponse)
def check_email(
    payload: CheckEmailRequest,
    _: None = Depends(_require_api_key),
) -> CheckEmailResponse:
    request_id, prompt_name, validated = _generate_structured_output(
        route_name="check_email",
        prompt_file="evidence_checker.md",
        model_name=settings.llm_model_check_email,
        prompt_version=settings.prompt_version_evidence_checker,
        request_payload=payload.model_dump(mode="json"),
        result_model=CheckEmailResult,
    )
    result = CheckEmailResult.model_validate(validated.model_dump())
    return CheckEmailResponse(
        request_id=request_id,
        model=settings.llm_model_check_email,
        prompt_name=prompt_name,
        prompt_version=settings.prompt_version_evidence_checker,
        **result.model_dump(),
    )
