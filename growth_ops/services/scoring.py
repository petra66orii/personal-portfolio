from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from django.conf import settings

from growth_ops.models import Lead, WebsiteReport

REASON_HAS_WEBSITE = "HAS_WEBSITE"
REASON_LOW_MOBILE_PERF = "LOW_MOBILE_PERFORMANCE"
REASON_MOBILE_PERF_NEEDS_IMPROVEMENT = "MOBILE_PERFORMANCE_NEEDS_IMPROVEMENT"
REASON_HIGH_MOBILE_PERF = "HIGH_MOBILE_PERFORMANCE"
REASON_HIGH_LCP = "HIGH_LCP"
REASON_FAST_LCP = "FAST_LCP"
REASON_CTA_POOR = "CTA_CLARITY_POOR"
REASON_CTA_MODERATE = "CTA_CLARITY_MODERATE"
REASON_NO_VISIBLE_CONTACT_METHOD = "NO_VISIBLE_CONTACT_METHOD"
REASON_NO_HTTPS = "NO_HTTPS"
REASON_SITEMAP_MISSING = "SITEMAP_MISSING"
REASON_TEMPLATE_LIMIT = "TEMPLATE_CMS_LIMITATION_SIGNAL"
REASON_TRUST_LOW = "TRUST_SIGNALS_WEAK"
REASON_TRUST_STRONG = "TRUST_SIGNALS_STRONG"
REASON_CONTACT_EMAIL = "CONTACT_EMAIL_PRESENT"
REASON_INDUSTRY_FIT = "INDUSTRY_FIT"
# Calibrated for outreach operations:
# A: strongest opportunity, B: worth contacting, C: skip for now.
OUTREACH_BUCKET_A_MIN = 70
OUTREACH_BUCKET_B_MIN = 35


@dataclass(frozen=True)
class ScoreResult:
    score: int
    bucket: str
    reason_codes: list[str]
    recommendation: dict[str, Any]


def _normalize_score_0_100(value: Any) -> int:
    parsed = _to_float(value)
    if parsed is None:
        return 0
    return max(0, min(int(round(parsed)), 100))


def bucket_for_outreach_score(score: int) -> str:
    normalized = _normalize_score_0_100(score)
    if normalized >= OUTREACH_BUCKET_A_MIN:
        return "A"
    if normalized >= OUTREACH_BUCKET_B_MIN:
        return "B"
    return "C"


def priority_for_bucket(bucket: str) -> str:
    normalized = str(bucket or "").strip().upper()
    if normalized == "A":
        return "high"
    if normalized == "B":
        return "medium"
    return "low"


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


def _report_payload(report_obj: WebsiteReport | None) -> dict[str, Any]:
    if report_obj is None:
        return {}
    payload = report_obj.report
    return payload if isinstance(payload, dict) else {}


def _extract_cta_clarity(report_obj: WebsiteReport | None) -> str:
    payload = _report_payload(report_obj)
    cta_value = str(payload.get("cta_clarity", "")).strip().lower()
    if cta_value in {"clear", "moderate", "weak", "missing", "unclear", "poor"}:
        return cta_value

    findings = payload.get("findings")
    if not isinstance(findings, list):
        return ""

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
        if "cta" in combined:
            if any(word in combined for word in ("unclear", "missing", "weak", "confusing", "poor")):
                return "weak"
            if "moderate" in combined:
                return "moderate"
    return ""


def _extract_report_performance_score(report_obj: WebsiteReport | None) -> float | None:
    payload = _report_payload(report_obj)
    return _to_float((payload.get("performance") or {}).get("score"))


def _extract_report_lcp_ms(report_obj: WebsiteReport | None) -> float | None:
    payload = _report_payload(report_obj)
    return _to_float((payload.get("performance") or {}).get("lcp_ms"))


def _extract_report_trust_ratio(report_obj: WebsiteReport | None) -> float | None:
    payload = _report_payload(report_obj)
    trust_payload = payload.get("trust")
    if not isinstance(trust_payload, dict):
        return None
    score = _to_float(trust_payload.get("score"))
    max_score = _to_float(trust_payload.get("max_score"))
    if score is None or max_score is None or max_score <= 0:
        return None
    ratio = score / max_score
    return max(0.0, min(ratio, 1.0))


