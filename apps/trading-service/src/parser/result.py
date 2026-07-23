from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from src.parser.constants import PARSER_VERSION, CONTRACT_VERSION
from src.parser.validation import ValidationIssue

@dataclass
class ParserResult:
    contractVersion: str = CONTRACT_VERSION
    parserVersion: str = PARSER_VERSION
    category: str = "INVALID"  # NEW_SIGNAL, FOLLOW_UP_COMMAND, INFORMATIONAL, AMBIGUOUS, INVALID, UNSUPPORTED
    isExecutable: bool = False
    requiresConfirmation: bool = True
    executionEligibility: str = "NEVER"  # NEVER, REQUIRES_CONFIRMATION, ELIGIBLE_AFTER_CAMPAIGN_MATCH, ELIGIBLE_AFTER_VALIDATION
    originalText: str = ""
    normalizedText: str = ""
    signal: Optional[Dict[str, Any]] = None
    command: Optional[Dict[str, Any]] = None
    commands: List[Dict[str, Any]] = field(default_factory=list)
    informational: Optional[Dict[str, Any]] = None
    ambiguous: Optional[Dict[str, Any]] = None
    validationIssues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    campaignMatchStrategyHint: str = "NONE"  # QUOTED_MESSAGE, LATEST_COMPATIBLE, NONE
    sourceMetadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contractVersion": self.contractVersion,
            "parserVersion": self.parserVersion,
            "category": self.category,
            "isExecutable": self.isExecutable,
            "requiresConfirmation": self.requiresConfirmation,
            "executionEligibility": self.executionEligibility,
            "originalText": self.originalText,
            "normalizedText": self.normalizedText,
            "signal": self.signal,
            "command": self.command,
            "commands": self.commands,
            "informational": self.informational,
            "ambiguous": self.ambiguous,
            "validationIssues": self.validationIssues,
            "warnings": self.warnings,
            "campaignMatchStrategyHint": self.campaignMatchStrategyHint,
            "sourceMetadata": self.sourceMetadata
        }
