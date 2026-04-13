from __future__ import annotations

from email.utils import make_msgid

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from django.utils import timezone

from growth_ops.models import OutboundDraft, OutboundSend, Sequence


class DraftSendError(RuntimeError):
    def __init__(
        self,
        error_code: str,
        message: str,
        *,
        status_code: int,
        log_failure: bool = False,
        provider_message_id: str = "",
    ):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code
        self.log_failure = log_failure
        self.provider_message_id = provider_message_id


def _record_failed_send(draft: OutboundDraft, error_code: str, message: str) -> OutboundSend:
    return OutboundSend.objects.create(
        draft=draft,
        provider="django_smtp",
        status="failed",
        error=f"{error_code}:{message}",
    )


def _resolve_message_id_domain() -> str:
    configured_domain = str(getattr(settings, "EMAIL_MESSAGE_ID_DOMAIN", "") or "").strip()
    if configured_domain:
        return configured_domain

    default_from_email = str(getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
    if "@" in default_from_email:
        return default_from_email.rsplit("@", 1)[1]

    return "localhost"


def send_approved_draft(*, draft: OutboundDraft) -> OutboundSend:
    try:
        with transaction.atomic():
            locked_draft = (
                OutboundDraft.objects.select_for_update()
                .select_related("lead", "contact")
                .get(pk=draft.pk)
            )

            if locked_draft.channel != "email":
                raise DraftSendError(
                    "unsupported_channel",
                    "Only email drafts can be sent via this endpoint.",
                    status_code=400,
                    log_failure=True,
                )

            if locked_draft.approval_status != "approved":
                raise DraftSendError(
                    "draft_not_approved",
                    "Draft must be approved before sending.",
                    status_code=400,
                    log_failure=True,
                )

            if OutboundSend.objects.filter(draft=locked_draft, status="sent").exists():
                raise DraftSendError(
                    "draft_already_sent",
                    "This draft has already been sent.",
                    status_code=409,
                )

            recipient = (locked_draft.contact.email if locked_draft.contact else "") or ""
            if not recipient:
                raise DraftSendError(
                    "missing_contact_email",
                    "Draft contact is missing an email address.",
                    status_code=400,
                    log_failure=True,
                )

            message_id = make_msgid(domain=_resolve_message_id_domain())
            email = EmailMessage(
                subject=locked_draft.subject,
                body=locked_draft.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                headers={"Message-ID": message_id},
            )

            try:
                send_count = email.send()
            except Exception as exc:
                raise DraftSendError(
                    "send_failed",
                    str(exc),
                    status_code=502,
                    log_failure=True,
                    provider_message_id=message_id,
                ) from exc

            if send_count < 1:
                raise DraftSendError(
                    "send_not_accepted",
                    "Email backend did not accept the message.",
                    status_code=502,
                    log_failure=True,
                    provider_message_id=message_id,
                )

            try:
                send_record = OutboundSend.objects.create(
                    draft=locked_draft,
                    provider="django_smtp",
                    provider_message_id=message_id,
                    sent_at=timezone.now(),
                    status="sent",
                )
            except IntegrityError as exc:
                raise DraftSendError(
                    "draft_already_sent",
                    "This draft has already been sent.",
                    status_code=409,
                ) from exc

            next_meta = {"last_sent_draft_id": locked_draft.id}
            try:
                Sequence.objects.update_or_create(
                    lead=locked_draft.lead,
                    defaults={
                        "status": "active",
                        "step": locked_draft.sequence_step,
                        "next_send_at": None,
                        "meta": next_meta,
                    },
                )
            except Sequence.MultipleObjectsReturned:
                sequence = Sequence.objects.filter(lead=locked_draft.lead).order_by("-created_at", "-id").first()
                if sequence is not None:
                    sequence.status = "active"
                    sequence.step = locked_draft.sequence_step
                    sequence.next_send_at = None
                    sequence.meta = next_meta
                    sequence.save(update_fields=["status", "step", "next_send_at", "meta"])
                    Sequence.objects.filter(lead=locked_draft.lead).exclude(pk=sequence.pk).delete()

            if locked_draft.lead.status != "in_sequence":
                locked_draft.lead.status = "in_sequence"
                locked_draft.lead.save(update_fields=["status", "updated_at"])

            return send_record
    except DraftSendError as exc:
        if exc.log_failure:
            if exc.error_code in {"send_failed", "send_not_accepted"}:
                OutboundSend.objects.create(
                    draft=draft,
                    provider="django_smtp",
                    provider_message_id=exc.provider_message_id,
                    status="failed",
                    error=str(exc),
                )
            else:
                _record_failed_send(draft, exc.error_code, str(exc))
        raise
