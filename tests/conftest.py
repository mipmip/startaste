import time
from pathlib import Path

import pytest

from startaste.db import database
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar

ALL_MODELS = [HnStory, HnComment, GithubStar]
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    """Resolve every path inside the test's own tmp_path.

    Enforced centrally rather than per test: a test that overrides nothing must
    still be unable to reach the developer's real data, state, database or log.
    Uses the documented STARTASTE_* overrides, so no production code is involved.
    """
    monkeypatch.setenv("STARTASTE_DATA", str(tmp_path))
    monkeypatch.setenv("STARTASTE_STATE", str(tmp_path))
    monkeypatch.setenv("STARTASTE_DB", str(tmp_path / "startaste.db"))
    monkeypatch.setenv("STARTASTE_LOG", str(tmp_path / "startaste.log"))


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
