import sqlite3

import pytest
from peewee import OperationalError

from startaste.db import database, init_database, open_readonly
from startaste.sources.hn.models import HnStory
from tests.conftest import ALL_MODELS


@pytest.fixture(autouse=True)
def _restore_writable_database():
    """These tests leave the shared connection read-only; the outer fixture's
    teardown drops tables, so hand it back something writable."""
    yield
    if not database.is_closed():
        database.close()
    database.init(":memory:")
    database.connect()
    database.create_tables(ALL_MODELS)


def _seed_file_db(tmp_path):
    """conftest already points STARTASTE_DB at tmp_path/startaste.db."""
    if not database.is_closed():
        database.close()
    init_database()
    HnStory.create(_id="1")
    database.close()
    return tmp_path / "startaste.db"


class TestReadOnlyOpen:
    def test_reads_are_allowed(self, tmp_path):
        _seed_file_db(tmp_path)
        open_readonly()
        assert HnStory.select().count() == 1

    def test_writes_are_refused_by_the_database(self, tmp_path):
        _seed_file_db(tmp_path)
        open_readonly()
        with pytest.raises(OperationalError, match="readonly"):
            HnStory.create(_id="2")

    def test_missing_database_is_a_clear_error_and_creates_nothing(self, tmp_path, monkeypatch):
        # a deliberate override, not isolation: this asserts behaviour for a
        # path with no database at it
        db_path = tmp_path / "absent.db"
        monkeypatch.setenv("STARTASTE_DB", str(db_path))
        if not database.is_closed():
            database.close()
        with pytest.raises(SystemExit, match="Run 'startaste sync' first"):
            open_readonly()
        assert not db_path.exists()

    def test_reads_succeed_while_another_connection_writes(self, tmp_path):
        """WAL (from sqlite-wal-mode) is what makes this work."""
        db_path = _seed_file_db(tmp_path)
        writer = sqlite3.connect(db_path, timeout=2)
        writer.execute("begin immediate")
        writer.execute("insert into hn_story (_id) values ('99')")
        try:
            open_readonly()
            assert HnStory.select().count() == 1  # the uncommitted row is not visible
        finally:
            writer.rollback()
            writer.close()
