from __future__ import annotations

import secrets

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class N8NAPIKeyAuthentication(BaseAuthentication):
    """
    Header-based service authentication for n8n/internal automation clients.
    """

    header_name = "X-N8N-API-KEY"

    def authenticate(self, request):
        expected_key = getattr(settings, "N8N_DJANGO_API_KEY", "")
        provided_key = request.headers.get(self.header_name, "")

        if not expected_key:
            raise AuthenticationFailed("n8n_api_key_not_configured")

        if not provided_key:
            raise AuthenticationFailed("missing_api_key")

        if not secrets.compare_digest(provided_key, expected_key):
            raise AuthenticationFailed("invalid_api_key")

        return (AnonymousUser(), "n8n_api_key")

    def authenticate_header(self, request):
        return self.header_name
