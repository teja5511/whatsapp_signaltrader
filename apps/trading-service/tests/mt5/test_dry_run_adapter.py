import pytest
from decimal import Decimal
from src.mt5.dry_run_adapter import DryRunMT5Adapter
from src.mt5.constants import MODE_DRY_RUN, HEALTH_READY
from src.mt5.contracts import Mt5OrderSendRequestDTO

def test_dry_run_adapter_never_submits_trades():
    adapter = DryRunMT5Adapter()
    assert adapter.mode == MODE_DRY_RUN
    assert adapter.initialize() is True
    assert adapter.is_initialized() is True

    req = Mt5OrderSendRequestDTO(
        symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
        price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=999, comment="dry-run", idempotency_key="k-dry"
    )
    res = adapter.order_send(req)

    assert res.dry_run is True
    assert res.execution_performed is False
    assert res.is_success is True
    assert res.order_ticket is None
    assert res.deal_ticket is None
    assert "No order submitted" in res.comment

    assert len(adapter.orders_get()) == 0
    assert len(adapter.positions_get()) == 0
