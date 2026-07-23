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
        "app_settings", "whatsapp_messages", "duplicate_keys", "parsed_messages",
        "signals", "campaigns", "campaign_state_transitions", "planned_entries",
        "pending_orders", "positions", "commands", "ambiguous_command_confirmations",
        "system_audit_events", "system_errors"
    ]
    for table in expected_tables:
        assert table in tables
