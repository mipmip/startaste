import json

from startaste.queries import (
    get_item,
    search_stars,
    search_upvotes,
    top_domains,
    top_languages,
    top_topics,
)
from startaste.sources.github.models import GithubStar
from startaste.sources.hn.models import HnComment, HnStory


def _star(_id, full_name, description="", language=None, topics=None):
    GithubStar.create(_id=_id)
    GithubStar.save_doc({
        "id": _id,
        "time": "1700000000",
        "starred_at": "2026-01-01T00:00:00Z",
        "repo": {
            "id": _id,
            "full_name": full_name,
            "description": description,
            "language": language,
            "topics": topics or [],
            "html_url": f"https://github.com/{full_name}",
            "stargazers_count": 42,
        },
    })


def _story(_id, title, url=None):
    HnStory.create(_id=_id)
    HnStory.save_doc({"id": _id, "time": "1700000000", "title": title, "url": url, "type": "story"})


def _comment(_id, text):
    HnComment.create(_id=_id)
    HnComment.save_doc({"id": _id, "time": "1700000000", "text": text, "type": "comment"})


class TestSearchStars:
    def test_empty_database(self):
        assert search_stars(query="anything") == {
            "items": [], "total": 0, "limit": 20, "truncated": False
        }

    def test_matches_name_and_description(self):
        _star("1", "altsem/gitu", "a git TUI", language="Rust", topics=["git", "tui"])
        _star("2", "other/thing", "unrelated", language="Go")
        assert [i["full_name"] for i in search_stars(query="gitu")["items"]] == ["altsem/gitu"]
        assert [i["full_name"] for i in search_stars(query="TUI")["items"]] == ["altsem/gitu"]

    def test_no_match(self):
        _star("1", "altsem/gitu", "a git TUI")
        assert search_stars(query="kubernetes")["total"] == 0

    def test_language_filter(self):
        _star("1", "a/rusty", language="Rust")
        _star("2", "b/gopher", language="Go")
        assert [i["full_name"] for i in search_stars(language="rust")["items"]] == ["a/rusty"]

    def test_topic_filter(self):
        _star("1", "a/one", topics=["nix", "cli"])
        _star("2", "b/two", topics=["react"])
        assert [i["full_name"] for i in search_stars(topic="CLI")["items"]] == ["a/one"]

    def test_limit_reports_truncation(self):
        for i in range(5):
            _star(str(i), f"o/repo{i}", "shared description")
        result = search_stars(query="shared", limit=2)
        assert len(result["items"]) == 2
        assert result["total"] == 5
        assert result["truncated"] is True

    def test_untruncated_result_says_so(self):
        _star("1", "a/one", "shared")
        result = search_stars(query="shared", limit=20)
        assert result["truncated"] is False


class TestSearchUpvotes:
    def test_matches_story_title_and_comment_text(self):
        _story("10", "Rust in the kernel")
        _comment("20", "I disagree about Rust")
        assert {i["id"] for i in search_upvotes(query="rust")["items"]} == {"10", "20"}

    def test_item_type_filter(self):
        _story("10", "Rust in the kernel")
        _comment("20", "I disagree about Rust")
        assert [i["id"] for i in search_upvotes(query="rust", item_type="story")["items"]] == ["10"]
        assert [i["id"] for i in search_upvotes(query="rust", item_type="comment")["items"]] == ["20"]

    def test_empty_database(self):
        assert search_upvotes(query="rust")["total"] == 0


class TestAggregations:
    def test_top_topics_ordered_by_count(self):
        _star("1", "a/one", topics=["nix", "cli"])
        _star("2", "b/two", topics=["nix"])
        _star("3", "c/three", topics=[])
        result = top_topics()
        assert result["items"] == [{"name": "nix", "count": 2}, {"name": "cli", "count": 1}]
        assert result["total_distinct"] == 2

    def test_top_languages_skips_missing(self):
        _star("1", "a/one", language="Nix")
        _star("2", "b/two", language="Nix")
        _star("3", "c/three", language=None)
        result = top_languages()
        assert result["items"] == [{"name": "Nix", "count": 2}]
        assert result["total_distinct"] == 1

    def test_top_domains_normalises_and_skips_urlless(self):
        _story("1", "one", url="https://www.example.com/a")
        _story("2", "two", url="https://example.com/b")
        _story("3", "no url")
        result = top_domains()
        assert result["items"] == [{"name": "example.com", "count": 2}]

    def test_limit_applies(self):
        _star("1", "a/one", topics=["a", "b", "c"])
        assert len(top_topics(limit=2)["items"]) == 2

    def test_empty_database(self):
        assert top_topics()["items"] == []
        assert top_languages()["items"] == []
        assert top_domains()["items"] == []


class TestGetItem:
    def test_finds_a_star(self):
        _star("1", "altsem/gitu")
        result = get_item("github", "1")
        assert result["found"] is True
        assert result["type"] == "star"
        assert result["body"]["repo"]["full_name"] == "altsem/gitu"

    def test_finds_story_and_comment_under_hn(self):
        _story("10", "a story")
        _comment("20", "a comment")
        assert get_item("hn", "10")["type"] == "story"
        assert get_item("hn", "20")["type"] == "comment"

    def test_unknown_id_is_not_found_not_an_error(self):
        result = get_item("github", "999")
        assert result["found"] is False
        assert "999" in result["reason"]

    def test_unknown_source(self):
        result = get_item("gitlab", "1")
        assert result["found"] is False
        assert "unknown source" in result["reason"]
