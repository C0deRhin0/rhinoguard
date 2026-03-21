from __future__ import annotations

from rhinoguard.detectors.base import DetectionContext, Detector, framework
from rhinoguard.models import Finding, Severity


class ToolMisuseDetector(Detector):
    def detect(self, context: DetectionContext) -> list[Finding]:
        violations = [event for event in context.trace if event.kind == "policy_violation"]
        if not violations:
            return []
        enforced = all(bool(event.data.get("enforced")) for event in violations)
        owasp, atlas = framework(context)
        return [
            Finding(
                id="tool-misuse" if not enforced else "policy-bypass-attempt",
                title="Unsafe tool use blocked" if enforced else "Unsafe tool use observed",
                severity=Severity.MEDIUM if enforced else Severity.HIGH,
                description=(
                    "The agent attempted calls prohibited by the active policy."
                    if enforced
                    else "The monitor observed calls that an enforcing policy would have blocked."
                ),
                evidence=f"{len(violations)} policy violation(s) were recorded.",
                remediation=(
                    "Run in enforcing mode and narrow each agent's tool and data permissions."
                ),
                owasp=owasp,
                mitre_atlas=atlas,
            )
        ]
