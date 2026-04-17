from __future__ import annotations

import os
from typing import Any

import requests
from django.conf import settings

GOOGLE_PLACES_TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GOOGLE_PLACES_TIMEOUT_SECONDS = 20


def _google_places_api_key() -> str:
    key = (
        getattr(settings, "GOOGLE_PLACES_KEY", "")
        or os.getenv("GOOGLE_PLACES_KEY", "")
    ).strip()
    if not key:
        raise RuntimeError("GOOGLE_PLACES_KEY is not configured.")
    return key


def _request_google_places_json(*, url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=GOOGLE_PLACES_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    status_value = payload.get("status", "UNKNOWN_ERROR")
    if status_value not in {"OK", "ZERO_RESULTS"}:
        error_message = payload.get("error_message", status_value)
        raise RuntimeError(f"Google Places API error: {error_message}")
    return payload


def search_places(*, keyword: str, location: str, limit: int) -> list[dict[str, Any]]:
    key = _google_places_api_key()
    query = f"{keyword} in {location}".strip()
    payload = _request_google_places_json(
        url=GOOGLE_PLACES_TEXTSEARCH_URL,
        params={"query": query, "key": key},
    )
    results = payload.get("results") or []
    return list(results[: max(1, limit)])


def fetch_place_details(place_id: str) -> dict[str, Any]:
    key = _google_places_api_key()
    payload = _request_google_places_json(
        url=GOOGLE_PLACES_DETAILS_URL,
        params={
            "place_id": place_id,
            "fields": "name,website,formatted_phone_number,formatted_address,rating,user_ratings_total,types,url",
            "key": key,
        },
    )
    return payload.get("result") or {}


def _normalize_candidate(
    *,
    keyword: str,
    location: str,
    place: dict[str, Any],
    details: dict[str, Any],
) -> dict[str, Any]:
    fallback_types = place.get("types") or []
    detail_types = details.get("types") or fallback_types
    place_id = place.get("place_id") or details.get("place_id") or ""

    return {
        "company_name": details.get("name") or place.get("name") or "",
        "website_url": details.get("website") or "",
        "phone": details.get("formatted_phone_number") or "",
        "location": location,
        "industry": keyword,
        "google_place_id": place_id,
        "source": "google_places_api",
        "notes": "Imported from Google Places discovery pipeline",
        "address": details.get("formatted_address") or place.get("formatted_address") or "",
        "rating": details.get("rating", place.get("rating")),
        "reviews_count": details.get("user_ratings_total", place.get("user_ratings_total")),
        "google_maps_url": details.get("url") or "",
        "raw_types": detail_types,
    }


def discover_place_candidates(*, keyword: str, location: str, limit: int) -> list[dict[str, Any]]:
    """Discover and normalize place candidates for downstream lead upsert."""
    candidates: list[dict[str, Any]] = []
    places = search_places(keyword=keyword, location=location, limit=limit)

    for place in places:
        place_id = (place.get("place_id") or "").strip()
        if not place_id:
            continue
        details: dict[str, Any] = {}
        try:
            details = fetch_place_details(place_id)
        except Exception as exc:
            details = {"detail_fetch_error": str(exc)}

        candidate = _normalize_candidate(
            keyword=keyword,
            location=location,
            place=place,
            details=details,
        )
        if details.get("detail_fetch_error"):
            candidate["notes"] = f"{candidate['notes']} (detail fetch degraded: {details['detail_fetch_error']})"
        candidates.append(candidate)

    return candidates
