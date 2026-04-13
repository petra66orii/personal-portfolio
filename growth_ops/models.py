from __future__ import annotations

from django.conf import settings
from django.db import models


class Lead(models.Model):
    MARKET_CHOICES = (
        ("IE", "Ireland"),
        ("RO", "Romania"),
        ("US", "United States"),
        ("OTHER", "Other"),
    )
    STATUS_CHOICES = (
        ("new", "New"),
        ("evidence_collected", "Evidence Collected"),
        ("reported", "Reported"),
        ("scored", "Scored"),
        ("draft_pending", "Draft Pending"),
        ("in_sequence", "In Sequence"),
        ("replied", "Replied"),
        ("archived", "Archived"),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    market = models.CharField(max_length=12, choices=MARKET_CHOICES, default="OTHER", db_index=True)
    location = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=120, blank=True, db_index=True)
    company_name = models.CharField(max_length=255, db_index=True)
    website_url = models.URLField(blank=True)
    google_place_id = models.CharField(max_length=128, blank=True, db_index=True)
    source = models.CharField(max_length=64, default="n8n", db_index=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="new", db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "created_at"), name="growth_lead_status_created_idx"),
            models.Index(fields=("market", "industry"), name="gops_lead_mkt_ind_idx"),
        ]

    def __str__(self) -> str:
        return self.company_name


class Contact(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contacts")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    linkedin_url = models.URLField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("lead", "email"), name="growth_contact_lead_email_idx"),
        ]

    def __str__(self) -> str:
        if self.email:
            return self.email
        return f"Contact {self.pk}"


class WebsiteEvidence(models.Model):
    EVIDENCE_TYPE_CHOICES = (
        ("lighthouse_json", "Lighthouse JSON"),
        ("pagespeed_json", "PageSpeed JSON"),
        ("homepage_headers", "Homepage Headers"),
        ("robots_txt", "robots.txt"),
        ("sitemap_xml", "sitemap.xml"),
        ("homepage_html_snippet", "Homepage HTML Snippet"),
        ("contact_html_snippet", "Contact HTML Snippet"),
        ("service_html_snippet", "Service HTML Snippet"),
        ("tech_fingerprint", "Tech Fingerprint"),
        ("other", "Other"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="website_evidence")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    evidence_type = models.CharField(max_length=64, choices=EVIDENCE_TYPE_CHOICES, db_index=True)
    url = models.URLField(blank=True)
    tool = models.CharField(max_length=64, blank=True, db_index=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("lead", "evidence_type"), name="growth_evidence_lead_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.lead_id} {self.evidence_type}"


class WebsiteReport(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="website_reports")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    model = models.CharField(max_length=128, db_index=True)
    prompt_version = models.CharField(max_length=64, db_index=True)
    evidence_ids = models.JSONField(default=list, blank=True)
    report = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("lead", "created_at"), name="growth_report_lead_created_idx"),
        ]

    def __str__(self) -> str:
        return f"Report {self.pk} ({self.model})"


class LeadScore(models.Model):
    BUCKET_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="scores")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    score = models.IntegerField(db_index=True)
    bucket = models.CharField(max_length=1, choices=BUCKET_CHOICES, db_index=True)
    reason_codes = models.JSONField(default=list, blank=True)
    recommendation = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("bucket", "score"), name="growth_score_bucket_score_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.lead_id} {self.score} ({self.bucket})"


class OutboundDraft(models.Model):
    CHANNEL_CHOICES = (
        ("email", "Email"),
        ("linkedin", "LinkedIn"),
    )
    APPROVAL_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="outbound_drafts")
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbound_drafts",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES, default="email", db_index=True)
    sequence_step = models.PositiveSmallIntegerField(default=1, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    model = models.CharField(max_length=128, blank=True)
    prompt_version = models.CharField(max_length=64, blank=True)
    proof_points = models.JSONField(default=list, blank=True)
    risk_flags = models.JSONField(default=list, blank=True)
    evidence_check = models.JSONField(default=dict, blank=True)
    approval_status = models.CharField(
        max_length=16,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_outbound_drafts",
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("approval_status", "created_at"), name="gops_draft_stat_cr_idx"),
            models.Index(fields=("lead", "sequence_step"), name="growth_draft_lead_step_idx"),
        ]

    def __str__(self) -> str:
        return f"Draft {self.pk} ({self.approval_status})"


