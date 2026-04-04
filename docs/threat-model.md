# Threat Model

## Assets

- Agent objectives and system instructions
- Synthetic secrets and private documents
- Tool authorization rules
- Human approval integrity
- Execution and evidence integrity

## Adversaries

- A user supplying a direct injection
- A malicious document or support ticket author
- A compromised synthetic connector
- An unauthenticated peer agent
- A party using urgency or false certainty to influence an operator

## Abuse cases

| Abuse case | Control under test |
| --- | --- |
| Read a protected path | Sensitive-path rule and least privilege |
| Send data externally | Domain and secret-aware sink policy |
| Persist an external instruction | Memory provenance rule |
| Chain several unsafe tools | Per-call policy and call budget |
| Claim approval in text | Authenticated approval outside model content |
| Hide a prompt in a document | Input provenance and injection detection |

## Residual risks

String-based detection is intentionally explainable but can miss obfuscated
language. Policy rules depend on accurate data classification. A real provider
may return malformed output or expose prompts to its configured service. HTML
reports are escaped and redacted, but should still be treated as security data.

