from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

from growth_ops.services.evidence_fetcher import fetch_url

MAILTO_RE = re.compile(r"mailto:([^\"'\s>]+)", re.IGNORECASE)
TEL_RE = re.compile(r"tel:([^\"'\s>]+)", re.IGNORECASE)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
ANCHOR_RE = re.compile(
    r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(\+?\d[\d\s().\-]{7,}\d)")
TAG_RE = re.compile(r"<[^>]+>")

CONTACT_LINK_HINT_WEIGHTS: dict[str, int] = {
    "contact": 100,
    "get-in-touch": 95,
    "enquire": 90,
    "inquiry": 90,
    "inquire": 90,
    "free-trial": 85,
    "trial": 75,
    "join": 75,
    "sign-up": 70,
    "signup": 70,
    "membership": 68,
    "locations": 60,
    "clubs": 58,
    "find-us": 58,
}
SOCIAL_HOST_MAP = {
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "linkedin.com": "linkedin",
}
PREFERRED_EMAIL_PREFIXES = ("info@", "hello@", "contact@", "enquiries@", "inquiries@", "sales@")


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def _normalize_email(raw: str) -> str:
    email = (raw or "").strip().lower()
    email = email.replace("mailto:", "").strip()
    if "?" in email:
        email = email.split("?", 1)[0].strip()
    if "@" not in email or "." not in email.split("@", 1)[-1]:
        return ""
    if " " in email or ".." in email:
        return ""
    return email


def _normalize_phone(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    value = value.replace("tel:", "").strip()
    value = re.sub(r"[^0-9+]", "", value)
    if value.count("+") > 1:
        return ""
    if "+" in value and not value.startswith("+"):
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) < 8 or len(digits) > 15:
        return ""
    return value


def _strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", html or "")).strip()


def _absolute_link(href: str, website_url: str | None) -> str:
    href_value = (href or "").strip()
    if not href_value:
        return ""
    if href_value.startswith("#") or href_value.lower().startswith("javascript:"):
        return ""
    if href_value.startswith("mailto:") or href_value.startswith("tel:"):
        return href_value
    if href_value.startswith("//"):
        return f"https:{href_value}"
    if href_value.startswith(("http://", "https://")):
        return href_value
    if website_url:
        return urljoin(website_url, href_value)
    return href_value


def _extract_social_links(links: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for link in links:
        parsed = urlparse(link if "://" in link else f"https://{link}")
        host = (parsed.netloc or "").lower()
        for domain, label in SOCIAL_HOST_MAP.items():
            if domain in host and label not in out:
                out[label] = link
    return out


def _extract_anchor_candidates(html: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen_hrefs: set[str] = set()

    for href, anchor_body in ANCHOR_RE.findall(html or ""):
        normalized_href = str(href or "").strip()
        if not normalized_href:
            continue
        anchor_text = _strip_html(anchor_body)
        candidates.append((normalized_href, anchor_text))
        seen_hrefs.add(normalized_href)

    for href in HREF_RE.findall(html or ""):
        normalized_href = str(href or "").strip()
        if not normalized_href or normalized_href in seen_hrefs:
            continue
        candidates.append((normalized_href, ""))
    return candidates


def _link_score(*, absolute_link: str, anchor_text: str) -> int:
    lowered_link = absolute_link.lower()
    lowered_text = (anchor_text or "").lower()
    score = 0
    for hint, weight in CONTACT_LINK_HINT_WEIGHTS.items():
        if hint in lowered_link:
            score += weight
        elif hint in lowered_text:
            score += max(1, weight // 2)
    return score


def _extract_contact_links(anchor_candidates: list[tuple[str, str]], website_url: str | None) -> list[str]:
    scored_links: list[tuple[int, int, str]] = []
    out: list[str] = []
    for href, anchor_text in anchor_candidates:
        normalized = _absolute_link(href, website_url)
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered.startswith("mailto:") or lowered.startswith("tel:"):
            continue
        if not lowered.startswith(("http://", "https://")):
            continue
        score = _link_score(absolute_link=normalized, anchor_text=anchor_text)
        if score <= 0:
            continue
        scored_links.append((score, len(normalized), normalized))

    scored_links.sort(key=lambda item: (-item[0], item[1], item[2].lower()))
    for _score, _length, normalized in scored_links:
        out.append(normalized)
    return _dedupe(out)


def _select_contact_link(contact_links: list[str]) -> str | None:
    for link in contact_links:
        normalized = str(link or "").strip()
        if normalized:
            return normalized
    return None


def _best_email(emails: list[str]) -> str | None:
    if not emails:
        return None
    lowered = [email.lower() for email in emails]
    for prefix in PREFERRED_EMAIL_PREFIXES:
        for idx, email in enumerate(lowered):
            if email.startswith(prefix):
                return emails[idx]
    return emails[0]


def _best_phone(phones: list[str]) -> str | None:
    if not phones:
        return None
    sorted_candidates = sorted(
        phones,
        key=lambda item: (0 if item.startswith("+") else 1, -len(re.sub(r"\D", "", item))),
    )
    return sorted_candidates[0]


def extract_contact_candidates(*, homepage_html: str, website_url: str | None = None) -> dict[str, Any]:
    html = homepage_html or ""
    anchor_candidates = _extract_anchor_candidates(html)
    hrefs = [href for href, _text in anchor_candidates]
    normalized_links = _dedupe([_absolute_link(href, website_url) for href in hrefs if href.strip()])
    text = _strip_html(html)

    mailto_matches = [_normalize_email(match) for match in MAILTO_RE.findall(html)]
    text_email_matches = [_normalize_email(match) for match in EMAIL_RE.findall(text)]
    emails = _dedupe([value for value in mailto_matches + text_email_matches if value])

    tel_matches = [_normalize_phone(match) for match in TEL_RE.findall(html)]
    text_phone_matches = [_normalize_phone(match) for match in PHONE_RE.findall(text)]
    phones = _dedupe([value for value in tel_matches + text_phone_matches if value])

    contact_links = _extract_contact_links(anchor_candidates, website_url)
    social_links = _extract_social_links(normalized_links)
    selected_contact_link = _select_contact_link(contact_links)

    return {
        "emails": emails,
        "phones": phones,
        "contact_links": contact_links,
        "social_links": social_links,
        "best_email": _best_email(emails),
        "best_phone": _best_phone(phones),
        "selected_contact_link": selected_contact_link,
    }


def enrich_with_contact_page(
    *,
    candidates: dict[str, Any],
    website_url: str | None = None,
) -> dict[str, Any]:
    """
    Optionally enrich candidates with up to two likely contact/action page fetches.
    Non-fatal and non-recursive.
    """
    enriched = dict(candidates or {})
    best_email = str(enriched.get("best_email") or "").strip()
    best_phone = str(enriched.get("best_phone") or "").strip()
    contact_links = list(enriched.get("contact_links") or [])
    if (best_email or best_phone) or not contact_links:
        return enriched

    candidate_links = _dedupe(contact_links)[:3]
    links_to_fetch = candidate_links[:2]
    merged_emails = list(enriched.get("emails") or [])
    merged_phones = list(enriched.get("phones") or [])
    merged_links = list(enriched.get("contact_links") or [])
    merged_social = dict(enriched.get("social_links") or {})

    for candidate_link in links_to_fetch:
        fetch_result = fetch_url(
            candidate_link,
            accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        )
        if not fetch_result.get("exists"):
            continue
        contact_html = str(fetch_result.get("body") or "")
        if not contact_html:
            continue

        page_candidates = extract_contact_candidates(
            homepage_html=contact_html,
            website_url=fetch_result.get("requested_url") or website_url,
        )
        merged_emails = _dedupe(merged_emails + list(page_candidates.get("emails") or []))
        merged_phones = _dedupe(merged_phones + list(page_candidates.get("phones") or []))
        merged_links = _dedupe(merged_links + list(page_candidates.get("contact_links") or []))
        for key, value in (page_candidates.get("social_links") or {}).items():
            if key not in merged_social and value:
                merged_social[key] = value

    enriched.update(
        {
            "emails": merged_emails,
            "phones": merged_phones,
            "contact_links": merged_links,
            "social_links": merged_social,
            "best_email": _best_email(merged_emails),
            "best_phone": _best_phone(merged_phones),
            "selected_contact_link": _select_contact_link(merged_links),
        }
    )
    return enriched