def _extract_site_type(report_obj: WebsiteReport | None) -> str:
    payload = _report_payload(report_obj)
    raw_value = str(payload.get("site_type") or "").strip().lower()
    if raw_value in {"institutional", "chain", "local"}:
        return raw_value
    technical = payload.get("technical")
    if isinstance(technical, dict):
        fallback = str(technical.get("site_type") or "").strip().lower()
        if fallback in {"institutional", "chain", "local"}:
            return fallback
    return "local"


def _extract_trust_rating(report_obj: WebsiteReport | None) -> str:
    payload = _report_payload(report_obj)
    trust = payload.get("trust")
    if not isinstance(trust, dict):
        return "moderate"
    rating = str(trust.get("rating") or "").strip().lower()
    if rating in {"weak", "moderate", "strong"}:
        return rating

    ratio = _extract_report_trust_ratio(report_obj)
    if ratio is None:
        return "moderate"
    if ratio >= 0.8:
        return "strong"
    if ratio >= 0.4:
        return "moderate"
    return "weak"


def _extract_has_contact_method(report_obj: WebsiteReport | None) -> bool | None:
    payload = _report_payload(report_obj)
    cta = payload.get("cta")
    if isinstance(cta, dict):
        value = cta.get("has_contact_method")
        if isinstance(value, bool):
            return value
    trust = payload.get("trust")
    if isinstance(trust, dict):
        value = trust.get("has_contact_info")
        if isinstance(value, bool):
            return value
    return None


def _extract_has_https(report_obj: WebsiteReport | None, lead: Lead) -> bool | None:
    payload = _report_payload(report_obj)
    technical = payload.get("technical")
    if isinstance(technical, dict):
        value = technical.get("has_https")
        if isinstance(value, bool):
            return value
    website_url = str(lead.website_url or "").strip().lower()
    if website_url:
        return website_url.startswith("https://")
    return None


def _cta_weight_for_site_type(site_type: str) -> dict[str, int]:
    if site_type == "institutional":
        return {"missing": -10, "weak": -7, "moderate": -3, "clear": 1}
    if site_type == "chain":
        return {"missing": -13, "weak": -9, "moderate": -4, "clear": 2}
    return {"missing": -15, "weak": -10, "moderate": -5, "clear": 2}


def _trust_weight_for_site_type(site_type: str) -> dict[str, int]:
    if site_type == "institutional":
        return {"weak": -8, "moderate": 0, "strong": 4}
    if site_type == "chain":
        return {"weak": -10, "moderate": 0, "strong": 3}
    return {"weak": -10, "moderate": 0, "strong": 2}


