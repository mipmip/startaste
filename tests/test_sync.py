import json
import os

import responses

from startaste.db import Story, Comment, database
from startaste.sync import run_sync
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
        monkeypatch.setattr(database, "close", lambda: None)

        _mock_login()

        # Stories: page 1 has 3 items, page 2 is empty
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_empty.html"))

        # Comments: page 1 has 2 items, page 2 is empty
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        # Item API calls for each ID
        for item_id in ["11111", "22222", "33333"]:
            _mock_item(item_id, "story")
        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        run_sync()

        assert Story.count_all() == 3
        assert Comment.count_all() == 2
        assert Story.count_empty() == 0
        assert Comment.count_empty() == 0


class TestIncrementalSync:
    @responses.activate
    def test_incremental_adds_only_new_items(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")
        monkeypatch.setattr(database, "close", lambda: None)

        # Pre-populate DB with story 11111 (simulates previous sync)
        Story.create(_id="11111")
        Story.save_doc({
            "id": "11111", "type": "story", "by": "alice",
            "time": "1700000000", "title": "Old Story",
        })

        _mock_login()

        # Stories page 1 has 11111 (known) + 22222, 33333 (new)
        # Page 2 is empty
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_empty.html"))

        # Comments
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        # API calls only for new items (22222, 33333 stories + 66666, 77777 comments)
        for item_id in ["22222", "33333"]:
            _mock_item(item_id, "story")
        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        run_sync()

        assert Story.count_all() == 3  # 1 old + 2 new
        assert Comment.count_all() == 2
        assert Story.count_empty() == 0

    @responses.activate
    def test_incremental_stops_when_all_ids_known(self, monkeypatch):
        monkeypatch.setenv("HN_COMMENTS_ACCT", "testuser")
        monkeypatch.setenv("HN_COMMENTS_PW", "testpass")
        monkeypatch.setattr(database, "close", lambda: None)

        # Pre-populate DB with ALL story IDs from page 1
        for item_id in ["11111", "22222", "33333"]:
            Story.create(_id=item_id)
            Story.save_doc({
                "id": item_id, "type": "story", "by": "alice",
                "time": "1700000000", "title": f"Story {item_id}",
            })

        _mock_login()

        # Stories page 1 — all IDs already known, should stop here
        responses.get(f"{HN}/upvoted?id=testuser&p=1", body=load_fixture("hn_stories_page1.html"))
        # Page 2 should NOT be requested — but register it to detect over-fetching
        responses.get(f"{HN}/upvoted?id=testuser&p=2", body=load_fixture("hn_stories_page2.html"))

        # Comments still need fetching
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=1", body=load_fixture("hn_comments_page1.html"))
        responses.get(f"{HN}/upvoted?id=testuser&comments=t&p=2", body=load_fixture("hn_stories_empty.html"))

        for item_id in ["66666", "77777"]:
            _mock_item(item_id, "comment")

        run_sync()

        # Stories unchanged (no new items fetched)
        assert Story.count_all() == 3
        assert Story.count_empty() == 0
        # Comments were fetched
        assert Comment.count_all() == 2
