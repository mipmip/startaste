import pytest

from startaste.sources import get_sources, get_configured_sources, get_source
from startaste.sources.hn import HnSource
from startaste.sources.github import GithubSource


class TestSourceRegistry:
    def test_get_sources_returns_all(self):
        sources = get_sources()
        names = [s.name for s in sources]
        assert "hn" in names
        assert "github" in names

    def test_get_configured_sources_none(self, monkeypatch):
        monkeypatch.delenv("HN_COMMENTS_ACCT", raising=False)
        monkeypatch.delenv("HN_COMMENTS_PW", raising=False)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        sources = get_configured_sources()
        assert len(sources) == 0

    def test_get_configured_sources_hn_only(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        sources = get_configured_sources()
        assert len(sources) == 1
        assert sources[0].name == "hn"

    def test_get_source_by_name(self):
        source = get_source("hn")
        assert isinstance(source, HnSource)

    def test_get_source_unknown(self):
        with pytest.raises(SystemExit, match="unknown source"):
            get_source("unknown")


class TestHnSource:
    def test_metadata(self):
        source = HnSource()
        assert source.name == "hn"
        assert source.item_types == ["story", "comment"]
        assert len(source.models) == 2

    def test_is_configured(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "user")
        monkeypatch.setenv("HN_COMMENTS_PW", "pass")
        assert HnSource().is_configured()

    def test_not_configured(self, monkeypatch):
        monkeypatch.delenv("HN_COMMENTS_ACCT", raising=False)
        monkeypatch.delenv("HN_COMMENTS_PW", raising=False)
        assert not HnSource().is_configured()


class TestGithubSource:
    def test_metadata(self):
        source = GithubSource()
        assert source.name == "github"
        assert source.item_types == ["star"]
        assert len(source.models) == 1

    def test_is_configured(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        assert GithubSource().is_configured()

    def test_not_configured(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        assert not GithubSource().is_configured()
