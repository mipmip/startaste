import sqlite3

from startaste.db import database, init_database


def _open_file_db(tmp_path):
    """Open the file database conftest points STARTASTE_DB at. The database
    fixture uses :memory:, which cannot be in WAL mode at all."""
    if not database.is_closed():
        database.close()
    init_database()
    return tmp_path / "startaste.db"


class TestJournalMode:
    def test_fresh_database_uses_wal(self, tmp_path):
        _open_file_db(tmp_path)
        mode = database.execute_sql("pragma journal_mode").fetchone()[0]
        assert mode == "wal"

    def test_rollback_journal_database_is_converted(self, tmp_path):
        # a database as it exists before this change
        db_path = tmp_path / "startaste.db"
        old = sqlite3.connect(db_path)
        old.execute("pragma journal_mode = delete")
        old.execute("create table if not exists probe (id integer)")
        old.commit()
        assert old.execute("pragma journal_mode").fetchone()[0] == "delete"
        old.close()

        _open_file_db(tmp_path)
        assert database.execute_sql("pragma journal_mode").fetchone()[0] == "wal"

        # WAL is persistent in the file, so a later connection sees it too
        after = sqlite3.connect(db_path)
        assert after.execute("pragma journal_mode").fetchone()[0] == "wal"
        after.close()

    def test_read_succeeds_during_open_write_transaction(self, tmp_path, monkeypatch):
        """The failure this change exists to prevent: in rollback-journal mode
        this read raises 'database is locked'."""
        from startaste.sources.hn.models import HnStory

        db_path = _open_file_db(tmp_path)
        HnStory.create(_id="1")

        writer = sqlite3.connect(db_path, timeout=1)
        writer.execute("begin immediate")
        writer.execute("insert into hn_story (_id) values ('2')")
        try:
            assert HnStory.select().count() == 1  # reader is not blocked
        finally:
            writer.rollback()
            writer.close()


class TestBusyTimeout:
    def test_busy_timeout_is_configured(self, tmp_path):
        _open_file_db(tmp_path)
        timeout = database.execute_sql("pragma busy_timeout").fetchone()[0]
        assert timeout > 0
