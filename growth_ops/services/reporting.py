from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlparse

from django.db import transaction

from growth_ops.models import Lead, WebsiteEvidence, WebsiteReport

RULES_REPORT_MODEL = "rules_v1"
RULES_REPORT_PROMPT_VERSION = "growth_report_v2_rules_1"
LOW_PERFORMANCE_THRESHOLD = 70.0
HIGH_LCP_THRESHOLD_MS = 2500.0
SEO_TITLE_MIN_LENGTH = 30
SEO_TITLE_MAX_LENGTH = 60
SEO_META_MIN_LENGTH = 70
SEO_META_MAX_LENGTH = 160
MAX_FINDINGS = 5
TEMPLATE_CMS_SIGNALS = {"wordpress", "wix", "squarespace", "shopify", "webflow"}
CTA_KEYWORDS = [
    "contact",
    "book",
    "join",
    "get started",
    "call",
    "email",
    "quote",
    "start",
    "schedule",
    "enquire",
    "inquiry",
]
PLATFORM_MARKERS = {
    "wp-content": "wordpress",
    "shopify": "shopify",
    "squarespace": "squarespace",
    "webflow": "webflow",
    "wix": "wix",
}
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1\b[^>]*>.*?</h1>", re.IGNORECASE | re.DOTALL)
META_DESCRIPTION_RE = re.compile(
    r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
    re.IGNORECASE | re.DOTALL,
)
META_DESCRIPTION_RE_ALT = re.compile(
    r'<meta\b[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\'][^>]*>',
    re.IGNORECASE | re.DOTALL,
)
CANONICAL_RE = re.compile(
    r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE | re.DOTALL,
)
CANONICAL_RE_ALT = re.compile(
    r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\'][^>]*>',
    re.IGNORECASE | re.DOTALL,
)
PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)")
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
FORM_RE = re.compile(r"<form\b[^>]*>", re.IGNORECASE)
TESTIMONIAL_RE = re.compile(r"\b(testimonial|testimonials|review|reviews|client stories)\b", re.IGNORECASE)
TEAM_RE = re.compile(r"\b(about us|our team|meet the team|our story|who we are)\b", re.IGNORECASE)
ADDRESS_RE = re.compile(r"\b(address|street|road|avenue|galway|dublin|ireland|location)\b", re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript>", re.IGNORECASE | re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
MULTISPACE_RE = re.compile(r"\s+")
H1_TEXT_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
HEADING_RE = re.compile(r"<h[1-6]\b[^>]*>.*?</h[1-6]>", re.IGNORECASE | re.DOTALL)
SECTION_RE = re.compile(r"<section\b[^>]*>", re.IGNORECASE)
CTA_ACTION_BLOCK_RE = re.compile(r"<(a|button)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
INSTITUTIONAL_RE = re.compile(r"\b(university|award|certified|official|since)\b", re.IGNORECASE)
PRICING_RE = re.compile(
    r"(€\s?\d+|pricing|price|starting at|from\s+€|per\s+month|/month)",
    re.IGNORECASE,
)
LOCATION_CLUSTER_RE = re.compile(
    r"\b(locations|clubs|branches|find a location|our locations|multiple locations)\b",
    re.IGNORECASE,
)
FINDING_SEVERITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
BUSINESS_IMPACT_KEYWORDS = {
    "revenue": 3,
    "conversion": 3,
    "leads": 3,
    "sales": 3,
    "booking": 2,
    "pipeline": 2,
    "trust": 2,
    "engagement": 1,
    "seo": 1,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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
        ((payload.get("lighthouseResult") or {}).get("categories") or {}).get("performance", {}).get("score"),
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


def _normalize_evidence_ids(evidence_ids: list[int | str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in evidence_ids:
        parsed = str(value).strip()
        if not parsed or parsed in seen:
            continue
        seen.add(parsed)
        out.append(parsed)
    return out


def _find_matching_report(
    *,
    lead: Lead,
    model: str,
    prompt_version: str,
    evidence_ids: list[str],
    report_payload: Any,
    summary: str,
) -> WebsiteReport | None:
    recent_reports = lead.website_reports.filter(
        model=model,
        prompt_version=prompt_version,
    ).order_by("-created_at")[:25]
    target_report = _canonical_json(report_payload)
    target_evidence_ids = list(evidence_ids)
    for report in recent_reports:
        if (
            list(report.evidence_ids or []) == target_evidence_ids
            and _canonical_json(report.report) == target_report
            and (report.summary or "") == summary
        ):
            return report
    return None


def validate_evidence_ids_for_lead(lead: Lead, evidence_ids: list[Any]) -> list[int]:
    numeric_ids: set[int] = set()
    for item in evidence_ids:
        try:
            numeric_ids.add(int(item))
        except (TypeError, ValueError):
            continue
    if not numeric_ids:
        return []

    existing_ids = set(lead.website_evidence.filter(id__in=numeric_ids).values_list("id", flat=True))
    return sorted(numeric_ids - existing_ids)


def get_latest_evidence_for_lead(lead: Lead) -> list[WebsiteEvidence]:
    """
    Return latest evidence rows per `(evidence_type, url, tool)` group.
    This keeps report generation deterministic and avoids stale duplicates.
    """
    queryset = lead.website_evidence.order_by("-created_at", "-id")
    seen_keys: set[tuple[str, str, str]] = set()
    selected: list[WebsiteEvidence] = []

    for evidence in queryset:
        key = (
            evidence.evidence_type,
            evidence.url or "",
            evidence.tool or "",
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        selected.append(evidence)

    return sorted(selected, key=lambda item: item.id)


def _latest_evidence_by_type(evidence: list[WebsiteEvidence], evidence_type: str) -> WebsiteEvidence | None:
    candidates = [item for item in evidence if item.evidence_type == evidence_type]
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.created_at, item.id))


def _evidence_exists(evidence_obj: WebsiteEvidence | None) -> bool:
    if evidence_obj is None:
        return False
    payload = evidence_obj.payload if isinstance(evidence_obj.payload, dict) else {}
    if payload.get("exists") is False:
        return False
    status_code_raw = payload.get("status_code")
    status_code: int | None
    try:
        status_code = int(status_code_raw) if status_code_raw is not None else None
    except (TypeError, ValueError):
        status_code = None
    if status_code in {404, 410}:
        return False
    if payload.get("exists") is True:
        return True
    return status_code is not None and 200 <= status_code < 400


def _strip_html_for_signal_analysis(html: str) -> str:
    cleaned = SCRIPT_RE.sub(" ", html or "")
    cleaned = STYLE_RE.sub(" ", cleaned)
    cleaned = NOSCRIPT_RE.sub(" ", cleaned)
    cleaned = HTML_COMMENT_RE.sub(" ", cleaned)
    cleaned = TAG_RE.sub(" ", cleaned)
    return MULTISPACE_RE.sub(" ", cleaned).strip()


def _extract_h1_texts(homepage_html: str) -> list[str]:
    values: list[str] = []
    for match in H1_TEXT_RE.findall(homepage_html):
        stripped = TAG_RE.sub(" ", match)
        normalized = MULTISPACE_RE.sub(" ", stripped).strip()
        if normalized:
            values.append(normalized)
    return values


def _extract_domain_token(domain_or_url: str) -> str:
    raw = (domain_or_url or "").strip().lower()
    if not raw:
        return ""
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.netloc or parsed.path or "").split("@")[-1]
    host = host.split(":")[0]
    host = host.removeprefix("www.")
    if not host:
        return ""
    parts = [part for part in host.split(".") if part]
    if len(parts) >= 2:
        return parts[-2]
    return parts[0]


def _dom_depth_until(html: str, position: int) -> int:
    depth = 0
    for token in re.finditer(r"<(/?)([a-zA-Z0-9]+)(?:\s[^>]*)?>", html[: max(position, 0)]):
        raw_tag = token.group(0)
        is_closing = token.group(1) == "/"
        is_self_closing = raw_tag.endswith("/>")
        if is_closing:
            depth = max(0, depth - 1)
            continue
        if not is_self_closing:
            depth += 1
    return max(depth, 1)


def _count_keyword_hits(text: str, keywords: list[str]) -> tuple[int, float | None]:
    normalized = (text or "").lower()
    text_len = max(len(normalized), 1)
    total_hits = 0
    first_pos: float | None = None

    for keyword in keywords:
        pattern = re.compile(rf"\b{re.escape(keyword.lower())}\b")
        matches = list(pattern.finditer(normalized))
        if not matches:
            continue
        total_hits += len(matches)
        hit_pos = matches[0].start() / text_len
        if first_pos is None or hit_pos < first_pos:
            first_pos = hit_pos

    return total_hits, first_pos


def _cta_position_label(first_cta_position: float | None) -> str:
    if first_cta_position is None:
        return "missing"
    if first_cta_position <= 0.35:
        return "early"
    if first_cta_position <= 0.70:
        return "mid"
    return "late"


def _derive_cta_signals(homepage_payload: dict[str, Any]) -> dict[str, Any]:
    body_html = str(homepage_payload.get("body") or "")
    exists = bool(homepage_payload.get("exists", False))
    if not exists or not body_html:
        return {
            "clarity": "missing",
            "keyword_hits": 0,
            "first_cta_position": "missing",
            "has_phone": False,
            "has_email": False,
            "has_form": False,
            "has_contact_method": False,
            "action_elements_count": 0,
            "pricing_detected": False,
            "multiple_ctas": False,
            "visual_cta_density": 0.0,
        }

    visible_text = _strip_html_for_signal_analysis(body_html)
    keyword_hits, first_cta_ratio = _count_keyword_hits(visible_text, CTA_KEYWORDS)
    first_cta_position_ratio = first_cta_ratio

    has_phone = bool(PHONE_RE.search(visible_text))
    has_email = bool(EMAIL_RE.search(visible_text))
    has_form = bool(FORM_RE.search(body_html))
    has_contact_method = has_phone or has_email or has_form

    body_length = max(len(body_html), 1)
    hero_length = max(1, int(body_length * 0.35))
    hero_html = body_html[:hero_length]
    hero_text = _strip_html_for_signal_analysis(hero_html)
    pricing_detected = bool(PRICING_RE.search(hero_html) or PRICING_RE.search(hero_text))

    action_elements_count = 0
    action_elements_above_fold = 0
    cta_depth_sum = 0.0
    first_action_ratio: float | None = None
    for match in CTA_ACTION_BLOCK_RE.finditer(body_html):
        attrs = (match.group(2) or "").lower()
        action_body = match.group(3) or ""
        action_text = MULTISPACE_RE.sub(" ", TAG_RE.sub(" ", action_body)).strip().lower()
        combined = f"{attrs} {action_text}".strip()
        if not combined:
            continue

        is_cta_intent = any(
            re.search(rf"\b{re.escape(keyword.lower())}\b", combined)
            for keyword in CTA_KEYWORDS
        ) or any(token in combined for token in ("mailto:", "tel:", "btn", "cta", "pricing", "price"))
        if not is_cta_intent:
            continue

        action_elements_count += 1
        start_ratio = match.start() / body_length
        if first_action_ratio is None or start_ratio < first_action_ratio:
            first_action_ratio = start_ratio
        if start_ratio <= 0.35:
            action_elements_above_fold += 1

        depth = _dom_depth_until(body_html, match.start())
        cta_depth_sum += float(depth)

    if first_action_ratio is not None:
        if first_cta_position_ratio is None:
            first_cta_position_ratio = first_action_ratio
        else:
            first_cta_position_ratio = min(first_cta_position_ratio, first_action_ratio)

    first_cta_position = _cta_position_label(first_cta_position_ratio)
    multiple_ctas = action_elements_above_fold >= 2
    avg_depth = cta_depth_sum / action_elements_count if action_elements_count else 1.0
    visual_cta_density = round(float(action_elements_count) / max(avg_depth, 1.0), 3)

    if keyword_hits >= 2 and (has_contact_method or pricing_detected or action_elements_count >= 2) and first_cta_position == "early":
        clarity = "clear"
    elif keyword_hits >= 1 and (action_elements_count >= 1 or pricing_detected):
        clarity = "moderate"
    elif keyword_hits >= 1:
        clarity = "weak"
    elif keyword_hits == 0 and action_elements_count == 0:
        clarity = "missing"
    else:
        clarity = "weak"

    return {
        "clarity": clarity,
        "keyword_hits": keyword_hits,
        "first_cta_position": first_cta_position,
        "has_phone": has_phone,
        "has_email": has_email,
        "has_form": has_form,
        "has_contact_method": has_contact_method,
        "action_elements_count": action_elements_count,
        "pricing_detected": pricing_detected,
        "multiple_ctas": multiple_ctas,
        "visual_cta_density": visual_cta_density,
    }


def _extract_title_text(homepage_html: str) -> str:
    match = TITLE_RE.search(homepage_html)
    if not match:
        return ""
    return " ".join(match.group(1).split()).strip()


def _extract_meta_description(homepage_html: str) -> str:
    match = META_DESCRIPTION_RE.search(homepage_html) or META_DESCRIPTION_RE_ALT.search(homepage_html)
    if not match:
        return ""
    return " ".join(match.group(1).split()).strip()


def _extract_canonical_href(homepage_html: str) -> str:
    match = CANONICAL_RE.search(homepage_html) or CANONICAL_RE_ALT.search(homepage_html)
    if not match:
        return ""
    return match.group(1).strip()


def _resolve_canonical_mismatch(canonical_href: str, requested_url: str) -> bool:
    if not canonical_href:
        return False

    requested = (requested_url or "").strip()
    if not requested:
        return False

    requested_parsed = urlparse(requested if "://" in requested else f"https://{requested}")
    absolute_canonical = canonical_href
    if canonical_href.startswith("/"):
        absolute_canonical = urljoin(f"{requested_parsed.scheme}://{requested_parsed.netloc}", canonical_href)
    canonical_parsed = urlparse(
        absolute_canonical if "://" in absolute_canonical else f"{requested_parsed.scheme}://{requested_parsed.netloc}{absolute_canonical}"
    )
    if not canonical_parsed.netloc:
        return False
    return canonical_parsed.netloc.lower() != requested_parsed.netloc.lower()


def _performance_rating(score: float | None) -> str:
    if score is None:
        return "needs_improvement"
    if score >= 90:
        return "good"
    if score >= 50:
        return "needs_improvement"
    return "poor"


def _detect_platform_signals(homepage_payload: dict[str, Any], tech_payload: dict[str, Any]) -> tuple[str, list[str]]:
    cms = str(
        tech_payload.get("cms")
        or tech_payload.get("platform")
        or tech_payload.get("builder")
        or ""
    ).strip().lower()
    signals: list[str] = []
    if cms:
        signals.append(cms)

    homepage_body = str(homepage_payload.get("body") or "").lower()
    for marker, signal in PLATFORM_MARKERS.items():
        if marker in homepage_body and signal not in signals:
            signals.append(signal)

    return cms, signals


def _severity_for_cta(cta_clarity: str) -> str:
    if cta_clarity in {"missing", "unclear"}:
        return "high"
    if cta_clarity == "weak":
        return "medium"
    if cta_clarity == "moderate":
        return "low"
    return "low"


def _trust_rating(score: int, max_score: int) -> str:
    if max_score <= 0:
        return "weak"
    if score >= 4:
        return "strong"
    if score >= 2:
        return "moderate"
    return "weak"


def infer_site_type(homepage_html: str, title: str, domain: str) -> str:
    combined = f"{title or ''} {_strip_html_for_signal_analysis(homepage_html)} {domain or ''}".lower()
    if "university" in combined:
        return "institutional"

    location_hits = len(LOCATION_CLUSTER_RE.findall(combined))
    if location_hits >= 2:
        return "chain"
    return "local"


def _add_finding(
    findings: list[dict[str, Any]],
    seen: set[str],
    *,
    title: str,
    diagnosis: str,
    business_impact: str,
    severity: str,
) -> None:
    normalized_title = re.sub(r"\s+", " ", title.strip().lower())
    if not normalized_title or normalized_title in seen:
        return
    seen.add(normalized_title)
    findings.append(
        {
            "title": title.strip(),
            "diagnosis": diagnosis.strip(),
            "business_impact": business_impact.strip(),
            "severity": severity if severity in {"high", "medium", "low"} else "medium",
        }
    )


def _prioritize_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not findings:
        return []

    def impact_weight(finding: dict[str, Any]) -> int:
        text = str(finding.get("business_impact", "")).lower()
        score = 0
        for keyword, weight in BUSINESS_IMPACT_KEYWORDS.items():
            if keyword in text:
                score += weight
        return score

    ordered = sorted(
        findings,
        key=lambda item: (
            -FINDING_SEVERITY_WEIGHT.get(str(item.get("severity", "")).lower(), 0),
            -impact_weight(item),
            str(item.get("title", "")).lower(),
        ),
    )

    selected: list[dict[str, Any]] = []
    low_count = 0
    for finding in ordered:
        severity = str(finding.get("severity", "")).lower()
        if severity == "low" and low_count >= 2 and len(ordered) > 3:
            continue
        selected.append(finding)
        if severity == "low":
            low_count += 1
        if len(selected) >= MAX_FINDINGS:
            break
    return selected


def build_report_payload(*, lead: Lead, evidence: list[WebsiteEvidence]) -> dict[str, Any]:
    homepage = _latest_evidence_by_type(evidence, "homepage_html_snippet")
    robots = _latest_evidence_by_type(evidence, "robots_txt")
    sitemap = _latest_evidence_by_type(evidence, "sitemap_xml")
    tech = _latest_evidence_by_type(evidence, "tech_fingerprint")
    pagespeed = _latest_evidence_by_type(evidence, "pagespeed_json")

    perf_evidence = pagespeed
    perf_source = "pagespeed_json" if perf_evidence is not None else "not_available"
    if perf_evidence is None:
        perf_evidence = _latest_evidence_by_type(evidence, "lighthouse_json")
        perf_source = "lighthouse_json" if perf_evidence is not None else "not_available"

    homepage_payload: dict[str, Any] = {}
    if homepage is not None and isinstance(homepage.payload, dict):
        homepage_payload = homepage.payload
    tech_payload: dict[str, Any] = {}
    if tech is not None and isinstance(tech.payload, dict):
        tech_payload = tech.payload
    perf_payload: dict[str, Any] = {}
    if perf_evidence is not None and isinstance(perf_evidence.payload, dict):
        perf_payload = perf_evidence.payload

    has_robots = _evidence_exists(robots)
    has_sitemap = _evidence_exists(sitemap)
    homepage_html = str(homepage_payload.get("body") or "")
    homepage_requested_url = str(homepage_payload.get("requested_url") or lead.website_url or "")
    homepage_text = _strip_html_for_signal_analysis(homepage_html)

    title_text = _extract_title_text(homepage_html)
    title_length = len(title_text)
    meta_description = _extract_meta_description(homepage_html)
    meta_description_length = len(meta_description)
    h1_texts = _extract_h1_texts(homepage_html)
    h1_count = len(h1_texts)
    unique_h1_count = len({value.lower() for value in h1_texts})
    has_h1 = h1_count > 0
    canonical_href = _extract_canonical_href(homepage_html)
    has_canonical = bool(canonical_href)
    canonical_mismatch = _resolve_canonical_mismatch(canonical_href, homepage_requested_url)

    cta_signals = _derive_cta_signals(homepage_payload)
    cta_clarity = str(cta_signals["clarity"])
    has_phone = bool(cta_signals["has_phone"])
    has_email = bool(cta_signals["has_email"])
    has_contact_form = bool(cta_signals["has_form"])
    has_any_contact_method = bool(cta_signals["has_contact_method"])
    has_contact_info = has_phone or has_email

    has_testimonials = bool(TESTIMONIAL_RE.search(homepage_text))
    has_about_section = bool(TEAM_RE.search(homepage_text))
    has_address = bool(ADDRESS_RE.search(homepage_text))
    if not has_address and (lead.location or "").strip():
        has_address = (lead.location or "").strip().lower() in homepage_text.lower()

    has_institutional_signal = bool(INSTITUTIONAL_RE.search(homepage_text))
    heading_count = len(HEADING_RE.findall(homepage_html))
    section_count = len(SECTION_RE.findall(homepage_html))
    content_depth_score = min(5, (heading_count // 2) + (section_count // 2))
    if len(homepage_text) > 2000:
        content_depth_score = min(5, content_depth_score + 1)

    brand_tokens = []
    company_name = (lead.company_name or "").strip().lower()
    if company_name:
        brand_tokens.extend([token for token in re.split(r"[^a-z0-9]+", company_name) if len(token) >= 4])
    domain_token = _extract_domain_token(homepage_requested_url or lead.website_url)
    if domain_token and len(domain_token) >= 4:
        brand_tokens.append(domain_token)
    normalized_brand_tokens = list(dict.fromkeys(brand_tokens))
    brand_mention_count = 0
    for token in normalized_brand_tokens:
        brand_mention_count = max(brand_mention_count, len(re.findall(rf"\b{re.escape(token)}\b", homepage_text.lower())))

    structured_sections = heading_count >= 4 or section_count >= 3
    has_brand_signal = brand_mention_count >= 2 or structured_sections

    inferred_site_type = infer_site_type(homepage_html, title_text, homepage_requested_url or lead.website_url or "")

    cms, platform_signals = _detect_platform_signals(homepage_payload, tech_payload)
    has_https = str(lead.website_url or "").strip().lower().startswith("https://")

    if perf_source == "pagespeed_json":
        performance_score = _to_float(perf_payload.get("performance_score"))
        lcp_ms = _to_float(perf_payload.get("lcp_ms"))
        cls = _to_float(perf_payload.get("cls"))
        fcp_ms = _to_float(perf_payload.get("fcp_ms"))
        tbt_ms = _to_float(perf_payload.get("tbt_ms"))
    else:
        performance_score = _extract_performance_score(perf_payload)
        lcp_ms = _extract_lcp_ms(perf_payload)
        cls = _to_float(perf_payload.get("cls"))
        fcp_ms = _to_float(perf_payload.get("fcp_ms"))
        tbt_ms = _to_float(perf_payload.get("tbt_ms"))
    performance_rating = _performance_rating(performance_score)

    trust_score = (
        int(has_testimonials)
        + int(has_about_section)
        + int(has_address)
        + int(has_institutional_signal)
        + int(has_brand_signal or content_depth_score >= 3)
    )
    trust_max_score = 5
    trust_rating = _trust_rating(trust_score, trust_max_score)

    seo_issues: list[str] = []
    technical_issues: list[str] = []
    trust_issues: list[str] = []
    findings: list[dict[str, Any]] = []
    finding_titles_seen: set[str] = set()

    if not has_robots:
        seo_issues.append("robots.txt missing or inaccessible")
        _add_finding(
            findings,
            finding_titles_seen,
            title="robots.txt missing or inaccessible",
            diagnosis="Search crawlers do not have a clear robots policy endpoint.",
            business_impact="Crawl behavior is less predictable, which can reduce SEO control.",
            severity="medium",
        )

    if not has_sitemap:
        seo_issues.append("sitemap.xml missing or inaccessible")
        _add_finding(
            findings,
            finding_titles_seen,
            title="sitemap.xml missing or inaccessible",
            diagnosis="No reliable sitemap endpoint was detected from collected evidence.",
            business_impact="Index discovery can be slower, especially for deep content structures.",
            severity="medium",
        )

    has_title = bool(title_text)
    has_meta_description = bool(meta_description)
    if not has_title:
        seo_issues.append("Homepage title tag missing")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Homepage title tag missing",
            diagnosis="No <title> tag was detected in homepage HTML.",
            business_impact="Missing titles reduce click-through and weaken SEO relevance signals.",
            severity="high",
        )
    elif title_length < SEO_TITLE_MIN_LENGTH or title_length > SEO_TITLE_MAX_LENGTH:
        seo_issues.append("Homepage title length is outside ideal range (30-60 chars)")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Homepage title length is outside ideal range",
            diagnosis=f"Detected title length: {title_length} characters (ideal: 30-60).",
            business_impact="Suboptimal titles can reduce search click-through and relevance clarity.",
            severity="medium" if title_length < 20 or title_length > 70 else "low",
        )

    if not has_meta_description:
        seo_issues.append("Meta description missing")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Meta description missing",
            diagnosis="No <meta name=\"description\"> tag was detected.",
            business_impact="Search snippets are less controllable, which may reduce qualified clicks.",
            severity="medium",
        )
    elif meta_description_length < SEO_META_MIN_LENGTH or meta_description_length > SEO_META_MAX_LENGTH:
        seo_issues.append("Meta description length is outside ideal range")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Meta description length is outside ideal range",
            diagnosis=f"Detected meta description length: {meta_description_length} characters (ideal: {SEO_META_MIN_LENGTH}-{SEO_META_MAX_LENGTH}).",
            business_impact="Weak or overlong descriptions can reduce qualified search traffic.",
            severity="low",
        )

    if not has_h1:
        seo_issues.append("Homepage H1 missing")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Homepage H1 missing",
            diagnosis="No <h1> heading was detected on homepage.",
            business_impact="Weak heading hierarchy can reduce both clarity and SEO quality signals.",
            severity="medium",
        )
    elif unique_h1_count > 1:
        seo_issues.append("Multiple distinct H1 headings detected")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Multiple distinct H1 headings detected",
            diagnosis=f"Detected {h1_count} H1 tags with {unique_h1_count} distinct values.",
            business_impact="Mixed primary headings can dilute page focus for users and search engines.",
            severity="medium",
        )

    if not has_canonical:
        seo_issues.append("Canonical link missing")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Canonical link missing",
            diagnosis="No canonical URL was found in homepage head metadata.",
            business_impact="Duplicate URL variants can dilute indexing and ranking consistency.",
            severity="low",
        )

    if cta_clarity in {"missing", "weak", "unclear"}:
        _add_finding(
            findings,
            finding_titles_seen,
            title="No clear call-to-action on homepage" if cta_clarity == "missing" else "Homepage call-to-action is weak",
            diagnosis=(
                f"CTA classified as '{cta_clarity}' "
                f"(hits={cta_signals['keyword_hits']}, first_position={cta_signals['first_cta_position']}, action_count={cta_signals['action_elements_count']})."
            ),
            business_impact="Visitors may not find a confident next step, reducing conversion potential.",
            severity=_severity_for_cta(cta_clarity),
        )
    elif cta_clarity == "moderate":
        _add_finding(
            findings,
            finding_titles_seen,
            title="CTA clarity is moderate",
            diagnosis=(
                f"CTA appears present but not consistently strong "
                f"(hits={cta_signals['keyword_hits']}, first_position={cta_signals['first_cta_position']}, pricing_detected={cta_signals['pricing_detected']})."
            ),
            business_impact="Users may hesitate before converting, especially on first visit.",
            severity="low",
        )

    if not has_any_contact_method:
        _add_finding(
            findings,
            finding_titles_seen,
            title="No visible contact method on homepage",
            diagnosis="No obvious phone number, email address, or contact form marker was detected.",
            business_impact="Prospects may abandon before contacting the business, lowering lead conversion.",
            severity="high",
        )

    if performance_score is not None and performance_score < LOW_PERFORMANCE_THRESHOLD:
        _add_finding(
            findings,
            finding_titles_seen,
            title="Performance score is poor on mobile" if performance_score < 50 else "Mobile/web performance signal is below target",
            diagnosis=f"Detected performance score: {performance_score:.1f}.",
            business_impact="Slower experiences can hurt conversion, retention, and SEO outcomes.",
            severity="high" if performance_score < 50 else "medium",
        )

    if lcp_ms is not None and lcp_ms > 4000:
        _add_finding(
            findings,
            finding_titles_seen,
            title="Largest Contentful Paint is very slow",
            diagnosis=f"Detected LCP: {lcp_ms:.0f}ms (above 4000ms).",
            business_impact="Very slow content rendering can significantly reduce engagement and trust.",
            severity="high",
        )
    elif lcp_ms is not None and lcp_ms > HIGH_LCP_THRESHOLD_MS:
        _add_finding(
            findings,
            finding_titles_seen,
            title="Largest Contentful Paint is high",
            diagnosis=f"Detected LCP: {lcp_ms:.0f}ms.",
            business_impact="Slow largest-content render can degrade UX and search quality signals.",
            severity="medium",
        )

    if cls is not None and cls > 0.1:
        _add_finding(
            findings,
            finding_titles_seen,
            title="Layout stability issues detected",
            diagnosis=f"Detected CLS: {cls:.3f} (above 0.1).",
            business_impact="Layout shifts can cause misclicks and lower user confidence.",
            severity="medium",
        )

    if cms and any(template in cms for template in TEMPLATE_CMS_SIGNALS):
        technical_issues.append(f"Template CMS signal detected: {cms}")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Template CMS limitation signal",
            diagnosis=f"Detected CMS/platform signal: {cms}.",
            business_impact="Complex workflow or integration requirements may need custom architecture.",
            severity="medium",
        )

    if not has_https:
        technical_issues.append("Website URL does not use HTTPS")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Website is not using HTTPS",
            diagnosis=f"Lead website URL is '{lead.website_url}', which is not HTTPS.",
            business_impact="Non-HTTPS sites reduce trust and can trigger browser warnings.",
            severity="high",
        )

    if canonical_mismatch:
        technical_issues.append("Canonical hostname mismatch detected")
        _add_finding(
            findings,
            finding_titles_seen,
            title="Canonical hostname mismatch detected",
            diagnosis="Canonical URL points to a different hostname than the requested homepage URL.",
            business_impact="Search engines may index unintended hosts, splitting ranking signals.",
            severity="medium",
        )

    if not has_testimonials:
        trust_issues.append("No testimonial/review signal detected")
    if not has_about_section:
        trust_issues.append("No team/about signal detected")
    if not has_address:
        trust_issues.append("No address/location signal detected")
    if not has_institutional_signal:
        trust_issues.append("No institutional trust signal detected")
    if not has_brand_signal and content_depth_score < 3:
        trust_issues.append("Brand/depth trust signal is weak")

    if trust_score <= 2:
        _add_finding(
            findings,
            finding_titles_seen,
            title="Trust signals are limited on homepage",
            diagnosis=(
                f"Trust score is {trust_score}/{trust_max_score}; "
                f"missing markers: {', '.join(trust_issues) if trust_issues else 'not specified'}."
            ),
            business_impact="Prospects may hesitate to engage when social proof and contact confidence are weak.",
            severity="high" if trust_score <= 1 else "medium",
        )

    prioritized_findings = _prioritize_findings(findings)
    if not prioritized_findings:
        summary = "Baseline report generated from available V1 evidence with no high-confidence blocking issues."
    else:
        top_findings = "; ".join(item["title"] for item in prioritized_findings[:3])
        summary = f"Baseline report generated from V1 evidence. Key findings: {top_findings}."

    return {
        "summary": summary,
        "site_type": inferred_site_type,
        "cta_clarity": cta_clarity,
        "cta": {
            "clarity": cta_clarity,
            "keyword_hits": int(cta_signals["keyword_hits"]),
            "first_cta_position": cta_signals["first_cta_position"],
            "action_elements_count": int(cta_signals["action_elements_count"]),
            "pricing_detected": bool(cta_signals["pricing_detected"]),
            "multiple_ctas": bool(cta_signals["multiple_ctas"]),
            "visual_cta_density": float(cta_signals["visual_cta_density"]),
            "has_phone": has_phone,
            "has_email": has_email,
            "has_form": has_contact_form,
            "has_contact_method": has_any_contact_method,
        },
        "performance": {
            "score": int(round(performance_score)) if performance_score is not None else None,
            "lcp_ms": int(round(lcp_ms)) if lcp_ms is not None else None,
            "cls": round(float(cls), 4) if cls is not None else None,
            "fcp_ms": int(round(fcp_ms)) if fcp_ms is not None else None,
            "tbt_ms": int(round(tbt_ms)) if tbt_ms is not None else None,
            "rating": performance_rating,
            "source": perf_source,
        },
        "seo": {
            "has_robots": has_robots,
            "has_sitemap": has_sitemap,
            "has_title": has_title,
            "title_length": title_length if has_title else 0,
            "has_meta_description": has_meta_description,
            "meta_description_length": meta_description_length if has_meta_description else 0,
            "has_h1": has_h1,
            "h1_count": h1_count,
            "unique_h1_count": unique_h1_count,
            "has_canonical": has_canonical,
            "issues": seo_issues,
        },
        "trust": {
            "has_testimonials": has_testimonials,
            "has_about_section": has_about_section,
            "has_address": has_address,
            "has_institutional_signal": has_institutional_signal,
            "has_brand_signal": has_brand_signal,
            "content_depth_score": content_depth_score,
            "has_contact_info": has_contact_info or has_contact_form,
            "score": trust_score,
            "max_score": trust_max_score,
            "rating": trust_rating,
            "issues": trust_issues,
        },
        "technical": {
            "cms": cms,
            "platform_signals": platform_signals,
            "has_https": has_https,
            "canonical_mismatch": canonical_mismatch,
            "site_type": inferred_site_type,
            "issues": technical_issues,
        },
        "findings": prioritized_findings,
    }


