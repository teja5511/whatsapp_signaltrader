import time
import pytest
from src.events.contracts import DomainEventDTO
from src.orchestration.idempotency import generate_orchestration_run_idempotency_key

def test_benchmark_domain_event_contract_constructions():
    """Benchmark: 100,000 domain event insert-contract constructions."""
    start_time = time.perf_counter()
    for i in range(100_000):
        dto = DomainEventDTO(
            event_id=f"evt-{i}",
            sequence=i,
            event_type="BENCHMARK_EVENT",
            aggregate_type="BENCHMARK",
            aggregate_id=f"agg-{i}",
            correlation_id=f"corr-{i}",
            payload={"index": i, "status": "OK"}
        )
    duration = time.perf_counter() - start_time
    ops_per_sec = 100_000 / duration
    print(f"\n[BENCHMARK] 100,000 Domain Event DTO constructions: {duration:.4f}s ({ops_per_sec:,.0f} ops/sec)")
    assert duration < 5.0

def test_benchmark_orchestration_idempotency_keys():
    """Benchmark: 10,000 orchestration decision idempotency key generations."""
    start_time = time.perf_counter()
    for i in range(10_000):
        key = generate_orchestration_run_idempotency_key("WHATSAPP_MESSAGE", f"msg-bench-{i}")
    duration = time.perf_counter() - start_time
    ops_per_sec = 10_000 / duration
    print(f"\n[BENCHMARK] 10,000 Orchestration Idempotency Key generations: {duration:.4f}s ({ops_per_sec:,.0f} ops/sec)")
    assert duration < 2.0
