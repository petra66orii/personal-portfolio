from __future__ import annotations

from django.test import override_settings
from rest_framework.test import APITestCase

from growth_ops.models import ContentItem, InboxMessage, Lead, LeadScore, OutboundDraft, WebsiteEvidence, WebsiteReport


@override_settings(N8N_DJANGO_API_KEY="test-n8n-key")
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

    def test_evidence_ingest_append_only(self):
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
        self.assertEqual(response_2.status_code, 201)
        self.assertEqual(response_2.data["created_count"], 2)
        self.assertEqual(WebsiteEvidence.objects.filter(lead=lead).count(), 4)

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
            "model": "qwen2.5:14b-instruct-q4_K_M",
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
        self.assertEqual(score.score, 100)
        self.assertIn("LOW_MOBILE_PERFORMANCE", score.reason_codes)
        self.assertIn("HIGH_LCP", score.reason_codes)
        self.assertIn("CTA_CLARITY_POOR", score.reason_codes)
        self.assertIn("SITEMAP_MISSING", score.reason_codes)
        self.assertIn("TEMPLATE_CMS_LIMITATION_SIGNAL", score.reason_codes)

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
