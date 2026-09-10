import pytest

import startaste.dashboard
from startaste.cli import main


class _FakeApp:
    def __init__(self):
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs


@pytest.fixture
def fake_app(monkeypatch):
    app = _FakeApp()
    monkeypatch.setattr(startaste.dashboard, "create_app", lambda: app)
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


class TestMcpCommand:
    def test_defaults_to_loopback_and_passes_arguments(self, monkeypatch, tmp_path):
        called = {}
        import startaste.mcp.server

        monkeypatch.setattr(
            startaste.mcp.server, "serve", lambda **kw: called.update(kw)
        )
        tokens = tmp_path / "tokens.json"
        tokens.write_text("[]")

        monkeypatch.setattr("sys.argv", ["startaste", "mcp", "--tokens-file", str(tokens)])
        main()
        assert called == {"host": "127.0.0.1", "port": 8766, "tokens_file": str(tokens)}

        called.clear()
        monkeypatch.setattr("sys.argv", [
            "startaste", "mcp", "--tokens-file", str(tokens),
            "--host", "192.168.100.2", "--port", "9999",
        ])
        main()
        assert called == {"host": "192.168.100.2", "port": 9999, "tokens_file": str(tokens)}

    def test_tokens_file_is_required(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["startaste", "mcp"])
        with pytest.raises(SystemExit):
            main()


class TestMcpTokenCommand:
    def test_prints_a_token_and_a_matching_record(self, monkeypatch, capsys, tmp_path):
        from startaste.mcp.auth import hash_token

        monkeypatch.setattr("sys.argv", ["startaste", "mcp-token", "--name", "laptop"])
        main()

        out = capsys.readouterr().out
        token = out.split("store it now):")[1].split("record to add")[0].strip()
        assert '"name": "laptop"' in out
        assert hash_token(token) in out
        # The database must not be created just to mint a token.
        assert not (tmp_path / "startaste.db").exists()
