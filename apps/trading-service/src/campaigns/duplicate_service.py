import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from src.database.models import DuplicateKeyModel, WhatsAppMessageModel, SignalModel, CampaignModel

class DuplicateProtectionService:
    DEFAULT_WINDOW_HOURS = 24

    @staticmethod
    def generate_semantic_fingerprint(
        instrument: str,
        direction: str,
        order_intent: str,
        zone_low: str,
        zone_high: str,
        stop_loss: Optional[str],
        tp1: Optional[str],
        tp2: Optional[str],
        tp_open_present: bool,
        group_id: str,
        sender_id: str
    ) -> str:
        """
        Generates SHA-256 hash over canonical JSON representation of normalized signal fields.
        """
        canonical_dict = {
            "instrument": instrument.upper(),
            "direction": direction.upper(),
            "order_intent": order_intent.upper(),
            "zone_low": f"{float(zone_low):.8f}",
            "zone_high": f"{float(zone_high):.8f}",
            "stop_loss": f"{float(stop_loss):.8f}" if stop_loss else None,
            "tp1": f"{float(tp1):.8f}" if tp1 else None,
            "tp2": f"{float(tp2):.8f}" if tp2 else None,
            "tp_open_present": bool(tp_open_present),
            "group_id": group_id,
            "sender_id": sender_id
        }
        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    def check_duplicate(
        self,
        db: Session,
        group_id: str,
        message_id: str,
        semantic_fingerprint: Optional[str] = None,
        duplicate_window_hours: int = 24
    ) -> Tuple[str, Optional[str]]:
        """
        Returns (decision_code, matched_campaign_id)
        Decision codes: NOT_DUPLICATE, EXACT_DUPLICATE, SEMANTIC_DUPLICATE
        """
        # 1. Exact Message Duplicate Check
        exact_key = f"EXACT_MESSAGE:{group_id}:{message_id}"
        exact_rec = db.query(DuplicateKeyModel).filter(DuplicateKeyModel.dedup_key == exact_key).first()
        if exact_rec:
            # Find campaign linked to exact message if exists
            raw_msg = db.get(WhatsAppMessageModel, message_id)
            if raw_msg and raw_msg.parsed_message and raw_msg.parsed_message.signal and raw_msg.parsed_message.signal.campaign:
                return "EXACT_DUPLICATE", raw_msg.parsed_message.signal.campaign.id
            return "EXACT_DUPLICATE", None

        # 2. Semantic Fingerprint Check
        if semantic_fingerprint:
            semantic_key = f"SEMANTIC_SIGNAL:{semantic_fingerprint}"
            semantic_rec = db.query(DuplicateKeyModel).filter(DuplicateKeyModel.dedup_key == semantic_key).first()
            if semantic_rec:
                now_utc = datetime.now(timezone.utc)
                if semantic_rec.expires_at is None:
                    is_valid_duplicate = True
                else:
                    exp = semantic_rec.expires_at
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    is_valid_duplicate = exp > now_utc

                if is_valid_duplicate:
                    if semantic_rec.message_id:
                        raw_msg = db.get(WhatsAppMessageModel, semantic_rec.message_id)
                        if raw_msg and raw_msg.parsed_message and raw_msg.parsed_message.signal and raw_msg.parsed_message.signal.campaign:
                            return "SEMANTIC_DUPLICATE", raw_msg.parsed_message.signal.campaign.id
                    return "SEMANTIC_DUPLICATE", None

        return "NOT_DUPLICATE", None

    def register_duplicate_keys(
        self,
        db: Session,
        group_id: str,
        message_id: str,
        semantic_fingerprint: Optional[str] = None,
        duplicate_window_hours: int = 24
    ) -> None:
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(hours=duplicate_window_hours)

        # Register Exact Key
        exact_key = f"EXACT_MESSAGE:{group_id}:{message_id}"
        if not db.query(DuplicateKeyModel).filter(DuplicateKeyModel.dedup_key == exact_key).first():
            db.add(DuplicateKeyModel(
                dedup_key=exact_key,
                duplicate_type="EXACT",
                message_id=message_id,
                expires_at=None,
                created_at=now_utc
            ))

        # Register Semantic Key if fingerprint provided
        if semantic_fingerprint:
            semantic_key = f"SEMANTIC_SIGNAL:{semantic_fingerprint}"
            if not db.query(DuplicateKeyModel).filter(DuplicateKeyModel.dedup_key == semantic_key).first():
                db.add(DuplicateKeyModel(
                    dedup_key=semantic_key,
                    duplicate_type="SEMANTIC",
                    message_id=message_id,
                    expires_at=expires_at,
                    created_at=now_utc
                ))
