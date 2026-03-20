from __future__ import annotations

import json
from typing import Any

from growth_ops.models import Contact, Lead, OutboundDraft, WebsiteEvidence, WebsiteReport
from growth_ops.services.evidence_checker import EvidenceCheckResult, check_proof_points
from growth_ops.services.llm_gateway import LLMGatewayClient, LLMGatewayError


class OutreachDraftingError(RuntimeError):
    """Raised when outbound drafting cannot be completed safely."""


class LeadNotDraftableError(OutreachDraftingError):
    """Raised when lead does not satisfy drafting prerequisites."""


def _flatten_scalar_paths(payload: Any, prefix: str = "", max_items: int = 20) -> list[tuple[str, str]]:
    flattened: list[tuple[str, str]] = []

    def walk(node: Any, path: str):
        if len(flattened) >= max_items:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                next_path = f"{path}.{key}" if path else str(key)
                walk(value, next_path)
            return
        if isinstance(node, list):
            return
        if node is None:
            return
        flattened.append((path, str(node)))

    walk(payload, prefix)
    return flattened


def _select_evidence_records(lead: Lead, report_obj: WebsiteReport | None) -> list[WebsiteEvidence]:
    if report_obj and isinstance(report_obj.evidence_ids, list) and report_obj.evidence_ids:
        numeric_ids = []
        for value in report_obj.evidence_ids:
            try:
                numeric_ids.append(int(value))
            except (TypeError, ValueError):
                continue
        if numeric_ids:
            records = list(
                lead.website_evidence.filter(id__in=numeric_ids).order_by("id")
            )
            if records:
                return records
    return list(lead.website_evidence.order_by("id"))


