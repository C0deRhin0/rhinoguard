from __future__ import annotations

from pathlib import PurePosixPath

from rhinoguard.errors import ToolExecutionError


class VirtualFilesystem:
    def __init__(self, files: dict[str, str] | None = None) -> None:
        self._files = {self._normalize(path): str(value) for path, value in (files or {}).items()}

    @staticmethod
    def _normalize(path: str) -> str:
        cleaned = path.strip().lstrip("/")
        parsed = PurePosixPath(cleaned)
        if not cleaned or ".." in parsed.parts:
            raise ToolExecutionError("Path traversal and empty paths are not allowed")
        return parsed.as_posix()

    def read(self, path: str) -> str:
        normalized = self._normalize(path)
        try:
            return self._files[normalized]
        except KeyError as exc:
            raise ToolExecutionError(f"Synthetic file not found: {normalized}") from exc

    def write(self, path: str, content: str) -> str:
        normalized = self._normalize(path)
        self._files[normalized] = str(content)
        return f"wrote {len(str(content))} characters to {normalized}"

    def list(self, prefix: str = "") -> list[str]:
        normalized = prefix.strip().lstrip("/")
        if ".." in PurePosixPath(normalized or ".").parts:
            raise ToolExecutionError("Path traversal is not allowed")
        return sorted(path for path in self._files if path.startswith(normalized))

    def search(self, query: str) -> list[str]:
        needle = query.casefold()
        return sorted(
            path
            for path, content in self._files.items()
            if needle in path.casefold() or needle in content.casefold()
        )
# Refine the surrounding context for filesystem module
