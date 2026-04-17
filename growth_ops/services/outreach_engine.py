from __future__ import annotations

from typing import Any

from growth_ops.models import Lead, LeadScore


def _findings_from_report(report_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = report_payload.get("findings")
    if not isinstance(findings, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        severity = str(item.get("severity") or "medium").strip().lower()
        diagnosis = str(item.get("diagnosis") or "").strip()
        if not title:
            continue
        if severity not in {"high", "medium", "low"}:
            severity = "medium"
        normalized.append(
            {
                "title": title,
                "severity": severity,
                "diagnosis": diagnosis,
            }
        )
    return normalized


def _is_cta_weak(report_payload: dict[str, Any]) -> bool:
    cta_clarity = str(report_payload.get("cta_clarity") or "").strip().lower()
    return cta_clarity in {"weak", "missing", "unclear", "poor"}


def _is_performance_poor(report_payload: dict[str, Any]) -> bool:
    performance = report_payload.get("performance")
    if not isinstance(performance, dict):
        return False
    score_raw = performance.get("score")
    lcp_raw = performance.get("lcp_ms")
    try:
        perf_score = float(score_raw) if score_raw is not None else None
    except (TypeError, ValueError):
        perf_score = None
    try:
        lcp_ms = float(lcp_raw) if lcp_raw is not None else None
    except (TypeError, ValueError):
        lcp_ms = None
    rating = str(performance.get("rating") or "").strip().lower()
    if perf_score is not None and perf_score < 70:
        return True
    if lcp_ms is not None and lcp_ms > 3000:
        return True
    return rating in {"poor"}


def _is_trust_weak(report_payload: dict[str, Any]) -> bool:
    trust = report_payload.get("trust")
    if not isinstance(trust, dict):
        return False
    rating = str(trust.get("rating") or "").strip().lower()
    if rating == "weak":
        return True
    score_raw = trust.get("score")
    max_score_raw = trust.get("max_score")
    try:
        score = float(score_raw) if score_raw is not None else None
        max_score = float(max_score_raw) if max_score_raw is not None else None
    except (TypeError, ValueError):
        return False
    if score is None or max_score is None or max_score <= 0:
        return False
    return score / max_score < 0.4


def _seo_issue_count(report_payload: dict[str, Any]) -> int:
    seo = report_payload.get("seo")
    if not isinstance(seo, dict):
        return 0
    issues = seo.get("issues")
    if not isinstance(issues, list):
        return 0
    return len([issue for issue in issues if str(issue).strip()])


def _reason_summary(
    *,
    findings: list[dict[str, Any]],
    default_message: str,
) -> str:
    if not findings:
        return default_message
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    prioritized = sorted(
        findings,
        key=lambda item: (-severity_rank.get(str(item.get("severity", "")).lower(), 0), item.get("title", "")),
    )
    top_titles = [str(item.get("title", "")).strip() for item in prioritized[:2] if str(item.get("title", "")).strip()]
    if not top_titles:
        return default_message
    return "; ".join(top_titles)


def classify_outreach_opportunity(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    score_obj: LeadScore,
) -> dict[str, Any]:
    score = int(score_obj.score or 0)
    if score >= 60:
        should_contact = True
        priority = "high"
    elif score >= 45:
        should_contact = True
        priority = "medium"
    else:
        should_contact = False
        priority = "low"

    findings = _findings_from_report(report_payload)
    cta_weak = _is_cta_weak(report_payload)
    performance_poor = _is_performance_poor(report_payload)
    trust_weak = _is_trust_weak(report_payload)
    seo_count = _seo_issue_count(report_payload)

    if cta_weak:
        offer_type = "conversion_fix"
        angle = "cta_missing"
        default_reason = "Homepage call-to-action is weak or missing."
    elif performance_poor:
        offer_type = "performance_sprint"
        angle = "slow_site"
        default_reason = "Mobile performance signals are below target."
    elif trust_weak:
        offer_type = "trust_rebuild"
        angle = "low_trust"
        default_reason = "Trust indicators are limited for first-time visitors."
    elif seo_count >= 3:
        offer_type = "seo_hygiene"
        angle = "seo_hygiene"
        default_reason = "Core SEO hygiene issues are reducing discoverability."
    else:
        offer_type = "general_audit"
        angle = "general"
        default_reason = "Multiple technical and conversion improvements are available."

    summary = _reason_summary(findings=findings, default_message=default_reason)
    return {
        "should_contact": should_contact,
        "priority": priority,
        "offer_type": offer_type,
        "angle": angle,
        "reason_summary": summary,
        "score": score,
        "lead_id": lead.id,
    }
