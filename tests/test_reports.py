import json
import tempfile
import unittest

from rhinoguard.models import PolicyMode
from rhinoguard.reports.writer import write_reports
from rhinoguard.runner.loader import load_scenario
from tests.helpers import SCENARIO_DIR, scripted_runner


class ReportTests(unittest.TestCase):
    def test_all_formats_redact_synthetic_secrets(self) -> None:
        scenario = load_scenario(SCENARIO_DIR / "prompt-injection" / "indirect-file.yaml")
        result = scripted_runner().run(scenario, PolicyMode.MONITOR)
        secret = scenario.sandbox["secrets"]["service_token"]
        with tempfile.TemporaryDirectory() as directory:
            paths = write_reports(result, directory)
            for path in paths.values():
                with self.subTest(format=path.suffix):
                    content = path.read_text(encoding="utf-8")
                    self.assertNotIn(secret, content)
                    self.assertIn("REDACTED", content)

    def test_json_report_is_machine_readable(self) -> None:
        scenario = load_scenario(SCENARIO_DIR / "prompt-injection" / "instruction-detection.yaml")
        result = scripted_runner().run(scenario, PolicyMode.MONITOR)
        with tempfile.TemporaryDirectory() as directory:
            path = write_reports(result, directory)["json"]
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["scenario"]["id"], "RG-PI-003")


if __name__ == "__main__":
    unittest.main()
