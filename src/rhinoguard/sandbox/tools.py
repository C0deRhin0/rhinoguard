from __future__ import annotations

from collections.abc import Callable
from typing import Any

from rhinoguard.errors import ToolExecutionError
from rhinoguard.models import ToolCall, ToolResult
from rhinoguard.sandbox.state import Sandbox

ToolFunction = Callable[..., Any]


class ToolRegistry:
    def __init__(self, sandbox: Sandbox) -> None:
        self.sandbox = sandbox
        self._tools: dict[str, ToolFunction] = {
            "read_file": sandbox.filesystem.read,
            "write_file": sandbox.filesystem.write,
            "list_files": sandbox.filesystem.list,
            "search_files": sandbox.filesystem.search,
            "send_email": sandbox.mailbox.send,
            "http_request": sandbox.http.request,
            "memory_read": sandbox.memory.read,
            "memory_write": sandbox.memory.write,
            "shell": sandbox.shell.execute,
        }

    @property
    def names(self) -> list[str]:
        return sorted(self._tools)

    def execute(self, call: ToolCall) -> ToolResult:
        function = self._tools.get(call.tool)
        if function is None:
            return ToolResult(
                call_id=call.id,
                tool=call.tool,
                success=False,
                error=f"Unknown synthetic tool: {call.tool}",
            )
        try:
            output = function(**call.arguments)
            return ToolResult(call_id=call.id, tool=call.tool, success=True, output=output)
        except (ToolExecutionError, TypeError, ValueError) as exc:
            return ToolResult(
                call_id=call.id,
                tool=call.tool,
                success=False,
                error=str(exc),
            )
# Capture a cleanup item for tools module
