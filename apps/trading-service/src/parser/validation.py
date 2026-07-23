from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class ValidationIssue:
    code: str
    severity: str  # INFO, WARNING, ERROR
    field: Optional[str]
    message: str
    sourceLine: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
            "sourceLine": self.sourceLine
        }

# Validation Issue Codes
EMPTY_MESSAGE = "EMPTY_MESSAGE"
UNSUPPORTED_INSTRUMENT = "UNSUPPORTED_INSTRUMENT"
INSTRUMENT_MISSING = "INSTRUMENT_MISSING"
DIRECTION_MISSING = "DIRECTION_MISSING"
DIRECTION_CONFLICT = "DIRECTION_CONFLICT"
ZONE_MISSING = "ZONE_MISSING"
ZONE_INVALID = "ZONE_INVALID"
ZONE_MULTIPLE_CONFLICT = "ZONE_MULTIPLE_CONFLICT"
ZONE_VALUES_REVERSED = "ZONE_VALUES_REVERSED"
STOP_LOSS_MISSING = "STOP_LOSS_MISSING"
TP1_MISSING = "TP1_MISSING"
TP2_MISSING = "TP2_MISSING"
TOO_MANY_TAKE_PROFITS = "TOO_MANY_TAKE_PROFITS"
INVALID_DECIMAL = "INVALID_DECIMAL"
AMBIGUOUS_COMMAND = "AMBIGUOUS_COMMAND"
UNSUPPORTED_MESSAGE = "UNSUPPORTED_MESSAGE"
MULTIPLE_EXPLICIT_COMMANDS = "MULTIPLE_EXPLICIT_COMMANDS"
