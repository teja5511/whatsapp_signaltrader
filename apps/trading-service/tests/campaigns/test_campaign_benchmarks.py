import time
import statistics
import pytest
from src.database.engine import engine, Base, SessionLocal
from src.campaigns.duplicate_service import DuplicateProtectionService

def test_semantic_fingerprint_benchmark_10000_runs():
    durations_ms = []

    for i in range(10000):
        start = time.perf_counter()
        DuplicateProtectionService.generate_semantic_fingerprint(
            instrument="XAUUSD", direction="SELL", order_intent="UNSPECIFIED",
            zone_low=f"{4120 + (i % 100):.2f}", zone_high=f"{4128 + (i % 100):.2f}",
            stop_loss="4136.00", tp1="4112.00", tp2="4104.00", tp_open_present=True,
            group_id="group-1", sender_id="admin-1"
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        durations_ms.append(elapsed_ms)

    median_ms = statistics.median(durations_ms)
    sorted_durations = sorted(durations_ms)
    p95_ms = sorted_durations[int(0.95 * len(durations_ms))]

    print(f"\n[Semantic Fingerprint Benchmark] 10,000 Runs -> Median: {median_ms:.4f} ms, p95: {p95_ms:.4f} ms")
    assert len(durations_ms) == 10000
    assert median_ms < 1.0
