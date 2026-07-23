import time
import pytest
from decimal import Decimal
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.contracts import Mt5OrderCheckRequestDTO, Mt5OrderSendRequestDTO
from src.mt5.idempotency import generate_execution_idempotency_key

def test_request_builder_benchmark():
    start = time.perf_counter()
    iterations = 100_000
    for i in range(iterations):
        req = Mt5OrderCheckRequestDTO(
            symbol="XAUUSD",
            volume=Decimal("0.30"),
            order_type="SELL_LIMIT",
            price=Decimal("3990.00"),
            stop_loss=Decimal("4008.00"),
            take_profit=Decimal("3960.00"),
            magic_number=1000 + i,
            comment=f"BENCH-{i}"
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    per_op = elapsed_ms / iterations
    print(f"\n[Request Builder Benchmark] {iterations:,} Runs -> Total: {elapsed_ms:.2f} ms, Per Op: {per_op:.6f} ms")
    assert elapsed_ms < 5000  # Must be fast

def test_idempotency_key_benchmark():
    start = time.perf_counter()
    iterations = 10_000
    for i in range(iterations):
        k = generate_execution_idempotency_key(
            campaign_id="c-bench-123",
            planning_fingerprint="fp-123",
            planned_entry_id=f"e-{i}",
            campaign_version=1,
            account_login=123456,
            account_server="Exness-Server",
            broker_symbol="XAUUSD"
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    per_op = elapsed_ms / iterations
    print(f"[Idempotency Benchmark] {iterations:,} Runs -> Total: {elapsed_ms:.2f} ms, Per Op: {per_op:.6f} ms")
    assert elapsed_ms < 2000

def test_fake_execution_batches_benchmark():
    adapter = FakeMT5Adapter()
    adapter.initialize()
    start = time.perf_counter()
    batches = 1_000
    for b in range(batches):
        for e in range(5):
            send_req = Mt5OrderSendRequestDTO(
                symbol="XAUUSD", volume=Decimal("0.30"), order_type="SELL_LIMIT",
                price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), magic_number=b, comment="bench", idempotency_key=f"k-{b}-{e}"
            )
            adapter.order_send(send_req)
    elapsed_ms = (time.perf_counter() - start) * 1000
    per_batch = elapsed_ms / batches
    print(f"[Fake Execution Batch Benchmark] {batches:,} 5-Entry Batches -> Total: {elapsed_ms:.2f} ms, Per Batch: {per_batch:.6f} ms")
    assert elapsed_ms < 3000
