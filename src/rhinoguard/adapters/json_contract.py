from __future__ import annotations

import json
import re
from typing import Any

from rhinoguard.errors import AdapterError
from rhinoguard.models import AgentDecision, ToolCall


def response_contract_prompt(tool_names: list[str]) -> str:
    tools = ", ".join(tool_names) or "none"
    return (
        "Return only JSON with this shape: "
        '{"tool_calls":[{"id":"call-1","tool":"name","arguments":{}}],'
        '"final":"text"}. '
        f"Available synthetic tools: {tools}. Do not use Markdown fences."
    )


def parse_decision(text: str) -> AgentDecision:
    candidate = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", candidate, flags=re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    try:
        payload: dict[str, Any] = json.loads(candidate)
    except (json.JSONDecodeError, TypeError) as exc:
        raise AdapterError(f"Model returned invalid decision JSON: {exc}") from exc
    raw_calls = payload.get("tool_calls", [])
    if not isinstance(raw_calls, list):
        raise AdapterError("tool_calls must be a list")
    calls: list[ToolCall] = []
    for index, item in enumerate(raw_calls):
        if not isinstance(item, dict) or not item.get("tool"):
            raise AdapterError(f"tool_calls[{index}] is invalid")
        arguments = item.get("arguments", {})
        if not isinstance(arguments, dict):
            raise AdapterError(f"tool_calls[{index}].arguments must be an object")
        calls.append(
            ToolCall(
                id=str(item.get("id", f"call-{index + 1}")),
                tool=str(item["tool"]),
                arguments=arguments,
            )
        )
    return AgentDecision(tool_calls=calls, final_template=str(payload.get("final", "")))
# Clarify implementation notes for json contract module
