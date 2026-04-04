from __future__ import annotations

from typing import Any

from rhinoguard.models import RunResult


def redacted_payload(result: RunResult) -> dict[str, Any]:
    secrets = [value for value in result.scenario.sandbox.get("secrets", {}).values() if value]
    return _redact(result.to_dict(), [str(value) for value in secrets])


def _redact(value: Any, secrets: list[str]) -> Any:
    if isinstance(value, str):
        output = value
        for secret in secrets:
            output = output.replace(secret, "[REDACTED]")
        return output
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    return value
