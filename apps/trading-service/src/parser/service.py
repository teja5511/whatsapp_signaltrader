import hashlib
import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from src.database.unit_of_work import UnitOfWork
from src.database.engine import SessionLocal
from src.database.models import WhatsAppMessageModel, ParsedMessageModel, SignalModel
from src.parser.classification import parse_raw_text
from src.parser.result import ParserResult

class MessageParsingService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

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
            result_dict = parse_result.to_dict()

            # 3. Store Parsed Message
            parsed_uuid = str(uuid4())
            parsed_rec = ParsedMessageModel(
                id=parsed_uuid,
                raw_message_id=message_id,
                message_type=parse_result.category,
                parsed_json=json.dumps(result_dict),
                parsed_at=now_utc
            )
            uow.db.add(parsed_rec)
            uow.db.flush()

            # 4. Store Signal Record if NEW_SIGNAL
            if parse_result.category == "NEW_SIGNAL" and parse_result.signal:
                sig_data = parse_result.signal
                sig_uuid = str(uuid4())
                sig_rec = SignalModel(
                    id=sig_uuid,
                    parsed_message_id=parsed_uuid,
                    symbol=sig_data["instrument"],
                    direction=sig_data["direction"],
                    entry_min=float(sig_data["zoneLow"]),
                    entry_max=float(sig_data["zoneHigh"]),
                    stop_loss=float(sig_data["stopLoss"]) if sig_data["stopLoss"] else 0.0,
                    tp1=float(sig_data["tp1"]) if sig_data["tp1"] else None,
                    tp2=float(sig_data["tp2"]) if sig_data["tp2"] else None,
                    has_tp_open=sig_data["tpOpenPresent"],
                    created_at=now_utc
                )
                uow.db.add(sig_rec)

            # 5. Record Audit Event
            uow.audit.log_event("MESSAGE_PARSED", {
                "message_id": message_id,
                "category": parse_result.category,
                "issues_count": len(parse_result.validationIssues)
            })

            return result_dict, False
