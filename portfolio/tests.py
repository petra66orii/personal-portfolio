import os
from unittest.mock import patch

import requests
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from backend.urls import _should_serve_media_publicly
from portfolio.models import BlogPost


class MediaServingTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_local_non_debug_run_still_serves_media_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(_should_serve_media_publicly())

    @override_settings(DEBUG=False)
    def test_render_defaults_to_private_media_without_override(self):
        with patch.dict(os.environ, {"RENDER": "true"}, clear=True):
            self.assertFalse(_should_serve_media_publicly())

    @override_settings(DEBUG=False)
    def test_explicit_override_can_enable_media(self):
        with patch.dict(
            os.environ,
            {"RENDER": "true", "SERVE_MEDIA_PUBLICLY": "true"},
            clear=True,
        ):
            self.assertTrue(_should_serve_media_publicly())


class PortfolioSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_blog_detail_sanitizes_dangerous_html(self):
        post = BlogPost.objects.create(
            title="Safe Output",
            excerpt="Excerpt",
            content=(
                '<p>Hello</p><script>alert("xss")</script>'
                '<a href="https://example.com" onclick="evil()">link</a>'
            ),
            tags="security",
            published=True,
            published_date=timezone.now(),
        )

        response = self.client.get(f"/api/blog/{post.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("<p>Hello</p>", response.json()["content"])
        self.assertNotIn("<script>", response.json()["content"])
        self.assertNotIn("onclick", response.json()["content"])

    @override_settings(
        MAILCHIMP_API_KEY="test-key",
        MAILCHIMP_DATA_CENTER="us1",
        MAILCHIMP_AUDIENCE_ID="aud-1",
    )
    @patch("portfolio.views.requests.post")
    def test_newsletter_signup_redacts_provider_error_details(self, mock_post):
        mock_response = requests.Response()
        mock_response.status_code = 400
        mock_response._content = b'{"detail":"user@example.com is already a list member"}'
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_post.side_effect = http_error

        response = self.client.post(
            "/api/newsletter-signup/",
            data={"email": "user@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Unable to process this signup request.")

    @override_settings(
        MAILCHIMP_API_KEY=None,
        MAILCHIMP_DATA_CENTER=None,
        MAILCHIMP_AUDIENCE_ID=None,
    )
    def test_newsletter_signup_hides_configuration_details(self):
        response = self.client.post(
            "/api/newsletter-signup/",
            data={"email": "user@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "Newsletter signup is temporarily unavailable.")
