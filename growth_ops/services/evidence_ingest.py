from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from django.db import transaction

from growth_ops.models import Lead, WebsiteEvidence
from growth_ops.services.lead_ingest import domain_from_url, normalize_website_url

FETCH_V1_EVIDENCE_TYPES = {
    "homepage_html_snippet",
    "robots_txt",
    "sitemap_xml",
    "pagespeed_json",
}
MAX_DEDUPE_TEXT_LENGTH = 12_000
WHITESPACE_RE = re.compile(r"\s+")
TAG_GAP_RE = re.compile(r">\s+<")
SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
NOSCRIPT_BLOCK_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript>", re.IGNORECASE | re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
XML_DECLARATION_RE = re.compile(r"^\s*<\?xml[^>]*\?>", re.IGNORECASE)
SITEMAP_LASTMOD_RE = re.compile(r"<lastmod\b[^>]*>.*?</lastmod>", re.IGNORECASE | re.DOTALL)

logger = logging.getLogger(__name__)


def technical_data_to_evidence_items(
    technical_data: dict[str, Any],
    default_url: str = "",
) -> list[dict[str, Any]]:
    """Map legacy technical payload keys to WebsiteEvidence-compatible items."""
    type_mapping: dict[str, tuple[str, str]] = {
        "lighthouse": ("lighthouse_json", "legacy_site_auditor"),
        "pagespeed": ("pagespeed_json", "legacy_site_auditor"),
        "headers": ("homepage_headers", "legacy_site_auditor"),
        "robots": ("robots_txt", "legacy_site_auditor"),
        "sitemap": ("sitemap_xml", "legacy_site_auditor"),
        "tech_fingerprint": ("tech_fingerprint", "legacy_site_auditor"),
    }
    items: list[dict[str, Any]] = []

    for key, value in technical_data.items():
        evidence_type, tool = type_mapping.get(key, ("other", "legacy_site_auditor"))
        payload = value
        if not isinstance(payload, (dict, list)):
            payload = {"value": payload}
        items.append(
            {
                "evidence_type": evidence_type,
                "url": default_url,
                "tool": tool,
                "payload": payload,
            }
        )
    return items


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _collapse_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", (text or "").strip())


def _truncate_for_dedupe(text: str) -> str:
    if len(text) > MAX_DEDUPE_TEXT_LENGTH:
        return text[:MAX_DEDUPE_TEXT_LENGTH]
    return text


def _normalize_text_for_dedupe(text: str) -> str:
    """
    Normalize text for deterministic evidence dedupe comparison:
    - trim outer whitespace
    - collapse repeated whitespace runs
    - truncate deterministically to bounded size
    """
    return _truncate_for_dedupe(_collapse_whitespace(text))


def _normalize_homepage_html_for_dedupe(html: str) -> tuple[str, str]:
    """
    Homepage-specific canonicalization for dedupe:
    - remove <script> blocks
    - remove <noscript> blocks
    - remove HTML comments
    - collapse whitespace and trim
    - deterministically truncate for comparison payload
    Returns (normalized_truncated_body, normalized_body_hash).
    """
    stripped = SCRIPT_BLOCK_RE.sub(" ", html or "")
    stripped = NOSCRIPT_BLOCK_RE.sub(" ", stripped)
    stripped = HTML_COMMENT_RE.sub(" ", stripped)
    normalized_full = _collapse_whitespace(stripped)
    normalized_truncated = _truncate_for_dedupe(normalized_full)
    normalized_hash = hashlib.sha256(normalized_full.encode("utf-8")).hexdigest()[:16]
    return normalized_truncated, normalized_hash


def _normalize_sitemap_xml_for_dedupe(xml: str) -> tuple[str, str]:
    """
    Sitemap-specific canonicalization for dedupe:
    - remove XML declaration
    - remove comments
    - remove <lastmod> values to ignore timestamp churn
    - normalize inter-tag whitespace
    - collapse remaining whitespace and trim
    - deterministically truncate for comparison payload
    Returns (normalized_truncated_body, normalized_body_hash).
    """
    stripped = XML_DECLARATION_RE.sub(" ", xml or "", count=1)
    stripped = HTML_COMMENT_RE.sub(" ", stripped)
    stripped = SITEMAP_LASTMOD_RE.sub(" ", stripped)
    stripped = TAG_GAP_RE.sub("><", stripped)
    normalized_full = _collapse_whitespace(stripped)
    normalized_truncated = _truncate_for_dedupe(normalized_full)
    normalized_hash = hashlib.sha256(normalized_full.encode("utf-8")).hexdigest()[:16]
    return normalized_truncated, normalized_hash


