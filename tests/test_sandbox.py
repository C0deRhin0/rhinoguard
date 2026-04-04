import unittest

from rhinoguard.errors import ToolExecutionError
from rhinoguard.models import ToolCall
from rhinoguard.sandbox.filesystem import VirtualFilesystem
from rhinoguard.sandbox.state import Sandbox
from rhinoguard.sandbox.tools import ToolRegistry


class SandboxTests(unittest.TestCase):
    def test_filesystem_rejects_traversal(self) -> None:
        filesystem = VirtualFilesystem({"public/a.txt": "safe"})
        with self.assertRaises(ToolExecutionError):
            filesystem.read("../etc/passwd")

    def test_http_tool_never_needs_a_real_endpoint(self) -> None:
        sandbox = Sandbox.from_config({"http_endpoints": {}})
        result = ToolRegistry(sandbox).execute(
            ToolCall(
                "request",
                "http_request",
                {"method": "GET", "url": "https://nonexistent.invalid/test"},
            )
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output["status"], 404)
        self.assertEqual(len(sandbox.http.requests), 1)

    def test_shell_is_an_interpreter_not_an_os_shell(self) -> None:
        sandbox = Sandbox.from_config({"files": {"public/a.txt": "safe"}})
        result = ToolRegistry(sandbox).execute(ToolCall("shell", "shell", {"command": "rm -rf /"}))
        self.assertFalse(result.success)
        self.assertIn("not supported", result.error)


if __name__ == "__main__":
    unittest.main()
