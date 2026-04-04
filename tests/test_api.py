import unittest

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover - minimal environments can still run core tests
    TestClient = None

from rhinoguard.config import Settings
from tests.helpers import POLICY_FILE, PROJECT_ROOT, SCENARIO_DIR


@unittest.skipIf(TestClient is None, "FastAPI development dependencies are not installed")
class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from rhinoguard.api.app import create_app

        settings = Settings(
            policy_file=POLICY_FILE,
            scenario_dir=SCENARIO_DIR,
            report_dir=PROJECT_ROOT / "reports",
        )
        cls.client = TestClient(create_app(settings))

    def test_health(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_run_response_is_redacted(self) -> None:
        response = self.client.post(
            "/v1/runs",
            json={"scenario_id": "RG-PI-002", "mode": "vulnerable", "provider": "scripted"},
        )
        self.assertEqual(response.status_code, 200)
        serialized = response.text
        self.assertNotIn("RG_SYNTH_TOKEN_7B4C9A", serialized)
        self.assertIn("[REDACTED]", serialized)

    def test_unknown_scenario_is_not_found(self) -> None:
        response = self.client.post(
            "/v1/runs",
            json={"scenario_id": "missing", "mode": "defended", "provider": "scripted"},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
