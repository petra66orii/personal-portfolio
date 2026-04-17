from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import N8NAPIKeyAuthentication
from .models import Contact, ContentItem, InboxMessage, Lead, OutboundDraft, WebsiteReport
from .serializers import (
    ContentQueueSerializer,
    DraftCreateRequestSerializer,
    EvidenceIngestRequestSerializer,
    LeadScoreSerializer,
    LeadSerializer,
    LeadUpsertRequestSerializer,
    OutboundDraftDetailSerializer,
    OutboundQueueSerializer,
    RepliesQueueSerializer,
    ReportPersistRequestSerializer,
    SendApprovedDraftRequestSerializer,
    ScorePersistRequestSerializer,
    WebsiteReportSerializer,
)
from .services.llm_gateway import LLMGatewayError
from .services.outreach import LeadNotDraftableError, OutreachDraftingError, create_outbound_draft
from .services.sending import DraftSendError, send_approved_draft
from .services.evidence_ingest import (
    persist_evidence_items,
    resolve_lead_for_evidence,
    technical_data_to_evidence_items,
)
from .services.lead_ingest import upsert_contacts, upsert_lead_from_candidate
from .services.reporting import upsert_report, validate_evidence_ids_for_lead
from .services.scoring_pipeline import upsert_lead_score


def _limit_from_request(request, *, default: int = 50, max_limit: int = 500) -> int:
    raw = request.query_params.get("limit", str(default))
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, min(value, max_limit))


class N8NProtectedAPIView(APIView):
    authentication_classes = [N8NAPIKeyAuthentication]
    permission_classes = [permissions.AllowAny]


