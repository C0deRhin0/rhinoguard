import unittest

from rhinoguard.models import PolicyMode, ToolCall
from rhinoguard.policies.engine import PolicyEngine
from tests.helpers import POLICY_FILE


class PolicyEngineTests(unittest.TestCase):
    def test_monitor_records_without_blocking(self) -> None:
        engine = PolicyEngine.from_file(POLICY_FILE, PolicyMode.MONITOR)
        decision = engine.evaluate(
            ToolCall("one", "read_file", {"path": "secrets/key.txt"}),
            call_index=0,
            secret_values=["secret"],
        )
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.would_block)
        self.assertEqual(decision.rule_id, "RG-DENY-SENSITIVE-READ")

    def test_enforce_blocks_sensitive_read(self) -> None:
        engine = PolicyEngine.from_file(POLICY_FILE, PolicyMode.ENFORCE)
        decision = engine.evaluate(
            ToolCall("one", "read_file", {"path": "credentials/admin.txt"}),
            call_index=0,
            secret_values=[],
        )
        self.assertFalse(decision.allowed)

    def test_internal_http_host_is_allowed(self) -> None:
        engine = PolicyEngine.from_file(POLICY_FILE, PolicyMode.ENFORCE)
        decision = engine.evaluate(
            ToolCall(
                "one",
                "http_request",
                {"method": "GET", "url": "https://api.internal.test/health"},
            ),
            call_index=0,
            secret_values=[],
        )
        self.assertTrue(decision.allowed)

    def test_secret_in_sink_is_blocked(self) -> None:
        engine = PolicyEngine.from_file(POLICY_FILE, PolicyMode.ENFORCE)
        decision = engine.evaluate(
            ToolCall(
                "one",
                "send_email",
                {"to": "analyst@internal.test", "subject": "x", "body": "TOKEN-1"},
            ),
            call_index=0,
            secret_values=["TOKEN-1"],
        )
        self.assertEqual(decision.rule_id, "RG-DENY-SECRET-IN-OUTPUT")
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
