import tempfile
import unittest
from pathlib import Path

from rhinoguard.errors import ScenarioValidationError
from rhinoguard.runner.loader import discover_scenarios, load_scenario
from tests.helpers import SCENARIO_DIR


class ScenarioLoaderTests(unittest.TestCase):
    def test_discovers_complete_corpus(self) -> None:
        paths = discover_scenarios(SCENARIO_DIR)
        self.assertEqual(len(paths), 10)
        self.assertEqual(len({load_scenario(path).id for path in paths}), 10)

    def test_expands_fixture_content(self) -> None:
        scenario = load_scenario(SCENARIO_DIR / "prompt-injection" / "indirect-file.yaml")
        content = scenario.sandbox["files"]["public/quarterly-plan.txt"]
        self.assertIn("UNTRUSTED EMBEDDED NOTE", content)

    def test_missing_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.yaml"
            path.write_text("id: incomplete\n", encoding="utf-8")
            with self.assertRaises(ScenarioValidationError):
                load_scenario(path)


if __name__ == "__main__":
    unittest.main()
# Review follow-up details for test loader module
