import json
import logging

import pytest
import responses

from startaste.sources.base import SourceAuthError
from startaste.sources.hn.scraper import Req
from tests.conftest import load_fixture

HN = "https://news.ycombinator.com"
API = "https://hacker-news.firebaseio.com/v0/item"

STORIES = f"{HN}/upvoted?id=testuser"
COMMENTS = f"{HN}/upvoted?id=testuser&comments=t"
# the cursor the More link in hn_stories_page1.html points at — HN paginates
# /upvoted with next/n/time, not with p=
CURSOR = f"{HN}/upvoted?id=testuser&next=44444&n=31&time=1.787635665137972e9"


class TestLogin:
    @responses.activate
    def test_login_success(self):
        responses.post(f"{HN}/login", body=load_fixture("hn_login_success.html"), status=200)
        req = Req()
        req.login("testuser", "testpassword")  # should not raise

    @responses.activate
    def test_login_failure_bad_credentials(self):
        responses.post(f"{HN}/login", body=load_fixture("hn_login_failure.html"), status=200)
        req = Req()
        with pytest.raises(SourceAuthError) as excinfo:
            req.login("testuser", "wrongpassword")
        assert excinfo.value.source == "hn"
        assert excinfo.value.env_vars == ["HN_COMMENTS_ACCT", "HN_COMMENTS_PW"]


class TestScrapeStories:
    @responses.activate
    def test_scrape_stories_follows_more_link(self):
        responses.get(STORIES, body=load_fixture("hn_stories_page1.html"))
        responses.get(CURSOR, body=load_fixture("hn_stories_page2.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == ["11111", "22222", "33333", "44444", "55555"]
        assert len(responses.calls) == 2

    @responses.activate
    def test_scrape_stories_stops_without_more_link(self):
        # hn_stories_page2.html is a last page: items, no More link
        responses.get(STORIES, body=load_fixture("hn_stories_page2.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == ["44444", "55555"]
        assert len(responses.calls) == 1

    @responses.activate
    def test_scrape_stories_empty_page_stops(self):
        responses.get(STORIES, body=load_fixture("hn_stories_empty.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == []
        assert len(responses.calls) == 1

    @responses.activate
    def test_page_limit_stops_traversal_and_warns(self, caplog):
        # a listing whose More link never runs out: page1 points at the cursor,
        # and the cursor serves page1 again
        responses.get(STORIES, body=load_fixture("hn_stories_page1.html"))
        responses.get(CURSOR, body=load_fixture("hn_stories_page1.html"))
        req = Req()
        with caplog.at_level(logging.WARNING):
            ids = req.get_upvoted_stories("testuser", max_page=3)
        assert len(responses.calls) == 3
        assert len(ids) == 9
        assert "page limit" in caplog.text


class TestScrapeComments:
    @responses.activate
    def test_scrape_comments(self):
        responses.get(COMMENTS, body=load_fixture("hn_comments_page1.html"))
        req = Req()
        ids = req.get_upvoted_comments("testuser", max_page=10)
        assert ids == ["66666", "77777"]

    @responses.activate
    def test_scrape_comments_ignores_parent_and_context_links(self):
        # each comment row also carries parent (item?id=60000) and context
        # (item?id=60000#66666) links; only the comment's own id may be taken
        responses.get(COMMENTS, body=load_fixture("hn_comments_page1.html"))
        req = Req()
        ids = req.get_upvoted_comments("testuser", max_page=10)
        assert ids == ["66666", "77777"]
        assert not [i for i in ids if "#" in i]


class TestGetItem:
    @responses.activate
    def test_get_item(self):
        item_data = load_fixture("hn_item_11111.json")
        responses.get(f"{API}/11111.json", body=item_data, content_type="application/json")
        req = Req()
        item = req.get_item("11111")
        assert item["id"] == 11111
        assert item["type"] == "story"
        assert item["by"] == "alice"
