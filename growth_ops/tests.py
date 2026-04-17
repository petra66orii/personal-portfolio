from __future__ import annotations

import os
from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from growth_ops.models import (
    ContentItem,
    InboxMessage,
    Lead,
    LeadScore,
    OutboundDraft,
    OutboundSend,
    Sequence,
    WebsiteEvidence,
    WebsiteReport,
)
from growth_ops.services.evidence_checker import check_proof_points
from growth_ops.services.contact_enrichment import upsert_contacts_for_lead
from growth_ops.services.contact_finder import extract_contact_candidates
from growth_ops.services.llm_gateway import LLMGatewayClient
from growth_ops.services.outreach_readiness import classify_draft_readiness
from growth_ops.services.scoring_pipeline import run_outreach_for_lead


@override_settings(
    N8N_DJANGO_API_KEY="test-n8n-key",
    DEFAULT_FROM_EMAIL="hello@missbott.test",
)
class GrowthOpsAPITests(APITestCase):
    api_key = "test-n8n-key"

    @property
    def headers(self) -> dict[str, str]:
        return {"HTTP_X_N8N_API_KEY": self.api_key}

    def test_api_key_auth_required(self):
        url = "/api/growth/leads/upsert"
        payload = {"company_name": "Acme Ltd"}

        no_key_response = self.client.post(url, data=payload, format="json")
        self.assertEqual(no_key_response.status_code, 401)

        bad_key_response = self.client.post(
            url,
            data=payload,
            format="json",
            HTTP_X_N8N_API_KEY="wrong-key",
        )
        self.assertEqual(bad_key_response.status_code, 401)

        ok_response = self.client.post(url, data=payload, format="json", **self.headers)
        self.assertEqual(ok_response.status_code, 201)
        self.assertTrue(ok_response.data["created"])

    def test_evidence_ingest_is_idempotent_for_duplicate_payloads(self):
        lead = Lead.objects.create(company_name="Evidence Co", website_url="https://evidence.example")

        payload = {
            "lead_id": lead.id,
            "items": [
                {
                    "evidence_type": "lighthouse_json",
                    "url": "https://evidence.example",
                    "tool": "pagespeed",
                    "payload": {"performance_score": 42, "lcp_ms": 3200},
                },
                {
                    "evidence_type": "homepage_headers",
                    "url": "https://evidence.example",
                    "tool": "http_head",
                    "payload": {"server": "nginx"},
                },
            ],
        }

        response_1 = self.client.post("/api/growth/evidence", data=payload, format="json", **self.headers)
        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_1.data["created_count"], 2)
        self.assertEqual(WebsiteEvidence.objects.filter(lead=lead).count(), 2)

        response_2 = self.client.post("/api/growth/evidence", data=payload, format="json", **self.headers)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_2.data["created_count"], 0)
        self.assertEqual(response_2.data["reused_count"], 2)
        self.assertEqual(WebsiteEvidence.objects.filter(lead=lead).count(), 2)

    def test_report_persistence(self):
        lead = Lead.objects.create(company_name="Report Co", website_url="https://report.example")
        ev1 = WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="lighthouse_json",
            url=lead.website_url,
            tool="pagespeed",
            payload={"performance_score": 50},
        )
        ev2 = WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="tech_fingerprint",
            url=lead.website_url,
            tool="fingerprint",
            payload={"cms": "wordpress"},
        )

        payload = {
            "lead_id": lead.id,
            "model": "qwen2.5:14b",
            "prompt_version": "2026-03-12",
            "evidence_ids": [str(ev1.id), str(ev2.id)],
            "report": {
                "executive_summary": "Performance and platform constraints are limiting growth.",
                "findings": [],
                "confidence": "high",
            },
        }

        response = self.client.post("/api/growth/reports", data=payload, format="json", **self.headers)
        self.assertEqual(response.status_code, 201)

        stored = WebsiteReport.objects.get(id=response.data["id"])
        self.assertEqual(stored.lead_id, lead.id)
        self.assertEqual(stored.prompt_version, "2026-03-12")
        self.assertEqual(stored.evidence_ids, [str(ev1.id), str(ev2.id)])
        self.assertEqual(
            stored.summary,
            "Performance and platform constraints are limiting growth.",
        )

        duplicate_response = self.client.post(
            "/api/growth/reports",
            data=payload,
            format="json",
            **self.headers,
        )
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.data["id"], response.data["id"])
        self.assertEqual(WebsiteReport.objects.filter(lead=lead).count(), 1)

    def test_deterministic_scoring(self):
        lead = Lead.objects.create(
            company_name="Scoring Co",
            website_url="https://score.example",
            industry="Ecommerce",
        )
        lead.contacts.create(email="owner@score.example", name="Owner")

        WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="lighthouse_json",
            url=lead.website_url,
            tool="pagespeed",
            payload={"performance_score": 45, "lcp_ms": 3800},
        )
        WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="tech_fingerprint",
            url=lead.website_url,
            tool="fingerprint",
            payload={"cms": "WordPress"},
        )

        report = WebsiteReport.objects.create(
            lead=lead,
            model="qwen2.5:14b",
            prompt_version="2026-03-12",
            evidence_ids=[],
            report={"cta_clarity": "poor"},
            summary="CTA is weak",
        )

        response = self.client.post(
            "/api/growth/scores",
            data={"lead_id": lead.id, "report_id": report.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 201)

        score = LeadScore.objects.get(id=response.data["id"])
        self.assertEqual(score.bucket, "A")
        self.assertEqual(score.score, 10)
        self.assertEqual(score.recommendation["quality_score"], 10)
        self.assertEqual(score.recommendation["opportunity_score"], 90)
        self.assertIn("LOW_MOBILE_PERFORMANCE", score.reason_codes)
        self.assertIn("HIGH_LCP", score.reason_codes)
        self.assertIn("CTA_CLARITY_POOR", score.reason_codes)
        self.assertIn("SITEMAP_MISSING", score.reason_codes)
        self.assertIn("TEMPLATE_CMS_LIMITATION_SIGNAL", score.reason_codes)

        duplicate_response = self.client.post(
            "/api/growth/scores",
            data={"lead_id": lead.id, "report_id": report.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.data["id"], response.data["id"])
        self.assertEqual(LeadScore.objects.filter(lead=lead).count(), 1)

    def test_v3_outreach_draft_create_and_reuse(self):
        lead = Lead.objects.create(
            company_name="Opportunity Co",
            website_url="https://opportunity.example",
            industry="Ecommerce",
        )
        report = WebsiteReport.objects.create(
            lead=lead,
            model="rules_v1",
            prompt_version="growth_report_v2_rules_1",
            evidence_ids=[],
            report={
                "cta_clarity": "weak",
                "performance": {"score": 72, "lcp_ms": 2200, "rating": "needs_improvement"},
                "trust": {"score": 3, "max_score": 5, "rating": "moderate"},
                "seo": {"issues": ["Meta description missing"]},
                "findings": [
                    {
                        "title": "Homepage call-to-action is weak",
                        "diagnosis": "CTA message is not specific.",
                        "business_impact": "Users may not know the next step.",
                        "severity": "medium",
                    }
                ],
            },
            summary="CTA needs improvement",
        )
        score = LeadScore.objects.create(
            lead=lead,
            score=68,
            bucket="A",
            reason_codes=["CTA_CLARITY_POOR"],
            recommendation={"offer_type": "aggressive_outreach"},
        )

        result_1 = run_outreach_for_lead(lead, report_obj=report, score_obj=score, force=False)
        self.assertTrue(result_1["should_contact"])
        self.assertEqual(result_1["priority"], "high")
        self.assertTrue(result_1["draft_created"])
        self.assertFalse(result_1["draft_reused"])
        created_draft = OutboundDraft.objects.get(id=result_1["draft_id"])
        self.assertEqual(created_draft.model, "deterministic_rules_v3")
        self.assertEqual(created_draft.evidence_check["v3_decision"]["offer_type"], "conversion_fix")

        result_2 = run_outreach_for_lead(lead, report_obj=report, score_obj=score, force=False)
        self.assertTrue(result_2["should_contact"])
        self.assertFalse(result_2["draft_created"])
        self.assertTrue(result_2["draft_reused"])
        self.assertEqual(OutboundDraft.objects.filter(lead=lead).count(), 1)

    def test_v3_outreach_skips_low_score(self):
        lead = Lead.objects.create(
            company_name="Low Priority Co",
            website_url="https://low-priority.example",
            industry="Ecommerce",
        )
        report = WebsiteReport.objects.create(
            lead=lead,
            model="rules_v1",
            prompt_version="growth_report_v2_rules_1",
            evidence_ids=[],
            report={
                "cta_clarity": "weak",
                "performance": {"score": 48, "lcp_ms": 4200, "rating": "poor"},
                "trust": {"score": 1, "max_score": 5, "rating": "weak"},
                "seo": {"issues": ["robots.txt missing", "sitemap missing"]},
                "findings": [],
            },
            summary="Low quality site",
        )
        score = LeadScore.objects.create(
            lead=lead,
            score=30,
            bucket="C",
            reason_codes=["LOW_MOBILE_PERFORMANCE"],
            recommendation={"offer_type": "low_priority"},
        )

        result = run_outreach_for_lead(lead, report_obj=report, score_obj=score, force=False)
        self.assertFalse(result["should_contact"])
        self.assertTrue(result["draft_skipped"])
        self.assertIsNone(result["draft_id"])
        self.assertEqual(OutboundDraft.objects.filter(lead=lead).count(), 0)

    def test_contact_finder_extracts_emails_phones_links_and_social(self):
        html = """
        <html>
          <body>
            <a href="mailto:info@example.com">Email us</a>
            <a href="tel:+353871234567">Call</a>
            <a href="/join">Join now</a>
            <a href="/free-trial">Book free trial</a>
            <a href="/contact">Contact</a>
            <a href="https://www.linkedin.com/company/example">LinkedIn</a>
            <p>Backup email: hello@example.com</p>
          </body>
        </html>
        """
        result = extract_contact_candidates(
            homepage_html=html,
            website_url="https://example.com",
        )
        self.assertEqual(result["best_email"], "info@example.com")
        self.assertIn("info@example.com", result["emails"])
        self.assertIn("hello@example.com", result["emails"])
        self.assertEqual(result["best_phone"], "+353871234567")
        self.assertEqual(result["selected_contact_link"], "https://example.com/contact")
        self.assertIn("https://example.com/contact", result["contact_links"])
        self.assertIn("https://example.com/join", result["contact_links"])
        self.assertIn("https://example.com/free-trial", result["contact_links"])
        self.assertIn("linkedin", result["social_links"])

    @patch("growth_ops.services.contact_finder.fetch_url")
    def test_contact_finder_contact_page_fallback_extracts_email_from_multiple_candidates(self, mock_fetch_url):
        from growth_ops.services.contact_finder import enrich_with_contact_page

        homepage_html = '<a href="/join">Join</a><a href="/free-trial">Trial</a><a href="/locations">Locations</a>'
        base = extract_contact_candidates(homepage_html=homepage_html, website_url="https://fallback.example")
        self.assertEqual(base["emails"], [])

        mock_fetch_url.side_effect = [
            {
                "exists": True,
                "status_code": 200,
                "requested_url": "https://fallback.example/join",
                "body": '<div><a href="/locations">Locations</a></div>',
            },
            {
                "exists": True,
                "status_code": 200,
                "requested_url": "https://fallback.example/free-trial",
                "body": '<a href="mailto:hello@fallback.example">Email</a>',
            },
        ]
        enriched = enrich_with_contact_page(
            candidates=base,
            website_url="https://fallback.example",
        )
        self.assertIn("hello@fallback.example", enriched["emails"])
        self.assertEqual(enriched["best_email"], "hello@fallback.example")
        self.assertEqual(mock_fetch_url.call_count, 2)

    def test_contact_enrichment_upserts_without_duplicates(self):
        lead = Lead.objects.create(company_name="Contacts Co", website_url="https://contacts.example")
        extracted = {
            "emails": ["info@contacts.example", "hello@contacts.example"],
            "phones": ["+353861234567"],
            "social_links": {"linkedin": "https://www.linkedin.com/company/contacts"},
            "best_email": "info@contacts.example",
            "best_phone": "+353861234567",
        }

        first = upsert_contacts_for_lead(lead=lead, extracted_contacts=extracted)
        self.assertEqual(first["contacts_created"], 2)
        self.assertEqual(first["contacts_reused"], 0)
        self.assertIsNotNone(first["primary_contact"])
        self.assertEqual(first["primary_contact"].email, "info@contacts.example")

        second = upsert_contacts_for_lead(lead=lead, extracted_contacts=extracted)
        self.assertEqual(second["contacts_created"], 0)
        self.assertGreaterEqual(second["contacts_reused"], 1)
        self.assertEqual(lead.contacts.count(), 2)

    def test_outreach_readiness_ready_when_contact_email_exists(self):
        lead = Lead.objects.create(company_name="Ready Co", website_url="https://ready.example")
        contact = lead.contacts.create(email="info@ready.example", role="website-derived")
        draft = OutboundDraft.objects.create(
            lead=lead,
            contact=contact,
            channel="email",
            subject="Test",
            body="Test body",
        )
        readiness = classify_draft_readiness(
            draft=draft,
            primary_contact=contact,
            extracted_contacts={"best_email": "info@ready.example"},
        )
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["contactability_type"], "email")

    def test_outreach_readiness_pending_without_email(self):
        lead = Lead.objects.create(company_name="Pending Co", website_url="https://pending.example")
        draft = OutboundDraft.objects.create(
            lead=lead,
            channel="email",
            subject="Test",
            body="Test body",
        )
        readiness = classify_draft_readiness(
            draft=draft,
            primary_contact=None,
            extracted_contacts={"best_email": ""},
        )
        self.assertEqual(readiness["status"], "pending")
        self.assertEqual(readiness["contactability_type"], "none")

    def test_outreach_readiness_ready_with_selected_email_metadata(self):
        lead = Lead.objects.create(company_name="Meta Ready Co", website_url="https://metaready.example")
        draft = OutboundDraft.objects.create(
            lead=lead,
            channel="email",
            subject="Test",
            body="Test body",
        )
        readiness = classify_draft_readiness(
            draft=draft,
            primary_contact=None,
            extracted_contacts={"best_email": "info@metaready.example"},
        )
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["contactability_type"], "email")

    def test_outreach_readiness_ready_with_phone(self):
        lead = Lead.objects.create(company_name="Phone Ready Co", website_url="https://phoneready.example")
        draft = OutboundDraft.objects.create(
            lead=lead,
            channel="email",
            subject="Test",
            body="Test body",
        )
        readiness = classify_draft_readiness(
            draft=draft,
            primary_contact=None,
            extracted_contacts={"best_phone": "+353861234567", "contact_links": []},
        )
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["contactability_type"], "phone")

    def test_outreach_readiness_ready_with_contact_link(self):
        lead = Lead.objects.create(company_name="Link Ready Co", website_url="https://linkready.example")
        draft = OutboundDraft.objects.create(
            lead=lead,
            channel="email",
            subject="Test",
            body="Test body",
        )
        readiness = classify_draft_readiness(
            draft=draft,
            primary_contact=None,
            extracted_contacts={
                "best_email": "",
                "best_phone": "",
                "selected_contact_link": "https://linkready.example/join",
                "contact_links": ["https://linkready.example/join"],
            },
        )
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["contactability_type"], "contact_link")

    def test_v35_outreach_rerun_is_idempotent_for_draft_and_contact(self):
        lead = Lead.objects.create(
            company_name="Idempotent Co",
            website_url="https://idempotent.example",
            industry="Ecommerce",
        )
        WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="homepage_html_snippet",
            url=lead.website_url,
            tool="python_requests",
            payload={
                "exists": True,
                "status_code": 200,
                "requested_url": lead.website_url,
                "body": '<a href="mailto:info@idempotent.example">Contact</a>',
            },
        )
        report = WebsiteReport.objects.create(
            lead=lead,
            model="rules_v1",
            prompt_version="growth_report_v2_rules_1",
            evidence_ids=[],
            report={
                "cta_clarity": "weak",
                "performance": {"score": 72, "lcp_ms": 2300, "rating": "needs_improvement"},
                "trust": {"score": 3, "max_score": 5, "rating": "moderate"},
                "seo": {"issues": []},
                "findings": [
                    {
                        "title": "Homepage call-to-action is weak",
                        "diagnosis": "CTA is not explicit.",
                        "business_impact": "Users may drop before enquiring.",
                        "severity": "medium",
                    }
                ],
            },
            summary="CTA needs improvement",
        )
        score = LeadScore.objects.create(
            lead=lead,
            score=70,
            bucket="A",
            reason_codes=["CTA_CLARITY_POOR"],
            recommendation={"offer_type": "aggressive_outreach"},
        )

        first = run_outreach_for_lead(lead, report_obj=report, score_obj=score, force=False)
        second = run_outreach_for_lead(lead, report_obj=report, score_obj=score, force=False)

        self.assertTrue(first["draft_created"])
        self.assertTrue(second["draft_reused"])
        self.assertEqual(OutboundDraft.objects.filter(lead=lead).count(), 1)
        self.assertEqual(lead.contacts.filter(email="info@idempotent.example").count(), 1)
        draft = OutboundDraft.objects.get(lead=lead)
        self.assertEqual(draft.evidence_check["v35_readiness"]["status"], "ready")
        self.assertEqual(draft.contact.email, "info@idempotent.example")

    def test_outreach_queue_includes_ready_drafts(self):
        lead = Lead.objects.create(company_name="Queue Ready Co", website_url="https://readyq.example")
        draft = OutboundDraft.objects.create(
            lead=lead,
            channel="email",
            subject="Ready draft",
            body="Body",
            evidence_check={
                "v3_decision": {"priority": "high"},
                "v35_readiness": {"status": "ready", "reason": "linked_contact_email_available"},
                "selected_email": "info@readyq.example",
            },
        )

        out = StringIO()
        call_command("run_outreach_queue", limit=10, stdout=out)
        output = out.getvalue()
        self.assertIn(f"draft_id={draft.id}", output)
        self.assertIn("drafts_considered: 1", output)
        self.assertIn("drafts_ready: 1", output)

    def test_outreach_queue_excludes_pending_when_ready_only(self):
        lead_pending = Lead.objects.create(company_name="Queue Pending Co", website_url="https://pendingq.example")
        pending_draft = OutboundDraft.objects.create(
            lead=lead_pending,
            channel="email",
            subject="Pending draft",
            body="Body",
            evidence_check={
                "v3_decision": {"priority": "high"},
                "v35_readiness": {"status": "pending", "reason": "no_usable_email_found"},
            },
        )
        lead_ready = Lead.objects.create(company_name="Queue Ready 2 Co", website_url="https://ready2.example")
        ready_draft = OutboundDraft.objects.create(
            lead=lead_ready,
            channel="email",
            subject="Ready draft 2",
            body="Body",
            evidence_check={
                "v3_decision": {"priority": "medium"},
                "v35_readiness": {"status": "ready", "reason": "extracted_email_available"},
                "selected_email": "hello@ready2.example",
            },
        )

        out = StringIO()
        call_command("run_outreach_queue", limit=10, stdout=out)
        output = out.getvalue()
        self.assertIn(f"draft_id={ready_draft.id}", output)
        self.assertNotIn(f"draft_id={pending_draft.id}", output)
        self.assertIn("drafts_ready: 1", output)
        self.assertIn("drafts_pending: 1", output)

    def test_outreach_queue_includes_ready_via_contact_link(self):
        lead_pending = Lead.objects.create(company_name="Queue Pending Link Co", website_url="https://pending-link.example")
        pending_draft = OutboundDraft.objects.create(
            lead=lead_pending,
            channel="email",
            subject="Pending link draft",
            body="Body",
            evidence_check={
                "v3_decision": {"priority": "high"},
                "v35_readiness": {"status": "pending", "reason": "no_usable_contact_route_found"},
            },
        )
        lead_ready = Lead.objects.create(company_name="Queue Ready Link Co", website_url="https://ready-link.example")
        ready_draft = OutboundDraft.objects.create(
            lead=lead_ready,
            channel="email",
            subject="Ready link draft",
            body="Body",
            evidence_check={
                "v3_decision": {"priority": "medium"},
                "v35_readiness": {
                    "status": "ready",
                    "reason": "contact_link_route_available",
                    "contactability_type": "contact_link",
                },
                "selected_contact_link": "https://ready-link.example/free-trial",
            },
        )

        out = StringIO()
        call_command("run_outreach_queue", limit=10, stdout=out)
        output = out.getvalue()
        self.assertIn(f"draft_id={ready_draft.id}", output)
        self.assertNotIn(f"draft_id={pending_draft.id}", output)
        self.assertIn("contact=https://ready-link.example/free-trial", output)

    def test_queue_filtering(self):
        lead = Lead.objects.create(company_name="Queue Co", website_url="https://queue.example")

        draft_pending = OutboundDraft.objects.create(lead=lead, approval_status="pending")
        draft_approved = OutboundDraft.objects.create(lead=lead, approval_status="approved")

        msg_pending = InboxMessage.objects.create(lead=lead, approval_status="pending", from_email="a@queue.example")
        msg_rejected = InboxMessage.objects.create(lead=lead, approval_status="rejected", from_email="b@queue.example")

        content_pending = ContentItem.objects.create(
            channel="linkedin",
            title="Pending Post",
            body="Body",
            status="pending_approval",
        )
        content_draft = ContentItem.objects.create(
            channel="blog",
            title="Draft Post",
            body="Body",
            status="draft",
        )

        outbound_response = self.client.get(
            "/api/growth/queue/outbound?status=approved",
            **self.headers,
        )
        self.assertEqual(outbound_response.status_code, 200)
        outbound_ids = [item["id"] for item in outbound_response.data["results"]]
        self.assertIn(draft_approved.id, outbound_ids)
        self.assertNotIn(draft_pending.id, outbound_ids)

        replies_response = self.client.get(
            "/api/growth/queue/replies?status=rejected",
            **self.headers,
        )
        self.assertEqual(replies_response.status_code, 200)
        reply_ids = [item["id"] for item in replies_response.data["results"]]
        self.assertIn(msg_rejected.id, reply_ids)
        self.assertNotIn(msg_pending.id, reply_ids)

        content_response = self.client.get(
            "/api/growth/queue/content?status=draft",
            **self.headers,
        )
        self.assertEqual(content_response.status_code, 200)
        content_ids = [item["id"] for item in content_response.data["results"]]
        self.assertIn(content_draft.id, content_ids)
        self.assertNotIn(content_pending.id, content_ids)

    def _create_draftable_lead(self, *, bucket: str) -> tuple[Lead, WebsiteEvidence]:
        lead = Lead.objects.create(
            company_name=f"Draft {bucket} Co",
            website_url=f"https://draft-{bucket.lower()}.example",
            industry="Ecommerce",
        )
        evidence = WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="lighthouse_json",
            url=lead.website_url,
            tool="pagespeed",
            payload={"performance_score": 45, "lcp_ms": 3800},
        )
        WebsiteReport.objects.create(
            lead=lead,
            model="qwen2.5:14b",
            prompt_version="2026-03-12",
            evidence_ids=[str(evidence.id)],
            report={"executive_summary": "Performance is weak", "findings": []},
            summary="Performance is weak",
        )
        LeadScore.objects.create(
            lead=lead,
            score=80 if bucket == "A" else 55 if bucket == "B" else 25,
            bucket=bucket,
            reason_codes=["LOW_MOBILE_PERFORMANCE"],
            recommendation={"offer_type": "paid_discovery"},
        )
        return lead, evidence

    def _create_sendable_draft(
        self,
        *,
        approval_status: str = "approved",
        approved_at_set: bool = True,
        sequence_step: int = 1,
    ) -> OutboundDraft:
        lead, _evidence = self._create_draftable_lead(bucket="A")
        contact = lead.contacts.create(email=f"owner-{lead.id}@example.com", name="Owner")
        draft = OutboundDraft.objects.create(
            lead=lead,
            contact=contact,
            channel="email",
            sequence_step=sequence_step,
            subject="Quick note",
            body="A short review of your site.",
            model="qwen2.5:14b",
            prompt_version="2026-03-12",
            approval_status=approval_status,
            approved_at=timezone.now() if approved_at_set and approval_status == "approved" else None,
        )
        return draft

    @patch("growth_ops.services.outreach.LLMGatewayClient.draft_email")
    def test_drafting_only_for_a_or_b_leads(self, mock_draft_email):
        lead_c, evidence_c = self._create_draftable_lead(bucket="C")
        response_c = self.client.post(
            "/api/growth/drafts",
            data={"lead_id": lead_c.id, "sequence_step": 1, "channel": "email"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response_c.status_code, 400)
        self.assertEqual(OutboundDraft.objects.filter(lead=lead_c).count(), 0)
        mock_draft_email.assert_not_called()

        lead_a, evidence_a = self._create_draftable_lead(bucket="A")
        mock_draft_email.return_value = {
            "subject": "Quick note on your mobile performance",
            "body": "Your mobile performance score is 45 and this can hurt conversion.",
            "proof_points": [
                {
                    "claim": "Your mobile performance score is 45.",
                    "evidence_id": str(evidence_a.id),
                    "evidence_path": "performance_score",
                    "quoted_value": "45",
                }
            ],
            "risk_flags": [],
            "model": "qwen2.5:14b",
            "prompt_version": "2026-03-12",
        }
        response_a = self.client.post(
            "/api/growth/drafts",
            data={"lead_id": lead_a.id, "sequence_step": 1, "channel": "email"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response_a.status_code, 201)
        self.assertEqual(OutboundDraft.objects.filter(lead=lead_a).count(), 1)

    def test_evidence_check_failure_on_unsupported_claim(self):
        lead = Lead.objects.create(company_name="Check Co", website_url="https://check.example")
        evidence = WebsiteEvidence.objects.create(
            lead=lead,
            evidence_type="lighthouse_json",
            url=lead.website_url,
            tool="pagespeed",
            payload={"performance_score": 45},
        )

        result = check_proof_points(
            proof_points=[
                {
                    "claim": "Your mobile performance score is 90.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "performance_score",
                    "quoted_value": "90",
                }
            ],
            evidence_records=[evidence],
        )
        self.assertEqual(result.status, "needs_rewrite")
        self.assertEqual(len(result.unsupported_proof_points), 1)
        self.assertEqual(result.unsupported_proof_points[0]["unsupported_reason"], "quoted_value_not_in_evidence")

    @patch("growth_ops.services.outreach.LLMGatewayClient.check_email")
    @patch("growth_ops.services.outreach.LLMGatewayClient.draft_email")
    def test_safe_rewrite_behaviour(self, mock_draft_email, mock_check_email):
        lead, evidence = self._create_draftable_lead(bucket="A")

        mock_draft_email.return_value = {
            "subject": "Quick note on site speed",
            "body": "Your mobile performance score is 45 and your LCP is 1000ms.",
            "proof_points": [
                {
                    "claim": "Your mobile performance score is 45.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "performance_score",
                    "quoted_value": "45",
                },
                {
                    "claim": "Your LCP is 1000ms.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "lcp_ms",
                    "quoted_value": "1000",
                }
            ],
            "risk_flags": [],
            "model": "qwen2.5:14b",
            "prompt_version": "2026-03-12",
        }
        mock_check_email.return_value = {
            "subject": "Quick note on site speed",
            "body": "Your mobile performance score is 45 and your LCP is 3800ms on mobile, which usually affects conversion and UX.",
            "proof_points": [
                {
                    "claim": "Your mobile performance score is 45.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "performance_score",
                    "quoted_value": "45",
                },
                {
                    "claim": "Your LCP is 3800ms on mobile.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "lcp_ms",
                    "quoted_value": "3800",
                }
            ],
            "model": "qwen2.5:14b",
            "prompt_version": "2026-03-12",
        }

        response = self.client.post(
            "/api/growth/drafts",
            data={"lead_id": lead.id, "sequence_step": 1, "channel": "email"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 201)
        draft = OutboundDraft.objects.get(id=response.data["id"])
        self.assertEqual(draft.evidence_check["status"], "rewritten_safe")
        self.assertIn("UNSUPPORTED_CLAIMS_REWRITTEN", draft.risk_flags)
        self.assertIn("3800", draft.body)
        self.assertNotIn("1000", draft.body)

    @patch("growth_ops.services.outreach.LLMGatewayClient.draft_email")
    def test_draft_persistence_pending_approval_status(self, mock_draft_email):
        lead, evidence = self._create_draftable_lead(bucket="B")
        mock_draft_email.return_value = {
            "subject": "Performance signal worth reviewing",
            "body": "Your mobile performance score is 45.",
            "proof_points": [
                {
                    "claim": "Your mobile performance score is 45.",
                    "evidence_id": str(evidence.id),
                    "evidence_path": "performance_score",
                    "quoted_value": "45",
                }
            ],
            "risk_flags": [],
            "model": "qwen2.5:14b",
            "prompt_version": "2026-03-12",
        }

        response = self.client.post(
            "/api/growth/drafts",
            data={"lead_id": lead.id, "sequence_step": 2, "channel": "email"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 201)

        draft = OutboundDraft.objects.get(id=response.data["id"])
        self.assertEqual(draft.approval_status, "pending")
        self.assertIsNone(draft.approved_at)
        self.assertIsNone(draft.approved_by)

    def test_approve_endpoint_sets_approved_at(self):
        draft = self._create_sendable_draft(approval_status="pending", approved_at_set=False)

        response = self.client.post(
            f"/api/growth/drafts/{draft.id}/approve",
            data={},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)

        draft.refresh_from_db()
        self.assertEqual(draft.approval_status, "approved")
        self.assertIsNotNone(draft.approved_at)

    def test_reject_endpoint_changes_approval_status(self):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)

        response = self.client.post(
            f"/api/growth/drafts/{draft.id}/reject",
            data={},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)

        draft.refresh_from_db()
        self.assertEqual(draft.approval_status, "rejected")
        self.assertIsNone(draft.approved_at)
        self.assertIsNone(draft.approved_by)

    @patch("growth_ops.services.sending.EmailMessage.send")
    def test_blocked_send_when_draft_not_approved(self, mock_send):
        draft = self._create_sendable_draft(approval_status="pending", approved_at_set=False)

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error_code"], "draft_not_approved")
        self.assertFalse(mock_send.called)

        send_record = OutboundSend.objects.get(draft=draft)
        self.assertEqual(send_record.status, "failed")
        self.assertIn("draft_not_approved", send_record.error)

    @patch("growth_ops.services.sending.EmailMessage.send")
    def test_blocked_send_for_non_email_channel(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)
        draft.channel = "linkedin"
        draft.save(update_fields=["channel", "updated_at"])

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error_code"], "unsupported_channel")
        self.assertFalse(mock_send.called)

        send_record = OutboundSend.objects.get(draft=draft)
        self.assertEqual(send_record.status, "failed")
        self.assertIn("unsupported_channel", send_record.error)

    @patch("growth_ops.services.sending.EmailMessage.send", return_value=1)
    def test_successful_send_for_approved_draft_creates_send_record(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "sent")
        self.assertTrue(mock_send.called)

        send_record = OutboundSend.objects.get(draft=draft, status="sent")
        self.assertIsNotNone(send_record.sent_at)
        self.assertTrue(send_record.provider_message_id)

    @patch("growth_ops.services.sending.EmailMessage.send", return_value=0)
    def test_zero_send_count_is_treated_as_failure(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["error_code"], "send_not_accepted")
        self.assertTrue(mock_send.called)

        send_record = OutboundSend.objects.get(draft=draft)
        self.assertEqual(send_record.status, "failed")
        self.assertEqual(send_record.error, "Email backend did not accept the message.")

    @patch("growth_ops.services.sending.EmailMessage.send", side_effect=RuntimeError("smtp down"))
    def test_failure_logging_on_send_error(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["error_code"], "send_failed")
        self.assertTrue(mock_send.called)

        send_record = OutboundSend.objects.get(draft=draft)
        self.assertEqual(send_record.status, "failed")
        self.assertEqual(send_record.error, "smtp down")

    @patch("growth_ops.services.sending.EmailMessage.send")
    def test_duplicate_protection_blocks_already_sent_draft(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True)
        OutboundSend.objects.create(
            draft=draft,
            provider="django_smtp",
            provider_message_id="<existing@example.com>",
            status="sent",
            sent_at=timezone.now(),
        )

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["error_code"], "draft_already_sent")
        self.assertFalse(mock_send.called)
        self.assertEqual(OutboundSend.objects.filter(draft=draft, status="sent").count(), 1)

    @patch("growth_ops.services.sending.EmailMessage.send", return_value=1)
    def test_sequence_record_created_updated_on_successful_send(self, mock_send):
        draft = self._create_sendable_draft(approval_status="approved", approved_at_set=True, sequence_step=1)

        response = self.client.post(
            "/api/growth/send-approved",
            data={"draft_id": draft.id},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_send.called)

        sequence = Sequence.objects.get(lead=draft.lead)
        self.assertEqual(sequence.status, "active")
        self.assertEqual(sequence.step, 1)
        self.assertIsNone(sequence.next_send_at)
        self.assertEqual(sequence.meta["last_sent_draft_id"], draft.id)

        draft.lead.refresh_from_db()
        self.assertEqual(draft.lead.status, "in_sequence")


class LLMGatewayClientTests(SimpleTestCase):
    @patch("growth_ops.services.llm_gateway.requests.post")
    def test_client_sends_api_key_header_when_configured(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {"LLM_GATEWAY_API_KEY": "test-gateway-key"}, clear=False):
            client = LLMGatewayClient(base_url="http://gateway.test", timeout_seconds=5)
            response = client.draft_email({"lead_id": 1})

        self.assertEqual(response, {"ok": True})
        mock_post.assert_called_once_with(
            "http://gateway.test/v1/draft-email",
            json={"lead_id": 1},
            headers={"X-LLM-GATEWAY-KEY": "test-gateway-key"},
            timeout=5,
        )
