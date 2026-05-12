from pathlib import Path

from startaste.paths import get_data_dir, get_state_dir, get_db_path, get_log_path, ensure_dirs, migrate_db_file


class TestDefaults:
    def test_data_dir_default(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_DATA", raising=False)
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        assert result == Path.home() / ".local" / "share" / "startaste"

    def test_state_dir_default(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_STATE", raising=False)
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)
        result = get_state_dir()
        assert result == Path.home() / ".local" / "state" / "startaste"

    def test_db_path_default(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_DB", raising=False)
        monkeypatch.delenv("STARTASTE_DATA", raising=False)
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_db_path()
        assert result == Path.home() / ".local" / "share" / "startaste" / "startaste.db"

    def test_log_path_default(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_LOG", raising=False)
        monkeypatch.delenv("STARTASTE_STATE", raising=False)
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)
        result = get_log_path()
        assert result == Path.home() / ".local" / "state" / "startaste" / "startaste.log"


class TestEnvOverrides:
    def test_data_dir_override(self, monkeypatch):
        monkeypatch.setenv("STARTASTE_DATA", "/var/lib/startaste")
        assert get_data_dir() == Path("/var/lib/startaste")

    def test_state_dir_override(self, monkeypatch):
        monkeypatch.setenv("STARTASTE_STATE", "/var/log/startaste")
        assert get_state_dir() == Path("/var/log/startaste")

    def test_db_path_override(self, monkeypatch):
        monkeypatch.setenv("STARTASTE_DB", "/custom/my.db")
        assert get_db_path() == Path("/custom/my.db")

    def test_log_path_override(self, monkeypatch):
        monkeypatch.setenv("STARTASTE_LOG", "/custom/app.log")
        assert get_log_path() == Path("/custom/app.log")

    def test_xdg_data_home_override(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_DATA", raising=False)
        monkeypatch.setenv("XDG_DATA_HOME", "/custom/data")
        assert get_data_dir() == Path("/custom/data/startaste")

    def test_xdg_state_home_override(self, monkeypatch):
        monkeypatch.delenv("STARTASTE_STATE", raising=False)
        monkeypatch.setenv("XDG_STATE_HOME", "/custom/state")
        assert get_state_dir() == Path("/custom/state/startaste")


class TestEnsureDirs:
    def test_creates_directories(self, monkeypatch, tmp_path):
        monkeypatch.setenv("STARTASTE_DATA", str(tmp_path / "data" / "startaste"))
        monkeypatch.setenv("STARTASTE_STATE", str(tmp_path / "state" / "startaste"))
        ensure_dirs()
        assert (tmp_path / "data" / "startaste").is_dir()
        assert (tmp_path / "state" / "startaste").is_dir()

    def test_existing_dirs_no_error(self, monkeypatch, tmp_path):
        data_dir = tmp_path / "data" / "startaste"
        data_dir.mkdir(parents=True)
        monkeypatch.setenv("STARTASTE_DATA", str(data_dir))
        monkeypatch.setenv("STARTASTE_STATE", str(tmp_path / "state" / "startaste"))
        ensure_dirs()


class TestMigrateDbFile:
    def test_rename_hn_db_in_data_dir(self, monkeypatch, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        old_db = data_dir / "hn.db"
        old_db.write_text("test data")
        monkeypatch.setenv("STARTASTE_DB", str(data_dir / "startaste.db"))

        migrate_db_file()

        assert not old_db.exists()
        assert (data_dir / "startaste.db").read_text() == "test data"

    def test_move_hn_db_from_cwd(self, monkeypatch, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        fake_cwd = tmp_path / "cwd"
        fake_cwd.mkdir()
        cwd_db = fake_cwd / "hn.db"
        cwd_db.write_text("cwd data")
        monkeypatch.setenv("STARTASTE_DB", str(data_dir / "startaste.db"))
        monkeypatch.setattr(Path, "cwd", staticmethod(lambda: fake_cwd))

        migrate_db_file()

        assert (data_dir / "startaste.db").read_text() == "cwd data"
        assert not cwd_db.exists()

    def test_no_migration_when_new_exists(self, monkeypatch, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        old_db = data_dir / "hn.db"
        old_db.write_text("old data")
        new_db = data_dir / "startaste.db"
        new_db.write_text("new data")
        monkeypatch.setenv("STARTASTE_DB", str(new_db))

        migrate_db_file()

        assert old_db.read_text() == "old data"
        assert new_db.read_text() == "new data"
