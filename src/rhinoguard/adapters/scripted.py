from __future__ import annotations

from rhinoguard.adapters.base import ModelAdapter, ModelRequest
from rhinoguard.models import AgentDecision, PolicyMode, ToolCall


class ScriptedAdapter(ModelAdapter):
    """Deterministic adapter used for repeatable security regression tests."""

    name = "scripted"

    def decide(self, request: ModelRequest) -> AgentDecision:
        script = request.scenario.model_script
        calls = [
            ToolCall(
                id=str(item.get("id", f"call-{index + 1}")),
                tool=str(item["tool"]),
                arguments=dict(item.get("arguments", {})),
            )
            for index, item in enumerate(script.get("actions", []))
        ]
        final = script.get("final", "Scenario completed.")
        if request.mode is PolicyMode.ENFORCE:
            final = script.get("defended_final", final)
        return AgentDecision(
            tool_calls=calls,
            final_template=str(final),
        )
# Refine the surrounding context for scripted module
