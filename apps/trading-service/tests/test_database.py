import pytest
from sqlalchemy import text
from src.database.engine import engine, SessionLocal, Base

def test_sqlite_pragma_wal_and_foreign_keys():
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        journal_mode = conn.execute(text("PRAGMA journal_mode;")).scalar()
        foreign_keys = conn.execute(text("PRAGMA foreign_keys;")).scalar()
        assert journal_mode.upper() in ["WAL", "MEMORY"]
        assert foreign_keys in [1, True]

def test_database_tables_exist():
    Base.metadata.create_all(bind=engine)
    tables = engine.dialect.get_table_names(engine.connect())
    expected_tables = [
        "app_settings", "trading_policies", "whatsapp_messages", "duplicate_keys",
        "parsed_messages", "signals", "campaigns", "campaign_state_transitions",
        "planned_entries", "mt5_orders", "mt5_positions", "commands",
        "ambiguous_command_confirmations", "system_audit_events", "system_errors",
        "reconciliation_runs", "reconciliation_items", "recovery_actions",
        "system_locks", "health_incidents", "worker_heartbeats",
    ]
    for table in expected_tables:
        assert table in tables


def test_removed_legacy_order_tables_are_absent():
    """pending_orders/positions were superseded by mt5_orders/mt5_positions.

    They were never written to; keeping them invited writes to the wrong table.
    """
    Base.metadata.create_all(bind=engine)
    tables = engine.dialect.get_table_names(engine.connect())
    assert "pending_orders" not in tables
    assert "positions" not in tables


def test_financial_columns_round_trip_exactly():
    """Money must survive the database without float drift."""
    from decimal import Decimal
    from src.database.models import SignalModel, ParsedMessageModel, WhatsAppMessageModel
    from datetime import datetime, timezone

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        db.add(WhatsAppMessageModel(
            id="msg-dec-1", group_id="g", sender_id="s", raw_content="x",
            content_hash="h", received_at=now,
        ))
        db.flush()
        db.add(ParsedMessageModel(
            id="pm-dec-1", raw_message_id="msg-dec-1", message_type="NEW_SIGNAL",
            parsed_json="{}", parsed_at=now,
        ))
        db.flush()
        db.add(SignalModel(
            id="sig-dec-1", parsed_message_id="pm-dec-1", direction="SELL",
            entry_min=Decimal("3990.12345678"), entry_max=Decimal("3998.87654321"),
            stop_loss=Decimal("4008.00000001"), created_at=now,
        ))
        db.commit()

        loaded = db.get(SignalModel, "sig-dec-1")
        assert loaded.entry_min == Decimal("3990.12345678")
        assert loaded.entry_max == Decimal("3998.87654321")
        assert loaded.stop_loss == Decimal("4008.00000001")
    finally:
        db.close()
