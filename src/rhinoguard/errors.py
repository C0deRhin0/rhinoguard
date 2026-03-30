class RhinoGuardError(Exception):
    """Base exception for expected RhinoGuard failures."""


class ScenarioValidationError(RhinoGuardError):
    """Raised when a scenario document is invalid."""


class AdapterError(RhinoGuardError):
    """Raised when a model adapter cannot produce a valid response."""


class ToolExecutionError(RhinoGuardError):
    """Raised when a synthetic tool cannot complete a request."""
# Document the next adjustment for errors module
