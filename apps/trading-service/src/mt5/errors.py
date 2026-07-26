"""MT5 Domain Exception Hierarchy."""
from typing import Optional, Any, Dict

class MT5Error(Exception):
    """Base domain exception for MT5 operations."""
    def __init__(self, message: str, code: str = "MT5_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class MT5PackageUnavailableError(MT5Error):
    def __init__(self, reason: str = ""):
        super().__init__(f"MetaTrader5 Python package is unavailable. {reason}".strip(), code="MT5_PACKAGE_UNAVAILABLE")

class MT5InitializeFailedError(MT5Error):
    def __init__(self, reason: str = ""):
        super().__init__(f"MT5 initialization failed: {reason}", code="MT5_INITIALIZE_FAILED")

class MT5LiveAccountBlockedError(MT5Error):
    def __init__(self, login: int, env_kind: str):
        super().__init__(f"Live account {login} (environment '{env_kind}') blocked. Only DEMO accounts permitted.", code="MT5_LIVE_ACCOUNT_BLOCKED")

class MT5AccountNotHedgingError(MT5Error):
    def __init__(self, margin_mode: str):
        super().__init__(f"Account margin mode '{margin_mode}' is not HEDGING. Execution blocked.", code="MT5_ACCOUNT_NOT_HEDGING")

class MT5AccountNotAllowedError(MT5Error):
    def __init__(self, login: int):
        super().__init__(f"Account login {login} is not in allowed logins list.", code="MT5_ACCOUNT_NOT_ALLOWED")

class MT5ServerNotAllowedError(MT5Error):
    def __init__(self, server: str):
        super().__init__(f"Server '{server}' is not in allowed servers list.", code="MT5_SERVER_NOT_ALLOWED")

class XAUUSDSymbolNotFoundError(MT5Error):
    def __init__(self, reason: str = ""):
        super().__init__(f"XAUUSD symbol not found on broker terminal. {reason}".strip(), code="XAUUSD_SYMBOL_NOT_FOUND")

class XAUUSDSymbolAmbiguousError(MT5Error):
    def __init__(self, matches: list):
        super().__init__(f"Multiple XAUUSD symbol candidates found: {matches}", code="XAUUSD_SYMBOL_AMBIGUOUS")

class SymbolSpecificationChangedError(MT5Error):
    def __init__(self, field: str, expected: Any, actual: Any):
        super().__init__(f"Symbol specification changed on '{field}': expected {expected}, got {actual}. Replan required.", code="SYMBOL_SPECIFICATION_CHANGED")

class OrderCheckFailedError(MT5Error):
    def __init__(self, retcode: int, retcode_name: str, comment: str):
        super().__init__(f"MT5 order_check failed [Retcode {retcode} - {retcode_name}]: {comment}", code="ORDER_CHECK_FAILED", details={"retcode": retcode, "retcode_name": retcode_name, "comment": comment})

class OrderSendFailedError(MT5Error):
    def __init__(self, retcode: int, retcode_name: str, comment: str):
        super().__init__(f"MT5 order_send failed [Retcode {retcode} - {retcode_name}]: {comment}", code="ORDER_SEND_FAILED", details={"retcode": retcode, "retcode_name": retcode_name, "comment": comment})

class ExecutionOutcomeUnknownError(MT5Error):
    def __init__(self, job_id: str, reason: str):
        super().__init__(f"Execution outcome unknown for job '{job_id}': {reason}. Automatic retry blocked.", code="EXECUTION_OUTCOME_UNKNOWN")

class BrokerMutationFailedError(MT5Error):
    def __init__(self, ticket: int, operation: str, retcode: int, comment: str):
        super().__init__(
            f"Broker rejected {operation} on ticket {ticket} [retcode {retcode}]: {comment}",
            code="BROKER_MUTATION_FAILED",
            details={"ticket": ticket, "operation": operation, "retcode": retcode, "comment": comment},
        )
        self.ticket = ticket
        self.operation = operation

class BrokerOutcomeUnknownError(MT5Error):
    """The request left the process but the result was never confirmed.

    Local state is deliberately left untouched: reconciliation resolves it, and
    the operation is never retried automatically.
    """
    def __init__(self, ticket: int, operation: str, comment: str):
        super().__init__(
            f"Outcome unknown for {operation} on ticket {ticket}: {comment}. "
            "Local state unchanged; resolve via reconciliation.",
            code="BROKER_OUTCOME_UNKNOWN",
            details={"ticket": ticket, "operation": operation, "comment": comment},
        )
        self.ticket = ticket
        self.operation = operation

class UnauthorizedLocalApiError(MT5Error):
    def __init__(self):
        super().__init__("Invalid or missing local API authorization token.", code="UNAUTHORIZED_LOCAL_API")

class EmergencyCloseDisabledError(MT5Error):
    def __init__(self):
        super().__init__("Emergency close-all operation is disabled by configuration.", code="EMERGENCY_CLOSE_DISABLED")

class InvalidCloseConfirmationError(MT5Error):
    def __init__(self, provided: str):
        super().__init__(f"Invalid emergency close confirmation phrase '{provided}'.", code="CLOSE_CONFIRMATION_INVALID")
