from __future__ import annotations

from typing import Any

from rest_framework import serializers

from .models import (
    Contact,
    ContentItem,
    InboxMessage,
    Lead,
    LeadScore,
    OutboundDraft,
    WebsiteEvidence,
    WebsiteReport,
)


class ContactInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.CharField(max_length=120, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)


class LeadUpsertRequestSerializer(serializers.Serializer):
    market = serializers.ChoiceField(
        choices=[choice[0] for choice in Lead.MARKET_CHOICES],
        required=False,
    )
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    industry = serializers.CharField(max_length=120, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    website_url = serializers.URLField(required=False, allow_blank=True)
    google_place_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    source = serializers.CharField(max_length=64, required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=[choice[0] for choice in Lead.STATUS_CHOICES],
        required=False,
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    contacts = ContactInputSerializer(many=True, required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not any(
            [
                attrs.get("google_place_id"),
                attrs.get("website_url"),
                attrs.get("company_name"),
            ]
        ):
            raise serializers.ValidationError(
                "At least one of google_place_id, website_url, or company_name is required."
            )
        return attrs


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id",
            "created_at",
            "updated_at",
            "market",
            "location",
            "industry",
            "company_name",
            "website_url",
            "google_place_id",
            "source",
            "status",
            "notes",
        ]


class EvidenceItemInputSerializer(serializers.Serializer):
    evidence_type = serializers.ChoiceField(choices=[choice[0] for choice in WebsiteEvidence.EVIDENCE_TYPE_CHOICES])
    url = serializers.URLField(required=False, allow_blank=True)
    tool = serializers.CharField(max_length=64, required=False, allow_blank=True)
    payload = serializers.JSONField()


class EvidenceIngestRequestSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField(required=False)
    website_url = serializers.URLField(required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    market = serializers.ChoiceField(
        choices=[choice[0] for choice in Lead.MARKET_CHOICES],
        required=False,
    )
    source = serializers.CharField(max_length=64, required=False, allow_blank=True)
    items = EvidenceItemInputSerializer(many=True, required=False)
    technical_data = serializers.JSONField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("items") and "technical_data" not in attrs:
            raise serializers.ValidationError("Either items or technical_data is required.")
        return attrs


class ReportPersistRequestSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    model = serializers.CharField(max_length=128)
    prompt_version = serializers.CharField(max_length=64)
    evidence_ids = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=False,
    )
    report = serializers.JSONField()
    summary = serializers.CharField(required=False, allow_blank=True)


class WebsiteReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteReport
        fields = [
            "id",
            "lead",
            "created_at",
            "model",
            "prompt_version",
            "evidence_ids",
            "report",
            "summary",
        ]


class ScorePersistRequestSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    report_id = serializers.IntegerField(required=False)


class LeadScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadScore
        fields = [
            "id",
            "lead",
            "created_at",
            "score",
            "bucket",
            "reason_codes",
            "recommendation",
        ]


class OutboundQueueSerializer(serializers.ModelSerializer):
    lead_company_name = serializers.CharField(source="lead.company_name", read_only=True)
    contact_email = serializers.EmailField(source="contact.email", read_only=True)

    class Meta:
        model = OutboundDraft
        fields = [
            "id",
            "lead",
            "lead_company_name",
            "contact",
            "contact_email",
            "channel",
            "sequence_step",
            "subject",
            "body",
            "approval_status",
            "created_at",
            "approved_at",
        ]


class RepliesQueueSerializer(serializers.ModelSerializer):
    lead_company_name = serializers.CharField(source="lead.company_name", read_only=True)

    class Meta:
        model = InboxMessage
        fields = [
            "id",
            "lead",
            "lead_company_name",
            "channel",
            "thread_id",
            "message_id",
            "from_email",
            "subject",
            "classification",
            "approval_status",
            "created_at",
        ]


class ContentQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = [
            "id",
            "channel",
            "title",
            "topic",
            "status",
            "scheduled_at",
            "created_at",
        ]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "lead", "name", "role", "email", "phone", "linkedin_url", "created_at"]


class DraftCreateRequestSerializer(serializers.Serializer):
    lead_id = serializers.IntegerField()
    contact_id = serializers.IntegerField(required=False)
    channel = serializers.ChoiceField(
        choices=[choice[0] for choice in OutboundDraft.CHANNEL_CHOICES],
        default="email",
    )
    sequence_step = serializers.IntegerField(min_value=1, max_value=10, default=1)


class OutboundDraftDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutboundDraft
        fields = [
            "id",
            "lead",
            "contact",
            "created_at",
            "updated_at",
            "channel",
            "sequence_step",
            "subject",
            "body",
            "model",
            "prompt_version",
            "proof_points",
            "risk_flags",
            "evidence_check",
            "approval_status",
            "approved_at",
            "approved_by",
        ]


class SendApprovedDraftRequestSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField()
