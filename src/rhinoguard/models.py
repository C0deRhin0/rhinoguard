from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyMode(StrEnum):
    OFF = "off"
    MONITOR = "monitor"
    ENFORCE = "enforce"


@dataclass(slots=True)
class ToolCall:
    id: str
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentDecision:
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_template: str = ""


@dataclass(slots=True)
class ToolResult:
    call_id: str
    tool: str
    success: bool
    output: Any = None
    error: str | None = None
    blocked: bool = False
    policy_rule: str | None = None


@dataclass(slots=True)
class TraceEvent:
    kind: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(slots=True)
class Finding:
    id: str
    title: str
    severity: Severity
    description: str
    evidence: str
    remediation: str
    owasp: list[str] = field(default_factory=list)
    mitre_atlas: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Scenario:
    id: str
    name: str
    description: str
    category: str
    severity: Severity
    objective: str
    system_prompt: str
    user_prompt: str
    attack_prompt: str
    tools: list[str]
    framework: dict[str, list[str]]
    sandbox: dict[str, Any]
    model_script: dict[str, Any]
    expected_findings: list[str]
    source_path: str = ""


@dataclass(slots=True)
class RunResult:
    run_id: str
    scenario: Scenario
    mode: PolicyMode
    provider: str
    started_at: str
    completed_at: str
    final_answer: str
    tool_results: list[ToolResult]
    findings: list[Finding]
    trace: list[TraceEvent]
    score: int
    attack_succeeded: bool
    expected_findings_met: bool

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        payload["scenario"]["severity"] = self.scenario.severity.value
        for finding in payload["findings"]:
            finding["severity"] = (
                finding["severity"].value
                if isinstance(finding["severity"], Severity)
                else finding["severity"]
            )
        return payload
