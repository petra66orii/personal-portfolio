import os
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from backend.urls import _should_serve_media_publicly


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
