"""Abstract Base Interface for MT5 Adapter."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
from src.mt5.contracts import (
    Mt5TerminalInfoDTO, Mt5AccountInfoDTO, Mt5SymbolResolutionDTO,
    Mt5SymbolSpecificationDTO, Mt5OrderCheckRequestDTO, Mt5OrderCheckResultDTO,
    Mt5OrderSendRequestDTO, Mt5OrderSendResultDTO, Mt5OrderSnapshotDTO,
    Mt5PositionSnapshotDTO, Mt5StatusDTO, Mt5TickDTO, Mt5HistoryOrderDTO,
    Mt5MutationResultDTO
)

class MT5AdapterInterface(ABC):
    @property
    @abstractmethod
    def mode(self) -> str:
        """Returns adapter mode ('fake', 'dry_run', 'real')."""
        pass

    @property
    @abstractmethod
    def health_state(self) -> str:
        """Returns current health state."""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initializes MT5 terminal connection and verifies demo safety gates."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shuts down MT5 connection safely."""
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """Returns True if adapter is initialized and ready."""
        pass

    @abstractmethod
    def terminal_info(self) -> Mt5TerminalInfoDTO:
        """Returns terminal information."""
        pass

    @abstractmethod
    def account_info(self) -> Mt5AccountInfoDTO:
        """Returns account information."""
        pass

    @abstractmethod
    def list_symbols(self) -> List[str]:
        """Lists available symbol names on broker."""
        pass

    @abstractmethod
    def resolve_symbol(self, canonical: str = "XAUUSD") -> Mt5SymbolResolutionDTO:
        """Resolves broker symbol for canonical symbol."""
        pass

    @abstractmethod
    def symbol_specification(self, symbol: str = "XAUUSD") -> Mt5SymbolSpecificationDTO:
        """Retrieves symbol specification."""
        pass

    @abstractmethod
    def order_check(self, req: Mt5OrderCheckRequestDTO) -> Mt5OrderCheckResultDTO:
        """Runs pre-send order check."""
        pass

    @abstractmethod
    def order_send(self, req: Mt5OrderSendRequestDTO) -> Mt5OrderSendResultDTO:
        """Sends order request to MT5."""
        pass

    @abstractmethod
    def orders_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5OrderSnapshotDTO]:
        """Retrieves active pending orders."""
        pass

    @abstractmethod
    def positions_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5PositionSnapshotDTO]:
        """Retrieves active positions."""
        pass

    @abstractmethod
    def get_status(self) -> Mt5StatusDTO:
        """Returns aggregated status summary."""
        pass

    # -- Mutations ----------------------------------------------------------
    # These are declared abstract on purpose. An adapter that cannot perform a
    # mutation must fail loudly; silently skipping it would let the service
    # layer report success for an operation the broker never saw.

    @abstractmethod
    def modify_order(
        self,
        ticket: int,
        price: Optional[Decimal] = None,
        sl: Optional[Decimal] = None,
        tp: Optional[Decimal] = None
    ) -> Mt5MutationResultDTO:
        """Modifies a pending order's price and/or stop levels."""
        pass

    @abstractmethod
    def delete_order(self, ticket: int) -> Mt5MutationResultDTO:
        """Deletes a pending order."""
        pass

    @abstractmethod
    def modify_position(
        self,
        ticket: int,
        sl: Decimal,
        tp: Optional[Decimal] = None
    ) -> Mt5MutationResultDTO:
        """Updates an open position's stop loss and take profit."""
        pass

    @abstractmethod
    def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        """Closes an open position, fully or partially."""
        pass

    # -- Market data & history ---------------------------------------------

    @abstractmethod
    def symbol_tick(self, symbol: str = "XAUUSD") -> Optional[Mt5TickDTO]:
        """Latest bid/ask, or None when the terminal has no quote available."""
        pass

    @abstractmethod
    def history_orders_get(self, magic_number: Optional[int] = None, limit: int = 100) -> List[Mt5HistoryOrderDTO]:
        """Historical (closed or cancelled) orders."""
        pass
