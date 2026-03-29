from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from rhinoguard.adapters.base import ModelAdapter, ModelRequest
from rhinoguard.models import PolicyMode, Scenario, ToolResult
from rhinoguard.policies.engine import PolicyEngine
from rhinoguard.runner.trace import TraceRecorder
from rhinoguard.sandbox.tools import ToolRegistry

_RESULT_TOKEN = re.compile(r"\{\{result:([^}]+)}}")


class ToolUsingAgent:
    def __init__(self, adapter: ModelAdapter) -> None:
        self.adapter = adapter

    def run(
        self,
        scenario: Scenario,
        mode: PolicyMode,
        tools: ToolRegistry,
        policy: PolicyEngine,
        trace: TraceRecorder,
    ) -> tuple[str, list[ToolResult]]:
        messages = [
            {"role": "system", "content": scenario.system_prompt},
            {
                "role": "user",
                "content": f"{scenario.user_prompt}\n\nUntrusted input:\n{scenario.attack_prompt}",
            },
        ]
        trace.record("model_request", "Requested an agent decision", provider=self.adapter.name)
        decision = self.adapter.decide(
            ModelRequest(
                scenario=scenario,
                mode=mode,
                messages=messages,
                tool_names=[name for name in tools.names if name in scenario.tools],
            )
        )
        results: list[ToolResult] = []
        result_values: dict[str, str] = {}
        for index, original_call in enumerate(decision.tool_calls):
            call = replace(
                original_call,
                arguments=self._resolve_value(original_call.arguments, result_values),
            )
            trace.record(
                "tool_attempt",
                f"Agent attempted {call.tool}",
                call_id=call.id,
                tool=call.tool,
                arguments=call.arguments,
            )
            if call.tool not in scenario.tools:
                result = ToolResult(
                    call_id=call.id,
                    tool=call.tool,
                    success=False,
                    blocked=True,
                    error="Tool is not granted to this scenario",
                    policy_rule="RG-TOOL-NOT-GRANTED",
                )
                trace.record(
                    "policy_block", result.error, call_id=call.id, rule_id=result.policy_rule
                )
            else:
                policy_decision = policy.evaluate(
                    call,
                    call_index=index,
                    secret_values=list(tools.sandbox.secrets.values()),
                )
                if policy_decision.would_block:
                    trace.record(
                        "policy_violation",
                        policy_decision.reason,
                        call_id=call.id,
                        rule_id=policy_decision.rule_id,
                        enforced=not policy_decision.allowed,
                    )
                if not policy_decision.allowed:
                    result = ToolResult(
                        call_id=call.id,
                        tool=call.tool,
                        success=False,
                        blocked=True,
                        error=policy_decision.reason,
                        policy_rule=policy_decision.rule_id,
                    )
                    trace.record(
                        "policy_block",
                        policy_decision.reason,
                        call_id=call.id,
                        rule_id=policy_decision.rule_id,
                    )
                else:
                    result = tools.execute(call)
                    trace.record(
                        "tool_result",
                        f"Synthetic tool {call.tool} completed",
                        call_id=call.id,
                        success=result.success,
                        output=result.output,
                        error=result.error,
                    )
            results.append(result)
            result_values[call.id] = self._result_text(result)
        final_answer = str(self._resolve_value(decision.final_template, result_values))
        trace.record("agent_final", "Agent produced its final answer", answer=final_answer)
        return final_answer, results

    @classmethod
    def _resolve_value(cls, value: Any, results: dict[str, str]) -> Any:
        if isinstance(value, str):
            return _RESULT_TOKEN.sub(
                lambda match: results.get(match.group(1), "[unavailable]"), value
            )
        if isinstance(value, list):
            return [cls._resolve_value(item, results) for item in value]
        if isinstance(value, dict):
            return {key: cls._resolve_value(item, results) for key, item in value.items()}
        return value

    @staticmethod
    def _result_text(result: ToolResult) -> str:
        if result.blocked:
            return f"[blocked by {result.policy_rule}]"
        if not result.success:
            return f"[tool error: {result.error}]"
        return str(result.output)
# Review follow-up details for tool agent module
