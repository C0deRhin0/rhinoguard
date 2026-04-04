FRAMEWORK_LABELS = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse",
    "ASI03": "Identity and Privilege Abuse",
    "ASI06": "Memory and Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "AML.T0051": "LLM Prompt Injection",
    "AML.T0087": "AI Agent Tool Invocation",
    "AML.T0086": "Exfiltration via AI Agent Tool Invocation",
}


def label(identifier: str) -> str:
    return FRAMEWORK_LABELS.get(identifier, identifier)