def _build_evidence_refs_for_llm(evidence_records: list[WebsiteEvidence]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for evidence in evidence_records:
        scalar_paths = _flatten_scalar_paths(evidence.payload, max_items=12)
        if scalar_paths:
            for path, value in scalar_paths:
                refs.append(
                    {
                        "evidence_id": str(evidence.id),
                        "evidence_type": evidence.evidence_type,
                        "evidence_path": path,
                        "evidence_excerpt": value[:500],
                    }
                )
        else:
            refs.append(
                {
                    "evidence_id": str(evidence.id),
                    "evidence_type": evidence.evidence_type,
                    "evidence_path": "payload",
                    "evidence_excerpt": json.dumps(evidence.payload, ensure_ascii=True)[:500],
                }
            )
    return refs[:200]


def _extract_report_findings(report_obj: WebsiteReport | None) -> list[dict[str, str]]:
    if report_obj is None or not isinstance(report_obj.report, dict):
        return []
    findings = report_obj.report.get("findings")
    if not isinstance(findings, list):
        return []
    output: list[dict[str, str]] = []
    for item in findings[:8]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        severity = str(item.get("severity", "medium")).strip().lower()
        diagnosis = str(item.get("diagnosis", "")).strip()
        if not title or not diagnosis:
            continue
        if severity not in {"low", "medium", "high", "critical"}:
            severity = "medium"
        output.append({"title": title, "severity": severity, "diagnosis": diagnosis})
    return output


def _fallback_safe_copy(lead: Lead, supported_points: list[dict[str, Any]]) -> tuple[str, str]:
    subject = f"Quick technical note on {lead.company_name}'s website"
    if not supported_points:
        body = (
            f"Hi {lead.company_name} team,\n\n"
            "I reviewed your site and identified technical opportunities around performance and scalability.\n"
            "If helpful, I can share a short, evidence-backed walkthrough and practical next steps.\n\n"
            "Would a 15-minute technical review call next week be useful?\n\n"
            "Best,\nMiss Bott"
        )
        return subject, body

    lines = [
        f"Hi {lead.company_name} team,",
        "",
        "I reviewed your site and noted a few verified technical signals:",
        "",
    ]
    for point in supported_points[:3]:
        lines.append(f"- {point.get('claim', '').strip()}")
    lines.extend(
        [
            "",
            "If useful, I can walk you through practical fixes and whether a custom stack upgrade is justified.",
            "",
            "Would a short technical review call next week be useful?",
            "",
            "Best,",
            "Miss Bott",
        ]
    )
    return subject, "\n".join(lines)


def _normalize_proof_points(raw_points: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_points, list):
        return []
    output: list[dict[str, Any]] = []
    for item in raw_points:
        if not isinstance(item, dict):
            continue
        point = {
            "claim": str(item.get("claim", "")).strip(),
            "evidence_id": str(item.get("evidence_id", "")).strip(),
            "evidence_path": str(item.get("evidence_path", "")).replace("payload.", "").strip(),
            "quoted_value": str(item.get("quoted_value", "")).strip(),
        }
        if point["claim"]:
            output.append(point)
    return output


def _rewrite_unsupported_claims(
    *,
    lead: Lead,
    subject: str,
    body: str,
    initial_check: EvidenceCheckResult,
    evidence_records: list[WebsiteEvidence],
    llm_client: LLMGatewayClient,
) -> tuple[str, str, list[dict[str, Any]], dict[str, Any], list[str]]:
    risk_flags = list(initial_check.risk_flags)
    rewrite_meta: dict[str, Any] = {}

    if not initial_check.supported_proof_points:
        safe_subject, safe_body = _fallback_safe_copy(lead, [])
        risk_flags.append("UNSUPPORTED_CLAIMS_REMOVED")
        rewrite_meta["strategy"] = "deterministic_fallback_no_supported_points"
        return safe_subject, safe_body, [], rewrite_meta, risk_flags

    try:
        rewrite_response = llm_client.check_email(
            {
                "lead_id": lead.id,
                "company_name": lead.company_name,
                "original_subject": subject,
                "original_body": body,
                "unsupported_claims": initial_check.unsupported_claims,
                "supported_proof_points": initial_check.supported_proof_points,
            }
        )
        rewritten_subject = str(rewrite_response.get("subject", "")).strip() or subject
        rewritten_body = str(rewrite_response.get("body", "")).strip() or body
        rewritten_points = _normalize_proof_points(rewrite_response.get("proof_points", []))

        post_check = check_proof_points(
            proof_points=rewritten_points,
            evidence_records=evidence_records,
        )
        if not post_check.unsupported_proof_points:
            risk_flags.append("UNSUPPORTED_CLAIMS_REWRITTEN")
            rewrite_meta["strategy"] = "llm_rewrite"
            rewrite_meta["model"] = rewrite_response.get("model", "")
            rewrite_meta["prompt_version"] = rewrite_response.get("prompt_version", "")
            return rewritten_subject, rewritten_body, post_check.supported_proof_points, rewrite_meta, risk_flags
    except LLMGatewayError as exc:
        rewrite_meta["llm_error"] = str(exc)

    fallback_subject, fallback_body = _fallback_safe_copy(
        lead,
        initial_check.supported_proof_points,
    )
    risk_flags.append("UNSUPPORTED_CLAIMS_REMOVED")
    rewrite_meta["strategy"] = "deterministic_fallback_supported_only"
    return (
        fallback_subject,
        fallback_body,
        initial_check.supported_proof_points,
        rewrite_meta,
        risk_flags,
    )


def create_outbound_draft(
    *,
    lead: Lead,
    contact: Contact | None = None,
    sequence_step: int = 1,
    channel: str = "email",
    llm_client: LLMGatewayClient | None = None,
) -> OutboundDraft:
    latest_score = lead.scores.order_by("-created_at").first()
    if latest_score is None:
        raise LeadNotDraftableError("lead_missing_score")
    if latest_score.bucket not in {"A", "B"}:
        raise LeadNotDraftableError("lead_bucket_not_eligible_for_drafting")

    report_obj = lead.website_reports.order_by("-created_at").first()
    if report_obj is None:
        raise OutreachDraftingError("lead_missing_report")

    evidence_records = _select_evidence_records(lead, report_obj)
    if not evidence_records:
        raise OutreachDraftingError("lead_missing_evidence")

    llm = llm_client or LLMGatewayClient()
    offer_type = str(latest_score.recommendation.get("offer_type", "technical_review"))
    draft_payload = {
        "lead_id": lead.id,
        "company_name": lead.company_name,
        "website_url": lead.website_url,
        "market": lead.market,
        "industry": lead.industry or None,
        "bucket": latest_score.bucket,
        "score": latest_score.score,
        "offer_type": offer_type,
        "sequence_step": sequence_step,
        "report_summary": report_obj.summary
        or str((report_obj.report or {}).get("executive_summary", "")),
        "report_findings": _extract_report_findings(report_obj),
        "evidence": _build_evidence_refs_for_llm(evidence_records),
    }

    draft_response = llm.draft_email(draft_payload)
    subject = str(draft_response.get("subject", "")).strip()
    body = str(draft_response.get("body", "")).strip()
    proof_points = _normalize_proof_points(draft_response.get("proof_points", []))
    if not subject or not body or not proof_points:
        raise OutreachDraftingError("invalid_draft_from_llm_gateway")

    initial_check = check_proof_points(
        proof_points=proof_points,
        evidence_records=evidence_records,
    )

    final_subject = subject
    final_body = body
    final_points = initial_check.supported_proof_points if not initial_check.unsupported_proof_points else []
    incoming_risk_flags = draft_response.get("risk_flags")
    if not isinstance(incoming_risk_flags, list):
        incoming_risk_flags = []
    risk_flags = list(dict.fromkeys(incoming_risk_flags + initial_check.risk_flags))
    rewrite_meta: dict[str, Any] = {}

    if initial_check.unsupported_proof_points:
        (
            final_subject,
            final_body,
            final_points,
            rewrite_meta,
            risk_flags,
        ) = _rewrite_unsupported_claims(
            lead=lead,
            subject=subject,
            body=body,
            initial_check=initial_check,
            evidence_records=evidence_records,
            llm_client=llm,
        )

    final_check = check_proof_points(
        proof_points=final_points,
        evidence_records=evidence_records,
    )
    if final_check.unsupported_proof_points:
        raise OutreachDraftingError("unable_to_produce_supported_draft")

    final_status = "pass"
    if initial_check.unsupported_proof_points:
        if rewrite_meta.get("strategy") == "llm_rewrite":
            final_status = "rewritten_safe"
        else:
            final_status = "fallback_safe"

    draft = OutboundDraft.objects.create(
        lead=lead,
        contact=contact,
        channel=channel,
        sequence_step=sequence_step,
        subject=final_subject,
        body=final_body,
        model=str(draft_response.get("model", "")),
        prompt_version=str(draft_response.get("prompt_version", "")),
        proof_points=final_points,
        risk_flags=list(dict.fromkeys(risk_flags)),
        evidence_check={
            "status": final_status,
            "initial": {
                "status": initial_check.status,
                "supported_count": len(initial_check.supported_proof_points),
                "unsupported_count": len(initial_check.unsupported_proof_points),
                "unsupported_claims": initial_check.unsupported_claims,
            },
            "final": {
                "status": final_check.status,
                "supported_count": len(final_check.supported_proof_points),
                "unsupported_count": len(final_check.unsupported_proof_points),
            },
            "rewrite": rewrite_meta,
        },
        approval_status="pending",
    )

    if lead.status in {"scored", "reported", "evidence_collected", "new"}:
        lead.status = "draft_pending"
        lead.save()

    return draft
