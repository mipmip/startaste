import sqlite3

from startaste.db import database, init_database


def _open_file_db(tmp_path, monkeypatch, name="startaste.db"):
    """Point startaste at a file database and open it. The autouse fixture
    uses :memory:, which cannot be in WAL mode at all."""
    db_path = tmp_path / name
    monkeypatch.setenv("STARTASTE_DB", str(db_path))
    monkeypatch.setenv("STARTASTE_DATA", str(tmp_path))
    monkeypatch.setenv("STARTASTE_STATE", str(tmp_path))
    if not database.is_closed():
        database.close()
    init_database()
    return db_path


class TestJournalMode:
    def test_fresh_database_uses_wal(self, tmp_path, monkeypatch):
        _open_file_db(tmp_path, monkeypatch)
        mode = database.execute_sql("pragma journal_mode").fetchone()[0]
        assert mode == "wal"

    def test_rollback_journal_database_is_converted(self, tmp_path, monkeypatch):
        # a database as it exists before this change
        db_path = tmp_path / "startaste.db"
        old = sqlite3.connect(db_path)
        old.execute("pragma journal_mode = delete")
        old.execute("create table if not exists probe (id integer)")
        old.commit()
        assert old.execute("pragma journal_mode").fetchone()[0] == "delete"
        old.close()

        _open_file_db(tmp_path, monkeypatch)
        assert database.execute_sql("pragma journal_mode").fetchone()[0] == "wal"

        # WAL is persistent in the file, so a later connection sees it too
        after = sqlite3.connect(db_path)
        assert after.execute("pragma journal_mode").fetchone()[0] == "wal"
        after.close()

    def test_read_succeeds_during_open_write_transaction(self, tmp_path, monkeypatch):
        """The failure this change exists to prevent: in rollback-journal mode
        this read raises 'database is locked'."""
        from startaste.sources.hn.models import HnStory

        db_path = _open_file_db(tmp_path, monkeypatch)
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
    def test_busy_timeout_is_configured(self, tmp_path, monkeypatch):
        _open_file_db(tmp_path, monkeypatch)
        timeout = database.execute_sql("pragma busy_timeout").fetchone()[0]
        assert timeout > 0
