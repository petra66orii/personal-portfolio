from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from growth_ops.models import Lead, WebsiteReport

REASON_HAS_WEBSITE = "HAS_WEBSITE"
REASON_LOW_MOBILE_PERF = "LOW_MOBILE_PERFORMANCE"
REASON_HIGH_LCP = "HIGH_LCP"
REASON_CTA_POOR = "CTA_CLARITY_POOR"
REASON_SITEMAP_MISSING = "SITEMAP_MISSING"
REASON_TEMPLATE_LIMIT = "TEMPLATE_CMS_LIMITATION_SIGNAL"
REASON_CONTACT_EMAIL = "CONTACT_EMAIL_PRESENT"
REASON_INDUSTRY_FIT = "INDUSTRY_FIT"


@dataclass(frozen=True)
class ScoreResult:
    score: int
    bucket: str
    reason_codes: list[str]
    recommendation: dict[str, Any]


def _int_setting(name: str, default: int) -> int:
    raw = str(getattr(settings, name, os.getenv(name, default))).strip()
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _list_setting(name: str, default: list[str]) -> list[str]:
    setting_value = getattr(settings, name, None)
    if isinstance(setting_value, (list, tuple)):
        return [str(item).strip().lower() for item in setting_value if str(item).strip()]

    raw = os.getenv(name, "")
    if not raw:
        return [item.lower() for item in default]
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_performance_score(payload: Any) -> float | None:
    if not isinstance(payload, dict):
        return None

    candidates: list[Any] = [
        payload.get("performance_score"),
        payload.get("performance"),
        payload.get("mobile_performance_score"),
        ((payload.get("categories") or {}).get("performance") or {}).get("score"),
        ((payload.get("lighthouseResult") or {}).get("categories") or {}).get("performance", {}).get(
            "score"
        ),
    ]
    for value in candidates:
        parsed = _to_float(value)
        if parsed is None:
            continue
        if 0 <= parsed <= 1:
            return parsed * 100
        return parsed
    return None


def _extract_lcp_ms(payload: Any) -> float | None:
    if not isinstance(payload, dict):
        return None

    candidates: list[Any] = [
        payload.get("lcp_ms"),
        payload.get("largest_contentful_paint_ms"),
        ((payload.get("metrics") or {}).get("lcp") or {}).get("value_ms"),
        ((payload.get("audits") or {}).get("largest-contentful-paint") or {}).get("numericValue"),
        (
            ((payload.get("lighthouseResult") or {}).get("audits") or {}).get("largest-contentful-paint")
            or {}
        ).get("numericValue"),
    ]
    for value in candidates:
        parsed = _to_float(value)
        if parsed is not None:
            return parsed
    return None


def _is_cta_clarity_poor(report_obj: WebsiteReport | None) -> bool:
    if report_obj is None:
        return False

    payload = report_obj.report
    if not isinstance(payload, dict):
        return False

    cta_value = str(payload.get("cta_clarity", "")).strip().lower()
    if cta_value in {"poor", "missing", "unclear", "weak"}:
        return True

    findings = payload.get("findings")
    if not isinstance(findings, list):
        return False

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        combined = " ".join(
            [
                str(finding.get("title", "")),
                str(finding.get("diagnosis", "")),
                str(finding.get("business_impact", "")),
            ]
        ).lower()
        if "cta" in combined and any(word in combined for word in ("unclear", "missing", "weak", "confusing")):
            return True
    return False


def compute_lead_score(*, lead: Lead, report_obj: WebsiteReport | None = None) -> ScoreResult:
    performance_threshold = _int_setting("LEAD_SCORE_LIGHTHOUSE_THRESHOLD", 70)
    lcp_threshold_ms = _int_setting("LEAD_SCORE_LCP_THRESHOLD_MS", 2500)
    bucket_a_min = _int_setting("LEAD_SCORE_BUCKET_A_MIN", 70)
    bucket_b_min = _int_setting("LEAD_SCORE_BUCKET_B_MIN", 45)

    fit_industries = _list_setting(
        "LEAD_SCORE_FIT_INDUSTRIES",
        [
            "construction",
            "legal",
            "medical",
            "finance",
            "real estate",
            "ecommerce",
            "hospitality",
            "saas",
        ],
    )
    template_cms = set(
        _list_setting(
            "LEAD_SCORE_TEMPLATE_CMS",
            ["wordpress", "wix", "squarespace", "shopify", "webflow"],
        )
    )

    reason_codes: list[str] = []
    score = 0

    if lead.website_url:
        score += 20
        reason_codes.append(REASON_HAS_WEBSITE)

    if lead.contacts.exclude(email="").exists():
        score += 10
        reason_codes.append(REASON_CONTACT_EMAIL)

    industry = (lead.industry or "").lower()
    if industry and any(keyword in industry for keyword in fit_industries):
        score += 5
        reason_codes.append(REASON_INDUSTRY_FIT)

    evidence_qs = lead.website_evidence.all()

    perf_score: float | None = None
    lcp_ms: float | None = None
    cms_value = ""
    has_sitemap_evidence = False
    sitemap_marked_missing = False

    for evidence in evidence_qs:
        if evidence.evidence_type == "sitemap_xml":
            has_sitemap_evidence = True
            payload = evidence.payload
            if isinstance(payload, dict):
                if payload.get("exists") is False:
                    sitemap_marked_missing = True
                status_code = payload.get("status_code")
                if status_code in {404, 410}:
                    sitemap_marked_missing = True

        payload = evidence.payload
        if perf_score is None:
            perf_score = _extract_performance_score(payload)
        if lcp_ms is None:
            lcp_ms = _extract_lcp_ms(payload)

        if evidence.evidence_type == "tech_fingerprint" and isinstance(payload, dict):
            cms_value = str(
                payload.get("cms") or payload.get("platform") or payload.get("builder") or ""
            ).lower()

    if perf_score is not None and perf_score < performance_threshold:
        score += 20
        reason_codes.append(REASON_LOW_MOBILE_PERF)

    if lcp_ms is not None and lcp_ms > lcp_threshold_ms:
        score += 15
        reason_codes.append(REASON_HIGH_LCP)

    if _is_cta_clarity_poor(report_obj):
        score += 10
        reason_codes.append(REASON_CTA_POOR)

    if not has_sitemap_evidence or sitemap_marked_missing:
        score += 10
        reason_codes.append(REASON_SITEMAP_MISSING)

    if cms_value and any(cms in cms_value for cms in template_cms):
        score += 10
        reason_codes.append(REASON_TEMPLATE_LIMIT)

    score = max(0, min(int(score), 100))

    if score >= bucket_a_min:
        bucket = "A"
        recommendation = {
            "offer_type": "paid_discovery",
            "label": "Pitch paid discovery",
            "priority": "high",
        }
    elif score >= bucket_b_min:
        bucket = "B"
        recommendation = {
            "offer_type": "free_loom_or_performance_sprint",
            "label": "Pitch free Loom/performance sprint",
            "priority": "medium",
        }
    else:
        bucket = "C"
        recommendation = {
            "offer_type": "skip_low_priority",
            "label": "Skip / low priority",
            "priority": "low",
        }

    # Preserve stable reason ordering and remove accidental duplicates.
    deduped_reasons = list(dict.fromkeys(reason_codes))
    return ScoreResult(
        score=score,
        bucket=bucket,
        reason_codes=deduped_reasons,
        recommendation=recommendation,
    )
