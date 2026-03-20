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


class ReportFindingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    severity: Literal["low", "medium", "high", "critical"]
    diagnosis: str = Field(min_length=1, max_length=1200)


class EmailProofPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(min_length=1, max_length=1000)
    evidence_id: str = Field(min_length=1, max_length=128)
    evidence_path: str = Field(min_length=1, max_length=255)
    quoted_value: str | None = Field(default=None, max_length=500)


class DraftEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lead_id: int
    company_name: str = Field(min_length=1, max_length=255)
    website_url: HttpUrl
    market: Literal["IE", "RO", "US", "OTHER"] = "OTHER"
    industry: str | None = Field(default=None, max_length=120)
    bucket: Literal["A", "B"]
    score: int = Field(ge=0, le=100)
    offer_type: str = Field(min_length=1, max_length=128)
    sequence_step: int = Field(ge=1, le=10, default=1)
    report_summary: str = Field(min_length=1, max_length=2000)
    report_findings: list[ReportFindingInput] = Field(default_factory=list, max_length=8)
    evidence: list[EvidenceReference] = Field(min_length=1, max_length=200)


class DraftEmailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    channel: Literal["email"]
    sequence_step: int = Field(ge=1, le=10)
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=8000)
    proof_points: list[EmailProofPoint] = Field(min_length=1, max_length=12)
    risk_flags: list[str] = Field(default_factory=list, max_length=10)


class DraftEmailResponse(DraftEmailResult):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    prompt_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)


class CheckEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lead_id: int
    company_name: str = Field(min_length=1, max_length=255)
    original_subject: str = Field(min_length=1, max_length=255)
    original_body: str = Field(min_length=1, max_length=8000)
    unsupported_claims: list[str] = Field(min_length=1, max_length=20)
    supported_proof_points: list[EmailProofPoint] = Field(min_length=1, max_length=20)


class CheckEmailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=8000)
    proof_points: list[EmailProofPoint] = Field(min_length=1, max_length=20)
    notes: list[str] = Field(default_factory=list, max_length=10)


class CheckEmailResponse(CheckEmailResult):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    prompt_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
