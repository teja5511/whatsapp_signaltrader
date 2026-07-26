"""Persistence and resolution for the trading policy catalog."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.models import TradingPolicyModel
from src.policies.catalog import (
    POLICY_BY_KEY,
    POLICY_CATALOG_VERSION,
    POLICY_DEFINITIONS,
    PLANNING_BLOCKING_KEYS,
    COMMAND_BLOCKING_KEYS,
    STATUS_CONFIRMED,
    STATUS_UNRESOLVED,
    PolicyDefinition,
)


class UnknownPolicyError(ValueError):
    pass


class InvalidPolicyOptionError(ValueError):
    pass


class PolicyUnresolvedError(RuntimeError):
    """Raised when a pipeline needs a policy that nobody has confirmed."""

    def __init__(self, keys: List[str]):
        self.keys = keys
        super().__init__(
            "Blocked by unresolved trading policies: " + ", ".join(sorted(keys))
        )


@dataclass(frozen=True)
class PolicyResolution:
    key: str
    status: str
    selected_option: Optional[str]
    parameters: Dict[str, Any]

    @property
    def is_resolved(self) -> bool:
        return self.status == STATUS_CONFIRMED and self.selected_option is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "status": self.status,
            "selected_option": self.selected_option,
            "parameters": dict(self.parameters),
        }


def _validate_parameters(definition: PolicyDefinition, option_value: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    option = definition.option(option_value)
    if option is None:
        valid = ", ".join(o.value for o in definition.options)
        raise InvalidPolicyOptionError(
            f"Option '{option_value}' is not valid for policy '{definition.key}'. Valid options: {valid}"
        )

    cleaned: Dict[str, Any] = {}
    for name in option.required_parameters:
        if name not in parameters or parameters[name] in (None, ""):
            raise InvalidPolicyOptionError(
                f"Policy '{definition.key}' option '{option_value}' requires parameter '{name}'."
            )
        raw = parameters[name]
        if name.endswith("_index"):
            try:
                cleaned[name] = int(raw)
            except (TypeError, ValueError):
                raise InvalidPolicyOptionError(f"Parameter '{name}' must be an integer.")
        elif name.endswith("distance"):
            try:
                dec = Decimal(str(raw))
            except (InvalidOperation, TypeError, ValueError):
                raise InvalidPolicyOptionError(f"Parameter '{name}' must be a decimal value.")
            if dec <= 0:
                raise InvalidPolicyOptionError(f"Parameter '{name}' must be greater than zero.")
            cleaned[name] = format(dec.quantize(Decimal("0.00000001")), "f")
        else:
            cleaned[name] = raw
    return cleaned


class PolicyService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    # -- seeding ------------------------------------------------------------

    @staticmethod
    def seed_missing(db: Session) -> int:
        """Create UNRESOLVED rows for any catalog entry that has none."""
        created = 0
        existing = {row.key for row in db.query(TradingPolicyModel).all()}
        now_utc = datetime.now(timezone.utc)
        for definition in POLICY_DEFINITIONS:
            if definition.key in existing:
                continue
            db.add(
                TradingPolicyModel(
                    key=definition.key,
                    selected_option=None,
                    parameters_json="{}",
                    status=STATUS_UNRESOLVED,
                    updated_at=now_utc,
                )
            )
            created += 1
        if created:
            db.flush()
        return created

    def ensure_seeded(self) -> int:
        db = self.session_factory()
        try:
            created = self.seed_missing(db)
            db.commit()
            return created
        finally:
            db.close()

    # -- reads --------------------------------------------------------------

    @staticmethod
    def resolution_from_db(db: Session, key: str) -> PolicyResolution:
        if key not in POLICY_BY_KEY:
            raise UnknownPolicyError(f"Unknown policy '{key}'.")
        row = db.get(TradingPolicyModel, key)
        if row is None:
            return PolicyResolution(key=key, status=STATUS_UNRESOLVED, selected_option=None, parameters={})
        return PolicyResolution(
            key=key,
            status=row.status,
            selected_option=row.selected_option,
            parameters=json.loads(row.parameters_json or "{}"),
        )

    @staticmethod
    def all_resolutions(db: Session) -> Dict[str, PolicyResolution]:
        PolicyService.seed_missing(db)
        return {d.key: PolicyService.resolution_from_db(db, d.key) for d in POLICY_DEFINITIONS}

    def list_policies(self) -> Dict[str, Any]:
        db = self.session_factory()
        try:
            resolutions = self.all_resolutions(db)
            db.commit()
            items = []
            for definition in POLICY_DEFINITIONS:
                res = resolutions[definition.key]
                row = db.get(TradingPolicyModel, definition.key)
                items.append(
                    {
                        **definition.to_dict(),
                        "status": res.status,
                        "selected_option": res.selected_option,
                        "parameters": res.parameters,
                        "confirmed_by": row.confirmed_by if row else None,
                        "confirmed_at": row.confirmed_at.isoformat() if row and row.confirmed_at else None,
                    }
                )
            unresolved = [k for k, r in resolutions.items() if not r.is_resolved]
            return {
                "policy_catalog_version": POLICY_CATALOG_VERSION,
                "total": len(items),
                "unresolved_count": len(unresolved),
                "unresolved_keys": sorted(unresolved),
                "planning_blocked": sorted(k for k in unresolved if k in PLANNING_BLOCKING_KEYS),
                "command_blocked": sorted(k for k in unresolved if k in COMMAND_BLOCKING_KEYS),
                "policies": items,
            }
        finally:
            db.close()

    def unresolved_planning_keys(self) -> List[str]:
        db = self.session_factory()
        try:
            resolutions = self.all_resolutions(db)
            db.commit()
            return sorted(k for k in PLANNING_BLOCKING_KEYS if not resolutions[k].is_resolved)
        finally:
            db.close()

    # -- writes -------------------------------------------------------------

    def confirm(
        self,
        key: str,
        selected_option: str,
        parameters: Optional[Dict[str, Any]] = None,
        actor: str = "OPERATOR",
    ) -> Dict[str, Any]:
        definition = POLICY_BY_KEY.get(key)
        if definition is None:
            raise UnknownPolicyError(f"Unknown policy '{key}'.")

        cleaned = _validate_parameters(definition, selected_option, parameters or {})

        db = self.session_factory()
        try:
            self.seed_missing(db)
            row = db.get(TradingPolicyModel, key)
            now_utc = datetime.now(timezone.utc)
            row.selected_option = selected_option
            row.parameters_json = json.dumps(cleaned, sort_keys=True)
            row.status = STATUS_CONFIRMED
            row.confirmed_by = actor
            row.confirmed_at = now_utc
            row.updated_at = now_utc
            db.commit()
            return {
                "key": key,
                "status": STATUS_CONFIRMED,
                "selected_option": selected_option,
                "parameters": cleaned,
                "confirmed_by": actor,
                "confirmed_at": now_utc.isoformat(),
            }
        finally:
            db.close()

    def reset(self, key: str) -> Dict[str, Any]:
        if key not in POLICY_BY_KEY:
            raise UnknownPolicyError(f"Unknown policy '{key}'.")
        db = self.session_factory()
        try:
            self.seed_missing(db)
            row = db.get(TradingPolicyModel, key)
            now_utc = datetime.now(timezone.utc)
            row.selected_option = None
            row.parameters_json = "{}"
            row.status = STATUS_UNRESOLVED
            row.confirmed_by = None
            row.confirmed_at = None
            row.updated_at = now_utc
            db.commit()
            return {"key": key, "status": STATUS_UNRESOLVED}
        finally:
            db.close()


def resolutions_to_snapshot_dict(resolutions: Dict[str, PolicyResolution]) -> Dict[str, Any]:
    """Canonical, order-stable representation for planning fingerprints."""
    return {
        "policy_catalog_version": POLICY_CATALOG_VERSION,
        "resolutions": {
            key: {
                "status": res.status,
                "selected_option": res.selected_option,
                "parameters": res.parameters,
            }
            for key, res in sorted(resolutions.items())
        },
    }
