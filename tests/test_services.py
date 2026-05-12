import json

from startaste.dashboard.services import get_overview, get_hn_stories, get_hn_comments, get_github_stars
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar


def _insert_hn_story(id, title="Test Story", time=1700000000):
    HnStory.create(_id=str(id))
    HnStory.save_doc({
        "id": str(id), "type": "story", "by": "alice",
        "time": str(time), "title": title, "url": "https://example.com",
        "score": 42, "descendants": 5,
    })


def _insert_hn_comment(id, text="Test comment", time=1700100000):
    HnComment.create(_id=str(id))
    HnComment.save_doc({
        "id": str(id), "type": "comment", "by": "bob",
        "time": str(time), "parent": "11111", "text": text,
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


class TestGetOverview:
    def test_empty_db(self):
        data = get_overview()
        assert len(data["sources"]) >= 2
        for src in data["sources"]:
            for count in src["counts"].values():
                assert count == 0

    def test_with_data(self):
        _insert_hn_story(11111)
        _insert_hn_comment(66666)
        _insert_github_star(100001)

        data = get_overview()
        hn = next(s for s in data["sources"] if s["name"] == "hn")
        gh = next(s for s in data["sources"] if s["name"] == "github")

        assert hn["counts"]["story"] == 1
        assert hn["counts"]["comment"] == 1
        assert gh["counts"]["star"] == 1
        assert hn["last_sync"] is not None


class TestGetHnStories:
    def test_empty(self):
        data = get_hn_stories()
        assert data["items"] == []
        assert data["total"] == 0

    def test_with_stories(self):
        for i in range(3):
            _insert_hn_story(11111 + i, time=1700000000 + i)

        data = get_hn_stories()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_pagination(self):
        for i in range(5):
            _insert_hn_story(11111 + i, time=1700000000 + i)

        page1 = get_hn_stories(page=1, per_page=2)
        assert len(page1["items"]) == 2
        assert page1["total"] == 5
        assert page1["pages"] == 3

        page3 = get_hn_stories(page=3, per_page=2)
        assert len(page3["items"]) == 1

    def test_body_is_parsed(self):
        _insert_hn_story(11111)
        data = get_hn_stories()
        assert isinstance(data["items"][0]["body"], dict)


class TestGetHnComments:
    def test_with_comments(self):
        _insert_hn_comment(66666)
        data = get_hn_comments()
        assert data["total"] == 1


class TestGetGithubStars:
    def test_with_stars(self):
        _insert_github_star(100001, "alice/project")
        _insert_github_star(100002, "bob/project")

        data = get_github_stars()
        assert data["total"] == 2
        assert isinstance(data["items"][0]["body"], dict)
