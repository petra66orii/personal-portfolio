from django.urls import path

from .views import (
    ContentQueueView,
    DraftCreateView,
    DraftApproveView,
    DraftRejectView,
    EvidenceIngestView,
    LeadUpsertView,
    OutboundQueueView,
    RepliesQueueView,
    ReportPersistView,
    SendApprovedDraftView,
    ScorePersistView,
)

app_name = "growth_ops"

urlpatterns = [
    path("leads/upsert", LeadUpsertView.as_view(), name="leads-upsert"),
    path("evidence", EvidenceIngestView.as_view(), name="evidence-ingest"),
    path("reports", ReportPersistView.as_view(), name="reports-persist"),
    path("scores", ScorePersistView.as_view(), name="scores-persist"),
    path("drafts", DraftCreateView.as_view(), name="drafts-create"),
    path("drafts/<int:draft_id>/approve", DraftApproveView.as_view(), name="drafts-approve"),
    path("drafts/<int:draft_id>/reject", DraftRejectView.as_view(), name="drafts-reject"),
    path("send-approved", SendApprovedDraftView.as_view(), name="send-approved"),
    path("queue/outbound", OutboundQueueView.as_view(), name="queue-outbound"),
    path("queue/replies", RepliesQueueView.as_view(), name="queue-replies"),
    path("queue/content", ContentQueueView.as_view(), name="queue-content"),
]
