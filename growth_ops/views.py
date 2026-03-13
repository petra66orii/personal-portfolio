from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import N8NAPIKeyAuthentication
from .models import ContentItem, InboxMessage, Lead, LeadScore, OutboundDraft, WebsiteEvidence, WebsiteReport
from .serializers import (
    ContentQueueSerializer,
    EvidenceIngestRequestSerializer,
    LeadScoreSerializer,
    LeadSerializer,
    LeadUpsertRequestSerializer,
    OutboundQueueSerializer,
    RepliesQueueSerializer,
    ReportPersistRequestSerializer,
    ScorePersistRequestSerializer,
    WebsiteReportSerializer,
)
from .services.scoring import compute_lead_score


def _normalize_website_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    return raw_url.strip().rstrip("/")


def _domain_from_url(raw_url: str) -> str:
    normalized = _normalize_website_url(raw_url)
    if not normalized:
        return ""
    parsed = urlparse(normalized if "://" in normalized else f"https://{normalized}")
    return (parsed.hostname or "").strip()


def _limit_from_request(request, *, default: int = 50, max_limit: int = 500) -> int:
    raw = request.query_params.get("limit", str(default))
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, min(value, max_limit))


def _technical_data_to_evidence_items(technical_data: dict[str, Any], default_url: str = "") -> list[dict[str, Any]]:
    type_mapping: dict[str, tuple[str, str]] = {
        "lighthouse": ("lighthouse_json", "legacy_site_auditor"),
        "pagespeed": ("pagespeed_json", "legacy_site_auditor"),
        "headers": ("homepage_headers", "legacy_site_auditor"),
        "robots": ("robots_txt", "legacy_site_auditor"),
        "sitemap": ("sitemap_xml", "legacy_site_auditor"),
        "tech_fingerprint": ("tech_fingerprint", "legacy_site_auditor"),
    }
    items: list[dict[str, Any]] = []

    for key, value in technical_data.items():
        evidence_type, tool = type_mapping.get(key, ("other", "legacy_site_auditor"))
        payload = value
        if not isinstance(payload, (dict, list)):
            payload = {"value": payload}
        items.append(
            {
                "evidence_type": evidence_type,
                "url": default_url,
                "tool": tool,
                "payload": payload,
            }
        )
    return items


class N8NProtectedAPIView(APIView):
    authentication_classes = [N8NAPIKeyAuthentication]
    permission_classes = [permissions.AllowAny]


