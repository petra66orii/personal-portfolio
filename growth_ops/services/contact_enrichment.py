from __future__ import annotations

from typing import Any

from growth_ops.models import Contact, Lead


def _normalized_emails(extracted_contacts: dict[str, Any]) -> list[str]:
    values = list(extracted_contacts.get("emails") or [])
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        email = str(value or "").strip().lower()
        if not email:
            continue
        if email in seen:
            continue
        seen.add(email)
        out.append(email)
    best = str(extracted_contacts.get("best_email") or "").strip().lower()
    if best and best not in seen:
        out.insert(0, best)
    return out


def _normalized_phones(extracted_contacts: dict[str, Any]) -> list[str]:
    values = list(extracted_contacts.get("phones") or [])
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        phone = str(value or "").strip()
        if not phone:
            continue
        if phone in seen:
            continue
        seen.add(phone)
        out.append(phone)
    best = str(extracted_contacts.get("best_phone") or "").strip()
    if best and best not in seen:
        out.insert(0, best)
    return out


def upsert_contacts_for_lead(*, lead: Lead, extracted_contacts: dict[str, Any]) -> dict[str, Any]:
    emails = _normalized_emails(extracted_contacts)
    phones = _normalized_phones(extracted_contacts)
    social_links = extracted_contacts.get("social_links") or {}
    linkedin_url = str(social_links.get("linkedin") or "").strip()

    contacts_created = 0
    contacts_reused = 0
    primary_contact: Contact | None = None

    best_phone = phones[0] if phones else ""

    for index, email in enumerate(emails):
        defaults = {
            "name": "",
            "role": "website-derived",
            "phone": best_phone if index == 0 else "",
            "linkedin_url": linkedin_url,
        }
        contact, created = lead.contacts.get_or_create(email=email, defaults=defaults)
        if created:
            contacts_created += 1
        else:
            contacts_reused += 1
            changed = False
            if not contact.phone and defaults["phone"]:
                contact.phone = defaults["phone"]
                changed = True
            if not contact.linkedin_url and linkedin_url:
                contact.linkedin_url = linkedin_url
                changed = True
            if not contact.role:
                contact.role = "website-derived"
                changed = True
            if changed:
                contact.save(update_fields=["phone", "linkedin_url", "role"])
        if primary_contact is None and email == str(extracted_contacts.get("best_email") or "").strip().lower():
            primary_contact = contact
        elif primary_contact is None and index == 0:
            primary_contact = contact

    if primary_contact is None and best_phone:
        phone_match = lead.contacts.filter(phone=best_phone).order_by("-created_at").first()
        if phone_match is None:
            phone_match = Contact.objects.create(
                lead=lead,
                name="",
                role="website-derived",
                phone=best_phone,
                linkedin_url=linkedin_url,
            )
            contacts_created += 1
        else:
            contacts_reused += 1
        primary_contact = phone_match

    return {
        "contacts_created": contacts_created,
        "contacts_reused": contacts_reused,
        "primary_contact": primary_contact,
    }
