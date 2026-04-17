from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from django.db import transaction

from growth_ops.models import Contact, Lead


def normalize_website_url(raw_url: str) -> str:
    """Return a stable website URL representation used for matching/upsert."""
    if not raw_url:
        return ""
    return raw_url.strip().rstrip("/")


def domain_from_url(raw_url: str) -> str:
    """Extract a hostname from a URL-like value for fallback company naming."""
    normalized = normalize_website_url(raw_url)
    if not normalized:
        return ""
    parsed = urlparse(normalized if "://" in normalized else f"https://{normalized}")
    return (parsed.hostname or "").strip()


def find_existing_lead(validated_data: dict[str, Any]) -> Lead | None:
    """
    Match existing leads in the same order as the current API contract:
    1) google_place_id
    2) normalized website_url
    3) company_name (+ optional location)
    """
    google_place_id = (validated_data.get("google_place_id") or "").strip()
    website_url = normalize_website_url(validated_data.get("website_url", ""))
    company_name = (validated_data.get("company_name") or "").strip()
    location = (validated_data.get("location") or "").strip()

    if google_place_id:
        match = Lead.objects.filter(google_place_id=google_place_id).order_by("-created_at").first()
        if match:
            return match

    if website_url:
        match = Lead.objects.filter(website_url__iexact=website_url).order_by("-created_at").first()
        if match:
            return match

    if company_name:
        queryset = Lead.objects.filter(company_name__iexact=company_name)
        if location:
            queryset = queryset.filter(location__iexact=location)
        match = queryset.order_by("-created_at").first()
        if match:
            return match

    return None


def upsert_contacts(lead: Lead, contacts_data: list[dict[str, Any]]) -> tuple[int, int]:
    """Create/update contacts idempotently (email-based when available)."""
    created_count = 0
    updated_count = 0

    for contact_data in contacts_data:
        email = (contact_data.get("email") or "").strip()
        if email:
            contact, created = lead.contacts.get_or_create(
                email=email,
                defaults={
                    "name": contact_data.get("name", ""),
                    "role": contact_data.get("role", ""),
                    "phone": contact_data.get("phone", ""),
                    "linkedin_url": contact_data.get("linkedin_url", ""),
                },
            )
            if created:
                created_count += 1
                continue

            changed = False
            for field in ("name", "role", "phone", "linkedin_url"):
                value = contact_data.get(field)
                if value not in (None, "") and getattr(contact, field) != value:
                    setattr(contact, field, value)
                    changed = True
            if changed:
                contact.save()
                updated_count += 1
            continue

        Contact.objects.create(
            lead=lead,
            name=contact_data.get("name", ""),
            role=contact_data.get("role", ""),
            phone=contact_data.get("phone", ""),
            linkedin_url=contact_data.get("linkedin_url", ""),
        )
        created_count += 1

    return created_count, updated_count


@transaction.atomic
def upsert_lead_from_candidate(candidate: dict[str, Any]) -> tuple[Lead, bool]:
    """
    Create or update a lead from candidate payload and return `(lead, created)`.

    Raises:
        ValueError: when a new lead cannot be created due to missing company name fallback.
    """
    normalized_candidate = dict(candidate)
    if not normalized_candidate.get("google_place_id") and normalized_candidate.get("google_places_id"):
        normalized_candidate["google_place_id"] = normalized_candidate.get("google_places_id")

    existing = find_existing_lead(normalized_candidate)
    website_url = normalize_website_url(normalized_candidate.get("website_url", ""))

    if existing is None:
        company_name = (normalized_candidate.get("company_name") or "").strip() or domain_from_url(website_url)
        if not company_name:
            raise ValueError("company_name_required_for_create")

        lead = Lead.objects.create(
            market=normalized_candidate.get("market", "OTHER"),
            location=normalized_candidate.get("location", ""),
            industry=normalized_candidate.get("industry", ""),
            company_name=company_name,
            website_url=website_url,
            google_place_id=normalized_candidate.get("google_place_id", ""),
            source=normalized_candidate.get("source", "n8n"),
            status=normalized_candidate.get("status", "new"),
            notes=normalized_candidate.get("notes", ""),
        )
        created = True
    else:
        lead = existing
        for field in (
            "market",
            "location",
            "industry",
            "company_name",
            "google_place_id",
            "source",
            "status",
            "notes",
        ):
            value = normalized_candidate.get(field)
            if value not in (None, ""):
                setattr(lead, field, value)
        if website_url:
            lead.website_url = website_url
        lead.save()
        created = False

    contacts_data: list[dict[str, Any]] = list(normalized_candidate.get("contacts") or [])
    if contacts_data:
        upsert_contacts(lead, contacts_data)

    return lead, created
