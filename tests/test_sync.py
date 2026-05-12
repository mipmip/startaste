import json
import os

import responses

from startaste.db import database
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.hn import HnSource
from tests.conftest import load_fixture

HN = "https://news.ycombinator.com"
API = "https://hacker-news.firebaseio.com/v0/item"


def _mock_login():
    responses.post(f"{HN}/login", body=load_fixture("hn_login_success.html"), status=200)


def _mock_item(item_id, item_type="story"):
    fixture = f"hn_item_{item_id}.json"
    try:
        body = load_fixture(fixture)
    except FileNotFoundError:
        body = json.dumps({
            "id": int(item_id), "type": item_type, "by": "testuser",
            "time": "1700000000", "title": f"Item {item_id}",
        })
    responses.get(f"{API}/{item_id}.json", body=body, content_type="application/json")


class TestFullSync:
    @responses.activate
    def test_full_sync_populates_database(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")

        _mock_login()

        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_empty.html"))

        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        for item_id in ["11111", "22222", "33333"]:
            _mock_item(item_id, "story")
        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        source = HnSource()
        source.sync()

        assert HnStory.count_all() == 3
        assert HnComment.count_all() == 2
        assert HnStory.count_empty() == 0
        assert HnComment.count_empty() == 0


class TestIncrementalSync:
    @responses.activate
    def test_incremental_adds_only_new_items(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")

        HnStory.create(_id="11111")
        HnStory.save_doc({
            "id": "11111", "type": "story", "by": "alice",
            "time": "1700000000", "title": "Old Story",
        })

        _mock_login()

        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_empty.html"))

        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        for item_id in ["22222", "33333"]:
            _mock_item(item_id, "story")
        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        source = HnSource()
        source.sync()

        assert HnStory.count_all() == 3
        assert HnComment.count_all() == 2
        assert HnStory.count_empty() == 0

    @responses.activate
    def test_incremental_stops_when_all_ids_known(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")

        for item_id in ["11111", "22222", "33333"]:
            HnStory.create(_id=item_id)
            HnStory.save_doc({
                "id": item_id, "type": "story", "by": "alice",
                "time": "1700000000", "title": f"Story {item_id}",
            })

        _mock_login()

        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_page2.html"))

        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        source = HnSource()
        source.sync()

        assert HnStory.count_all() == 3
        assert HnStory.count_empty() == 0
        assert HnComment.count_all() == 2
