from __future__ import annotations

from typing import Any

from growth_ops.models import Lead, LeadScore


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _select_primary_issue(*, report_payload: dict[str, Any], decision: dict[str, Any]) -> str:
    cta_clarity = str(report_payload.get("cta_clarity") or "").strip().lower()
    cta = report_payload.get("cta")
    performance = report_payload.get("performance")
    trust = report_payload.get("trust")
    seo = report_payload.get("seo")
    technical = report_payload.get("technical")
    angle = str(decision.get("angle") or "").strip().lower()

    has_contact_method = None
    if isinstance(cta, dict):
        has_contact_method = cta.get("has_contact_method")
    if has_contact_method is None and isinstance(trust, dict):
        has_contact_method = trust.get("has_contact_info")

    perf_score = _to_float((performance or {}).get("score")) if isinstance(performance, dict) else None
    lcp_ms = _to_float((performance or {}).get("lcp_ms")) if isinstance(performance, dict) else None
    trust_rating = str((trust or {}).get("rating") or "").strip().lower() if isinstance(trust, dict) else ""
    seo_issues = (seo or {}).get("issues") if isinstance(seo, dict) else []
    seo_issue_count = len([issue for issue in seo_issues if str(issue).strip()]) if isinstance(seo_issues, list) else 0
    has_https = (technical or {}).get("has_https") if isinstance(technical, dict) else None

    # Priority order requested by user:
    # 1) weak CTA, 2) no contact method, 3) poor performance, 4) weak trust, 5) SEO issues
    if cta_clarity in {"missing", "weak", "unclear", "poor"}:
        return "weak_cta"
    if has_contact_method is False:
        return "no_contact_method"
    if (lcp_ms is not None and lcp_ms > 3000) or (perf_score is not None and perf_score < 70):
        return "poor_performance"
    if has_https is False:
        return "no_https"
    if trust_rating == "weak":
        return "weak_trust"
    if seo_issue_count > 0:
        return "seo_issues"

    # Deterministic fallback to decision angle if report is thin.
    if angle == "cta_missing":
        return "weak_cta"
    if angle == "slow_site":
        return "poor_performance"
    if angle == "low_trust":
        return "weak_trust"
    if angle == "seo_hygiene":
        return "seo_issues"
    return "general"


def _issue_copy(*, issue_key: str, report_payload: dict[str, Any]) -> tuple[str, str]:
    cta_clarity = str(report_payload.get("cta_clarity") or "weak").strip().lower()
    performance = report_payload.get("performance")
    seo = report_payload.get("seo")
    perf_score = _to_float((performance or {}).get("score")) if isinstance(performance, dict) else None
    lcp_ms = _to_float((performance or {}).get("lcp_ms")) if isinstance(performance, dict) else None

    if issue_key == "weak_cta":
        return (
            f"the homepage call-to-action is {cta_clarity}, so the next step is easy to miss.",
            "That usually means fewer enquiries from visitors who were ready to contact you.",
        )
    if issue_key == "no_contact_method":
        return (
            "there is no clear contact route visible on the homepage.",
            "If people cannot quickly find how to contact you, it can cost enquiries.",
        )
    if issue_key == "poor_performance":
        if perf_score is not None and lcp_ms is not None:
            return (
                f"mobile performance is slow (score {int(round(perf_score))}, LCP {int(round(lcp_ms))}ms).",
                "Slow pages lose attention early and can reduce conversion from paid and organic traffic.",
            )
        return (
            "mobile performance is below target.",
            "Slow load times usually reduce both engagement and enquiry intent.",
        )
    if issue_key == "no_https":
        return (
            "the site appears to run without HTTPS.",
            "A non-secure connection reduces trust for new visitors before they enquire.",
        )
    if issue_key == "weak_trust":
        return (
            "trust signals are light for first-time visitors.",
            "When trust is unclear, high-intent prospects often delay or skip contacting.",
        )
    if issue_key == "seo_issues":
        first_issue = ""
        if isinstance(seo, dict) and isinstance(seo.get("issues"), list):
            non_empty = [str(item).strip() for item in seo["issues"] if str(item).strip()]
            first_issue = non_empty[0] if non_empty else ""
        detail = f" ({first_issue})" if first_issue else ""
        return (
            f"there is an SEO hygiene gap{detail}.",
            "That can limit discoverability and reduce qualified inbound traffic over time.",
        )
    return (
        "one high-impact website issue stood out on review.",
        "Fixing it first should improve conversion confidence and lead flow.",
    )


def _subject(*, lead: Lead, issue_key: str) -> str:
    company = (lead.company_name or "your website").strip()
    if issue_key == "weak_cta":
        return f"Quick CTA fix for {company}"
    if issue_key == "no_contact_method":
        return f"Quick contact-path fix for {company}"
    if issue_key == "poor_performance":
        return f"Quick speed fix for {company}"
    if issue_key in {"weak_trust", "no_https"}:
        return f"Quick trust fix for {company}"
    if issue_key == "seo_issues":
        return f"Quick SEO fix for {company}"
    return f"Quick website idea for {company}"


def build_outreach_email(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    score_obj: LeadScore,
    decision: dict[str, Any],
) -> dict[str, str]:
    company = (lead.company_name or "your team").strip()
    issue_key = _select_primary_issue(report_payload=report_payload, decision=decision)
    issue_sentence, impact_sentence = _issue_copy(issue_key=issue_key, report_payload=report_payload)
    subject = _subject(lead=lead, issue_key=issue_key)

    body_lines = [
        f"Hi {company} team,",
        "",
        f"I had a quick look at {company}'s website and noticed that {issue_sentence}",
        impact_sentence,
        "",
        "If useful, I can share a short plan for fixing this first.",
        "Open to a quick call next week?",
        "",
        "Best,",
        "Petra",
        "Miss Bott",
    ]
    body = "\n".join(body_lines)
    preview = f"{company}: {issue_sentence} {impact_sentence}"
    return {
        "subject": subject,
        "body": body,
        "preview": preview[:200],
    }
