"""Position SL/TP Modification, Closing, and Campaign Close Service."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, MT5PositionRecordModel
from src.mt5.adapter import MT5AdapterInterface

class MT5PositionService:
    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal):
        self.adapter = adapter
        self.session_factory = session_factory

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

            if hasattr(self.adapter, "modify_position"):
                ok = self.adapter.modify_position(position_ticket, sl=stop_loss, tp=take_profit)
                if not ok:
                    raise ValueError(f"Failed to modify position {position_ticket} in MT5 adapter.")

            pos_rec.stop_loss = float(stop_loss)
            if take_profit is not None:
                pos_rec.take_profit = float(take_profit)
            pos_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("POSITION_SLTP_MODIFIED", {
                "ticket": position_ticket,
                "stop_loss": float(stop_loss),
                "take_profit": float(take_profit) if take_profit else None
            })

            return {"status": "success", "ticket": position_ticket}

    def close_position(self, position_ticket: int, volume: Optional[Decimal] = None) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            pos_rec = uow.db.query(MT5PositionRecordModel).filter(MT5PositionRecordModel.ticket == position_ticket).first()
            if not pos_rec:
                raise ValueError(f"Position ticket {position_ticket} not found in database registry.")

            if hasattr(self.adapter, "close_position"):
                self.adapter.close_position(position_ticket)

            pos_rec.state = "CLOSED"
            pos_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("POSITION_CLOSED", {"ticket": position_ticket})
            return {"status": "success", "ticket": position_ticket}

    def close_campaign_positions(self, campaign_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            positions = self.adapter.positions_get(magic_number=campaign.magic_number)
            closed_tickets = []
            for p in positions:
                if hasattr(self.adapter, "close_position"):
                    self.adapter.close_position(p.ticket)
                    closed_tickets.append(p.ticket)

            uow.audit.log_event("CAMPAIGN_POSITIONS_CLOSED", {
                "campaign_id": campaign_id,
                "closed_count": len(closed_tickets),
                "tickets": closed_tickets
            })

            return {
                "status": "success",
                "campaign_id": campaign_id,
                "closed_count": len(closed_tickets),
                "tickets": closed_tickets
            }
