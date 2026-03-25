# Security Policy

## Scope

RhinoGuard is a defensive test harness. Its bundled targets, secrets, mailboxes,
APIs, and shell are synthetic and local. Do not point scenarios at systems you
do not own or have explicit permission to test.

## Supported versions

The latest release on the default branch receives security fixes.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the repository owner. Do
not include live credentials, personal data, or payloads that target third-party
systems. Include the affected revision, reproduction steps, impact, and a safe
proof of concept when possible.

## Hard boundaries

- The synthetic HTTP tool never performs network requests.
- The synthetic email tool records messages locally and never sends mail.
- The shell simulator implements a tiny allowlisted command set and does not
  invoke an operating-system shell.
- Reports redact registered synthetic secret values.
- Real-provider credentials are read only from environment variables.

<!-- Document the next adjustment for security documentation -->
