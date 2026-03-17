# Security Model

RhinoGuard assumes scenario input and model output may be hostile. It treats the
policy engine—not a model instruction—as the authorization boundary.

## Included controls

- Explicit per-scenario tool grants
- Pre-execution policy decisions
- Sensitive path patterns
- External email domain blocks
- Synthetic HTTP host allowlisting
- Secret-aware argument checks
- Untrusted memory-write prevention
- Tool-call budgets
- Recursive output redaction

## Synthetic tool guarantees

`SyntheticHTTP` records an endpoint-mapped request and never opens a socket.
`SyntheticMailbox` appends to an in-memory outbox and never sends mail.
`SyntheticShell` parses a tiny command vocabulary and never invokes a subprocess.
`VirtualFilesystem` stores an in-memory mapping and rejects traversal components.

These guarantees are intentionally enforced in code rather than supplied as
prompts to an AI model.

## Real model providers

Ollama and OpenAI-compatible adapters do perform operator-configured HTTP calls
to obtain model decisions. Their endpoints should normally be loopback or an
approved private service. RhinoGuard never sends registered sandbox secrets in
the initial model request; scripted tool results are processed locally.

## Non-goals

- Scanning third-party endpoints
- Executing generated shell commands
- Proving formal model alignment
- Replacing production IAM or DLP systems
- Claiming OWASP or MITRE certification

