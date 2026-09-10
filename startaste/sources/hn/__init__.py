from __future__ import annotations

import logging
import os

from startaste.sources.base import Source
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.hn.scraper import Req, get_credentials

log = logging.getLogger(__name__)


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
            all_ids = self._scrape_all(req, username, comments, klass)
        else:
            all_ids = self._scrape_incremental(req, username, comments, klass, model)

        # Store a listing in one go. A partially stored listing would leave the
        # database non-empty, so the next run would take the incremental path,
        # stop on the first page of known IDs, and silently abandon the rest.
        model.save_ids(all_ids)

        empty = model.list_empty()
        count = model.count_empty()
        log.info(f"Fetching metadata for {count} {label}")

        fetched = 0
        for item in empty:
            model.save_doc(req.get_item(item._id))
            fetched += 1
            log.info(f"Got {label[:-1]} {item._id} ({fetched} of {count})")

    def _scrape_all(self, req, username, comments, klass):
        return req.scrape_ids(username, comments, klass)

    def _scrape_incremental(self, req, username, comments, klass, model):
        label = "comments" if comments else "stories"
        all_ids = []

        for page, page_ids in enumerate(req.iter_upvoted(username, comments, klass), start=1):
            all_known = all(model.has_id(_id) for _id in page_ids)
            all_ids.extend(page_ids)

            if all_known:
                log.debug(f"incremental: all {label} IDs on page {page} are known, stopping")
                break

        return all_ids
