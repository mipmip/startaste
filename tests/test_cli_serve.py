import pytest

import startaste.dashboard
from startaste.cli import main


class _FakeApp:
    def __init__(self):
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs


@pytest.fixture
def fake_app(monkeypatch, tmp_path):
    app = _FakeApp()
    monkeypatch.setattr(startaste.dashboard, "create_app", lambda: app)
    monkeypatch.setenv("STARTASTE_DB", str(tmp_path / "t.db"))
    monkeypatch.setenv("STARTASTE_DATA", str(tmp_path))
    monkeypatch.setenv("STARTASTE_STATE", str(tmp_path))
    return app


class TestServeBind:
    def test_defaults_to_loopback(self, fake_app, monkeypatch):
        monkeypatch.setattr("sys.argv", ["startaste", "serve"])
        main()
        assert fake_app.run_kwargs == {"host": "127.0.0.1", "port": 8421}

    def test_host_and_port_are_passed_through(self, fake_app, monkeypatch):
        monkeypatch.setattr(
            "sys.argv", ["startaste", "serve", "--host", "192.168.100.2", "--port", "9000"]
        )
        main()
        assert fake_app.run_kwargs == {"host": "192.168.100.2", "port": 9000}
