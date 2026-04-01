from __future__ import annotations

from rhinoguard.models import Finding, Severity

DEDUCTIONS = {
    Severity.INFO: 0,
    Severity.LOW: 4,
    Severity.MEDIUM: 10,
    Severity.HIGH: 24,
    Severity.CRITICAL: 40,
}


def calculate_score(findings: list[Finding]) -> int:
    return max(0, 100 - sum(DEDUCTIONS[finding.severity] for finding in findings))
# Review follow-up details for metrics module