def compute_lead_score(*, lead: Lead, report_obj: WebsiteReport | None = None) -> ScoreResult:
    performance_threshold = _int_setting("LEAD_SCORE_LIGHTHOUSE_THRESHOLD", 70)
    lcp_threshold_ms = _int_setting("LEAD_SCORE_LCP_THRESHOLD_MS", 3000)

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
    score = 50

    if lead.website_url:
        score += 5
        reason_codes.append(REASON_HAS_WEBSITE)

    if lead.contacts.exclude(email="").exists():
        score += 3
        reason_codes.append(REASON_CONTACT_EMAIL)

    industry = (lead.industry or "").lower()
    if industry and any(keyword in industry for keyword in fit_industries):
        score += 2
        reason_codes.append(REASON_INDUSTRY_FIT)

    site_type = _extract_site_type(report_obj)

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

    report_perf_score = _extract_report_performance_score(report_obj)
    if report_perf_score is not None:
        perf_score = report_perf_score if perf_score is None else min(perf_score, report_perf_score)

    report_lcp_ms = _extract_report_lcp_ms(report_obj)
    if report_lcp_ms is not None:
        lcp_ms = report_lcp_ms if lcp_ms is None else max(lcp_ms, report_lcp_ms)

    if perf_score is not None and perf_score < performance_threshold:
        score -= 16
        reason_codes.append(REASON_LOW_MOBILE_PERF)
    elif perf_score is not None and perf_score < 90:
        score -= 5
        reason_codes.append(REASON_MOBILE_PERF_NEEDS_IMPROVEMENT)
    elif perf_score is not None:
        score += 6
        reason_codes.append(REASON_HIGH_MOBILE_PERF)

    if lcp_ms is not None and lcp_ms > lcp_threshold_ms:
        score -= 10
        reason_codes.append(REASON_HIGH_LCP)
    elif lcp_ms is not None and lcp_ms < 1500:
        score += 3
        reason_codes.append(REASON_FAST_LCP)

    cta_clarity = _extract_cta_clarity(report_obj)
    cta_weights = _cta_weight_for_site_type(site_type)
    if cta_clarity in {"poor", "missing", "unclear"}:
        score += cta_weights["missing"]
        reason_codes.append(REASON_CTA_POOR)
    elif cta_clarity == "moderate":
        score += cta_weights["moderate"]
        reason_codes.append(REASON_CTA_MODERATE)
    elif cta_clarity == "weak":
        score += cta_weights["weak"]
        reason_codes.append(REASON_CTA_POOR)
    elif cta_clarity == "clear":
        score += cta_weights["clear"]

    has_contact_method = _extract_has_contact_method(report_obj)
    if has_contact_method is False:
        if site_type == "institutional":
            score -= 6
        elif site_type == "chain":
            score -= 7
        else:
            score -= 8
        reason_codes.append(REASON_NO_VISIBLE_CONTACT_METHOD)

    has_https = _extract_has_https(report_obj, lead)
    if has_https is False:
        if site_type == "institutional":
            score -= 8
        elif site_type == "chain":
            score -= 9
        else:
            score -= 10
        reason_codes.append(REASON_NO_HTTPS)

    if not has_sitemap_evidence or sitemap_marked_missing:
        score -= 8
        reason_codes.append(REASON_SITEMAP_MISSING)

    if cms_value and any(cms in cms_value for cms in template_cms):
        score -= 5
        reason_codes.append(REASON_TEMPLATE_LIMIT)

    trust_rating = _extract_trust_rating(report_obj)
    trust_weights = _trust_weight_for_site_type(site_type)
    if trust_rating == "weak":
        score += trust_weights["weak"]
        reason_codes.append(REASON_TRUST_LOW)
    elif trust_rating == "moderate":
        score += trust_weights["moderate"]
    elif trust_rating == "strong":
        score += trust_weights["strong"]
        reason_codes.append(REASON_TRUST_STRONG)

    quality_score = _normalize_score_0_100(score)
    outreach_score = 100 - quality_score
    bucket = bucket_for_outreach_score(outreach_score)
    priority = priority_for_bucket(bucket)

    if bucket == "A":
        recommendation = {
            "offer_type": "aggressive_outreach",
            "label": "Aggressive outreach",
            "priority": priority,
            "outreach_mode": "aggressive",
            "score_semantics": "outreach_opportunity",
            "outreach_score": outreach_score,
            # Alias retained for backward compatibility.
            "opportunity_score": outreach_score,
            "quality_score": quality_score,
        }
    elif bucket == "B":
        recommendation = {
            "offer_type": "moderate_outreach",
            "label": "Moderate outreach",
            "priority": priority,
            "outreach_mode": "moderate",
            "score_semantics": "outreach_opportunity",
            "outreach_score": outreach_score,
            "opportunity_score": outreach_score,
            "quality_score": quality_score,
        }
    else:
        recommendation = {
            "offer_type": "low_priority",
            "label": "Low priority",
            "priority": priority,
            "outreach_mode": "low",
            "score_semantics": "outreach_opportunity",
            "outreach_score": outreach_score,
            "opportunity_score": outreach_score,
            "quality_score": quality_score,
        }

    # Preserve stable reason ordering and remove accidental duplicates.
    deduped_reasons = list(dict.fromkeys(reason_codes))
    return ScoreResult(
        score=outreach_score,
        bucket=bucket,
        reason_codes=deduped_reasons,
        recommendation=recommendation,
    )
