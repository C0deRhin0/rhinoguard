from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from rhinoguard.models import Finding, Scenario, ToolResult, TraceEvent
from rhinoguard.sandbox.state import Sandbox


@dataclass(slots=True)
class DetectionContext:
    scenario: Scenario
    final_answer: str
    tool_results: list[ToolResult]
    trace: list[TraceEvent]
    sandbox: Sandbox


class Detector(ABC):
    @abstractmethod
    def detect(self, context: DetectionContext) -> list[Finding]:
        """Inspect one completed run."""


def framework(context: DetectionContext) -> tuple[list[str], list[str]]:
    return (
        list(context.scenario.framework.get("owasp", [])),
        list(context.scenario.framework.get("mitre_atlas", [])),
    )
