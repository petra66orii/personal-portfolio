from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))


def _draft_payload() -> dict:
    return {
        "lead_id": 1,
        "company_name": "Example Co",
        "website_url": "https://example.com",
        "bucket": "A",
        "score": 82,
        "offer_type": "paid_discovery",
        "report_summary": "Example summary",
        "evidence": [
            {
                "evidence_id": "1",
                "evidence_type": "lighthouse_json",
                "evidence_path": "performance_score",
            }
        ],
    }


class LLMGatewaySettingsTests(unittest.TestCase):
    def test_settings_require_api_key_when_auth_enabled(self):
        with patch.dict(
            os.environ,
            {"LLM_GATEWAY_REQUIRE_API_KEY": "true"},
            clear=True,
        ):
            config_module = importlib.import_module("app.config")
            config_module = importlib.reload(config_module)
            with self.assertRaisesRegex(
                ValueError,
                "LLM_GATEWAY_API_KEY is required when gateway auth is enabled",
            ):
                config_module.Settings.from_env()


class LLMGatewayAuthRouteTests(unittest.TestCase):
    def _load_main_module(self):
        with patch.dict(
            os.environ,
            {
                "LLM_GATEWAY_API_KEY": "local-test-key",
                "LLM_GATEWAY_REQUIRE_API_KEY": "true",
            },
            clear=True,
        ):
            main_module = importlib.import_module("app.main")
            return importlib.reload(main_module)

    def test_health_route_remains_public(self):
        main_module = self._load_main_module()
        client = TestClient(main_module.app)

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_protected_route_rejects_missing_api_key(self):
        main_module = self._load_main_module()
        client = TestClient(main_module.app)

        with patch.object(main_module, "_generate_structured_output") as mock_generate:
            response = client.post("/v1/draft-email", json=_draft_payload())

        self.assertEqual(response.status_code, 401)
        mock_generate.assert_not_called()

    def test_protected_route_accepts_valid_api_key(self):
        main_module = self._load_main_module()
        client = TestClient(main_module.app)
        expected_result = main_module.DraftEmailResult(
            channel="email",
            sequence_step=1,
            subject="Example subject",
            body="Example body",
            proof_points=[
                {
                    "claim": "Performance score is 45.",
                    "evidence_id": "1",
                    "evidence_path": "performance_score",
                    "quoted_value": "45",
                }
            ],
            risk_flags=[],
        )

        with patch.object(
            main_module,
            "_generate_structured_output",
            return_value=("req-1", "outreach_writer", expected_result),
        ) as mock_generate:
            response = client.post(
                "/v1/draft-email",
                json=_draft_payload(),
                headers={"X-LLM-GATEWAY-KEY": "local-test-key"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["request_id"], "req-1")
        mock_generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
