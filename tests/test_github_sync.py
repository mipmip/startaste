import json

import responses

from startaste.sources.github import GithubSource
from startaste.sources.github.models import GithubStar
from tests.conftest import load_fixture

GITHUB_API = "https://api.github.com"


class TestGithubFullSync:
    @responses.activate
    def test_full_sync_populates_database(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")

        responses.get(
            f"{GITHUB_API}/user/starred?page=1&per_page=100",
            body=load_fixture("github_starred_page1.json"),
            content_type="application/json",
        )
        responses.get(
            f"{GITHUB_API}/user/starred?page=2&per_page=100",
            body=load_fixture("github_starred_empty.json"),
            content_type="application/json",
        )
        # Second pass for metadata
        responses.get(
            f"{GITHUB_API}/user/starred?page=1&per_page=100",
            body=load_fixture("github_starred_page1.json"),
            content_type="application/json",
        )

        source = GithubSource()
        source.sync()

        assert GithubStar.count_all() == 3
        assert GithubStar.count_empty() == 0


class TestGithubIncrementalSync:
    @responses.activate
    def test_incremental_stops_when_all_known(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")

        # Pre-populate all 3 stars
        starred = json.loads(load_fixture("github_starred_page1.json"))
        for star in starred:
            repo = star["repo"]
            GithubStar.create(_id=str(repo["id"]))
            GithubStar.save_doc(star)

        responses.get(
            f"{GITHUB_API}/user/starred?page=1&per_page=100",
            body=load_fixture("github_starred_page1.json"),
            content_type="application/json",
        )

        source = GithubSource()
        source.sync()

        # No new items
        assert GithubStar.count_all() == 3
        assert GithubStar.count_empty() == 0
