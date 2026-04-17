from __future__ import annotations

from typing import Any

from growth_ops.models import Contact, OutboundDraft


def classify_draft_readiness(
    *,
    draft: OutboundDraft,
    primary_contact: Contact | None = None,
    extracted_contacts: dict[str, Any] | None = None,
) -> dict[str, str]:
    extracted = extracted_contacts or {}

    linked_contact = primary_contact or draft.contact
    if linked_contact is not None and str(linked_contact.email or "").strip():
        return {
            "status": "ready",
            "reason": "linked_contact_email_available",
            "contactability_type": "email",
        }

    best_email = str(extracted.get("best_email") or "").strip()
    if best_email:
        return {
            "status": "ready",
            "reason": "extracted_email_available",
            "contactability_type": "email",
        }

    linked_phone = str((linked_contact.phone if linked_contact is not None else "") or "").strip()
    best_phone = str(extracted.get("best_phone") or "").strip()
    if linked_phone or best_phone:
        return {
            "status": "ready",
            "reason": "phone_contact_route_available",
            "contactability_type": "phone",
        }

    selected_contact_link = str(extracted.get("selected_contact_link") or "").strip()
    if selected_contact_link:
        return {
            "status": "ready",
            "reason": "contact_link_route_available",
            "contactability_type": "contact_link",
        }

    contact_links = extracted.get("contact_links")
    if isinstance(contact_links, list):
        usable_links = [str(link).strip() for link in contact_links if str(link).strip()]
        if usable_links:
            return {
                "status": "ready",
                "reason": "contact_link_route_available",
                "contactability_type": "contact_link",
            }

    return {
        "status": "pending",
        "reason": "no_usable_contact_route_found",
        "contactability_type": "none",
    }