@transaction.atomic
def upsert_report(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    evidence_ids: list[int | str],
    model: str,
    prompt_version: str,
    summary: str = "",
    force: bool = False,
) -> tuple[WebsiteReport, bool]:
    normalized_evidence_ids = _normalize_evidence_ids(evidence_ids)
    resolved_summary = summary.strip()
    if not resolved_summary and isinstance(report_payload, dict):
        resolved_summary = str(
            report_payload.get("executive_summary")
            or report_payload.get("summary")
            or ""
        ).strip()

    if not force:
        existing_report = _find_matching_report(
            lead=lead,
            model=model,
            prompt_version=prompt_version,
            evidence_ids=normalized_evidence_ids,
            report_payload=report_payload,
            summary=resolved_summary,
        )
        if existing_report is not None:
            if lead.status in {"new", "evidence_collected"}:
                lead.status = "reported"
                lead.save(update_fields=["status", "updated_at"])
            return existing_report, False

    report = WebsiteReport.objects.create(
        lead=lead,
        model=model,
        prompt_version=prompt_version,
        evidence_ids=normalized_evidence_ids,
        report=report_payload,
        summary=resolved_summary,
    )
    if lead.status in {"new", "evidence_collected"}:
        lead.status = "reported"
        lead.save(update_fields=["status", "updated_at"])
    return report, True


def persist_report(
    *,
    lead: Lead,
    report_payload: dict[str, Any],
    evidence_ids: list[int],
    model: str,
    prompt_version: str,
    summary: str = "",
) -> WebsiteReport:
    report, _created = upsert_report(
        lead=lead,
        report_payload=report_payload,
        evidence_ids=evidence_ids,
        model=model,
        prompt_version=prompt_version,
        summary=summary,
        force=False,
    )
    return report
