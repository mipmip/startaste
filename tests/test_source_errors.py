"""How credential and availability failures are reported.

The contract: a condition a source understands becomes a SourceError, never a
transport exception escaping to the user as a traceback.
"""

import pytest
import requests
import responses

from startaste.sources.base import SourceAuthError, SourceError, SourceUnavailableError
from startaste.sources.github.api import GithubClient

STARRED = "https://api.github.com/user/starred?page=1&per_page=100"


class TestGithubFailureMapping:
    @responses.activate
    def test_401_is_a_rejected_token(self):
        responses.get(STARRED, json={"message": "Bad credentials"}, status=401)
        with pytest.raises(SourceAuthError) as excinfo:
            GithubClient("bad").get_starred()
        assert excinfo.value.source == "github"
        assert excinfo.value.env_vars == ["GITHUB_TOKEN"]
        assert "GITHUB_TOKEN was rejected" in excinfo.value.detail

    @responses.activate
    def test_403_with_the_rate_limit_exhausted_is_not_blamed_on_the_token(self):
        responses.get(
            STARRED,
            json={"message": "API rate limit exceeded"},
            status=403,
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700000000"},
        )
        with pytest.raises(SourceUnavailableError) as excinfo:
            GithubClient("good").get_starred()
        assert "rate limit" in excinfo.value.detail
        assert "GITHUB_TOKEN" not in excinfo.value.detail

    @responses.activate
    def test_403_without_a_rate_limit_is_a_rejected_token(self):
        responses.get(STARRED, json={"message": "Forbidden"}, status=403)
        with pytest.raises(SourceAuthError):
            GithubClient("bad").get_starred()

    @responses.activate
    def test_connection_failure_is_unavailable_not_a_credential_problem(self):
        # requests wraps a real connection failure in its own ConnectionError
        responses.get(STARRED, body=requests.exceptions.ConnectionError("reset"))
        with pytest.raises(SourceUnavailableError) as excinfo:
            GithubClient("good").get_starred()
        assert "could not reach" in excinfo.value.detail

    @responses.activate
    def test_retry_exhaustion_is_unavailable(self):
        """The adapter retries 429 and 5xx; when it gives up, requests raises
        RetryError, which must read as transient rather than as a bad token."""
        responses.get(STARRED, body=requests.exceptions.RetryError("gave up"))
        with pytest.raises(SourceUnavailableError) as excinfo:
            GithubClient("good").get_starred()
        assert "GITHUB_TOKEN" not in excinfo.value.detail

    @responses.activate
    def test_an_unexpected_status_is_unavailable(self):
        responses.get(STARRED, json={}, status=500)
        with pytest.raises(SourceUnavailableError):
            GithubClient("good").get_starred()

    @responses.activate
    def test_every_failure_is_a_source_error(self):
        """So one handler in run_sync covers them all."""
        responses.get(STARRED, json={}, status=401)
        with pytest.raises(SourceError):
            GithubClient("bad").get_starred()


class TestRunSyncKeepsGoing:
    def _source(self, name, exc=None):
        class _S:
            def __init__(self):
                self.synced = False

            def sync(self_inner):
                if exc:
                    raise exc
                self_inner.synced = True

        s = _S()
        s.name = name
        s.env_help = {}
        s.is_configured = lambda: True
        return s

    def test_a_failing_source_does_not_stop_the_next_one(self, monkeypatch):
        import startaste.sync as sync_mod

        first = self._source("first", SourceAuthError("first", "token was rejected", ["T"]))
        second = self._source("second")
        monkeypatch.setattr(sync_mod, "get_configured_sources", lambda: [first, second])

        with pytest.raises(SystemExit) as excinfo:
            sync_mod.run_sync()

        assert second.synced is True, "the second source must still be synced"
        assert "first" in str(excinfo.value)
        assert "Other configured sources were synced" in str(excinfo.value)

    def test_all_sources_failing_exits_non_zero_naming_them(self, monkeypatch):
        import startaste.sync as sync_mod

        a = self._source("a", SourceUnavailableError("a", "unreachable"))
        b = self._source("b", SourceAuthError("b", "rejected", ["T"]))
        monkeypatch.setattr(sync_mod, "get_configured_sources", lambda: [a, b])

        with pytest.raises(SystemExit) as excinfo:
            sync_mod.run_sync()
        assert "a" in str(excinfo.value) and "b" in str(excinfo.value)

    def test_a_successful_run_does_not_raise(self, monkeypatch):
        import startaste.sync as sync_mod

        only = self._source("only")
        monkeypatch.setattr(sync_mod, "get_configured_sources", lambda: [only])
        sync_mod.run_sync()
        assert only.synced is True

    def test_an_unexpected_exception_is_not_swallowed(self, monkeypatch):
        """Only conditions a source understands are turned into one clean line;
        a genuine bug must still surface."""
        import startaste.sync as sync_mod

        boom = self._source("boom", ValueError("a real bug"))
        monkeypatch.setattr(sync_mod, "get_configured_sources", lambda: [boom])
        with pytest.raises(ValueError, match="a real bug"):
            sync_mod.run_sync()
