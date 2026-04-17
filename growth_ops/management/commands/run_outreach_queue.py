from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from growth_ops.models import OutboundDraft

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _draft_priority(draft: OutboundDraft) -> str:
    evidence_check = draft.evidence_check if isinstance(draft.evidence_check, dict) else {}
    decision = evidence_check.get("v3_decision")
    value = ""
    if isinstance(decision, dict):
        value = str(decision.get("priority") or "").strip().lower()
    if not value:
        value = str(evidence_check.get("priority") or "").strip().lower()
    if not value:
        diagnostics = evidence_check.get("v35_diagnostics")
        if isinstance(diagnostics, dict):
            value = str(diagnostics.get("priority") or "").strip().lower()
    if not value:
        value = "low"
    return value if value in PRIORITY_ORDER else "low"


def _draft_readiness_status(draft: OutboundDraft) -> str:
    evidence_check = draft.evidence_check if isinstance(draft.evidence_check, dict) else {}
    readiness = evidence_check.get("v35_readiness")
    value = ""
    if isinstance(readiness, dict):
        value = str(readiness.get("status") or "").strip().lower()
    if not value:
        value = str(evidence_check.get("readiness_status") or "").strip().lower()
    if not value:
        diagnostics = evidence_check.get("v35_diagnostics")
        if isinstance(diagnostics, dict):
            value = str(diagnostics.get("readiness_status") or "").strip().lower()
    if not value:
        value = "pending"
    return value if value in {"ready", "pending"} else "pending"


def _draft_contact_route(draft: OutboundDraft) -> str:
    if draft.contact and draft.contact.email:
        return draft.contact.email
    evidence_check = draft.evidence_check if isinstance(draft.evidence_check, dict) else {}
    selected_email = str(evidence_check.get("selected_email") or "").strip()
    if selected_email:
        return selected_email
    contacts = evidence_check.get("v35_contacts")
    if isinstance(contacts, dict):
        best_email = str(contacts.get("best_email") or "").strip()
        if best_email:
            return best_email
    diagnostics = evidence_check.get("v35_diagnostics")
    if isinstance(diagnostics, dict):
        selected_email_from_diag = str(diagnostics.get("selected_email") or "").strip()
        if selected_email_from_diag:
            return selected_email_from_diag

    if draft.contact and draft.contact.phone:
        return str(draft.contact.phone).strip()
    selected_phone = str(evidence_check.get("selected_phone") or "").strip()
    if selected_phone:
        return selected_phone
    if isinstance(contacts, dict):
        best_phone = str(contacts.get("best_phone") or "").strip()
        if best_phone:
            return best_phone
    if isinstance(diagnostics, dict):
        selected_phone_from_diag = str(diagnostics.get("selected_phone") or "").strip()
        if selected_phone_from_diag:
            return selected_phone_from_diag

    selected_contact_link = str(evidence_check.get("selected_contact_link") or "").strip()
    if selected_contact_link:
        return selected_contact_link
    if isinstance(contacts, dict):
        selected_contact_from_contacts = str(contacts.get("selected_contact_link") or "").strip()
        if selected_contact_from_contacts:
            return selected_contact_from_contacts
        contact_links = contacts.get("contact_links")
        if isinstance(contact_links, list):
            for link in contact_links:
                normalized = str(link or "").strip()
                if normalized:
                    return normalized
    if isinstance(diagnostics, dict):
        selected_contact_from_diag = str(diagnostics.get("selected_contact_link") or "").strip()
        if selected_contact_from_diag:
            return selected_contact_from_diag
    contact_links_root = evidence_check.get("contact_links")
    if isinstance(contact_links_root, list):
        for link in contact_links_root:
            normalized = str(link or "").strip()
            if normalized:
                return normalized
    return ""


class Command(BaseCommand):
    help = "Print a deterministic outreach review queue from existing drafts."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum drafts to print (default: 20).",
        )
        parser.add_argument(
            "--priority",
            choices=["high", "medium", "low"],
            help="Optional priority filter.",
        )
        parser.add_argument(
            "--ready-only",
            action="store_true",
            default=True,
            help="Show ready drafts only (default: true).",
        )
        parser.add_argument(
            "--include-pending",
            action="store_true",
            help="Include pending drafts as well.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        limit: int = max(1, int(options.get("limit") or 20))
        priority_filter: str | None = options.get("priority")
        include_pending: bool = bool(options.get("include_pending"))
        ready_only: bool = bool(options.get("ready_only")) and not include_pending

        queryset = (
            OutboundDraft.objects.select_related("lead", "contact")
            .filter(channel="email")
            .order_by("-created_at")
        )
        drafts = list(queryset)
        failures = 0
        filtered: list[OutboundDraft] = []
        drafts_ready = 0
        drafts_pending = 0

        for draft in drafts:
            try:
                priority = _draft_priority(draft)
                readiness = _draft_readiness_status(draft)
                if priority_filter and priority != priority_filter:
                    continue
                if readiness == "ready":
                    drafts_ready += 1
                else:
                    drafts_pending += 1
                if ready_only and readiness != "ready":
                    continue
                filtered.append(draft)
            except Exception:
                failures += 1

        filtered.sort(
            key=lambda draft: (
                PRIORITY_ORDER.get(_draft_priority(draft), 3),
                -int(draft.created_at.timestamp()),
            )
        )
        selected = filtered[:limit]
        drafts_considered = len(filtered)

        self.stdout.write(
            self.style.NOTICE(
                f"Outreach queue: considered={drafts_considered} ready_only={ready_only} priority={priority_filter or 'all'}"
            )
        )
        for index, draft in enumerate(selected, start=1):
            priority = _draft_priority(draft)
            readiness = _draft_readiness_status(draft)
            contact_route = _draft_contact_route(draft) or "-"
            subject = (draft.subject or "").strip()
            self.stdout.write(
                f"[{index}] draft_id={draft.id} lead=\"{draft.lead.company_name}\" "
                f"priority={priority} readiness={readiness} contact={contact_route} subject=\"{subject}\""
            )

        self.stdout.write("")
        self.stdout.write(f"drafts_considered: {drafts_considered}")
        self.stdout.write(f"drafts_ready: {drafts_ready}")
        self.stdout.write(f"drafts_pending: {drafts_pending}")
        self.stdout.write(f"failures: {failures}")
