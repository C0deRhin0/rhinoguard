# Architecture

RhinoGuard separates decision generation, enforcement, side effects, detection,
and reporting so each can be tested independently.

```text
Scenario loader
  ├─ validates required fields
  └─ expands local fixture references
          │
          ▼
Model adapter ──► normalized AgentDecision
          │
          ▼
ToolUsingAgent
  ├─ resolves prior synthetic tool results
  ├─ checks scenario grants
  └─ asks PolicyEngine for preflight decisions
          │
          ▼
ToolRegistry ──► Sandbox state
          │
          ▼
TraceRecorder ──► DetectorPipeline ──► Score ──► Reports
```

## Trust boundaries

1. Scenario fixtures are untrusted test input.
2. Model responses are untrusted decisions.
3. The policy engine is the authorization boundary.
4. Synthetic tools are the side-effect boundary.
5. Report redaction is the output boundary.

The scripted adapter is not a pretend LLM. It is an explicit deterministic test
double used to prove policy and detector behavior. Real model adapters implement
the same normalized decision interface.

## Modes

- `off`: calls execute without policy evaluation.
- `monitor`: calls execute, but violations are recorded as if a proposed policy
  were shadow deployed.
- `enforce`: violating calls return a blocked result and never reach the tool.

The CLI aliases `vulnerable` to `monitor` and `defended` to `enforce`.

## Data lifecycle

Sandbox state exists only for one run. It is not shared between runs or written
to disk. Generated reports contain a serialized scenario and trace, but every
registered synthetic secret is replaced recursively before serialization.

