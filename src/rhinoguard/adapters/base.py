from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from rhinoguard.models import AgentDecision, PolicyMode, Scenario


@dataclass(slots=True)
class ModelRequest:
    scenario: Scenario
    mode: PolicyMode
    messages: list[dict[str, str]]
    tool_names: list[str]
    context: dict[str, Any] = field(default_factory=dict)


class ModelAdapter(ABC):
    name = "base"

    @abstractmethod
    def decide(self, request: ModelRequest) -> AgentDecision:
        """Return a normalized agent decision."""