def _normalize_status_code(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _normalize_float(value: Any, *, precision: int = 4) -> float | None:
    try:
        if value is None or value == "":
            return None
        return round(float(value), precision)
    except (TypeError, ValueError):
        return None


def canonicalize_evidence_payload(evidence_type: str, payload: Any) -> Any:
    """
    Return canonical payload used only for dedupe comparison.

    Raw payload persistence remains unchanged.
    """
    if evidence_type not in FETCH_V1_EVIDENCE_TYPES:
        return payload

    if not isinstance(payload, dict):
        payload = {"body": str(payload or "")}

    requested_url = normalize_website_url(str(payload.get("requested_url") or ""))
    if evidence_type == "homepage_html_snippet":
        body, body_hash = _normalize_homepage_html_for_dedupe(str(payload.get("body") or ""))
        return {
            "exists": bool(payload.get("exists", False)),
            "status_code": _normalize_status_code(payload.get("status_code")),
            "requested_url": requested_url,
            "body": body,
            "body_hash": body_hash,
        }
    if evidence_type == "sitemap_xml":
        body, body_hash = _normalize_sitemap_xml_for_dedupe(str(payload.get("body") or ""))
        return {
            "exists": bool(payload.get("exists", False)),
            "status_code": _normalize_status_code(payload.get("status_code")),
            "requested_url": requested_url,
            "body": body,
            "body_hash": body_hash,
        }
    if evidence_type == "pagespeed_json":
        return {
            "performance_score": _normalize_int(payload.get("performance_score")),
            "lcp_ms": _normalize_int(payload.get("lcp_ms")),
            "cls": _normalize_float(payload.get("cls"), precision=4),
            "fcp_ms": _normalize_int(payload.get("fcp_ms")),
            "tbt_ms": _normalize_int(payload.get("tbt_ms")),
            "error": str(payload.get("error") or "").strip(),
        }

    body = _normalize_text_for_dedupe(str(payload.get("body") or ""))
    return {
        "exists": bool(payload.get("exists", False)),
        "status_code": _normalize_status_code(payload.get("status_code")),
        "requested_url": requested_url,
        "body": body,
    }


def find_matching_evidence(
    *,
    lead: Lead,
    evidence_type: str,
    url: str,
    tool: str,
    payload: Any,
) -> WebsiteEvidence | None:
    recent_records = lead.website_evidence.filter(
        evidence_type=evidence_type,
        url=url,
        tool=tool,
    ).order_by("-created_at")[:25]
    canonical_target = canonicalize_evidence_payload(evidence_type, payload)
    target_payload = _canonical_json(canonical_target)
    target_fingerprint = hashlib.sha256(target_payload.encode("utf-8")).hexdigest()[:16]
    candidate_fingerprints: list[str] = []
    for record in recent_records:
        candidate_payload = canonicalize_evidence_payload(evidence_type, record.payload)
        candidate_json = _canonical_json(candidate_payload)
        if evidence_type == "sitemap_xml":
            candidate_fingerprints.append(hashlib.sha256(candidate_json.encode("utf-8")).hexdigest()[:16])
        if candidate_json == target_payload:
            return record
    if evidence_type == "sitemap_xml":
        logger.debug(
            "Sitemap dedupe miss: lead_id=%s url=%s tool=%s target_fp=%s candidates=%s",
            lead.id,
            url,
            tool,
            target_fingerprint,
            candidate_fingerprints,
        )
    return None


def resolve_lead_for_evidence(validated_data: dict[str, Any]) -> Lead:
    """
    Resolve or create a lead for incoming evidence using the current API behavior.

    Raises:
        Lead.DoesNotExist: when no resolvable lead key is available for fallback create.
    """
    lead_id = validated_data.get("lead_id")
    if lead_id is not None:
        return Lead.objects.get(pk=lead_id)

    website_url = normalize_website_url(validated_data.get("website_url", ""))
    company_name = (validated_data.get("company_name") or "").strip()
    source = (validated_data.get("source") or "n8n").strip() or "n8n"

    if website_url:
        existing = Lead.objects.filter(website_url__iexact=website_url).order_by("-created_at").first()
        if existing:
            return existing

    if company_name:
        existing = Lead.objects.filter(company_name__iexact=company_name).order_by("-created_at").first()
        if existing:
            return existing

    fallback_name = company_name or domain_from_url(website_url)
    if not fallback_name:
        raise Lead.DoesNotExist("Lead could not be resolved and no create fallback data was provided")

    return Lead.objects.create(
        company_name=fallback_name,
        website_url=website_url,
        market=validated_data.get("market", "OTHER"),
        source=source,
        status="new",
    )


@transaction.atomic
def persist_evidence_items(*, lead: Lead, items: list[dict[str, Any]]) -> dict[str, Any]:
    """Persist evidence with duplicate detection and return summary counters."""
    created_ids: list[int] = []
    reused_ids: list[int] = []

    for item in items:
        normalized_url = normalize_website_url(item.get("url", "")) or lead.website_url
        tool = item.get("tool", "")
        payload = item.get("payload", {})
        existing = find_matching_evidence(
            lead=lead,
            evidence_type=item["evidence_type"],
            url=normalized_url,
            tool=tool,
            payload=payload,
        )
        if existing is not None:
            reused_ids.append(existing.id)
            continue

        record = WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type=item["evidence_type"],
            url=normalized_url,
            tool=tool,
            payload=payload,
        )
        created_ids.append(record.id)

    if created_ids and lead.status == "new":
        lead.status = "evidence_collected"
        lead.save(update_fields=["status", "updated_at"])

    return {
        "lead_id": lead.id,
        "created_count": len(created_ids),
        "reused_count": len(reused_ids),
        "evidence_ids": created_ids + reused_ids,
    }


def persist_technical_data(
    *,
    lead: Lead,
    technical_data: dict[str, Any],
    default_url: str = "",
) -> dict[str, Any]:
    """Convert technical_data into evidence items and persist them."""
    items = technical_data_to_evidence_items(technical_data, default_url=default_url)
    return persist_evidence_items(lead=lead, items=items)
