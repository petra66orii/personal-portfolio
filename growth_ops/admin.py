from __future__ import annotations

from django.contrib import admin
from django.utils import timezone

from .models import (
    Contact,
    ContentItem,
    InboxMessage,
    Lead,
    LeadScore,
    OutboundDraft,
    OutboundSend,
    PromptLog,
    Sequence,
    WebsiteEvidence,
    WebsiteReport,
)


class DraftV3PriorityFilter(admin.SimpleListFilter):
    title = "V3 Priority"
    parameter_name = "v3_priority"

    def lookups(self, request, model_admin):
        return (
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        )

    def queryset(self, request, queryset):
        if self.value() not in {"high", "medium", "low"}:
            return queryset
        return queryset.filter(evidence_check__v3_decision__priority=self.value())


class DraftV3OfferTypeFilter(admin.SimpleListFilter):
    title = "V3 Offer"
    parameter_name = "v3_offer"

    def lookups(self, request, model_admin):
        return (
            ("conversion_fix", "Conversion Fix"),
            ("performance_sprint", "Performance Sprint"),
            ("trust_rebuild", "Trust Rebuild"),
            ("seo_hygiene", "SEO Hygiene"),
            ("general_audit", "General Audit"),
        )

    def queryset(self, request, queryset):
        if self.value() not in {
            "conversion_fix",
            "performance_sprint",
            "trust_rebuild",
            "seo_hygiene",
            "general_audit",
        }:
            return queryset
        return queryset.filter(evidence_check__v3_decision__offer_type=self.value())


class DraftReadinessFilter(admin.SimpleListFilter):
    title = "Readiness"
    parameter_name = "v35_readiness"

    def lookups(self, request, model_admin):
        return (
            ("ready", "Ready"),
            ("pending", "Pending"),
        )

    def queryset(self, request, queryset):
        if self.value() == "ready":
            return queryset.filter(evidence_check__v35_readiness__status="ready")
        if self.value() == "pending":
            return queryset.exclude(evidence_check__v35_readiness__status="ready")
        return queryset


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ("name", "role", "email", "phone", "linkedin_url", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("company_name", "market", "industry", "status", "website_url", "created_at")
    search_fields = ("company_name", "website_url", "google_place_id", "location", "industry")
    list_filter = ("market", "status", "industry", "source")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ContactInline]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "lead", "role", "created_at")
    search_fields = ("name", "email", "phone", "linkedin_url")
    list_filter = ("role", "created_at")
    autocomplete_fields = ("lead",)
    readonly_fields = ("created_at",)


@admin.register(WebsiteEvidence)
class WebsiteEvidenceAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "evidence_type", "tool", "url", "created_at")
    search_fields = ("lead__company_name", "url", "tool", "evidence_type")
    list_filter = ("evidence_type", "tool", "created_at")
    autocomplete_fields = ("lead",)
    readonly_fields = ("created_at",)


@admin.register(WebsiteReport)
class WebsiteReportAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "model", "prompt_version", "created_at")
    search_fields = ("lead__company_name", "model", "prompt_version")
    list_filter = ("model", "prompt_version", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("lead",)


@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "score", "bucket", "created_at")
    search_fields = ("lead__company_name",)
    list_filter = ("bucket", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("lead",)


@admin.action(description="Approve selected outbound drafts")
def approve_outbound_drafts(modeladmin, request, queryset):
    now = timezone.now()
    queryset.filter(approval_status="pending").update(
        approval_status="approved",
        approved_at=now,
        approved_by=request.user,
    )


@admin.action(description="Reject selected outbound drafts")
def reject_outbound_drafts(modeladmin, request, queryset):
    queryset.filter(approval_status="pending").update(
        approval_status="rejected",
        approved_at=None,
        approved_by=None,
    )


@admin.register(OutboundDraft)
class OutboundDraftAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lead",
        "contact",
        "channel",
        "sequence_step",
        "v3_priority",
        "v3_offer_type",
        "v35_readiness",
        "model",
        "prompt_version",
        "approval_status",
        "approved_at",
        "created_at",
    )
    search_fields = ("lead__company_name", "contact__email", "subject", "body")
    list_filter = (
        "approval_status",
        "channel",
        "sequence_step",
        DraftV3PriorityFilter,
        DraftV3OfferTypeFilter,
        DraftReadinessFilter,
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at", "approved_at", "approved_by")
    autocomplete_fields = ("lead", "contact", "approved_by")
    actions = [approve_outbound_drafts, reject_outbound_drafts]

    @admin.display(description="V3 Priority")
    def v3_priority(self, obj: OutboundDraft) -> str:
        evidence_check = obj.evidence_check if isinstance(obj.evidence_check, dict) else {}
        decision = evidence_check.get("v3_decision")
        if not isinstance(decision, dict):
            return "-"
        return str(decision.get("priority") or "-")

    @admin.display(description="V3 Offer")
    def v3_offer_type(self, obj: OutboundDraft) -> str:
        evidence_check = obj.evidence_check if isinstance(obj.evidence_check, dict) else {}
        decision = evidence_check.get("v3_decision")
        if not isinstance(decision, dict):
            return "-"
        return str(decision.get("offer_type") or "-")

    @admin.display(description="V3.5 Readiness")
    def v35_readiness(self, obj: OutboundDraft) -> str:
        evidence_check = obj.evidence_check if isinstance(obj.evidence_check, dict) else {}
        readiness = evidence_check.get("v35_readiness")
        if not isinstance(readiness, dict):
            return "pending"
        return str(readiness.get("status") or "pending")


@admin.register(OutboundSend)
class OutboundSendAdmin(admin.ModelAdmin):
    list_display = ("id", "draft", "provider", "status", "sent_at", "created_at")
    search_fields = ("draft__lead__company_name", "provider_message_id", "error")
    list_filter = ("status", "provider", "created_at", "sent_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("draft",)


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "status", "step", "next_send_at", "created_at")
    search_fields = ("lead__company_name",)
    list_filter = ("status", "step", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("lead",)


@admin.action(description="Approve selected suggested replies")
def approve_suggested_replies(modeladmin, request, queryset):
    queryset.filter(approval_status="pending").update(
        approval_status="approved",
        approved_at=timezone.now(),
    )


@admin.action(description="Reject selected suggested replies")
def reject_suggested_replies(modeladmin, request, queryset):
    queryset.filter(approval_status="pending").update(
        approval_status="rejected",
        approved_at=None,
    )


@admin.register(InboxMessage)
class InboxMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lead",
        "from_email",
        "classification",
        "approval_status",
        "created_at",
    )
    search_fields = ("lead__company_name", "from_email", "subject", "body", "thread_id", "message_id")
    list_filter = ("channel", "classification", "approval_status", "created_at")
    readonly_fields = ("created_at", "approved_at")
    autocomplete_fields = ("lead",)
    actions = [approve_suggested_replies, reject_suggested_replies]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ("id", "channel", "title", "status", "topic", "scheduled_at", "created_at")
    search_fields = ("title", "topic", "body")
    list_filter = ("channel", "status", "created_at", "scheduled_at")
    readonly_fields = ("created_at", "posted_at")


@admin.register(PromptLog)
class PromptLogAdmin(admin.ModelAdmin):
    list_display = ("id", "prompt_name", "prompt_version", "model", "status", "created_at")
    search_fields = ("prompt_name", "prompt_version", "model", "notes")
    list_filter = ("status", "prompt_name", "model", "created_at")
    readonly_fields = ("created_at",)
