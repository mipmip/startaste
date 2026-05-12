import json

import pytest
import responses

from startaste.scraper import Req
from tests.conftest import load_fixture

HN = "https://news.ycombinator.com"
API = "https://hacker-news.firebaseio.com/v0/item"


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
        with pytest.raises(Exception, match="authentication failed"):
            req.login("testuser", "wrongpassword")


class TestScrapeStories:
    @responses.activate
    def test_scrape_stories_single_page(self):
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_empty.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == ["11111", "22222", "33333"]

    @responses.activate
    def test_scrape_stories_multiple_pages(self):
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_page2.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=3", body=load_fixture("hn_stories_empty.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == ["11111", "22222", "33333", "44444", "55555"]

    @responses.activate
    def test_scrape_stories_empty_page_stops(self):
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_empty.html"))
        req = Req()
        ids = req.get_upvoted_stories("testuser", max_page=10)
        assert ids == []


class TestScrapeComments:
    @responses.activate
    def test_scrape_comments(self):
        responses.get(
            f"{HN}/upvoted?id=testuser&comments=t&p=1",
            body=load_fixture("hn_comments_page1.html"),
        )
        responses.get(
            f"{HN}/upvoted?id=testuser&comments=t&p=2",
            body=load_fixture("hn_stories_empty.html"),
        )
        req = Req()
        ids = req.get_upvoted_comments("testuser", max_page=10)
        assert ids == ["66666", "77777"]


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
