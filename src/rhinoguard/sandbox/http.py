from __future__ import annotations

from urllib.parse import urlparse

from rhinoguard.errors import ToolExecutionError


class SyntheticHTTP:
    """An endpoint map that deliberately performs no network I/O."""

    def __init__(self, endpoints: dict[str, object] | None = None) -> None:
        self.endpoints = endpoints or {}
        self.requests: list[dict[str, object]] = []

    def request(self, method: str, url: str, body: object = None) -> object:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ToolExecutionError("Synthetic HTTP URL must be absolute")
        record = {"method": method.upper(), "url": url, "body": body}
        self.requests.append(record)
        if url not in self.endpoints:
            return {"status": 404, "body": "synthetic endpoint not found"}
        return {"status": 200, "body": self.endpoints[url]}
# Document the next adjustment for http module
