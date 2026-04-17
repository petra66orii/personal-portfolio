from __future__ import annotations

from typing import Any

from django.utils import timezone

from growth_ops.models import Lead, LeadScore, OutboundDraft, WebsiteReport

DETERMINISTIC_DRAFT_MODEL = "deterministic_rules_v3"
DETERMINISTIC_DRAFT_PROMPT_VERSION = "growth_outreach_v3_rules_1"


def _decision_key(decision: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(decision.get("offer_type") or "").strip().lower(),
        str(decision.get("angle") or "").strip().lower(),
        str(decision.get("priority") or "").strip().lower(),
    )


def _draft_matches(
    *,
    draft: OutboundDraft,
    decision: dict[str, Any],
    email_payload: dict[str, Any],
) -> bool:
    if (draft.subject or "").strip() != (email_payload.get("subject") or "").strip():
        return False
    if (draft.body or "").strip() != (email_payload.get("body") or "").strip():
        return False

    evidence_check = draft.evidence_check if isinstance(draft.evidence_check, dict) else {}
    saved_decision = evidence_check.get("v3_decision")
    if not isinstance(saved_decision, dict):
        return False
    return _decision_key(saved_decision) == _decision_key(decision)


def _find_matching_outbound_draft(
    *,
    lead: Lead,
    decision: dict[str, Any],
    email_payload: dict[str, Any],
) -> OutboundDraft | None:
    recent_drafts = lead.outbound_drafts.filter(channel="email").order_by("-created_at")[:25]
    for draft in recent_drafts:
        if _draft_matches(draft=draft, decision=decision, email_payload=email_payload):
            return draft
    return None


def upsert_outbound_draft(
    *,
    lead: Lead,
    decision: dict[str, Any],
    email_payload: dict[str, Any],
    score_obj: LeadScore,
    report_obj: WebsiteReport | None = None,
    force: bool = False,
) -> tuple[OutboundDraft, bool]:
    if not force:
        existing = _find_matching_outbound_draft(
            lead=lead,
            decision=decision,
            email_payload=email_payload,
        )
        if existing is not None:
            if lead.status in {"scored", "reported", "evidence_collected", "new"}:
                lead.status = "draft_pending"
                lead.save(update_fields=["status", "updated_at"])
            return existing, False

    draft_generation_mode = str(email_payload.get("draft_generation_mode") or "deterministic").strip()
    llm_prompt_name = str(email_payload.get("llm_prompt_name") or "").strip()
    llm_prompt_version = str(email_payload.get("llm_prompt_version") or "").strip()
    llm_fallback_used = bool(email_payload.get("llm_fallback_used", False))
    llm_fallback_reason = str(email_payload.get("llm_fallback_reason") or "").strip()
    claim_check = email_payload.get("claim_check")
    normalized_claim_check = claim_check if isinstance(claim_check, dict) else {}
    proof_points = email_payload.get("proof_points")
    normalized_proof_points = proof_points if isinstance(proof_points, list) else []
    incoming_risk_flags = email_payload.get("risk_flags")
    normalized_risk_flags = (
        [str(item).strip() for item in incoming_risk_flags if str(item).strip()]
        if isinstance(incoming_risk_flags, list)
        else []
    )
    if not normalized_risk_flags:
        normalized_risk_flags = ["DETERMINISTIC_V3"]

    status_value = "deterministic_v3"
    if draft_generation_mode != "deterministic":
        status_value = "llm_assisted_v3"

    evidence_check = {
        "status": status_value,
        "generated_at": timezone.now().isoformat(),
        "v3_decision": {
            "should_contact": bool(decision.get("should_contact", False)),
            "priority": str(decision.get("priority") or ""),
            "offer_type": str(decision.get("offer_type") or ""),
            "angle": str(decision.get("angle") or ""),
            "reason_summary": str(decision.get("reason_summary") or ""),
        },
        "draft_generation_mode": draft_generation_mode,
        "llm_prompt_name": llm_prompt_name,
        "llm_prompt_version": llm_prompt_version,
        "llm_fallback_used": llm_fallback_used,
        "llm_fallback_reason": llm_fallback_reason,
        "claim_check": normalized_claim_check,
        "score_id": score_obj.id,
        "report_id": report_obj.id if report_obj is not None else None,
        "preview": str(email_payload.get("preview") or ""),
    }

    draft = OutboundDraft.objects.create(
        lead=lead,
        channel="email",
        sequence_step=1,
        subject=str(email_payload.get("subject") or "").strip(),
        body=str(email_payload.get("body") or "").strip(),
        model=str(email_payload.get("model") or DETERMINISTIC_DRAFT_MODEL).strip(),
        prompt_version=str(email_payload.get("prompt_version") or DETERMINISTIC_DRAFT_PROMPT_VERSION).strip(),
        proof_points=normalized_proof_points,
        risk_flags=list(dict.fromkeys(normalized_risk_flags)),
        evidence_check=evidence_check,
        approval_status="pending",
    )

    if lead.status in {"scored", "reported", "evidence_collected", "new"}:
        lead.status = "draft_pending"
        lead.save(update_fields=["status", "updated_at"])
    return draft, True
