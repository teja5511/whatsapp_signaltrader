"""Dry Run MT5 Adapter."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from src.mt5.constants import (
    MODE_DRY_RUN, HEALTH_NOT_INITIALIZED, HEALTH_READY, CANONICAL_SYMBOL_XAUUSD
)
from src.mt5.contracts import (
    Mt5TerminalInfoDTO, Mt5AccountInfoDTO, Mt5SymbolResolutionDTO,
    Mt5SymbolSpecificationDTO, Mt5OrderCheckRequestDTO, Mt5OrderCheckResultDTO,
    Mt5OrderSendRequestDTO, Mt5OrderSendResultDTO, Mt5OrderSnapshotDTO,
    Mt5PositionSnapshotDTO, Mt5StatusDTO, Mt5TickDTO, Mt5HistoryOrderDTO,
    Mt5MutationResultDTO
)
from src.mt5.adapter import MT5AdapterInterface

#: Dry run reports a plausible quote so planning policies can be exercised end
#: to end without ever touching a terminal.
DRY_RUN_MID_PRICE = Decimal("3980.00")

class DryRunMT5Adapter(MT5AdapterInterface):
    def __init__(self):
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED

    @property
    def mode(self) -> str:
        return MODE_DRY_RUN

    @property
    def health_state(self) -> str:
        return self._health_state

    def initialize(self) -> bool:
        self._initialized = True
        self._health_state = HEALTH_READY
        return True

    def shutdown(self) -> None:
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED

    def is_initialized(self) -> bool:
        return self._initialized and self._health_state == HEALTH_READY

    def terminal_info(self) -> Mt5TerminalInfoDTO:
        return Mt5TerminalInfoDTO(connected=self._initialized)

    def account_info(self) -> Mt5AccountInfoDTO:
        return Mt5AccountInfoDTO()

    def list_symbols(self) -> List[str]:
        return [CANONICAL_SYMBOL_XAUUSD]

    def resolve_symbol(self, canonical: str = "XAUUSD") -> Mt5SymbolResolutionDTO:
        return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol=canonical, is_resolved=True, source="DRY_RUN")

    def symbol_specification(self, symbol: str = "XAUUSD") -> Mt5SymbolSpecificationDTO:
        return Mt5SymbolSpecificationDTO(symbol=symbol, source="DRY_RUN")

    def order_check(self, req: Mt5OrderCheckRequestDTO) -> Mt5OrderCheckResultDTO:
        return Mt5OrderCheckResultDTO(retcode=0, retcode_name="TRADE_RETCODE_DONE", is_valid=True, comment="Dry-run check OK")

    def order_send(self, req: Mt5OrderSendRequestDTO) -> Mt5OrderSendResultDTO:
        # Dry Run NEVER calls order_send or generates real tickets
        return Mt5OrderSendResultDTO(
            retcode=0,
            retcode_name="DRY_RUN_PASSED",
            deal_ticket=None,
            order_ticket=None,
            volume=req.volume,
            price=req.price,
            comment="Dry run preflight passed cleanly. No order submitted.",
            is_success=True,
            dry_run=True,
            execution_performed=False
        )

    def orders_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5OrderSnapshotDTO]:
        return []

    def positions_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5PositionSnapshotDTO]:
        return []

    def _refused(self, ticket: int, operation: str) -> Mt5MutationResultDTO:
        return Mt5MutationResultDTO(
            ticket=ticket,
            operation=operation,
            retcode=0,
            retcode_name="DRY_RUN_REFUSED",
            is_success=False,
            comment="Dry-run adapter never mutates broker state.",
        )

    def modify_order(self, ticket: int, price: Optional[Decimal] = None, sl: Optional[Decimal] = None, tp: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        return self._refused(ticket, "MODIFY_ORDER")

    def delete_order(self, ticket: int) -> Mt5MutationResultDTO:
        return self._refused(ticket, "DELETE_ORDER")

    def modify_position(self, ticket: int, sl: Decimal, tp: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        return self._refused(ticket, "MODIFY_POSITION")

    def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        return self._refused(ticket, "CLOSE_POSITION")

    def symbol_tick(self, symbol: str = CANONICAL_SYMBOL_XAUUSD) -> Optional[Mt5TickDTO]:
        return Mt5TickDTO(
            symbol=symbol,
            bid=DRY_RUN_MID_PRICE - Decimal("0.10"),
            ask=DRY_RUN_MID_PRICE + Decimal("0.10"),
        )

    def history_orders_get(self, magic_number: Optional[int] = None, limit: int = 100) -> List[Mt5HistoryOrderDTO]:
        return []

    def get_status(self) -> Mt5StatusDTO:
        return Mt5StatusDTO(
            adapter_mode=MODE_DRY_RUN,
            health_state=self._health_state,
            execution_enabled=False,
            demo_only=True,
            live_execution_enabled=False,
            trading_enabled=False,
            account_connected=self._initialized,
            resolved_symbol=CANONICAL_SYMBOL_XAUUSD
        )
