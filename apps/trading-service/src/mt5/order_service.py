"""Order Modification, Deletion, and Campaign Cancellation Service."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, MT5OrderRecordModel
from src.database.types import coerce_decimal
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.contracts import Mt5MutationResultDTO
from src.mt5.errors import BrokerOutcomeUnknownError, BrokerMutationFailedError


class MT5OrderService:
    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal):
        self.adapter = adapter
        self.session_factory = session_factory

    @staticmethod
    def _raise_for_result(result: Mt5MutationResultDTO) -> None:
        """Never let an unconfirmed broker call be recorded as a success."""
        if result.outcome_unknown:
            raise BrokerOutcomeUnknownError(result.ticket, result.operation, result.comment)
        if not result.is_success:
            raise BrokerMutationFailedError(result.ticket, result.operation, result.retcode, result.comment)

    def modify_order(
        self,
        order_ticket: int,
        price: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            order_rec = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.ticket == order_ticket).first()
            if not order_rec:
                raise ValueError(f"Order ticket {order_ticket} not found in database registry.")

            result = self.adapter.modify_order(order_ticket, price=price, sl=stop_loss, tp=take_profit)
            self._raise_for_result(result)

            if price is not None:
                order_rec.price = coerce_decimal(price)
            if stop_loss is not None:
                order_rec.stop_loss = coerce_decimal(stop_loss)
            if take_profit is not None:
                order_rec.take_profit = coerce_decimal(take_profit)
            order_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("ORDER_MODIFIED", {
                "ticket": order_ticket,
                "price": str(price) if price is not None else None,
                "stop_loss": str(stop_loss) if stop_loss is not None else None,
                "take_profit": str(take_profit) if take_profit is not None else None,
                "retcode": result.retcode,
            })

            return {"status": "success", "ticket": order_ticket, "retcode": result.retcode}

    def delete_order(self, order_ticket: int) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            order_rec = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.ticket == order_ticket).first()
            if not order_rec:
                raise ValueError(f"Order ticket {order_ticket} not found in database registry.")

            result = self.adapter.delete_order(order_ticket)
            self._raise_for_result(result)

            order_rec.state = "CANCELLED"
            order_rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("ORDER_DELETED", {"ticket": order_ticket, "retcode": result.retcode})
            return {"status": "success", "ticket": order_ticket, "retcode": result.retcode}

    def cancel_campaign_pending_orders(self, campaign_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            orders = self.adapter.orders_get(magic_number=campaign.magic_number)
            cancelled: List[int] = []
            failed: List[Dict[str, Any]] = []
            unknown: List[Dict[str, Any]] = []

            for o in orders:
                result = self.adapter.delete_order(o.ticket)
                if result.outcome_unknown:
                    # Leave the local record alone; reconciliation decides.
                    unknown.append({"ticket": o.ticket, "comment": result.comment})
                    continue
                if not result.is_success:
                    failed.append({"ticket": o.ticket, "retcode": result.retcode, "comment": result.comment})
                    continue
                cancelled.append(o.ticket)
                rec = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.ticket == o.ticket).first()
                if rec:
                    rec.state = "CANCELLED"
                    rec.updated_at = datetime.now(timezone.utc)

            uow.audit.log_event("CAMPAIGN_PENDING_ORDERS_CANCELLED", {
                "campaign_id": campaign_id,
                "cancelled_count": len(cancelled),
                "failed_count": len(failed),
                "unknown_count": len(unknown),
                "tickets": cancelled,
            })

            return {
                "status": "success" if not failed and not unknown else "partial",
                "campaign_id": campaign_id,
                "cancelled_count": len(cancelled),
                "tickets": cancelled,
                "failed": failed,
                "outcome_unknown": unknown,
            }
