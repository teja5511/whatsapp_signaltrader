"""In-memory Fake MT5 Adapter for testing and development."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from src.mt5.constants import (
    MODE_FAKE, HEALTH_NOT_INITIALIZED, HEALTH_READY, HEALTH_BLOCKED_LIVE_ACCOUNT,
    HEALTH_BLOCKED_NON_HEDGING, HEALTH_BLOCKED_SYMBOL_NOT_FOUND, HEALTH_BLOCKED_SYMBOL_AMBIGUOUS,
    HEALTH_TRADING_NOT_ALLOWED, ENV_DEMO, ENV_REAL, ENV_CONTEST, MARGIN_HEDGING, MARGIN_NETTING,
    CANONICAL_SYMBOL_XAUUSD
)
from src.mt5.contracts import (
    Mt5TerminalInfoDTO, Mt5AccountInfoDTO, Mt5SymbolResolutionDTO,
    Mt5SymbolSpecificationDTO, Mt5OrderCheckRequestDTO, Mt5OrderCheckResultDTO,
    Mt5OrderSendRequestDTO, Mt5OrderSendResultDTO, Mt5OrderSnapshotDTO,
    Mt5PositionSnapshotDTO, Mt5StatusDTO, Mt5TickDTO, Mt5HistoryOrderDTO,
    Mt5MutationResultDTO
)
from src.mt5.adapter import MT5AdapterInterface

#: Sits below the fixture SELL zone (3990-3998), i.e. BEFORE_ZONE for a sell
#: limit grid. Tests that need a different classification call ``set_price``.
DEFAULT_FAKE_MID_PRICE = Decimal("3980.00")

class FakeMT5Adapter(MT5AdapterInterface):
    def __init__(self, scenario: str = "healthy_demo_hedging", mid_price: Decimal = DEFAULT_FAKE_MID_PRICE):
        self.scenario = scenario
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED
        self._orders: Dict[int, Mt5OrderSnapshotDTO] = {}
        self._positions: Dict[int, Mt5PositionSnapshotDTO] = {}
        self._history: List[Mt5HistoryOrderDTO] = []
        self._ticket_counter = 5000000
        self._send_counter = 0
        self.current_bid = mid_price - Decimal("0.10")
        self.current_ask = mid_price + Decimal("0.10")

    @property
    def mode(self) -> str:
        return MODE_FAKE

    @property
    def health_state(self) -> str:
        return self._health_state

    def initialize(self) -> bool:
        if self.scenario == "live_account":
            self._health_state = HEALTH_BLOCKED_LIVE_ACCOUNT
            self._initialized = False
            return False
        if self.scenario == "netting_account":
            self._health_state = HEALTH_BLOCKED_NON_HEDGING
            self._initialized = False
            return False
        if self.scenario == "trade_disabled":
            self._health_state = HEALTH_TRADING_NOT_ALLOWED
            self._initialized = False
            return False
        if self.scenario == "symbol_missing":
            self._health_state = HEALTH_BLOCKED_SYMBOL_NOT_FOUND
            self._initialized = False
            return False
        if self.scenario == "symbol_ambiguous":
            self._health_state = HEALTH_BLOCKED_SYMBOL_AMBIGUOUS
            self._initialized = False
            return False

        self._initialized = True
        self._health_state = HEALTH_READY
        return True

    def shutdown(self) -> None:
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED

    def is_initialized(self) -> bool:
        return self._initialized and self._health_state == HEALTH_READY

    def terminal_info(self) -> Mt5TerminalInfoDTO:
        return Mt5TerminalInfoDTO(
            connected=self._initialized,
            trade_allowed=self.scenario != "trade_disabled"
        )

    def account_info(self) -> Mt5AccountInfoDTO:
        env_kind = ENV_DEMO
        margin_mode = MARGIN_HEDGING
        trade_allowed = True

        if self.scenario == "live_account":
            env_kind = ENV_REAL
        elif self.scenario == "contest_account":
            env_kind = ENV_CONTEST
        elif self.scenario == "netting_account":
            margin_mode = MARGIN_NETTING
        elif self.scenario == "trade_disabled":
            trade_allowed = False

        return Mt5AccountInfoDTO(
            environment_kind=env_kind,
            margin_mode=margin_mode,
            trade_allowed=trade_allowed
        )

    def list_symbols(self) -> List[str]:
        if self.scenario == "symbol_missing":
            return ["EURUSD", "GBPUSD"]
        if self.scenario == "symbol_ambiguous":
            return ["XAUUSD", "XAUUSDm", "GOLD"]
        return [CANONICAL_SYMBOL_XAUUSD, "EURUSD", "GBPUSD"]

    def resolve_symbol(self, canonical: str = "XAUUSD") -> Mt5SymbolResolutionDTO:
        if self.scenario == "symbol_missing":
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol="", is_resolved=False, source="NOT_FOUND")
        if self.scenario == "symbol_ambiguous":
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol="", is_resolved=False, source="AMBIGUOUS")
        return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol=canonical, is_resolved=True, source="EXACT_MATCH")

    def symbol_specification(self, symbol: str = "XAUUSD") -> Mt5SymbolSpecificationDTO:
        if self.scenario == "symbol_spec_changed":
            return Mt5SymbolSpecificationDTO(
                symbol=symbol,
                tick_size=Decimal("0.05"),  # Changed tick size
                volume_min=Decimal("0.10")
            )
        return Mt5SymbolSpecificationDTO(symbol=symbol)

    def order_check(self, req: Mt5OrderCheckRequestDTO) -> Mt5OrderCheckResultDTO:
        if self.scenario == "order_check_failure":
            return Mt5OrderCheckResultDTO(retcode=10013, retcode_name="TRADE_RETCODE_INVALID", is_valid=False, comment="Invalid money check in fake scenario")
        return Mt5OrderCheckResultDTO(retcode=0, retcode_name="TRADE_RETCODE_DONE", is_valid=True, comment="Fake check OK")

    def order_send(self, req: Mt5OrderSendRequestDTO) -> Mt5OrderSendResultDTO:
        if not self.is_initialized():
            return Mt5OrderSendResultDTO(retcode=10014, retcode_name="TRADE_RETCODE_TRADE_DISABLED", is_success=False, comment="Adapter not initialized")

        self._send_counter += 1

        if self.scenario == "first_send_failure" and self._send_counter == 1:
            return Mt5OrderSendResultDTO(retcode=10006, retcode_name="TRADE_RETCODE_REJECT", is_success=False, comment="First send rejected in fake scenario")

        if self.scenario == "middle_send_failure" and self._send_counter == 3:
            return Mt5OrderSendResultDTO(retcode=10006, retcode_name="TRADE_RETCODE_REJECT", is_success=False, comment="Middle send rejected in fake scenario")

        ticket = self._ticket_counter
        self._ticket_counter += 1

        order = Mt5OrderSnapshotDTO(
            ticket=ticket,
            magic_number=req.magic_number,
            symbol=req.symbol,
            order_type=req.order_type,
            volume=req.volume,
            price=req.price,
            stop_loss=req.stop_loss,
            take_profit=req.take_profit,
            comment=req.comment,
            state="PLACED"
        )
        self._orders[ticket] = order

        if self.scenario == "immediate_first_fill" and self._send_counter == 1:
            # Convert first order immediately into a position
            pos_ticket = ticket + 90000
            position = Mt5PositionSnapshotDTO(
                ticket=pos_ticket,
                magic_number=req.magic_number,
                symbol=req.symbol,
                position_type="SELL" if "SELL" in req.order_type else "BUY",
                volume=req.volume,
                price_open=req.price,
                stop_loss=req.stop_loss,
                take_profit=req.take_profit,
                comment=req.comment,
                state="OPEN"
            )
            self._positions[pos_ticket] = position
            del self._orders[ticket]
            return Mt5OrderSendResultDTO(retcode=10009, retcode_name="TRADE_RETCODE_DONE", order_ticket=ticket, deal_ticket=pos_ticket, volume=req.volume, price=req.price, is_success=True)

        return Mt5OrderSendResultDTO(retcode=10009, retcode_name="TRADE_RETCODE_DONE", order_ticket=ticket, volume=req.volume, price=req.price, is_success=True)

    def orders_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5OrderSnapshotDTO]:
        res = list(self._orders.values())
        if magic_number is not None:
            res = [o for o in res if o.magic_number == magic_number]
        if ticket is not None:
            res = [o for o in res if o.ticket == ticket]
        return res

    def positions_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5PositionSnapshotDTO]:
        res = list(self._positions.values())
        if magic_number is not None:
            res = [p for p in res if p.magic_number == magic_number]
        if ticket is not None:
            res = [p for p in res if p.ticket == ticket]
        return res

    def modify_order(self, ticket: int, price: Optional[Decimal] = None, sl: Optional[Decimal] = None, tp: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        if ticket not in self._orders:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="MODIFY_ORDER", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Unknown order ticket {ticket}."
            )
        if self.scenario == "modify_outcome_unknown":
            return Mt5MutationResultDTO(
                ticket=ticket, operation="MODIFY_ORDER", retcode=10031,
                retcode_name="TRADE_RETCODE_CONNECTION", is_success=False,
                outcome_unknown=True, comment="Connection lost before confirmation."
            )
        o = self._orders[ticket]
        if price is not None:
            o.price = price
        if sl is not None:
            o.stop_loss = sl
        if tp is not None:
            o.take_profit = tp
        return Mt5MutationResultDTO(ticket=ticket, operation="MODIFY_ORDER", comment="Fake order modified.")

    def delete_order(self, ticket: int) -> Mt5MutationResultDTO:
        if ticket not in self._orders:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="DELETE_ORDER", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Unknown order ticket {ticket}."
            )
        removed = self._orders.pop(ticket)
        self._history.append(Mt5HistoryOrderDTO(
            ticket=removed.ticket,
            magic_number=removed.magic_number,
            symbol=removed.symbol,
            order_type=removed.order_type,
            volume=removed.volume,
            price=removed.price,
            state="CANCELLED",
            comment=removed.comment,
        ))
        return Mt5MutationResultDTO(ticket=ticket, operation="DELETE_ORDER", comment="Fake order deleted.")

    def modify_position(self, ticket: int, sl: Decimal, tp: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        if ticket not in self._positions:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="MODIFY_POSITION", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Unknown position ticket {ticket}."
            )
        p = self._positions[ticket]
        p.stop_loss = sl
        p.take_profit = tp
        return Mt5MutationResultDTO(ticket=ticket, operation="MODIFY_POSITION", comment="Fake position modified.")

    def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        if ticket not in self._positions:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Unknown position ticket {ticket}."
            )
        if self.scenario == "close_outcome_unknown":
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION", retcode=10031,
                retcode_name="TRADE_RETCODE_CONNECTION", is_success=False,
                outcome_unknown=True, comment="Connection lost before confirmation."
            )
        position = self._positions[ticket]
        if volume is not None and volume < position.volume:
            position.volume = position.volume - volume
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION",
                closed_volume=volume, comment="Fake partial close."
            )
        closed_volume = position.volume
        del self._positions[ticket]
        return Mt5MutationResultDTO(
            ticket=ticket, operation="CLOSE_POSITION",
            closed_volume=closed_volume, comment="Fake position closed."
        )

    def symbol_tick(self, symbol: str = CANONICAL_SYMBOL_XAUUSD) -> Optional[Mt5TickDTO]:
        if self.scenario == "no_quote":
            return None
        return Mt5TickDTO(symbol=symbol, bid=self.current_bid, ask=self.current_ask)

    def set_price(self, mid: Decimal, spread: Decimal = Decimal("0.20")) -> None:
        """Test hook so zone-position policies can be exercised deterministically."""
        half = spread / Decimal("2")
        self.current_bid = mid - half
        self.current_ask = mid + half

    def history_orders_get(self, magic_number: Optional[int] = None, limit: int = 100) -> List[Mt5HistoryOrderDTO]:
        res = list(self._history)
        if magic_number is not None:
            res = [h for h in res if h.magic_number == magic_number]
        return res[:limit]

    def get_status(self) -> Mt5StatusDTO:
        acc = self.account_info()
        return Mt5StatusDTO(
            adapter_mode=MODE_FAKE,
            health_state=self._health_state,
            execution_enabled=True,
            demo_only=True,
            live_execution_enabled=False,
            trading_enabled=self.is_initialized(),
            account_connected=self.is_initialized(),
            account_environment=acc.environment_kind,
            margin_mode=acc.margin_mode,
            resolved_symbol=CANONICAL_SYMBOL_XAUUSD
        )
