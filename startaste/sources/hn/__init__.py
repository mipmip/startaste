from __future__ import annotations

import logging
import os

from bs4 import BeautifulSoup

from startaste.sources.base import Source
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.hn.scraper import Req, get_credentials

log = logging.getLogger(__name__)

VERY_HIGH_PAGE = 10000


class HnSource(Source):
    name = "hn"
    item_types = ["story", "comment"]
    models = [HnStory, HnComment]
    env_help = {
        "HN_COMMENTS_ACCT": "Hacker News username",
        "HN_COMMENTS_PW": "Hacker News password",
    }

    def is_configured(self) -> bool:
        return bool(os.getenv("HN_COMMENTS_ACCT") and os.getenv("HN_COMMENTS_PW"))

    def sync(self) -> None:
        username, password = get_credentials()
        req = Req()
        req.login(username, password)

        story_count = HnStory.count_all()
        comment_count = HnComment.count_all()
        is_full = story_count == 0 and comment_count == 0

        if is_full:
            log.info("HN full sync: database is empty, scraping all pages")
        else:
            log.info("HN incremental sync: stopping when all IDs on a page are known")

        self._sync_type(req, username, comments=False, model=HnStory, is_full=is_full)
        self._sync_type(req, username, comments=True, model=HnComment, is_full=is_full)

    def _sync_type(self, req, username, comments, model, is_full):
        label = "comments" if comments else "stories"
        klass = "default" if comments else "subtext"

        if is_full:
            all_ids = self._scrape_all(req, username, comments)
        else:
            all_ids = self._scrape_incremental(req, username, comments, klass, model)

        model.save_ids(all_ids)

        empty = model.list_empty()
        count = model.count_empty()
        log.info(f"Fetching metadata for {count} {label}")

        fetched = 0
        for item in empty:
            model.save_doc(req.get_item(item._id))
            fetched += 1
            log.info(f"Got {label[:-1]} {item._id} ({fetched} of {count})")

    def _scrape_all(self, req, username, comments):
        if comments:
            return req.get_upvoted_comments(username, VERY_HIGH_PAGE)
        else:
            return req.get_upvoted_stories(username, VERY_HIGH_PAGE)

    def _scrape_incremental(self, req, username, comments, klass, model):
        import time

        all_ids = []
        page = 1
        hackernews = "https://news.ycombinator.com"

        while True:
            time.sleep(0.5)
            label = "comments" if comments else "stories"
            log.debug(f"incremental: scraping {label} page {page}")

            url = f"{hackernews}/upvoted?id={username}{'&comments=t' if comments else ''}&p={page}"
            saved = req.get(url)
            soup = BeautifulSoup(saved.content, features="html.parser")

            page_ids = []
            for tag in soup.find_all("td", attrs={"class": klass}):
                if tag.a is not type(None):
                    a_tags = tag.find_all("a")
                    for a_tag in a_tags:
                        if a_tag["href"][:5] == "item?":
                            story_id = a_tag["href"].split("id=")[1]
                            page_ids.append(story_id)
                            break

            if len(page_ids) == 0:
                break

            all_known = all(model.has_id(_id) for _id in page_ids)
            all_ids.extend(page_ids)

            if all_known:
                log.debug(f"incremental: all IDs on page {page} are known, stopping")
                break

            page += 1

        return all_ids
