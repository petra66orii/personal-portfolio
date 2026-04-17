from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from django.conf import settings

REQUEST_TIMEOUT_SECONDS = 15
MAX_BODY_CHARS = 20_000
MAX_PAGESPEED_RAW_CHARS = 35_000
PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PAGESPEED_RELEVANT_AUDITS = {
    "largest-contentful-paint",
    "cumulative-layout-shift",
    "first-contentful-paint",
    "total-blocking-time",
    "speed-index",
    "interactive",
}

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def _pagespeed_api_key() -> str:
    return (
        getattr(settings, "PAGESPEED_API_KEY", "")
        or os.getenv("PAGESPEED_API_KEY", "")
    ).strip()


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_pagespeed_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    lighthouse = payload.get("lighthouseResult") or {}
    categories = lighthouse.get("categories") or {}
    audits = lighthouse.get("audits") or {}

    perf_score_raw = ((categories.get("performance") or {}).get("score"))
    perf_score: int | None = None
    if perf_score_raw is not None:
        parsed = _as_float(perf_score_raw)
        if parsed is not None:
            perf_score = _as_int(parsed * 100 if 0 <= parsed <= 1 else parsed)

    return {
        "performance_score": perf_score,
        "lcp_ms": _as_int((audits.get("largest-contentful-paint") or {}).get("numericValue")),
        "cls": _as_float((audits.get("cumulative-layout-shift") or {}).get("numericValue")),
        "fcp_ms": _as_int((audits.get("first-contentful-paint") or {}).get("numericValue")),
        "tbt_ms": _as_int((audits.get("total-blocking-time") or {}).get("numericValue")),
    }


