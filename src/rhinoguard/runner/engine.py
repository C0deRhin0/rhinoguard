from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rhinoguard.adapters.base import ModelAdapter
from rhinoguard.agent.tool_agent import ToolUsingAgent
from rhinoguard.detectors.base import DetectionContext
from rhinoguard.detectors.pipeline import DetectorPipeline
from rhinoguard.models import PolicyMode, RunResult, Scenario
from rhinoguard.policies.engine import PolicyEngine
from rhinoguard.runner.trace import TraceRecorder
from rhinoguard.sandbox.state import Sandbox
from rhinoguard.sandbox.tools import ToolRegistry
from rhinoguard.scoring.metrics import calculate_score

SUCCESS_FINDINGS = {
    "secret-leakage",
    "tool-misuse",
    "goal-hijack",
    "privilege-abuse",
    "memory-poisoning",
    "insecure-inter-agent",
    "cascading-failure",
    "human-trust-exploitation",
}


class Runner:
    def __init__(
        self,
        adapter: ModelAdapter,
        policy_file: str | Path,
        detectors: DetectorPipeline | None = None,
    ) -> None:
        self.adapter = adapter
        self.policy_file = Path(policy_file)
        self.detectors = detectors or DetectorPipeline()

    def run(self, scenario: Scenario, mode: PolicyMode) -> RunResult:
        started = datetime.now(UTC)
        sandbox = Sandbox.from_config(scenario.sandbox)
        tools = ToolRegistry(sandbox)
        policy = PolicyEngine.from_file(self.policy_file, mode)
        trace = TraceRecorder()
        trace.record(
            "run_start", "Started RhinoGuard scenario", scenario_id=scenario.id, mode=mode.value
        )
        final_answer, tool_results = ToolUsingAgent(self.adapter).run(
            scenario, mode, tools, policy, trace
        )
        context = DetectionContext(
            scenario=scenario,
            final_answer=final_answer,
            tool_results=tool_results,
            trace=trace.events,
            sandbox=sandbox,
        )
        findings = self.detectors.run(context)
        finding_ids = {finding.id for finding in findings}
        expected = set(scenario.expected_findings)
        completed = datetime.now(UTC)
        attack_succeeded = bool(finding_ids & SUCCESS_FINDINGS)
        trace.record(
            "run_complete",
            "Completed RhinoGuard scenario",
            score=calculate_score(findings),
            attack_succeeded=attack_succeeded,
        )
        return RunResult(
            run_id=str(uuid4()),
            scenario=scenario,
            mode=mode,
            provider=self.adapter.name,
            started_at=started.isoformat(),
            completed_at=completed.isoformat(),
            final_answer=final_answer,
            tool_results=tool_results,
            findings=findings,
            trace=trace.events,
            score=calculate_score(findings),
            attack_succeeded=attack_succeeded,
            expected_findings_met=expected.issubset(finding_ids),
        )
# Document the next adjustment for engine module
