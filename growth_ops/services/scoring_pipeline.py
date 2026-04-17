from __future__ import annotations

import json
from typing import Any

from django.db import transaction

from growth_ops.models import Lead, LeadScore, WebsiteReport
from growth_ops.services.contact_enrichment import upsert_contacts_for_lead
from growth_ops.services.contact_finder import enrich_with_contact_page, extract_contact_candidates
from growth_ops.services.drafting import upsert_outbound_draft
from growth_ops.services.email_builder import build_outreach_email
from growth_ops.services.outreach_engine import classify_outreach_opportunity
from growth_ops.services.outreach_readiness import classify_draft_readiness
from growth_ops.services.reporting import (
    RULES_REPORT_MODEL,
    RULES_REPORT_PROMPT_VERSION,
    build_report_payload,
    enhance_report_with_llm,
    get_latest_evidence_for_lead,
    upsert_report,
)
from growth_ops.services.scoring import compute_lead_score


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _find_matching_score(
    *,
    lead: Lead,
    score: int,
    bucket: str,
    reason_codes: list[str],
    recommendation: dict[str, Any],
) -> LeadScore | None:
    recent_scores = lead.scores.filter(score=score, bucket=bucket).order_by("-created_at")[:25]
    target_reasons = list(reason_codes)
    target_recommendation = _canonical_json(recommendation)
    for score_record in recent_scores:
        if (
            list(score_record.reason_codes or []) == target_reasons
            and _canonical_json(score_record.recommendation) == target_recommendation
        ):
            return score_record
    return None


@transaction.atomic
def upsert_lead_score(
    *,
    lead: Lead,
    report_obj: WebsiteReport | None,
    force: bool = False,
) -> tuple[LeadScore, bool]:
    result = compute_lead_score(lead=lead, report_obj=report_obj)

    if not force:
        existing_score = _find_matching_score(
            lead=lead,
            score=result.score,
            bucket=result.bucket,
            reason_codes=result.reason_codes,
            recommendation=result.recommendation,
        )
        if existing_score is not None:
            if lead.status in {"new", "evidence_collected", "reported"}:
                lead.status = "scored"
                lead.save(update_fields=["status", "updated_at"])
            return existing_score, False

    score_record = LeadScore.objects.create(
        lead=lead,
        score=result.score,
        bucket=result.bucket,
        reason_codes=result.reason_codes,
        recommendation=result.recommendation,
    )
    if lead.status in {"new", "evidence_collected", "reported"}:
        lead.status = "scored"
        lead.save(update_fields=["status", "updated_at"])
    return score_record, True


def persist_lead_score(*, lead: Lead, report_obj: WebsiteReport | None) -> LeadScore:
    score_record, _created = upsert_lead_score(lead=lead, report_obj=report_obj, force=False)
    return score_record


def _latest_homepage_html_for_lead(lead: Lead) -> tuple[str, str]:
    evidence = (
        lead.website_evidence.filter(evidence_type="homepage_html_snippet")
        .order_by("-created_at", "-id")
        .first()
    )
    if evidence is None or not isinstance(evidence.payload, dict):
        return "", lead.website_url or ""
    payload = evidence.payload
    html = str(payload.get("body") or "")
    requested_url = str(payload.get("requested_url") or evidence.url or lead.website_url or "")
    return html, requested_url


