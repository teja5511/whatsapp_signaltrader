"""Catalog of trading policies that must be chosen explicitly.

Each entry is a typed policy with an explicit option set and no implicit default.
Until an operator confirms an option, the policy reports UNRESOLVED and every
pipeline that depends on it blocks. Nothing here is ever guessed.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

POLICY_CATALOG_VERSION = "1.0.0"

STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_CONFIRMED = "CONFIRMED"

# Which subsystem is blocked while a policy is unresolved.
BLOCKS_PLANNING = "PLANNING"
BLOCKS_EXECUTION = "EXECUTION"
BLOCKS_COMMAND = "COMMAND"


@dataclass(frozen=True)
class PolicyOption:
    value: str
    label: str
    description: str
    #: Parameters the operator must supply alongside this option.
    required_parameters: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyDefinition:
    key: str
    title: str
    decision_reference: str
    description: str
    blocks: str
    options: List[PolicyOption]
    #: Commands whose handling depends on this policy (COMMAND-blocking only).
    applies_to_commands: List[str] = field(default_factory=list)

    def option(self, value: str) -> Optional[PolicyOption]:
        return next((o for o in self.options if o.value == value), None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "decision_reference": self.decision_reference,
            "description": self.description,
            "blocks": self.blocks,
            "applies_to_commands": list(self.applies_to_commands),
            "options": [
                {
                    "value": o.value,
                    "label": o.label,
                    "description": o.description,
                    "required_parameters": list(o.required_parameters),
                }
                for o in self.options
            ],
        }


# --- Policy keys -------------------------------------------------------------

POLICY_HUNDRED_PIP = "hundred_pip_distance"
POLICY_TP_INDEX = "tp_index_allocation"
POLICY_PRICE_INSIDE_ZONE = "price_inside_zone"
POLICY_PRICE_PAST_ZONE = "price_past_zone"
POLICY_ORDER_INTENT = "unspecified_order_intent"
POLICY_DELAYED_TP = "delayed_tp_arrival"
POLICY_SECURE_PROFITS = "secure_profits_phrase"
POLICY_EXIT_COMFORT = "exit_on_comfort_phrase"
POLICY_HOLD_IT = "hold_it_phrase"
POLICY_SKIP_FOR_NOW = "skip_this_for_now"
POLICY_ZONE_VALID = "zone_valid_reactivation"
POLICY_CONCURRENT_CAMPAIGN = "new_signal_while_active"
POLICY_FILLED_AFTER_NEW_SIGNAL = "filled_positions_after_new_signal"


POLICY_DEFINITIONS: List[PolicyDefinition] = [
    PolicyDefinition(
        key=POLICY_HUNDRED_PIP,
        title="Exact XAUUSD meaning of 100 pips",
        decision_reference="OPEN_DECISIONS Item 1",
        description=(
            "Price delta represented by the fixed 100-pip take profit target. "
            "Choosing wrong sets every non-signal TP 10x too wide or too tight."
        ),
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("PRICE_DELTA_1_00", "100 pips = 1.00 price delta", "100 points on a 2-digit gold quote."),
            PolicyOption("PRICE_DELTA_10_00", "100 pips = 10.00 price delta", "1000 points on a 2-digit gold quote."),
            PolicyOption("CUSTOM_PRICE_DELTA", "Custom price delta", "Explicit delta supplied by the operator.", ["price_distance"]),
        ],
    ),
    PolicyDefinition(
        key=POLICY_TP_INDEX,
        title="Ladder indices that receive signal TP1 and TP2",
        decision_reference="OPEN_DECISIONS Item 5",
        description="Which ladder entries carry the signal TPs; all others carry the fixed 100-pip target.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("LOWEST_INDICES_TO_SIGNAL_TPS", "Index 0 -> TP1, index 1 -> TP2", "Shallowest two entries take the signal TPs."),
            PolicyOption("HIGHEST_INDICES_TO_SIGNAL_TPS", "Index N-2 -> TP1, index N-1 -> TP2", "Deepest two entries take the signal TPs."),
            PolicyOption("OUTER_BOUNDARIES_TO_SIGNAL_TPS", "Index 0 -> TP1, index N-1 -> TP2", "Zone boundaries take the signal TPs."),
            PolicyOption("CENTER_TO_SIGNAL_TPS", "Two central indices", "Middle of the ladder takes the signal TPs."),
            PolicyOption("EXPLICIT_INDICES", "Explicit indices", "Operator names both indices.", ["tp1_index", "tp2_index"]),
        ],
    ),
    PolicyDefinition(
        key=POLICY_PRICE_INSIDE_ZONE,
        title="Live price already inside the entry zone",
        decision_reference="OPEN_DECISIONS Item 2",
        description="Behaviour when the market is mid-zone at signal arrival.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("BLOCK_IF_INSIDE_ZONE", "Block the campaign", "Safest: refuse to plan and require operator review."),
            PolicyOption("LIMIT_STOP_SPLIT", "Split into limit and stop orders", "Levels beyond the market become stop orders."),
            PolicyOption("SKIP_PASSED_LEVELS", "Skip crossed levels", "Plan only the levels the market has not reached."),
            PolicyOption("REJECT_STALE", "Reject the signal as stale", "Campaign is cancelled."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_PRICE_PAST_ZONE,
        title="Live price has passed the whole entry zone",
        decision_reference="OPEN_DECISIONS Item 3",
        description="Behaviour when the market has fully breached the zone before planning.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("BLOCK_IF_ZONE_PASSED", "Block the campaign", "Safest: refuse to plan and require operator review."),
            PolicyOption("PLACE_LIMITS_ANYWAY", "Place limit orders anyway", "Wait for a retracement into the zone."),
            PolicyOption("CANCEL_AS_MISSED", "Cancel as missed", "Campaign is cancelled."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_ORDER_INTENT,
        title="Signal without an explicit order intent",
        decision_reference="TRADING_RULES 2.4",
        description="What to do when the signal text does not say limit or stop.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("BLOCK", "Block the campaign", "Require an explicit intent."),
            PolicyOption("TREAT_AS_LIMIT", "Treat as limit", "Assume pending limit orders."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_DELAYED_TP,
        title="TP1/TP2 arriving in a later message",
        decision_reference="OPEN_DECISIONS Item 4",
        description="Whether to hold the campaign until the exit plan is complete.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("WAIT_FOR_TP", "Wait for the TP message", "No orders until the exit plan is complete."),
            PolicyOption("PLACE_WITH_DEFAULT_TP", "Place now with the fixed target", "Update TPs when the message arrives."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_SECURE_PROFITS,
        title='Interpretation of "Secure Profits"',
        decision_reference="OPEN_DECISIONS Item 6",
        description="Action taken when the admin posts a secure-profits instruction.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["SECURE_PROFITS"],
        options=[
            PolicyOption("REQUIRE_CONFIRMATION", "Raise a confirmation card", "Never automated."),
            PolicyOption("MOVE_SL_BREAK_EVEN", "Move stop loss to break even", "Applies to all open positions."),
            PolicyOption("CLOSE_HALF", "Close half the open volume", "Partial close across open positions."),
            PolicyOption("INFORMATIONAL_ONLY", "Log only", "No trading action."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_EXIT_COMFORT,
        title='Interpretation of "Exit on your comfort"',
        decision_reference="OPEN_DECISIONS Item 7",
        description="Action taken when the admin defers the exit to the operator.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["EXIT_ON_COMFORT"],
        options=[
            PolicyOption("REQUIRE_CONFIRMATION", "Raise a confirmation card with a close button", "Never automated."),
            PolicyOption("INFORMATIONAL_ONLY", "Log only", "No trading action."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_HOLD_IT,
        title='Interpretation of "Hold it"',
        decision_reference="OPEN_DECISIONS Item 8",
        description="Action taken when the admin says to hold.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["HOLD"],
        options=[
            PolicyOption("INFORMATIONAL_ONLY", "Log only", "No trading action."),
            PolicyOption("FREEZE_AUTOMATION", "Freeze automated modifications", "Blocks automated SL/TP changes for the campaign."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_SKIP_FOR_NOW,
        title='Action of "Skip this for now"',
        decision_reference="OPEN_DECISIONS Item 11",
        description="Effect on a campaign with live pending orders.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["SKIP"],
        options=[
            PolicyOption("REQUIRE_CONFIRMATION", "Raise a confirmation card", "Never automated."),
            PolicyOption("CANCEL_PENDING", "Cancel pending grid orders", "Removes unfilled exposure."),
            PolicyOption("PAUSE_ONLY", "Pause automation only", "Leaves broker orders in place."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_ZONE_VALID,
        title='Action of "Zone Valid" on a paused campaign',
        decision_reference="OPEN_DECISIONS Item 12",
        description="Whether a paused campaign resubmits orders automatically.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["ZONE_VALID"],
        options=[
            PolicyOption("REQUIRE_CONFIRMATION", "Raise a confirmation card", "Operator re-enables manually."),
            PolicyOption("AUTO_REACTIVATE", "Reactivate and resubmit", "Resubmits the pending grid."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_CONCURRENT_CAMPAIGN,
        title="New signal while another campaign is active",
        decision_reference="OPEN_DECISIONS Item 9",
        description="Whether campaigns may coexist on the hedging account.",
        blocks=BLOCKS_PLANNING,
        options=[
            PolicyOption("BLOCK_UNTIL_REVIEWED", "Block the new campaign", "Safest: operator decides."),
            PolicyOption("COEXIST_DISTINCT_MAGIC", "Allow coexistence", "Separate magic numbers per campaign."),
            PolicyOption("CANCEL_PREVIOUS", "Cancel the previous campaign", "Old pending orders are cancelled first."),
        ],
    ),
    PolicyDefinition(
        key=POLICY_FILLED_AFTER_NEW_SIGNAL,
        title="Filled positions when a campaign is superseded",
        decision_reference="OPEN_DECISIONS Item 10",
        description="Whether already-filled positions are closed when a campaign is replaced.",
        blocks=BLOCKS_COMMAND,
        applies_to_commands=["SUPERSEDE"],
        options=[
            PolicyOption("LEAVE_RUNNING", "Leave positions running", "Only pending orders are cancelled."),
            PolicyOption("CLOSE_IMMEDIATELY", "Close open positions", "Realises PnL immediately."),
            PolicyOption("REQUIRE_CONFIRMATION", "Raise a confirmation card", "Operator decides per campaign."),
        ],
    ),
]

POLICY_BY_KEY: Dict[str, PolicyDefinition] = {p.key: p for p in POLICY_DEFINITIONS}

PLANNING_BLOCKING_KEYS = [p.key for p in POLICY_DEFINITIONS if p.blocks == BLOCKS_PLANNING]
COMMAND_BLOCKING_KEYS = [p.key for p in POLICY_DEFINITIONS if p.blocks == BLOCKS_COMMAND]

#: Command types that must never execute automatically, regardless of policy.
NEVER_AUTOMATIC_COMMANDS = {"AMBIGUOUS", "UNKNOWN"}
