from __future__ import annotations

from rhinoguard.models import RunResult
from rhinoguard.reports.redaction import redacted_payload


def render_markdown(result: RunResult) -> str:
    payload = redacted_payload(result)
    status = "SUCCEEDED" if payload["attack_succeeded"] else "BLOCKED"
    lines = [
        f"# RhinoGuard Report: {payload['scenario']['name']}",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Provider: `{payload['provider']}`",
        f"- Security score: **{payload['score']}/100**",
        f"- Attack: **{status}**",
        f"- Expected findings met: **{payload['expected_findings_met']}**",
        "",
        "## Findings",
        "",
    ]
    if not payload["findings"]:
        lines.append("No findings.")
    for finding in payload["findings"]:
        lines.extend(
            [
                f"### {finding['title']} ({str(finding['severity']).upper()})",
                "",
                finding["description"],
                "",
                f"Evidence: {finding['evidence']}",
                "",
                f"Remediation: {finding['remediation']}",
                "",
                f"OWASP: {', '.join(finding['owasp']) or '—'}  ",
                f"MITRE ATLAS: {', '.join(finding['mitre_atlas']) or '—'}",
                "",
            ]
        )
    lines.extend(["## Tool Results", ""])
    for tool_result in payload["tool_results"]:
        state = "blocked" if tool_result["blocked"] else "ok" if tool_result["success"] else "error"
        lines.append(f"- `{tool_result['call_id']}` / `{tool_result['tool']}`: **{state}**")
    lines.extend(["", "## Redacted Final Answer", "", str(payload["final_answer"]), ""])
    return "\n".join(lines)
# Clarify implementation notes for markdown report module
