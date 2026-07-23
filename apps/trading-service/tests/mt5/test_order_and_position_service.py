import pytest
from decimal import Decimal
from src.database.engine import engine, Base, SessionLocal
from src.database.models import MT5OrderRecordModel, MT5PositionRecordModel, CampaignModel
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.order_service import MT5OrderService
from src.mt5.position_service import MT5PositionService
from src.mt5.execution_service import MT5ExecutionService
from src.mt5.contracts import Mt5OrderSnapshotDTO, Mt5PositionSnapshotDTO

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_order_modification_and_deletion():
    adapter = FakeMT5Adapter(scenario="healthy_demo_hedging")
    adapter.initialize()
    order_svc = MT5OrderService(adapter=adapter, session_factory=SessionLocal)

    # Seed fake adapter order
    adapter._orders[7001] = Mt5OrderSnapshotDTO(
        ticket=7001, magic_number=5555, symbol="XAUUSD", order_type="SELL_LIMIT",
        volume=Decimal("0.30"), price=Decimal("3990.00"), stop_loss=Decimal("4008.00"), comment="c1"
    )

    db = SessionLocal()
    try:
        o = MT5OrderRecordModel(
            id="order-rec-1", ticket=7001, magic_number=5555, symbol="XAUUSD",
            order_type="SELL_LIMIT", volume=0.30, price=3990.00, stop_loss=4008.00, comment="c1"
        )
        db.add(o)
        db.commit()
    finally:
        db.close()

    # Modify
    res_mod = order_svc.modify_order(7001, price=Decimal("3992.00"), stop_loss=Decimal("4010.00"))
    assert res_mod["status"] == "success"

    # Delete
    res_del = order_svc.delete_order(7001)
    assert res_del["status"] == "success"

def test_emergency_close_all_demo_xauusd():
    adapter = FakeMT5Adapter(scenario="healthy_demo_hedging")
    adapter.initialize()
    exec_svc = MT5ExecutionService(adapter=adapter, session_factory=SessionLocal)

    import os
    os.environ["MT5_CLOSE_ALL_ENABLED"] = "true"

    try:
        res = exec_svc.emergency_close_all_xauusd(confirmation_phrase="CLOSE ALL DEMO XAUUSD", scope="APPLICATION_OWNED")
        assert res["status"] == "success"
    finally:
        os.environ["MT5_CLOSE_ALL_ENABLED"] = "false"
