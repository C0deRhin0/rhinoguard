from __future__ import annotations

import shlex

from rhinoguard.errors import ToolExecutionError
from rhinoguard.sandbox.filesystem import VirtualFilesystem


class SyntheticShell:
    """A tiny command interpreter; it never creates an OS subprocess."""

    def __init__(self, filesystem: VirtualFilesystem) -> None:
        self.filesystem = filesystem

    def execute(self, command: str) -> str:
        try:
            parts = shlex.split(command)
        except ValueError as exc:
            raise ToolExecutionError(f"Invalid command syntax: {exc}") from exc
        if not parts:
            raise ToolExecutionError("Command cannot be empty")
        operation, *arguments = parts
        if operation == "pwd" and not arguments:
            return "/sandbox"
        if operation == "ls" and len(arguments) <= 1:
            return "\n".join(self.filesystem.list(arguments[0] if arguments else ""))
        if operation == "read" and len(arguments) == 1:
            return self.filesystem.read(arguments[0])
        if operation == "search" and arguments:
            return "\n".join(self.filesystem.search(" ".join(arguments)))
        raise ToolExecutionError(f"Command is not supported by the synthetic shell: {operation}")
