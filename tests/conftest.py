import time
from pathlib import Path

import pytest

from startaste.db import database, Story, Comment

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def tmp_database():
    database.init(":memory:")
    database.connect()
    database.create_tables([Story, Comment])
    yield
    if not database.is_closed():
        database.drop_tables([Story, Comment])
        database.close()


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def load_fixture_bytes(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()
