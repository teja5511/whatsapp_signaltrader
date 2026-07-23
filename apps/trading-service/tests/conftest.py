import pytest
from sqlalchemy import text
import src.database.models
from src.database.engine import engine, Base, SessionLocal

@pytest.fixture(autouse=True, scope="function")
def setup_and_clean_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys = OFF;"))
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(text(f"DELETE FROM {table.name};"))
        db.execute(text("PRAGMA foreign_keys = ON;"))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield
