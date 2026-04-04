import unittest

from rhinoguard.adapters.json_contract import parse_decision
from rhinoguard.errors import AdapterError


class AdapterContractTests(unittest.TestCase):
    def test_parses_plain_json(self) -> None:
        decision = parse_decision(
            '{"tool_calls":[{"id":"x","tool":"read_file","arguments":{"path":"a"}}],"final":"done"}'
        )
        self.assertEqual(decision.tool_calls[0].tool, "read_file")
        self.assertEqual(decision.final_template, "done")

    def test_parses_fenced_json_defensively(self) -> None:
        decision = parse_decision('```json\n{"tool_calls":[],"final":"safe"}\n```')
        self.assertEqual(decision.final_template, "safe")

    def test_rejects_invalid_contract(self) -> None:
        with self.assertRaises(AdapterError):
            parse_decision("not-json")


if __name__ == "__main__":
    unittest.main()
