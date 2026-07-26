"""Position SL/TP Modification, Closing, and Campaign Close Service."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, MT5PositionRecordModel
from src.database.types import coerce_decimal
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.contracts import Mt5MutationResultDTO
from src.mt5.errors import BrokerOutcomeUnknownError, BrokerMutationFailedError


class MT5PositionService:
    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal):
        self.adapter = adapter
        self.session_factory = session_factory

    @staticmethod
    def _raise_for_result(result: Mt5MutationResultDTO) -> None:
        if result.outcome_unknown:
            raise BrokerOutcomeUnknownError(result.ticket, result.operation, result.comment)
        if not result.is_success:
            raise BrokerMutationFailedError(result.ticket, result.operation, result.retcode, result.comment)

    def modify_position_sltp(
        self,
        position_ticket: int,
        stop_loss: Decimal,
        take_profit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            pos_rec = uow.db.query(MT5PositionRecordModel).filter(MT5PositionRecordModel.ticket == position_ticket).first()
            if not pos_rec:
                raise ValueError(f"Position ticket {position_ticket} not found in database registry.")

            result = self.adapter.modify_position(position_ticket, sl=stop_loss, tp=take_profit)
            self._raise_for_result(result)

            pos_rec.stop_loss = coerce_decimal(stop_loss)
            if take_profit is not None:
                pos_rec.take_profit = coerce_decimal(take_profit)
            pos_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("POSITION_SLTP_MODIFIED", {
                "ticket": position_ticket,
                "stop_loss": str(stop_loss),
                "take_profit": str(take_profit) if take_profit is not None else None,
                "retcode": result.retcode,
            })

            return {"status": "success", "ticket": position_ticket, "retcode": result.retcode}

    def close_position(self, position_ticket: int, volume: Optional[Decimal] = None) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            pos_rec = uow.db.query(MT5PositionRecordModel).filter(MT5PositionRecordModel.ticket == position_ticket).first()
            if not pos_rec:
                raise ValueError(f"Position ticket {position_ticket} not found in database registry.")

            result = self.adapter.close_position(position_ticket, volume=volume)
            self._raise_for_result(result)

            closed = result.closed_volume
            if closed is not None and closed < coerce_decimal(pos_rec.volume):
                pos_rec.volume = coerce_decimal(pos_rec.volume) - closed
                pos_rec.state = "OPEN"
            else:
                pos_rec.state = "CLOSED"
            pos_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("POSITION_CLOSED", {
                "ticket": position_ticket,
                "closed_volume": str(closed) if closed is not None else None,
                "retcode": result.retcode,
            })
            return {
                "status": "success",
                "ticket": position_ticket,
                "closed_volume": str(closed) if closed is not None else None,
                "remaining_volume": str(pos_rec.volume),
            }

    def close_campaign_positions(self, campaign_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            positions = self.adapter.positions_get(magic_number=campaign.magic_number)
            closed: List[int] = []
            failed: List[Dict[str, Any]] = []
            unknown: List[Dict[str, Any]] = []

            for p in positions:
                result = self.adapter.close_position(p.ticket)
                if result.outcome_unknown:
                    unknown.append({"ticket": p.ticket, "comment": result.comment})
                    continue
                if not result.is_success:
                    failed.append({"ticket": p.ticket, "retcode": result.retcode, "comment": result.comment})
                    continue
                closed.append(p.ticket)
                rec = uow.db.query(MT5PositionRecordModel).filter(MT5PositionRecordModel.ticket == p.ticket).first()
                if rec:
                    rec.state = "CLOSED"
                    rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("CAMPAIGN_POSITIONS_CLOSED", {
                "campaign_id": campaign_id,
                "closed_count": len(closed),
                "failed_count": len(failed),
                "unknown_count": len(unknown),
                "tickets": closed,
            })

            return {
                "status": "success" if not failed and not unknown else "partial",
                "campaign_id": campaign_id,
                "closed_count": len(closed),
                "tickets": closed,
                "failed": failed,
                "outcome_unknown": unknown,
            }