class OutboundSend(models.Model):
    STATUS_CHOICES = (
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("bounced", "Bounced"),
        ("replied", "Replied"),
    )

    draft = models.ForeignKey(OutboundDraft, on_delete=models.CASCADE, related_name="sends")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    provider = models.CharField(max_length=64, default="django_smtp")
    provider_message_id = models.CharField(max_length=255, blank=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="queued", db_index=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("draft",),
                condition=models.Q(status="sent"),
                name="growth_send_one_sent_per_draft",
            ),
        ]
        indexes = [
            models.Index(fields=("status", "created_at"), name="growth_send_status_created_idx"),
        ]

    def __str__(self) -> str:
        return f"Send {self.pk} ({self.status})"


class Sequence(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("stopped_on_reply", "Stopped On Reply"),
        ("cancelled", "Cancelled"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="sequences")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="active", db_index=True)
    step = models.PositiveSmallIntegerField(default=1, db_index=True)
    next_send_at = models.DateTimeField(null=True, blank=True, db_index=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("lead",), name="growth_sequence_unique_lead"),
        ]
        indexes = [
            models.Index(fields=("status", "next_send_at"), name="growth_seq_status_nextsend_idx"),
        ]

    def __str__(self) -> str:
        return f"Sequence {self.pk} ({self.status})"


class InboxMessage(models.Model):
    CHANNEL_CHOICES = (
        ("email", "Email"),
        ("linkedin", "LinkedIn"),
    )
    CLASSIFICATION_CHOICES = (
        ("interested", "Interested"),
        ("needs_more_info", "Needs More Info"),
        ("not_now", "Not Now"),
        ("not_a_fit", "Not A Fit"),
        ("unsubscribe", "Unsubscribe"),
        ("out_of_office", "Out Of Office"),
        ("unknown", "Unknown"),
    )
    APPROVAL_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbox_messages",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES, default="email", db_index=True)
    thread_id = models.CharField(max_length=255, blank=True, db_index=True)
    message_id = models.CharField(max_length=255, blank=True, db_index=True)
    from_email = models.EmailField(blank=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    classification = models.CharField(
        max_length=32,
        choices=CLASSIFICATION_CHOICES,
        default="unknown",
        db_index=True,
    )
    suggested_reply = models.TextField(blank=True)
    approval_status = models.CharField(
        max_length=16,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("approval_status", "classification"), name="growth_inbox_status_class_idx"),
        ]

    def __str__(self) -> str:
        return f"Inbox {self.pk} ({self.classification})"


class ContentItem(models.Model):
    CHANNEL_CHOICES = (
        ("linkedin", "LinkedIn"),
        ("blog", "Blog"),
    )
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("posted", "Posted"),
        ("rejected", "Rejected"),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    channel = models.CharField(max_length=24, choices=CHANNEL_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    model = models.CharField(max_length=128, blank=True)
    prompt_version = models.CharField(max_length=64, blank=True)
    topic = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="draft", db_index=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    posted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "scheduled_at"), name="gops_content_stat_sched_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.channel}: {self.title}"


class PromptLog(models.Model):
    STATUS_CHOICES = (
        ("success", "Success"),
        ("error", "Error"),
        ("invalid_schema", "Invalid Schema"),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    prompt_name = models.CharField(max_length=128, db_index=True)
    prompt_version = models.CharField(max_length=64, db_index=True)
    model = models.CharField(max_length=128, db_index=True)
    input_payload = models.JSONField(default=dict, blank=True)
    output_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("prompt_name", "prompt_version"), name="growth_prompt_name_ver_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.prompt_name} {self.status}"
