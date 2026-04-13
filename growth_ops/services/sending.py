from __future__ import annotations

from email.utils import make_msgid

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from growth_ops.models import OutboundDraft, OutboundSend, Sequence


class DraftSendError(RuntimeError):
    def __init__(self, error_code: str, message: str, *, status_code: int):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


def _record_failed_send(draft: OutboundDraft, error_code: str, message: str) -> OutboundSend:
    return OutboundSend.objects.create(
        draft=draft,
        provider="django_smtp",
        status="failed",
        error=f"{error_code}:{message}",
    )


def send_approved_draft(*, draft: OutboundDraft) -> OutboundSend:
    if draft.approval_status != "approved":
        _record_failed_send(draft, "draft_not_approved", "Draft must be approved before sending.")
        raise DraftSendError(
            "draft_not_approved",
            "Draft must be approved before sending.",
            status_code=400,
        )

    if OutboundSend.objects.filter(draft=draft, status="sent").exists():
        raise DraftSendError(
            "draft_already_sent",
            "This draft has already been sent.",
            status_code=409,
        )

    recipient = (draft.contact.email if draft.contact else "") or ""
    if not recipient:
        _record_failed_send(draft, "missing_contact_email", "Draft contact is missing an email address.")
        raise DraftSendError(
            "missing_contact_email",
            "Draft contact is missing an email address.",
            status_code=400,
        )

    message_id = make_msgid(domain="missbott.online")
    email = EmailMessage(
        subject=draft.subject,
        body=draft.body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        headers={"Message-ID": message_id},
    )

    try:
        email.send()
    except Exception as exc:
        OutboundSend.objects.create(
            draft=draft,
            provider="django_smtp",
            provider_message_id=message_id,
            status="failed",
            error=str(exc),
        )
        raise DraftSendError("send_failed", "Sending failed.", status_code=502) from exc

    send_record = OutboundSend.objects.create(
        draft=draft,
        provider="django_smtp",
        provider_message_id=message_id,
        sent_at=timezone.now(),
        status="sent",
    )

    sequence, created = Sequence.objects.get_or_create(
        lead=draft.lead,
        defaults={
            "status": "active",
            "step": draft.sequence_step,
            "next_send_at": None,
            "meta": {"last_sent_draft_id": draft.id},
        },
    )
    if not created:
        sequence.status = "active"
        sequence.step = draft.sequence_step
        sequence.next_send_at = None
        next_meta = dict(sequence.meta or {})
        next_meta["last_sent_draft_id"] = draft.id
        sequence.meta = next_meta
        sequence.save(update_fields=["status", "step", "next_send_at", "meta"])

    if draft.lead.status != "in_sequence":
        draft.lead.status = "in_sequence"
        draft.lead.save(update_fields=["status", "updated_at"])

    return send_record
