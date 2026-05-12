import time
from pathlib import Path

import pytest

from startaste.db import database
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar

ALL_MODELS = [HnStory, HnComment, GithubStar]
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def tmp_database():
    database.init(":memory:")
    database.connect()
    database.create_tables(ALL_MODELS)
    yield
    if not database.is_closed():
        database.drop_tables(ALL_MODELS)
        database.close()


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def load_fixture_bytes(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()