class LeadUpsertView(N8NProtectedAPIView):
    @staticmethod
    def _find_existing_lead(validated_data: dict[str, Any]) -> Lead | None:
        google_place_id = (validated_data.get("google_place_id") or "").strip()
        website_url = _normalize_website_url(validated_data.get("website_url", ""))
        company_name = (validated_data.get("company_name") or "").strip()
        location = (validated_data.get("location") or "").strip()

        if google_place_id:
            match = Lead.objects.filter(google_place_id=google_place_id).order_by("-created_at").first()
            if match:
                return match

        if website_url:
            match = Lead.objects.filter(website_url__iexact=website_url).order_by("-created_at").first()
            if match:
                return match

        if company_name:
            queryset = Lead.objects.filter(company_name__iexact=company_name)
            if location:
                queryset = queryset.filter(location__iexact=location)
            match = queryset.order_by("-created_at").first()
            if match:
                return match

        return None

    @staticmethod
    def _upsert_contacts(lead: Lead, contacts_data: list[dict[str, Any]]) -> tuple[int, int]:
        created_count = 0
        updated_count = 0

        for contact_data in contacts_data:
            email = (contact_data.get("email") or "").strip()
            if email:
                contact, created = lead.contacts.get_or_create(
                    email=email,
                    defaults={
                        "name": contact_data.get("name", ""),
                        "role": contact_data.get("role", ""),
                        "phone": contact_data.get("phone", ""),
                        "linkedin_url": contact_data.get("linkedin_url", ""),
                    },
                )
                if created:
                    created_count += 1
                    continue

                changed = False
                for field in ("name", "role", "phone", "linkedin_url"):
                    value = contact_data.get(field)
                    if value not in (None, "") and getattr(contact, field) != value:
                        setattr(contact, field, value)
                        changed = True
                if changed:
                    contact.save()
                    updated_count += 1
                continue

            lead.contacts.create(
                name=contact_data.get("name", ""),
                role=contact_data.get("role", ""),
                phone=contact_data.get("phone", ""),
                linkedin_url=contact_data.get("linkedin_url", ""),
            )
            created_count += 1

        return created_count, updated_count

    @transaction.atomic
    def post(self, request):
        serializer = LeadUpsertRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = dict(serializer.validated_data)
        contacts_data = validated_data.pop("contacts", [])

        existing = self._find_existing_lead(validated_data)
        website_url = _normalize_website_url(validated_data.get("website_url", ""))

        if existing is None:
            company_name = (validated_data.get("company_name") or "").strip() or _domain_from_url(website_url)
            if not company_name:
                return Response(
                    {"error": "company_name_required_for_create"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            lead = Lead.objects.create(
                market=validated_data.get("market", "OTHER"),
                location=validated_data.get("location", ""),
                industry=validated_data.get("industry", ""),
                company_name=company_name,
                website_url=website_url,
                google_place_id=validated_data.get("google_place_id", ""),
                source=validated_data.get("source", "n8n"),
                status=validated_data.get("status", "new"),
                notes=validated_data.get("notes", ""),
            )
            created = True
        else:
            lead = existing
            for field in (
                "market",
                "location",
                "industry",
                "company_name",
                "google_place_id",
                "source",
                "status",
                "notes",
            ):
                value = validated_data.get(field)
                if value not in (None, ""):
                    setattr(lead, field, value)
            if website_url:
                lead.website_url = website_url
            lead.save()
            created = False

        contacts_created, contacts_updated = self._upsert_contacts(lead, contacts_data)
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
    @staticmethod
    def _resolve_lead(validated_data: dict[str, Any]) -> Lead:
        lead_id = validated_data.get("lead_id")
        if lead_id is not None:
            return get_object_or_404(Lead, pk=lead_id)

        website_url = _normalize_website_url(validated_data.get("website_url", ""))
        company_name = (validated_data.get("company_name") or "").strip()
        source = (validated_data.get("source") or "n8n").strip() or "n8n"

        if website_url:
            existing = Lead.objects.filter(website_url__iexact=website_url).order_by("-created_at").first()
            if existing:
                return existing

        if company_name:
            existing = Lead.objects.filter(company_name__iexact=company_name).order_by("-created_at").first()
            if existing:
                return existing

        fallback_name = company_name or _domain_from_url(website_url)
        if not fallback_name:
            raise Lead.DoesNotExist("Lead could not be resolved and no create fallback data was provided")

        return Lead.objects.create(
            company_name=fallback_name,
            website_url=website_url,
            market=validated_data.get("market", "OTHER"),
            source=source,
            status="new",
        )

    @transaction.atomic
    def post(self, request):
        serializer = EvidenceIngestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            lead = self._resolve_lead(validated_data)
        except Lead.DoesNotExist:
            return Response(
                {"error": "lead_not_found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        incoming_items = list(validated_data.get("items", []))
        technical_data = validated_data.get("technical_data")
        if isinstance(technical_data, dict):
            incoming_items.extend(
                _technical_data_to_evidence_items(technical_data, default_url=lead.website_url)
            )

        if not incoming_items:
            return Response(
                {"error": "no_evidence_items_provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_ids: list[int] = []
        for item in incoming_items:
            record = WebsiteEvidence.objects.create(
                lead=lead,
                evidence_type=item["evidence_type"],
                url=_normalize_website_url(item.get("url", "")) or lead.website_url,
                tool=item.get("tool", ""),
                payload=item.get("payload", {}),
            )
            created_ids.append(record.id)

        if lead.status == "new":
            lead.status = "evidence_collected"
            lead.save()

        return Response(
            {
                "lead_id": lead.id,
                "created_count": len(created_ids),
                "evidence_ids": created_ids,
            },
            status=status.HTTP_201_CREATED,
        )


class ReportPersistView(N8NProtectedAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = ReportPersistRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        lead = get_object_or_404(Lead, pk=validated_data["lead_id"])
        evidence_ids = validated_data["evidence_ids"]

        numeric_ids = set()
        for item in evidence_ids:
            try:
                numeric_ids.add(int(item))
            except (TypeError, ValueError):
                continue

        if numeric_ids:
            existing_ids = set(
                lead.website_evidence.filter(id__in=numeric_ids).values_list("id", flat=True)
            )
            missing = sorted(numeric_ids - existing_ids)
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

        report = WebsiteReport.objects.create(
            lead=lead,
            model=validated_data["model"],
            prompt_version=validated_data["prompt_version"],
            evidence_ids=evidence_ids,
            report=report_payload,
            summary=summary,
        )

        if lead.status in {"new", "evidence_collected"}:
            lead.status = "reported"
            lead.save()

        return Response(
            WebsiteReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
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

        result = compute_lead_score(lead=lead, report_obj=report_obj)

        score_record = LeadScore.objects.create(
            lead=lead,
            score=result.score,
            bucket=result.bucket,
            reason_codes=result.reason_codes,
            recommendation=result.recommendation,
        )

        if lead.status in {"new", "evidence_collected", "reported"}:
            lead.status = "scored"
            lead.save()

        return Response(
            LeadScoreSerializer(score_record).data,
            status=status.HTTP_201_CREATED,
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
