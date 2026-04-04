# Local API

Start the service with `rhinoguard serve`. It binds to `127.0.0.1:8080` unless
the operator explicitly selects another interface.

## `GET /healthz`

Returns service status and version.

## `GET /v1/scenarios`

Lists stable scenario identifiers, names, categories, and severities. It does
not return fixture contents or registered secrets.

## `POST /v1/runs`

```json
{
  "scenario_id": "RG-PI-002",
  "mode": "defended",
  "provider": "scripted"
}
```

Accepted modes are `vulnerable`, `defended`, `monitor`, `enforce`, and `off`.
The response is the recursively redacted run payload.

The API is designed for local automation. It does not provide authentication,
multi-tenancy, job queues, or arbitrary filesystem scenario selection.

<!-- Clarify implementation notes for api documentation -->
<!-- Review follow-up details for api documentation -->
