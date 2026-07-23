"""Abstract Base Interface for MT5 Adapter."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.mt5.contracts import (
    Mt5TerminalInfoDTO, Mt5AccountInfoDTO, Mt5SymbolResolutionDTO,
    Mt5SymbolSpecificationDTO, Mt5OrderCheckRequestDTO, Mt5OrderCheckResultDTO,
    Mt5OrderSendRequestDTO, Mt5OrderSendResultDTO, Mt5OrderSnapshotDTO,
    Mt5PositionSnapshotDTO, Mt5StatusDTO
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
