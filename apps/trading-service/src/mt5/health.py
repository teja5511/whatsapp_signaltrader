"""MT5 Health & Status Monitoring."""

from typing import Dict, Any
from src.mt5.adapter import MT5AdapterInterface

class MT5HealthMonitor:
    def __init__(self, adapter: MT5AdapterInterface):
        self.adapter = adapter

    def check_health(self) -> Dict[str, Any]:
        status = self.adapter.get_status()
        return {
            "adapter_mode": status.adapter_mode,
            "health_state": status.health_state,
            "execution_enabled": status.execution_enabled,
            "demo_only": status.demo_only,
            "live_execution_enabled": status.live_execution_enabled,
            "trading_enabled": status.trading_enabled,
            "account_connected": status.account_connected,
            "account_environment": status.account_environment,
            "margin_mode": status.margin_mode,
            "resolved_symbol": status.resolved_symbol
        }
