import pytest

from startaste.dashboard import create_app
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _insert_hn_story(id, title="Test Story", time=1700000000):
    HnStory.create(_id=str(id))
    HnStory.save_doc({
        "id": str(id), "type": "story", "by": "alice",
        "time": str(time), "title": title, "url": "https://example.com",
        "score": 42, "descendants": 5,
    })


def _insert_github_star(id, name="owner/repo"):
    GithubStar.create(_id=str(id))
    GithubStar.save_doc({
        "starred_at": "2024-06-15T10:30:00Z",
        "repo": {
            "id": id, "full_name": name,
            "description": "A project", "language": "Python",
            "stargazers_count": 100,
        },
    })


class TestIndexRoute:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_shows_sources(self, client):
        resp = client.get("/")
        assert b"hn" in resp.data
        assert b"github" in resp.data

    def test_index_shows_counts(self, client):
        _insert_hn_story(11111)
        resp = client.get("/")
        assert b"1" in resp.data


class TestHnRoute:
    def test_hn_returns_200(self, client):
        resp = client.get("/hn")
        assert resp.status_code == 200

    def test_hn_shows_stories(self, client):
        _insert_hn_story(11111, title="My Test Story")
        resp = client.get("/hn")
        assert b"My Test Story" in resp.data

    def test_hn_comments_returns_200(self, client):
        resp = client.get("/hn/comments")
        assert resp.status_code == 200

    def test_hn_pagination(self, client):
        for i in range(60):
            _insert_hn_story(11111 + i, time=1700000000 + i)
        resp = client.get("/hn")
        assert b"page 1 of 2" in resp.data


class TestGithubRoute:
    def test_github_returns_200(self, client):
        resp = client.get("/github")
        assert resp.status_code == 200

    def test_github_shows_repos(self, client):
        _insert_github_star(100001, "alice/cool-project")
        resp = client.get("/github")
        assert b"alice/cool-project" in resp.data