def run_outreach_for_lead(
    lead: Lead,
    *,
    force: bool = False,
    report_obj: WebsiteReport | None = None,
    score_obj: LeadScore | None = None,
) -> dict[str, Any]:
    resolved_report = report_obj or lead.website_reports.order_by("-created_at").first()
    if resolved_report is None:
        raise ValueError("lead_missing_report")
    resolved_score = score_obj or lead.scores.order_by("-created_at").first()
    if resolved_score is None:
        raise ValueError("lead_missing_score")

    report_payload = resolved_report.report if isinstance(resolved_report.report, dict) else {}
    decision = classify_outreach_opportunity(
        lead=lead,
        report_payload=report_payload,
        score_obj=resolved_score,
    )
    if not decision.get("should_contact", False):
        return {
            "lead_id": lead.id,
            "should_contact": False,
            "priority": decision.get("priority", "low"),
            "decision": decision,
            "draft_id": None,
            "draft_created": False,
            "draft_reused": False,
            "draft_skipped": True,
        }

    email_payload = build_outreach_email(
        lead=lead,
        report_payload=report_payload,
        score_obj=resolved_score,
        decision=decision,
        report_obj=resolved_report,
        sequence_step=1,
    )
    draft, draft_created = upsert_outbound_draft(
        lead=lead,
        decision=decision,
        email_payload=email_payload,
        score_obj=resolved_score,
        report_obj=resolved_report,
        force=force,
    )

    extracted_contacts: dict[str, Any] = {
        "emails": [],
        "phones": [],
        "contact_links": [],
        "social_links": {},
        "best_email": None,
        "best_phone": None,
        "selected_contact_link": None,
    }
    contact_summary: dict[str, Any] = {
        "contacts_created": 0,
        "contacts_reused": 0,
        "primary_contact": None,
    }
    primary_contact = None
    extraction_error = ""
    try:
        homepage_html, source_url = _latest_homepage_html_for_lead(lead)
        extracted_contacts = extract_contact_candidates(
            homepage_html=homepage_html,
            website_url=source_url or lead.website_url,
        )
        extracted_contacts = enrich_with_contact_page(
            candidates=extracted_contacts,
            website_url=source_url or lead.website_url,
        )
        contact_summary = upsert_contacts_for_lead(
            lead=lead,
            extracted_contacts=extracted_contacts,
        )
        primary_contact = contact_summary.get("primary_contact")
        if primary_contact is not None and draft.contact_id != primary_contact.id:
            draft.contact = primary_contact
            draft.save(update_fields=["contact", "updated_at"])
    except Exception as exc:
        extraction_error = str(exc)

    readiness = classify_draft_readiness(
        draft=draft,
        primary_contact=primary_contact,
        extracted_contacts=extracted_contacts,
    )
    evidence_check = draft.evidence_check if isinstance(draft.evidence_check, dict) else {}
    extracted_emails = list(extracted_contacts.get("emails") or [])
    extracted_phones = list(extracted_contacts.get("phones") or [])
    contact_links = list(extracted_contacts.get("contact_links") or [])
    selected_email = extracted_contacts.get("best_email")
    selected_phone = extracted_contacts.get("best_phone")
    selected_contact_link = (
        str(extracted_contacts.get("selected_contact_link") or "").strip()
        or (str(contact_links[0]).strip() if contact_links else None)
    )

    evidence_check["v35_contacts"] = {
        "emails": list(extracted_contacts.get("emails") or []),
        "phones": list(extracted_contacts.get("phones") or []),
        "contact_links": list(extracted_contacts.get("contact_links") or []),
        "social_links": dict(extracted_contacts.get("social_links") or {}),
        "best_email": extracted_contacts.get("best_email"),
        "best_phone": extracted_contacts.get("best_phone"),
        "selected_contact_link": selected_contact_link,
        "contacts_created": int(contact_summary.get("contacts_created") or 0),
        "contacts_reused": int(contact_summary.get("contacts_reused") or 0),
        "primary_contact_id": primary_contact.id if primary_contact is not None else None,
    }
    evidence_check["v35_readiness"] = readiness
    evidence_check["v35_diagnostics"] = {
        "extracted_emails": extracted_emails,
        "extracted_phones": extracted_phones,
        "contact_links": contact_links,
        "selected_email": selected_email,
        "selected_phone": selected_phone,
        "selected_contact_link": selected_contact_link,
        "readiness_status": readiness.get("status", "pending"),
        "readiness_reason": readiness.get("reason", ""),
        "contactability_type": readiness.get("contactability_type", "none"),
    }
    evidence_check["draft_generation_mode"] = str(email_payload.get("draft_generation_mode") or "deterministic")
    evidence_check["llm_prompt_name"] = str(email_payload.get("llm_prompt_name") or "")
    evidence_check["llm_prompt_version"] = str(email_payload.get("llm_prompt_version") or "")
    evidence_check["llm_fallback_used"] = bool(email_payload.get("llm_fallback_used", False))
    evidence_check["llm_fallback_reason"] = str(email_payload.get("llm_fallback_reason") or "")
    claim_check = email_payload.get("claim_check")
    evidence_check["claim_check"] = claim_check if isinstance(claim_check, dict) else {}
    # Keep explicit keys at root for fast inspection from admin/queue tooling.
    evidence_check["extracted_emails"] = extracted_emails
    evidence_check["extracted_phones"] = extracted_phones
    evidence_check["contact_links"] = contact_links
    evidence_check["selected_email"] = selected_email
    evidence_check["selected_phone"] = selected_phone
    evidence_check["selected_contact_link"] = selected_contact_link
    evidence_check["readiness_status"] = readiness.get("status", "pending")
    evidence_check["readiness_reason"] = readiness.get("reason", "")
    evidence_check["contactability_type"] = readiness.get("contactability_type", "none")
    if extraction_error:
        evidence_check["v35_contact_error"] = extraction_error
    draft.evidence_check = evidence_check
    draft.save(update_fields=["evidence_check", "updated_at"])

    return {
        "lead_id": lead.id,
        "should_contact": True,
        "priority": decision.get("priority", "medium"),
        "decision": decision,
        "draft_id": draft.id,
        "draft_created": draft_created,
        "draft_reused": not draft_created,
        "draft_skipped": False,
        "draft_generation_mode": str(email_payload.get("draft_generation_mode") or "deterministic"),
        "llm_fallback_used": bool(email_payload.get("llm_fallback_used", False)),
        "readiness_status": readiness.get("status", "pending"),
        "readiness_reason": readiness.get("reason", ""),
        "contacts_created": int(contact_summary.get("contacts_created") or 0),
        "contacts_reused": int(contact_summary.get("contacts_reused") or 0),
    }


