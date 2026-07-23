import hashlib
import json
from decimal import Decimal
from typing import List, Dict, Any, Tuple, Optional
from src.planning.constants import PLANNER_VERSION, RISK_ENGINE_VERSION
from src.planning.decimal_math import to_decimal
from src.planning.symbol_spec import SymbolSpecification, get_default_xauusd_spec
from src.planning.policies import PlanningPolicySnapshot, get_production_default_policies
from src.planning.ladder import calculate_entry_ladder
from src.planning.price_normalization import normalize_price_levels
from src.planning.volume_normalization import validate_and_normalize_volume
from src.planning.tp_allocation import allocate_tp_categories
from src.planning.tp_calculation import calculate_entry_tp
from src.planning.risk_engine import validate_campaign_risk

def generate_entry_magic_number(campaign_id: str, entry_sequence: int) -> int:
    seed = f"{campaign_id}:{entry_sequence}".encode("utf-8")
    hash_bytes = hashlib.sha256(seed).digest()
    # Convert first 4 bytes to unsigned 31-bit positive int
    val = int.from_bytes(hash_bytes[:4], byteorder="big") & 0x7FFFFFFF
    return val if val > 0 else 100001

def generate_planning_fingerprint(
    campaign_id: str,
    campaign_version: int,
    entry_count: int,
    lot_per_entry: Decimal,
    zone_low: Decimal,
    zone_high: Decimal,
    stop_loss: Decimal,
    tp1: Optional[Decimal],
    tp2: Optional[Decimal],
    spec: SymbolSpecification,
    policies: PlanningPolicySnapshot
) -> str:
    canonical = {
        "campaign_id": campaign_id,
        "campaign_version": campaign_version,
        "planner_version": PLANNER_VERSION,
        "risk_engine_version": RISK_ENGINE_VERSION,
        "entry_count": entry_count,
        "lot_per_entry": f"{lot_per_entry:.4f}",
        "zone_low": f"{zone_low:.8f}",
        "zone_high": f"{zone_high:.8f}",
        "stop_loss": f"{stop_loss:.8f}",
        "tp1": f"{tp1:.8f}" if tp1 else None,
        "tp2": f"{tp2:.8f}" if tp2 else None,
        "symbol_spec": spec.to_dict(),
        "policies": policies.to_dict()
    }
    raw_json = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw_json.encode('utf-8')).hexdigest()

def plan_campaign_entries(
    campaign_id: str,
    campaign_code: str,
    campaign_state: str,
    direction: str,
    order_intent: str,
    entry_count: int,
    lot_per_entry: Decimal,
    maximum_total_lots: Decimal,
    zone_low: Decimal,
    zone_high: Decimal,
    stop_loss: Decimal,
    tp1: Optional[Decimal],
    tp2: Optional[Decimal],
    tp_open_present: bool,
    campaign_version: int = 1,
    spec: Optional[SymbolSpecification] = None,
    policies: Optional[PlanningPolicySnapshot] = None
) -> Dict[str, Any]:
    spec = spec or get_default_xauusd_spec()
    policies = policies or get_production_default_policies()

    all_issues = []

    # 1. Volume & Exposure Validation
    req_lots, vol_issues = validate_and_normalize_volume(
        entry_count=entry_count,
        lot_per_entry=lot_per_entry,
        maximum_total_lots=maximum_total_lots,
        spec=spec
    )
    all_issues.extend(vol_issues)

    # 2. Entry Ladder Calculation
    raw_levels, raw_step = calculate_entry_ladder(zone_low, zone_high, entry_count)

    # 3. Price Normalization to Tick Size
    norm_levels, price_issues = normalize_price_levels(raw_levels, zone_low, zone_high, spec)
    all_issues.extend(price_issues)

    # 4. Risk Engine Validation
    risk_issues = validate_campaign_risk(
        campaign_state=campaign_state,
        direction=direction,
        order_intent=order_intent,
        entry_count=entry_count,
        stop_loss=stop_loss,
        price_levels=norm_levels,
        trading_enabled=False,
        policies=policies
    )
    all_issues.extend(risk_issues)

    # 5. TP Category Allocation
    tp_categories, tp_alloc_issues = allocate_tp_categories(entry_count, direction, policies.tp_index_policy)
    all_issues.extend(tp_alloc_issues)

    # 6. Calculate Per-Entry Planned Entries
    planned_entries = []
    direction_upper = direction.upper()
    order_type_str = f"{direction_upper}_LIMIT"

    for i in range(entry_count):
        seq = i + 1
        price = norm_levels[i]
        category = tp_categories[i]

        calc_tp, tp_calc_issues = calculate_entry_tp(
            direction=direction,
            entry_price=price,
            tp_category=category,
            signal_tp1=tp1,
            signal_tp2=tp2,
            pip_policy=policies.hundred_pip_policy,
            spec=spec
        )
        all_issues.extend(tp_calc_issues)

        magic = generate_entry_magic_number(campaign_id, seq)
        comment = f"WA-{campaign_code}-E{seq:02d}-{category}"

        planned_entries.append({
            "entry_sequence": seq,
            "ladder_index": i,
            "planned_price": f"{raw_levels[i]:.8f}",
            "normalized_price": f"{price:.8f}",
            "lot_size": f"{lot_per_entry:.4f}",
            "stop_loss": f"{stop_loss:.8f}",
            "take_profit": f"{calc_tp:.8f}" if calc_tp else None,
            "tp_category": category,
            "order_type": order_type_str,
            "magic_number": magic,
            "order_comment": comment,
            "status": "PLANNED"
        })

    has_errors = any(issue.get("severity") == "ERROR" for issue in all_issues)
    fingerprint = generate_planning_fingerprint(
        campaign_id=campaign_id,
        campaign_version=campaign_version,
        entry_count=entry_count,
        lot_per_entry=lot_per_entry,
        zone_low=zone_low,
        zone_high=zone_high,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        spec=spec,
        policies=policies
    )

    return {
        "campaign_id": campaign_id,
        "campaign_code": campaign_code,
        "planner_version": PLANNER_VERSION,
        "risk_engine_version": RISK_ENGINE_VERSION,
        "planning_fingerprint": fingerprint,
        "entry_count": entry_count,
        "lot_per_entry": f"{lot_per_entry:.4f}",
        "requested_total_lots": f"{req_lots:.4f}",
        "maximum_total_lots": f"{maximum_total_lots:.4f}",
        "zone_low": f"{zone_low:.8f}",
        "zone_high": f"{zone_high:.8f}",
        "stop_loss": f"{stop_loss:.8f}",
        "tp1": f"{tp1:.8f}" if tp1 else None,
        "tp2": f"{tp2:.8f}" if tp2 else None,
        "tp_open_present": tp_open_present,
        "is_valid": not has_errors,
        "validation_issues": all_issues,
        "planned_entries": planned_entries if not has_errors else [],
        "policy_snapshot": policies.to_dict(),
        "symbol_spec": spec.to_dict()
    }
