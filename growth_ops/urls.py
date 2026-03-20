from django.urls import path

from .views import (
    ContentQueueView,
    DraftCreateView,
    EvidenceIngestView,
    LeadUpsertView,
    OutboundQueueView,
    RepliesQueueView,
    ReportPersistView,
    ScorePersistView,
)

app_name = "growth_ops"

urlpatterns = [
    path("leads/upsert", LeadUpsertView.as_view(), name="leads-upsert"),
    path("evidence", EvidenceIngestView.as_view(), name="evidence-ingest"),
    path("reports", ReportPersistView.as_view(), name="reports-persist"),
    path("scores", ScorePersistView.as_view(), name="scores-persist"),
    path("drafts", DraftCreateView.as_view(), name="drafts-create"),
    path("queue/outbound", OutboundQueueView.as_view(), name="queue-outbound"),
    path("queue/replies", RepliesQueueView.as_view(), name="queue-replies"),
    path("queue/content", ContentQueueView.as_view(), name="queue-content"),
]
