from typing import List, Tuple, Dict, Any, Optional
from src.planning.constants import TP_CATEGORY_1, TP_CATEGORY_2, TP_CATEGORY_100
from src.planning.policies import TpIndexAllocationPolicy

def allocate_tp_categories(
    entry_count: int,
    direction: str,
    policy: TpIndexAllocationPolicy
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Allocates TP categories across entry_count entries based on policy.
    Returns (categories_list, list_of_issue_dicts).
    """
    issues = []
    if policy.value == "UNRESOLVED":
        issues.append({
            "code": "TP_INDEX_POLICY_MISSING",
            "severity": "ERROR",
            "message": "TP index allocation policy is UNRESOLVED. Explicit allocation policy required to compute entry TPs."
        })
        # Return fallback for preview structure
        return [TP_CATEGORY_100] * entry_count, issues

    tp1_idx: Optional[int] = None
    tp2_idx: Optional[int] = None

    if policy.value == "EXPLICIT_INDICES":
        tp1_idx = policy.tp1_index
        tp2_idx = policy.tp2_index
        if tp1_idx is None or tp2_idx is None or tp1_idx == tp2_idx or not (0 <= tp1_idx < entry_count) or not (0 <= tp2_idx < entry_count):
            issues.append({
                "code": "TP_INDEX_POLICY_MISSING",
                "severity": "ERROR",
                "message": f"EXPLICIT_INDICES policy requires distinct valid indices (tp1={tp1_idx}, tp2={tp2_idx}) for entry_count={entry_count}"
            })
            return [TP_CATEGORY_100] * entry_count, issues
    elif policy.value == "OUTER_BOUNDARIES_TO_SIGNAL_TPS":
        # Boundary allocation: index 0 and index N-1
        if direction.upper() == "SELL":
            tp1_idx = 0
            tp2_idx = entry_count - 1
        else:
            tp1_idx = 0
            tp2_idx = entry_count - 1
    elif policy.value == "LOWEST_INDICES_TO_SIGNAL_TPS":
        tp1_idx = 0
        tp2_idx = 1
    elif policy.value == "HIGHEST_INDICES_TO_SIGNAL_TPS":
        tp1_idx = entry_count - 2
        tp2_idx = entry_count - 1
    elif policy.value == "CENTER_TO_SIGNAL_TPS":
        mid = entry_count // 2
        tp1_idx = mid - 1
        tp2_idx = mid
    else:
        issues.append({
            "code": "TP_INDEX_POLICY_MISSING",
            "severity": "ERROR",
            "message": f"Unsupported TP index allocation policy '{policy.value}'"
        })
        return [TP_CATEGORY_100] * entry_count, issues

    categories = []
    for i in range(entry_count):
        if i == tp1_idx:
            categories.append(TP_CATEGORY_1)
        elif i == tp2_idx:
            categories.append(TP_CATEGORY_2)
        else:
            categories.append(TP_CATEGORY_100)

    return categories, issues
