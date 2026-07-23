import pytest
from decimal import Decimal
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.constants import (
    HEALTH_READY, HEALTH_BLOCKED_LIVE_ACCOUNT, HEALTH_BLOCKED_NON_HEDGING,
    HEALTH_TRADING_NOT_ALLOWED, HEALTH_BLOCKED_SYMBOL_NOT_FOUND, HEALTH_BLOCKED_SYMBOL_AMBIGUOUS,
    ENV_DEMO, ENV_REAL, MARGIN_HEDGING, MARGIN_NETTING
)
from src.mt5.contracts import Mt5OrderCheckRequestDTO, Mt5OrderSendRequestDTO

def test_fake_adapter_healthy_scenario():
    adapter = FakeMT5Adapter(scenario="healthy_demo_hedging")
    assert adapter.initialize() is True
    assert adapter.is_initialized() is True
    assert adapter.health_state == HEALTH_READY

    acc = adapter.account_info()
    assert acc.environment_kind == ENV_DEMO
    assert acc.margin_mode == MARGIN_HEDGING

    spec = adapter.symbol_specification("XAUUSD")
    assert spec.symbol == "XAUUSD"

    check_req = Mt5OrderCheckRequestDTO(
        symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
        price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=123, comment="test"
    )
    check_res = adapter.order_check(check_req)
    assert check_res.is_valid is True

    send_req = Mt5OrderSendRequestDTO(
        symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
        price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=123, comment="test", idempotency_key="key-1"
    )
    send_res = adapter.order_send(send_req)
    assert send_res.is_success is True
    assert send_res.order_ticket is not None

def test_fake_adapter_live_account_blocked():
    adapter = FakeMT5Adapter(scenario="live_account")
    assert adapter.initialize() is False
    assert adapter.health_state == HEALTH_BLOCKED_LIVE_ACCOUNT
    assert adapter.is_initialized() is False

def test_fake_adapter_netting_account_blocked():
    adapter = FakeMT5Adapter(scenario="netting_account")
    assert adapter.initialize() is False
    assert adapter.health_state == HEALTH_BLOCKED_NON_HEDGING

def test_fake_adapter_trade_disabled_blocked():
    adapter = FakeMT5Adapter(scenario="trade_disabled")
    assert adapter.initialize() is False
    assert adapter.health_state == HEALTH_TRADING_NOT_ALLOWED

def test_fake_adapter_symbol_missing_blocked():
    adapter = FakeMT5Adapter(scenario="symbol_missing")
    assert adapter.initialize() is False
    assert adapter.health_state == HEALTH_BLOCKED_SYMBOL_NOT_FOUND

def test_fake_adapter_symbol_ambiguous_blocked():
    adapter = FakeMT5Adapter(scenario="symbol_ambiguous")
    assert adapter.initialize() is False
    assert adapter.health_state == HEALTH_BLOCKED_SYMBOL_AMBIGUOUS

def test_fake_adapter_order_check_failure():
    adapter = FakeMT5Adapter(scenario="order_check_failure")
    adapter.initialize()
    check_req = Mt5OrderCheckRequestDTO(
        symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
        price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=123, comment="test"
    )
    check_res = adapter.order_check(check_req)
    assert check_res.is_valid is False

def test_fake_adapter_first_send_failure():
    adapter = FakeMT5Adapter(scenario="first_send_failure")
    adapter.initialize()
    send_req = Mt5OrderSendRequestDTO(
        symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
        price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=123, comment="test", idempotency_key="k1"
    )
    send_res = adapter.order_send(send_req)
    assert send_res.is_success is False
