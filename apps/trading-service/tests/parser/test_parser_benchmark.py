import time
import statistics
import pytest
from src.parser.classification import parse_raw_text

FIXTURES = [
    "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104\ntp - Open",
    "Gold Sell Limit\n3990-3998\nSl - 4008",
    "Move SL to 4138 for added safety",
    "Market is very shaky move SL to 4074 for safety",
    "Secure Profits.",
    "Exit this trade on your comfort.",
    "50+ Pips.",
    "Zone Valid",
    "Same Zone for Re-entry",
    "BTCUSD Buy 65000-66000 SL 64000"
]

def test_pure_parser_benchmark_1000_runs():
    durations_ms = []

    # Warmup
    for f in FIXTURES:
        parse_raw_text(f)

    # 1,000 runs
    for i in range(1000):
        text = FIXTURES[i % len(FIXTURES)]
        start = time.perf_counter()
        parse_raw_text(text)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        durations_ms.append(elapsed_ms)

    median_ms = statistics.median(durations_ms)
    sorted_durations = sorted(durations_ms)
    p95_ms = sorted_durations[int(0.95 * len(sorted_durations))]

    print(f"\n[Parser Benchmark] 1,000 Runs -> Median: {median_ms:.4f} ms, p95: {p95_ms:.4f} ms")
    assert len(durations_ms) == 1000
    assert median_ms < 5.0  # Pure parsing is sub-millisecond to low-millisecond
