"""MT5 Adapter and Demo Execution Worker Package."""

from src.mt5.constants import MT5_ADAPTER_VERSION, EXECUTION_WORKER_VERSION
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.dry_run_adapter import DryRunMT5Adapter
from src.mt5.real_adapter import RealMT5Adapter
from src.mt5.execution_service import MT5ExecutionService
from src.mt5.execution_worker import MT5ExecutionWorker
from src.mt5.order_service import MT5OrderService
from src.mt5.position_service import MT5PositionService

__all__ = [
    "MT5_ADAPTER_VERSION",
    "EXECUTION_WORKER_VERSION",
    "MT5AdapterInterface",
    "FakeMT5Adapter",
    "DryRunMT5Adapter",
    "RealMT5Adapter",
    "MT5ExecutionService",
    "MT5ExecutionWorker",
    "MT5OrderService",
    "MT5PositionService"
]