class LeadUpsertView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = LeadUpsertRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = dict(serializer.validated_data)
        contacts_data = validated_data.pop("contacts", [])

        try:
            lead, created = upsert_lead_from_candidate(validated_data)
        except ValueError as exc:
            if str(exc) == "company_name_required_for_create":
                return Response(
                    {"error": "company_name_required_for_create"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            raise

        contacts_created, contacts_updated = upsert_contacts(lead, contacts_data)
        response_payload = {
            "created": created,
            "lead": LeadSerializer(lead).data,
            "contacts_created": contacts_created,
            "contacts_updated": contacts_updated,
        }
        return Response(
            response_payload,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class EvidenceIngestView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = EvidenceIngestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            lead = resolve_lead_for_evidence(dict(validated_data))
        except Lead.DoesNotExist:
            if validated_data.get("lead_id") is not None:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(
                {"error": "lead_not_found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        incoming_items = list(validated_data.get("items", []))
        technical_data = validated_data.get("technical_data")
        if isinstance(technical_data, dict):
            incoming_items.extend(
                technical_data_to_evidence_items(technical_data, default_url=lead.website_url)
            )

        if not incoming_items:
            return Response(
                {"error": "no_evidence_items_provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = persist_evidence_items(lead=lead, items=incoming_items)
        return Response(
            result,
            status=status.HTTP_201_CREATED if result["created_count"] else status.HTTP_200_OK,
        )


class ReportPersistView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = ReportPersistRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        lead = get_object_or_404(Lead, pk=validated_data["lead_id"])
        evidence_ids = list(validated_data["evidence_ids"])
        missing = validate_evidence_ids_for_lead(lead, evidence_ids)
        if missing:
            return Response(
                {"error": "invalid_evidence_ids", "missing_ids": missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report_payload = validated_data["report"]
        summary = validated_data.get("summary", "").strip()
        if not summary and isinstance(report_payload, dict):
            summary = str(
                report_payload.get("executive_summary")
                or report_payload.get("summary")
                or ""
            ).strip()

        report, created = upsert_report(
            lead=lead,
            report_payload=report_payload,
            evidence_ids=evidence_ids,
            model=validated_data["model"],
            prompt_version=validated_data["prompt_version"],
            summary=summary,
            force=False,
        )

        return Response(
            WebsiteReportSerializer(report).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ScorePersistView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = ScorePersistRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        lead = get_object_or_404(Lead, pk=validated_data["lead_id"])

        report_id = validated_data.get("report_id")
        report_obj: WebsiteReport | None
        if report_id is not None:
            report_obj = get_object_or_404(WebsiteReport, pk=report_id, lead=lead)
        else:
            report_obj = lead.website_reports.order_by("-created_at").first()

        score_record, created = upsert_lead_score(
            lead=lead,
            report_obj=report_obj,
            force=False,
        )

        return Response(
            LeadScoreSerializer(score_record).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class DraftCreateView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = DraftCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        lead = get_object_or_404(Lead, pk=validated["lead_id"])
        contact: Contact | None = None
        contact_id = validated.get("contact_id")
        if contact_id is not None:
            contact = get_object_or_404(Contact, pk=contact_id, lead=lead)

        try:
            draft = create_outbound_draft(
                lead=lead,
                contact=contact,
                sequence_step=validated["sequence_step"],
                channel=validated["channel"],
            )
        except LeadNotDraftableError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except OutreachDraftingError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except LLMGatewayError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            OutboundDraftDetailSerializer(draft).data,
            status=status.HTTP_201_CREATED,
        )


class DraftApproveView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request, draft_id: int):
        draft = get_object_or_404(OutboundDraft, pk=draft_id)
        if draft.approval_status != "approved":
            draft.approval_status = "approved"
            draft.approved_at = timezone.now()
            draft.approved_by = request.user if getattr(request.user, "is_authenticated", False) else None
            draft.save(update_fields=["approval_status", "approved_at", "approved_by", "updated_at"])
        return Response(OutboundDraftDetailSerializer(draft).data, status=status.HTTP_200_OK)


class DraftRejectView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request, draft_id: int):
        draft = get_object_or_404(OutboundDraft, pk=draft_id)
        draft.approval_status = "rejected"
        draft.approved_at = None
        draft.approved_by = None
        draft.save(update_fields=["approval_status", "approved_at", "approved_by", "updated_at"])
        return Response(OutboundDraftDetailSerializer(draft).data, status=status.HTTP_200_OK)


class SendApprovedDraftView(N8NProtectedAPIView):
    def post(self, request):
        serializer = SendApprovedDraftRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        draft = get_object_or_404(
            OutboundDraft.objects.select_related("lead", "contact"),
            pk=serializer.validated_data["draft_id"],
        )

        try:
            send_record = send_approved_draft(draft=draft)
        except DraftSendError as exc:
            return Response(
                {"error_code": exc.error_code, "error": str(exc)},
                status=exc.status_code,
            )

        return Response(
            {
                "status": "sent",
                "draft_id": draft.id,
                "send_id": send_record.id,
                "provider_message_id": send_record.provider_message_id,
            },
            status=status.HTTP_200_OK,
        )


class OutboundQueueView(N8NProtectedAPIView):
    def get(self, request):
        allowed = {choice[0] for choice in OutboundDraft.APPROVAL_STATUS_CHOICES}
        status_filter = request.query_params.get("status", "pending")
        if status_filter not in allowed:
            return Response(
                {"error": "invalid_status_filter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = _limit_from_request(request)
        queryset = (
            OutboundDraft.objects.select_related("lead", "contact")
            .filter(approval_status=status_filter)
            .order_by("created_at")
        )
        total = queryset.count()
        results = OutboundQueueSerializer(queryset[:limit], many=True).data
        return Response({"count": total, "limit": limit, "results": results}, status=status.HTTP_200_OK)


class RepliesQueueView(N8NProtectedAPIView):
    def get(self, request):
        allowed = {choice[0] for choice in InboxMessage.APPROVAL_STATUS_CHOICES}
        status_filter = request.query_params.get("status", "pending")
        if status_filter not in allowed:
            return Response(
                {"error": "invalid_status_filter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = _limit_from_request(request)
        queryset = (
            InboxMessage.objects.select_related("lead")
            .filter(approval_status=status_filter)
            .order_by("created_at")
        )
        total = queryset.count()
        results = RepliesQueueSerializer(queryset[:limit], many=True).data
        return Response({"count": total, "limit": limit, "results": results}, status=status.HTTP_200_OK)


class ContentQueueView(N8NProtectedAPIView):
    def get(self, request):
        allowed = {choice[0] for choice in ContentItem.STATUS_CHOICES}
        status_filter = request.query_params.get("status", "pending_approval")
        if status_filter not in allowed:
            return Response(
                {"error": "invalid_status_filter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = _limit_from_request(request)
        queryset = ContentItem.objects.filter(status=status_filter).order_by("created_at")
        total = queryset.count()
        results = ContentQueueSerializer(queryset[:limit], many=True).data
        return Response({"count": total, "limit": limit, "results": results}, status=status.HTTP_200_OK)
