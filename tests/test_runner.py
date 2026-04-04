import unittest

from rhinoguard.models import PolicyMode
from rhinoguard.runner.loader import discover_scenarios, load_scenario
from tests.helpers import SCENARIO_DIR, scripted_runner


class RunnerTests(unittest.TestCase):
    def test_indirect_injection_has_before_after_delta(self) -> None:
        scenario = load_scenario(SCENARIO_DIR / "prompt-injection" / "indirect-file.yaml")
        runner = scripted_runner()
        vulnerable = runner.run(scenario, PolicyMode.MONITOR)
        defended = runner.run(scenario, PolicyMode.ENFORCE)
        self.assertTrue(vulnerable.attack_succeeded)
        self.assertFalse(defended.attack_succeeded)
        self.assertGreater(defended.score, vulnerable.score)
        self.assertIn("secret-leakage", {finding.id for finding in vulnerable.findings})
        self.assertNotIn("secret-leakage", {finding.id for finding in defended.findings})

    def test_vulnerable_corpus_meets_expected_findings(self) -> None:
        runner = scripted_runner()
        for path in discover_scenarios(SCENARIO_DIR):
            with self.subTest(path=path.name):
                result = runner.run(load_scenario(path), PolicyMode.MONITOR)
                self.assertTrue(result.expected_findings_met)

    def test_defended_corpus_has_no_successful_attack(self) -> None:
        runner = scripted_runner()
        for path in discover_scenarios(SCENARIO_DIR):
            with self.subTest(path=path.name):
                result = runner.run(load_scenario(path), PolicyMode.ENFORCE)
                self.assertFalse(result.attack_succeeded)


if __name__ == "__main__":
    unittest.main()
