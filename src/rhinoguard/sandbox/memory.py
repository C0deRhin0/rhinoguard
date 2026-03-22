from __future__ import annotations


class SyntheticMemory:
    def __init__(self, values: dict[str, str] | None = None) -> None:
        self.values = dict(values or {})
        self.writes: list[dict[str, str]] = []

    def read(self, key: str) -> str:
        return self.values.get(key, "")

    def write(self, key: str, value: str, source: str = "agent") -> str:
        self.values[key] = value
        self.writes.append({"key": key, "value": value, "source": source})
        return f"stored synthetic memory key {key}"
