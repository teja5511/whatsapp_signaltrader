import time
import statistics
from decimal import Decimal
from src.planning.ladder import calculate_entry_ladder
from src.planning.risk_engine import validate_campaign_risk
from src.planning.policies import get_test_fixture_policies

def test_ladder_benchmark_100k():
    runs = 100000
    durations = []

    start_total = time.perf_counter()
    for _ in range(runs):
        t0 = time.perf_counter()
        calculate_entry_ladder(3990.0, 3998.0, 5)
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)
    end_total = time.perf_counter()

    durations.sort()
    median = statistics.median(durations)
    p95 = durations[int(runs * 0.95)]
    total_ms = (end_total - start_total) * 1000.0

    print(f"\n[Ladder Benchmark] 100,000 Runs -> Median: {median:.6f} ms, p95: {p95:.6f} ms, Total: {total_ms:.2f} ms")
    assert median < 0.05

def test_risk_benchmark_10k():
    runs = 10000
    durations = []
    policies = get_test_fixture_policies()
    levels = [Decimal("3990.0"), Decimal("3992.0"), Decimal("3994.0"), Decimal("3996.0"), Decimal("3998.0")]

    start_total = time.perf_counter()
    for _ in range(runs):
        t0 = time.perf_counter()
        validate_campaign_risk(
            campaign_state="PLANNED",
            direction="SELL",
            order_intent="LIMIT",
            entry_count=5,
            stop_loss=Decimal("4008.0"),
            price_levels=levels,
            trading_enabled=False,
            policies=policies
        )
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)
    end_total = time.perf_counter()

    durations.sort()
    median = statistics.median(durations)
    p95 = durations[int(runs * 0.95)]
    total_ms = (end_total - start_total) * 1000.0

    print(f"[Risk Benchmark] 10,000 Runs -> Median: {median:.6f} ms, p95: {p95:.6f} ms, Total: {total_ms:.2f} ms")
    assert median < 0.10
