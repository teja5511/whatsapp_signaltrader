import hashlib
import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from src.database.unit_of_work import UnitOfWork
from src.database.engine import SessionLocal
from src.database.models import WhatsAppMessageModel, ParsedMessageModel, SignalModel
from src.parser.classification import parse_raw_text
from src.parser.result import ParserResult

class MessageParsingService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def parse_stateless(
        self,
        text: str,
        message_id: str,
        group_id: str,
        sender_id: str,
        quoted_message_id: Optional[str] = None,
        is_reply: bool = False
    ) -> Dict[str, Any]:
        res = parse_raw_text(
            raw_text=text,
            message_id=message_id,
            group_id=group_id,
            sender_id=sender_id,
            quoted_message_id=quoted_message_id,
            is_reply=is_reply
        )
        return res.to_dict()

    def parse_and_persist(
        self,
        raw_text: str,
        message_id: str,
        group_id: str,
        sender_id: str,
        is_admin: bool = True,
        quoted_message_id: str = None,
        is_reply: bool = False
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Returns (parser_result_dict, is_duplicate_submission)
        """
        content_hash = hashlib.sha256(raw_text.strip().encode("utf-8")).hexdigest()
        dedup_key = f"{group_id}:{message_id}"

        with UnitOfWork(session_factory=self.session_factory) as uow:
            # Check Idempotency for raw message submission
            if uow.messages.is_duplicate(dedup_key):
                # Retrieve existing parsed message
                existing_msg = uow.db.get(WhatsAppMessageModel, message_id)
                if existing_msg and existing_msg.parsed_message:
                    existing_result = json.loads(existing_msg.parsed_message.parsed_json)
                    return existing_result, True

            # 1. Store Raw WhatsApp Message
            now_utc = datetime.now(timezone.utc)
            raw_msg = WhatsAppMessageModel(
                id=message_id,
                group_id=group_id,
                sender_id=sender_id,
                is_admin=is_admin,
                raw_content=raw_text,
                content_hash=content_hash,
                received_at=now_utc
            )
            uow.messages.add_message(raw_msg, dedup_key)

            # 2. Run Deterministic Parser
            parse_result: ParserResult = parse_raw_text(
                raw_text=raw_text,
                message_id=message_id,
                group_id=group_id,
                sender_id=sender_id,
                quoted_message_id=quoted_message_id,
                is_reply=is_reply
            )
            parse_dict = parse_result.to_dict()
            category_val = parse_result.category.value if hasattr(parse_result.category, "value") else str(parse_result.category)

            # 3. Store Parsed Message Record
            parsed_id = str(uuid4())
            parsed_rec = ParsedMessageModel(
                id=parsed_id,
                raw_message_id=message_id,
                message_type=category_val,
                parsed_json=json.dumps(parse_dict),
                parsed_at=now_utc
            )
            uow.db.add(parsed_rec)
            uow.db.flush()

            # 4. Store Signal Record if NEW_SIGNAL
            if category_val == "NEW_SIGNAL" and parse_result.signal:
                sig_dto = parse_result.signal
                if isinstance(sig_dto, dict):
                    instrument = sig_dto.get("instrument", "XAUUSD")
                    direction_val = str(sig_dto.get("direction", "SELL"))
                    entry_min = float(sig_dto.get("zoneLow", 0.0))
                    entry_max = float(sig_dto.get("zoneHigh", 0.0))
                    stop_loss = float(sig_dto.get("stopLoss")) if sig_dto.get("stopLoss") else 0.0
                    tp1 = float(sig_dto.get("tp1")) if sig_dto.get("tp1") else None
                    tp2 = float(sig_dto.get("tp2")) if sig_dto.get("tp2") else None
                    has_tp_open = bool(sig_dto.get("tpOpenPresent", False))
                else:
                    instrument = sig_dto.instrument
                    direction_val = sig_dto.direction.value if hasattr(sig_dto.direction, "value") else str(sig_dto.direction)
                    entry_min = float(sig_dto.zoneLow)
                    entry_max = float(sig_dto.zoneHigh)
                    stop_loss = float(sig_dto.stopLoss) if sig_dto.stopLoss else 0.0
                    tp1 = float(sig_dto.tp1) if sig_dto.tp1 else None
                    tp2 = float(sig_dto.tp2) if sig_dto.tp2 else None
                    has_tp_open = sig_dto.tpOpenPresent

                signal_rec = SignalModel(
                    id=str(uuid4()),
                    parsed_message_id=parsed_id,
                    symbol=instrument,
                    direction=direction_val,
                    entry_min=entry_min,
                    entry_max=entry_max,
                    stop_loss=stop_loss,
                    tp1=tp1,
                    tp2=tp2,
                    has_tp_open=has_tp_open,
                    created_at=now_utc
                )
                uow.db.add(signal_rec)

            uow.audit.log_event("MESSAGE_PARSED", {
                "message_id": message_id,
                "category": category_val,
                "is_executable": parse_result.isExecutable
            })

            return parse_dict, False