def _trim_pagespeed_loading_experience(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    metrics_payload = payload.get("metrics")
    metrics: dict[str, Any] = {}
    if isinstance(metrics_payload, dict):
        for key, value in metrics_payload.items():
            if not isinstance(value, dict):
                continue
            metrics[key] = {
                "percentile": _as_int(value.get("percentile")),
                "category": value.get("category"),
            }
    return {
        "overall_category": payload.get("overall_category"),
        "metrics": metrics,
    }


def _trim_pagespeed_raw_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    lighthouse = payload.get("lighthouseResult")
    lighthouse_result: dict[str, Any] = {}
    if isinstance(lighthouse, dict):
        audits_payload = lighthouse.get("audits")
        trimmed_audits: dict[str, Any] = {}
        if isinstance(audits_payload, dict):
            for key in PAGESPEED_RELEVANT_AUDITS:
                audit_value = audits_payload.get(key)
                if not isinstance(audit_value, dict):
                    continue
                trimmed_audits[key] = {
                    "score": _as_float(audit_value.get("score")),
                    "numericValue": _as_float(audit_value.get("numericValue")),
                    "displayValue": str(audit_value.get("displayValue") or "").strip(),
                }

        lighthouse_result = {
            "requestedUrl": lighthouse.get("requestedUrl"),
            "finalDisplayedUrl": lighthouse.get("finalDisplayedUrl"),
            "fetchTime": lighthouse.get("fetchTime"),
            "categories": {
                "performance": {
                    "score": _as_float(
                        ((lighthouse.get("categories") or {}).get("performance") or {}).get("score")
                    )
                }
            },
            "audits": trimmed_audits,
        }

    trimmed = {
        "analysisUTCTimestamp": payload.get("analysisUTCTimestamp"),
        "id": payload.get("id"),
        "captchaResult": payload.get("captchaResult"),
        "loadingExperience": _trim_pagespeed_loading_experience(payload.get("loadingExperience")),
        "originLoadingExperience": _trim_pagespeed_loading_experience(payload.get("originLoadingExperience")),
        "lighthouseResult": lighthouse_result,
    }

    raw_json = json.dumps(trimmed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if len(raw_json) <= MAX_PAGESPEED_RAW_CHARS:
        return trimmed

    # Hard cap fallback when source payload is unexpectedly large.
    return {
        "analysisUTCTimestamp": payload.get("analysisUTCTimestamp"),
        "id": payload.get("id"),
        "captchaResult": payload.get("captchaResult"),
        "lighthouseResult": {
            "categories": {
                "performance": {
                    "score": _as_float(
                        ((lighthouse.get("categories") or {}).get("performance") or {}).get("score")
                        if isinstance(lighthouse, dict)
                        else None
                    )
                }
            }
        },
        "truncated": True,
    }


def normalize_and_split_url(url: str) -> tuple[str | None, str | None]:
    """
    Normalize incoming URL and return:
    - normalized URL
    - origin (`scheme://host[:port]`)
    """
    raw = (url or "").strip()
    if not raw:
        return None, None
    if "://" not in raw:
        raw = f"https://{raw}"

    parsed = urlparse(raw)
    if not parsed.netloc:
        return None, None

    scheme = parsed.scheme or "https"
    normalized_parsed = parsed._replace(
        scheme=scheme,
        path=parsed.path or "/",
        params="",
        fragment="",
    )
    normalized_url = urlunparse(normalized_parsed)
    if normalized_url.endswith("/") and normalized_parsed.path == "/":
        normalized_url = normalized_url.rstrip("/")

    origin = f"{scheme}://{parsed.netloc}"
    return normalized_url, origin


def fetch_url(url: str, accept: str) -> dict[str, Any]:
    """Fetch URL with browser-like headers and return a non-throwing structured result."""
    headers = dict(BASE_HEADERS)
    headers["Accept"] = accept

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        return {
            "exists": False,
            "status_code": None,
            "requested_url": url,
            "body": "",
            "error": str(exc),
        }

    body = response.text or ""
    truncated = len(body) > MAX_BODY_CHARS
    body_snippet = body[:MAX_BODY_CHARS]
    result: dict[str, Any] = {
        "exists": 200 <= response.status_code < 400,
        "status_code": response.status_code,
        "requested_url": response.url or url,
        "body": body_snippet,
        "headers": dict(response.headers),
    }
    if truncated:
        result["truncated"] = True
    return result


def fetch_homepage(url: str) -> dict[str, Any]:
    return fetch_url(url, accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")


def fetch_robots(origin: str) -> dict[str, Any]:
    robots_url = urljoin(f"{origin}/", "robots.txt")
    return fetch_url(robots_url, accept="text/plain,*/*;q=0.8")


def fetch_sitemap(origin: str) -> dict[str, Any]:
    sitemap_url = urljoin(f"{origin}/", "sitemap.xml")
    return fetch_url(sitemap_url, accept="application/xml,text/xml;q=0.9,*/*;q=0.8")


def fetch_pagespeed(url: str) -> dict[str, Any]:
    """
    Fetch PageSpeed Insights data (mobile strategy) and return normalized metrics.
    Never raises for operational errors; always returns structured payload.
    """
    normalized_url, _origin = normalize_and_split_url(url)
    if not normalized_url:
        return {
            "performance_score": None,
            "lcp_ms": None,
            "cls": None,
            "fcp_ms": None,
            "tbt_ms": None,
            "error": "invalid_website_url",
            "raw": {},
        }

    api_key = _pagespeed_api_key()
    if not api_key:
        return {
            "performance_score": None,
            "lcp_ms": None,
            "cls": None,
            "fcp_ms": None,
            "tbt_ms": None,
            "error": "missing_pagespeed_api_key",
            "raw": {},
        }

    params = {
        "url": normalized_url,
        "strategy": "mobile",
        "key": api_key,
    }

    try:
        response = requests.get(PAGESPEED_API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        return {
            "performance_score": None,
            "lcp_ms": None,
            "cls": None,
            "fcp_ms": None,
            "tbt_ms": None,
            "error": "pagespeed_request_failed",
            "error_detail": str(exc),
            "raw": {},
        }

    raw_payload: dict[str, Any]
    try:
        raw_payload = response.json()
    except ValueError:
        raw_payload = {}

    if response.status_code >= 400:
        return {
            "performance_score": None,
            "lcp_ms": None,
            "cls": None,
            "fcp_ms": None,
            "tbt_ms": None,
            "error": "pagespeed_http_error",
            "status_code": response.status_code,
            "raw": _trim_pagespeed_raw_payload(raw_payload if isinstance(raw_payload, dict) else {}),
        }

    metrics = _extract_pagespeed_metrics(raw_payload if isinstance(raw_payload, dict) else {})
    return {
        **metrics,
        "error": "",
        "raw": _trim_pagespeed_raw_payload(raw_payload if isinstance(raw_payload, dict) else {}),
    }


def collect_basic_evidence(website_url: str) -> list[dict[str, Any]]:
    """Collect homepage/robots/sitemap evidence payloads ready for WebsiteEvidence persistence."""
    normalized_url, origin = normalize_and_split_url(website_url)
    if not normalized_url or not origin:
        error_payload = {
            "exists": False,
            "status_code": None,
            "requested_url": website_url,
            "body": "",
            "error": "invalid_website_url",
        }
        return [
            {
                "evidence_type": "homepage_html_snippet",
                "url": website_url,
                "tool": "python_requests",
                "payload": error_payload,
            },
            {
                "evidence_type": "robots_txt",
                "url": website_url,
                "tool": "python_requests",
                "payload": error_payload,
            },
            {
                "evidence_type": "sitemap_xml",
                "url": website_url,
                "tool": "python_requests",
                "payload": error_payload,
            },
        ]

    homepage = fetch_homepage(normalized_url)
    robots = fetch_robots(origin)
    sitemap = fetch_sitemap(origin)
    return [
        {
            "evidence_type": "homepage_html_snippet",
            "url": normalized_url,
            "tool": "python_requests",
            "payload": homepage,
        },
        {
            "evidence_type": "robots_txt",
            "url": robots.get("requested_url", urljoin(f"{origin}/", "robots.txt")),
            "tool": "python_requests",
            "payload": robots,
        },
        {
            "evidence_type": "sitemap_xml",
            "url": sitemap.get("requested_url", urljoin(f"{origin}/", "sitemap.xml")),
            "tool": "python_requests",
            "payload": sitemap,
        },
    ]
