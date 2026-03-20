from __future__ import annotations

from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from growth_ops.models import ContentItem, InboxMessage, Lead, LeadScore, OutboundDraft, WebsiteEvidence, WebsiteReport
from growth_ops.services.evidence_checker import check_proof_points


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
