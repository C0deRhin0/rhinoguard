from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from rhinoguard.models import PolicyMode, ToolCall


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    rule_id: str | None = None
    reason: str = "allowed by default"
    would_block: bool = False


class PolicyEngine:
    def __init__(self, document: dict[str, Any], mode: PolicyMode) -> None:
        self.document = document
        self.mode = mode
        self.rules = list(document.get("rules", []))
        defaults = dict(document.get("defaults", {}))
        self.max_tool_calls = int(defaults.get("max_tool_calls", 20))

    @classmethod
    def from_file(cls, path: str | Path, mode: PolicyMode) -> PolicyEngine:
        with Path(path).open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
        if not isinstance(document, dict):
            raise ValueError("Policy document must be a mapping")
        return cls(document, mode)

    def evaluate(
        self,
        call: ToolCall,
        *,
        call_index: int,
        secret_values: list[str],
    ) -> PolicyDecision:
        if self.mode is PolicyMode.OFF:
            return PolicyDecision(allowed=True, reason="policy engine disabled")
        if call_index >= self.max_tool_calls:
            return self._decision("RG-LIMIT-TOOL-CALLS", "tool-call budget exceeded")
        for rule in self.rules:
            if self._matches(rule, call, secret_values):
                return self._decision(
                    str(rule["id"]), str(rule.get("reason", "policy denied call"))
                )
        return PolicyDecision(allowed=True)

    def _decision(self, rule_id: str, reason: str) -> PolicyDecision:
        if self.mode is PolicyMode.MONITOR:
            return PolicyDecision(allowed=True, rule_id=rule_id, reason=reason, would_block=True)
        return PolicyDecision(allowed=False, rule_id=rule_id, reason=reason, would_block=True)

    @staticmethod
    def _matches(rule: dict[str, Any], call: ToolCall, secret_values: list[str]) -> bool:
        tools = [str(value) for value in rule.get("tools", [])]
        if tools and call.tool not in tools:
            return False
        conditions = dict(rule.get("when", {}))
        if not conditions:
            return True

        path_patterns = conditions.get("path_matches")
        if path_patterns is not None:
            path = str(call.arguments.get("path", ""))
            if not any(fnmatch.fnmatch(path, str(pattern)) for pattern in path_patterns):
                return False

        blocked_domains = conditions.get("destination_domains")
        if blocked_domains is not None:
            destination = str(call.arguments.get("to", ""))
            domain = destination.rsplit("@", 1)[-1].lower() if "@" in destination else ""
            if domain not in {str(item).lower() for item in blocked_domains}:
                return False

        allowed_hosts = conditions.get("url_host_not_in")
        if allowed_hosts is not None:
            host = (urlparse(str(call.arguments.get("url", ""))).hostname or "").lower()
            if host in {str(item).lower() for item in allowed_hosts}:
                return False

        if conditions.get("arguments_contain_secret"):
            flattened = repr(call.arguments)
            if not any(secret and secret in flattened for secret in secret_values):
                return False

        if conditions.get("untrusted_memory_write") and str(
            call.arguments.get("source", "")
        ).lower() not in {"untrusted", "external"}:
            return False

        command_not_in = conditions.get("command_not_in")
        if command_not_in is not None:
            operation = str(call.arguments.get("command", "")).strip().split(" ", 1)[0]
            if operation in {str(item) for item in command_not_in}:
                return False
        return True
# Capture a cleanup item for engine module
