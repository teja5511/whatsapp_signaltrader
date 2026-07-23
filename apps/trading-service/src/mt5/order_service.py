"""Order Modification, Deletion, and Campaign Cancellation Service."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, MT5OrderRecordModel
from src.mt5.adapter import MT5AdapterInterface

class MT5OrderService:
    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal):
        self.adapter = adapter
        self.session_factory = session_factory

    def modify_order(
        self,
        order_ticket: int,
        price: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            # Verify Ownership
            order_rec = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.ticket == order_ticket).first()
            if not order_rec:
                raise ValueError(f"Order ticket {order_ticket} not found in database registry.")

            if hasattr(self.adapter, "modify_order"):
                ok = self.adapter.modify_order(order_ticket, price=price, sl=stop_loss, tp=take_profit)
                if not ok:
                    raise ValueError(f"Failed to modify order {order_ticket} in MT5 adapter.")

            if price is not None:
                order_rec.price = float(price)
            if stop_loss is not None:
                order_rec.stop_loss = float(stop_loss)
            if take_profit is not None:
                order_rec.take_profit = float(take_profit)
            order_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("ORDER_MODIFIED", {
                "ticket": order_ticket,
                "price": float(price) if price else None,
                "stop_loss": float(stop_loss) if stop_loss else None,
                "take_profit": float(take_profit) if take_profit else None
            })

            return {"status": "success", "ticket": order_ticket}

    def delete_order(self, order_ticket: int) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            order_rec = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.ticket == order_ticket).first()
            if not order_rec:
                raise ValueError(f"Order ticket {order_ticket} not found in database registry.")

            if hasattr(self.adapter, "delete_order"):
                self.adapter.delete_order(order_ticket)

            order_rec.state = "CANCELLED"
            order_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("ORDER_DELETED", {"ticket": order_ticket})
            return {"status": "success", "ticket": order_ticket}

    def cancel_campaign_pending_orders(self, campaign_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            orders = self.adapter.orders_get(magic_number=campaign.magic_number)
            deleted_tickets = []
            for o in orders:
                if hasattr(self.adapter, "delete_order"):
                    self.adapter.delete_order(o.ticket)
                    deleted_tickets.append(o.ticket)

            uow.audit.log_event("CAMPAIGN_PENDING_ORDERS_CANCELLED", {
                "campaign_id": campaign_id,
                "cancelled_count": len(deleted_tickets),
                "tickets": deleted_tickets
            })

            return {
                "status": "success",
                "campaign_id": campaign_id,
                "cancelled_count": len(deleted_tickets),
                "tickets": deleted_tickets
            }
