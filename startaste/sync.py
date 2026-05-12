from __future__ import annotations

import logging
import sys

from startaste.db import Story, Comment, database, create_tables
from startaste.scraper import Req, get_credentials

log = logging.getLogger(__name__)

VERY_HIGH_PAGE = 10000


def run_sync():
    create_tables()
    database.connect()

    username, password = get_credentials()
    req = Req()
    req.login(username, password)

    # Auto-detect mode
    story_count = Story.count_all()
    comment_count = Comment.count_all()
    is_full = story_count == 0 and comment_count == 0

    if is_full:
        log.info("Full sync: database is empty, scraping all pages")
        max_page = VERY_HIGH_PAGE
    else:
        log.info("Incremental sync: stopping when all IDs on a page are known")
        max_page = VERY_HIGH_PAGE

    # Sync stories
    _sync_type(req, username, max_page, comments=False, model=Story, is_full=is_full)

    # Sync comments
    _sync_type(req, username, max_page, comments=True, model=Comment, is_full=is_full)

    database.close()
    log.info("Sync complete")


def _sync_type(req: Req, username: str, max_page: int, comments: bool, model, is_full: bool):
    label = "comments" if comments else "stories"
    klass = "default" if comments else "subtext"

    ids = []
    for page in range(1, max_page):
        import time
        time.sleep(0.5)
        log.debug(f"scraping {label} page {page}")

        page_ids = req.scrape_ids(
            user=username, comments=comments, klass=klass, max_page=page + 1
        )
        # scrape_ids with max_page=page+1 will only scrape one page starting at page 1
        # We need direct page access instead — use the scraper's internal logic
        break  # fall through to simpler approach

    # Use the scraper but with incremental stop condition
    if is_full:
        all_ids = _scrape_all(req, username, comments, klass)
    else:
        all_ids = _scrape_incremental(req, username, comments, klass, model)

    model.save_ids(all_ids)

    # Fetch metadata for items without bodies
    empty = model.list_empty()
    count = model.count_empty()
    log.info(f"Fetching metadata for {count} {label}")

    fetched = 0
    for item in empty:
        model.save_doc(req.get_item(item._id))
        fetched += 1
        log.info(f"Got {label[:-1]} {item._id} ({fetched} of {count})")


def _scrape_all(req: Req, username: str, comments: bool, klass: str) -> list[str]:
    """Full sync: scrape all pages until HN returns an empty page."""
    if comments:
        return req.get_upvoted_comments(username, VERY_HIGH_PAGE)
    else:
        return req.get_upvoted_stories(username, VERY_HIGH_PAGE)


def _scrape_incremental(req: Req, username: str, comments: bool, klass: str, model) -> list[str]:
    """Incremental sync: scrape page by page, stop when all IDs on a page are already known."""
    from bs4 import BeautifulSoup
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

        # Check if all IDs on this page are already known
        all_known = all(model.has_id(_id) for _id in page_ids)
        all_ids.extend(page_ids)

        if all_known:
            log.debug(f"incremental: all IDs on page {page} are known, stopping")
            break

        page += 1

    return all_ids
