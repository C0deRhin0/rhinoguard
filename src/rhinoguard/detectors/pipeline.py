from __future__ import annotations

from rhinoguard.detectors.base import DetectionContext, Detector
from rhinoguard.detectors.behavior import BehaviorDetector
from rhinoguard.detectors.prompt_injection import PromptInjectionDetector
from rhinoguard.detectors.secret_leakage import SecretLeakageDetector
from rhinoguard.detectors.tool_misuse import ToolMisuseDetector
from rhinoguard.models import Finding


class DetectorPipeline:
    def __init__(self, detectors: list[Detector] | None = None) -> None:
        self.detectors = detectors or [
            PromptInjectionDetector(),
            SecretLeakageDetector(),
            ToolMisuseDetector(),
            BehaviorDetector(),
        ]

    def run(self, context: DetectionContext) -> list[Finding]:
        findings: list[Finding] = []
        seen: set[str] = set()
        for detector in self.detectors:
            for finding in detector.detect(context):
                if finding.id not in seen:
                    findings.append(finding)
                    seen.add(finding.id)
        return sorted(findings, key=lambda item: _severity_rank(item.severity), reverse=True)


def _severity_rank(severity: object) -> int:
    return {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}.get(
        getattr(severity, "value", str(severity)), 0
    )