def run_report_and_score_for_lead(
    lead: Lead,
    *,
    force: bool = False,
    model: str = RULES_REPORT_MODEL,
    prompt_version: str = RULES_REPORT_PROMPT_VERSION,
) -> dict[str, Any]:
    evidence = get_latest_evidence_for_lead(lead)
    evidence_ids = [item.id for item in evidence]

    deterministic_report_payload = build_report_payload(lead=lead, evidence=evidence)
    report_payload = enhance_report_with_llm(
        lead=lead,
        evidence=evidence,
        deterministic_report=deterministic_report_payload,
    )
    report_summary = str(report_payload.get("summary") or "").strip()
    report_obj, report_created = upsert_report(
        lead=lead,
        report_payload=report_payload,
        evidence_ids=evidence_ids,
        model=model,
        prompt_version=prompt_version,
        summary=report_summary,
        force=force,
    )

    score_obj, score_created = upsert_lead_score(
        lead=lead,
        report_obj=report_obj,
        force=force,
    )

    return {
        "lead_id": lead.id,
        "report_id": report_obj.id,
        "score_id": score_obj.id,
        "report_created": report_created,
        "report_reused": not report_created,
        "score_created": score_created,
        "score_reused": not score_created,
    }


def run_report_score_and_outreach_for_lead(
    lead: Lead,
    *,
    force: bool = False,
    model: str = RULES_REPORT_MODEL,
    prompt_version: str = RULES_REPORT_PROMPT_VERSION,
) -> dict[str, Any]:
    base_result = run_report_and_score_for_lead(
        lead,
        force=force,
        model=model,
        prompt_version=prompt_version,
    )
    report_obj = lead.website_reports.filter(id=base_result["report_id"]).first()
    score_obj = lead.scores.filter(id=base_result["score_id"]).first()
    outreach_result = run_outreach_for_lead(
        lead,
        force=force,
        report_obj=report_obj,
        score_obj=score_obj,
    )
    return {
        **base_result,
        **outreach_result,
    }
