from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1, max_length=128)
    evidence_type: str = Field(min_length=1, max_length=64)
    evidence_path: str = Field(min_length=1, max_length=255)
    evidence_excerpt: str | None = Field(default=None, max_length=1000)


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lead_id: int | None = None
    company_name: str = Field(min_length=1, max_length=255)
    website_url: HttpUrl
    market: Literal["IE", "RO", "US", "OTHER"] = "OTHER"
    industry: str | None = Field(default=None, max_length=120)
    objective: str | None = Field(default=None, max_length=500)
    evidence: list[EvidenceReference] = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class ReportFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    severity: Literal["low", "medium", "high", "critical"]
    diagnosis: str = Field(min_length=1, max_length=1200)
    business_impact: str = Field(min_length=1, max_length=1200)
    recommendation: str = Field(min_length=1, max_length=1200)
    evidence_refs: list[EvidenceReference] = Field(min_length=1)


class ReportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(min_length=1, max_length=2000)
    findings: list[ReportFinding] = Field(min_length=1)
    quick_wins: list[str] = Field(default_factory=list, max_length=5)
    confidence: Literal["low", "medium", "high"]


class ReportResponse(ReportResult):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    prompt_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: Literal["llm_gateway"]
    model_report: str = Field(min_length=1)
