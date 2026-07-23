class OrchestrationError(Exception):
    """Base exception for orchestration domain."""
    def __init__(self, message: str, code: str = "ORCHESTRATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class EmergencyStopActiveError(OrchestrationError):
    def __init__(self, message: str = "Operation blocked: Emergency stop is currently active."):
        super().__init__(message, "EMERGENCY_STOP_ACTIVE")

class InvalidControlPhraseError(OrchestrationError):
    def __init__(self, message: str = "Invalid control confirmation phrase."):
        super().__init__(message, "INVALID_CONTROL_PHRASE")

class ExecutionBlockedError(OrchestrationError):
    def __init__(self, reason: str):
        super().__init__(f"Execution blocked: {reason}", "EXECUTION_BLOCKED")
