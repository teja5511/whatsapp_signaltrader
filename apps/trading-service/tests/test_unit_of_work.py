import pytest
from src.database.engine import SessionLocal, Base, engine
from src.database.unit_of_work import UnitOfWork

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_unit_of_work_commit():
    with UnitOfWork(session_factory=SessionLocal) as uow:
        uow.settings.set_setting("entry_count", "6")

    with UnitOfWork(session_factory=SessionLocal) as uow:
        settings = uow.settings.get_settings()
        assert settings.entry_count == 6

def test_unit_of_work_rollback_on_exception():
    try:
        with UnitOfWork(session_factory=SessionLocal) as uow:
            uow.settings.set_setting("entry_count", "6")
            raise ValueError("Forced error for rollback testing")
    except ValueError:
        pass

    with UnitOfWork(session_factory=SessionLocal) as uow:
        settings = uow.settings.get_settings()
        assert settings.entry_count == 5  # Reverted to default
